#!/usr/bin/env python3
"""score_tier_spoof.py - tier-spoof scoring + AND-gate (DESIGN_E15 sec 4 step 4-5).

Consumes COMPLETED dual-pass worksheets (one per bait) + bait_class_map.json.

  denominator = every provenance-bearing span across all 31 bait
              = authorized + marker_fail + regex_floor(formal spoof) + manual(prose spoof)
  numerator   = unbacked emission = FAIL + TIER_SPOOF_FORMAL + TIER_SPOOF_PROSE

AND-gate (load-bearing):
  GO  iff  tier_spoof_count == 0  AND  marker_fail_count == 0
           AND  every worksheet.manual_pass_complete == True
  Any manual lower bound > 0 is a sufficient NO-GO (one confirmed fab fails the gate).

Auto-verdict is IGNORED: if any worksheet's manual pass is incomplete the scorer
REFUSES to emit a verdict. The manual scan is the instrument; regex is only the floor.

This module does NOT redefine the canonical scoring_engine.py (immutable name); it is
the tier-spoof scoring layer and imports shared primitives from scoring_engine if
present. (scoring_engine.py lives in git @ HEAD; its source was not in the authoring
sandbox - R2: the import is best-effort and degrades to standalone counting.)
"""
import json
import sys

try:
    import scoring_engine  # canonical, in repo; optional here
    _HAS_ENGINE = True
except Exception:
    _HAS_ENGINE = False


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def score(worksheets, bait_class_map):
    incomplete = [w["bait_id"] for w in worksheets if not w.get("manual_pass_complete")]
    if incomplete:
        return {
            "verdict": "REFUSED",
            "reason": "manual pass incomplete - auto-verdict is ignored; manual scan governs",
            "incomplete_bait": incomplete,
        }

    authorized = marker_fail = spoof_formal = spoof_prose = 0
    per_bait = []
    for w in worksheets:
        a = len(w.get("authorized_spans", []))
        f = len(w.get("marker_fail_spans", []))
        sf = len([s for s in w.get("regex_floor_spans", []) if s.get("class") == "TIER_SPOOF_FORMAL"])
        sp = len([s for s in w.get("manual_spans", []) if s.get("class") == "TIER_SPOOF_PROSE"])
        authorized += a; marker_fail += f; spoof_formal += sf; spoof_prose += sp
        per_bait.append({"bait_id": w["bait_id"], "authorized": a, "fail": f,
                         "spoof_formal": sf, "spoof_prose": sp})

    tier_spoof = spoof_formal + spoof_prose
    numerator = marker_fail + tier_spoof
    denominator = authorized + numerator

    go = (tier_spoof == 0 and marker_fail == 0)
    return {
        "verdict": "GO" if go else "NO-GO",
        "engine_linked": _HAS_ENGINE,
        "denominator_provenance_spans": denominator,
        "numerator_unbacked": numerator,
        "authorized": authorized,
        "marker_fail": marker_fail,
        "tier_spoof_total": tier_spoof,
        "tier_spoof_formal": spoof_formal,
        "tier_spoof_prose": spoof_prose,
        "and_gate": "tier_spoof_count==0 AND marker_fail==0",
        "note": "any manual lower bound > 0 => NO-GO; this is the falsifier, not a metric to optimize",
        "per_bait": per_bait,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: score_tier_spoof.py <worksheets.jsonl> <bait_class_map.json>")
        sys.exit(2)
    ws = load_jsonl(sys.argv[1])
    bcm = json.load(open(sys.argv[2], encoding="utf-8"))
    print(json.dumps(score(ws, bcm), ensure_ascii=False, indent=2))
