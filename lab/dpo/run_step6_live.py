#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
run_step6_live.py -- LIVE A/B falsifier (run on lab machine: Ollama up + net on).
LOCAL probe, n<=8/arm (protocol sec 3.7). Does NOT reopen the sealed cycle (1184d19):
reuses controller.live_adapters()'s VERIFY (external oracle) byte-for-byte.

HARD GATE: exits if self_model has < 2 carded weaknesses -> GUARD2 rotation cannot
fire -> a PASS verdict is unreachable. Authoring A2/A4 cards is Founder-owned
(CONCEPT_step6 sec 3/7). This runner refuses to spend a run that cannot pass.

Usage (from C:\\Projects\\onto-research\\lab\\dpo\\):
    python run_step6_live.py --self-model eval/o0/self_model.json \
        --verdicts eval/o0/o0_verdicts.jsonl --gold-frame gold_frame.txt --k 8
"""
import argparse, json, sys
from pathlib import Path
import o0_retrieve as R
import generate_step6 as G
import falsifier_step6 as F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-model", required=True)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--gold-frame", default="", help="path to routed E16 GOLD module text")
    ap.add_argument("--k", type=int, default=8)
    a = ap.parse_args()

    sm = json.loads(Path(a.self_model).read_text(encoding="utf-8"))
    nW = sm.get("n_weaknesses", len(sm.get("weaknesses", [])))
    # ---- HARD BLOCKER GATE (Founder-owned A2/A4) ----
    if nW < 2:
        print("BLOCKED: self_model has", nW, "weakness card(s); need >= 2 (A2 + A4) for GUARD2 "
              "rotation. Author cards via selfmodel_compile.py, then re-run. Refusing run.")
        sys.exit(3)

    model = sm["substrate"]
    W = next((w for w in sm["weaknesses"] if w["name"] == "fabricated-specifics"),
             sm["weaknesses"][0])
    audit = W["audit_instruction"]

    # shared substrate verify (UNCHANGED external oracle) from the sealed controller
    from controller import live_adapters
    _gen_blind_real, verify, _absorb = live_adapters()   # we use only verify

    # G2-scope fix: SAME 3 DOI provoke_id topics G2 PASSED on (rate_f_blind=0.667).
    # Single source of truth = step6_hardset_blind_probe.DOI_TOPICS (no copy drift).
    from step6_hardset_blind_probe import DOI_TOPICS
    topics = list(DOI_TOPICS)
    conf = R.load_confirmed(a.verdicts)
    gold_frame = Path(a.gold_frame).read_text(encoding="utf-8") if a.gold_frame else ""

    # both arms share substrate, decoding params, topic-seed sequence; differ ONLY in context
    opts = {"temperature": 0.7, "seed": 0, "num_predict": 220}
    g_blind = G.make_generate(False, model, topics, audit, options=opts)
    g_cond = G.make_generate(True, model, topics, audit, confirmed=conf,
                             retrieve_fn=R.retrieve, gold_frame=gold_frame, k=3, options=opts)

    # retrieved-by-topic for novelty (only the topics the cond arm will hit)
    fed = {}
    for i in range(a.k):
        t = topics[i % len(topics)]
        fed[t] = [r["claim"] for r in R.retrieve(t, conf, 3)]

    print("== BLIND arm ==")
    blind = F.run_arm(g_blind, verify, a.k)
    print("== CONDITIONED arm ==")
    cond = F.run_arm(g_cond, verify, a.k, retrieved_by_topic=fed)

    # GUARD2 precondition met (>=2 cards). Full rotation evidence (worst-first >=2 distinct,
    # cooldown >=1x) comes from the controller multi-cycle log; confirm there.
    guard2_ok = (nW >= 2)
    res = F.adjudicate(blind, cond, guard2_ok)
    res["NOTE_guard2"] = ("precondition met (>=2 cards); confirm rotation in controller "
                          "multi-cycle log (>=2 distinct selected, cooldown >=1x)")
    print(json.dumps(res, indent=2))
    Path("eval/o0/step6_falsifier_E6.json").write_text(json.dumps(
        {"blind": blind, "cond": cond, "verdict": res}, indent=2), encoding="utf-8")
    print("\nwrote eval/o0/step6_falsifier_E6.json")


if __name__ == "__main__":
    main()
