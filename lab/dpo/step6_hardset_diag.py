#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
step6_hardset_diag.py -- READ-ONLY disambiguation for rate_f_blind=0 on the hard-set.

WHY: the blind probe returned rate_f_blind=0 (9/9 CLEAN). A CLEAN verdict is ambiguous between
  H1  substrate ABSTAINS  (no fabricated specific emitted -> nothing to catch -> honestly CLEAN)
  H2  substrate FABRICATES but verify returns CLEAN-on-not-found (instrument too weak to bind)
The frozen run_arm discards claim text + verify reasons, so the verdict alone cannot tell them apart.

This diagnostic reuses the SAME injected generate (blind) and the SAME verify (external oracle) BYTE
-FOR-BYTE -- it does NOT edit the frozen path. It only OBSERVES and prints the full claim text and the
verify (verdict, reasons) per topic, for ONE topic per floor family (n=3, LOCAL).

It writes nothing into any knowledge/eval slot. Pure stdout + a local dump for inspection.

Usage (from lab/dpo, Ollama up + net on):
    python step6_hardset_diag.py --self-model self_model.json
"""
import argparse, json
from pathlib import Path

import generate_step6 as G
from hard_topics import HARD_TOPICS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-model", default="self_model.json")
    ap.add_argument("--meta", default="hard_topics_meta.json")
    ap.add_argument("--out", default="eval/_local/hardset_diag.json")
    a = ap.parse_args()

    sm = json.loads(Path(a.self_model).read_text(encoding="utf-8"))
    model = sm["substrate"]
    W = next((w for w in sm["weaknesses"] if w["name"] == "fabricated-specifics"),
             sm["weaknesses"][0])
    audit = W["audit_instruction"]

    from controller import live_adapters
    _gen, verify, _absorb = live_adapters()

    # one topic per floor family
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    seen, picks = set(), []
    for row in meta["floor"]:
        if row["family"] not in seen:
            seen.add(row["family"]); picks.append((row["family"], row["topic"]))
    # generate each picked topic blind, in isolation (cursor over just that topic)
    dump = []
    for fam, topic in picks:
        g = G.make_generate(False, model, [topic], audit,
                            options={"temperature": 0.7, "seed": 0, "num_predict": 220})
        claim = g(1)[0]
        v, reasons = verify({"topic": claim["topic"], "claim": claim["claim"]})
        rec = {"family": fam, "topic": topic, "claim": claim["claim"],
               "verdict": v, "reasons": reasons}
        dump.append(rec)
        print("=" * 78)
        print(f"FAMILY : {fam}")
        print(f"TOPIC  : {topic}")
        print(f"CLAIM  : {claim['claim']}")
        print(f"VERDICT: {v}")
        print(f"REASONS: {json.dumps(reasons, ensure_ascii=True)}")
    outp = Path(a.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(dump, indent=2, ensure_ascii=True), encoding="utf-8")
    print("=" * 78)
    print(f"wrote {outp}")
    print("\nREAD: if CLAIM contains an invented specific (number/ID/date) AND verdict==CLEAN -> H2 "
          "(verify cannot bind this class). If CLAIM abstains/declines -> H1 (substrate robust).")


if __name__ == "__main__":
    main()
