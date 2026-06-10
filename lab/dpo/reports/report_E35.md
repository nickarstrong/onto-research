# report_E35 -- second organ: entailment-lift ACCEPT rescue + FROZEN binding-veto REJECT (three-way) vs reject-only 0.1667 (S1/S2/S3)

- pre-register   : PRE_REGISTER_E35.md (FROZEN md5 8c719b0bdc88250165bce434c9652eea) -- sec1/2/4/5/6 operative ; reject path inherits PRE_REGISTER_E34 (91ae26c51ee794fa6f5c94497d109be0)
- lever          : THREE-WAY -- REJECT (FROZEN: con>=C AND B>=B_floor) RESCUED by ACCEPT (ent>=A AND B>=B_floor) over BOUND subset; B=lexical overlap(claim,premise); premise=source.FINDING / hyp=claim ; MODEL=MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (UNCHANGED)
- accept arm     : ent direction premise=source.finding ; hyp=claim ; P(entailment) ; entailment_idx READ from id2label (single, asserted) ; A swept over FROZEN A_GRID [0..1 step 0.05]; A=+inf = accept-off regression anchor
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## trust gates (else VOID)
- baseline (C=+inf) B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True
- degeneracy (B_floor=0,A=+inf scope=any) fa=0.23333333333333328 vs deberta anchor 0.2333 +/-0.02 -> ok=True (inherited clean-superset)
- accept-off regression (A=+inf reject-only op) fa=0.16666666666666663 vs E34b op 0.1667 +/-0.02 -> ok=True (clean-superset for the accept arm)
- decorrelation spearman(contradiction,cosine) rho = -0.269 over 139 pairs | VOID-guard rho>=0.95 -> degenerate=False
- advisory: |rho| < 0.5 -> True (REPORTED ONLY; FROZEN substrate VOID-guard is 0.95; see CONFLICT note)
- contradiction_idx + entailment_idx read from id2label (single each, asserted) ; from_finding=109 asserted > 0

## op-point gate (scope=any; min fa s.t. B2>=0.90 over (A_GRID, observed C, B_floor)). bars: reject-only 0.1667 (beat) / GATE 0.10
- anchor-compare (scope=any): A=0.05 C=0.9077617526054382 B_floor=0.0 fa_op=0.06666666666666665 vs bart 0.0667 / deberta 0.2333 / reject-only 0.1667 -> below_bart=True
- chosen A (accept) = 0.05 | chosen C = 0.9077617526054382 | chosen B_floor (binding gate) = 0.0 | B2 at op-point = 0.9
- B1 spoof-demotion = 0.9333333333333333
- false-accept      = 0.06666666666666665  (gate <= 0.1)
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.4003333333333334
- op-point verdict  = PASS

## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=any). delta gates a cosine bound-neighborhood on top of B
    delta=0.00  C=0.0018105095950886607  B_floor=0.1  fa=0.16666666666666663  B2=0.9  band_robust=False  reject_share=0.6428571428571429
    delta=0.02  C=0.04188667610287666  B_floor=0.07692307692307693  fa=0.1333333333333333  B2=0.9  band_robust=False  reject_share=0.7142857142857143
    delta=0.05  C=0.04188667610287666  B_floor=0.07692307692307693  fa=0.06666666666666665  B2=0.9  band_robust=False  reject_share=0.8571428571428572
    delta=0.10  C=0.04188667610287666  B_floor=0.07692307692307693  fa=0.033333333333333326  B2=0.9  band_robust=False  reject_share=0.9285714285714286
    delta=0.20  C=0.2226661592721939  B_floor=0.07692307692307693  fa=0.033333333333333326  B2=0.9  band_robust=False  reject_share=0.9285714285714286

## S2 -- (C, B_floor) band / lift-off robustness (band read at op-point B_floor; FROZEN grids)
- band at op-point B_floor=0.0: joint (fa<=0.1 AND B2>=0.9) C_lo=0.905 C_hi=0.985 width=0.0800 points=17
- B2 lift-off within band (max B2 - floor) = 0.0000  (>0 == not pinned to floor)
- robustness bar: width>=0.01 AND points>=3 AND liftoff>0 -> robust=False
- bf-band non-triviality (verdict input): 2 B_floor points clear GATE_FA -> nontrivial=False (bar >= 3)
- per-B_floor summary (B_floor, C-band_width, points, b2_liftoff, robust, min_fa, clears_gate):
    B_floor=0.00  width=0.0800  points=17  liftoff=0.0000  robust=False  min_fa=0.06666666666666665  clears=True
    B_floor=0.05  width=0.0050  points=2  liftoff=0.0000  robust=False  min_fa=0.09999999999999998  clears=True
    B_floor=0.10  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.19999999999999996  clears=False
    B_floor=0.15  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.2666666666666667  clears=False
    B_floor=0.20  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.30000000000000004  clears=False
    B_floor=0.25  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.30000000000000004  clears=False
    B_floor=0.30  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4  clears=False
    B_floor=0.35  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4  clears=False
    B_floor=0.40  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.43333333333333335  clears=False
    B_floor=0.45  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.50  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.55  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.60  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.65  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.70  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.75  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.80  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.85  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.90  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=0.95  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
    B_floor=1.00  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.4666666666666667  clears=False
- C-sweep at op-point B_floor (C, false-accept, B2, joint_ok):
    C=0.900  fa=0.0667  B2=0.8667  joint=.
    C=0.905  fa=0.0667  B2=0.9000  joint=Y
    C=0.910  fa=0.0667  B2=0.9000  joint=Y
    C=0.915  fa=0.0667  B2=0.9000  joint=Y
    C=0.920  fa=0.0667  B2=0.9000  joint=Y
    C=0.925  fa=0.0667  B2=0.9000  joint=Y
    C=0.930  fa=0.0667  B2=0.9000  joint=Y
    C=0.935  fa=0.0667  B2=0.9000  joint=Y
    C=0.940  fa=0.0667  B2=0.9000  joint=Y
    C=0.945  fa=0.0667  B2=0.9000  joint=Y
    C=0.950  fa=0.0667  B2=0.9000  joint=Y
    C=0.955  fa=0.0667  B2=0.9000  joint=Y
    C=0.960  fa=0.0667  B2=0.9000  joint=Y
    C=0.965  fa=0.0667  B2=0.9000  joint=Y
    C=0.970  fa=0.0667  B2=0.9000  joint=Y
    C=0.975  fa=0.0667  B2=0.9000  joint=Y
    C=0.980  fa=0.0667  B2=0.9000  joint=Y
    C=0.985  fa=0.0667  B2=0.9000  joint=Y
    C=0.990  fa=0.1333  B2=0.9000  joint=.
    C=0.991  fa=0.1333  B2=0.9000  joint=.
    C=0.992  fa=0.1333  B2=0.9000  joint=.
    C=0.993  fa=0.1333  B2=0.9000  joint=.
    C=0.994  fa=0.1667  B2=0.9000  joint=.
    C=0.995  fa=0.1667  B2=0.9000  joint=.
    C=0.996  fa=0.1667  B2=0.9000  joint=.
    C=0.997  fa=0.2000  B2=0.9000  joint=.
    C=0.998  fa=0.2000  B2=0.9000  joint=.
    C=0.999  fa=0.2333  B2=0.9000  joint=.

## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions + accept-arm action at conditioned op-point)
- spoofs total=30 | demoted@op=28 | survived(false-accept)=2
- (a) noauth baseline (demote @ C=+inf)         = 16
- (b) contradiction-veto reject organ           = 12  (demoted because veto fired, accept not rescuing)
- (c) accept/entailment-lift organ              = 4  (GOLD items RESCUED from reject by accept; A toggled +inf->op_A)
- (c-leak) spoofs WRONGLY rescued by accept      = 0  (false-accepts the accept arm introduces; already counted in fa)
- reject_share = (fa_base - fa_op)/fa_base = (0.4667 - 0.0667)/0.4667 = 0.8571
- S3 bar: reject_share > 0.5 -> True  (== organ, not coverage, owns the fa-reduction)

## S1 -- per-class contradiction distribution + knife-edge DRIVER ISOLATION
- gold_backed                  premise=finding : n=74 mean=0.1188 p10=0.0002 p50=0.0023 p90=0.5013
- gold_backed                  premise=source  : n=14 mean=0.3198 p10=0.0018 p50=0.0422 p90=0.8750
- spoof_cuestripped_entitied   premise=finding : n=35 mean=0.6328 p10=0.0049 p50=0.9316 p90=0.9997
- spoof_cuestripped_entitied   premise=source  : n=16 mean=0.5263 p10=0.0057 p50=0.6371 p90=0.9968
- gold-content tail (contradiction>=0.95): n=3 cos_med=0.5081 (the knife-edge drivers)
- spoof-content tail (contradiction>=0.95): n=17 cos_med=0.5338
- S1 expectation (diagnostic): cosine is RETAINED only for the rho guard + this diagnostic; the E35 levers are
  lexical binding B + entailment lift, not cosine (E28 cosine-separability FALSIFIED). gold/spoof cos shown for continuity.
- gold tail drivers (contradiction, cosine, id):
    con=0.9994  cos=0.4801  id=ho_g05
    con=0.9991  cos=0.5081  id=ho_g12
    con=0.9906  cos=0.6003  id=ho_g08
- spoof tail (contradiction, cosine, id) [first 20]:
    con=0.9998  cos=0.5338  id=ho_sn07
    con=0.9998  cos=0.5064  id=ho_sn01
    con=0.9997  cos=0.5661  id=ho_sn05
    con=0.9997  cos=0.5735  id=ho_sn03
    con=0.9997  cos=0.4833  id=ho_sn08
    con=0.9997  cos=0.5304  id=ho_sn10
    con=0.9995  cos=0.5830  id=ho_sn11
    con=0.9994  cos=0.5034  id=ho_sn10
    con=0.9988  cos=0.5472  id=ho_sn10
    con=0.9985  cos=0.5812  id=ho_sn03
    con=0.9984  cos=0.4952  id=ho_sn13
    con=0.9980  cos=0.5501  id=ho_sn10
    con=0.9938  cos=0.4852  id=ho_sn04
    con=0.9914  cos=0.5414  id=ho_sn11
    con=0.9886  cos=0.5112  id=ho_sn05
    con=0.9835  cos=0.5623  id=ho_sn11
    con=0.9785  cos=0.4953  id=ho_sn00

## candidate-level separation at op-point (C=0.90776, B_floor=0.0; counts finding candidates -- DIAGNOSTIC)
- gold-content candidates  : n=74 mean=0.1188 p10=0.0002 p50=0.0023 p90=0.5013 | cross (con>=C; B not paired in diag): 4/74
- spoof-content candidates : n=35 mean=0.6328 p10=0.0049 p50=0.9316 p90=0.9997 | cross (con>=C; B not paired in diag): 19/35
- spoof-vs-gold content p50 separation = 0.9293 (spoof 0.9316 - gold 0.0023)
- S1 expectation: separation > 0.5 -> True (diagnostic only; verdict reads max-based fa, not sep)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).

## VERDICT : TWO_ORGAN_KNIFE_EDGE

decision (PRE_REGISTER_E35.md sec6, the operative forks -- read scope=any fa_op (accept ON) vs reject-only 0.1667 + gate 0.10 + bf-band):
  TWO_ORGAN_LEVER (fa_op <= 0.10 AND B2>=0.90 AND bf-band nontrivial) -> the combined accept+reject organ clears
    the gate -> proceed to robustness sweep + verifier-integration (rho 0.95-vs-0.50 reconcile, full-GOLD scale). TOMMY GO REQUIRED.
  TWO_ORGAN_KNIFE_EDGE (fa_op <= 0.10 but bf-band trivial) -> clears on a single B_floor point (E27-class fragility)
    -> tighten the binding/accept signal or widen the grid before claiming the lever.
  ACCEPT_HELPS_PARTIAL (0.10 < fa_op < 0.1667) -> the accept arm beats reject-only but does NOT clear the gate ->
    directionally right, insufficient -> a third signal or a different binding observable (design, next).
  ENTAILMENT_LIFT_EXHAUSTED (fa_op >= 0.1667) -> no gain over the reject-only ceiling; the per-candidate accept/reject
    organ class is DONE -> pivot to a structurally different verifier (cross-source consistency over the candidate SET).
  VOID_* -> trust gate failed (baseline / rho / B_floor=0!=0.2333 / A=+inf!=0.1667 reject-only / recall) -> reconcile, re-run.

CONFLICT note (R15 / proto 3.10): advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95 (one-sided),
  spearman on (contradiction, cosine). The E35 levers are BINDING (lexical) + ENTAILMENT, NOT cosine -- cosine is
  retained ONLY for this rho guard + S1 diagnostics. Both pass at observed rho. This file keeps the FROZEN 0.95 as
  the VOID trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.
