#!/usr/bin/env python3
# o0_subclaim_selftest.py -- OFFLINE falsifier for the subclaim-scope patch.
# NO network, NO model, NOT the §3 eval. Runs scope_verdict() (patched o0_temporal_evidence.py)
# over the FROZEN claims_blind_ev_temporal.jsonl (v219 wire output) and checks the pre-registered
# falsifier from REPORT_organ_subclaim_scope_v1 sec 5:
#   PRIMARY  : the 3 v219 fa_live cases MUST read DIRTY post-scope (fabricated day/number no longer
#              rides a year CONFIRM/coverage).
#   SECONDARY: genuinely year-only CONFIRM-rescued CLEANs MUST NOT regress to DIRTY.
# FLAGGED is reported, not asserted: a non-year-only claim carrying an extra unverifiable exact day
# -> scope catches it DIRTY; whether that is a true catch or an over-flag is a Founder label (E15).

import json, sys
import o0_temporal_evidence as W

PRIMARY          = ["held2_04_0", "held2_11_0", "held2_13_1"]   # correct year + fabricated day/number
YEAR_ONLY_CLEAN  = ["held2_05_1", "held2_11_1", "held2_14_0",   # subject+topic+year, no extra
                    "held2_14_1", "held2_19_0"]                 # date/number specific
FLAGGED          = ["held2_06_1"]                               # extra exact day, not year-only

def main(path):
    rows = {json.loads(l)["id"]: json.loads(l) for l in open(path, encoding="utf-8") if l.strip()}
    ok = True

    print("== PRIMARY (must be DIRTY) ==")
    for i in PRIMARY:
        v, why = W.scope_verdict(rows[i]); good = (v == "DIRTY"); ok &= good
        print("  %-14s -> %-6s %s  %s" % (i, v, "PASS" if good else "FAIL", why))

    print("== SECONDARY year-only (must NOT regress -> CLEAN) ==")
    for i in YEAR_ONLY_CLEAN:
        v, why = W.scope_verdict(rows[i]); good = (v == "CLEAN"); ok &= good
        print("  %-14s -> %-6s %s  %s" % (i, v, "PASS" if good else "FAIL", why))

    print("== FLAGGED (not year-only; scope catches extra unverified day; label E15-owed) ==")
    for i in FLAGGED:
        v, why = W.scope_verdict(rows[i])
        print("  %-14s -> %-6s  %s" % (i, v, why))

    print("\nSELF-TEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "claims_blind_ev_temporal.jsonl"))
