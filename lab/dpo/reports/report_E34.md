# report_E34 -- reframe reject task: binding-gate veto (scope=any over BOUND subset) vs deberta 0.1667 bar (S1/S2/S3)

- pre-register   : PRE_REGISTER_E34.md (FROZEN md5 91ae26c51ee794fa6f5c94497d109be0) -- sec1/2/4/5/6 operative
- lever          : BINDING GATE -- veto SCOPE=any over BOUND subset iff (P(CON)>=C AND B>=B_floor); B=lexical overlap(claim,premise); premise=source.FINDING / hyp=claim ; MODEL=MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (UNCHANGED)
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## trust gates (else VOID)
- baseline (C=+inf) B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True
- degeneracy (B_floor=0 scope=any) fa=0.23333333333333328 vs deberta anchor 0.1667 +/-0.02 -> ok=False (clean-superset check)
- decorrelation spearman(contradiction,cosine) rho = -0.269 over 139 pairs | VOID-guard rho>=0.95 -> degenerate=False
- advisory: |rho| < 0.5 -> True (REPORTED ONLY; FROZEN substrate VOID-guard is 0.95; see CONFLICT note)
- contradiction_idx read from id2label (single, asserted) ; from_finding=109 asserted > 0

## op-point gate (scope=any; min fa s.t. B2>=0.90 over observed (C,B_floor)). bars: bart 0.0667 (cross-model) / deberta 0.1667 (beat)
- anchor-compare (scope=any): C=0.9914347529411316 B_floor=0.08333333333333333 fa_op=0.16666666666666663 vs bart 0.0667 / deberta 0.1667 -> below_bart=False
- chosen C = 0.9914347529411316 | chosen B_floor (binding gate) = 0.08333333333333333 | B2 at op-point = 0.9
- B1 spoof-demotion = 0.8333333333333334
- false-accept      = 0.16666666666666663  (gate <= 0.1)
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.3003333333333334
- op-point verdict  = FAIL_PARTIAL_VETO

## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=any). delta gates a cosine bound-neighborhood on top of B
    delta=0.00  C=0.0007885394734330475  B_floor=0.15384615384615385  fa=0.23333333333333328  B2=0.9  band_robust=False  reject_share=0.5000000000000001
    delta=0.02  C=0.12710720300674438  B_floor=0.07692307692307693  fa=0.16666666666666663  B2=0.9  band_robust=False  reject_share=0.6428571428571429
    delta=0.05  C=0.9914347529411316  B_floor=0.08333333333333333  fa=0.16666666666666663  B2=0.9  band_robust=False  reject_share=0.6428571428571429
    delta=0.10  C=0.9914347529411316  B_floor=0.08333333333333333  fa=0.16666666666666663  B2=0.9  band_robust=False  reject_share=0.6428571428571429
    delta=0.20  C=0.9914347529411316  B_floor=0.08333333333333333  fa=0.16666666666666663  B2=0.9  band_robust=False  reject_share=0.6428571428571429

## S2 -- (C, B_floor) band / lift-off robustness (band read at op-point B_floor; FROZEN grids)
- band at op-point B_floor=0.08333333333333333: joint (fa<=0.1 AND B2>=0.9) C_lo=None C_hi=None width=0.0000 points=0
- B2 lift-off within band (max B2 - floor) = 0.0000  (>0 == not pinned to floor)
- robustness bar: width>=0.01 AND points>=3 AND liftoff>0 -> robust=False
- bf-band non-triviality (verdict input): 0 B_floor points clear GATE_FA -> nontrivial=False (bar >= 3)
- per-B_floor summary (B_floor, C-band_width, points, b2_liftoff, robust, min_fa, clears_gate):
    B_floor=0.00  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=nan  clears=False
    B_floor=0.05  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=nan  clears=False
    B_floor=0.10  width=0.0000  points=0  liftoff=0.0000  robust=False  min_fa=0.23333333333333328  clears=False
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
    C=0.900  fa=0.1333  B2=0.8333  joint=.
    C=0.905  fa=0.1333  B2=0.8333  joint=.
    C=0.910  fa=0.1333  B2=0.8333  joint=.
    C=0.915  fa=0.1333  B2=0.8333  joint=.
    C=0.920  fa=0.1333  B2=0.8333  joint=.
    C=0.925  fa=0.1333  B2=0.8333  joint=.
    C=0.930  fa=0.1333  B2=0.8333  joint=.
    C=0.935  fa=0.1333  B2=0.8333  joint=.
    C=0.940  fa=0.1333  B2=0.8333  joint=.
    C=0.945  fa=0.1333  B2=0.8667  joint=.
    C=0.950  fa=0.1333  B2=0.8667  joint=.
    C=0.955  fa=0.1333  B2=0.8667  joint=.
    C=0.960  fa=0.1333  B2=0.8667  joint=.
    C=0.965  fa=0.1333  B2=0.8667  joint=.
    C=0.970  fa=0.1333  B2=0.8667  joint=.
    C=0.975  fa=0.1333  B2=0.8667  joint=.
    C=0.980  fa=0.1333  B2=0.8667  joint=.
    C=0.985  fa=0.1333  B2=0.8667  joint=.
    C=0.990  fa=0.1667  B2=0.8667  joint=.
    C=0.991  fa=0.1667  B2=0.9000  joint=.
    C=0.992  fa=0.1667  B2=0.9000  joint=.
    C=0.993  fa=0.1667  B2=0.9000  joint=.
    C=0.994  fa=0.2000  B2=0.9000  joint=.
    C=0.995  fa=0.2000  B2=0.9000  joint=.
    C=0.996  fa=0.2000  B2=0.9000  joint=.
    C=0.997  fa=0.2000  B2=0.9000  joint=.
    C=0.998  fa=0.2000  B2=0.9000  joint=.
    C=0.999  fa=0.2333  B2=0.9000  joint=.

## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions at conditioned op-point)
- spoofs total=30 | demoted@op=25 | survived(false-accept)=5
- (a) noauth baseline (demote @ C=+inf)         = 16
- (b) contradiction-veto reject organ           = 9  (demoted ONLY because veto fired)
- (c) accept/entailment-lift organ              = 0  (NOT wired in standalone probe; verifier-integration step)
- reject_share = (fa_base - fa_op)/fa_base = (0.4667 - 0.1667)/0.4667 = 0.6429
- S3 bar: reject_share > 0.5 -> True  (== veto, not coverage, owns the fa-reduction)

## S1 -- per-class contradiction distribution + knife-edge DRIVER ISOLATION
- gold_backed                  premise=finding : n=74 mean=0.1188 p10=0.0002 p50=0.0023 p90=0.5013
- gold_backed                  premise=source  : n=14 mean=0.3198 p10=0.0018 p50=0.0422 p90=0.8750
- spoof_cuestripped_entitied   premise=finding : n=35 mean=0.6328 p10=0.0049 p50=0.9316 p90=0.9997
- spoof_cuestripped_entitied   premise=source  : n=16 mean=0.5263 p10=0.0057 p50=0.6371 p90=0.9968
- gold-content tail (contradiction>=0.95): n=3 cos_med=0.5081 (the knife-edge drivers)
- spoof-content tail (contradiction>=0.95): n=17 cos_med=0.5338
- S1 expectation (diagnostic): cosine is RETAINED only for the rho guard + this diagnostic; the E34 lever is
  lexical binding B, not cosine (E28 cosine-separability FALSIFIED). gold/spoof cos shown for continuity.
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

## candidate-level separation at op-point (C=0.99143, B_floor=0.08333333333333333; counts finding candidates -- DIAGNOSTIC)
- gold-content candidates  : n=74 mean=0.1188 p10=0.0002 p50=0.0023 p90=0.5013 | cross (con>=C; B not paired in diag): 2/74
- spoof-content candidates : n=35 mean=0.6328 p10=0.0049 p50=0.9316 p90=0.9997 | cross (con>=C; B not paired in diag): 14/35
- spoof-vs-gold content p50 separation = 0.9293 (spoof 0.9316 - gold 0.0023)
- S1 expectation: separation > 0.5 -> True (diagnostic only; verdict reads max-based fa, not sep)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).

## VERDICT : VOID_DEGENERACY

decision (PRE_REGISTER_E34.md sec6, the operative forks -- read scope=any fa_op vs deberta bar 0.1667 + gate 0.10):
  BINDING_IS_THE_LEVER (fa_op <= 0.10 AND B2>=0.90 AND bf-band nontrivial) -> the reject-task reframe WORKS;
    the binding gate fixes the E29 retrieval-misbinding defect -> proceed to robustness sweep + verifier-
    integration (rho 0.95-vs-0.50 reconcile, entailment-lift -> S3 three-way, full-GOLD scale). TOMMY GO REQUIRED.
  BINDING_KNIFE_EDGE (fa_op <= 0.10 but bf-band trivial) -> clears the gate on a single B_floor point (E27-class
    fragility) -> tighten the binding signal / widen the grid before claiming the lever.
  BINDING_HELPS_PARTIAL (0.10 < fa_op < 0.1667) -> binding beats deberta-plain but does NOT clear the gate ->
    directionally right, insufficient alone -> combine with a second organ (design, next).
  BINDING_NOT_THE_LEVER (fa_op >= 0.1667) -> no gain over E33; the per-candidate contradiction-veto organ is
    EXHAUSTED even reframed -> escalate to a DIFFERENT reject/accept organ class (accept/entailment-lift three-way).
  VOID_* -> trust gate failed (baseline mismatch / rho degenerate / recall unusable / B_floor=0 != 0.1667) -> reconcile, re-run.

CONFLICT note (R15 / proto 3.10): advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95 (one-sided),
  spearman on (contradiction, cosine). The E34 lever is BINDING (lexical), NOT cosine -- cosine is retained ONLY
  for this rho guard + S1 diagnostics. Both pass at observed rho. This file keeps the FROZEN 0.95 as the VOID
  trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.
