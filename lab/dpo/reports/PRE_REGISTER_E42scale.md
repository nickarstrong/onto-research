# PRE_REGISTER_E42scale.md  --  FROZEN pre-data

Status   : FROZEN (pre-data, pre-code-that-sees-scores). No result seen at freeze.
Plane    : RESEARCH / verifier SCALE -- fork B (INTEGRATE+CAP), graduated organ D_lambda.
Type     : TYPE C re-emit (NO fixture build). Resolves F1 + F2 at full-GOLD. Fork on result.

## 0. SCOPE CORRECTION (load-bearing -- pack v92 sec3 misframe)
Pack v92 sec3 says "BUILD full-GOLD fixture". There is nothing to build.
- build_fixture_E17.py (md5 7df1615138c389c568590bab8588e084) _meta.purpose:
  "Full-GOLD retrieval bind-corpus ... supersedes E16 61-record slice." The 61->full scale
  already happened at E17.
- On disk gold_fixture.json / _E18 / _E25b ALL carry the SAME 217 records / 216 manifest_files.
  E17->E18->E25b added `finding` coverage (0 -> 27 -> 90/217), NOT records.
- => gold_fixture_E25b.json (md5 4a45f52883a802e8d8d1d5ff5d185bdb, 217 auth DOI-sources) IS the
  full-GOLD bind-corpus. Snippet categories are non-DOI -> not authorizable -> correctly excluded.
DECISION (Founder-confirmed): "full-GOLD" = E25b as frozen. NO rebuild (would break the gated
fixture + the 0.0333 regression anchor + the entire anchored ladder). The run is a RE-EMIT over
the already-full store that surfaces the bind field F1 needs.

## 1. FROZEN OP (carried from E40 graduation -- replayed, NOT re-selected)
- organ   : D_lambda = (n_con - lambda * n_ent) / |S|
- best_op : lambda = 1.0 ; tau = 0.67 ; reject iff (pre_demoted OR D_lambda >= tau)
- source  : E40 FLOOR_BOUND (f15d4d6), region |R|=86 WIDE/STABLE. Op is FROZEN here; no sweep.

## 2. EXTENDED READOUT SCHEMA (6-field + upstream_bind)
Per auth-resolved heldout item (B1=spoof / B2=gold, B2_EXCLUDE removed):
  { item_id, n_con, n_ent, S_size, true_class, pre_demoted, upstream_bind }
- 6-field portion: byte-identical contract to E39/E40 (emit_E37 representative()).
- NEW upstream_bind = mean( beff(B_lex, B_anchor) ) over the REPRESENTATIVE item's bound subset S.
  - beff = (1 - W) * B_lex + W * B_anchor ; W FROZEN 0 (E36 BINDING_EXHAUSTED) => beff == B_lex.
  - representative = the same max-con_share auth claim used for (n_con, n_ent, S_size).
  - set-level mean (matches D_lambda's set-statistic over the SAME S).
  - empty S (S_size==0) -> upstream_bind = null ; item EXCLUDED from the F1 correlation (not 0).
- WITHOUT upstream_bind, F1 is uncomputable -> VOID-by-construction (E23 lesson). This field is
  the only schema change vs the frozen readout.

## 3. REGRESSION ANCHOR (VOID_ANCHOR otherwise -- mandatory, byte-identical)
The re-emit over E25b + heldout_E17 MUST reproduce, on the 30 spoofs:
  - composite fa_op = 0.0333  (16 pre_demoted + 13 con-veto = 29/30 reject)  [4dp]
  - auth-only  fa   = 0.0714  (13/14)                                        [4dp]
under (pre_demoted OR D_lambda(1.0) >= 0.67). Same store, same op => MUST hold. Any deviation =>
VOID_ANCHOR (the run instrument drifted; stop, do not read F1/F2).
Cross-check note: on the 60-row boundset con_share(D_0) and D_lambda(1.0) coincide (0 divergent
spoofs, verified). The apply-step computes D_lambda(1.0) EXPLICITLY (not con_share) so that any
scale-divergence is real, not masked by the boundset coincidence.

## 4. F1 -- rho posture (the live falsifier)
signal  : per-item D_lambda value (continuous reject-signal) vs upstream_bind.
test    : spearman(D_lambda, upstream_bind), ONE-SIDED (positive), over ALL auth-resolved items
          with non-null upstream_bind (both classes; the population the organ acts on).
verdict :
  - rho >= 0.95  -> D_lambda is a RETRIEVAL RELABEL -> E40 graduation CONTAMINATED -> posture +
                    graduation RE-OPEN (back to E39 with bind regressed out). FORK: GRADUATION_REOPEN.
  - rho <  0.95  -> independence HOLDS -> enforce one-sided rho>=0.95 VOID as the v1 guard.
                    FORK continues to F2.
bar provenance: RHO_RECONCILE.md (4bb389b) -- single enforced bar = one-sided 0.95; advisory 0.50
RETIRED; axis re-targeted from the retired cosine to (D_lambda reject-signal, upstream bind).

## 5. F2 -- recall cap structurality
prior   : E40/E41 measured heldout recall = 27/30 = 0.9000 against THIS 217-record store, floor-
          pinned by 3 unrescuable golds (2 noauth pre_demoted + 1 pure-consensus ho_g12 n_ent=0 ->
          D=1.0). Because the store is already full-GOLD, this IS the at-scale recall.
re-confirm (under the frozen op, this run):
  - recall ~= 0.90 (3 fixed golds)  -> cap HOLDS (structural) -> verifier v1 FREEZE path.
                                       FORK: CAP_HOLDS -> v1 freeze + provenance-verifier SPEC fold.
  - recall << 0.90 (debt class large) -> E42 recall organ MANDATORY (noauth-channel, emit extend).
                                       FORK: CAP_DROPS -> open E42 recall organ.

## 6. ORACLE-LEAK GATE (pre-data -- PASS by construction)
- upstream_bind (B_lex) reads ONLY observable text (claim, source.finding); NEVER the held-out
  class label. Oracle-clean.
- op is FROZEN (E40); there is NO op-selection this run -> no recall>=0.90 peek, no class peek.
- class label is JOINED only for reporting (fa by class, recall), never for compute.

## 7. VOID-BY-CONSTRUCTION / CONTENTS COUNTERS (md5 pass != usable -- E15/E23)
Assert BEFORE reading F1/F2:
  - non-empty spoof set (expect 30) AND non-empty gold set (expect 30) in the readout.
  - from_finding > 0 (fixture did not drop `finding`; E23 guard).
  - r[1] top-1-cosine-first ordering guard holds (E30).
  - upstream_bind non-null for every item with S_size>0 (else F1 silently runs on a subset -> VOID).
  - sec6 reconcile: emit decision == E37 op label for all SPOOF items (representative faithful).

## 8. FROZEN INPUTS (md5-gated at run)
- fixture  : eval/_local/gold_fixture_E25b.json   4a45f52883a802e8d8d1d5ff5d185bdb  (217 rec)
- heldout  : eval/_local/heldout_E17.jsonl        7e9fe030646d5671952e7a9fe9437e37
- anchor   : emit_E37_readout.py                  81bc538bd34009e29a7df73e85fc0485  (UNTOUCHED;
             run as-is to reproduce the boundset 0.0333; emit_E42scale is a SEPARATE new script)
- model    : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (FROZEN; ~900 NLI fwd; GPU)

## 9. PASS/FAIL (graduation of this rung)
PASS  : anchor reproduced (0.0333 + 0.0714 byte-identical) AND F1 measured (rho one-sided) AND
        F2 recall measured under op AND fork named in report_E42scale.md AND committed
        (explicit git add of the rung's artifacts, single -m, push main).
FAIL  : VOID_ANCHOR, or any CONTENTS/oracle gate trips, or upstream_bind null where S_size>0.

## 10. TO PRODUCE
- emit_E42scale_readout.py   (new; emit_E37 + 4 deltas: param FIXTURE_MD5 to E25b, add upstream_bind,
  apply D_lambda(1.0) explicit, keep all VOID guards). Committed ALONGSIDE its report only.
- reports/report_E42scale.md | gate_E42scale.log | E42scale_region.json
