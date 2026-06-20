#!/usr/bin/env python3
"""
o0_loop.py — organism-0 loop orchestrator (steps 1-4)

Runs the Crown pipeline WITHOUT B2 judging:
  topic → propose (Ollama) → reformulate (Ollama) → retrieve (Crossref+OpenAlex)
  → embedding score (MiniLM CPU) → gate (DOI resolve + retraction) → enriched JSONL

Output = enriched JSONL ready for B2 session (Claude judges batch in S2).
Each record stores best_abstract so B2 can judge without re-fetching.

Usage:
  python o0_loop.py --run                          # 100 cycles, default output
  python o0_loop.py --run --n 150 --out eval/o0/o0_enriched.jsonl
  python o0_loop.py --run --n 100 --resume         # resume from existing output

Prereqs:
  - Ollama running locally: qwen2.5-coder:7b loaded
  - pip: torch transformers (CPU, for embedding)
  - Run from onto-research/lab/dpo/
  - o0_domain_list.py, rung1_wiring_v0.py, rung1_build_topics.py in same dir

Binds: CONCEPT_organism0_v1.md §2 steps 1-5.
Does NOT: B2 judge (that's S2 session), learn (S3), report (S4).
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Pipeline functions (frozen interface from rung1_wiring_v0.py)
from rung1_wiring_v0 import (
    generate_claim,
    reformulate_claim,
    retrieve_best_paper,
    gate_check,
    ollama_generate,
)
from o0_domain_list import DOMAIN_TOPICS
from o0_contact import emit as contact_emit


# ════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════

DEFAULT_OUT = "eval/o0/o0_enriched.jsonl"
PLATEAU_WINDOW = 10  # consecutive gate-level rejects → PLATEAU contact


# ════════════════════════════════════════════════════════════════════
# LOOP
# ════════════════════════════════════════════════════════════════════

def run_loop(n_cycles=100, out_path=DEFAULT_OUT, resume=False):
    """Run organism-0 steps 1-4 for n_cycles topics.

    Each cycle:
      1. Select topic (sequential from DOMAIN_TOPICS)
      2. Generate claim (Ollama)
      3. Reformulate → search keywords (Ollama)
      4. Retrieve best paper (Crossref + OpenAlex + embedding)
      5. Gate check (DOI resolve + retraction)
      → Write enriched record (with abstract for B2)

    Returns 0 on success.
    """
    if n_cycles > len(DOMAIN_TOPICS):
        print(f"WARNING: n_cycles={n_cycles} > DOMAIN_TOPICS={len(DOMAIN_TOPICS)}, "
              f"capping at {len(DOMAIN_TOPICS)}")
        n_cycles = len(DOMAIN_TOPICS)

    topics = DOMAIN_TOPICS[:n_cycles]

    # Pre-flight: Ollama reachable?
    try:
        ollama_generate("Say OK", timeout=15)
    except Exception as e:
        sys.exit(f"FATAL: Ollama not reachable — {e}")

    # Resume support
    done_ids = set()
    if resume and Path(out_path).exists():
        with open(out_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    done_ids.add(rec["id"])
        print(f"  [resume] {len(done_ids)} already processed, skipping")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Truncate on fresh start; append on resume
    if not resume:
        open(out, "w").close()

    # ── Banner ──
    print("=" * 70)
    print("ORGANISM-0 LOOP — Steps 1-4 (enrichment for B2)")
    print(f"  proposer:  Ollama qwen2.5-coder:7b")
    print(f"  scorer:    all-MiniLM-L6-v2 (CPU)")
    print(f"  topics:    {len(topics)} from o0_domain_list.py")
    print(f"  output:    {out_path}")
    print(f"  resume:    {resume} ({len(done_ids)} done)")
    print("=" * 70)

    # ── Main loop ──
    stats = {"total": 0, "pending_b2": 0, "reject": 0, "error": 0,
             "gate_pass": 0, "gate_reject": 0}
    errors = []
    consec_reject = 0
    t_start = time.time()

    for i, topic in enumerate(topics):
        cid = f"o0_{i:03d}"
        if cid in done_ids:
            continue

        print(f"\n[{i+1}/{len(topics)}] {cid} — {topic}")
        stats["total"] += 1

        rec = {
            "id": cid,
            "topic": topic,
            "claim": None,
            "reform_query": None,
            "retrieval": None,
            "best_abstract": None,
            "gate": None,
            "s2b": None,
            "verdict": None,
            "error": None,
            "ts": datetime.now(timezone.utc).isoformat(),
        }

        # ── Step 1: PROPOSE ──
        try:
            claim = generate_claim(topic)
            rec["claim"] = claim
            print(f"  [propose] {claim[:90]}...")
        except Exception as e:
            rec["error"] = f"proposer_error: {e}"
            rec["verdict"] = "ERROR"
            stats["error"] += 1
            errors.append(cid)
            contact_emit("GEN_FAIL", i, f"Ollama proposer error: {e}")
            _append(out, rec)
            continue

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
                consec_reject += 1
                _append(out, rec)
                print("  [retrieve] NO CANDIDATES → REJECT")
                _check_plateau(consec_reject, i)
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
                consec_reject += 1
                _append(out, rec)
                print(f"  [gate]    REJECT ({reason})")
                _check_plateau(consec_reject, i)
                continue
            stats["gate_pass"] += 1
            consec_reject = 0
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

        # ── Gate passed → PENDING_B2 ──
        rec["verdict"] = "PENDING_B2"
        stats["pending_b2"] += 1
        _append(out, rec)
        print(f"  [VERDICT] PENDING_B2 (awaits B2 session)")

    # ── Summary ──
    elapsed = time.time() - t_start
    _print_summary(stats, errors, out, elapsed)
    return 0


def _append(path, rec):
    """Append one record to JSONL (crash-safe: flush per record)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _check_plateau(consec, cycle):
    """Emit PLATEAU contact if consecutive gate-level rejects >= window."""
    if consec >= PLATEAU_WINDOW:
        contact_emit("PLATEAU", cycle,
                     f"{consec} consecutive gate-level rejects")


def _print_summary(stats, errors, out, elapsed):
    s = stats
    total = s["total"]
    print("\n" + "=" * 70)
    print("ORGANISM-0 LOOP SUMMARY")
    print("=" * 70)
    print(f"  Total cycles:      {total}")
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
    print("NEXT: upload o0_enriched.jsonl → Claude B2 session (S2)")
    print("      Claude judges PENDING_B2 records → b2_verdicts.jsonl")
    print("      python o0_accumulator.py integrate <enriched> <verdicts>")


# ════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="organism-0 loop (steps 1-4)")
    ap.add_argument("--run", action="store_true",
                    help="Run the enrichment loop")
    ap.add_argument("--n", type=int, default=100,
                    help="Number of cycles (default 100, max %d)" % len(DOMAIN_TOPICS))
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="Output JSONL path")
    ap.add_argument("--resume", action="store_true",
                    help="Resume from existing output (skip done IDs)")
    args = ap.parse_args()

    if not args.run:
        ap.print_help()
        sys.exit(0)

    raise SystemExit(run_loop(n_cycles=args.n, out_path=args.out, resume=args.resume))
