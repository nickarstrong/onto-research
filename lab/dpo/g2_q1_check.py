#!/usr/bin/env python3
# -*- coding: ascii -*-
"""g2_q1_check.py -- offline check that Q1 removed the Discipline line.

Deterministic. NO Ollama / NO net / NO GPU. Stubs the substrate call with an
echo so the FULL prompt that WOULD reach the model is inspected. Proves:
  (1) "Discipline:" is absent from the constructed prompt in BOTH arms;
  (2) the audit_instruction string never appears in any generated prompt;
  (3) the topic and (conditioned) frame/extend scaffolding are still present.
PASS here is the pass-gate for Step-2 (Q1); the live blind eval follows only on PASS.
"""
import sys
import generate_step6 as G

AUDIT = "SENTINEL_AUDIT_RUBRIC_must_not_leak_into_prompt"
TOPICS = ["Number of neurons in the human brain with a supporting DOI",
          "Speed of sound in air at 20 C with the DOI of the source used"]
FRAME = "[FRAME]\nan example GOLD belief frame line"

ok = True


def check(name, cond):
    global ok
    if not cond:
        ok = False
    print("  [%s] %s" % ("PASS" if cond else "FAIL", name))


# --- _prompt unit (pure, both arms) ---
p_blind = G._prompt(TOPICS[0], "")
p_cond = G._prompt(TOPICS[0], FRAME)
check("blind: no 'Discipline:'", "Discipline:" not in p_blind)
check("cond:  no 'Discipline:'", "Discipline:" not in p_cond)
check("blind: topic present", TOPICS[0] in p_blind)
check("cond:  frame present", "[FRAME]" in p_cond)
check("cond:  extend scaffold present", "do NOT merely repeat" in p_cond)

# --- full make_generate path with an echo substrate (no network) ---
captured = []


def echo(model, prompt, options):
    captured.append(prompt)
    return "CLAIM_PLACEHOLDER"


g = G.make_generate(False, "echo-model", TOPICS, AUDIT, options={"seed": 0},
                    _call=echo)
out = g(len(TOPICS))
check("make_generate emits topic+claim only",
      all(set(r.keys()) == {"topic", "claim"} for r in out))
check("no prompt contains 'Discipline:'",
      all("Discipline:" not in p for p in captured))
check("no prompt leaks the audit rubric",
      all(AUDIT not in p for p in captured))
check("captured one prompt per generation", len(captured) == len(TOPICS))

print("\nQ1 CHECK:",
      "PASS -- Discipline line gone, audit not threaded -> proceed to blind eval"
      if ok else "FAIL -- do NOT run the eval")
sys.exit(0 if ok else 1)
