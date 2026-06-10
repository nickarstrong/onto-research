# report_E30 -- binding-discipline veto: candidate-SCOPE lever (TOP1 vs ANY) (S1/S2/S3)

- pre-register   : PRE_REGISTER_E30.md (FROZEN md5 609e9b41db440aba9e78cc32affa4dee) -- sec1/2/4/6 operative
- lever          : facebook/bart-large-mnli -- veto candidate SCOPE=top1 (only r[1][0]=bound support) iff (P(CON)>=C AND cos<=K); premise=source.FINDING / hyp=claim
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## trust gates (else VOID)
- baseline (C=+inf) B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True
- decorrelation spearman(contradiction,cosine) rho = -0.237 over 139 pairs | VOID-guard rho>=0.95 -> degenerate=False
- advisory (PRE_REGISTER sec4): |rho| < 0.5 -> True (REPORTED ONLY; FROZEN substrate VOID-guard is 0.95; see CONFLICT note)
- contradiction_idx read from id2label (single, asserted) ; from_finding=109 asserted > 0

## op-point gate (scope=top1; min fa s.t. B2>=0.90 over observed (C,K)). regression anchor = scope=any == E28
- regression anchor (scope=any): C=0.9938673377037048 K=0.651951789855957 fa=0.06666666666666665 reproduces_E28(0.0667+/-0.001)=True
- chosen C = 0.9827359914779663 | chosen K (cosine gate) = 0.8251297473907471 | B2 at op-point = 0.9
- B1 spoof-demotion = 0.7666666666666667
- false-accept      = 0.23333333333333328  (gate <= 0.1)
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.23366666666666674
- op-point verdict  = FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT

## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=top1). delta=+inf == any (anchor); delta=0 ~ top1
    delta=0.00  C=0.9827359914779663  K=0.8251297473907471  fa=0.23333333333333328  B2=0.9  band_robust=False  reject_share=0.5000000000000001
    delta=0.02  C=0.9827359914779663  K=0.8251297473907471  fa=0.19999999999999996  B2=0.9  band_robust=False  reject_share=0.5714285714285715
    delta=0.05  C=0.9827359914779663  K=0.5999017953872681  fa=0.1333333333333333  B2=0.9  band_robust=False  reject_share=0.7142857142857143
    delta=0.10  C=0.9938673377037048  K=0.651951789855957  fa=0.09999999999999998  B2=0.9  band_robust=False  reject_share=0.7857142857142858
    delta=0.20  C=0.9938673377037048  K=0.651951789855957  fa=0.06666666666666665  B2=0.9  band_robust=False  reject_share=0.8571428571428572

## S2 -- (C,K) band / lift-off robustness (PRIMARY E30 question at scope=top1; band read at op-point K; FROZEN grids)
- band at op-point K=0.8251297473907471: joint (fa<=0.1 AND B2>=0.9) C_lo=None C_hi=None width=0.0000 points=0
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
    C=0.900  fa=0.2000  B2=0.8667  joint=.
    C=0.905  fa=0.2000  B2=0.8667  joint=.
    C=0.910  fa=0.2000  B2=0.8667  joint=.
    C=0.915  fa=0.2000  B2=0.8667  joint=.
    C=0.920  fa=0.2333  B2=0.8667  joint=.
    C=0.925  fa=0.2333  B2=0.8667  joint=.
    C=0.930  fa=0.2333  B2=0.8667  joint=.
    C=0.935  fa=0.2333  B2=0.8667  joint=.
    C=0.940  fa=0.2333  B2=0.8667  joint=.
    C=0.945  fa=0.2333  B2=0.8667  joint=.
    C=0.950  fa=0.2333  B2=0.8667  joint=.
    C=0.955  fa=0.2333  B2=0.8667  joint=.
    C=0.960  fa=0.2333  B2=0.8667  joint=.
    C=0.965  fa=0.2333  B2=0.8667  joint=.
    C=0.970  fa=0.2333  B2=0.8667  joint=.
    C=0.975  fa=0.2333  B2=0.8667  joint=.
    C=0.980  fa=0.2333  B2=0.8667  joint=.
    C=0.985  fa=0.2333  B2=0.9000  joint=.
    C=0.990  fa=0.2667  B2=0.9000  joint=.
    C=0.991  fa=0.3000  B2=0.9000  joint=.
    C=0.992  fa=0.3000  B2=0.9000  joint=.
    C=0.993  fa=0.3000  B2=0.9000  joint=.
    C=0.994  fa=0.3000  B2=0.9333  joint=.
    C=0.995  fa=0.3000  B2=0.9333  joint=.
    C=0.996  fa=0.3333  B2=0.9333  joint=.
    C=0.997  fa=0.3333  B2=0.9333  joint=.
    C=0.998  fa=0.3333  B2=0.9333  joint=.
    C=0.999  fa=0.3333  B2=0.9333  joint=.

## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions at conditioned op-point)
- spoofs total=30 | demoted@op=23 | survived(false-accept)=7
- (a) noauth baseline (demote @ C=+inf)         = 16
- (b) contradiction-veto reject organ           = 7  (demoted ONLY because veto fired)
- (c) accept/entailment-lift organ              = 0  (NOT wired in standalone probe; verifier-integration step)
- reject_share = (fa_base - fa_op)/fa_base = (0.4667 - 0.2333)/0.4667 = 0.5000
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

## candidate-level separation at op-point (C=0.98274, K=0.8251297473907471; counts ALL finding candidates crossing -- DIAGNOSTIC, not the top1 item-veto)
- gold-content candidates  : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793 | cross (con>=C AND cos<=K): 7/74
- spoof-content candidates : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998 | cross (con>=C AND cos<=K): 21/35
- spoof-vs-gold content p50 separation = 0.9532 (spoof 0.9909 - gold 0.0377)
- S1 expectation: separation > 0.5 -> True (diagnostic only; verdict reads max-based fa, not sep)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).

## VERDICT : FAIL_NOT_THE_DRIVER

decision (PRE_REGISTER_E30.md sec6, the ONLY operative fork -- reads scope=top1):
  PASS_BINDING_CONFIRMED (fa_top1 < anchor 0.0667 strictly AND band robust width>=0.01/>=3pts/B2 lifts off
    AND S3 reject_share>0.50) -> the E27/E28 knife-edge was ANY-veto MISBINDING; TOP1 resolves it ->
    graduate the bound-veto into the verifier (verify_E16 integration; TOMMY GO REQUIRED). At integration:
    reconcile rho guard (0.95 vs 0.50) into one bar; wire (c) entailment-lift -> S3 three-way -> full-GOLD scale.
  PASS_WEAK (fa_top1<=0.10 AND B2>=0.90 AND S3>0.50, but fa_top1>=0.0667 OR band non-robust) -> TOP1 holds
    the gate but does not beat E28; misbinding partial. Run the MARGIN arm; do NOT integrate.
  FAIL_NOT_THE_DRIVER (fa_top1>0.10 OR S3<=0.50: TOP1 lost spoof rejection -- spoofs needed non-top1) ->
    near-source veto is NOT the dominant driver -> ceiling is model scale -> escalate model class
    (lab-migration: regenerate L1 -> retrain -> baseline eval -> compare R-bars).
  REGRESSION (scope=any did NOT reproduce E28 op fa 0.0667) -> machinery broke -> reconcile before reading.
  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.

CONFLICT note (R15 / proto 3.10): PRE_REGISTER advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95
  (one-sided). The lever now USES cosine, so low |rho| is required for the conditioning to add signal (not be
  redundant with contradiction). Both pass at observed rho (E27 -0.237). This file keeps the FROZEN 0.95 as the
  VOID trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.

## diff-proof : run_E28_probe.py -> run_E30_probe.py (PRE_REGISTER_E30 sec2)
- stat: 1 file changed, 149 insertions(+), 98 deletions(-)
- changed ONLY: header comment; scope param+top1/any/margin branch; scope threading (metrics/s2/s3/select_op); anchor K=+inf -> scope=any (E28 op 0.0667); MARGIN reported-arm; verdict fork (PRE_REGISTER_E30 sec6); --out report_E30.md; r[1] top1-cosine-first guard.
- NO grid/constant/threshold changed: GATE_FA=0.10, E20B=0.467, S3_BAR=0.50, RECALL_FLOOR, S2_GRID, K_GRID, DEGENERATE_RHO=0.95, S1_TAIL_CON=0.95 byte-identical. any-branch == run_E28 line153 verbatim (anchor reproduced 0.0667 at runtime).

```diff
diff --git a/run_E28_probe.py b/run_E30_probe.py
index d3ea2f2..34432f3 100644
--- a/run_E28_probe.py
+++ b/run_E30_probe.py
@@ -19,17 +19,19 @@ import semantic_retrieve as sem
 import torch
 from transformers import AutoTokenizer, AutoModelForSequenceClassification
 
-# E28 = OBSERVABLE-CONDITIONED contradiction-veto (knife-edge tune of E27). PRE_REGISTER_E28.md (FROZEN,
-#   md5 f3fab7581d1c15e7b58926da82d01dc3). E27 was PASS_KNIFE_EDGE: op fa 0.0667 reproduced E26 deterministically
-#   and S3 reject_share 0.857 (veto owns), but the joint (fa<=0.10 AND B2>=0.90) band was a single C=0.995 with
-#   B2 pinned to the 0.90 floor (width 0) -> robust=False. DIAGNOSIS: not one outlier but TAIL OVERLAP -- gold
-#   p90=0.979 interleaves the spoof mass in C in [0.99,0.996], unseparable by a single scalar threshold.
-#   LEVER (per-OBSERVABLE C, NOT per-class true-class which is oracle leak): veto fires iff
-#   (contradiction >= C AND binding_cosine <= K). cosine is observable at decision time; high-cosine gold is
-#   spared, low-cosine spoof in the overlap is demoted. K=+inf DEGENERATES to E27's scalar C (regression guard).
-#   SAME frozen gate (fa<=0.10) + SAME trust gates. ADDS: S1 driver isolation, S2 (C,K) band robustness, S3
-#   attribution. NO new data, NO fixture edit. Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve,
-#   run_E26, run_E27) untouched; conditioning + footgun fixes folded into THIS file only.
+# E30 = BINDING-DISCIPLINE veto: candidate-SCOPE lever (TOP1 vs ANY). PRE_REGISTER_E30.md (FROZEN,
+#   md5 609e9b41db440aba9e78cc32affa4dee). E29 REVERSAL (report_E29_reauthor.md md5 c1f38de7769eda990d20ee68404480c1):
+#   the E27/E28 knife-edge is RETRIEVAL MISBINDING under an ANY-CANDIDATE veto, NOT a premise-phrasing defect and
+#   NOT cosine-separable. A gold claim retrieves its true entailing support AND a topically-near WRONG-SOURCE
+#   record; the wrong-source record faithfully contradicts the claim, so `any-candidate` veto (run_E28 line 153)
+#   falsely vetoes the gold claim -> pins B2 to the 0.90 floor -> the op-point cannot lower C to catch more spoof.
+#   LEVER (E30): restrict the veto's CANDIDATE SCOPE. scope='top1' = veto considers ONLY r[1][0] (highest-cosine
+#   authorized candidate = the bound support); 'any' = run_E28 line 153 verbatim (REGRESSION ANCHOR); 'margin'
+#   (delta) = bound-neighborhood (robustness arm). A candidate vetoes iff (contradiction >= C AND cosine <= K);
+#   K carried from E28 (K=+inf disables the gate). SCOPE is observable (cosine/rank, no true-class) -> oracle-safe.
+#   SAME frozen gate (fa<=0.10) + SAME grids + SAME trust gates as run_E28. ADDS: scope param + scope='any'
+#   regression-anchor reproducing E28 op fa 0.0667 + margin sweep. ONE line of veto logic differs from run_E28.
+#   Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26/E27/E28) untouched; scope folded HERE.
 CE_MODEL = os.environ.get("ONTO_CE_MODEL", "facebook/bart-large-mnli")   # model-scale NLI; override via env
 E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
 GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
@@ -54,6 +56,15 @@ S3_REJECT_SHARE_BAR = 0.50    # reject organ must own > this share of baseline f
 K_GRID = sorted(set([round(0.45 + 0.05 * i, 2) for i in range(0, 12)]))  # 0.45 .. 1.00
 S1_TAIL_CON = 0.95            # S1 driver isolation: gold-content items with contradiction >= this
 
+# --- E30 candidate-SCOPE lever (FROZEN pre-data, PRE_REGISTER_E30.md sec1-2) -------------------------------
+#   scope='top1' (PRIMARY) = veto considers ONLY r[1][0] (bound support). scope='any' = run_E28 line 153
+#   (REGRESSION ANCHOR). scope=('margin',delta) = bound-neighborhood (robustness arm; reported, not the verdict).
+PRIMARY_SCOPE = "top1"
+ANCHOR_SCOPE  = "any"
+MARGIN_GRID = [0.00, 0.02, 0.05, 0.10, 0.20]   # delta grid for the reported robustness arm
+E28_OP_FA   = 0.0667         # E28 operating-point false-accept; scope='any' MUST reproduce this (regression)
+ANCHOR_TOL  = 1e-3           # reproduction tolerance (< one spoof-item granularity ~0.0667)
+
 _ce_tok = _ce_model = _con_idx = None
 def _ce_load():
     global _ce_tok, _ce_model, _con_idx
@@ -139,26 +150,39 @@ def precompute_item(item, store, mat, recs, decorr, prem_log, finding_by_source,
         resolutions.append(("auth", [(float(c), float(s)) for c, s in zip(coss, scs)]))
     return resolutions
 
-def item_label_at_C(resolutions, C, K=float("inf")):
-    """E28 observable-conditioned veto: an authorized claim is VETOED (UNVERIFIABLE) when ANY authorized
-    candidate has (contradiction >= C AND binding_cosine <= K), else VERIFIED. K=+inf disables the cosine
-    gate -> veto iff max contradiction >= C == E27 scalar behavior (regression anchor; reproduces E26/E27).
-    Baseline C=+inf => nothing vetoed => only noauth demotes => no-veto fa 0.467 (model-independent).
-    Rollup identical to run_E26/E27 (UNVERIFIABLE dominates -> DEMOTE)."""
+def item_label_at_C(resolutions, C, K=float("inf"), scope=PRIMARY_SCOPE):
+    """E30 binding-discipline veto. `scope` selects WHICH authorized candidate(s) may veto:
+       'top1'            : only r[1][0] (highest-cosine authorized candidate = bound support) -- E30 PRIMARY.
+       'any'             : any candidate (== run_E28 line 153 verbatim) -- REGRESSION ANCHOR only.
+       ('margin', delta) : any candidate with cos >= cos0 - delta (bound-neighborhood) -- robustness arm.
+    A candidate vetoes iff (contradiction >= C AND binding_cosine <= K). K=+inf disables the cosine gate.
+    Baseline C=+inf => nothing crosses under ANY scope => only noauth demotes => no-veto fa 0.467
+    (scope-independent, model-independent). Rollup identical to run_E26/E27/E28 (UNVERIFIABLE dominates -> DEMOTE).
+    r[1] is ordered top-1-cosine-first (asserted in main); r[1][0] is the bound support."""
     labs = []
     for r in resolutions:
         if r == "common":   labs.append("PASS-COMMON")
         elif r == "noauth": labs.append("UNVERIFIABLE")
         else:
-            veto = any((sc >= C and cos <= K) for (cos, sc) in r[1])
+            cands = r[1]                                   # [(cos, contradiction), ...] top-1 cosine first
+            if scope == "top1":
+                cos0, sc0 = cands[0]
+                veto = (sc0 >= C and cos0 <= K)
+            elif scope == "any":
+                veto = any((sc >= C and cos <= K) for (cos, sc) in cands)
+            elif isinstance(scope, tuple) and scope[0] == "margin":
+                delta = float(scope[1]); cos0 = cands[0][0]
+                veto = any((sc >= C and cos <= K and cos >= cos0 - delta) for (cos, sc) in cands)
+            else:
+                raise ValueError(f"unknown scope {scope!r}")
             labs.append("UNVERIFIABLE" if veto else "VERIFIED")
     if not labs: return "PASS-COMMON"
     if "UNVERIFIABLE" in labs: return "DEMOTE"
     if "VERIFIED" in labs: return "VERIFIED"
     return "PASS-COMMON"
 
-def metrics_at_C(items_pre, C, K=float("inf")):
-    res = [(it, item_label_at_C(r, C, K)) for (it, r) in items_pre]
+def metrics_at_C(items_pre, C, K=float("inf"), scope=PRIMARY_SCOPE):
+    res = [(it, item_label_at_C(r, C, K, scope)) for (it, r) in items_pre]
     b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
     b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
     b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
@@ -169,12 +193,12 @@ def metrics_at_C(items_pre, C, K=float("inf")):
 
 # ===== E27 NEW: S2 robustness sweep, S3 demotion attribution ==============================================
 
-def s2_band_at_K(items_pre, K):
+def s2_band_at_K(items_pre, K, scope=PRIMARY_SCOPE):
     """S2 -- C-sweep at a FIXED cosine-gate K over the FROZEN C grid; locate the joint (fa<=0.10 AND B2>=0.90)
-    band. Returns (rows, band). The robustness verdict is read at the OP-POINT's selected K (PRE_REGISTER sec3)."""
+    band. Returns (rows, band). The robustness verdict is read at the OP-POINT's selected K (PRE_REGISTER sec4)."""
     rows = []
     for C in S2_GRID:
-        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C), K)
+        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C), K, scope)
         fa = (1.0 - B1) if not np.isnan(B1) else float("nan")
         joint = (not np.isnan(fa)) and (not np.isnan(B2)) and (fa <= GATE_FA) and (B2 >= RECALL_FLOOR)
         rows.append((float(C), float(fa), float(B2), bool(joint)))
@@ -191,28 +215,28 @@ def s2_band_at_K(items_pre, K):
         band = dict(c_lo=None, c_hi=None, width=0.0, points=0, b2_liftoff=0.0, robust=False)
     return rows, band
 
-def s2_perK_summary(items_pre):
+def s2_perK_summary(items_pre, scope=PRIMARY_SCOPE):
     """Per-K joint C-band summary over the FROZEN K_GRID (+ K=+inf E27 anchor). Reporting; the verdict reads
     the band at the op-point K (s2_band_at_K). Shows WHERE in K the cosine gate opens band air."""
     out = []
     for K in (K_GRID + [float("inf")]):
-        _rows, band = s2_band_at_K(items_pre, float(K))
+        _rows, band = s2_band_at_K(items_pre, float(K), scope)
         out.append((K, band["width"], band["points"], band["b2_liftoff"], band["robust"]))
     return out
 
-def s3_attribution(items_pre, op_C, op_K, fa_base, fa_op):
-    """S3 -- decompose B1-class (spoof) demotions at the conditioned op-point (op_C, op_K) into:
-       (a) noauth baseline  : demotes already at C=+inf (no veto needed),
-       (b) contradiction-veto reject organ : demotes at (op_C,op_K) but NOT at C=+inf (a candidate crossed
-                                             the conditioned veto: contradiction>=op_C AND cos<=op_K),
+def s3_attribution(items_pre, op_C, op_K, fa_base, fa_op, scope=PRIMARY_SCOPE):
+    """S3 -- decompose B1-class (spoof) demotions at the op-point (op_C, op_K, scope) into:
+       (a) noauth baseline  : demotes already at C=+inf (no veto needed; scope-independent),
+       (b) contradiction-veto reject organ : demotes at (op_C,op_K,scope) but NOT at C=+inf (a candidate in
+                                             scope crossed the veto: contradiction>=op_C AND cos<=op_K),
        (c) accept/entailment-lift organ    : NOT wired in this standalone probe -> structurally 0.
-    reject_share = (fa_base - fa_op)/fa_base. Bar (PRE_REGISTER_E28 sec3-S3): > 0.50."""
+    reject_share = (fa_base - fa_op)/fa_base. Bar (PRE_REGISTER_E30 sec4-S3): > 0.50."""
     spoofs = [r for (it, r) in items_pre if it["class"] == B1_CLASS]
     n_total = len(spoofs)
     n_demote_op = n_by_noauth = n_by_veto = n_survive = 0
     for r in spoofs:
-        base = item_label_at_C(r, float("inf"))
-        op = item_label_at_C(r, float(op_C), float(op_K))
+        base = item_label_at_C(r, float("inf"), float("inf"), scope)
+        op = item_label_at_C(r, float(op_C), float(op_K), scope)
         if op == "DEMOTE":
             n_demote_op += 1
             if base == "DEMOTE":  n_by_noauth += 1
@@ -230,7 +254,7 @@ def main():
     ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
     ap.add_argument("--fixture_md5", default="4a45f52883a802e8d8d1d5ff5d185bdb")
     ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
-    ap.add_argument("--out", default="reports/report_E28.md")
+    ap.add_argument("--out", default="reports/report_E30.md")   # NEVER a frozen-report path (no clobber E28/E27)
     a = ap.parse_args()
 
     fm, hm = md5(a.fixture), md5(a.heldout)
@@ -257,6 +281,15 @@ def main():
     print(f"[premise] from_finding={n_find}/{n_prem} from_source(fallback)={n_prem-n_find}")
     assert n_find > 0, "from_finding=0 -> fixture dropped 'finding' -> VOID-by-construction (E23 guard)"
 
+    # E30 ORDERING GUARD: r[1] MUST be top-1-cosine-first (r[1][0] = bound support). The TOP1 scope is invalid
+    # otherwise. candidates_with_cosine returns argsort(-sims) + floor-break; authorized filter preserves order.
+    for (_it, rr) in items_pre:
+        for x in rr:
+            if isinstance(x, tuple) and x[0] == "auth":
+                cs = [c for (c, _s) in x[1]]
+                assert all(cs[i] >= cs[i + 1] - 1e-9 for i in range(len(cs) - 1)), \
+                    "r[1] not top-1-cosine-first -> TOP1 scope invalid -> STOP"
+
     rho = spearman([c for c, _ in decorr], [s for _, s in decorr])
     degenerate = (not np.isnan(rho)) and rho >= DEGENERATE_RHO            # FROZEN E26 VOID guard (0.95, one-sided)
     rho_advisory_ok = (not np.isnan(rho)) and abs(rho) < PREREG_RHO_ADVISORY   # PRE_REGISTER sec4 advisory (reported)
@@ -275,68 +308,79 @@ def main():
     C_obs = sorted({sc for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc) in x[1]})
     K_obs = sorted({cos for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc) in x[1]})
 
-    # REGRESSION ANCHOR: K=+inf disables the cosine gate -> E27 scalar rule (lowest observed C with B2>=0.90).
-    # MUST reproduce E27 (C~0.9949, fa~0.0667). Mismatch => REGRESSION (wiring drifted from frozen behavior).
-    reg_C = None
-    for C in C_obs:
-        _b1, b2, _b3, _ = metrics_at_C(items_pre, C, float("inf"))
-        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
-            reg_C = float(C); break
-    if reg_C is not None:
-        rB1, _rB2, _rB3, _ = metrics_at_C(items_pre, reg_C, float("inf")); reg_fa = 1.0 - rB1
-    else:
-        reg_fa = float("nan")
-    reg_reproduces = (reg_C is not None) and (not np.isnan(reg_fa)) and (reg_fa <= GATE_FA)
-    print(f"[regression-anchor K=+inf] C={reg_C} fa={reg_fa} reproduces_E27(fa<={GATE_FA})={reg_reproduces}")
-
-    # E28 conditioned op-point: over OBSERVED (C,K), MIN fa subject to B2>=0.90. Tie-break (frozen):
-    # widest joint C-band at that K -> lowest C -> highest K (deterministic; selection peeks ONLY recall feasibility).
-    feasible = []
-    for K in K_obs:
-        for C in C_obs:
-            b1, b2, _b3, _ = metrics_at_C(items_pre, C, K)
-            if not np.isnan(b2) and b2 >= RECALL_FLOOR:
-                feasible.append((1.0 - b1, float(C), float(K)))
-    chosen_C = chosen_K = chosen_B2 = None
-    if feasible:
+    # ---- op-point selector (FROZEN selection, byte-identical to E28; only `scope` added) ---------------------
+    # over OBSERVED (C,K): MIN false-accept subject to B2>=0.90. Tie-break (frozen): widest joint C-band at that
+    # K -> lowest C -> highest K. selection peeks ONLY recall feasibility (no post-hoc fishing on fa).
+    def select_op(scope):
+        feasible = []
+        for K in K_obs:
+            for C in C_obs:
+                b1, b2, _b3, _ = metrics_at_C(items_pre, C, K, scope)
+                if not np.isnan(b2) and b2 >= RECALL_FLOOR:
+                    feasible.append((1.0 - b1, float(C), float(K)))
+        if not feasible:
+            return None, None, None, float("nan")
         min_fa = min(f for f, _c, _k in feasible)
-        cands = [(c, k) for (f, c, k) in feasible if abs(f - min_fa) < 1e-12]
-        _bw = {k: s2_band_at_K(items_pre, k)[1]["width"] for (_c, k) in cands}
-        cands.sort(key=lambda ck: (-_bw[ck[1]], ck[0], -ck[1]))
-        chosen_C, chosen_K = cands[0]
-        _b1, chosen_B2, _b3, _ = metrics_at_C(items_pre, chosen_C, chosen_K)
-
+        cand = [(c, k) for (f, c, k) in feasible if abs(f - min_fa) < 1e-12]
+        _bw = {k: s2_band_at_K(items_pre, k, scope)[1]["width"] for (_c, k) in cand}
+        cand.sort(key=lambda ck: (-_bw[ck[1]], ck[0], -ck[1]))
+        c_, k_ = cand[0]
+        _b1, b2_, _b3, _ = metrics_at_C(items_pre, c_, k_, scope)
+        return float(c_), float(k_), float(b2_), float(min_fa)
+
+    # REGRESSION ANCHOR (E30 sec3-T6): scope='any' == run_E28 line 153. Re-selecting the op-point under 'any'
+    # MUST reproduce the E28 operating point (false-accept 0.0667). Mismatch => REGRESSION (machinery broke).
+    anc_C, anc_K, anc_B2, anc_fa = select_op(ANCHOR_SCOPE)
+    reg_reproduces = (anc_C is not None) and (not np.isnan(anc_fa)) and (abs(anc_fa - E28_OP_FA) <= ANCHOR_TOL)
+    print(f"[regression-anchor scope=any] C={anc_C} K={anc_K} fa={anc_fa} "
+          f"reproduces_E28({E28_OP_FA}+/-{ANCHOR_TOL})={reg_reproduces}")
+
+    # E30 PRIMARY op-point: scope='top1' (veto considers ONLY the bound support r[1][0]).
+    chosen_C, chosen_K, chosen_B2, _min_fa = select_op(PRIMARY_SCOPE)
     if chosen_C is None:
         op_verdict = "FAIL_RECALL_UNUSABLE"; B1 = B2 = B3 = fa = move = float("nan")
     else:
-        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C, chosen_K)
+        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C, chosen_K, PRIMARY_SCOPE)
         fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
         if   fa <= GATE_FA:           op_verdict = "PASS"
         elif fa < PARTIAL_BAND:       op_verdict = "FAIL_PARTIAL_VETO"
         else:                         op_verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"
 
-    # ---- S2 robustness: band read at the OP-POINT's K (PRE_REGISTER_E28 sec3-S2) + per-K summary -------------
+    # ---- S2 robustness: band read at the TOP1 OP-POINT's K + per-K summary (scope=top1) ---------------------
     K_for_band = chosen_K if chosen_K is not None else float("inf")
-    s2_rows, band = s2_band_at_K(items_pre, float(K_for_band))
-    s2_perK = s2_perK_summary(items_pre)
+    s2_rows, band = s2_band_at_K(items_pre, float(K_for_band), PRIMARY_SCOPE)
+    s2_perK = s2_perK_summary(items_pre, PRIMARY_SCOPE)
     if chosen_C is not None and base_ok:
-        s3 = s3_attribution(items_pre, chosen_C, chosen_K, fa_base, fa)
+        s3 = s3_attribution(items_pre, chosen_C, chosen_K, fa_base, fa, PRIMARY_SCOPE)
     else:
         s3 = dict(n_total=0, n_demote_op=0, n_by_noauth=0, n_by_veto=0, n_survive=0, n_by_entailment=0,
                   reject_share=float("nan"), bar_met=False)
 
-    # ---- E28 verdict (PRE_REGISTER_E28 sec6, the ONLY operative fork) -----------------------------------------
+    # ---- MARGIN robustness arm (REPORTED ONLY; NOT the verdict) -- op-point per delta over the FROZEN grid ---
+    margin_rows = []
+    for delta in MARGIN_GRID:
+        mC, mK, mB2, mfa = select_op(("margin", float(delta)))
+        if mC is None:
+            margin_rows.append((delta, None, None, float("nan"), float("nan"), False, float("nan")))
+        else:
+            _r, mband = s2_band_at_K(items_pre, float(mK), ("margin", float(delta)))
+            ms3 = s3_attribution(items_pre, mC, mK, fa_base, mfa, ("margin", float(delta))) if base_ok else \
+                  dict(reject_share=float("nan"))
+            margin_rows.append((delta, mC, mK, mfa, mB2, mband["robust"], ms3["reject_share"]))
+
+    # ---- E30 verdict (PRE_REGISTER_E30.md sec6, the ONLY operative fork; reads scope=top1) -------------------
+    s3rej = s3["reject_share"]
     if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"
     elif degenerate:                verdict = "VOID_DEGENERATE_LEVER"
-    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"   # veto destroys gold recall (no op-point)
-    elif not reg_reproduces:        verdict = "REGRESSION"             # K=+inf did NOT reproduce E27 scalar op
-    elif fa > GATE_FA:              verdict = "REGRESSION"             # conditioned op above the frozen gate
-    elif band["robust"] and s3["bar_met"]:
-        verdict = "PASS_ROBUST"
-    elif not band["robust"]:
-        verdict = "PASS_KNIFE_EDGE"
-    else:                           # band robust but reject organ doesn't own the gain
-        verdict = "PASS_MISATTRIBUTED"
+    elif not reg_reproduces:        verdict = "REGRESSION"             # scope=any did NOT reproduce E28 op fa 0.0667
+    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"   # TOP1 veto destroys gold recall (no op-point)
+    elif fa > GATE_FA:              verdict = "FAIL_NOT_THE_DRIVER"    # TOP1 breaches the frozen gate
+    elif np.isnan(s3rej) or s3rej <= S3_REJECT_SHARE_BAR:
+        verdict = "FAIL_NOT_THE_DRIVER"                               # spoof rejection collapsed (needed non-top1)
+    elif (fa < anc_fa) and band["robust"]:
+        verdict = "PASS_BINDING_CONFIRMED"                            # TOP1 beats E28 anchor + band opens robust
+    else:
+        verdict = "PASS_WEAK"                                         # holds the gate but does not beat E28 / not robust
 
     # ---- S1 per-class contradiction distribution (formalized E26 diag) ---------------------------------------
     def _summ(vals):
@@ -367,10 +411,10 @@ def main():
 
     # ---- report --------------------------------------------------------------------------------------------
     L = [
-        "# report_E28 -- observable-conditioned contradiction-veto: (C x cosine-gate K) knife-edge tune (S1/S2/S3)",
+        "# report_E30 -- binding-discipline veto: candidate-SCOPE lever (TOP1 vs ANY) (S1/S2/S3)",
         "",
-        f"- pre-register   : PRE_REGISTER_E28.md (FROZEN md5 f3fab7581d1c15e7b58926da82d01dc3) -- sec2/3/5/6 operative",
-        f"- lever          : {CE_MODEL} -- veto iff (P(CONTRADICTION)>=C AND binding_cosine<=K); premise=source.FINDING / hyp=claim",
+        f"- pre-register   : PRE_REGISTER_E30.md (FROZEN md5 609e9b41db440aba9e78cc32affa4dee) -- sec1/2/4/6 operative",
+        f"- lever          : {CE_MODEL} -- veto candidate SCOPE=top1 (only r[1][0]=bound support) iff (P(CON)>=C AND cos<=K); premise=source.FINDING / hyp=claim",
         f"- premise content: from_finding={n_find}/{n_prem} (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)",
         f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
         f"- fixture md5    : {fm} (E25b) | heldout md5 : {hm}",
@@ -382,8 +426,8 @@ def main():
         f"- advisory (PRE_REGISTER sec4): |rho| < {PREREG_RHO_ADVISORY} -> {rho_advisory_ok} (REPORTED ONLY; FROZEN substrate VOID-guard is {DEGENERATE_RHO}; see CONFLICT note)",
         f"- contradiction_idx read from id2label (single, asserted) ; from_finding={n_find} asserted > 0",
         "",
-        "## op-point gate (conditioned; min fa s.t. B2>=0.90 over observed (C,K); K=+inf reduces to E27 scalar)",
-        f"- regression anchor (K=+inf): C={reg_C} fa={reg_fa} reproduces_E27(fa<={GATE_FA})={reg_reproduces}",
+        "## op-point gate (scope=top1; min fa s.t. B2>=0.90 over observed (C,K)). regression anchor = scope=any == E28",
+        f"- regression anchor (scope=any): C={anc_C} K={anc_K} fa={anc_fa} reproduces_E28({E28_OP_FA}+/-{ANCHOR_TOL})={reg_reproduces}",
         f"- chosen C = {chosen_C} | chosen K (cosine gate) = {chosen_K} | B2 at op-point = {chosen_B2}",
         f"- B1 spoof-demotion = {B1}",
         f"- false-accept      = {fa}  (gate <= {GATE_FA})",
@@ -392,7 +436,13 @@ def main():
         f"- movement vs 0.467 = {move}",
         f"- op-point verdict  = {op_verdict}",
         "",
-        "## S2 -- (C,K) band / lift-off robustness (PRIMARY E28 question; band read at the op-point K; FROZEN grids)",
+        "## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=top1). delta=+inf == any (anchor); delta=0 ~ top1",
+    ]
+    for (delta, mC, mK, mfa, mB2, mrob, mrej) in margin_rows:
+        L.append(f"    delta={delta:.2f}  C={mC}  K={mK}  fa={mfa}  B2={mB2}  band_robust={mrob}  reject_share={mrej}")
+    L += [
+        "",
+        "## S2 -- (C,K) band / lift-off robustness (PRIMARY E30 question at scope=top1; band read at op-point K; FROZEN grids)",
         f"- band at op-point K={K_for_band}: joint (fa<={GATE_FA} AND B2>={RECALL_FLOOR}) C_lo={band['c_lo']} "
         f"C_hi={band['c_hi']} width={band['width']:.4f} points={band['points']}",
         f"- B2 lift-off within band (max B2 - floor) = {band['b2_liftoff']:.4f}  (>0 == not pinned to floor)",
@@ -435,9 +485,9 @@ def main():
         L.append(f"    con={sc:.4f}  cos={cos:.4f}  id={_id}")
     L += [
         "",
-        f"## conditioned separation at op-point (C={Cn:.5f}, K={Kn}; veto iff contradiction>=C AND cos<=K)",
-        f"- gold-content  (want NOT vetoed) : {_summ(gc_s)} | falsely vetoed: {gv}/{len(gc_s)}",
-        f"- spoof-content (want vetoed)     : {_summ(spc_s)} | correctly vetoed: {sv}/{len(spc_s)}",
+        f"## candidate-level separation at op-point (C={Cn:.5f}, K={Kn}; counts ALL finding candidates crossing -- DIAGNOSTIC, not the top1 item-veto)",
+        f"- gold-content candidates  : {_summ(gc_s)} | cross (con>=C AND cos<=K): {gv}/{len(gc_s)}",
+        f"- spoof-content candidates : {_summ(spc_s)} | cross (con>=C AND cos<=K): {sv}/{len(spc_s)}",
         f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
         f"- S1 expectation: separation > 0.5 -> {s1_sep_ok} (diagnostic only; verdict reads max-based fa, not sep)",
         "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
@@ -445,16 +495,17 @@ def main():
         "",
         f"## VERDICT : {verdict}",
         "",
-        "decision (PRE_REGISTER_E28.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate):",
-        "  PASS_ROBUST (conditioned band robust: width>=0.01/>=3pts/B2 lifts off at op-K AND S3 reject_share>0.50)",
-        "    -> reject organ ROBUST under observable conditioning -> graduate the (contradiction x cosine) veto into",
-        "       the verifier (verify_E16 integration; TOMMY GO REQUIRED, frozen substrate edited). At integration:",
-        "       reconcile rho guard (0.95 vs 0.50) into one bar; wire (c) entailment-lift -> S3 three-way.",
-        "  PASS_KNIFE_EDGE (cosine gate does NOT open the band: single point / B2 pinned) -> tail overlap NOT",
-        "    cosine-separable -> premise quality is the binding constraint -> E29 targeted re-author of the S1 tail",
-        "    drivers with a FRESH fixture freeze (NEW data, separate session). No verifier integration.",
-        "  PASS_MISATTRIBUTED (band robust but reject_share<=0.50) -> gain not owned by the reject organ -> tune.",
-        "  REGRESSION (K=+inf does not reproduce E27 scalar op, OR conditioned op fa>0.10) -> reconcile before anything.",
+        "decision (PRE_REGISTER_E30.md sec6, the ONLY operative fork -- reads scope=top1):",
+        "  PASS_BINDING_CONFIRMED (fa_top1 < anchor 0.0667 strictly AND band robust width>=0.01/>=3pts/B2 lifts off",
+        "    AND S3 reject_share>0.50) -> the E27/E28 knife-edge was ANY-veto MISBINDING; TOP1 resolves it ->",
+        "    graduate the bound-veto into the verifier (verify_E16 integration; TOMMY GO REQUIRED). At integration:",
+        "    reconcile rho guard (0.95 vs 0.50) into one bar; wire (c) entailment-lift -> S3 three-way -> full-GOLD scale.",
+        "  PASS_WEAK (fa_top1<=0.10 AND B2>=0.90 AND S3>0.50, but fa_top1>=0.0667 OR band non-robust) -> TOP1 holds",
+        "    the gate but does not beat E28; misbinding partial. Run the MARGIN arm; do NOT integrate.",
+        "  FAIL_NOT_THE_DRIVER (fa_top1>0.10 OR S3<=0.50: TOP1 lost spoof rejection -- spoofs needed non-top1) ->",
+        "    near-source veto is NOT the dominant driver -> ceiling is model scale -> escalate model class",
+        "    (lab-migration: regenerate L1 -> retrain -> baseline eval -> compare R-bars).",
+        "  REGRESSION (scope=any did NOT reproduce E28 op fa 0.0667) -> machinery broke -> reconcile before reading.",
         "  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.",
         "",
         "CONFLICT note (R15 / proto 3.10): PRE_REGISTER advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95",
```
