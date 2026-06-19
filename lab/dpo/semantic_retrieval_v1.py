#!/usr/bin/env python3
"""
semantic_retrieval_v1.py — Track E: Semantic Retrieval Scoring (TF-IDF variant)
Replaces "longest abstract" heuristic with TF-IDF cosine similarity scoring.

INPUT:  data/model_claims_v1.jsonl  (20 model-generated claims from v189)
OUTPUT: eval/semantic_retrieval_results_v1.jsonl

Pipeline per claim:
  1. Query Crossref (top 10) + OpenAlex (top 10)
  2. Deduplicate by DOI, discard entries without abstract
  3. Score claim vs all abstracts via TF-IDF cosine similarity
  4. Pick best match by similarity (vs baseline: longest abstract)

Baseline comparison: v189 raw = 0.19, reformulated = 0.44.
Target: support_supply > 0.44 on same 20 claims with relevance scoring only.

Usage:
  python semantic_retrieval_v1.py [--claims PATH] [--out PATH] [--top-k 10]
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── abstract reconstruction helpers ──────────────────────────────────────────

def clean_jats_abstract(text: str) -> str:
    """Strip JATS XML tags from Crossref abstracts."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def reconstruct_openalex_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract from OpenAlex inverted index."""
    if not inverted_index:
        return ""
    words = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words))


# ── API helpers ──────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "ONTO-Research/1.0 (mailto:council@ontostandard.org)"
}


def _get_json(url: str, retries: int = 2) -> dict | None:
    """Fetch JSON from URL with retries and rate-limit backoff."""
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            print(f"  HTTP {e.code} for {url[:80]}...", file=sys.stderr)
            return None
        except (URLError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(1)
                continue
            print(f"  Network error: {e}", file=sys.stderr)
            return None


def query_crossref(claim: str, top_k: int = 10) -> list[dict]:
    """Query Crossref works API, return list of {doi, title, abstract}."""
    q = quote(claim[:300])
    url = (
        f"https://api.crossref.org/works"
        f"?query={q}&rows={top_k}"
        f"&select=DOI,title,abstract"
        f"&mailto=council@ontostandard.org"
    )
    data = _get_json(url)
    if not data or "message" not in data:
        return []

    results = []
    for item in data["message"].get("items", []):
        doi = item.get("DOI", "")
        title_parts = item.get("title", [])
        title = title_parts[0] if title_parts else ""
        abstract = clean_jats_abstract(item.get("abstract", ""))
        if doi and abstract and len(abstract) > 30:
            results.append({
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "source": "crossref",
            })
    return results


def query_openalex(claim: str, top_k: int = 10) -> list[dict]:
    """Query OpenAlex works API, return list of {doi, title, abstract}."""
    q = quote(claim[:300])
    url = (
        f"https://api.openalex.org/works"
        f"?search={q}&per_page={top_k}"
        f"&mailto=council@ontostandard.org"
    )
    data = _get_json(url)
    if not data or "results" not in data:
        return []

    results = []
    for item in data.get("results", []):
        doi = (item.get("doi") or "").replace("https://doi.org/", "")
        title = item.get("title", "") or ""
        abstract = reconstruct_openalex_abstract(
            item.get("abstract_inverted_index")
        )
        if not abstract:
            abstract = item.get("abstract", "") or ""
        if doi and abstract and len(abstract) > 30:
            results.append({
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "source": "openalex",
            })
    return results


# ── dedup + TF-IDF scoring ───────────────────────────────────────────────────

def deduplicate_papers(papers: list[dict]) -> list[dict]:
    """Deduplicate by DOI (case-insensitive), prefer Crossref source."""
    seen = {}
    for p in papers:
        key = p["doi"].lower()
        if key not in seen:
            seen[key] = p
        elif p["source"] == "crossref" and seen[key]["source"] == "openalex":
            seen[key] = p
    return list(seen.values())


def score_tfidf(claim: str, papers: list[dict]) -> list[dict]:
    """Score each paper's abstract against the claim using TF-IDF cosine sim."""
    if not papers:
        return []

    # Build corpus: [claim, abstract_0, abstract_1, ...]
    corpus = [claim] + [p["abstract"] for p in papers]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=10000,
        ngram_range=(1, 2),  # unigrams + bigrams for phrase matching
        sublinear_tf=True,   # log-scaled TF for better discrimination
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Cosine similarity between claim (row 0) and each abstract
    sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    for i, p in enumerate(papers):
        p["similarity"] = round(float(sims[i]), 4)

    return sorted(papers, key=lambda x: x["similarity"], reverse=True)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Semantic retrieval scoring")
    parser.add_argument(
        "--claims", default="data/model_claims_v1.jsonl",
        help="Path to claims JSONL"
    )
    parser.add_argument(
        "--out", default="eval/semantic_retrieval_results_v1.jsonl",
        help="Output path"
    )
    parser.add_argument(
        "--top-k", type=int, default=10,
        help="Papers to retrieve per API per claim"
    )
    args = parser.parse_args()

    # ── load claims ──
    claims_path = Path(args.claims)
    if not claims_path.exists():
        print(f"ERROR: claims file not found: {claims_path}", file=sys.stderr)
        sys.exit(1)

    claims = []
    with open(claims_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                claim_text = obj.get("claim") or obj.get("text") or ""
                claim_id = obj.get("id", f"mc{len(claims):02d}")
                if claim_text:
                    claims.append({"id": claim_id, "claim": claim_text})

    print(f"Loaded {len(claims)} claims from {claims_path}")

    # ── process each claim ──
    results = []
    for i, c in enumerate(claims):
        cid, claim = c["id"], c["claim"]
        print(f"\n[{i+1}/{len(claims)}] {cid}: {claim[:70]}...")

        # retrieve from both APIs
        cr_papers = query_crossref(claim, args.top_k)
        time.sleep(0.5)
        oa_papers = query_openalex(claim, args.top_k)
        time.sleep(0.5)

        # pool + dedup
        all_papers = deduplicate_papers(cr_papers + oa_papers)
        print(f"  Retrieved: {len(cr_papers)} crossref + {len(oa_papers)} openalex"
              f" -> {len(all_papers)} unique with abstract")

        if not all_papers:
            results.append({
                "id": cid, "claim": claim,
                "status": "NO_CANDIDATES",
                "n_crossref": len(cr_papers),
                "n_openalex": len(oa_papers),
                "n_unique": 0,
            })
            print("  -> NO CANDIDATES with abstract")
            continue

        # TF-IDF scoring
        ranked = score_tfidf(claim, all_papers)
        best = ranked[0]

        # baseline: longest abstract
        baseline_pick = max(all_papers, key=lambda x: len(x["abstract"]))

        result = {
            "id": cid,
            "claim": claim,
            "status": "MATCHED",
            "best_doi": best["doi"],
            "best_title": best["title"],
            "best_abstract": best["abstract"],
            "best_similarity": best["similarity"],
            "best_source": best["source"],
            "baseline_doi": baseline_pick["doi"],
            "baseline_title": baseline_pick["title"],
            "baseline_abstract": baseline_pick["abstract"],
            "baseline_similarity": baseline_pick.get("similarity", 0),
            "n_crossref": len(cr_papers),
            "n_openalex": len(oa_papers),
            "n_unique": len(all_papers),
            "sim_range": f"{ranked[-1]['similarity']:.4f}-{ranked[0]['similarity']:.4f}",
            "same_as_baseline": best["doi"].lower() == baseline_pick["doi"].lower(),
        }
        results.append(result)

        print(f"  -> BEST (tfidf): sim={best['similarity']:.4f}  {best['title'][:60]}")
        print(f"     BASELINE (longest): sim={baseline_pick.get('similarity',0):.4f}  "
              f"{baseline_pick['title'][:60]}")
        if result["same_as_baseline"]:
            print("     (same paper)")

    # ── write output ──
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ── summary ──
    matched = [r for r in results if r["status"] == "MATCHED"]
    no_match = [r for r in results if r["status"] == "NO_CANDIDATES"]
    same = sum(1 for r in matched if r.get("same_as_baseline", False))
    diff = len(matched) - same

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Claims: {len(results)}")
    print(f"  Matched: {len(matched)}, No candidates: {len(no_match)}")
    print(f"  TF-IDF pick == baseline pick: {same}")
    print(f"  TF-IDF pick DIFFERENT from baseline: {diff}")
    if matched:
        avg_sim = sum(r["best_similarity"] for r in matched) / len(matched)
        print(f"  Avg best similarity: {avg_sim:.4f}")
    print(f"\nOutput: {out_path}")
    print(f"\nNEXT: B2 eval on TF-IDF picks -> support_supply vs baseline 0.44")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
