#!/usr/bin/env python3
"""
retrieval_proposer_v1.py — Track B: Source Retrieval

For each claim, search Crossref + OpenAlex, retrieve best match
(DOI, title, abstract), output JSONL for s2b SUPPORTS verification.

Usage:
  python retrieval_proposer_v1.py --run                      # embedded claims
  python retrieval_proposer_v1.py --run --claims file.jsonl   # custom claims
  python retrieval_proposer_v1.py --summary results.jsonl     # print summary

Output: retrieval_results_v1.jsonl
Requires: network access (Crossref + OpenAlex APIs, free, no auth).
"""

import argparse, json, os, re, sys, time
import urllib.request, urllib.parse

USER_AGENT = "ONTOResearch/1.0 (mailto:council@ontostandard.org)"
CROSSREF_URL = "https://api.crossref.org/works"
OPENALEX_URL = "https://api.openalex.org/works"

# 20 model-like factual claims, diverse domains, all should have real papers
CLAIMS = [
    "Intermittent fasting improves insulin sensitivity in overweight adults",
    "CRISPR-Cas9 enables targeted genome editing in mammalian cells",
    "The gut microbiome influences mental health through the gut-brain axis",
    "Regular aerobic exercise reduces the risk of cardiovascular disease",
    "Quantum entanglement has been demonstrated over distances exceeding 1000 kilometers",
    "Deep learning models can detect diabetic retinopathy from retinal images",
    "The Mediterranean diet is associated with reduced risk of cognitive decline",
    "Gravitational waves were first directly detected in 2015 by LIGO",
    "Microplastics have been found in human blood samples",
    "Transformer architecture improved natural language processing performance",
    "Sleep deprivation impairs cognitive function and decision-making",
    "The human genome contains approximately 20000 protein-coding genes",
    "Ocean acidification threatens coral reef ecosystems worldwide",
    "Lithium-ion batteries degrade faster at higher temperatures",
    "Cognitive behavioral therapy is effective for treating anxiety disorders",
    "The cosmic microwave background radiation supports the Big Bang theory",
    "Antibiotic resistance is accelerated by overuse of antibiotics in agriculture",
    "Solar panel efficiency has increased significantly over the past decade",
    "Neuroplasticity allows the adult brain to reorganize neural pathways",
    "Rising global temperatures increase the frequency of extreme weather events",
]


# ──────────────────────────────────────────────
# API
# ──────────────────────────────────────────────
def api_get(url, params):
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    API error: {e}")
        return None


def search_crossref(claim, rows=3):
    data = api_get(CROSSREF_URL, {"query": claim, "rows": rows,
                                   "select": "DOI,title,abstract,published-print,published-online,score"})
    if not data or "message" not in data:
        return []
    out = []
    for item in data["message"].get("items", []):
        title = (item.get("title") or [""])[0]
        abstract = re.sub(r"<[^>]+>", "", item.get("abstract", "")).strip()
        pub = item.get("published-print") or item.get("published-online") or {}
        year = (pub.get("date-parts") or [[None]])[0][0]
        out.append({
            "api": "crossref", "doi": item.get("DOI", ""), "title": title,
            "abstract": abstract, "year": year, "score": item.get("score", 0),
        })
    return out


def reconstruct_abstract(inv_idx):
    if not inv_idx:
        return ""
    pairs = []
    for word, positions in inv_idx.items():
        for pos in positions:
            pairs.append((pos, word))
    pairs.sort()
    return " ".join(w for _, w in pairs)


def search_openalex(claim, per_page=3):
    data = api_get(OPENALEX_URL, {"search": claim, "per_page": per_page})
    if not data or "results" not in data:
        return []
    out = []
    for item in data["results"]:
        doi = (item.get("doi") or "").replace("https://doi.org/", "")
        abstract = reconstruct_abstract(item.get("abstract_inverted_index"))
        out.append({
            "api": "openalex", "doi": doi, "title": item.get("title", ""),
            "abstract": abstract, "year": item.get("publication_year"),
            "score": item.get("relevance_score", 0),
        })
    return out


def pick_best(crossref, openalex):
    """Best match: prefer longest abstract (most context for verifier)."""
    all_r = crossref + openalex
    if not all_r:
        return None
    with_abs = [r for r in all_r if r.get("abstract")]
    if with_abs:
        return max(with_abs, key=lambda r: len(r["abstract"]))
    if all_r:
        return max(all_r, key=lambda r: r.get("score", 0))
    return None


# ──────────────────────────────────────────────
# RUN
# ──────────────────────────────────────────────
def run(claims, outdir):
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "retrieval_results_v1.jsonl")
    results = []

    for i, claim in enumerate(claims):
        print(f"\n[{i+1}/{len(claims)}] {claim[:70]}...")
        print("  Crossref...", end=" ", flush=True)
        cr = search_crossref(claim)
        print(f"{len(cr)} hits")
        time.sleep(1.0)  # polite

        print("  OpenAlex...", end=" ", flush=True)
        oa = search_openalex(claim)
        print(f"{len(oa)} hits")
        time.sleep(0.5)

        match = pick_best(cr, oa)
        entry = {"id": i, "claim": claim, "match": None,
                 "crossref_hits": len(cr), "openalex_hits": len(oa)}

        if match:
            entry["match"] = {
                "doi": match["doi"],
                "title": match["title"],
                "abstract": match["abstract"][:3000],
                "api": match["api"],
                "year": match.get("year"),
                "has_abstract": bool(match.get("abstract")),
            }
            abs_len = len(match.get("abstract", ""))
            print(f"  => [{match['api']}] {match['title'][:60]}")
            print(f"     DOI: {match['doi']}  Year: {match.get('year')}")
            print(f"     Abstract: {'YES' if abs_len else 'NO'} ({abs_len} chars)")
        else:
            print("  => NO MATCH")

        results.append(entry)

    with open(outpath, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nResults -> {outpath}")
    print_summary(results)


def print_summary(results):
    matched = sum(1 for r in results if r["match"])
    with_abs = sum(1 for r in results if r["match"] and r["match"]["has_abstract"])
    no_match = len(results) - matched
    print(f"\n{'='*60}")
    print(f"  Claims:            {len(results)}")
    print(f"  Matched:           {matched}/{len(results)}")
    print(f"  With abstract:     {with_abs}/{len(results)}  <- ready for s2b")
    print(f"  No abstract:       {matched - with_abs}/{len(results)}")
    print(f"  No match:          {no_match}/{len(results)}")
    print(f"{'='*60}")


def show_summary(path):
    results = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    print_summary(results)
    for r in results:
        m = r.get("match")
        if m and m["has_abstract"]:
            tag = "READY"
        elif m:
            tag = "NO-ABS"
        else:
            tag = "MISS"
        print(f"  [{r['id']+1:2d}] {tag:7s} {r['claim'][:50]}")
        if m:
            print(f"          DOI:{m['doi']}  {m['title'][:50]}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Track B: Retrieval Proposer")
    p.add_argument("--run", action="store_true")
    p.add_argument("--claims", type=str, help="JSONL with 'claim' field")
    p.add_argument("--summary", type=str, help="Show results summary")
    p.add_argument("--outdir", default=".")
    a = p.parse_args()

    if a.run:
        if a.claims:
            cl = []
            with open(a.claims) as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        cl.append(obj.get("claim", obj.get("text", "")))
            print(f"Loaded {len(cl)} claims from {a.claims}")
        else:
            cl = CLAIMS
            print(f"Using {len(cl)} embedded claims")
        run(cl, a.outdir)
    elif a.summary:
        show_summary(a.summary)
    else:
        p.print_help()
