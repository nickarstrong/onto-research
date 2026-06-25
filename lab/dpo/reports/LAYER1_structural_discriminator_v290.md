# LAYER-1 HERMETIC STRUCTURAL DISCRIMINATOR -- BUILD REPORT (v290)

Plane: Type C BUILD. Substrate frozen; verifier o0_temporal_evidence.py (md5 92766b06) NOT edited.
Discriminator shipped as a SEPARATE module (o0_structural_discriminator.py).
Aggregate verdicts only -- no row-level claims / labels / planted-true mapping (R15 leak-guard;
held-out cut + keyfile stay LOCAL, never public git).

Bar authority: sealed PREREG_gengap_structural (v287, LOCAL). On any wording conflict the sealed
PREREG governs over session-pack shorthand (disk-wins, conveyor Sec 3.10).

## 0 - INTAKE / ANCHORS
- HEAD f752b9a, tree clean.
- Substrate (4) + structural mint (3 jsonl) md5 = anchors (7/7 PASS). Frozen verifier = 92766b06.
- offline year table present (2 rows).
- GT-CLEAN held-out source: heldout_raw_20260625 + sealed_labels_heldout_20260625 (LOCAL bait).

## 1 - SEAL N_c (truthful, by-construction)
- N_anachronism = 5 ; N_false_precision = 5 ; N_internal_inconsistency = 5. TOTAL 15, all DIRTY.
- Matches v289 mint anchor.

## 2 - BASELINE FLIP-RATE (sealed B1 baseline clause, frozen verifier, offline, blind rows)
Sealed bar (PREREG sec 2 B1) requires: baseline flip-rate on the structural subset == 0, where a
"flip" = the frozen verifier firing DIRTY (catching the fabrication). NOT "every row ABSTAIN" --
that was session-pack shorthand drift; the sealed clause governs.

Frozen 92766b06 over the 15 blind fabrication rows:
- DIRTY fires: 0 / 15  -> baseline flip-rate 0 -> subset confirmed UNSEEN (R6 sec 3 not void).
- texture: anachronism 5 x CLEAN-by-vacuum ; numeric_false_precision 5 x ABSTAIN ;
  internal_inconsistency 5 x ABSTAIN.

CLEAN-by-vacuum: C-1 year single-ownership strips the lone year token of a year-only claim ->
empty non-year specific set -> verifier default CLEAN. Structural property of the frozen verifier
(not a mint defect); a false-CLEAN that strengthens the case for Layer-2.

Collision-check: 5 planted anachronism years vs the 2-row offline year table -> intersection
EMPTY. No anachronism row already-gated. PASS. (Operand year sets withheld: R15.)

## 3 - SEALED BARS B0 / B1 / B2
### B0 -- ABSOLUTE (false-DIRTY on GT-CLEAN held-out == 0)
Discriminator over the GT-CLEAN held-out subset (founder_label==CLEAN): 35 rows.
Verdicts: ABSTAIN 35 / DIRTY 0.  false_DIRTY_on_GT_CLEAN = 0  -> PASS.
(Held-out label dist on disk = CLEAN 35 / DIRTY 13, post-P4-correction v274; an earlier 31/17
memory tile is stale -- disk-wins.)

### B1 -- DISCRIMINATION (per class, PASS iff flips > floor(N_c/2); floor(5/2)=2)
- internal_inconsistency : flips 5 > 2 -> PASS
  (two in-claim years + asserted "N years" span; recompute |Y2-Y1|; asserted != computed -> DIRTY.
   Cross-validated vs keyfile recompute spec: computed==true and asserted==planted on all 5.)
- numeric_false_precision : flips 0 <= 2 AND false_DIRTY 0 -> HONEST-ABSTAIN (declared, not a pass)
- anachronism            : flips 0 <= 2 AND false_DIRTY 0 -> HONEST-ABSTAIN (defer Layer-2 / B3)

### B2 -- HERMETICITY (Layer 1 only)
Two cold runs byte-identical (verdict dump md5 0b963900 both); 0 stderr; no network primitives
referenced in either module.  -> PASS.

Keystone (PREREG sec 1): enemy is FALSE-DIRTY, never ABSTAIN. Total false-DIRTY across DIRTY-cut
and GT-CLEAN = 0. A fabricated verdict would be R7 on the verifier itself.

BUILD = CLEAN-PASS (B0 & B1 & B2; keyfile xcheck OK).

## 4 - R3 LIMITATION (declared, not swallowed)
The intinc rule assumes the two years + the "N years" span form a subtraction relation. A claim
with two UNRELATED years plus an unrelated "N years" count could false-DIRTY. Verified 0
false-DIRTY on both the 15-row PREREG set AND the 35-row GT-CLEAN held-out; a relation-anchor gate
is deferred, not built here.

## 5 - NEXT (verdict only)
Catching anachronism + numeric_false_precision needs Layer-2 (oracle, B3), BLOCKED until WATCH-F
closes (year-oracle false-refute on a true-year claim). Entity/relation rows (v288 OPEN RULING)
enter only if the ruling pulls them into scope.

---
v290 - Type C BUILD - o0_structural_discriminator.py (Layer-1). Aggregate-only, R15-clean.
