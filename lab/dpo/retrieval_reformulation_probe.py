#!/usr/bin/env python3
"""
retrieval_reformulation_probe.py — Track C-bis: Query Reformulation Probe

Takes the 12 NOT-supported claims from Track C, uses manually targeted
search queries instead of raw claim text, re-runs retrieval.
Measures: how many flip from NOT → matched-with-abstract.

Usage:
  python retrieval_reformulation_probe.py --run --outdir .

Output: retrieval_reformulated_v1.jsonl
"""

import argparse, json, os, re, sys, time
import urllib.request, urllib.parse

USER_AGENT = "ONTOResearch/1.0 (mailto:council@ontostandard.org)"
CROSSREF_URL = "https://api.crossref.org/works"
OPENALEX_URL = "https://api.openalex.org/works"

# 12 NOT-supported claims from Track C with reformulated search queries.
# Original queries = full claim text (too generic, diluted keyword match).
# Reformulated = targeted key terms for better retrieval precision.
PROBES = [
    {
        "id": "mc00",
        "claim": "The half-life of carbon-14 is approximately 5730 years. This property makes carbon-14 extremely useful for radiocarbon dating, a method that scientists use to determine the age of organic materials up to about 50,000 years old.",
        "original_query_type": "full claim",
        "reformulated_query": "carbon-14 half-life 5730 radiocarbon dating",
    },
    {
        "id": "mc02",
        "claim": "Metformin works as a diabetes treatment by lowering glucose production in the liver and improving insulin sensitivity in muscle, fat, and liver tissues.",
        "original_query_type": "full claim",
        "reformulated_query": "metformin mechanism hepatic glucose production insulin sensitivity",
    },
    {
        "id": "mc04",
        "claim": "Long-term exposure to particulate matter (PM2.5) has been linked to increased risk of mortality from cardiovascular disease and lung cancer.",
        "original_query_type": "full claim",
        "reformulated_query": "PM2.5 long-term exposure cardiovascular mortality lung cancer",
    },
    {
        "id": "mc05",
        "claim": "The discovery of the Higgs boson at CERN in 2012 confirmed a key prediction made by the Standard Model of particle physics.",
        "original_query_type": "full claim",
        "reformulated_query": "Higgs boson discovery 2012 CERN Standard Model confirmation",
    },
    {
        "id": "mc06",
        "claim": "mRNA vaccines have been shown to be highly effective, with the Pfizer-BioNTech and Moderna vaccines having an efficacy rate of around 95% against symptomatic COVID-19.",
        "original_query_type": "full claim",
        "reformulated_query": "mRNA vaccine efficacy 95 percent Pfizer BioNTech clinical trial",
    },
    {
        "id": "mc08",
        "claim": "CRISPR-Cas13 differs from CRISPR-Cas9 in that it targets RNA rather than DNA, making it more specific for applications like detecting pathogens or editing RNA molecules.",
        "original_query_type": "full claim",
        "reformulated_query": "CRISPR Cas13 RNA targeting diagnostic application",
    },
    {
        "id": "mc10",
        "claim": "The evidence for dark matter in galaxy rotation curves comes from observations that show stars orbit galaxies at speeds much faster than expected based on visible matter alone.",
        "original_query_type": "full claim",
        "reformulated_query": "dark matter galaxy rotation curves flat velocity evidence",
    },
    {
        "id": "mc11",
        "claim": "Ocean Thermal Energy Conversion (OTEC) works by utilizing the temperature difference between warm surface waters and cold deep waters to drive a power turbine.",
        "original_query_type": "full claim",
        "reformulated_query": "OTEC ocean thermal energy conversion warm cold seawater",
    },
    {
        "id": "mc12",
        "claim": "The measured rate of Arctic sea ice decline has been approximately 12.8% per decade since the late 20th century.",
        "original_query_type": "full claim",
        "reformulated_query": "Arctic sea ice extent decline rate percent per decade satellite",
    },
    {
        "id": "mc14",
        "claim": "Lithium acts as a mood stabilizer by modulating the function of ion channels in nerve cells, specifically sodium and potassium channels.",
        "original_query_type": "full claim",
        "reformulated_query": "lithium mood stabilizer molecular mechanism neuron",
    },
    {
        "id": "mc18",
        "claim": "Glyphosate has been shown to have adverse effects on non-target organisms in the environment, disrupting endocrine systems in aquatic organisms.",
        "original_query_type": "full claim",
        "reformulated_query": "glyphosate endocrine disruption aquatic organisms fish amphibians",
    },
    {
        "id": "mc19",
        "claim": "The Hubble constant has been measured to be approximately 74 kilometers per second per megaparsec.",
        "original_query_type": "full claim",
        "reformulated_query": "Hubble constant measurement 74 km/s/Mpc Cepheid",
    },
]


def api_get(url, params):
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    API error: {e}")
        return None


def search_crossref(query, rows=3):
    data = api_get(CROSSREF_URL, {"query": query, "rows": rows,
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


def search_openalex(query, per_page=3):
    data = api_get(OPENALEX_URL, {"search": query, "per_page": per_page})
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
    all_r = crossref + openalex
    if not all_r:
        return None
    with_abs = [r for r in all_r if r.get("abstract")]
    if with_abs:
        return max(with_abs, key=lambda r: len(r["abstract"]))
    if all_r:
        return max(all_r, key=lambda r: r.get("score", 0))
    return None


def run(outdir):
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "retrieval_reformulated_v1.jsonl")
    results = []

    print(f"Reformulation probe: {len(PROBES)} claims")
    print(f"Output: {outpath}\n")

    for i, p in enumerate(PROBES):
        q = p["reformulated_query"]
        print(f"[{i+1:2d}/{len(PROBES)}] {p['id']}: {q}")

        print("  Crossref...", end=" ", flush=True)
        cr = search_crossref(q)
        print(f"{len(cr)} hits")
        time.sleep(1.0)

        print("  OpenAlex...", end=" ", flush=True)
        oa = search_openalex(q)
        print(f"{len(oa)} hits")
        time.sleep(0.5)

        match = pick_best(cr, oa)
        entry = {
            "id": p["id"],
            "claim": p["claim"],
            "reformulated_query": q,
            "match": None,
            "crossref_hits": len(cr),
            "openalex_hits": len(oa),
        }

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

    # Summary
    matched = sum(1 for r in results if r["match"])
    with_abs = sum(1 for r in results if r["match"] and r["match"]["has_abstract"])
    print(f"\n{'='*60}")
    print(f"  Claims:          {len(results)}")
    print(f"  Matched:         {matched}/{len(results)}")
    print(f"  With abstract:   {with_abs}/{len(results)}  <- ready for B2")
    print(f"  No abstract:     {matched - with_abs}/{len(results)}")
    print(f"  No match:        {len(results) - matched}/{len(results)}")
    print(f"{'='*60}")
    print(f"\nResults -> {outpath}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Track C-bis: Reformulation probe")
    p.add_argument("--run", action="store_true")
    p.add_argument("--outdir", default=".")
    a = p.parse_args()

    if a.run:
        run(a.outdir)
    else:
        p.print_help()
