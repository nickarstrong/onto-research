# report_E28 -- observable-conditioned contradiction-veto: (C x cosine-gate K) knife-edge tune (S1/S2/S3)

- pre-register   : PRE_REGISTER_E28.md (FROZEN md5 f3fab7581d1c15e7b58926da82d01dc3) -- sec2/3/5/6 operative
- lever          : facebook/bart-large-mnli -- veto iff (P(CONTRADICTION)>=C AND binding_cosine<=K); premise=source.FINDING / hyp=claim
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## trust gates (else VOID)
- baseline (C=+inf) B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True
- decorrelation spearman(contradiction,cosine) rho = -0.237 over 139 pairs | VOID-guard rho>=0.95 -> degenerate=False
- advisory (PRE_REGISTER sec4): |rho| < 0.5 -> True (REPORTED ONLY; FROZEN substrate VOID-guard is 0.95; see CONFLICT note)
- contradiction_idx read from id2label (single, asserted) ; from_finding=109 asserted > 0

## op-point gate (conditioned; min fa s.t. B2>=0.90 over observed (C,K); K=+inf reduces to E27 scalar)
- regression anchor (K=+inf): C=0.9949175119400024 fa=0.06666666666666665 reproduces_E27(fa<=0.1)=True
- chosen C = 0.9938673377037048 | chosen K (cosine gate) = 0.651951789855957 | B2 at op-point = 0.9
- B1 spoof-demotion = 0.9333333333333333
- false-accept      = 0.06666666666666665  (gate <= 0.1)
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.4003333333333334
- op-point verdict  = PASS

## S2 -- (C,K) band / lift-off robustness (PRIMARY E28 question; band read at the op-point K; FROZEN grids)
- band at op-point K=0.651951789855957: joint (fa<=0.1 AND B2>=0.9) C_lo=0.994 C_hi=0.995 width=0.0010 points=2
- B2 lift-off within band (max B2 - floor) = 0.0000  (>0 == not pinned to floor)
- robustness bar: width>=0.01 AND points>=3 AND liftoff>0 -> robust=False
- per-K joint C-band summary (K, band_width, points, b2_liftoff, robust); K=inf = E27 scalar anchor:
    K= 0.45  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.50  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.55  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 0.60  width=0.0010  points=2  liftoff=0.0000  robust=False
    K= 0.65  width=0.0010  points=2  liftoff=0.0000  robust=False
    K= 0.70  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 0.75  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 0.80  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 0.85  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 0.90  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 0.95  width=0.0000  points=1  liftoff=0.0000  robust=False
    K= 1.00  width=0.0000  points=1  liftoff=0.0000  robust=False
    K=  inf  width=0.0000  points=1  liftoff=0.0000  robust=False
- C-sweep at op-point K (C, false-accept, B2, joint_ok):
    C=0.900  fa=0.0333  B2=0.6667  joint=.
    C=0.905  fa=0.0333  B2=0.6667  joint=.
    C=0.910  fa=0.0333  B2=0.6667  joint=.
    C=0.915  fa=0.0333  B2=0.6667  joint=.
    C=0.920  fa=0.0333  B2=0.6667  joint=.
    C=0.925  fa=0.0333  B2=0.6667  joint=.
    C=0.930  fa=0.0333  B2=0.6667  joint=.
    C=0.935  fa=0.0333  B2=0.6667  joint=.
    C=0.940  fa=0.0333  B2=0.6667  joint=.
    C=0.945  fa=0.0333  B2=0.6667  joint=.
    C=0.950  fa=0.0333  B2=0.6667  joint=.
    C=0.955  fa=0.0333  B2=0.7000  joint=.
    C=0.960  fa=0.0333  B2=0.7000  joint=.
    C=0.965  fa=0.0333  B2=0.7000  joint=.
    C=0.970  fa=0.0333  B2=0.7000  joint=.
    C=0.975  fa=0.0333  B2=0.7000  joint=.
    C=0.980  fa=0.0333  B2=0.7333  joint=.
    C=0.985  fa=0.0333  B2=0.8333  joint=.
    C=0.990  fa=0.0333  B2=0.8333  joint=.
    C=0.991  fa=0.0333  B2=0.8333  joint=.
    C=0.992  fa=0.0667  B2=0.8667  joint=.
    C=0.993  fa=0.0667  B2=0.8667  joint=.
    C=0.994  fa=0.0667  B2=0.9000  joint=Y
    C=0.995  fa=0.0667  B2=0.9000  joint=Y
    C=0.996  fa=0.1667  B2=0.9000  joint=.
    C=0.997  fa=0.1667  B2=0.9000  joint=.
    C=0.998  fa=0.2000  B2=0.9000  joint=.
    C=0.999  fa=0.2333  B2=0.9333  joint=.

## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions at conditioned op-point)
- spoofs total=30 | demoted@op=28 | survived(false-accept)=2
- (a) noauth baseline (demote @ C=+inf)         = 16
- (b) contradiction-veto reject organ           = 12  (demoted ONLY because veto fired)
- (c) accept/entailment-lift organ              = 0  (NOT wired in standalone probe; verifier-integration step)
- reject_share = (fa_base - fa_op)/fa_base = (0.4667 - 0.0667)/0.4667 = 0.8571
- S3 bar: reject_share > 0.5 -> True  (== veto, not coverage, owns the fa-reduction)

## S1 -- per-class contradiction distribution + knife-edge DRIVER ISOLATION
- gold_backed                  premise=finding : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793
- gold_backed                  premise=source  : n=14 mean=0.3259 p10=0.0110 p50=0.1098 p90=0.9096
- spoof_cuestripped_entitied   premise=finding : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998
- spoof_cuestripped_entitied   premise=source  : n=16 mean=0.7737 p10=0.1500 p50=0.9889 p90=0.9984
- gold-content tail (contradiction>=0.95): n=10 cos_med=0.4855 (the knife-edge drivers)
- spoof-content tail (contradiction>=0.95): n=21 cos_med=0.5112
- S1 expectation (diagnostic): gold tail-items sit at HIGHER cosine than spoof tail-items (the gap the K-gate exploits).
- gold tail drivers (contradiction, cosine, id):
    con=0.9983  cos=0.4801  id=ho_g05
    con=0.9948  cos=0.6520  id=ho_g17
    con=0.9932  cos=0.5081  id=ho_g12
    con=0.9929  cos=0.4656  id=ho_g05
    con=0.9911  cos=0.4909  id=ho_g10
    con=0.9840  cos=0.6003  id=ho_g08
    con=0.9827  cos=0.5900  id=ho_g23
    con=0.9804  cos=0.4585  id=ho_g26
    con=0.9767  cos=0.4733  id=ho_g13
    con=0.9696  cos=0.4610  id=ho_g10
- spoof tail (contradiction, cosine, id) [first 20]:
    con=0.9999  cos=0.5338  id=ho_sn07
    con=0.9999  cos=0.5304  id=ho_sn10
    con=0.9998  cos=0.5830  id=ho_sn11
    con=0.9998  cos=0.5661  id=ho_sn05
    con=0.9998  cos=0.5064  id=ho_sn01
    con=0.9991  cos=0.4952  id=ho_sn13
    con=0.9985  cos=0.5252  id=ho_sn06
    con=0.9976  cos=0.4564  id=ho_sn00
    con=0.9975  cos=0.5623  id=ho_sn11
    con=0.9974  cos=0.5472  id=ho_sn10
    con=0.9964  cos=0.5812  id=ho_sn03
    con=0.9952  cos=0.5735  id=ho_sn03
    con=0.9951  cos=0.4833  id=ho_sn08
    con=0.9951  cos=0.4852  id=ho_sn04
    con=0.9947  cos=0.5034  id=ho_sn10
    con=0.9945  cos=0.5112  id=ho_sn05
    con=0.9924  cos=0.4953  id=ho_sn00
    con=0.9909  cos=0.4553  id=ho_sn04
    con=0.9904  cos=0.4746  id=ho_sn02
    con=0.9902  cos=0.5501  id=ho_sn10

## conditioned separation at op-point (C=0.99387, K=0.651951789855957; veto iff contradiction>=C AND cos<=K)
- gold-content  (want NOT vetoed) : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793 | falsely vetoed: 1/74
- spoof-content (want vetoed)     : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998 | correctly vetoed: 16/35
- spoof-vs-gold content p50 separation = 0.9532 (spoof 0.9909 - gold 0.0377)
- S1 expectation: separation > 0.5 -> True (diagnostic only; verdict reads max-based fa, not sep)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).

## VERDICT : PASS_KNIFE_EDGE

decision (PRE_REGISTER_E28.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate):
  PASS_ROBUST (conditioned band robust: width>=0.01/>=3pts/B2 lifts off at op-K AND S3 reject_share>0.50)
    -> reject organ ROBUST under observable conditioning -> graduate the (contradiction x cosine) veto into
       the verifier (verify_E16 integration; TOMMY GO REQUIRED, frozen substrate edited). At integration:
       reconcile rho guard (0.95 vs 0.50) into one bar; wire (c) entailment-lift -> S3 three-way.
  PASS_KNIFE_EDGE (cosine gate does NOT open the band: single point / B2 pinned) -> tail overlap NOT
    cosine-separable -> premise quality is the binding constraint -> E29 targeted re-author of the S1 tail
    drivers with a FRESH fixture freeze (NEW data, separate session). No verifier integration.
  PASS_MISATTRIBUTED (band robust but reject_share<=0.50) -> gain not owned by the reject organ -> tune.
  REGRESSION (K=+inf does not reproduce E27 scalar op, OR conditioned op fa>0.10) -> reconcile before anything.
  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.

CONFLICT note (R15 / proto 3.10): PRE_REGISTER advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95
  (one-sided). The lever now USES cosine, so low |rho| is required for the conditioning to add signal (not be
  redundant with contradiction). Both pass at observed rho (E27 -0.237). This file keeps the FROZEN 0.95 as the
  VOID trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.
