#!/usr/bin/env python3
"""
o0_s4_validate.py -- organism-0 S4 validation pipeline

Push 20 post-LoRA held-out claims through Crown steps 2-5:
  reformulate (Ollama) -> retrieve (Crossref+OpenAlex+embedding) -> gate (DOI)
  -> enriched JSONL ready for B2 batch judging.

Does NOT generate claims (they exist in o0_heldout_gen.jsonl from S3).
Does NOT judge (Claude B2 in session).

Usage:
  python o0_s4_validate.py --run
  python o0_s4_validate.py --run --input eval/o0/o0_heldout_gen.jsonl --out eval/o0/o0_s4_enriched.jsonl

Prereqs:
  - Ollama running locally: qwen2.5-coder:7b loaded
  - pip: torch transformers (CPU, for embedding)
  - Run from onto-research/lab/dpo/
  - rung1_wiring_v0.py, rung1_build_topics.py in same dir

Binds: CONCEPT_organism0_v1.md sec 3 (validation after LoRA).
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Pipeline functions (frozen interface from rung1_wiring_v0.py)
from rung1_wiring_v0 import (
    reformulate_claim,
    retrieve_best_paper,
    gate_check,
    ollama_generate,
)

# ════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════

DEFAULT_INPUT = "eval/o0/o0_heldout_gen.jsonl"
DEFAULT_OUT = "eval/o0/o0_s4_enriched.jsonl"


# ════════════════════════════════════════════════════════════════════
# PIPELINE
# ════════════════════════════════════════════════════════════════════

def run_validation(input_path=DEFAULT_INPUT, out_path=DEFAULT_OUT):
    """Push pre-generated claims through reform -> retrieve -> gate.

    Reads claims from input_path (o0_heldout_gen.jsonl format).
    Writes enriched records with best_abstract for B2 judging.
    """
    # Load claims
    claims = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                claims.append(json.loads(line))

    if not claims:
        sys.exit(f"FATAL: no claims in {input_path}")

    # Pre-flight: Ollama reachable?
    try:
        ollama_generate("Say OK", timeout=15)
    except Exception as e:
        sys.exit(f"FATAL: Ollama not reachable — {e}")

    # Banner
    print("=" * 70)
    print("ORGANISM-0 S4 VALIDATION PIPELINE")
    print(f"  input:     {input_path} ({len(claims)} claims)")
    print(f"  source:    post_lora (pre-generated, NOT proposing)")
    print(f"  pipeline:  reform -> retrieve -> gate -> enriched")
    print(f"  output:    {out_path}")
    print("=" * 70)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    open(out, "w").close()  # fresh start

    stats = {"total": 0, "pending_b2": 0, "reject": 0, "error": 0,
             "gate_pass": 0, "gate_reject": 0}
    errors = []
    t_start = time.time()

    for i, src in enumerate(claims):
        cid = src["id"]
        topic = src["topic"]
        claim = src["claim"]
        stats["total"] += 1

        print(f"\n[{i+1}/{len(claims)}] {cid} — {topic}")
        print(f"  [claim]   {claim[:90]}...")

        rec = {
            "id": cid,
            "topic": topic,
            "claim": claim,
            "source": src.get("source", "post_lora"),
            "adapter": src.get("adapter", ""),
            "reform_query": None,
            "retrieval": None,
            "best_abstract": None,
            "gate": None,
            "verdict": None,
            "error": None,
            "ts": datetime.now(timezone.utc).isoformat(),
        }

        # ── Step 2: REFORMULATE ──
        try:
            reform = reformulate_claim(claim)
            rec["reform_query"] = reform
            print(f"  [reform]  {reform[:90]}")
        except Exception as e:
            reform = " ".join(claim.split()[:8])
            rec["reform_query"] = reform
            print(f"  [reform]  FALLBACK: {reform[:80]}")

        # ── Step 3: RETRIEVE ──
        try:
            best, r_meta = retrieve_best_paper(claim, reform)
            rec["retrieval"] = r_meta
            if best is None:
                rec["verdict"] = "REJECT"
                rec["gate"] = {"passed": False, "reason": "no_retrieval_candidates"}
                stats["reject"] += 1
                stats["gate_reject"] += 1
                _append(out, rec)
                print("  [retrieve] NO CANDIDATES -> REJECT")
                continue
            rec["retrieval"]["best_doi"] = best["doi"]
            rec["retrieval"]["best_title"] = best["title"]
            rec["best_abstract"] = best.get("abstract", "")
            print(f"  [retrieve] sim={best['similarity']:.4f}  DOI={best['doi']}")
            print(f"             {best['title'][:70]}")
        except Exception as e:
            rec["error"] = f"retrieval_error: {e}"
            rec["verdict"] = "ERROR"
            stats["error"] += 1
            errors.append(cid)
            _append(out, rec)
            print(f"  [retrieve] ERROR: {e}")
            continue

        # ── Step 4: GATE (resolve + retraction) ──
        try:
            passed, reason = gate_check(best["doi"])
            rec["gate"] = {"passed": passed, "reason": reason}
            if not passed:
                rec["verdict"] = "REJECT"
                stats["reject"] += 1
                stats["gate_reject"] += 1
                _append(out, rec)
                print(f"  [gate]    REJECT ({reason})")
                continue
            stats["gate_pass"] += 1
            print(f"  [gate]    PASS ({reason})")
            time.sleep(0.3)
        except Exception as e:
            rec["error"] = f"gate_error: {e}"
            rec["verdict"] = "ERROR"
            stats["error"] += 1
            errors.append(cid)
            _append(out, rec)
            print(f"  [gate]    ERROR: {e}")
            continue

        # ── Gate passed -> PENDING_B2 ──
        rec["verdict"] = "PENDING_B2"
        stats["pending_b2"] += 1
        _append(out, rec)
        print(f"  [VERDICT] PENDING_B2 (awaits B2 session)")

    # ── Summary ──
    elapsed = time.time() - t_start
    _print_summary(stats, errors, out, elapsed, len(claims))
    return 0


def _append(path, rec):
    """Append one record to JSONL (crash-safe: flush per record)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _print_summary(stats, errors, out, elapsed, n_input):
    s = stats
    total = s["total"]
    print("\n" + "=" * 70)
    print("S4 VALIDATION PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Input claims:      {n_input}")
    print(f"  Processed:         {total}")
    print(f"  PENDING_B2:        {s['pending_b2']}")
    print(f"  REJECT (pre-B2):   {s['reject']}")
    print(f"  ERROR:             {s['error']}")
    print(f"  ---")
    print(f"  Gate PASS:         {s['gate_pass']}")
    print(f"  Gate REJECT:       {s['gate_reject']}")
    print(f"  ---")
    if total:
        print(f"  B2 supply:         {s['pending_b2']}/{total} "
              f"({s['pending_b2']/total:.3f})")
    print(f"  Elapsed:           {elapsed:.0f}s ({elapsed/max(total,1):.1f}s/cycle)")
    print(f"  Output:            {out}")
    if errors:
        print(f"  Errors:            {', '.join(errors)}")
    print("=" * 70)
    print()
    print("NEXT: upload o0_s4_enriched.jsonl -> Claude B2 session")
    print("      Claude judges PENDING_B2 records -> S4 verdicts")
    print("      Founder labels CLEAN/DIRTY -> gate measurement (G1/G2/G3)")


# ════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="organism-0 S4 validation pipeline")
    ap.add_argument("--run", action="store_true",
                    help="Run validation pipeline on held-out claims")
    ap.add_argument("--input", default=DEFAULT_INPUT,
                    help=f"Input JSONL (default {DEFAULT_INPUT})")
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help=f"Output JSONL (default {DEFAULT_OUT})")
    args = ap.parse_args()

    if not args.run:
        ap.print_help()
        sys.exit(0)

    raise SystemExit(run_validation(input_path=args.input, out_path=args.out))
