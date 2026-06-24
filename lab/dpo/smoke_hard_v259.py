#!/usr/bin/env python3
# -*- coding: ascii -*-
# smoke_hard_v259.py -- NO-GPU build smoke for v259 TYPE C (hard-topics wiring + emit-side).
#
# Proves, with a MOCK substrate (no Ollama / no GPU / no net):
#   A. HARD_TOPICS loads + asserts 24 unique; the SEALED proposer factory walks them and emits
#      {topic,claim} ONLY (firewall emit shape intact).
#   B. run_cycle now emits pool_size + topics on the trace row; topics come from HARD_TOPICS;
#      the DIRTY verdict path fires (capable-of-dirty PLUMBING witness).
#
# OUT OF SCOPE (by design -- DO-NOT "capture a baseline"): the live blind rate_f of the substrate
#   on the hard set is the v260 HEADROOM gate, NOT this smoke. The live_adapters absorb.pool_size
#   INCREMENT is static-verified (diff) and witnessed for real in v260's trace.
#
# Isolation (VIOLATION-A): section B runs inside a temp CWD (save->run->restore); no pre-existing
#   lab/dpo state is read or mutated.
import json, os, sys, tempfile

FAIL = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)

# ---------- A: SEALED proposer walks HARD_TOPICS via mock substrate ----------
from hard_topics import HARD_TOPICS
from generate_step6 import make_generate

check("A1 HARD_TOPICS == 24 unique", len(HARD_TOPICS) == 24 and len(set(HARD_TOPICS)) == 24)

def mock_call(model, prompt, options):
    return "MOCK specific claim"   # substrate stub; never touches the network

g = make_generate(conditioned=False, model="mock", topics=HARD_TOPICS,
                  audit_instruction="", _call=mock_call)
out = g(8)
check("A2 generate(8) -> 8 records", len(out) == 8)
check("A3 firewall emit shape {topic,claim} only",
      all(set(r.keys()) == {"topic", "claim"} for r in out))
check("A4 topics drawn from HARD_TOPICS", all(r["topic"] in HARD_TOPICS for r in out))
check("A5 cursor walks first 8 hard topics in order",
      [r["topic"] for r in out] == HARD_TOPICS[:8])

# ---------- B: run_cycle emits pool_size + topics; DIRTY path fires ----------
from controller import run_cycle, GoalStack

tmp = tempfile.mkdtemp()
cwd0 = os.getcwd()
os.chdir(tmp)   # VIOLATION-A guard: relative writes (CONTACT_LOG, goal_stack, trace) -> tmp
try:
    trace = "smoke_trace.jsonl"
    gstack = GoalStack("goal_stack.json")
    self_model = {"weaknesses": [
        {"name": "fabricated-specifics", "severity": "med", "audit_instruction": "stub"}]}

    mc = {"i": 0}
    def gen_mock(n):
        o = []
        for _ in range(n):
            t = HARD_TOPICS[mc["i"] % len(HARD_TOPICS)]; mc["i"] += 1
            o.append({"topic": t, "claim": "stub claim"})
        gen_mock.retrieval_hits = [0] * n
        return o
    gen_mock.retrieval_hits = []

    vc = {"i": 0}
    def ver_mock(c):
        vc["i"] += 1
        return ("DIRTY", "mock") if (vc["i"] % 2) else ("CLEAN", "mock")  # 4 DIRTY / 4 CLEAN

    def abs_mock(v, kind):
        # mirrors live_adapters absorb.pool_size side-channel (knowledge increments)
        if kind == "knowledge":
            abs_mock.pool_size = getattr(abs_mock, "pool_size", 0) + 1
        v["_absorbed_knowledge"] = (kind == "knowledge")
    abs_mock.pool_size = 0

    run_cycle(self_model, gstack, gen_mock, ver_mock, abs_mock,
              n=8, live=False, pin_weakness="fabricated-specifics", trace_path=trace)

    rows = [json.loads(l) for l in open(trace, encoding="utf-8") if l.strip()]
    check("B1 trace row emitted", len(rows) >= 1)
    row = rows[-1] if rows else {}
    check("B2 pool_size field present", "pool_size" in row)
    check("B3 topics field present", "topics" in row)
    check("B4 topics == 8 from HARD_TOPICS",
          isinstance(row.get("topics"), list) and len(row.get("topics", [])) == 8
          and all(t in HARD_TOPICS for t in row.get("topics", [])))
    check("B5 pool_size == 4 (CLEAN absorbs)", row.get("pool_size") == 4)
    check("B6 DIRTY path fired (rate_f == 0.5)", row.get("rate_f") == 0.5)
    check("B7 fa_live == 0 (no leak)", row.get("fa_live") == 0.0)
finally:
    os.chdir(cwd0)   # restore

print("=" * 44)
print("SMOKE: " + ("ALL PASS" if not FAIL else "FAIL -> " + ", ".join(FAIL)))
sys.exit(1 if FAIL else 0)
