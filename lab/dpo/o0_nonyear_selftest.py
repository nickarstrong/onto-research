#!/usr/bin/env python3
# o0_nonyear_selftest.py -- OFFLINE mechanism falsifier for the NON-YEAR EVIDENCE consumption patch.
# NO network, NO model, NOT the S3 eval, NO real labels (E15-safe: synthetic logic fixtures only).
# Proves scope_verdict() consumes temporal.per_specific correctly:
#   F1 (safety): a non-year specific is rescued ONLY by an oracle CONFIRM. REFUTE -> DIRTY (hard);
#                ABSTAIN or absent -> DIRTY (precision-first). A fabricated value can therefore never
#                pass without the exact+entity-anchored oracle (2b) emitting CONFIRM for it.
#   CONSUME: a CONFIRMed true specific is treated as SUPPORTED even on an empty abstract (the ff lift).
#   CONJUNCTION: one unverified specific sinks the whole claim even if another is CONFIRMed.
#   PRECEDENCE: a year REFUTE dominates any per_specific CONFIRM.

import sys
import o0_temporal_evidence as W

def rec(claim, abstract="", per_specific=None, per_year=None):
    return {"claim": claim,
            "evidence": {"abstract": abstract},
            "temporal": {"per_year": per_year or {}, "snippets": [],
                         "per_specific": per_specific or {}}}

# (name, record, expected_verdict)
CASES = [
    ("CONFIRM rescues true date (empty abstract -> ff lift)",
     rec("Event on March 5 of that year.", per_specific={"march 5": "CONFIRM"}), "CLEAN"),
    ("REFUTE catches fabricated date (hard DIRTY)",
     rec("Event on March 5 of that year.", per_specific={"march 5": "REFUTE"}), "DIRTY"),
    ("ABSTAIN -> precision-first DIRTY",
     rec("Event on March 5 of that year.", per_specific={"march 5": "ABSTAIN"}), "DIRTY"),
    ("absent (no oracle entry) -> DIRTY",
     rec("Event on March 5 of that year.", per_specific={}), "DIRTY"),
    ("literal-in-abstract still supported (no regression)",
     rec("Event on March 5 of that year.", abstract="It happened on March 5.",
         per_specific={"march 5": "ABSTAIN"}), "CLEAN"),
    ("NUMBER CONFIRM rescues true percentage",
     rec("The efficiency was 56.3% in tests.", per_specific={"56.3%": "CONFIRM"}), "CLEAN"),
    ("NUMBER REFUTE catches fabricated percentage",
     rec("The efficiency was 56.3% in tests.", per_specific={"56.3%": "REFUTE"}), "DIRTY"),
    ("CONJUNCTION: one ABSTAIN sinks claim despite other CONFIRM",
     rec("On March 5, efficiency was 56.3%.",
         per_specific={"march 5": "CONFIRM", "56.3%": "ABSTAIN"}), "DIRTY"),
    ("PRECEDENCE: year REFUTE dominates a specific CONFIRM",
     rec("On March 5, in that year.", per_year={"1999": "REFUTE"},
         per_specific={"march 5": "CONFIRM"}), "DIRTY"),
]

def main():
    ok = True
    for name, r, want in CASES:
        got, why = W.scope_verdict(r)
        good = (got == want); ok &= good
        print("  [%s] %-55s want=%-5s got=%-5s %s" %
              ("PASS" if good else "FAIL", name, want, got, "" if good else why))
    print("\nNON-YEAR MECHANISM SELF-TEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
