#!/usr/bin/env python3
# -*- coding: ascii -*-
"""g2_wire_sanity.py -- offline validation of the G2 citation wire.

Deterministic. NO network / NO GPU / NO Ollama / NO temporal module.
Validates the new seam (controller.citation_pass / merge_verdict) with a
FrozenOracle AND the real falsifier.run_arm contract, BEFORE the generator is
touched. PASS here is the pass-gate for the blind eval.

REGRESSION GUARD (the v-prev bug): merge_verdict MUST return reasons as a DICT
because falsifier.run_arm calls reasons.get("_absorbed_knowledge"). A list
coercion raised AttributeError at run time -- caught here now via a dict-shape
assert and a real run_arm round-trip.
"""
import sys

import controller
import falsifier_step6 as F
from citation_verify import FrozenOracle

REAL = "10.1038/nature14539"   # exists  (G1 CLEAN anchor)
FAKE = "10.1038/nature20547"   # absent  (G1 DIRTY anchor)
ORACLE = FrozenOracle(real={REAL}, fake={FAKE})

# scope_verdict returns reasons as a DICT -- mirror that here.
TDICT = {"_absorbed_knowledge": None, "note": "temporal-stub"}

# (name, claim, temporal_in, expect_verdict, expect_dirty_count)
CASES = [
    ("fake_doi_in_prose",
     "The human brain has ~86 billion neurons (see %s)." % FAKE,
     "CLEAN", "DIRTY", 1),
    ("real_doi_passthrough",
     "Deep learning was reviewed in %s." % REAL,
     "CLEAN", "CLEAN", 0),
    ("no_doi_temporal_clean_stands",
     "Water boils at 100 C at sea level.",
     "CLEAN", "CLEAN", 0),
    ("no_doi_temporal_dirty_stands",
     "Event happened on February 30, 1999.",
     "DIRTY", "DIRTY", 0),
    ("fake_doi_overrides_clean_temporal",
     "Daily intake 2 L, ref %s." % FAKE,
     "CLEAN", "DIRTY", 1),
    ("trailing_period_stripped",
     "Speed of sound 343 m/s, doi %s." % FAKE,
     "CLEAN", "DIRTY", 1),
    ("unknown_doi_unverified_not_flagged",
     "Some fact with doi 10.9999/unknown-but-wellformed.",
     "CLEAN", "CLEAN", 0),
]

ok = True


def fail(name):
    global ok
    ok = False
    print("  [FAIL] %s" % name)


for name, claim, tin, exp_v, exp_dc in CASES:
    dirty, _ann = controller.citation_pass(claim, ORACLE)
    # real signature: merge_verdict(temporal_verdict, temporal_reasons, claim, oracle)
    v, reasons = controller.merge_verdict(tin, dict(TDICT), claim, ORACLE)
    shape_ok = isinstance(reasons, dict)
    getable = True
    try:
        _ = reasons.get("_absorbed_knowledge")   # the exact call run_arm makes
    except AttributeError:
        getable = False
    if not (v == exp_v and len(dirty) == exp_dc and shape_ok and getable):
        fail("%-38s verdict=%s(exp %s) dirty=%d(exp %d) dict=%s getable=%s"
             % (name, v, exp_v, len(dirty), exp_dc, shape_ok, getable))
    else:
        print("  [PASS] %-38s verdict=%-6s dirty=%d dict=ok getable=ok"
              % (name, v, len(dirty)))

# --- end-to-end run_arm contract (the path that crashed) ---
CLAIMS = [{"topic": "t_fake", "claim": "neurons ref %s" % FAKE},
          {"topic": "t_real", "claim": "review %s" % REAL},
          {"topic": "t_none", "claim": "water boils at 100 C"}]


def stub_generate(k):
    return [dict(CLAIMS[i % len(CLAIMS)]) for i in range(k)]


def stub_verify(c):
    # mimics controller.live verify: temporal-stub dict + citation merge
    return controller.merge_verdict("CLEAN", dict(TDICT), c["claim"], ORACLE)


try:
    arm = F.run_arm(stub_generate, stub_verify, 3)
    contract_ok = (arm["k"] == 3 and arm["fa_live"] == 0.0
                   and abs(arm["rate_f"] - 1.0 / 3.0) < 1e-9 and len(arm["rows"]) == 3)
    print("  [%s] run_arm contract  rate_f=%.3f fa_live=%.3f rows=%d"
          % ("PASS" if contract_ok else "FAIL", arm["rate_f"], arm["fa_live"], len(arm["rows"])))
    if not contract_ok:
        ok = False
except Exception as e:
    ok = False
    print("  [FAIL] run_arm raised: %r" % e)

print("\nfirewall: oracle =", type(ORACLE).__name__,
      "(external-registry stand-in; no GOLD/episodic field touched)")
print("WIRE SANITY:",
      "PASS -- merge dict-shape correct, run_arm contract holds -> re-run blind eval"
      if ok else "FAIL -- do NOT run the eval")
sys.exit(0 if ok else 1)
