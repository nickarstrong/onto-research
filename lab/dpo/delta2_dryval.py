#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
delta2_dryval.py -- OFFLINE proof that rung C delta-2 makes the GENERATE arms
differentiable, WITHOUT touching the sealed substrate.

What it proves (no Ollama, no network, no append to eval/o0/o0_verdicts.jsonl):
  P1 CAUSAL: the CONDITIONED arm carries retrieved curated facts + GOLD frame
     into the proposer PROMPT; the BLIND arm carries "". (arms differentiable)
  P2 FIREWALL: the emitted claim dict is EXACTLY {topic, claim} in both arms
     -- no retrieval handle, no gold object leaks toward verify().
  P3 IMPORT-FIREWALL: controller.verify() source references no generate-side
     module (o0_retrieve / gold / curated / make_generate).
  P4 CONTRACT: make_generate walks the SAME topic-seed cursor in both arms
     (only context differs), so the A/B is a controlled comparison.

Method: inject a FAKE substrate _call into the sealed make_generate (its public
seam) that echoes whether the CONFIRMED-context marker reached the prompt. No
real model is invoked. Sealed apparatus is exercised, never edited.

Run:  python delta2_dryval.py
Exit: 0 = all proofs PASS, 1 = any FAIL.
"""
import sys
from pathlib import Path

from generate_step6 import make_generate, compose_context
from o0_retrieve import retrieve

MARKER = "[CONFIRMED KNOWLEDGE YOU ALREADY ESTABLISHED]"
FRAME_MARKER = "[FRAME]"

# Synthetic CONFIRMED episodic store (NOT the sealed file). Topic chosen so the
# token-overlap retriever returns it deterministically.
TOPIC = "superconductivity critical temperature"
CONFIRMED = [
    {"id": "syn_001", "topic": "superconductivity critical temperature",
     "claim": "FACT-A: YBCO has a critical temperature near 92 K.",
     "best_abstract": "abs"},
    {"id": "syn_002", "topic": "unrelated botany xylem",
     "claim": "FACT-B: xylem transports water.", "best_abstract": "abs"},
]


def _fake_call(model, prompt, options):
    """Echo what the prompt actually contained -- proves context causality."""
    saw_facts = MARKER in prompt
    saw_frame = FRAME_MARKER in prompt
    return "CTX[facts=%d,frame=%d]" % (int(saw_facts), int(saw_frame))


def main():
    fails = []

    # ---- precondition: retriever actually returns a relevant record ----
    hits = retrieve(TOPIC, CONFIRMED, k=3)
    if len(hits) < 1 or hits[0]["id"] != "syn_001":
        fails.append("RETRIEVE: expected syn_001 for topic, got %r" % hits)
    gold_frame = "ABIOGENESIS IGR=0.92; Source is an abstract placeholder."

    # P1/P4 CAUSAL + cursor: build both arms over the SAME single-topic seed.
    blind = make_generate(conditioned=False, model="m", topics=[TOPIC],
                          audit_instruction="", _call=_fake_call)
    cond = make_generate(conditioned=True, model="m", topics=[TOPIC],
                         audit_instruction="", confirmed=CONFIRMED,
                         retrieve_fn=retrieve, gold_frame=gold_frame, k=3,
                         _call=_fake_call)
    out_b = blind(1)
    out_c = cond(1)

    if out_b[0]["claim"] != "CTX[facts=0,frame=0]":
        fails.append("P1 BLIND carried context (expected empty): %r" % out_b[0]["claim"])
    if out_c[0]["claim"] != "CTX[facts=1,frame=1]":
        fails.append("P1 CONDITIONED missing facts/frame in prompt: %r" % out_c[0]["claim"])
    if out_b[0]["topic"] != out_c[0]["topic"]:
        fails.append("P4 arms diverged on topic seed: %r vs %r"
                     % (out_b[0]["topic"], out_c[0]["topic"]))

    # P2 FIREWALL: emitted dict shape is EXACTLY {topic, claim} in both arms.
    for tag, rec in (("blind", out_b[0]), ("cond", out_c[0])):
        if set(rec.keys()) != {"topic", "claim"}:
            fails.append("P2 %s leaked extra fields: %r" % (tag, sorted(rec.keys())))

    # sanity: compose_context is empty iff no facts and no frame
    if compose_context([], "") != "":
        fails.append("compose_context([],'') must be empty")
    if MARKER not in compose_context(hits, gold_frame):
        fails.append("compose_context did not embed the CONFIRMED marker")

    # P3 IMPORT-FIREWALL: verify() body references no generate-side module.
    src = Path("controller.py").read_text(encoding="utf-8")
    vstart = src.find("def verify(c):")
    vend = src.find("return merge_verdict", vstart)
    vbody = src[vstart:vend] if vstart >= 0 and vend > vstart else ""
    if not vbody:
        fails.append("P3 could not isolate verify() body")
    for bad in ("o0_retrieve", "make_generate", "gold_frame", "curated", "retrieve_fn"):
        if bad in vbody:
            fails.append("P3 verify() references generate-side token: %s" % bad)

    # ---- report ----
    print("=" * 64)
    print("DELTA-2 DRY-VAL (offline; sealed substrate untouched)")
    print("=" * 64)
    print("  retrieve(topic) -> %d hit(s), top id=%s"
          % (len(hits), hits[0]["id"] if hits else "-"))
    print("  BLIND       claim: %s" % out_b[0]["claim"])
    print("  CONDITIONED claim: %s" % out_c[0]["claim"])
    print("  emitted keys     : blind=%s cond=%s"
          % (sorted(out_b[0].keys()), sorted(out_c[0].keys())))
    print("  verify() leak    : %s" % ("NONE" if vbody and not any(
        b in vbody for b in ("o0_retrieve", "make_generate", "gold_frame")) else "CHECK"))
    print("-" * 64)
    if fails:
        print("RESULT: FAIL (%d)" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("RESULT: PASS  (P1 causal | P2 emit-firewall | P3 import-firewall | P4 cursor)")
    print("NOTE: this is the differentiability proof only. --gate d for a VERDICT")
    print("      stays gated on a real curated!=raw view (delta-1 / D-GATE session).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
