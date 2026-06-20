#!/usr/bin/env python3
"""
o0_accumulator.py — organism-0 verdict store + ABSORB buffer

Append-only JSONL audit trail (o0_verdicts.jsonl).
All cycle outcomes are logged: ABSORB, REJECT, ERROR, PENDING_B2.
ABSORB buffer feeds RFT LoRA when |buffer| >= K (default 50).

Usage:
  # As library
  from o0_accumulator import Accumulator
  acc = Accumulator("eval/o0/o0_verdicts.jsonl")
  acc.append(record)
  buf = acc.absorb_buffer(k=50)

  # As CLI — integrate B2 verdicts into enriched records
  python o0_accumulator.py --integrate eval/o0/o0_enriched.jsonl eval/o0/b2_verdicts.jsonl
  python o0_accumulator.py --stats eval/o0/o0_verdicts.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

from o0_contact import emit as contact_emit


class Accumulator:
    """Append-only JSONL verdict store."""

    def __init__(self, path="eval/o0/o0_verdicts.jsonl"):
        self.path = Path(path)
        self.records = []
        self._load()

    def _load(self):
        """Load existing records from file."""
        self.records = []
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.records.append(json.loads(line))

    def append(self, record):
        """Append one record to the audit trail (file + memory)."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.records.append(record)

    def integrate_verdicts(self, enriched_path, b2_verdicts):
        """Merge B2 verdicts into enriched records → append to trail.

        enriched_path : path to o0_enriched.jsonl (from o0_loop.py)
        b2_verdicts   : list of dicts {"id": "o0_XXX", "s2b_verdict": "SUPPORTS/NOT/UNCLEAR",
                                        "reason": "..."}

        Returns list of integrated records.
        """
        # Load enriched records (only PENDING_B2 ones get verdicts)
        enriched = []
        with open(enriched_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    enriched.append(json.loads(line))

        verdict_map = {v["id"]: v for v in b2_verdicts}
        integrated = []

        for rec in enriched:
            rid = rec["id"]

            if rec.get("verdict") in ("REJECT", "ERROR"):
                # Already decided at gate/error level — keep as-is
                self.append(rec)
                integrated.append(rec)
                continue

            if rid in verdict_map:
                v = verdict_map[rid]
                rec["s2b"] = {
                    "verdict": v["s2b_verdict"],
                    "reason": v.get("reason", ""),
                }
                rec["verdict"] = "ABSORB" if v["s2b_verdict"] == "SUPPORTS" else "REJECT"
            else:
                # PENDING_B2 with no verdict — flag as error
                rec["verdict"] = "ERROR"
                rec["error"] = "no_b2_verdict"

            self.append(rec)
            integrated.append(rec)

        # Check PLATEAU after integration
        if self.consecutive_rejects() >= 10:
            last_cycle = integrated[-1].get("id", "?") if integrated else "?"
            contact_emit("PLATEAU", last_cycle,
                         f"10+ consecutive REJECT verdicts (post-B2)")

        return integrated

    # ── Queries ──

    @property
    def absorb_count(self):
        return sum(1 for r in self.records if r.get("verdict") == "ABSORB")

    @property
    def reject_count(self):
        return sum(1 for r in self.records if r.get("verdict") == "REJECT")

    @property
    def error_count(self):
        return sum(1 for r in self.records if r.get("verdict") == "ERROR")

    def absorb_buffer(self, k=50):
        """Return ABSORB records if count >= k, else None."""
        absorbs = [r for r in self.records if r.get("verdict") == "ABSORB"]
        return absorbs if len(absorbs) >= k else None

    def consecutive_rejects(self, window=10):
        """Count of consecutive REJECT verdicts at tail."""
        count = 0
        for r in reversed(self.records):
            if r.get("verdict") == "REJECT":
                count += 1
            else:
                break
        return count

    def stats(self):
        """Return summary counts."""
        total = len(self.records)
        return {
            "total": total,
            "absorb": self.absorb_count,
            "reject": self.reject_count,
            "error": self.error_count,
            "absorb_rate": round(self.absorb_count / total, 3) if total else 0.0,
            "consecutive_rejects_tail": self.consecutive_rejects(),
        }


# ── CLI ──

def _cli_integrate(enriched_path, verdicts_path, out_path):
    """Load B2 verdicts JSONL, integrate, write to accumulator."""
    with open(verdicts_path, "r", encoding="utf-8") as f:
        verdicts = [json.loads(line.strip()) for line in f if line.strip()]

    acc = Accumulator(out_path)
    integrated = acc.integrate_verdicts(enriched_path, verdicts)

    s = acc.stats()
    print("\n" + "=" * 60)
    print("ACCUMULATOR INTEGRATION")
    print("=" * 60)
    print(f"  Integrated:  {len(integrated)} records")
    print(f"  ABSORB:      {s['absorb']}")
    print(f"  REJECT:      {s['reject']}")
    print(f"  ERROR:       {s['error']}")
    print(f"  Absorb rate: {s['absorb_rate']:.3f}")
    print(f"  Trail:       {out_path}")

    buf = acc.absorb_buffer(k=50)
    if buf is not None:
        print(f"  THRESHOLD:   REACHED ({len(buf)} >= 50) — ready for RFT")
    else:
        print(f"  THRESHOLD:   NOT REACHED ({s['absorb']} < 50)")
    print("=" * 60)


def _cli_stats(path):
    """Print stats from existing verdict trail."""
    acc = Accumulator(path)
    s = acc.stats()
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="organism-0 accumulator")
    sub = ap.add_subparsers(dest="cmd")

    p_int = sub.add_parser("integrate", help="Merge B2 verdicts into enriched records")
    p_int.add_argument("enriched", help="Path to o0_enriched.jsonl")
    p_int.add_argument("verdicts", help="Path to b2_verdicts.jsonl")
    p_int.add_argument("--out", default="eval/o0/o0_verdicts.jsonl",
                       help="Verdict trail output (default: eval/o0/o0_verdicts.jsonl)")

    p_st = sub.add_parser("stats", help="Print accumulator stats")
    p_st.add_argument("path", help="Path to o0_verdicts.jsonl")

    args = ap.parse_args()
    if args.cmd == "integrate":
        _cli_integrate(args.enriched, args.verdicts, args.out)
    elif args.cmd == "stats":
        _cli_stats(args.path)
    else:
        ap.print_help()
