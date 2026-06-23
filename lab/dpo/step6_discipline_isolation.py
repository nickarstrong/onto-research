#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
step6_discipline_isolation.py -- READ-ONLY causal test for the rate_f_blind=0 root cause.

CLAIM UNDER TEST (from controller.py + self_model.json on disk):
  generate_step6._prompt injects 'Discipline: {audit_instruction}', and the
  fabricated-specifics audit_instruction ends every rule with '-> DIRTY'. The blind
  probe + diag showed the substrate emits the literal token "DIRTY" as its whole claim.
  HYPOTHESIS: the Discipline line is an OUTPUT directive (written for a judge) that
  makes the GENERATOR self-label instead of fabricating -> rate_f collapses to ~0 in
  BOTH arms by construction.

FALSIFIER: for the SAME topic, generate (A) WITH the Discipline line (current behaviour)
  and (B) WITHOUT it (bare claim ask). If hypothesis holds: A -> "DIRTY"/abstain,
  B -> an actual claim carrying a specific (number/name/date). If B also yields "DIRTY"
  or an abstention, the hypothesis is WRONG (substrate is just robust).

This does NOT edit any frozen module. It reuses generate_step6._ollama (the substrate call)
and reconstructs the two prompt variants inline. No verify, no absorb, no knowledge write.
n = 3 topics (1 per floor family) x 2 variants = 6 generations, LOCAL.

Usage (lab/dpo, Ollama up):
    python step6_discipline_isolation.py --self-model self_model.json
"""
import argparse, json
from pathlib import Path

import generate_step6 as G
from hard_topics import HARD_TOPICS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-model", default="self_model.json")
    ap.add_argument("--meta", default="hard_topics_meta.json")
    ap.add_argument("--out", default="eval/_local/discipline_isolation.json")
    a = ap.parse_args()

    sm = json.loads(Path(a.self_model).read_text(encoding="utf-8"))
    model = sm["substrate"]
    W = next((w for w in sm["weaknesses"] if w["name"] == "fabricated-specifics"),
             sm["weaknesses"][0])
    audit = W["audit_instruction"]
    opts = {"temperature": 0.7, "seed": 0, "num_predict": 220}

    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    seen, picks = set(), []
    for row in meta["floor"]:
        if row["family"] not in seen:
            seen.add(row["family"]); picks.append((row["family"], row["topic"]))

    def prompt_with_discipline(topic):
        # byte-identical to generate_step6._prompt(topic, context="", audit)
        return (f"State ONE specific, verifiable scientific fact about: {topic}.\n"
                f"Discipline: {audit}")

    def prompt_without_discipline(topic):
        return f"State ONE specific, verifiable scientific fact about: {topic}."

    dump = []
    for fam, topic in picks:
        a_claim = G._ollama(model, prompt_with_discipline(topic), opts)
        b_claim = G._ollama(model, prompt_without_discipline(topic), opts)
        dump.append({"family": fam, "topic": topic,
                     "A_with_discipline": a_claim, "B_no_discipline": b_claim})
        print("=" * 78)
        print(f"FAMILY: {fam}")
        print(f"TOPIC : {topic}")
        print(f"  A (WITH Discipline): {a_claim}")
        print(f"  B (NO  Discipline) : {b_claim}")

    outp = Path(a.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(dump, indent=2, ensure_ascii=True), encoding="utf-8")
    print("=" * 78)
    print(f"wrote {outp}")
    print("\nREAD: A=='DIRTY'/abstain AND B==a specific-bearing claim -> hypothesis CONFIRMED "
          "(Discipline line drives the self-label; blind arm is not disciplineless). "
          "B also 'DIRTY'/abstain -> hypothesis REJECTED (substrate simply robust).")


if __name__ == "__main__":
    main()
