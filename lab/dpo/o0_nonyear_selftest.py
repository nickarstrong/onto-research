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


# ----------------------------------------------------------------------------------------------
# ORACLE control-flow falsifier (verify_specific) via a MOCK frozen-probe T. NO network.
# Proves: CONFIRM only on EXACT spec + subject same-sentence; ABSTAIN on absence, fabrication
# (exactness), and incidental non-co-location. No REFUTE path (non-year is CONFIRM|ABSTAIN).
import re as _re
class _MockT:
    def __init__(self, article): self.article = article
    _TOK = staticmethod(lambda x: set(_re.findall(r'[a-z]{3,}', (x or "").lower())))
    def strip_wiki_markup(self, t): return t or ""
    def extract_subjects_in_sentence(self, sent, spec): return ["Watson"]
    def subject_role(self, label, sent): return "person"
    def resolve_subject(self, label, ctx, role): return ("Q123", "biologist", 1, "ctx")
    def entity_data(self, qid): return {"enwiki_title": "James Watson"}
    def wiki_fulltext(self, title): return self.article

ORACLE_CASES = [
    ("CONFIRM exact date + subject same sentence",
     "February 28", "On February 28, 1953, Watson and Crick described the structure.", "CONFIRM"),
    ("ABSTAIN date absent from article",
     "February 28", "Watson and Crick worked at Cambridge for years.", "ABSTAIN"),
    ("ABSTAIN fabricated number not in article (F1 exactness)",
     "56.3%", "Watson reported an efficiency around 56% in the study.", "ABSTAIN"),
    ("CONFIRM exact number + subject same sentence",
     "56.3%", "Watson measured 56.3% in the controlled run.", "CONFIRM"),
    ("ABSTAIN spec present but not co-located with subject",
     "February 28", "February 28 is a date. Separately, Watson studied genetics.", "ABSTAIN"),
]

def test_oracle():
    ok = True
    print("== ORACLE control-flow (mock-T, no network) ==")
    for name, spec, article, want in ORACLE_CASES:
        v, _ = W.verify_specific(spec, "claim " + spec, set(["watson", "crick"]), _MockT(article), {})
        good = v == want; ok &= good
        print("  [%s] %-50s want=%-7s got=%-7s" % ("PASS" if good else "FAIL", name, want, v))
    return ok


def main():
    ok = True
    for name, r, want in CASES:
        got, why = W.scope_verdict(r)
        good = (got == want); ok &= good
        print("  [%s] %-55s want=%-5s got=%-5s %s" %
              ("PASS" if good else "FAIL", name, want, got, "" if good else why))
    ok &= test_oracle()
    print("\nNON-YEAR MECHANISM SELF-TEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
