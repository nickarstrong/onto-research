#!/usr/bin/env python3
"""o0_subclaim_probe.py -- Sub-claim decomposition probe for Crown granularity fix.

Takes 5 S4 claims (2 DIRTY + 3 CLEAN), decomposes into atomic sub-claims via Ollama,
runs per-subclaim retrieval pipeline (reform -> retrieve -> gate), outputs enriched
subclaims for B2 judging.

Usage:
  python o0_subclaim_probe.py --heldout eval/o0/o0_heldout_gen.jsonl --out eval/o0/o0_subclaim_probe.jsonl

Requires: Ollama (qwen2.5-coder:7b), rung1_wiring_v0.py in same dir, internet.
"""

import json, sys, time, argparse, requests

from rung1_wiring_v0 import reformulate_claim, retrieve_best_paper, gate_check

PROBE_IDS = ["heldout_03", "heldout_09", "heldout_14", "heldout_16", "heldout_18"]

DECOMPOSE_SYS = (
    "You are a scientific fact extractor. Your ONLY job is to split a compound "
    "scientific claim into atomic verifiable facts. Follow the rules exactly."
)

DECOMPOSE_PROMPT = """Break this scientific claim into atomic verifiable facts.

RULES:
- Each fact must contain exactly ONE specific detail (a date, a name, a number, or a mechanism).
- Each fact must be independently verifiable from a single scientific source.
- Do NOT add information not present in the original claim.
- Do NOT omit any dates, names, numbers, or mechanisms from the original.
- Do NOT add commentary or explanation.
- Output one fact per line. No numbering, no bullets, no blank lines.

Claim: {claim}
Atomic facts:"""


def decompose_claim(claim_text, model="qwen2.5-coder:7b"):
    """Decompose a compound claim into atomic sub-claims via Ollama."""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": DECOMPOSE_PROMPT.format(claim=claim_text),
            "system": DECOMPOSE_SYS,
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 512},
        },
        timeout=120,
    )
    resp.raise_for_status()
    raw = resp.json()["response"].strip()
    subclaims = [line.strip() for line in raw.split("\n") if line.strip()]
    return subclaims, raw


def extract_claim_text(rec):
    """Try multiple field names for claim text."""
    for key in ("claim", "text", "completion", "generated_text", "output"):
        if key in rec and rec[key]:
            return rec[key]
    return None


def run_subclaim_pipeline(subclaim_text, idx):
    """Run reform -> retrieve -> gate for one sub-claim. Returns result dict."""
    result = {"subclaim_idx": idx, "subclaim": subclaim_text}

    # Reform
    try:
        keywords = reformulate_claim(subclaim_text)
        result["keywords"] = keywords
        print(f"      Reform: {keywords}")
    except Exception as e:
        result["error"] = f"reform: {e}"
        result["verdict"] = "ERROR"
        print(f"      Reform ERROR: {e}")
        return result

    # Retrieve
    try:
        paper, retr_stats = retrieve_best_paper(subclaim_text, keywords)
        if paper and paper.get("doi"):
            result["doi"] = paper.get("doi")
            result["title"] = paper.get("title")
            result["abstract"] = paper.get("abstract", "")
            result["similarity"] = paper.get("similarity")
            print(
                f"      Retrieved: {paper.get('title','?')[:60]}... "
                f"(sim={paper.get('similarity', 0):.3f})"
            )
        else:
            result["gate"] = "NO_CANDIDATES"
            result["verdict"] = "REJECT"
            print(f"      Retrieved: NO CANDIDATES")
            return result
    except Exception as e:
        result["error"] = f"retrieve: {e}"
        result["verdict"] = "ERROR"
        print(f"      Retrieve ERROR: {e}")
        return result

    # Gate
    try:
        gate_pass, gate_reason_str = gate_check(result["doi"])
        result["gate"] = "PASS" if gate_pass else "REJECT"
        result["gate_reason"] = gate_reason_str
        result["verdict"] = "PENDING_B2" if gate_pass else "REJECT"
        print(
            f"      Gate: {'PASS' if gate_pass else 'REJECT'} "
            f"({gate_reason_str})"
        )
    except Exception as e:
        result["gate"] = "ERROR"
        result["gate_reason"] = str(e)
        result["verdict"] = "ERROR"
        print(f"      Gate ERROR: {e}")

    return result


def main():
    ap = argparse.ArgumentParser(description="Sub-claim decomposition probe")
    ap.add_argument("--heldout", required=True, help="Path to o0_heldout_gen.jsonl")
    ap.add_argument("--out", required=True, help="Output JSONL path")
    args = ap.parse_args()

    # Load probe claims
    claims = []
    with open(args.heldout, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            rid = rec.get("id", "")
            if rid in PROBE_IDS:
                claims.append(rec)

    print(f"Loaded {len(claims)}/{len(PROBE_IDS)} probe claims")
    if len(claims) != len(PROBE_IDS):
        missing = set(PROBE_IDS) - {r.get("id") for r in claims}
        print(f"  MISSING: {missing}")
        if not claims:
            print("FATAL: no claims loaded. Check --heldout path and ID field.")
            sys.exit(1)

    # Sort by ID for reproducibility
    claims.sort(key=lambda r: r.get("id", ""))

    results = []
    for rec in claims:
        claim_id = rec.get("id", "?")
        claim_text = extract_claim_text(rec)
        if not claim_text:
            print(f"\n[{claim_id}] ERROR: no claim text found. Fields: {list(rec.keys())}")
            continue

        print(f"\n{'=' * 70}")
        print(f"[{claim_id}] {claim_text[:120]}...")

        # Step 1: Decompose
        subclaims, raw_decomp = decompose_claim(claim_text)
        print(f"  Decomposed into {len(subclaims)} sub-claims:")
        for i, sc in enumerate(subclaims):
            print(f"    [{i}] {sc}")

        # Step 2-4: Per sub-claim pipeline
        subclaim_results = []
        for i, sc in enumerate(subclaims):
            print(f"\n    --- Sub-claim [{i}]: {sc[:80]}...")
            sr = run_subclaim_pipeline(sc, i)
            subclaim_results.append(sr)
            time.sleep(1)  # rate limit

        parent = {
            "parent_id": claim_id,
            "parent_claim": claim_text,
            "raw_decomposition": raw_decomp,
            "n_subclaims": len(subclaims),
            "subclaims": subclaim_results,
            "n_gate_pass": sum(1 for s in subclaim_results if s.get("gate") == "PASS"),
            "n_pending_b2": sum(
                1 for s in subclaim_results if s.get("verdict") == "PENDING_B2"
            ),
            "n_reject_pre_b2": sum(
                1 for s in subclaim_results if s.get("verdict") == "REJECT"
            ),
            "n_error": sum(
                1 for s in subclaim_results if s.get("verdict") == "ERROR"
            ),
        }
        results.append(parent)

        print(f"\n  PARENT [{claim_id}]: {parent['n_subclaims']} sub-claims | "
              f"gate-pass={parent['n_gate_pass']} | "
              f"PENDING_B2={parent['n_pending_b2']} | "
              f"REJECT={parent['n_reject_pre_b2']} | "
              f"ERROR={parent['n_error']}")

    # Write
    with open(args.out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(results)} parent results to {args.out}")

    # Final summary
    print(f"\n{'=' * 70}")
    print("PROBE SUMMARY")
    print(f"{'=' * 70}")
    total_subclaims = sum(r["n_subclaims"] for r in results)
    total_pending = sum(r["n_pending_b2"] for r in results)
    total_reject = sum(r["n_reject_pre_b2"] for r in results)
    total_error = sum(r["n_error"] for r in results)
    for r in results:
        print(
            f"  {r['parent_id']}: {r['n_subclaims']} sub-claims, "
            f"{r['n_pending_b2']} PENDING_B2, {r['n_reject_pre_b2']} REJECT"
        )
    print(f"\n  TOTAL: {total_subclaims} sub-claims, "
          f"{total_pending} PENDING_B2, {total_reject} pre-B2 REJECT, {total_error} ERROR")
    print(f"\n  Next: upload {args.out} -> Claude B2 judges PENDING_B2 sub-claims")


if __name__ == "__main__":
    main()


