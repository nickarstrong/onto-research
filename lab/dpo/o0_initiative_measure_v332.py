#!/usr/bin/env python3
# o0_initiative_measure_v332.py
# INITIATIVE v332 TYPE-B measure (READ-ONLY). Scores emit/suppress correctness
# against pre-registered expected_emit; attests 3 v330 correctness bars.
# ZERO new verdict logic: reuses certified route()/trigger/emission verbatim
# from the FROZEN harness module (o0_initiative_harness_v331). Hermetic.
from __future__ import annotations
import json, sys
from collections import Counter
from o0_initiative_harness_v331 import (
    route, GOLD, trigger_predicate, emission_decision, load_rows,
)

EVAL_OUT = "eval/initiative_measure_v332_E332.jsonl"

def measure(rows):
    recs = []
    for r in rows:
        trig = trigger_predicate(r)
        tier = route(r["verifier_verdict"], r["grounded"])
        emit = bool(emission_decision(r))
        recs.append({
            "id": r["id"],
            "bucket": r["bucket"],
            "trigger_fired": bool(trig),
            "gate_tier": tier,
            "emit_decision": emit,
            "expected_emit": bool(r["expected_emit"]),
            "match": emit == bool(r["expected_emit"]),
            "verifier_verdict": r["verifier_verdict"],
            "grounded": bool(r["grounded"]),
        })
    return recs

def main():
    rows = load_rows()
    if len(rows) != 15:
        print("FAIL: expected 15 rows, got %d" % len(rows)); sys.exit(1)
    recs = measure(rows)

    # write per-row eval (LOCAL, KEEP-LOCAL)
    with open(EVAL_OUT, "w", encoding="utf-8", newline="\n") as f:
        for rec in recs:
            f.write(json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n")

    # join consistency
    mism = [r["id"] for r in recs if not r["match"]]
    if mism:
        print("FAIL: emit != expected_emit:", mism); sys.exit(1)

    emitted = [r for r in recs if r["emit_decision"]]
    suppressed = [r for r in recs if not r["emit_decision"]]
    bc = Counter(r["bucket"] for r in rows)

    # --- BAR: I-discipline-floor (ABSOLUTE) ---
    # 0 emit on any non-A row (B1/B2/C). Any false-emit -> RED.
    false_emit = [r["id"] for r in emitted if r["bucket"] != "A"]
    floor = "GREEN" if not false_emit else "RED"

    # --- BAR: I-liveness ---
    # all Bucket-A emit, A non-empty.
    a_rows = [r for r in recs if r["bucket"] == "A"]
    a_suppressed = [r["id"] for r in a_rows if not r["emit_decision"]]
    liveness = "GREEN" if (a_rows and not a_suppressed) else "RED"

    # --- BAR: I-no-noise ---
    # every emitted row: verifier_verdict==CLEAN AND grounded==True.
    noise = [r["id"] for r in emitted
             if not (r["verifier_verdict"] == "CLEAN" and r["grounded"])]
    no_noise = "GREEN" if not noise else "RED"

    print("=== v332 INITIATIVE MEASURE (wiring-grade) ===")
    print("ROWS: 15  BUCKETS:", dict(bc))
    print("CONFUSION: emit=%d suppress=%d false_emit=%d false_suppress=%d"
          % (len(emitted), len(suppressed),
             len([r for r in recs if r["emit_decision"] and not r["expected_emit"]]),
             len([r for r in recs if (not r["emit_decision"]) and r["expected_emit"]])))
    print("EMITTED IDS:", [r["id"] for r in emitted])
    print("BAR I-discipline-floor (ABSOLUTE):", floor,
          ("" if floor == "GREEN" else "false_emit=%s" % false_emit))
    print("BAR I-liveness:", liveness,
          ("" if liveness == "GREEN" else "A_suppressed=%s" % a_suppressed))
    print("BAR I-no-noise:", no_noise,
          ("" if no_noise == "GREEN" else "noise=%s" % noise))
    allg = floor == "GREEN" and liveness == "GREEN" and no_noise == "GREEN"
    print("CORRECTNESS-BARS:", "ALL GREEN" if allg else "RED")
    print("EVAL-WRITTEN:", EVAL_OUT)
    if not allg:
        sys.exit(2)

if __name__ == "__main__":
    main()
