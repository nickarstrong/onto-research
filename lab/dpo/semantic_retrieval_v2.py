#!/usr/bin/env python3
"""
semantic_retrieval_v2.py — Track E: Semantic Retrieval Scoring (transformer embeddings)
Uses transformers + torch DIRECTLY (bypasses sentence_transformers pyarrow crash).
Same model (all-MiniLM-L6-v2), same pipeline, real semantic scoring.

INPUT:  data/model_claims_v1.jsonl  (20 model-generated claims from v189)
OUTPUT: eval/semantic_retrieval_results_v2.jsonl

Pipeline per claim:
  1. Query Crossref (top 10) + OpenAlex (top 10)
  2. Deduplicate by DOI, discard entries without abstract
  3. Embed claim + all abstracts via all-MiniLM-L6-v2 (mean pooling + L2 norm)
  4. Rank by cosine similarity, pick best match

Baseline: v189 raw=0.19, reformulated=0.44, v1 TF-IDF=0.263.
Target: support_supply > 0.44.
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

import torch
from transformers import AutoTokenizer, AutoModel

# ── embedding engine (no sentence_transformers) ──────────────────────────────

_tokenizer = None
_model = None

def _load_model():
    global _tokenizer, _model
    if _model is not None:
        return
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading {model_name} via transformers (CPU)...")
    _tokenizer = AutoTokenizer.from_pretrained(model_name)
    _model = AutoModel.from_pretrained(model_name)
    _model.eval()
    print("Model loaded.")


def encode(texts: list[str]) -> torch.Tensor:
    """Encode texts to L2-normalized embeddings (mean pooling)."""
    _load_model()
    inputs = _tokenizer(
        texts, padding=True, truncation=True,
        return_tensors="pt", max_length=256
    )
    with torch.no_grad():
        outputs = _model(**inputs)
    mask = inputs["attention_mask"].unsqueeze(-1).float()
    token_embs = outputs.last_hidden_state
    pooled = (token_embs * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
    return torch.nn.functional.normalize(pooled, p=2, dim=1)


def cosine_scores(query_emb: torch.Tensor, doc_embs: torch.Tensor) -> list[float]:
    """Cosine similarity between one query and multiple docs."""
    sims = torch.mm(query_emb, doc_embs.T)[0]
    return [round(float(s), 4) for s in sims]


# ── abstract reconstruction helpers ──────────────────────────────────────────

def clean_jats_abstract(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def reconstruct_openalex_abstract(inverted_index: dict) -> str:
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
            results.append({"doi": doi, "title": title, "abstract": abstract, "source": "crossref"})
    return results


def query_openalex(claim: str, top_k: int = 10) -> list[dict]:
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
        abstract = reconstruct_openalex_abstract(item.get("abstract_inverted_index"))
        if not abstract:
            abstract = item.get("abstract", "") or ""
        if doi and abstract and len(abstract) > 30:
            results.append({"doi": doi, "title": title, "abstract": abstract, "source": "openalex"})
    return results


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen = {}
    for p in papers:
        key = p["doi"].lower()
        if key not in seen:
            seen[key] = p
        elif p["source"] == "crossref" and seen[key]["source"] == "openalex":
            seen[key] = p
    return list(seen.values())


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Semantic retrieval v2 (transformer embeddings)")
    parser.add_argument("--claims", default="data/model_claims_v1.jsonl")
    parser.add_argument("--out", default="eval/semantic_retrieval_results_v2.jsonl")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    claims_path = Path(args.claims)
    if not claims_path.exists():
        print(f"ERROR: {claims_path} not found", file=sys.stderr)
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

    # pre-load model
    _load_model()

    results = []
    for i, c in enumerate(claims):
        cid, claim = c["id"], c["claim"]
        print(f"\n[{i+1}/{len(claims)}] {cid}: {claim[:70]}...")

        cr_papers = query_crossref(claim, args.top_k)
        time.sleep(0.5)
        oa_papers = query_openalex(claim, args.top_k)
        time.sleep(0.5)

        all_papers = deduplicate_papers(cr_papers + oa_papers)
        print(f"  Retrieved: {len(cr_papers)} crossref + {len(oa_papers)} openalex"
              f" -> {len(all_papers)} unique with abstract")

        if not all_papers:
            results.append({
                "id": cid, "claim": claim, "status": "NO_CANDIDATES",
                "n_crossref": len(cr_papers), "n_openalex": len(oa_papers), "n_unique": 0,
            })
            print("  -> NO CANDIDATES with abstract")
            continue

        # semantic scoring via transformer embeddings
        claim_emb = encode([claim])
        abstracts = [p["abstract"] for p in all_papers]
        abs_embs = encode(abstracts)
        sims = cosine_scores(claim_emb, abs_embs)

        for j, p in enumerate(all_papers):
            p["similarity"] = sims[j]

        ranked = sorted(all_papers, key=lambda x: x["similarity"], reverse=True)
        best = ranked[0]

        # baseline: longest abstract
        baseline_pick = max(all_papers, key=lambda x: len(x["abstract"]))

        result = {
            "id": cid, "claim": claim, "status": "MATCHED",
            "best_doi": best["doi"], "best_title": best["title"],
            "best_abstract": best["abstract"],
            "best_similarity": best["similarity"], "best_source": best["source"],
            "baseline_doi": baseline_pick["doi"], "baseline_title": baseline_pick["title"],
            "baseline_abstract": baseline_pick["abstract"],
            "baseline_similarity": baseline_pick.get("similarity", 0),
            "n_crossref": len(cr_papers), "n_openalex": len(oa_papers),
            "n_unique": len(all_papers),
            "sim_range": f"{ranked[-1]['similarity']:.4f}-{ranked[0]['similarity']:.4f}",
            "same_as_baseline": best["doi"].lower() == baseline_pick["doi"].lower(),
        }
        results.append(result)

        print(f"  -> BEST (embed): sim={best['similarity']:.4f}  {best['title'][:60]}")
        print(f"     BASELINE (longest): sim={baseline_pick.get('similarity',0):.4f}  "
              f"{baseline_pick['title'][:60]}")
        if result["same_as_baseline"]:
            print("     (same paper)")

    # write output
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # summary
    matched = [r for r in results if r["status"] == "MATCHED"]
    no_match = [r for r in results if r["status"] == "NO_CANDIDATES"]
    same = sum(1 for r in matched if r.get("same_as_baseline", False))
    diff = len(matched) - same

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Claims: {len(results)}")
    print(f"  Matched: {len(matched)}, No candidates: {len(no_match)}")
    print(f"  Embed pick == baseline: {same}")
    print(f"  Embed pick DIFFERENT: {diff}")
    if matched:
        avg_sim = sum(r["best_similarity"] for r in matched) / len(matched)
        print(f"  Avg best similarity: {avg_sim:.4f}")
    print(f"\nOutput: {out_path}")
    print(f"\nNEXT: B2 eval -> support_supply vs baseline 0.44")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
