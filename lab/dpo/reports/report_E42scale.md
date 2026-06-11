# report_E42scale.md  --  full-GOLD scale: F1 + F2 resolved

Verdict   : PASS / CAP_HOLDS. D_lambda graduation CONFIRMED at full-GOLD; verifier-v1 freeze path open.
Pre-reg   : reports/PRE_REGISTER_E42scale.md (FROZEN md5 a2f6bb5fd19fbfd1c08c6de4d111df6e). No bar relitigated.
Type      : TYPE C re-emit (NO fixture build). Compute: RTX A4500 (cuda), DeBERTa-v3-large-mnli (frozen).

## 0. Scope (confirmed, not assumed)
"full-GOLD" = gold_fixture_E25b.json (md5 4a45f52883a802e8d8d1d5ff5d185bdb, 217 auth records / 216
manifest / 90 findings) -- the FULL build_fixture_E17 output (supersedes E16 61-slice). E17->E18->E25b
grew `finding` (0->27->90), NOT records. No rebuild. The run is a re-emit over the already-full store
that surfaces upstream_bind (the bind field F1 needs), absent from the frozen 6-field readout.

## 1. Inputs (md5-gated at run -- both OK)
- fixture : eval/_local/gold_fixture_E25b.json  4a45f52883a802e8d8d1d5ff5d185bdb
- heldout : eval/_local/heldout_E17.jsonl       7e9fe030646d5671952e7a9fe9437e37
            classes {gold_backed:30, spoof_cuestripped_entitied:30, negctrl_common:15}; items=75
- probe   : run_E37_probe.py 15e694a6690a70b801431d64c0b5c368 (frozen substrate)
- model   : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli ;
            id2label={0:entailment,1:neutral,2:contradiction}; contradiction_idx=2, entailment_idx=0
- emit    : emit_E42scale_readout.py (this rung) ; from_finding=109/139 (E23 guard OK)
- op      : D_lambda=(n_con-1.0*n_ent)/|S| ; reject iff (pre_demoted OR D_lambda>=0.67)  [E40, frozen]

## 2. Anchor (VOID_ANCHOR guard -- reproduced byte-identical)
- composite fa_op = 0.0333  (spoof reject 29/30)        == E37 0.0333
- auth-only  fa   = 0.0714  (13/14)                     == E37 0.0714
- sec6 reconcile  = PASS (emit decision == E37 op label, all 30 spoof items)
- apply-step computes D_lambda(1.0) explicitly (not con_share): spoof reject 29/30 -> fa_op 0.0333.
  (boundset coincidence of D_0/D_1 verified pre-run; explicit D_1 confirms no scale-divergence masked.)

## 3. F1 -- rho posture (RESOLVED: INDEPENDENT)
- test    : spearman(D_lambda reject-signal, upstream_bind), one-sided, over auth-resolved items
            (non-null bind, both classes). upstream_bind = mean beff(B_lex,B_anchor) over the
            representative bound-subset S ; W frozen 0 -> beff == B_lex ; observable-only, oracle-clean.
- result  : rho = -0.5481 (n = 37). Bar = one-sided rho >= 0.95 VOID. NOT met.
- reading : not merely below bar -- NEGATIVE. Stronger upstream binding associates with a LOWER
            reject-signal (well-bound claims trend consensus-supported, not contradicted). D_lambda is
            measuring consensus over the bound set, NOT relabeling retrieval strength.
- verdict : INDEPENDENCE HOLDS -> E40 graduation NOT contaminated. The one-sided rho>=0.95 VOID guard
            (RHO_RECONCILE 4bb389b) is ENFORCED going forward and is cleanly satisfied.
- falsifier that would overturn: rho >= 0.95 on a wider held-out -> D_lambda collinear with retrieval
            -> reopen at E39 with the bind score regressed out. Not observed here.

## 4. F2 -- recall cap (RESOLVED: CAP_HOLDS, structural)
- recall  : 27/30 = 0.9000 under the frozen op, on the full-GOLD store.
- cap     : floor-pinned by the same 3 unrescuable golds (E40/E41): 2 noauth pre_demoted + 1 pure-
            consensus (ho_g12 n_ent=0 -> D=1.0). D_lambda cannot touch them by construction.
- at scale: because E25b IS full-GOLD, this recall IS the at-scale recall -- no larger store exists to
            degrade it. Cap is STRUCTURAL, not a small-sample artifact. == E40/E41, confirmed.
- verdict : CAP_HOLDS (recall >= 0.90, <=3 rejected golds). Recovery of those 3 is a DIFFERENT organ
            (E42 noauth-channel), gated on the cap -- which holds -> recovery is OPTIONAL for v1.

## 5. Fork (resolved + named)
CAP_HOLDS. F1 independent + F2 cap structural at full-GOLD ->
  -> verifier-v1 FREEZE path: D_lambda=(n_con-n_ent)/|S| @ tau=0.67, pre_demote channel, one-sided
     rho>=0.95 VOID guard. fa_op 0.0333 / recall 0.9000 on full-GOLD.
  -> NEXT: fold provenance-verifier SPEC (AUDIT a602c41 D1-D6 vs SPEC d9c33937eb1b2fe6f30977f2514e00af).
     FOUNDER fold -- gated AFTER this cap-at-scale (now satisfied). PARKED on Tommy.

## 6. Reproducibility
Bundle onto_E42_runpod.zip: emit_E42scale_readout.py + run_E37_probe.py + gold_retrieve.py +
semantic_retrieve.py + verify_E16.py + the 2 gated fixtures. Run from extract dir with env paths
(ONTO_RETRIEVE_FLOOR=0.45, E39_FIXTURE/E39_HELDOUT/E42_READOUT/E42_REGION). Deterministic (eval mode,
no sampling); anchor reproduction is the version-drift guard (transformers logit drift would trip
VOID_ANCHOR -- did not).

## 7. Artifacts
- reports/E42scale_region.json   : aggregate verdict (no per-item content; git).
- reports/gate_E42scale.log      : run stdout (gate markers; git).
- eval/_local/E42scale_readout.json : 7-field per-item readout (LOCAL only, gitignored).
- emit_E42scale_readout.py        : committed alongside this report.
