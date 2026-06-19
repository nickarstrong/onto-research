#!/usr/bin/env python3
"""
generate_model_claims_v1.py — Track C Step 1: Model-Generated Claims

Prompts substrate (via ollama) with diverse questions, extracts one
factual claim per answer. Output = JSONL compatible with
retrieval_proposer_v1.py --claims.

Usage:
  python generate_model_claims_v1.py --run
  python generate_model_claims_v1.py --run --model gemma3:4e4b
  python generate_model_claims_v1.py --summary model_claims_v1.jsonl

Output: model_claims_v1.jsonl
Requires: ollama running locally (localhost:11434).
"""

import argparse, json, os, re, sys, time
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:7b"

# 20 prompts designed to elicit specific factual claims.
# Diverse domains, no overlap with v188 hand-written set.
# Each prompt asks for ONE specific fact — short answer expected.
PROMPTS = [
    "What is the half-life of carbon-14 and why is it useful?",
    "What did the Voyager 1 spacecraft discover about Jupiter's moons?",
    "How does metformin work as a diabetes treatment?",
    "What is the Mpemba effect and has it been experimentally confirmed?",
    "What are the health effects of long-term exposure to particulate matter PM2.5?",
    "What is the significance of the Higgs boson discovery at CERN?",
    "How effective are mRNA vaccines compared to traditional vaccine platforms?",
    "What is the current scientific consensus on the age of the universe?",
    "How does CRISPR-Cas13 differ from CRISPR-Cas9?",
    "What role does dopamine play in addiction according to current neuroscience?",
    "What is the evidence for dark matter in galaxy rotation curves?",
    "How does ocean thermal energy conversion work and what is its efficiency?",
    "What is the measured rate of Arctic sea ice decline?",
    "What are the main findings of the Human Microbiome Project?",
    "How does lithium act as a mood stabilizer at the molecular level?",
    "What is the Fermi paradox and what are the leading proposed resolutions?",
    "What evidence supports plate tectonics as the mechanism for continental drift?",
    "What is the current state of quantum error correction?",
    "How does glyphosate affect non-target organisms in the environment?",
    "What is the measured expansion rate of the universe (Hubble constant)?",
]

SYSTEM = (
    "You are a knowledgeable assistant. Answer the question with one specific, "
    "concrete factual claim supported by scientific evidence. Be precise: include "
    "numbers, dates, or specific findings where relevant. Keep your answer to 1-3 "
    "sentences. Do not hedge or add disclaimers."
)


def ollama_generate(prompt, model, system=SYSTEM):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 256},
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        print(f"    ollama error: {e}")
        return ""


def extract_claim(response):
    """Take first 1-2 sentences as the core claim."""
    if not response:
        return ""
    # Split on sentence boundaries
    sents = re.split(r'(?<=[.!?])\s+', response.strip())
    # Take first 2 sentences max
    claim = " ".join(sents[:2]).strip()
    # Remove any leading "Answer:" or similar
    claim = re.sub(r'^(Answer|Response|Claim)[:\s]*', '', claim, flags=re.I)
    return claim


def run(model, outdir):
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "model_claims_v1.jsonl")
    results = []

    print(f"Model: {model}")
    print(f"Claims to generate: {len(PROMPTS)}")
    print(f"Output: {outpath}\n")

    for i, prompt in enumerate(PROMPTS):
        print(f"[{i+1:2d}/{len(PROMPTS)}] {prompt[:65]}...")
        t0 = time.time()
        raw = ollama_generate(prompt, model)
        dt = time.time() - t0

        claim = extract_claim(raw)
        entry = {
            "id": f"mc{i:02d}",
            "claim": claim,
            "prompt": prompt,
            "raw_response": raw,
            "substrate": model,
            "gen_time_s": round(dt, 1),
        }
        results.append(entry)

        if claim:
            print(f"  => {claim[:90]}")
        else:
            print(f"  => EMPTY")
        print(f"  ({dt:.1f}s)")

    with open(outpath, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Summary
    non_empty = sum(1 for r in results if r["claim"])
    total_time = sum(r["gen_time_s"] for r in results)
    print(f"\n{'='*60}")
    print(f"  Total:       {len(results)}")
    print(f"  Non-empty:   {non_empty}/{len(results)}")
    print(f"  Empty:       {len(results) - non_empty}/{len(results)}")
    print(f"  Total time:  {total_time:.0f}s")
    print(f"  Output:      {outpath}")
    print(f"{'='*60}")


def show_summary(path):
    results = []
    with open(path) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    non_empty = sum(1 for r in results if r.get("claim"))
    print(f"Claims: {len(results)}, non-empty: {non_empty}")
    for r in results:
        tag = "OK" if r.get("claim") else "EMPTY"
        print(f"  [{r['id']}] {tag:5s} {r.get('claim', '')[:80]}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Track C: Generate model claims")
    p.add_argument("--run", action="store_true")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--summary", type=str)
    p.add_argument("--outdir", default=".")
    a = p.parse_args()

    if a.run:
        run(a.model, a.outdir)
    elif a.summary:
        show_summary(a.summary)
    else:
        p.print_help()
