# PRE_REGISTER_E37 -- SET-CONSISTENCY veto over the bound candidate SET (the per-candidate organ class is DONE)

STATUS: FROZEN pre-data. No fixture/model touched at authoring. Run = pack v82 (TYPE C, RunPod). Commit PAIRED at run.

## 0 NORTH STAR / PIVOT
NORTH STAR: a grounded verifier whose discipline is external to the substrate. The reject organ is one rung.
PIVOT (pre-registered at E35/E36 sec6): the PER-CANDIDATE organ class is CLOSED. Evidence chain E29-E36:
- E29: gold contradiction tail = retrieval MISBINDING under an ANY-CANDIDATE veto (each premise faithful to its
  OWN source, contradicting a claim about a DIFFERENT co-surfaced source).
- E34/E34b: binding-veto (con>=C AND B>=B_floor), B=lexical -> reject-only ceiling fa 0.1667.
- E35: accept-rescue (entailment lift) -> fa_op 0.0667 but bf-band TRIVIAL (2 pts, liftoff 0). TWO_ORGAN_KNIFE_EDGE.
- E36: anchored binding B=(1-W)lex+W*anchor does NOT lift the bf-band; W MONOTONE HURTS. ROOT: spoof class is
  `entitied` -> surface anchors bind spoofs as readily as the gold-tail. VERDICT BINDING_EXHAUSTED [FALSIFIER].
  => per-candidate binding is EXHAUSTED as the floor-lifting lever. Do NOT re-attempt a per-candidate sharpen.

E37 is a STRUCTURALLY DIFFERENT verifier: CROSS-SOURCE CONSISTENCY over the bound candidate SET, not per-candidate.

## 1 LEVER (SET-level consistency statistic)
DERIVATION (why SET-level): a gold-tail driver (ho_g05/g12/g08, con>=0.99) is FAITHFUL to its OWN source but
CONTRADICTS a claim about a DIFFERENT co-surfaced source -> its contradiction is a LONE, misbound candidate while
the true source corroborates/is neutral. A spoof's bound source AUTHORITATIVELY contradicts it and NO bound source
entails it -> the contradiction is the SET CONSENSUS. The discriminating signal is the SHAPE of the
contradiction/entailment distribution OVER the bound set, NOT any single candidate (E36 closed that).

Over the bound subset S of a claim (candidates with b_eff = (1-W)*B_lexical + W*B_anchor >= B_floor, scope-filtered;
W FROZEN 0 in E37 -> b_eff == B_lexical byte-identical):
    n_con     = #{ c in S : con_c >= C }          (contradictors at threshold C)
    n_ent     = #{ c in S : ent_c >= A }          (entailers at threshold A -- INHERITED accept channel)
    con_share = n_con / |S|                        (CONSENSUS measure ; observable ; |S|>=1 on the auth path)
    set_veto  = (n_con >= 1) AND (n_ent == 0) AND (con_share >= P)

P = consensus-share threshold (the NEW selection axis). A LONE contradictor among corroborating/neutral candidates
(con_share < P) is SPARED regardless of its own con magnitude or B -- that is the cross-source-consistency organ,
structurally OUTSIDE per-candidate space. Two corroboration channels, both observable:
  (i) NEUTRALITY: a non-contradicting bound candidate lowers con_share -> a lone contradictor is spared at P>0.
  (ii) ENTAILMENT: any bound entailer (ent>=A) sets n_ent>=1 -> kills the veto (E36 accept-rescue, INHERITED).

## 2 REGRESSION ANCHOR (mandatory; E28-K / E35-A / E36-W discipline, one more rung)
P=0 => con_share >= 0 is ALWAYS true => set_veto == (n_con>=1) AND (n_ent==0) == the EXACT E36 per-candidate
any-veto (accept-rescue). Therefore:
- VOID_SET_REGRESSION unless the op-point over (A_GRID x observed C x observed B_floor) at P=0, W=0 reproduces the
  E36/E35 op fa 0.0667 (E36_OP_FA) within SET_REG_TOL 0.02 (clean-superset).
- UNIT-PROOF (label-level, stronger than the metric anchor): at P=0 the SET veto LABEL is BYTE-IDENTICAL to the E36
  reference `reject and not accept` for EVERY (item x C x A x B_floor x scope) grid point. Asserted at runtime AND
  proven at design time on synthetic sets (320000 checks, 0 mismatches).
INHERITED anchors (byte-identical, P defaults 0 in all of them):
- B_floor=0, A=+inf, scope=any -> deberta bare scope=any fa 0.2333 (VOID_DEGENERACY else).
- A=+inf -> E34b reject-only op fa 0.1667 (VOID_ACCEPT_REGRESSION else).
- W=0 -> E35 TWO_ORGAN op fa 0.0667 (VOID_BINDING_REGRESSION else; numerically coincident with P=0 at this rung).

## 3 FROZEN SUBSTRATE + GRIDS (byte-identical from run_E36 @070e526, md5 2c85e848d05e213fc86fe763ad49dfb9)
FROZEN byte-identical (verified by AST body-equality): _ce_load, ce_scores, ce_entail, idx-from-id2label,
binding_score (lexical), _content_tokens, _anchor_tokens, anchor_score, md5, spearman, candidates_with_cosine,
precompute_item. The cosine rho VOID-guard (rho>=0.95) + S1 cosine diagnostics, the from_finding counter, the E30
ordering guard, fixture/heldout loaders, the C=+inf baseline path -> UNTOUCHED. NO new model. NO cosine in any
PRIMARY predicate (scope=any is cosine-free; the margin reported-arm inherits E36's cosine-neighborhood, unchanged).
W AXIS FROZEN OFF: W_GRID = (0.0,) -- pre-registered consequence of E36 BINDING_EXHAUSTED (W monotone hurts). Keeps
the sweep 4-D (P x A x B_floor x C), same order as E36.
FROZEN grids (pre-data): P_GRID = (0.0, 0.20, 0.26, 0.34, 0.50, 0.67, 0.75, 1.00) -- spans con_share breakpoints at
small |S| (1/5,1/4,1/3,1/2,2/3,3/4,1). A_GRID [0..1 step 0.05] + A=+inf anchor. B_floor grid = observed lexical B.
C grid = observed contradiction values. S2_GRID, B_FLOOR_GRID, MARGIN_GRID, S2 band bars -> inherited unchanged.
fixtures (md5-gated at RUN): gold_fixture_E25b.json 4a45f52883a802e8d8d1d5ff5d185bdb ;
heldout_E17.jsonl 7e9fe030646d5671952e7a9fe9437e37.

## 4 ORACLE-CLEAN (pre-data)
con_share reads ONLY observable per-candidate con/ent (computed from observable (claim, premise) text by the FROZEN
scorers) + the observable bound-set size |S|. It NEVER conditions on the held-out true class label or any per-class
quantity (AST-verified: no ['class'] / B*_CLASS read on the veto/SET path). P swept over a FROZEN coarse grid.
Op-selection peeks ONLY recall feasibility (B2 >= 0.90), never fa, never per-class, never the bf-band -- the same
discipline that caught the E28 per-class-C leak pre-data. SELECTOR tie-break BYTE-IDENTICAL to E36 minus the dead W
axis, with LOWEST-P appended last: P>0 is selected ONLY if it strictly lowers min-fa or widens the C-band; P=0 wins
all ties -> exact E36 reproduction at the degenerate point. The per-P bf-band lift is REPORTED-ONLY (feeds the
falsifier fork), never the op-selection.

## 5 TRUST GATES (else VOID) -- evaluated in order
VOID_BASELINE_MISMATCH (C=+inf fa not ~0.467) | VOID_RHO (spearman(con,cos)>=0.95) | VOID_DEGENERACY (0.2333) |
VOID_ACCEPT_REGRESSION (A=+inf != 0.1667) | VOID_BINDING_REGRESSION (W=0 != 0.0667) |
VOID_SET_REGRESSION (P=0 != 0.0667) | VOID_RECALL_UNUSABLE (no op holds B2>=0.90).

## 6 VERDICT FORKS (operative; read scope=any fa_op, P swept, vs gate 0.10 + bf-band@chosen-P + best-over-P)
- SET_CONSISTENCY_LEVER  : fa_op <= 0.10 AND B2 >= 0.90 AND bf-band@chosen-P NON-TRIVIAL (>=3 B_floor pts clear).
    -> cross-source consistency lifts the bf-band off the floor. GRADUATE -> verifier-integration
       (rho 0.95-vs-0.50 reconcile, full-GOLD scale). TOMMY GO REQUIRED.
- SET_CONSISTENCY_KNIFE_EDGE : fa_op <= 0.10, bf-band@chosen-P trivial, BUT some P lifts it (best-over-P >= 3).
    -> directionally right, insufficient -> a different SET statistic / richer corroboration signal (design, next).
- SET_EXHAUSTED [FALSIFIER] : fa_op <= 0.10 but NO P lifts the bf-band.
    -> the SET-consistency organ is EXHAUSTED. FALSIFIER FIRES: the per-instance heldout fixture is likely the
       ceiling. ESCALATE -> richer retrieval / multi-source corroboration corpus, OR re-examine heldout construction.
- VOID_* -> trust gate failed -> reconcile, re-run.
FALSIFIER (stated): if NO P over the frozen (A, B_floor, C) sweep clears fa<=0.10 AND B2>=0.90 with a NON-TRIVIAL
bf-band, the SET-consistency organ is FALSIFIED. (The metric is leak-honest: a fork cleared only by spoof rescues is
caught by fa itself, since rescued spoofs ARE false-accepts.) Forks FROZEN pre-data.

## 7 DELIVERABLES + DESIGN GATE + MANIFEST
DELIVERABLES: run_E37_probe.py + reports/PRE_REGISTER_E37.md (this file, FROZEN md5 recorded in pack v82) +
reports/E37_vs_E36.diff. Files placed UNCOMMITTED; commit PAIRED at the E37 RUN (pack v82, TYPE C, RunPod).
DESIGN GATE (all PASS at authoring):
- py_compile OK ; ASCII-only (0 non-ASCII bytes).
- diff isolates ONLY the SET statistic + its sweep-threading ; 11 frozen scorers/loaders AST-byte-identical ;
  baseline/rho/loaders untouched ; primary scope=any veto cosine-free.
- unit-proof: SET OFF-SWITCH (P=0) == per-candidate any-veto, BYTE-IDENTICAL (320000 synthetic checks, 0 mismatch;
  runtime assert wired). P-monotone (raising P only spares) verified. Lone-contradictor SPARE + consensus VETO
  mechanism demonstrated on constructed sets.
- oracle-leak check PASS (AST: no class-label / per-class read on the veto/SET path).
- sec6 forks frozen pre-data.
RUN COMMAND (pack v82): python run_E37_probe.py  (defaults: --out reports/report_E37.md ; fixture/heldout md5-gated).
