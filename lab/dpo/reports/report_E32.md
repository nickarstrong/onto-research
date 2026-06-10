# report_E32 -- model-class escalation: NLI cross-encoder SWAP (scope=any fixed) vs bart 0.0667 bar (S1/S2/S3)

- pre-register   : PRE_REGISTER_E32.md (FROZEN md5 e25b801f3b6eb8ced194f47d4c488c66) -- sec1/2/3/5 operative
- lever          : MODEL SWAP -> MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli -- veto SCOPE=any (E30 proven-best) iff (P(CON)>=C AND cos<=K); premise=source.FINDING / hyp=claim
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## trust gates (else VOID)
- baseline (C=+inf) B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True
- decorrelation spearman(contradiction,cosine) rho = -0.269 over 139 pairs | VOID-guard rho>=0.95 -> degenerate=False
- advisory (PRE_REGISTER sec4): |rho| < 0.5 -> True (REPORTED ONLY; FROZEN substrate VOID-guard is 0.95; see CONFLICT note)
- contradiction_idx read from id2label (single, asserted) ; from_finding=109 asserted > 0

## op-point gate (scope=any; min fa_new s.t. B2>=0.90 over observed (C,K)). 0.0667 = bart COMPARISON bar (not regression)
- anchor-compare (scope=any): C=0.978492021560669 K=0.5066235661506653 fa_new=0.16666666666666663 vs bar E28_OP_FA=0.0667 -> below_bar=False
- chosen C = 0.978492021560669 | chosen K (cosine gate) = 0.5066235661506653 | B2 at op-point = 0.9
- B1 spoof-demotion = 0.8333333333333334
- false-accept      = 0.16666666666666663  (gate <= 0.1)
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.3003333333333334
- op-point verdict  = FAIL_PARTIAL_VETO

## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=top1). delta=+inf == any (anchor); delta=0 ~ top1
    delta=0.00  C=0.9077622294425964  K=0.8251297473907471  fa=0.2666666666666667  B2=0.9  band_robust=False  reject_share=0.4285714285714285
    delta=0.02  C=0.9077622294425964  K=0.8251297473907471  fa=0.23333333333333328  B2=0.9  band_robust=False  reject_share=0.5000000000000001
    delta=0.05  C=0.963958203792572  K=0.5999017953872681  fa=0.1333333333333333  B2=0.9  band_robust=False  reject_share=0.7142857142857143
    delta=0.10  C=0.978492021560669  K=0.5066235661506653  fa=0.19999999999999996  B2=0.9  band_robust=False  reject_share=0.5714285714285715
    delta=0.20  C=0.978492021560669  K=0.5066235661506653  fa=0.16666666666666663  B2=0.9  band_robust=False  reject_share=0.6428571428571429

## S2 -- (C,K) band / lift-off robustness (PRIMARY E30 question at scope=top1; band read at op-point K; FROZEN grids)
- band at op-point K=0.5066235661506653: joint (fa<=0.1 AND B2>=0.9) C_lo=None C_hi=None width=0.0000 points=0
- B2 lift-off within band (max B2 - floor) = 0.0000  (>0 == not pinned to floor)
- robustness bar: width>=0.01 AND points>=3 AND liftoff>0 -> robust=False
- per-K joint C-band summary (K, band_width, points, b2_liftoff, robust); K=inf = E27 scalar anchor:
    K= 0.45  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.50  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.55  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.60  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.65  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.70  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.75  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.80  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.85  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.90  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 0.95  width=0.0000  points=0  liftoff=0.0000  robust=False
    K= 1.00  width=0.0000  points=0  liftoff=0.0000  robust=False
    K=  inf  width=0.0000  points=0  liftoff=0.0000  robust=False
- C-sweep at op-point K (C, false-accept, B2, joint_ok):
    C=0.900  fa=0.1667  B2=0.8667  joint=.
    C=0.905  fa=0.1667  B2=0.8667  joint=.
    C=0.910  fa=0.1667  B2=0.8667  joint=.
    C=0.915  fa=0.1667  B2=0.8667  joint=.
    C=0.920  fa=0.1667  B2=0.8667  joint=.
    C=0.925  fa=0.1667  B2=0.8667  joint=.
    C=0.930  fa=0.1667  B2=0.8667  joint=.
    C=0.935  fa=0.1667  B2=0.8667  joint=.
    C=0.940  fa=0.1667  B2=0.8667  joint=.
    C=0.945  fa=0.1667  B2=0.8667  joint=.
    C=0.950  fa=0.1667  B2=0.8667  joint=.
    C=0.955  fa=0.1667  B2=0.8667  joint=.
    C=0.960  fa=0.1667  B2=0.8667  joint=.
    C=0.965  fa=0.1667  B2=0.9000  joint=.
    C=0.970  fa=0.1667  B2=0.9000  joint=.
    C=0.975  fa=0.1667  B2=0.9000  joint=.
    C=0.980  fa=0.1667  B2=0.9000  joint=.
    C=0.985  fa=0.1667  B2=0.9000  joint=.
    C=0.990  fa=0.2333  B2=0.9000  joint=.
    C=0.991  fa=0.2333  B2=0.9000  joint=.
    C=0.992  fa=0.2333  B2=0.9000  joint=.
    C=0.993  fa=0.2333  B2=0.9000  joint=.
    C=0.994  fa=0.2667  B2=0.9000  joint=.
    C=0.995  fa=0.2667  B2=0.9000  joint=.
    C=0.996  fa=0.2667  B2=0.9000  joint=.
    C=0.997  fa=0.3000  B2=0.9000  joint=.
    C=0.998  fa=0.3000  B2=0.9000  joint=.
    C=0.999  fa=0.3333  B2=0.9000  joint=.

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
- S1 expectation (diagnostic): gold tail-items sit at HIGHER cosine than spoof tail-items (the gap the K-gate exploits).
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

## candidate-level separation at op-point (C=0.97849, K=0.5066235661506653; counts ALL finding candidates crossing -- DIAGNOSTIC, not the top1 item-veto)
- gold-content candidates  : n=74 mean=0.1188 p10=0.0002 p50=0.0023 p90=0.5013 | cross (con>=C AND cos<=K): 1/74
- spoof-content candidates : n=35 mean=0.6328 p10=0.0049 p50=0.9316 p90=0.9997 | cross (con>=C AND cos<=K): 6/35
- spoof-vs-gold content p50 separation = 0.9293 (spoof 0.9316 - gold 0.0023)
- S1 expectation: separation > 0.5 -> True (diagnostic only; verdict reads max-based fa, not sep)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).

## VERDICT : CEILING_NOT_MODEL_SCALE

decision (PRE_REGISTER_E32.md sec5, the operative forks -- read scope=any fa_new vs bart bar 0.0667):
  ESCALATION_CONFIRMED (fa_new < 0.0667 strict AND B2>=0.90) -> model discriminative scale WAS the ceiling ->
    E33 graduates to a robustness sweep + the verifier-integration question (rho guard 0.95-vs-0.50 reconcile,
    entailment-lift -> S3 three-way, full-GOLD scale). TOMMY GO REQUIRED before integration.
  MODEL_HELPS_PARTIAL (0.0667 <= fa_new <= 0.10 AND B2>=0.90) -> bigger model helps but does NOT clear E28 ->
    decide deeper model class vs task reformulation at the E33 readout.
  CEILING_NOT_MODEL_SCALE (fa_new > 0.10) -> the ceiling is task/data, not model scale -> the contradiction-veto
    task itself is the constraint -> EXIT the NLI-swap family and reframe the reject task.
  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable=fa unreadable) -> reconcile, re-run.

CONFLICT note (R15 / proto 3.10): PRE_REGISTER advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95
  (one-sided). The lever now USES cosine, so low |rho| is required for the conditioning to add signal (not be
  redundant with contradiction). Both pass at observed rho (E27 -0.237). This file keeps the FROZEN 0.95 as the
  VOID trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.

## diff-proof (E32_vs_E30 -- copied probe; declared zones: scope/CE_MODEL/anchor-repurpose/verdict-forks/--out/comments)
```diff
--- _base_run_E30.py	2026-06-10 13:19:01.701699975 +0000
+++ run_E32_probe.py	2026-06-10 13:18:31.484339896 +0000
@@ -19,20 +19,21 @@
 import torch
 from transformers import AutoTokenizer, AutoModelForSequenceClassification
 
-# E30 = BINDING-DISCIPLINE veto: candidate-SCOPE lever (TOP1 vs ANY). PRE_REGISTER_E30.md (FROZEN,
-#   md5 609e9b41db440aba9e78cc32affa4dee). E29 REVERSAL (report_E29_reauthor.md md5 c1f38de7769eda990d20ee68404480c1):
-#   the E27/E28 knife-edge is RETRIEVAL MISBINDING under an ANY-CANDIDATE veto, NOT a premise-phrasing defect and
-#   NOT cosine-separable. A gold claim retrieves its true entailing support AND a topically-near WRONG-SOURCE
-#   record; the wrong-source record faithfully contradicts the claim, so `any-candidate` veto (run_E28 line 153)
-#   falsely vetoes the gold claim -> pins B2 to the 0.90 floor -> the op-point cannot lower C to catch more spoof.
-#   LEVER (E30): restrict the veto's CANDIDATE SCOPE. scope='top1' = veto considers ONLY r[1][0] (highest-cosine
-#   authorized candidate = the bound support); 'any' = run_E28 line 153 verbatim (REGRESSION ANCHOR); 'margin'
-#   (delta) = bound-neighborhood (robustness arm). A candidate vetoes iff (contradiction >= C AND cosine <= K);
-#   K carried from E28 (K=+inf disables the gate). SCOPE is observable (cosine/rank, no true-class) -> oracle-safe.
-#   SAME frozen gate (fa<=0.10) + SAME grids + SAME trust gates as run_E28. ADDS: scope param + scope='any'
-#   regression-anchor reproducing E28 op fa 0.0667 + margin sweep. ONE line of veto logic differs from run_E28.
-#   Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26/E27/E28) untouched; scope folded HERE.
-CE_MODEL = os.environ.get("ONTO_CE_MODEL", "facebook/bart-large-mnli")   # model-scale NLI; override via env
+# E32 = MODEL-CLASS ESCALATION: NLI cross-encoder SWAP is the lever. PRE_REGISTER_E32.md (FROZEN,
+#   md5 e25b801f3b6eb8ced194f47d4c488c66). E31 (report_E30.md, VERDICT FAIL_NOT_THE_DRIVER) proved candidate-SCOPE
+#   is NOT the lever: top1 LOSES the spoof rejections living in non-top1 candidates (fa monotone 0.0667->0.2333);
+#   bart-large-mnli is therefore the PROVEN ceiling. The only remaining in-family lever is NLI discriminative CLASS.
+#   LEVER (E32): swap the cross-encoder bart-large-mnli -> a stronger ANLI-hardened head (default below), holding
+#   the veto geometry FIXED at scope='any' (E30 proven-best). A candidate vetoes iff (contradiction >= C AND
+#   cosine <= K); K carried from E28 (K=+inf disables the gate). The MODEL is the ONLY new variable; nothing held-out
+#   conditions on it -> oracle-clean. SAME gate (fa<=0.10) + SAME grids + SAME trust gates + SAME substrate as run_E30.
+#   ANCHOR REPURPOSE: under a NEW model fa is NOT expected to reproduce bart's 0.0667 -- 0.0667 is the bart-specific
+#   COMPARISON BAR fa_new is read against (sec5 forks), NOT a regression gate. No REGRESSION verdict at E32.
+#   Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26/E27/E28, scope logic) untouched.
+#   ESCALATION is discriminative CLASS not param count: deberta-v3-large (~304M) < bart-large-mnli (~407M); the lift
+#   is DeBERTa-v3 (RTD + disentangled attn) + ANLI/WANLI adversarial training. ANLI-hardened head not clearing 0.0667
+#   => CEILING_NOT_MODEL_SCALE (task, not model, is the constraint) -- this SHARPENS falsifiability.
+CE_MODEL = os.environ.get("ONTO_CE_MODEL", "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")   # ANLI-hardened NLI; override via env
 E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
 GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
 PARTIAL_BAND = 0.20           # 0.10 < fa < 0.20 = PARTIAL ; fa >= 0.20 = plateau (contradiction insufficient)
@@ -56,14 +57,14 @@
 K_GRID = sorted(set([round(0.45 + 0.05 * i, 2) for i in range(0, 12)]))  # 0.45 .. 1.00
 S1_TAIL_CON = 0.95            # S1 driver isolation: gold-content items with contradiction >= this
 
-# --- E30 candidate-SCOPE lever (FROZEN pre-data, PRE_REGISTER_E30.md sec1-2) -------------------------------
-#   scope='top1' (PRIMARY) = veto considers ONLY r[1][0] (bound support). scope='any' = run_E28 line 153
-#   (REGRESSION ANCHOR). scope=('margin',delta) = bound-neighborhood (robustness arm; reported, not the verdict).
-PRIMARY_SCOPE = "top1"
-ANCHOR_SCOPE  = "any"
+# --- E32 veto geometry (FROZEN pre-data, PRE_REGISTER_E32.md sec3) -----------------------------------------
+#   scope='any' (PRIMARY at E32) = E30 proven-best veto geometry (E31: top1 LOST non-top1 spoof rejections).
+#   The model is the lever; the geometry is held fixed. scope=('margin',delta) robustness arm = reported only.
+PRIMARY_SCOPE = "any"
+ANCHOR_SCOPE  = "any"        # == PRIMARY_SCOPE at E32; anchor-compare prints fa_new vs the bart bar
 MARGIN_GRID = [0.00, 0.02, 0.05, 0.10, 0.20]   # delta grid for the reported robustness arm
-E28_OP_FA   = 0.0667         # E28 operating-point false-accept; scope='any' MUST reproduce this (regression)
-ANCHOR_TOL  = 1e-3           # reproduction tolerance (< one spoof-item granularity ~0.0667)
+E28_OP_FA   = 0.0667         # bart-SPECIFIC COMPARISON BAR (sec5 forks); NOT a reproduce-assert at E32
+ANCHOR_TOL  = 1e-3           # carried (unused as a gate at E32; kept for byte-stability of the constants block)
 
 _ce_tok = _ce_model = _con_idx = None
 def _ce_load():
@@ -254,7 +255,7 @@
     ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
     ap.add_argument("--fixture_md5", default="4a45f52883a802e8d8d1d5ff5d185bdb")
     ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
-    ap.add_argument("--out", default="reports/report_E30.md")   # NEVER a frozen-report path (no clobber E28/E27)
+    ap.add_argument("--out", default="reports/report_E32.md")   # NEVER a frozen-report path (no clobber E30/E28/E27)
     a = ap.parse_args()
 
     fm, hm = md5(a.fixture), md5(a.heldout)
@@ -328,12 +329,13 @@
         _b1, b2_, _b3, _ = metrics_at_C(items_pre, c_, k_, scope)
         return float(c_), float(k_), float(b2_), float(min_fa)
 
-    # REGRESSION ANCHOR (E30 sec3-T6): scope='any' == run_E28 line 153. Re-selecting the op-point under 'any'
-    # MUST reproduce the E28 operating point (false-accept 0.0667). Mismatch => REGRESSION (machinery broke).
-    anc_C, anc_K, anc_B2, anc_fa = select_op(ANCHOR_SCOPE)
-    reg_reproduces = (anc_C is not None) and (not np.isnan(anc_fa)) and (abs(anc_fa - E28_OP_FA) <= ANCHOR_TOL)
-    print(f"[regression-anchor scope=any] C={anc_C} K={anc_K} fa={anc_fa} "
-          f"reproduces_E28({E28_OP_FA}+/-{ANCHOR_TOL})={reg_reproduces}")
+    # E32 ANCHOR-COMPARE (repurposed): scope='any' IS the primary veto geometry here (E30 proven-best). Under a
+    # NEW model fa is NOT expected to reproduce 0.0667 -- the 0.0667 anchor is the bart-specific COMPARISON BAR
+    # that fa_new is read against (sec5 forks), NOT a regression gate. No REGRESSION verdict at E32.
+    anc_C, anc_K, anc_B2, anc_fa = select_op(ANCHOR_SCOPE)   # ANCHOR_SCOPE == PRIMARY_SCOPE == 'any' at E32
+    anchor_below_bar = (anc_C is not None) and (not np.isnan(anc_fa)) and (anc_fa < E28_OP_FA)
+    print(f"[anchor-compare scope=any] C={anc_C} K={anc_K} fa_new={anc_fa} "
+          f"vs bar E28_OP_FA={E28_OP_FA} -> below_bar={anchor_below_bar}")
 
     # E30 PRIMARY op-point: scope='top1' (veto considers ONLY the bound support r[1][0]).
     chosen_C, chosen_K, chosen_B2, _min_fa = select_op(PRIMARY_SCOPE)
@@ -368,19 +370,18 @@
                   dict(reject_share=float("nan"))
             margin_rows.append((delta, mC, mK, mfa, mB2, mband["robust"], ms3["reject_share"]))
 
-    # ---- E30 verdict (PRE_REGISTER_E30.md sec6, the ONLY operative fork; reads scope=top1) -------------------
+    # ---- E32 verdict (PRE_REGISTER_E32.md sec5; reads scope=any fa_new vs bar 0.0667 + B2>=0.90) -------------
+    # baseline-sanity + degenerate = model-INDEPENDENT VOID guards. chosen_C None = no (C,K) holds B2>=0.90 ->
+    # fa unreadable -> VOID (not a clean CEILING). The 3 escalation forks read fa (primary scope=any under the NEW
+    # model); B2>=0.90 is GUARANTEED by select_op feasibility (RECALL_FLOOR). S3 reject_share + band robustness are
+    # DIAGNOSTIC here (deferred to the E33 robustness sweep), NOT verdict gates. 0.0667 = bart COMPARISON bar.
     s3rej = s3["reject_share"]
-    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"
-    elif degenerate:                verdict = "VOID_DEGENERATE_LEVER"
-    elif not reg_reproduces:        verdict = "REGRESSION"             # scope=any did NOT reproduce E28 op fa 0.0667
-    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"   # TOP1 veto destroys gold recall (no op-point)
-    elif fa > GATE_FA:              verdict = "FAIL_NOT_THE_DRIVER"    # TOP1 breaches the frozen gate
-    elif np.isnan(s3rej) or s3rej <= S3_REJECT_SHARE_BAR:
-        verdict = "FAIL_NOT_THE_DRIVER"                               # spoof rejection collapsed (needed non-top1)
-    elif (fa < anc_fa) and band["robust"]:
-        verdict = "PASS_BINDING_CONFIRMED"                            # TOP1 beats E28 anchor + band opens robust
-    else:
-        verdict = "PASS_WEAK"                                         # holds the gate but does not beat E28 / not robust
+    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"    # noauth path broke (model-independent)
+    elif degenerate:                verdict = "VOID_DEGENERATE_LEVER"     # contradiction~cosine collinear (rho>=0.95)
+    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"      # no op-point holds B2>=0.90 -> fa unreadable
+    elif fa < E28_OP_FA:            verdict = "ESCALATION_CONFIRMED"      # fa_new < 0.0667 strict (B2>=0.90 by select_op)
+    elif fa <= GATE_FA:             verdict = "MODEL_HELPS_PARTIAL"       # 0.0667 <= fa_new <= 0.10 (B2>=0.90)
+    else:                           verdict = "CEILING_NOT_MODEL_SCALE"   # fa_new > 0.10 -> task/data ceiling, exit family
 
     # ---- S1 per-class contradiction distribution (formalized E26 diag) ---------------------------------------
     def _summ(vals):
@@ -411,10 +412,10 @@
 
     # ---- report --------------------------------------------------------------------------------------------
     L = [
-        "# report_E30 -- binding-discipline veto: candidate-SCOPE lever (TOP1 vs ANY) (S1/S2/S3)",
+        "# report_E32 -- model-class escalation: NLI cross-encoder SWAP (scope=any fixed) vs bart 0.0667 bar (S1/S2/S3)",
         "",
-        f"- pre-register   : PRE_REGISTER_E30.md (FROZEN md5 609e9b41db440aba9e78cc32affa4dee) -- sec1/2/4/6 operative",
-        f"- lever          : {CE_MODEL} -- veto candidate SCOPE=top1 (only r[1][0]=bound support) iff (P(CON)>=C AND cos<=K); premise=source.FINDING / hyp=claim",
+        f"- pre-register   : PRE_REGISTER_E32.md (FROZEN md5 e25b801f3b6eb8ced194f47d4c488c66) -- sec1/2/3/5 operative",
+        f"- lever          : MODEL SWAP -> {CE_MODEL} -- veto SCOPE=any (E30 proven-best) iff (P(CON)>=C AND cos<=K); premise=source.FINDING / hyp=claim",
         f"- premise content: from_finding={n_find}/{n_prem} (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)",
         f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
         f"- fixture md5    : {fm} (E25b) | heldout md5 : {hm}",
@@ -426,8 +427,8 @@
         f"- advisory (PRE_REGISTER sec4): |rho| < {PREREG_RHO_ADVISORY} -> {rho_advisory_ok} (REPORTED ONLY; FROZEN substrate VOID-guard is {DEGENERATE_RHO}; see CONFLICT note)",
         f"- contradiction_idx read from id2label (single, asserted) ; from_finding={n_find} asserted > 0",
         "",
-        "## op-point gate (scope=top1; min fa s.t. B2>=0.90 over observed (C,K)). regression anchor = scope=any == E28",
-        f"- regression anchor (scope=any): C={anc_C} K={anc_K} fa={anc_fa} reproduces_E28({E28_OP_FA}+/-{ANCHOR_TOL})={reg_reproduces}",
+        "## op-point gate (scope=any; min fa_new s.t. B2>=0.90 over observed (C,K)). 0.0667 = bart COMPARISON bar (not regression)",
+        f"- anchor-compare (scope=any): C={anc_C} K={anc_K} fa_new={anc_fa} vs bar E28_OP_FA={E28_OP_FA} -> below_bar={anchor_below_bar}",
         f"- chosen C = {chosen_C} | chosen K (cosine gate) = {chosen_K} | B2 at op-point = {chosen_B2}",
         f"- B1 spoof-demotion = {B1}",
         f"- false-accept      = {fa}  (gate <= {GATE_FA})",
@@ -495,18 +496,15 @@
         "",
         f"## VERDICT : {verdict}",
         "",
-        "decision (PRE_REGISTER_E30.md sec6, the ONLY operative fork -- reads scope=top1):",
-        "  PASS_BINDING_CONFIRMED (fa_top1 < anchor 0.0667 strictly AND band robust width>=0.01/>=3pts/B2 lifts off",
-        "    AND S3 reject_share>0.50) -> the E27/E28 knife-edge was ANY-veto MISBINDING; TOP1 resolves it ->",
-        "    graduate the bound-veto into the verifier (verify_E16 integration; TOMMY GO REQUIRED). At integration:",
-        "    reconcile rho guard (0.95 vs 0.50) into one bar; wire (c) entailment-lift -> S3 three-way -> full-GOLD scale.",
-        "  PASS_WEAK (fa_top1<=0.10 AND B2>=0.90 AND S3>0.50, but fa_top1>=0.0667 OR band non-robust) -> TOP1 holds",
-        "    the gate but does not beat E28; misbinding partial. Run the MARGIN arm; do NOT integrate.",
-        "  FAIL_NOT_THE_DRIVER (fa_top1>0.10 OR S3<=0.50: TOP1 lost spoof rejection -- spoofs needed non-top1) ->",
-        "    near-source veto is NOT the dominant driver -> ceiling is model scale -> escalate model class",
-        "    (lab-migration: regenerate L1 -> retrain -> baseline eval -> compare R-bars).",
-        "  REGRESSION (scope=any did NOT reproduce E28 op fa 0.0667) -> machinery broke -> reconcile before reading.",
-        "  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.",
+        "decision (PRE_REGISTER_E32.md sec5, the operative forks -- read scope=any fa_new vs bart bar 0.0667):",
+        "  ESCALATION_CONFIRMED (fa_new < 0.0667 strict AND B2>=0.90) -> model discriminative scale WAS the ceiling ->",
+        "    E33 graduates to a robustness sweep + the verifier-integration question (rho guard 0.95-vs-0.50 reconcile,",
+        "    entailment-lift -> S3 three-way, full-GOLD scale). TOMMY GO REQUIRED before integration.",
+        "  MODEL_HELPS_PARTIAL (0.0667 <= fa_new <= 0.10 AND B2>=0.90) -> bigger model helps but does NOT clear E28 ->",
+        "    decide deeper model class vs task reformulation at the E33 readout.",
+        "  CEILING_NOT_MODEL_SCALE (fa_new > 0.10) -> the ceiling is task/data, not model scale -> the contradiction-veto",
+        "    task itself is the constraint -> EXIT the NLI-swap family and reframe the reject task.",
+        "  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable=fa unreadable) -> reconcile, re-run.",
         "",
         "CONFLICT note (R15 / proto 3.10): PRE_REGISTER advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95",
         "  (one-sided). The lever now USES cosine, so low |rho| is required for the conditioning to add signal (not be",
```
