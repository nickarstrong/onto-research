# report_E27 -- contradiction-veto reject organ: full gate + robustness sweep (S1/S2/S3)

- pre-register   : PRE_REGISTER_E27.md (FROZEN md5 20dde8b3f6d54b9417ea1007a12210d4) -- sec2/3/5/6 operative
- lever          : facebook/bart-large-mnli -- P(CONTRADICTION), premise=source.FINDING (fallback source) / hypothesis=claim
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## trust gates (else VOID)
- baseline (C=+inf) B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True
- decorrelation spearman(contradiction,cosine) rho = -0.237 over 139 pairs | VOID-guard rho>=0.95 -> degenerate=False
- advisory (PRE_REGISTER sec4): |rho| < 0.5 -> True (REPORTED ONLY; FROZEN substrate VOID-guard is 0.95; see CONFLICT note)
- contradiction_idx read from id2label (single, asserted) ; from_finding=109 asserted > 0

## op-point gate (FROZEN E26 rule: iso-recall LOWEST observed-C with B2>=0.90 ; reproduces E26 = regression check)
- chosen C = 0.9949175119400024 | B2 at op-point = 0.9
- B1 spoof-demotion = 0.9333333333333333
- false-accept      = 0.06666666666666665  (gate <= 0.1)
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.4003333333333334
- op-point verdict  = PASS

## S2 -- C-sweep / lift-off robustness (PRIMARY E27 question; FROZEN fixed grid)
- joint (fa<=0.1 AND B2>=0.9) band: C_lo=0.995 C_hi=0.995 width=0.0000 points=1
- B2 lift-off within band (max B2 - floor) = 0.0000  (>0 == not pinned to floor)
- robustness bar: width>=0.01 AND points>=3 AND liftoff>0 -> robust=False
- sweep (C, false-accept, B2, joint_ok):
    C=0.900  fa=0.0333  B2=0.6333  joint=.
    C=0.905  fa=0.0333  B2=0.6333  joint=.
    C=0.910  fa=0.0333  B2=0.6333  joint=.
    C=0.915  fa=0.0333  B2=0.6333  joint=.
    C=0.920  fa=0.0333  B2=0.6333  joint=.
    C=0.925  fa=0.0333  B2=0.6333  joint=.
    C=0.930  fa=0.0333  B2=0.6333  joint=.
    C=0.935  fa=0.0333  B2=0.6333  joint=.
    C=0.940  fa=0.0333  B2=0.6333  joint=.
    C=0.945  fa=0.0333  B2=0.6333  joint=.
    C=0.950  fa=0.0333  B2=0.6333  joint=.
    C=0.955  fa=0.0333  B2=0.6667  joint=.
    C=0.960  fa=0.0333  B2=0.6667  joint=.
    C=0.965  fa=0.0333  B2=0.6667  joint=.
    C=0.970  fa=0.0333  B2=0.6667  joint=.
    C=0.975  fa=0.0333  B2=0.6667  joint=.
    C=0.980  fa=0.0333  B2=0.7000  joint=.
    C=0.985  fa=0.0333  B2=0.8000  joint=.
    C=0.990  fa=0.0333  B2=0.8000  joint=.
    C=0.991  fa=0.0333  B2=0.8000  joint=.
    C=0.992  fa=0.0667  B2=0.8333  joint=.
    C=0.993  fa=0.0667  B2=0.8333  joint=.
    C=0.994  fa=0.0667  B2=0.8667  joint=.
    C=0.995  fa=0.0667  B2=0.9000  joint=Y
    C=0.996  fa=0.1667  B2=0.9000  joint=.
    C=0.997  fa=0.1667  B2=0.9000  joint=.
    C=0.998  fa=0.2000  B2=0.9000  joint=.
    C=0.999  fa=0.2333  B2=0.9333  joint=.

## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions at op-point)
- spoofs total=30 | demoted@op=28 | survived(false-accept)=2
- (a) noauth baseline (demote @ C=+inf)         = 16
- (b) contradiction-veto reject organ           = 12  (demoted ONLY because veto fired)
- (c) accept/entailment-lift organ              = 0  (NOT wired in standalone probe; verifier-integration step)
- reject_share = (fa_base - fa_op)/fa_base = (0.4667 - 0.0667)/0.4667 = 0.8571
- S3 bar: reject_share > 0.5 -> True  (== veto, not coverage, owns the fa-reduction)

## S1 -- per-class contradiction distribution (formalized E26 diagnostic)
- gold_backed                  premise=finding : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793
- gold_backed                  premise=source  : n=14 mean=0.3259 p10=0.0110 p50=0.1098 p90=0.9096
- spoof_cuestripped_entitied   premise=finding : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998
- spoof_cuestripped_entitied   premise=source  : n=16 mean=0.7737 p10=0.1500 p50=0.9889 p90=0.9984

## contradiction separation (chosen_C=0.99492; veto when contradiction >= C)
- gold-content  (want LOW)  : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793 | vetoed(>=C, false): 1/74
- spoof-content (want HIGH) : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998 | vetoed(>=C, true): 14/35
- spoof-vs-gold content p50 separation = 0.9532 (spoof 0.9909 - gold 0.0377)
- S1 expectation: separation > 0.5 -> True (diagnostic only; verdict reads max-based fa, not sep)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).

## VERDICT : PASS_KNIFE_EDGE

decision (PRE_REGISTER_E27.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate):
  PASS_ROBUST (op fa<=0.10 reproduced AND S2 band width>=0.01/>=3pts/B2 lifts off AND S3 reject_share>0.50)
    -> reject organ ROBUST -> graduate into the verifier (verify_E16 integration; TOMMY GO REQUIRED, frozen
       substrate is edited) + per-class secondaries.
  PASS_KNIFE_EDGE (op fa<=0.10 but band knife-edge: single C / B2 pinned to floor) -> NOT robust -> tune
    premise quality / per-class C, ONE more readout, NO new data.
  PASS_MISATTRIBUTED (band robust but reject_share<=0.50) -> gain not owned by the reject organ -> tune.
  REGRESSION (op fa>0.10 on re-run) -> E26 single readout did not reproduce -> reconcile before anything.
  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.

CONFLICT note (R15 / proto 3.10): PRE_REGISTER_E27 sec4 froze advisory |rho|<0.50; the REUSED frozen E26
  substrate VOID-guard is rho>=0.95 (one-sided). Both pass at observed rho=-0.237 (no functional delta this
  run). This file keeps the FROZEN 0.95 as the VOID trigger (does not fork frozen behavior) and reports the
  0.50 advisory separately. Reconcile the bar at verifier-integration; do NOT silently edit the pre-register.
