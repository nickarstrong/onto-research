# REPORT -- number-class v4 ff RE-MEASURE (fresh set, TYPE B)
date: 2026-06-25 | session: v268 | type: B (analysis, measure-only)
verifier: o0_temporal_evidence.py md5 6857e801dad6ea7069edfd3d0cf96ee8 (FROZEN, == v4 build, diff empty)
sealed bars: reports/PREREG_AMENDMENT_v4_number_class.md md5 7a42d312404839272b5d556662d7043c
input set: fresh held-out, 48 claims (LOCAL/gitignored), md5 6255ce008ab554a392c93ab0163d6d1b (unchanged pre/post, VIOLATION-A guard held)
GT: Founder labels (LOCAL/gitignored). run: oracle-bound LOCAL, 334.3s. HEAD a46c7df.

## GT distribution
CLEAN=31 | DIRTY=17 (all dirty_class=specifics; ZERO year-class dirty in this set)

## Confusion (founder_label x scope.verdict)
GT-CLEAN(31): CLEAN=21  DIRTY=0   ABSTAIN=10
GT-DIRTY(17): CLEAN=11  DIRTY=1   ABSTAIN=5

## Partition vs sealed v4 falsifiers
C-1 year channel:
  - FF-clear arm: year-only GT-CLEAN -> DIRTY = 0 (baseline 14/24). PASS.
  - catch arm (GT-DIRTY year-class): 0 such items in set -> NOT EXERCISED.
    held2_20_0 (lone DIRTY) caught via year_refuted:1837 but GT class = specifics -> incidental mechanism.
C-2 number gate (empty-abstract partition, per_specific != {}):
  - arm1 empty-abstract GT-CLEAN bare-qty -> ABSTAIN: 10/10, DIRTY=0 (baseline 9/9 -> 0). PASS.
  - arm2 non-empty-abstract GT-DIRTY contradicted bare-qty -> DIRTY: 0 such cases -> NOT EXERCISED.
Sealed FAIL triggers (ABSTAIN-leak-contradicted / empty-true-bare-qty-still-DIRTY): none fired.

## VERDICT: PASS on sealed bars (false-fire elimination, 0/31 GT-CLEAN false-fires)
Caveats (R2/R3/R7, load-bearing):
  1. Pass is false-fire-side ONLY. Both catch-preservation arms NON-EXERCISED.
     A pure-ABSTAIN gate would pass identically. Non-discriminative on this set.
  2. 11/17 GT-DIRTY leaked CLEAN -- NOT a C-1/C-2 falsifier-FAIL. Root cause = EXTRACTION layer:
     load-bearing dirty specific never tokenized into per_specific (all 11 have per_specific={})
     -> gate never adjudicated -> scope CLEAN via "...or none" branch.
     NEW defect class, outside number-gate scope. Hard blocker for any conditioned/absorb run.
  3. DIRTY recall raw 1/17 caught, 5/17 quarantine-ABSTAIN (empty-abstract, design-excused), 11/17 leak CLEAN.

## CONSEQUENCE
PASS (literal) -> HEADROOM v4 un-defers + POOL HYGIENE unblocks (per prereg ?4).
NEW OWED (this measure): EXTRACTION-LEAK -- 11 GT-DIRTY-specifics absorbed CLEAN via non-extraction.
  Open BEFORE any conditioned/absorb run. Separate track from C-1/C-2 (gate behaved correctly given inputs).
WATCH: held2_00_0 claim text carries terminal escape codes (gen artifact, parse-only, no verdict impact).
