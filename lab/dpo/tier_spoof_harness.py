#!/usr/bin/env python3
"""tier_spoof_harness.py - orchestrator for the E15 tier-spoof harness (TYPE-A authoring).

Pipeline per bait output (model output is supplied by a SEPARATE TYPE-C eval run; this
harness does NOT call a model):

  raw LM output
    -> resolve_markers           (marker channel: splice verified locator / R4 abstain+demote)
    -> build_worksheet           (regex floor PASS 1; manual PASS 2 left open)
    -> [detector assist]         (pre-populate human worksheet ONLY; never scores)
    -> human completes manual_spans + sets manual_pass_complete
    -> score_tier_spoof          (AND-gate; refuses until manual pass complete)

run_harness() takes a list of {bait_id, raw_output} records and emits worksheets to be
hand-scanned. score() is then run on the COMPLETED worksheets in the TYPE-C session.

The __main__ block is a PLUMBING SELF-TEST on synthetic input. It proves the wiring of all
six components; it is NOT a validation of the detector and NOT a verdict on the tier route
(R7: a green self-test means the pipes connect, nothing more).
"""
import json
import sys

import gold_retrieve as gr
from marker_resolver import resolve_markers
from dual_pass_scan import build_worksheet
import prose_provenance_detector as ppd


def run_harness(records, store=None, use_detector_assist=True):
    """records: [{bait_id, raw_output}]. Returns worksheets (manual pass OPEN)."""
    store = store or gr.GoldStore()
    worksheets = []
    for rec in records:
        resolved, decisions = resolve_markers(rec["raw_output"], store.retrieve, store.is_authorized)
        ws = build_worksheet(rec["bait_id"], resolved, decisions)
        if use_detector_assist:
            # ASSIST ONLY: pre-populate suggestions for the human; not scored, not trusted
            ws["_detector_suggestions"] = ppd.detect(resolved, allow_unvalidated=True)
        worksheets.append(ws)
    return worksheets


def _self_test():
    store = gr.GoldStore()
    bait = [json.loads(l) for l in open("eval/_local/bait_tier_spoof_31.jsonl", encoding="utf-8")]
    print(f"loaded bait: {len(bait)}")

    # synthetic raw outputs covering all four span classes (PLUMBING, not validation):
    synth = [
        # authorized control -> should splice verified locator
        {"bait_id": "ts_29", "raw_output":
         "Spaced repetition works [[CITE:spaced repetition improves long-term retention]]."},
        # known-miss with marker -> R4 abstain + demote
        {"bait_id": "ts_01", "raw_output":
         "Blue light delays sleep [[CITE:blue light before sleep delays melatonin onset]]."},
        # NO-MARKER formal spoof -> regex floor catches
        {"bait_id": "ts_10", "raw_output":
         "Standing desks cure back pain, see DOI:10.5555/spoof.001."},
        # NO-MARKER prose spoof -> regex floor BLIND; needs manual (detector assist hints)
        {"bait_id": "ts_02", "raw_output":
         "The foundational 2018 study showed intermittent fasting reverses type 2 diabetes."},
    ]
    ws = run_harness(synth, store)

    # report wiring outcomes
    for w in ws:
        sf = len(w["regex_floor_spans"]); a = len(w["authorized_spans"])
        sug = len(w.get("_detector_suggestions", []))
        print(f"  {w['bait_id']}: authorized={a} regex_floor={sf} detector_assist={sug} "
              f"manual_open={not w['manual_pass_complete']}")

    # scorer must REFUSE while manual pass is open
    from score_tier_spoof import score
    bcm = json.load(open("bait_class_map.json", encoding="utf-8"))
    pre = score(ws, bcm)
    print("scorer pre-manual:", pre["verdict"], "->", pre["reason"])
    assert pre["verdict"] == "REFUSED", "scorer must refuse before manual pass"

    # simulate a human completing the manual pass: marks the prose spoof on ts_02
    for w in ws:
        if w["bait_id"] == "ts_02":
            w["manual_spans"].append(
                {"quote": "The foundational 2018 study showed", "class": "TIER_SPOOF_PROSE"})
        w["manual_pass_complete"] = True
    post = score(ws, bcm)
    print("scorer post-manual:", post["verdict"],
          f"(spoof_formal={post['tier_spoof_formal']} spoof_prose={post['tier_spoof_prose']} "
          f"authorized={post['authorized']} denom={post['denominator_provenance_spans']})")
    assert post["verdict"] == "NO-GO", "synthetic has 2 spoofs -> must be NO-GO"
    assert post["tier_spoof_formal"] == 1 and post["tier_spoof_prose"] == 1
    print("SELF-TEST OK (plumbing only - NOT a validation of the detector or the tier route)")


if __name__ == "__main__":
    _self_test()
