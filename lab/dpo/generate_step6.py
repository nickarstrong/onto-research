#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
generate_step6.py -- retrieval-conditioned GENERATE adapter factory.

make_generate(conditioned, ...) -> a generate(n) adapter with the SAME signature
the sealed controller (1184d19) injects. The cycle is NOT reopened; only the
proposer's input changes (CONCEPT_step6 sec 1).

Two arms share one substrate call path; the ONLY difference is proposer-context:
  BLIND       arm: conditioned=False -> context = ""   (current behaviour)
  CONDITIONED arm: conditioned=True  -> context = [retrieved ABSORB facts] + [GOLD frame]

FIREWALL (CONCEPT_step6 sec 2, #1 watch): retrieval/GOLD enter the PROMPT only.
The emitted claim dict carries EXACTLY {"topic","claim"} -- no retrieval handle,
no GOLD object -- so the downstream verify(c) (external oracle, unchanged) cannot
see episodic memory or beliefs. belief-checks-belief / memory-checks-memory is
mechanically impossible because the channels never share a field.

Substrate call = Ollama /api/generate {"stream":false}, read ['response']
(pack rule: never TTY stdout -> ANSI/mojibake). Shared decoding params across arms.
"""
import json, urllib.request

OLLAMA = "http://localhost:11434/api/generate"


def _ollama(model, prompt, options):
    payload = {"model": model, "prompt": prompt, "stream": False, "options": options}
    req = urllib.request.Request(
        OLLAMA, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))["response"].strip()


def compose_context(retrieved, gold_frame):
    """proposer-context = confirmed episodic facts + GOLD belief frame.
    PROMPT TEXT ONLY -- never returned to the verifier."""
    if not retrieved and not gold_frame:
        return ""
    parts = []
    if gold_frame:
        parts.append("[FRAME]\n" + gold_frame.strip())
    if retrieved:
        facts = "\n".join(f"- {r['claim']}" for r in retrieved)
        parts.append("[CONFIRMED KNOWLEDGE YOU ALREADY ESTABLISHED]\n" + facts)
    return "\n\n".join(parts)


def _prompt(topic, context):
    # Q1 (E6 fix, defect D-B): the audit rubric is a JUDGE instruction, NOT a
    # generator instruction. Injecting "Discipline: {audit}" made the substrate
    # self-label DIRTY -> rate_f 0 in BOTH arms (the line rode both). The generator
    # now states a claim with no self-audit; verification is external (controller).
    base = f"State ONE specific, verifiable scientific fact about: {topic}."
    if context:
        return context + "\n\n" + base + ("\nExtend from what you already know; "
                                          "do NOT merely repeat the confirmed facts above.")
    return base


def make_generate(conditioned, model, topics, audit_instruction,
                  confirmed=None, retrieve_fn=None, gold_frame="",
                  k=3, options=None, _call=_ollama):
    """Returns generate(n) -> [{"topic","claim"}, ...]. Cursor-stable across arms
    so BLIND and CONDITIONED walk the SAME topic seed sequence.
    NOTE (Q1): audit_instruction is accepted to keep the caller contract stable
    but is intentionally NOT threaded into the prompt (E6/D-B). It remains a
    JUDGE-side rubric only."""
    options = options or {"temperature": 0.7, "seed": 0, "num_predict": 220}
    cur = {"i": 0}

    def generate(n):
        out = []
        for _ in range(n):
            topic = topics[cur["i"] % len(topics)]
            cur["i"] += 1
            if conditioned:
                retrieved = retrieve_fn(topic, confirmed, k=k) if retrieve_fn else []
                ctx = compose_context(retrieved, gold_frame)
            else:
                ctx = ""
            prompt = _prompt(topic, ctx)
            claim = _call(model, prompt, options)
            # FIREWALL: emit ONLY topic+claim. No ctx, no retrieved, no gold leak.
            out.append({"topic": topic, "claim": claim})
        return out

    return generate
