#!/usr/bin/env python3
# -*- coding: ascii -*-
"""SMOKE (BUILD-FRONT #1): prove retrieval_hit>0 when the conditioned proposer
retrieves over a NON-empty live ABSORB trail, through the REAL patched feed
(controller._live_retrieve_fn) + the SEALED proposer (generate_step6.make_generate).

ISOLATION (VIOLATION-A): a temp trail file only; no pre-existing state read or
mutated; substrate is mocked (no Ollama, no net). FROZEN trace 9c960429 NOT touched.
PASS gate: retrieve()>0 over the populated trail AND sum(retrieval_hits)>0 AND every
emitted dict carries EXACTLY {topic,claim} (firewall).
Run FROM lab/dpo: python smoke_retrieval_hit.py
"""
import json, os, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.getcwd())  # lab/dpo on path

import controller                          # patched module (real)
from generate_step6 import make_generate   # sealed proposer (real)

TOPIC = "Casimir effect between parallel conducting plates"  # a real DOMAIN_TOPIC


def main():
    tmpdir = tempfile.mkdtemp(prefix="smoke_rh_")
    trail = Path(tmpdir) / "trail.jsonl"
    try:
        # synthetic LIVE ABSORB trail = exactly what absorb() would have written
        rec = {"id": "smoke_1", "topic": TOPIC,
               "claim": "The Casimir force scales as the inverse fourth power of plate separation.",
               "best_abstract": "", "verdict": "ABSORB", "_absorbed_knowledge": True}
        trail.write_text(json.dumps(rec) + "\n", encoding="utf-8")

        # 1) REAL patched feed retrieves over the populated trail
        rfn = controller._live_retrieve_fn(str(trail))
        got = rfn(TOPIC, None, k=3)
        assert len(got) >= 1, f"FAIL: retrieve() empty over populated trail -> {got}"

        # 2) REAL sealed proposer records the hit on its side-channel; mock substrate
        calls = {"n": 0}
        def mock_call(model, prompt, options):
            calls["n"] += 1
            assert "Casimir" in prompt, "retrieved fact / topic did not reach the PROMPT"
            return "Mock claim about the Casimir effect (smoke)."
        gen = make_generate(conditioned=True, model="mock", topics=[TOPIC],
                            audit_instruction="", confirmed=[], retrieve_fn=rfn,
                            gold_frame="", k=3, _call=mock_call)
        out = gen(2)
        hits = list(getattr(gen, "retrieval_hits", []))
        total = sum(hits)

        # 3) FIREWALL: emitted dicts carry ONLY {topic,claim}
        bad = [o for o in out if set(o.keys()) != {"topic", "claim"}]
        assert not bad, f"FIREWALL BREACH: emit carried extra keys -> {bad}"

        print(f"[SMOKE] retrieve_n={len(got)}  hits={hits}  sum={total}  "
              f"substrate_calls={calls['n']}  emit_keys_ok=True")
        assert total > 0, "FAIL: sum(retrieval_hit)==0 over a populated trail"
        print("[SMOKE] PASS: retrieval_hit>0 on synthetic retrieval; "
              "firewall {topic,claim} intact; verify() untouched.")
    finally:
        try:
            trail.unlink()
        except OSError:
            pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


if __name__ == "__main__":
    main()
