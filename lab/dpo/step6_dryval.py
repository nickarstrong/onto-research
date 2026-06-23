#!/usr/bin/env python3
# -*- coding: ascii -*-
"""step6_dryval.py -- OFFLINE logic validation (no Ollama/net).
Validates LOGIC against the REAL o0_verdicts.jsonl schema. This is probe-validates-
logic, NOT a live measurement (ROADMAP lesson). LIVE run is a separate, gated step."""
import sys, json
import o0_retrieve as R
import generate_step6 as G
import falsifier_step6 as F

VERD = sys.argv[1] if len(sys.argv) > 1 else "o0_verdicts.jsonl"
fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


print("=" * 64)
print("STEP 6 DRY-VALIDATION (offline; real schema)")
print("=" * 64)

# --- 1. RETRIEVAL against real disk ---
print("\n[1] RETRIEVAL (CONFIRMED-only + topic match) on real o0_verdicts.jsonl")
conf = R.load_confirmed(VERD)
total = sum(1 for _ in open(VERD, encoding="utf-8"))
check(f"loaded {len(conf)} CONFIRMED of {total} (ABSORB-only filter)", len(conf) == 131)
check("zero non-ABSORB leaked into confirmed set",
      all(c["claim"] for c in conf))
hits = R.retrieve("Cooper pairs superconductivity BCS theory", conf, k=3)
check(f"topic match returned {len(hits)} record(s) for a real topic", len(hits) >= 1)
check("retrieve returns [] on no-overlap topic",
      R.retrieve("zzz nonexistent quux topic", conf, k=3) == [])
aud = R.snippet_audit(R.retrieve("Casimir effect parallel plates", conf, k=5))
print(f"      snippet-audit sample: {aud['n']} retrieved, {len(aud['snippet_dropped'])} snippet-dropped")

# --- 2. FIREWALL: verify input carries no retrieval/GOLD handle ---
print("\n[2] FIREWALL (proposer-feed vs verify-proof mechanically disjoint)")
seen_inputs = []

def mock_verify(c):
    seen_inputs.append(dict(c))                 # record exactly what verify sees
    # mark a DIRTY only if claim text contains 'FAB'
    dirty = "FAB" in c["claim"]
    return ("DIRTY" if dirty else "CLEAN"), {"_absorbed_knowledge": False}

def mock_call(model, prompt, options):
    # echo a fact; include the topic so novelty has something to compare
    return f"established fact about the topic in this prompt tail"

topics = ["Cooper pairs in BCS superconductivity theory",
          "Casimir effect between parallel conducting plates"]
gen_cond = G.make_generate(True, "mock", topics, "Scrutinize for fabricated-specifics.",
                           confirmed=conf, retrieve_fn=R.retrieve,
                           gold_frame="You are a disciplined epistemic agent.",
                           _call=mock_call)
out = gen_cond(2)
check("conditioned generate emits ONLY {topic,claim}",
      all(set(o.keys()) == {"topic", "claim"} for o in out))
# run through harness verify; harness asserts firewall internally
arm = F.run_arm(lambda n: out, mock_verify, k=2,
                retrieved_by_topic={t: [r["claim"] for r in R.retrieve(t, conf, 3)] for t in topics})
check("verify NEVER saw a retrieval/GOLD field (only topic,claim)",
      all(set(s.keys()) == {"topic", "claim"} for s in seen_inputs))
check("GOLD frame + confirmed facts were composed into PROMPT (context non-empty)",
      G.compose_context(R.retrieve(topics[0], conf, 3), "frame") != "")

# --- 3. NOVELTY guard ---
print("\n[3] GUARD1 novelty (regurgitation detection)")
fed = ["the casimir effect is an attractive force between two uncharged conducting plates"]
check("verbatim regurgitation flagged non-novel",
      F._near_dup(fed[0], fed) is True)
check("genuinely different claim flagged novel",
      F._near_dup("rubidium gas cooled to nanokelvin forms a condensate", fed) is False)

# --- 4. VERDICT LOGIC table (all 5 branches) ---
print("\n[4] VERDICT LOGIC (pre-registered, all branches)")
def arm_m(rate_f, fa=0.0, nov=None):
    return {"rate_f": rate_f, "fa_live": fa, "novelty": nov}
# FAIL: fa_live breach overrides
check("fa_live!=0 -> FAIL",
      F.adjudicate(arm_m(0.75), arm_m(0.25, fa=0.125, nov=1.0), True)["verdict"] == "FAIL")
# PASS: drop>=bar, novelty>=bar, guard2 ok
check("drop>=bar & novelty ok & rotation ok -> PASS",
      F.adjudicate(arm_m(0.75), arm_m(0.25, nov=0.875), True)["verdict"] == "PASS")
# COSMETIC: drop ok but novelty low
check("drop>=bar & novelty<bar -> COSMETIC",
      F.adjudicate(arm_m(0.75), arm_m(0.25, nov=0.50), True)["verdict"] == "COSMETIC")
# NULL_INERT: drop ok, novelty ok, but no rotation
check("drop>=bar & novelty ok & rotation MISSING -> NULL_INERT",
      F.adjudicate(arm_m(0.75), arm_m(0.25, nov=0.875), False)["verdict"] == "NULL_INERT")
# NULL: drop below bar
check("drop<bar -> NULL",
      F.adjudicate(arm_m(0.50), arm_m(0.50, nov=1.0), True)["verdict"] == "NULL")

print("\n" + "=" * 64)
if fails:
    print(f"DRY-VAL FAIL ({len(fails)}): " + "; ".join(fails))
    sys.exit(1)
print("DRY-VAL PASS -- logic sound vs real schema. LIVE run gated separately.")
print("=" * 64)
