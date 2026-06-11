# PRE_REGISTER_E38  -- corpus-vs-construction disambiguator  [FROZEN]

## 0 META
- id          : E38
- type        : TYPE A DESIGN -> no-GPU CPU probe (binding-count ONLY; NO NLI eval, NO model load)
- parent      : E37 SET_EXHAUSTED [FALSIFIER], 88489f8. fa_op 0.0333 best-on-ladder, bf-band FLAT at all P.
- closes      : per-candidate ORGAN CLASS (binding E36 + set-consistency E37). E38 does NOT add a lever.
- purpose     : disambiguate WHY E37's set-veto cannot lift the bf-band:
                (A) CONSTRUCTION ceiling -- heldout has no multi-source SET to consense over (|S| ~ 1), OR
                (B) STATISTIC wrong     -- a multi-source SET exists (|S| healthy) but consensus-share is the wrong stat.
- frozen-on   : design close, pack v83. RUN is pack v84 (no-GPU; CPU-local, likely no pod).

## 1 GOAL (one line)
Measure the bound-candidate-set size |S| distribution (pre-NLI, binding-only) over the FROZEN E37 op-point,
plus the ground-truth n_sources-per-claim, to decide CONSTRUCTION-CEILING vs STATISTIC-WRONG BEFORE spending on a
multi-source corroboration corpus. This is a diagnostic, not a rung -- it produces NO fa/bf number and NO verdict
on the ladder metric.

## 2 INPUTS (md5-gated at RUN; mismatch = STOP)
- heldout_E17.jsonl        : 7e9fe030646d5671952e7a9fe9437e37   (items / claims)
- gold_fixture_E25b.json   : 4a45f52883a802e8d8d1d5ff5d185bdb   (candidate pool + class label + n_sources sidemap)
- binding (frozen)         : IMPORTED from run_E37_probe.py (15e694a6690a70b801431d64c0b5c368 as committed).
- NO new fixture. NO regenerated data. Reuse only the md5-gated artifacts above.

## 3 FROZEN BINDING (verbatim E37; imported, NOT reimplemented)
- B = lexical, floor 0.45, top_k 5.   (identical to E34b/E36/E37 binding step.)
- DESIGN RULE: the probe IMPORTS E37's binding callable. It MUST NOT contain a second copy of the binding logic.
  Reimplementation is the exact drift vector the regression anchor exists to catch; importing makes the replay
  byte-identical BY CONSTRUCTION, which is strictly stronger than a numeric re-derivation.
- If E37 does not expose its binding as an importable callable, the v84 RUN first refactors run_E37_probe.py to
  expose it -- BEHAVIOR-PRESERVING ONLY, verified by the sec-5 regression anchor (byte-identical |S| per item at P=0).
  No behavior change is permitted under the refactor.

## 4 OBSERVABLES (read ONLY observable signals; class is for REPORTING grouping, never selection)
- |S| per item              : size of the lexically-bound candidate set (floor 0.45, top_k 5), pre-NLI.
- |S| distribution overall  : p10 / p50 / p90 / max, and share[|S| <= 1].
- |S| distribution per CLASS : gold_backed / spoof_cuestripped_entitied / negctrl_common  (grouping only).
- n_sources-per-claim       : independent gold sources backing each gold claim, from the fixture sidemap
                              (distribution over gold_backed items: p10 / p50 / p90 / max, share[n_sources <= 1]).
- counts                    : n_items total, n per class (provenance / sanity).

## 5 REGRESSION ANCHOR + VOID
- ANCHOR (mandatory, byte-identical): at the P=0 op-point (set-veto OFF), the per-item bound set
  { item_id -> sorted(bound_candidate_ids) } MUST equal the E36/E37 bound set.
  Enforcement, in priority order:
    (a) binding callable's module path resolves to run_E37_probe.py (imported, not local) -> identity by construction; AND
    (b) if reports/E37_boundset.json (or the E37 report's bound-set dump) is present, assert byte-identical per item.
  If neither identity can be established -> VOID (do not emit a readout; STOP and reconcile).
- VOID conditions (any -> the run is VOID, no |S| readout trusted):
  * any input md5 != sec-2 manifest;
  * binding logic re-coded locally (module path of the binding callable != run_E37_probe.py);
  * P=0 bound set perturbed vs E36/E37;
  * n_items != E37 n_items (item set changed under us).

## 6 FORK  (FALSIFIABLE -- READ BEFORE ANY DATA IS SEEN)
Decision is on |S| (n_sources corroborates the same branch; it does not override |S|):
- BRANCH A -- CONSTRUCTION CEILING CONFIRMED:
    trigger  : p50(|S|) <= 1  OR  share[|S| <= 1] high (>= 0.50).
    meaning  : no multi-source set exists to consense over -> SET-consistency was UN-TESTABLE by construction.
    verdict  : E37 falsifier upheld as a CORPUS verdict, not a lever verdict.
    next rung: v85 designs a multi-source corroboration corpus build (N >= 3 independent gold sources per claim);
               GOLD enters as the source pool (first GOLD touch on this ladder).
- BRANCH B -- STATISTIC WRONG:
    trigger  : p50(|S|) >= 3  (a real multi-source set exists) AND E37 still flat.
    meaning  : the corpus carries a set; consensus-share over the same bound subset is the wrong cross-source stat.
    next rung: v85 designs an ALTERNATIVE cross-source statistic -- NOT consensus-share over the same bound subset.
- INDETERMINATE band (1 < p50(|S|) < 3 and share[|S|<=1] < 0.50): report as INDETERMINATE; do NOT force a branch.
    v85 then narrows with n_sources as the tie-breaker (n_sources p50 <= 1 -> lean A; >= 3 -> lean B) and states the
    residual ambiguity in one line. No fabricated branch selection.

## 7 INTEGRITY
- oracle-leak guard (E28 lesson): selection / binding / |S| are computed CLASS-BLIND over ALL items. Class label is
  joined in ONLY at the reporting/aggregation step (per-class grouping). Nothing conditions on class, fa, or bf-band.
- VOID-by-construction guard (E23 lesson): assert n_items > 0 and at least one gold_backed item present before
  emitting; an empty bound pass is VOID, not a clean "|S| ~ 1" readout.
- no fixture mutation: E25b / E17 are read-only, md5-gated; the probe never writes them.
- no NLI: this probe loads NO model. Pure binding-count + sidemap read. CPU-only.

## 8 OUT (deliverables; what the v84 RUN produces)
- run_E38_Sdist_probe.py  -> on disk at lab\dpo\ (UNCOMMITTED at v83 close; paired + committed at v84 run).
- RUN (v84) emits: reports\report_E38.md (|S| readout + branch verdict) + reports\gate_E38.log
  + reports\E38_Sdist.json (machine readout). Pre-register frozen here is the read-before-data contract for sec6.
