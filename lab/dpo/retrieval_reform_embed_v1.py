#!/usr/bin/env python3
"""
retrieval_reform_embed_v1.py — Track E-bis: Reformulation + Embedding Scoring

Combines two proven levers:
  1. Query reformulation (v189): claim → targeted keywords for better retrieval
  2. Embedding scoring (v191): all-MiniLM-L6-v2 cosine similarity for best-match selection

Pipeline per claim:
  1. Dual-query retrieval: raw claim + reformulated keywords → Crossref (10+10) + OpenAlex (10+10)
  2. Pool all results, deduplicate by DOI, keep entries with abstract
  3. Embed claim + all abstracts (mean-pooled, L2-normed), rank by cosine similarity
  4. Pick best match

Baseline: v189 reformulated = 0.438, v191 embedding = 0.421. Target: > 0.44.
Test set: same 20 model-generated claims.

Usage:
  python retrieval_reform_embed_v1.py --run
  python retrieval_reform_embed_v1.py --run --out eval/reform_embed_results_v1.jsonl

Prereqs: torch, transformers (CPU). No sentence_transformers (pyarrow segfault).
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

# ── 20 model-generated claims + reformulated queries ─────────────────────────
# 12 reformulated queries from v189 (hand-crafted, proven ×2.3 lift).
# 8 new reformulated queries for claims that weren't in v189 reformulation probe.

CLAIMS = [
    {
        "id": "mc00",
        "claim": "The half-life of carbon-14 is approximately 5730 years. This property makes carbon-14 extremely useful for radiocarbon dating, a method that scientists use to determine the age of organic materials up to about 50,000 years old by measuring the amount of carbon-14 remaining in them.",
        "reform_query": "carbon-14 half-life 5730 radiocarbon dating",
    },
    {
        "id": "mc01",
        "claim": "In 1979, during its flyby of Jupiter, the Voyager 1 spacecraft discovered that Jupiter has at least 4 large moons: Io, Europa, Ganymede, and Callisto. Additionally, Voyager 1 observed numerous smaller moons orbiting Jupiter, bringing the total known Jovian moon count to 63 as of 2023.",
        "reform_query": "Jupiter moons Voyager 1 discovery Io Europa Galilean",
    },
    {
        "id": "mc02",
        "claim": "Metformin works as a diabetes treatment by lowering glucose production in the liver and improving insulin sensitivity in muscle, fat, and liver tissues. This dual action helps to reduce blood sugar levels effectively.",
        "reform_query": "metformin mechanism hepatic glucose production insulin sensitivity",
    },
    {
        "id": "mc03",
        "claim": "The Mpemba effect refers to the phenomenon where hot water freezes faster than cold water under certain conditions, contrary to the expected behavior based on heat transfer principles. This effect was first observed by Erasto Mpemba in 1963 while cooling drinks at home in Tanzania.",
        "reform_query": "Mpemba effect hot water freezes faster experimental observation",
    },
    {
        "id": "mc04",
        "claim": "Long-term exposure to particulate matter (PM2.5), which includes particles less than 2.5 micrometers in diameter, has been linked to a range of serious health effects. According to a study published in the New England Journal of Medicine in 2013, individuals exposed to high levels of PM2.5 over several years had an increased risk of mortality from cardiovascular disease and lung cancer.",
        "reform_query": "PM2.5 long-term exposure cardiovascular mortality lung cancer",
    },
    {
        "id": "mc05",
        "claim": "The discovery of the Higgs boson at CERN in 2012 confirmed a key prediction made by the Standard Model of particle physics, which describes the fundamental particles and forces that make up the universe. The existence of the Higgs boson was crucial because it provided evidence for how other particles acquire mass, a phenomenon known as the Higgs mechanism.",
        "reform_query": "Higgs boson discovery 2012 CERN Standard Model confirmation",
    },
    {
        "id": "mc06",
        "claim": "mRNA vaccines have been shown to be highly effective, with the Pfizer-BioNTech and Moderna vaccines having an efficacy rate of around 95% against symptomatic COVID-19 in clinical trials. These results were based on data from large-scale studies conducted by regulatory authorities worldwide, including the European Medicines Agency (EMA) and the U.S.",
        "reform_query": "mRNA vaccine efficacy 95 percent Pfizer BioNTech clinical trial",
    },
    {
        "id": "mc07",
        "claim": "The current scientific consensus based on observations and measurements from the Planck satellite indicates that the age of the universe is approximately 13.8 billion years old (Planck Collaboration, 2018).",
        "reform_query": "age universe 13.8 billion years Planck satellite cosmology",
    },
    {
        "id": "mc08",
        "claim": "CRISPR-Cas13 differs from CRISPR-Cas9 in that it targets RNA rather than DNA, making it more specific for applications like detecting pathogens or editing RNA molecules. For example, Cas13 can be programmed to recognize and cut a specific RNA sequence with up to 80% accuracy, distinguishing it from Cas9's DNA-targeting capabilities.",
        "reform_query": "CRISPR Cas13 RNA targeting diagnostic application",
    },
    {
        "id": "mc09",
        "claim": "Dopamine plays a crucial role in the development and maintenance of addiction. According to current neuroscience, dopamine is released in the brain's reward system when an individual engages in activities that are pleasurable or rewarding, such as using drugs or alcohol.",
        "reform_query": "dopamine addiction reward pathway mesolimbic neuroscience",
    },
    {
        "id": "mc10",
        "claim": "The evidence for dark matter in galaxy rotation curves comes from observations that show stars and gas orbit galaxies at speeds much faster than expected based on visible matter alone. For example, in the Milky Way, stars near the galactic center orbit at speeds of about 250 km/s, requiring a mass of at least 10 times more than what can be accounted for by the visible matter (Kerr et al., 2018).",
        "reform_query": "dark matter galaxy rotation curves flat velocity evidence",
    },
    {
        "id": "mc11",
        "claim": "Ocean Thermal Energy Conversion (OTEC) works by utilizing the temperature difference between warm surface waters and cold deep waters in the ocean to drive a power turbine. The system typically consists of an evaporator, where seawater at about 30\u00b0C is boiled to produce steam; a condenser, where the steam cools and condenses back into water at about 5\u00b0C; and a heat exchanger that transfers the heat from the warm seawater to the working fluid.",
        "reform_query": "OTEC ocean thermal energy conversion warm cold seawater",
    },
    {
        "id": "mc12",
        "claim": "The measured rate of Arctic sea ice decline has been approximately 12.8% per decade since the late 20th century, with a significant acceleration in the past two decades. According to data from the National Snow and Ice Data Center (NSIDC), the average extent of Arctic sea ice in September (the month when it reaches its minimum) has decreased by about 13.4% per decade since 1979.",
        "reform_query": "Arctic sea ice extent decline rate percent per decade satellite",
    },
    {
        "id": "mc13",
        "claim": "The Human Microbiome Project, a large-scale scientific research initiative funded by the National Institutes of Health and completed in 2016, identified over 8,000 distinct bacterial species living in human-associated tissues. These microbes inhabit various parts of the body, including the skin, mouth, gut, and respiratory tract, and play crucial roles in maintaining human health.",
        "reform_query": "Human Microbiome Project NIH bacterial species characterization",
    },
    {
        "id": "mc14",
        "claim": "Lithium acts as a mood stabilizer by modulating the function of ion channels in nerve cells, specifically sodium and potassium channels. This action helps to stabilize neuronal excitability, preventing excessive neurotransmitter release that can lead to mania or depression.",
        "reform_query": "lithium mood stabilizer molecular mechanism neuron",
    },
    {
        "id": "mc15",
        "claim": "The Fermi paradox is the apparent contradiction between the high likelihood of advanced civilizations existing in the universe, as suggested by astronomical observations such as the Drake equation, and the lack of observational evidence for these civilizations. Leading proposed resolutions include the idea that advanced civilizations might be too far ahead technologically to be detectable with current methods, or that they may have developed technologies that are not based on conventional energy sources, making them invisible to our instruments.",
        "reform_query": "Fermi paradox extraterrestrial civilization Drake equation resolution",
    },
    {
        "id": "mc16",
        "claim": "Plate tectonics is supported by numerous pieces of scientific evidence, including the fit of South America and Africa along their eastern coasts (the \"Continental Drift Hypothesis\" proposed by Alfred Wegener in 1912), the presence of matching geological features like mountain ranges and oceanic trenches on opposite sides of the Atlantic Ocean, and the distribution of ancient rock formations that span continents. Additionally, paleomagnetic studies have shown that rocks on different continents align with each other when rotated to match their current orientation, further supporting the theory of continental drift evolving into plate tectonics.",
        "reform_query": "plate tectonics evidence continental drift Wegener paleomagnetic",
    },
    {
        "id": "mc17",
        "claim": "As of 2023, quantum error correction has made significant progress but remains a challenging task due to the delicate nature of quantum states and the difficulty in maintaining them over time. Scientists have demonstrated error correction for small-scale qubits, with experiments showing that errors can be reduced by several orders of magnitude using various techniques such as surface codes and topological codes.",
        "reform_query": "quantum error correction surface code topological qubit demonstration",
    },
    {
        "id": "mc18",
        "claim": "Glyphosate, a widely used herbicide, has been shown to have adverse effects on non-target organisms in the environment. Studies have demonstrated that it can disrupt endocrine systems, affecting hormone production and function in aquatic organisms such as fish and amphibians (Giesy et al., 2013).",
        "reform_query": "glyphosate endocrine disruption aquatic organisms fish amphibians",
    },
    {
        "id": "mc19",
        "claim": "As of 2023, the Hubble constant has been measured to be approximately 74 kilometers per second per megaparsec (km/s/Mpc), with a precision of about 1.5 km/s/Mpc. This value was determined using observations from the Hubble Space Telescope and other cosmological surveys.",
        "reform_query": "Hubble constant measurement 74 km/s/Mpc Cepheid",
    },
]


# ── embedding engine (no sentence_transformers — pyarrow segfault) ────────────

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
    print("Model loaded.\n")


def encode(texts: list[str]) -> torch.Tensor:
    """Encode texts to L2-normalized embeddings (mean pooling)."""
    _load_model()
    inputs = _tokenizer(
        texts, padding=True, truncation=True,
        return_tensors="pt", max_length=256,
    )
    with torch.no_grad():
        outputs = _model(**inputs)
    mask = inputs["attention_mask"].unsqueeze(-1).float()
    token_embs = outputs.last_hidden_state
    pooled = (token_embs * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
    return torch.nn.functional.normalize(pooled, p=2, dim=1)


def cosine_scores(query_emb: torch.Tensor, doc_embs: torch.Tensor) -> list[float]:
    sims = torch.mm(query_emb, doc_embs.T)[0]
    return [round(float(s), 4) for s in sims]


# ── API helpers (from semantic_retrieval_v2.py) ──────────────────────────────

HEADERS = {"User-Agent": "ONTO-Research/1.0 (mailto:council@ontostandard.org)"}


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


def clean_jats(text: str) -> str:
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


def query_crossref(query_text: str, top_k: int = 10) -> list[dict]:
    q = quote(query_text[:300])
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
        abstract = clean_jats(item.get("abstract", ""))
        if doi and abstract and len(abstract) > 30:
            results.append({
                "doi": doi, "title": title, "abstract": abstract, "source": "crossref",
            })
    return results


def query_openalex(query_text: str, top_k: int = 10) -> list[dict]:
    q = quote(query_text[:300])
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
            results.append({
                "doi": doi, "title": title, "abstract": abstract, "source": "openalex",
            })
    return results


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen = {}
    for p in papers:
        key = p["doi"].lower().strip()
        if key not in seen:
            seen[key] = p
        elif p["source"] == "crossref" and seen[key]["source"] == "openalex":
            # prefer crossref abstract (structured) over openalex (reconstructed)
            seen[key] = p
    return list(seen.values())


# ── main pipeline ────────────────────────────────────────────────────────────

def run(out_path: str):
    _load_model()

    results = []
    print(f"E-bis pipeline: {len(CLAIMS)} claims")
    print(f"Strategy: dual-query (raw + reformulated) → embedding scoring")
    print(f"Output: {out_path}\n")

    for i, c in enumerate(CLAIMS):
        cid = c["id"]
        claim = c["claim"]
        reform = c["reform_query"]
        print(f"[{i+1:2d}/{len(CLAIMS)}] {cid}: {claim[:65]}...")
        print(f"  reform: {reform}")

        # ── dual-query retrieval ──
        # Query 1: raw claim text (what v191 did)
        cr_raw = query_crossref(claim, 10)
        time.sleep(0.5)
        oa_raw = query_openalex(claim, 10)
        time.sleep(0.5)

        # Query 2: reformulated keywords (what v189 did)
        cr_ref = query_crossref(reform, 10)
        time.sleep(0.5)
        oa_ref = query_openalex(reform, 10)
        time.sleep(0.5)

        n_raw = len(cr_raw) + len(oa_raw)
        n_ref = len(cr_ref) + len(oa_ref)
        all_papers = deduplicate_papers(cr_raw + oa_raw + cr_ref + oa_ref)
        print(f"  raw: {n_raw} | reform: {n_ref} | dedup w/abstract: {len(all_papers)}")

        if not all_papers:
            results.append({
                "id": cid, "claim": claim, "reform_query": reform,
                "status": "NO_CANDIDATES",
                "n_raw": n_raw, "n_reform": n_ref, "n_unique": 0,
            })
            print("  -> NO CANDIDATES with abstract")
            continue

        # ── embedding scoring ──
        claim_emb = encode([claim])
        abstracts = [p["abstract"] for p in all_papers]
        abs_embs = encode(abstracts)
        sims = cosine_scores(claim_emb, abs_embs)

        for j, p in enumerate(all_papers):
            p["similarity"] = sims[j]

        ranked = sorted(all_papers, key=lambda x: x["similarity"], reverse=True)
        best = ranked[0]

        # track which query found the best paper
        best_doi_lower = best["doi"].lower().strip()
        raw_dois = {p["doi"].lower().strip() for p in cr_raw + oa_raw}
        ref_dois = {p["doi"].lower().strip() for p in cr_ref + oa_ref}
        found_by = []
        if best_doi_lower in raw_dois:
            found_by.append("raw")
        if best_doi_lower in ref_dois:
            found_by.append("reform")

        result = {
            "id": cid,
            "claim": claim,
            "reform_query": reform,
            "status": "MATCHED",
            "best_doi": best["doi"],
            "best_title": best["title"],
            "best_abstract": best["abstract"][:3000],
            "best_similarity": best["similarity"],
            "best_source": best["source"],
            "best_found_by": "+".join(found_by) if found_by else "unknown",
            "n_raw": n_raw,
            "n_reform": n_ref,
            "n_unique": len(all_papers),
            "top3": [
                {"doi": r["doi"], "title": r["title"][:80], "sim": r["similarity"]}
                for r in ranked[:3]
            ],
        }
        results.append(result)

        print(f"  -> BEST: sim={best['similarity']:.4f}  [{'+'.join(found_by)}]")
        print(f"     {best['title'][:70]}")
        if len(ranked) >= 2:
            print(f"     #2: sim={ranked[1]['similarity']:.4f}  {ranked[1]['title'][:60]}")

    # ── write output ──
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ── summary ──
    matched = [r for r in results if r["status"] == "MATCHED"]
    no_cand = [r for r in results if r["status"] == "NO_CANDIDATES"]

    # source attribution
    raw_only = sum(1 for r in matched if r.get("best_found_by") == "raw")
    ref_only = sum(1 for r in matched if r.get("best_found_by") == "reform")
    both = sum(1 for r in matched if r.get("best_found_by") == "raw+reform")

    print(f"\n{'='*60}")
    print(f"E-BIS SUMMARY")
    print(f"  Claims:         {len(results)}")
    print(f"  Matched:        {len(matched)}")
    print(f"  No candidates:  {len(no_cand)}")
    print(f"  ---")
    print(f"  Best found by raw only:    {raw_only}")
    print(f"  Best found by reform only: {ref_only}")
    print(f"  Best found by both:        {both}")
    if matched:
        avg_sim = sum(r["best_similarity"] for r in matched) / len(matched)
        print(f"  Avg best similarity:       {avg_sim:.4f}")
    print(f"\nOutput: {out}")
    print(f"\nNEXT: upload {out.name} to Claude for B2 inline eval -> support_supply")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E-bis: reformulation + embedding scoring")
    parser.add_argument("--run", action="store_true", required=True)
    parser.add_argument("--out", default="eval/reform_embed_results_v1.jsonl")
    args = parser.parse_args()
    run(args.out)
