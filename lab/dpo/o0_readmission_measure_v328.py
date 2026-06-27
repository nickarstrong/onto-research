#!/usr/bin/env python3
# o0_readmission_measure_v328.py
# v328 TYPE-B: read-only measurement of MEMORY->GOLD RE-ADMISSION over the FROZEN held-out.
# Re-runs the CERTIFIED gate route(verdict, grounded) (v324, C26D5146) on the updated tuple of
# each frozen row; scores the SIX pre-registered v326 bars. Reuses the o0_tiering_measure_v325
# pattern. NO build, NO new design, NO threshold weakening.
#
# Hermetic: pure routing, no network, no GPU, no L2/oracle. Deterministic outputs (no timestamps)
# => two cold offline runs byte-identical (RA-hermetic evidence).
#
# Run from C:\Projects\onto-research\lab\dpo:
#   python o0_readmission_measure_v328.py
# Inputs (frozen, on disk):
#   o0_tiering_gate_v324.py            route(verdict, grounded) -> {GOLD|MEMORY|REJECT}
#   readmission_heldout_v327.jsonl     md5 9CEC01392BFB991EBC92F967AD7A660F (25 rows, 4 RA-buckets)
# Outputs:
#   readmission_gate_report_v328.jsonl LOCAL per-row routing (sorted, sort_keys, LF; has ids -> KEEP-LOCAL)
#   eval/READMISSION_bars_E328.md      PUBLIC-BOUND eval report (aggregate only; NO ids, NO claim text)
#
# Compare semantics: route() is compared to row['expected_tier'] (the v326 PRE-REGISTRATION),
# NOT to row['reroute_actual'] (the build's own answer). route()==route() would be a tautology.
#
# Pre-registered bars (v326 sec 2; FIXED before this measurement):
#   RA-floor              : 0 GOLD-routed rows on tuple != (CLEAN, True)     (ABSOLUTE)
#   RA-ungrounded-promote : all 5 RA-ungrounded -> GOLD                      (LIVENESS)
#   RA-abstain-stays      : all 10 RA-abstain -> MEMORY, 0 GOLD              (ABSOLUTE, (C) terminal)
#   RA-reject-stays       : all 5 RA-reject -> REJECT, 0 MEMORY/GOLD         (ABSOLUTE, poison-loop)
#   RA-idempotent         : double re-route identical for all 25; 5 RA-idempotent -> GOLD; no MEMORY<-GOLD
#   RA-hermetic           : report byte-identical across two cold runs (re-run md5 compare)

from __future__ import annotations
import hashlib
import json
import os
import sys
from collections import Counter

import o0_tiering_gate_v324 as gate

HELDOUT = "readmission_heldout_v327.jsonl"
PERROW_REPORT = "readmission_gate_report_v328.jsonl"  # LOCAL (has ids)
EVAL_MD = os.path.join("eval", "READMISSION_bars_E328.md")  # PUBLIC-BOUND (aggregate only)
GATE_SRC = "o0_tiering_gate_v324.py"

EXPECT_HELDOUT_MD5 = "9CEC01392BFB991EBC92F967AD7A660F"  # HARD staleness guard

RA_EXPECT = {"RA-ungrounded": 5, "RA-abstain": 10, "RA-idempotent": 5, "RA-reject": 5}
TOTAL_EXPECT = 25


def _md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main():
    # --- HARD staleness guard: held-out byte-identity ------------------------
    ho_md5 = _md5_file(HELDOUT)
    if ho_md5 != EXPECT_HELDOUT_MD5:
        print("STOP: held-out md5 %s != expected %s (substrate drift)." % (ho_md5, EXPECT_HELDOUT_MD5))
        sys.exit(2)
    gate_md5 = _md5_file(GATE_SRC)

    rows = []
    with open(HELDOUT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    # --- route (Phase-2 hermetic re-run) -------------------------------------
    out = []
    for r in rows:
        routed = gate.route(r["verdict"], r.get("grounded", False))
        routed2 = gate.route(r["verdict"], r.get("grounded", False))  # idempotent re-route
        out.append({
            "id": r["id"],
            "ra_bucket": r["ra_bucket"],
            "origin_bucket": r.get("origin_bucket"),
            "verdict": r["verdict"],
            "grounded": r.get("grounded"),
            "expected_tier": r["expected_tier"],
            "routed_tier": routed,
            "routed_tier_rerun": routed2,
            "match": routed == r["expected_tier"],
            "idem": routed == routed2,
        })

    out.sort(key=lambda x: x["id"])

    # --- per-row LOCAL report (deterministic; has ids -> KEEP-LOCAL) ----------
    with open(PERROW_REPORT, "w", encoding="utf-8", newline="\n") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=True, sort_keys=True) + "\n")
    perrow_md5 = _md5_file(PERROW_REPORT)

    # --- aggregates ----------------------------------------------------------
    ra_counts = Counter(x["ra_bucket"] for x in out)
    tier_tally = Counter(x["routed_tier"] for x in out)
    matched = sum(1 for x in out if x["match"])

    def cnt(bucket, tier):
        return sum(1 for x in out if x["ra_bucket"] == bucket and x["routed_tier"] == tier)

    # --- bar scoring ---------------------------------------------------------
    gold_rows = [x for x in out if x["routed_tier"] == "GOLD"]
    floor_violations = [x for x in gold_rows
                        if not (x["verdict"] == "CLEAN" and x["grounded"] is True)]
    b_floor = (len(floor_violations) == 0)

    ung_gold = cnt("RA-ungrounded", "GOLD")
    b_ung = (ra_counts["RA-ungrounded"] == 5 and ung_gold == 5)

    abs_mem = cnt("RA-abstain", "MEMORY")
    abs_gold = cnt("RA-abstain", "GOLD")
    b_abs = (ra_counts["RA-abstain"] == 10 and abs_mem == 10 and abs_gold == 0)

    rej_rej = cnt("RA-reject", "REJECT")
    rej_leak = cnt("RA-reject", "MEMORY") + cnt("RA-reject", "GOLD")
    b_rej = (ra_counts["RA-reject"] == 5 and rej_rej == 5 and rej_leak == 0)

    idem_gold = cnt("RA-idempotent", "GOLD")
    double_ok = all(x["idem"] for x in out)
    # no MEMORY<-GOLD edge: no row GOLD on run1 then MEMORY on run2 (covered by double_ok; explicit)
    no_back_edge = not any(x["routed_tier"] == "GOLD" and x["routed_tier_rerun"] == "MEMORY" for x in out)
    b_idem = (ra_counts["RA-idempotent"] == 5 and idem_gold == 5 and double_ok and no_back_edge)

    # RA-hermetic: report byte-identity across two cold runs (Tommy double-run md5 compare).
    # Within one run we assert determinism property holds; verdict GREEN requires the external
    # double-run md5 match. Here we self-report perrow_md5 for that compare.
    b_herm_intrinsic = (
        ra_counts == Counter(RA_EXPECT) and len(out) == TOTAL_EXPECT
    )

    all_match = matched == len(out)
    formal_green = b_floor and b_ung and b_abs and b_rej and b_idem and b_herm_intrinsic and all_match

    # --- eval .md (PUBLIC-BOUND; aggregate only; NO ids, NO claim text, NO timestamp) ---
    def g(flag):
        return "GREEN" if flag else "RED"

    lines = []
    lines.append("# READMISSION_bars_E328 -- MEMORY->GOLD re-admission MEASURE (TYPE-B, aggregate)")
    lines.append("")
    lines.append("> Public-bound eval (E325 pattern): mechanism + aggregate counts + checksums ONLY.")
    lines.append("> NO held-out claim text, NO row ids. Held-out + harness NEVER public.")
    lines.append("> Re-run of certified gate route(verdict, grounded) (v324) over frozen held-out;")
    lines.append("> compared to v326 PRE-REGISTERED expected_tier (not the build's reroute_actual).")
    lines.append("")
    lines.append("## inputs")
    lines.append("- held-out md5: %s (expect 9CEC0139..., 25 rows)" % ho_md5)
    lines.append("- gate src md5: %s (o0_tiering_gate_v324.py)" % gate_md5)
    lines.append("- rows: %d" % len(out))
    lines.append("- RA-bucket counts: %s" % dict(sorted(ra_counts.items())))
    lines.append("- routed-tier tally: %s" % dict(sorted(tier_tally.items())))
    lines.append("- expected-tier match: %d/%d" % (matched, len(out)))
    lines.append("")
    lines.append("## bars (v326 sec 2, pre-registered; falsifier-first, no threshold weakening)")
    lines.append("- RA-floor              : %s  (GOLD rows on tuple != (CLEAN,True) = %d; ABSOLUTE)" % (g(b_floor), len(floor_violations)))
    lines.append("- RA-ungrounded-promote : %s  (RA-ungrounded -> GOLD = %d/5)" % (g(b_ung), ung_gold))
    lines.append("- RA-abstain-stays      : %s  (RA-abstain -> MEMORY = %d/10, -> GOLD = %d; ABSOLUTE)" % (g(b_abs), abs_mem, abs_gold))
    lines.append("- RA-reject-stays       : %s  (RA-reject -> REJECT = %d/5, leak = %d; ABSOLUTE)" % (g(b_rej), rej_rej, rej_leak))
    lines.append("- RA-idempotent         : %s  (RA-idempotent -> GOLD = %d/5, double-route identical = %s, no MEMORY<-GOLD = %s)" % (g(b_idem), idem_gold, double_ok, no_back_edge))
    lines.append("- RA-hermetic           : %s  (counts/shape consistent; report md5 below; CONFIRM by 2-cold-run md5 compare)" % g(b_herm_intrinsic))
    lines.append("")
    lines.append("## formal result")
    lines.append("- FORMAL (5 intrinsic bars + match): %s" % ("ALL-GREEN" if formal_green else "REFUTED"))
    lines.append("- RA-hermetic final verdict: GREEN iff this report's md5 is identical across two cold runs.")
    lines.append("")
    lines.append("## checksums")
    lines.append("- per-row report md5 (LOCAL): %s" % perrow_md5)
    lines.append("- held-out md5: %s" % ho_md5)
    lines.append("- gate src md5: %s" % gate_md5)
    if not formal_green:
        lines.append("")
        lines.append("## mismatches (aggregate; falsifier-first)")
        mm = Counter(x["ra_bucket"] for x in out if not x["match"])
        lines.append("- mismatched rows by RA-bucket: %s" % dict(sorted(mm.items())))

    os.makedirs("eval", exist_ok=True)
    with open(EVAL_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    eval_md5 = _md5_file(EVAL_MD)

    # --- stdout summary ------------------------------------------------------
    print("rows=%d  RA-buckets=%s" % (len(out), dict(sorted(ra_counts.items()))))
    print("routed_tiers=%s  match=%d/%d" % (dict(sorted(tier_tally.items())), matched, len(out)))
    print("--- BARS (pre-registered v326) ---")
    print("RA-floor              : %s  (illegal-GOLD=%d)" % (g(b_floor), len(floor_violations)))
    print("RA-ungrounded-promote : %s  (%d/5 -> GOLD)" % (g(b_ung), ung_gold))
    print("RA-abstain-stays      : %s  (MEMORY=%d/10 GOLD=%d)" % (g(b_abs), abs_mem, abs_gold))
    print("RA-reject-stays       : %s  (REJECT=%d/5 leak=%d)" % (g(b_rej), rej_rej, rej_leak))
    print("RA-idempotent         : %s  (GOLD=%d/5 dbl=%s noBackEdge=%s)" % (g(b_idem), idem_gold, double_ok, no_back_edge))
    print("RA-hermetic(intrinsic): %s  (confirm via 2-cold-run md5)" % g(b_herm_intrinsic))
    print("--- checksums ---")
    print("eval_md_md5    = %s" % eval_md5)
    print("perrow_md5     = %s" % perrow_md5)
    print("heldout_md5    = %s" % ho_md5)
    print("OVERALL FORMAL : %s" % ("ALL-GREEN -> RA-hermetic pending 2-run md5; then Founder-gate commit."
                                   if formal_green else "REFUTED -> diagnose, NO commit, NO threshold weakening."))
    if not formal_green:
        for x in out:
            if not x["match"]:
                print("  MISMATCH:", {"id": x["id"], "ra_bucket": x["ra_bucket"],
                                      "verdict": x["verdict"], "grounded": x["grounded"],
                                      "expected": x["expected_tier"], "routed": x["routed_tier"]})
        sys.exit(1)


if __name__ == "__main__":
    main()
