"""
test_citation_verify.py -- G1 gate, deterministic, NO GPU, NO network.

Gate step6_apparatus_v1, G1:
  PASS = flags fake DOI 10.1038/nature20547 -> DIRTY
         AND passes >=1 known-real DOI -> CLEAN.
Plus the false-DIRTY-free guard: resolution-failure -> UNVERIFIED, not DIRTY.

Frozen allowlist (offline-deterministic):
  real:  10.1038/nature14539  (LeCun/Bengio/Hinton, Nature 521:436-444, 2015;
                               existence web-verified at build time -- R7)
  fake:  10.1038/nature20547  (Founder-sealed DIRTY ground-truth, gate; E15 -- not re-authored)
"""

import sys

from citation_verify import (
    CLEAN, DIRTY, UNVERIFIED,
    FrozenOracle, verify_citation,
)

REAL_DOI = "10.1038/nature14539"
FAKE_DOI = "10.1038/nature20547"

ORACLE = FrozenOracle(real={REAL_DOI}, fake={FAKE_DOI})


def run() -> int:
    checks = [
        # (label, doi, expected) -- the two gate-mandated cases first.
        ("fake DOI -> DIRTY            (gate)", FAKE_DOI, DIRTY),
        ("real DOI -> CLEAN           (gate)", REAL_DOI, CLEAN),
        # false-DIRTY-free guard: an unknown well-formed DOI must NOT be flagged.
        ("unknown DOI -> UNVERIFIED   (no false flag)", "10.1000/xyz123", UNVERIFIED),
        # resolution-failure proxy is the same UNRESOLVED path (covered above).
        # malformed identifier must never become DIRTY.
        ("malformed -> UNVERIFIED     (not DIRTY)", "not-a-doi", UNVERIFIED),
        ("empty -> UNVERIFIED         (not DIRTY)", "", UNVERIFIED),
    ]

    failed = 0
    for label, doi, expected in checks:
        got = verify_citation(doi, ORACLE)
        ok = got == expected
        failed += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {label:42s} -> {got:11s} (exp {expected})")

    gate_pass = (
        verify_citation(FAKE_DOI, ORACLE) == DIRTY
        and verify_citation(REAL_DOI, ORACLE) == CLEAN
    )
    print("-" * 64)
    print(f"G1 GATE: fake->DIRTY AND real->CLEAN  ==>  {'PASS' if gate_pass else 'FAIL'}")
    print(f"false-DIRTY-free guard (3 cases)      ==>  "
          f"{'PASS' if failed == 0 else 'FAIL'}")
    return 0 if (gate_pass and failed == 0) else 1


if __name__ == "__main__":
    sys.exit(run())
