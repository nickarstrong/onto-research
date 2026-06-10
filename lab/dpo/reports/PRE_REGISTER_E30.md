# PRE_REGISTER_E30 -- binding-discipline veto: candidate-SCOPE lever (TOP1 vs ANY)

STATUS: FROZEN pre-data. No probe has been run. Authored TYPE A (design). The supervised run is E31 (TYPE C).
This document fixes the decision rule, grids, gates, regression anchor, falsifier, and oracle-leak ruling
BEFORE any E30 data is seen. After freeze: relitigation forbidden; results read against THIS file only.

provenance read at STEP 0 (md5-verified on disk):
- run_E28_probe.py            md5 a9fe3ba18ec7f4c0c0e37f84f5052bd7  (frozen BASE; copied, not edited in place)
- report_E29_reauthor.md      md5 c1f38de7769eda990d20ee68404480c1  (REVERSAL: tail = misbinding, not phrasing)

## 0  hypothesis (derived from E29 REVERSAL)

The E27/E28 knife-edge (B2 pinned to the 0.90 recall floor; joint band width 0) is produced by the
ANY-CANDIDATE veto (run_E28 line 153). A gold claim retrieves its true entailing support AND a topically-near
WRONG-SOURCE record; the wrong-source record faithfully contradicts the claim, so `any-candidate` veto fires
and the gold claim is falsely vetoed -- pinning recall to the floor and preventing the op-point from lowering
C to catch more spoof.

H1 (primary): restricting the veto to the claim's BOUND support (top-1 cosine candidate) spares the misbound
gold (its top-1 candidate entails, not contradicts), lifting B2 off the 0.90 floor. The op-point can then push
C lower -- catching more spoof via their OWN top-1 contradiction -- so false-accept drops BELOW the E28 op
0.0667 while spoof reject-share holds. The E28 knife-edge opens into a robust joint band.

H0 (falsifier, see sec6): TOP1 does NOT drop false-accept below 0.0667, OR the band stays non-robust, OR
spoof reject-share collapses (S3 <= 0.50). Any of these => near-source veto is NOT the dominant driver =>
the ceiling is model scale (bart-large-mnli) => escalate model class (lab-migration protocol).

## 1  decision rule -- FROZEN (the ONLY change vs run_E28)

run_E28 candidate scope (line 153, ANY):
    veto = any((sc >= C and cos <= K) for (cos, sc) in r[1])

E30 candidate scope = a SCOPE parameter on item_label_at_C. Exactly one line of veto logic changes; everything
else (retrieval, NLI direction premise=source.finding / hyp=claim, rollup, classes, gates machinery) is
byte-identical to run_E28.

    SCOPE = "top1"  (PRIMARY, frozen operative rule for E30/E31):
        cos0, sc0 = r[1][0]            # r[1][0] = highest-cosine authorized candidate = bound support
        veto = (sc0 >= C and cos0 <= K)
    SCOPE = "any"   (REGRESSION ANCHOR ONLY; == run_E28 line 153 verbatim):
        veto = any((sc >= C and cos <= K) for (cos, sc) in r[1])

r[1] is guaranteed non-empty in the "auth" branch (authorized non-empty checked at run_E28 line 126); r[1][0]
is well-defined. Ordering top-1-first is guaranteed by candidates_with_cosine (argsort(-sims), floor-break) +
the authorized filter preserving order (run_E28 lines 102-106, 125, 129-139). VERIFIED at STEP 0.

ROBUSTNESS ARM (B, reported, NOT the primary verdict):
    SCOPE = "margin"(delta):  a candidate may veto iff cos_j >= cos0 - delta  (bound-neighborhood).
        delta = 0      -> degenerates toward TOP1 (top-1 only, modulo cosine ties).
        delta = +inf   -> degenerates to ANY  (regression anchor; identical to SCOPE="any").
        delta grid (FROZEN pre-data): [0.00, 0.02, 0.05, 0.10, 0.20].
    The margin arm is computed and reported for sensitivity; the E30/E31 PASS/FAIL verdict reads SCOPE="top1".

## 2  grids -- CARRIED BYTE-IDENTICAL from run_E28 (no re-tuning; diff proof below)

C selection: over OBSERVED contradiction values only (no post-hoc fishing) -- run_E28 C_obs construction reused.
K cosine gate (carried; K=+inf disables the gate):
    K_GRID = sorted(set(round(0.45 + 0.05*i, 2) for i in range(0,12)))   # 0.45 .. 1.00   (run_E28 line 54)
S2 robustness sweep grid (carried):
    S2_GRID = coarse [0.900,0.995] step 0.005 + fine [0.990,0.999] step 0.001  (run_E28 lines 45-46)
    S2_BAND_MIN_WIDTH = 0.01 ; S2_BAND_MIN_POINTS = 3 ; liftoff > 0          (run_E28 lines 47-48,187)
S3 attribution + bar:
    S3_REJECT_SHARE_BAR = 0.50                                              (run_E28 line 49)
constants carried verbatim: E20B_FALSE_ACCEPT 0.467 ; GATE_FA 0.10 ; RECALL_FLOOR 0.90 ; DEGENERATE_RHO 0.95
    (FROZEN E26 VOID guard) ; PREREG_RHO_ADVISORY 0.50 (reported only) ; B*_CLASS labels ; B2_EXCLUDE {ho_23}.

DIFF PROOF (to be recorded in report_E30 by the E31 runner): `diff run_E28_probe.py run_E30_probe.py` must
show ONLY (a) the SCOPE branch in item_label_at_C + its threading through metrics_at_C/s2_band_at_K/
s3_attribution/op-point selection, (b) the default --out path, (c) the regression-anchor SCOPE="any" control +
its assert, (d) header/comment text. NO grid constant, NO class label, NO gate threshold differs.

## 3  trust gates (else VOID) -- carried + one added

T1 baseline-sanity (carried): C=+inf, no veto fires under ANY scope (nothing crosses) -> false-accept MUST
    reproduce no-veto 0.467 (model-independent). Acceptance band 0.40 <= fa_base <= 0.53. Else VOID_BASELINE.
T2 input md5 (carried): fixture 4a45f52883a802e8d8d1d5ff5d185bdb (gold_fixture_E25b.json, E29 byte-identical),
    heldout 7e9fe030646d5671952e7a9fe9437e37 (heldout_E17.jsonl). Mismatch -> STOP.
T3 from_finding > 0 (carried): VOID-by-construction guard (E23). content-binding must be live.
T4 contradiction_idx read from id2label (carried): never hardcoded; single contradiction label asserted.
T5 decorrelation rho (carried): FROZEN VOID guard rho >= 0.95 (one-sided) -> VOID_DEGENERATE. advisory
    |rho| < 0.50 REPORTED only (unchanged conflict; reconcile at integration, not here).
T6 REGRESSION ANCHOR (E30-specific, the load-bearing new guard): with SCOPE="any" the op-point selection MUST
    reproduce E28's operating point -- chosen op false-accept == 0.0667 (E28 op, == E26/E27). If SCOPE="any"
    does NOT reproduce 0.0667 -> VERDICT REGRESSION: the edit broke the machinery; reconcile before reading
    the TOP1 result. (Subsumes E28's K=+inf->E27 scalar check transitively.)

## 4  op-point + verdict machinery (carried; verdict reads SCOPE="top1")

op-point (carried selection): over OBSERVED (C,K) under SCOPE="top1", min false-accept subject to B2 >= 0.90;
    frozen tie-break = widest joint C-band at that K -> lowest C -> highest K. selection peeks ONLY recall.
metrics read at the TOP1 op-point:
    fa  = 1 - B1  (spoof demotion miss-rate)        GATE: fa <= 0.10
    B2  = gold VERIFIED rate (recall)               GATE: B2 >= 0.90
    S2  joint (fa<=0.10 AND B2>=0.90) band at op-K  ROBUST: width>=0.01 AND points>=3 AND B2-liftoff>0
    S3  reject_share = (fa_base - fa_op)/fa_base    GATE: > 0.50  (veto, not coverage, owns the reduction)

## 5  oracle-leak ruling -- ADMISSIBLE (checked pre-data)

The TOP1 rule conditions the veto on `top-1 by binding COSINE`. Cosine and retrieval rank are OBSERVABLE at
decision time -- no held-out true-class label, no gold/spoof identity, enters the rule. The MARGIN arm
conditions on cosine distance to top-1: also observable. NEITHER scope reads a per-class or true-class signal.
RULING: admissible (same standard that admitted E28's cosine gate K). Explicitly forbidden and absent: any
selection keyed on the held-out class label, the bound-source identity, or per-pair gold/spoof membership.

## 6  PASS / FAIL fork (the ONLY operative E30/E31 verdict; reads SCOPE="top1")

PASS_BINDING_CONFIRMED (H1 supported, misbinding is the driver):
    fa_top1 < 0.0667 (strictly below the SCOPE="any" regression anchor)  AND
    S2 band robust (width>=0.01, points>=3, B2 lifts off the 0.90 floor)  AND
    S3 reject_share > 0.50.
    -> the E27/E28 knife-edge was the ANY-veto misbinding; TOP1 resolves it. Graduate the bound-veto into the
       verifier (verify_E16 integration; TOMMY GO REQUIRED; reconcile rho guard 0.95 vs 0.50; wire
       entailment-lift -> S3 three-way) -> full-GOLD scale re-test.
PASS_WEAK (gate met, mechanism not decisively shown):
    fa_top1 <= 0.10 AND B2 >= 0.90 AND S3 > 0.50, but fa_top1 >= 0.0667 OR band still non-robust.
    -> TOP1 holds the gate but does not beat E28; misbinding is partial. Run the MARGIN arm; do NOT integrate.
FAIL_NOT_THE_DRIVER (H0 / falsifier):
    fa_top1 > 0.10, OR spoof reject-share S3 <= 0.50 (TOP1 lost spoof rejection -- spoofs needed non-top-1
    candidates to be caught).
    -> near-source veto is NOT the dominant driver -> ceiling is model scale (bart-large-mnli) -> escalate
       model class via lab-migration protocol (regenerate L1 -> retrain -> baseline eval -> compare R-bars).
REGRESSION:
    SCOPE="any" op-point does NOT reproduce E28 op fa 0.0667 (T6) -> machinery broke -> reconcile before reading.
VOID_*:
    any trust gate T1/T2/T3/T4/T5 fails -> rebuild.

## 7  design-gate checklist (this session, TYPE A -- NOT a probe verdict)

- [x] decision rule FROZEN pre-data (sec1: SCOPE="top1" primary; "any" = regression anchor; margin = arm).
- [x] oracle-leak checked + ruled admissible (sec5: cosine/rank observable; no class/true-source conditioning).
- [x] regression anchor defined (sec3 T6: SCOPE="any" reproduces E28 op fa 0.0667).
- [x] falsifier stated (sec6 FAIL_NOT_THE_DRIVER: escalate model class).
- [x] grids carried byte-identical from run_E28 (sec2 + diff-proof requirement on the E31 runner).
- [ ] PRE_REGISTER_E30.md frozen + md5 recorded + committed (this session, after authoring).
- [ ] run_E30_probe.py built, on disk, NOT in git (next step; committed in E31 alongside report_E30).

## 8  footguns (carry from run_E28 sec6 / pack v68 sec6)

- default --out MUST be reports/report_E30.md -- NEVER a frozen-report path (no clobber of report_E28/E27).
- env floor 0.45 set BEFORE importing semantic_retrieve (code default 0.55 = footgun); assert == 0.45.
- pyarrow imported line 1 before torch; never sentence_transformers; KMP_DUPLICATE_LIB_OK=TRUE.
- frozen run_E28_probe.py NEVER edited in place; E30 is a NEW file.
- r[1][0] assumes top-1-first ordering -- asserted in the probe (cosines non-increasing within each resolution).
