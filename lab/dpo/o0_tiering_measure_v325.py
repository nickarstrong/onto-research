#!/usr/bin/env python3
# o0_tiering_measure_v325.py
# v325 TYPE-B: read-only measurement of the FROZEN tiering gate over the FROZEN held-out.
# Scores the 5 pre-registered bars (design sec 2). NO build, NO threshold weakening, NO new design.
# Hermetic: pure routing, no network, no GPU. Deterministic report (T-hermetic).
#
# Run from C:\Projects\onto-research\lab\dpo:
#   python o0_tiering_measure_v325.py
# Inputs (frozen, on disk):
#   o0_tiering_gate_v324.py            route_row(row) -> {GOLD|MEMORY|REJECT}
#   tiering_heldout_v324.jsonl         md5 CABA277117FCC121B5C00E49A27911D1 (25 rows)
# Output:
#   tiering_gate_report_v325.jsonl     deterministic per-row routing (sorted, sort_keys, LF)
#
# Pre-registered bars (FIXED before this measurement; F = 5/5):
#   T0-strict           : 0 DIRTY-bucket rows -> GOLD            (ABSOLUTE; any leak = REFUTED)
#   T-abstain           : 0 ABSTAIN-bucket rows -> GOLD          (any leak = REFUTED)
#   T-ungrounded-floor  : 0 CLEAN_UNGROUNDED rows -> GOLD        (any leak = REFUTED)
#   T-clean-recall      : CLEAN_GROUNDED -> GOLD recall >= F=5/5 (collapse < F = REFUTED)
#   T-hermetic          : report byte-identical across two cold runs (re-run md5 compare)

from __future__ import annotations
import json
import sys
from collections import Counter

import o0_tiering_gate_v324 as gate

HELDOUT = "tiering_heldout_v324.jsonl"
REPORT = "tiering_gate_report_v325.jsonl"
EXPECT_HELDOUT_MD5 = "CABA277117FCC121B5C00E49A27911D1"  # staleness guard (informational)
F_NUM, F_DEN = 5, 5  # pre-registered clean-recall floor


def main():
    rows = []
    with open(HELDOUT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    out = []
    for r in rows:
        routed = gate.route_row(r)
        out.append({"id": r["id"], "bucket": r["bucket"], "verdict": r["verdict"],
                    "grounded": r.get("grounded"), "expected_tier": r["expected_tier"],
                    "routed_tier": routed, "match": routed == r["expected_tier"]})

    out.sort(key=lambda x: x["id"])
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=True, sort_keys=True) + "\n")

    # bar scoring
    def gold(bucket):
        return sum(1 for x in out if x["bucket"] == bucket and x["routed_tier"] == "GOLD")

    dirty_gold = gold("DIRTY")
    abstain_gold = gold("ABSTAIN")
    ungrounded_gold = gold("CLEAN_UNGROUNDED")
    cleang_gold = gold("CLEAN_GROUNDED")
    cleang_total = sum(1 for x in out if x["bucket"] == "CLEAN_GROUNDED")

    t0 = dirty_gold == 0
    t_abstain = abstain_gold == 0
    t_ungrounded = ungrounded_gold == 0
    recall_ok = cleang_total > 0 and (cleang_gold * F_DEN >= F_NUM * cleang_total)
    all_match = all(x["match"] for x in out)

    print("rows=%d  buckets=%s" % (len(out), dict(Counter(x["bucket"] for x in out))))
    print("routed_tiers=%s" % dict(Counter(x["routed_tier"] for x in out)))
    print("--- BARS (pre-registered) ---")
    print("T0-strict          (DIRTY->GOLD=0)            : %s  (got %d)" % ("GREEN" if t0 else "RED", dirty_gold))
    print("T-abstain          (ABSTAIN->GOLD=0)          : %s  (got %d)" % ("GREEN" if t_abstain else "RED", abstain_gold))
    print("T-ungrounded-floor (UNGROUNDED->GOLD=0)       : %s  (got %d)" % ("GREEN" if t_ungrounded else "RED", ungrounded_gold))
    print("T-clean-recall     (GROUNDED->GOLD >= %d/%d)   : %s  (got %d/%d)" % (F_NUM, F_DEN, "GREEN" if recall_ok else "RED", cleang_gold, cleang_total))
    print("all_rows_match_expected_tier                  : %s" % ("GREEN" if all_match else "RED"))
    overall = t0 and t_abstain and t_ungrounded and recall_ok and all_match
    print("OVERALL: %s" % ("ALL-GREEN -> gate validated; Founder-gate public commit." if overall
                           else "REFUTED -> redesign (NO threshold weakening). See mismatched rows."))
    if not overall:
        for x in out:
            if not x["match"]:
                print("  MISMATCH:", x)
        sys.exit(1)


if __name__ == "__main__":
    main()
