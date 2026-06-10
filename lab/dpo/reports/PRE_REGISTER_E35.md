# PRE_REGISTER_E35

experiment : E35 -- SECOND ORGAN: entailment-lift ACCEPT rescue layered on the FROZEN E34b binding-veto REJECT
type       : TYPE A DESIGN (pre-registration). No run, no eval, no data this session.
base       : run_E34b_probe.py @ git 89975cb (md5 5a758f2071bf29a06e3d045602ea155f, TRUSTED; report_E34b committed).
             run_E35 = copy-with-declared-zones of this file (accept-arm zones A1-A10 only; diff-proof CLEAN).
             PRE_REGISTER_E34 (91ae26c51ee794fa6f5c94497d109be0) + PRE_REGISTER_E34b (703d80ef8d77b3c1a1ed817502917d10)
             are FROZEN and UNTOUCHED; E35 is a NEW frozen file, not an edit of either.
model      : INHERITED, UNCHANGED -- CE_MODEL default = MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli.
             NO new model. The accept arm reads the SAME head: contradiction_idx AND entailment_idx are BOTH read
             from id2label (single each, asserted), never hardcoded. bart 0.0667 = CROSS-MODEL bar (not the running model).
fixtures   : gold_fixture_E25b.json md5 4a45f52883a802e8d8d1d5ff5d185bdb ; heldout_E17.jsonl md5 7e9fe030646d5671952e7a9fe9437e37
             (LOCAL/gitignored, md5-gated at the E35 run; NOT seen this session).
status     : FROZEN. md5 of this file recorded in pack v78 = the E35-run contract. No edit after freeze.

WHY E35 (the E34b RESULT forces it): E34b (TRUSTED, committed 89975cb) proved the per-candidate contradiction-veto
REJECT organ CAPS at fa 0.1667 on this fixture. At the op-point (C=0.9914, B_floor=0.0833): 5/30 spoofs survive
(residual false-accept the veto cannot reach) and recall is held ONLY by the binding gate sparing the 3 gold-tail
drivers (ho_g05/g12/g08, con>=0.99, retrieval-MISBOUND -> low B -> excluded from veto). To demote the 5 survivors
you must lower C; but lowering C catches the gold-tail drivers too (they sit at con>=0.99) -> B2 drops below 0.90.
A pure-reject lever is EXHAUSTED at this ceiling. The next gain must come from the ACCEPT side. S3 reject_share 0.64
already confirmed the reject ORGAN (not coverage) owns the fa-reduction -> a second ORGAN, not a re-tuned reject, is
the structurally-necessary move.

--------------------------------------------------------------------------------
## 0 DERIVATION (why ENTAILMENT-LIFT -- not a choice)

The reject organ's residual false-accepts (5 surviving spoofs) cannot be reached by tightening C without breaking
recall, because gold and the soft spoofs both sit in the high-contradiction tail. The asymmetry the reject organ
does NOT exploit: a GOLD claim is ENTAILED by its correctly-bound authorized source; a SPOOF is CONTRADICTED by
its bound source and NOT entailed by any bound source. So the entailment signal on the BOUND subset is a positive
verifier of gold that the contradiction signal cannot supply. If gold is protected by its bound-source ENTAILMENT
rather than by keeping C high, C can be LOWERED -> the soft spoofs cross con>=C and are demoted -> while the gold
claims that newly cross are RESCUED by their bound entailment. Spoofs are not rescued (no bound source entails them).
The lift is oracle-clean (P(entailment) of (premise=source.finding, hyp=claim), observable text only) and reuses the
already-loaded head -> no new model, no held-out leak.

--------------------------------------------------------------------------------
## 1 LEVER (E35 three-way -- accept rescue layered on the FROZEN E34b reject)

Per authorized candidate the resolution now carries (cos, contradiction, ENTAILMENT, B). Over the BOUND subset
(candidates with B >= B_floor):
  REJECT(candidate)  iff  P(contradiction) >= C   AND  B >= B_floor   (FROZEN from E34b -- byte-identical predicate)
  ACCEPT(candidate)  iff  P(entailment)    >= A   AND  B >= B_floor   (NEW; A = entailment-lift threshold)

CLAIM label (accept-protective precedence -- the ONLY precedence under which the accept lets C tighten):
  effective_veto  =  (some bound candidate REJECTs)  AND  (no bound candidate ACCEPTs)
  label = UNVERIFIABLE if effective_veto else VERIFIED.
Item rollup UNCHANGED (any UNVERIFIABLE -> DEMOTE).

scope = 'any' over the BOUND subset (E35 PRIMARY). top1/margin are REPORTED arms (E31 falsified rank as the lever);
both reject AND accept use the same scope filter. ent direction = premise=source.finding / hyp=claim (SAME encoding
as the contradiction scorer; entailment_idx located from id2label).

SWEEP:
  - accept axis A swept over a FROZEN COARSE grid A_GRID = [0.00 .. 1.00] step 0.05 (bounds the 3rd selection axis
    -> tractable run). NOT observed values, to keep the (A x C x B_floor) selection feasible in pure Python.
  - C inherited from run_E32 sweep range (observed C). B_floor over the FROZEN B_FLOOR_GRID (E34b, unchanged).
  - A = +inf (accept OFF) is NOT in the sweep -- it is the regression anchor (sec 2).

--------------------------------------------------------------------------------
## 2 BARS + DEGENERACY ANCHORS

  bart-large-mnli scope=any         fa = 0.0667   CROSS-MODEL bar (not the running model; not reproduced).
  deberta bare scope=any            fa = 0.2333   INHERITED B_floor=0,A=+inf degeneracy anchor (E34b, sec2).
  E34b reject-only op               fa = 0.1667   the BAR E35 must BEAT, and the ACCEPT-OFF regression anchor.
  GATE                              fa <= 0.10    PASS target for the COMBINED organ.

TWO DEGENERACY ANCHORS (both asserted; either fail -> VOID):
  (I)  INHERITED -- B_floor = 0 AND A = +inf admits all candidates, accept off -> three-way collapses to deberta
       bare cosine-free scope=any. MUST reproduce fa 0.2333 +/- ANCHOR_TOL(0.02). Fail -> VOID_DEGENERACY.
  (II) ACCEPT-OFF REGRESSION -- A = +inf (ent>=+inf never true -> accept never fires) makes the three-way EXACTLY
       the E34b reject-only label. The op-point over (C_obs, B_obs) at A=+inf MUST reproduce the E34b reject-only
       op fa 0.1667 +/- ACCEPT_TOL(0.02). This is the accept analog of E28's K=+inf -> E27 scalar regression. It
       proves the accept arm is a CLEAN SUPERSET: at A=+inf E35 == E34b bit-for-bit on the decision. Fail ->
       VOID_ACCEPT_REGRESSION (the accept wiring perturbed the frozen reject path -> do NOT trust any E35 reading).

HARD: cosine is NOT re-introduced into either predicate (E28 falsified cosine separability). cos is retained ONLY
for the rho VOID-guard + S1 diagnostics + the reported margin arm. The accept lever is ENTAILMENT, not cosine.

--------------------------------------------------------------------------------
## 3 METRIC DISCIPLINE (UNCHANGED from E34b)

  - Verdict reads GATE fa = max-over-candidates false-accept rate. NOT sep (p50). (E25b sep 0.084->0.008 -> sep
    does not predict robustness.)
  - B2 = gold recall on the bound subset (>= 0.90; enforced by op-point feasibility, RECALL_FLOOR).
  - reject_share + bf-band reported for robustness; bf-band non-triviality IS a verdict input (sec 6).
  - LEAK-HONEST BY CONSTRUCTION: a spoof WRONGLY rescued by accept IS a false-accept -> it raises fa directly.
    So a TWO_ORGAN_LEVER that "clears" the gate only by rescuing spoofs cannot exist -- fa would not clear. S3
    reports n_spoof_rescued separately for transparency, but the verdict needs no extra leak gate: fa already pays.

--------------------------------------------------------------------------------
## 4 ORACLE-LEAK GATE (pre-data, on paper)

ADMISSIBLE   : A is a SINGLE scalar threshold on P(entailment) computed from (claim string, candidate premise text),
               both observable at inference. Same admissibility as C on contradiction.
INADMISSIBLE : A reads the held-out true class label, the gold/spoof tag, or ANY per-class quantity; A_GRID chosen
               post-hoc from fa; a per-class A.
RULE         : any per-class accept term = oracle leak -> REJECT before freeze (E28 per-class C was exactly this
               leak, caught pre-data). A is computable on a single (claim, candidate) pair with no class knowledge.
CHECK (passes): A_GRID is FROZEN coarse [0..1 step 0.05] pre-data. op-point selection peeks ONLY recall feasibility
               (B2>=0.90), NEVER fa, NEVER a per-class statistic. n_by_entailment / n_spoof_rescued read class
               labels for ATTRIBUTION/diagnostics ONLY (post-hoc), exactly as B1/B2/B3 already do -- the DECISION
               (item_label_at_C) never reads a label. PASS on paper.

--------------------------------------------------------------------------------
## 5 VOID GUARDS (carry; trip -> VOID, not a result)

  - BASELINE SANITY: no-veto (C=+inf) MUST reproduce fa 0.467 (model-INDEPENDENT). Fail -> VOID_BASELINE.
  - from_finding > 0 (manipulation fired; not VOID-by-construction, E23). 0 -> VOID_NOFIRE.
  - rho VOID-guard frozen 0.95 on spearman(contradiction, cosine) (UNCHANGED; cos retained for this guard).
    advisory |rho|<0.50 reported SEPARATELY (CONFLICT carried, reconcile at integration). Trip -> VOID_RHO.
  - DEGENERACY (I): B_floor=0,A=+inf reproduces deberta bare scope=any fa 0.2333 +/- 0.02. Fail -> VOID_DEGENERACY.
  - ACCEPT REGRESSION (II): A=+inf reject-only op reproduces E34b 0.1667 +/- 0.02. Fail -> VOID_ACCEPT_REGRESSION.

--------------------------------------------------------------------------------
## 6 FALSIFIABLE FORKS (verdict at the E35 run)

  TWO_ORGAN_LEVER        : fa_op <= 0.10 AND B2 >= 0.90 over a NON-TRIVIAL bf-band (>= S2_BAND_MIN_POINTS B_floor
                           grid points clear the joint gate; not a single point -- avoids E27 knife-edge).
                           => the combined accept+reject organ clears the gate -> robustness sweep +
                           verifier-integration (rho 0.95-vs-0.50 reconcile, full-GOLD scale). TOMMY GO REQUIRED.
  TWO_ORGAN_KNIFE_EDGE   : fa_op <= 0.10 but bf-band TRIVIAL (single point, E27-class) -> tighten binding/accept
                           or widen the grid before claiming the lever.
  ACCEPT_HELPS_PARTIAL   : 0.10 < fa_op < 0.1667. Beats the reject-only ceiling, does NOT clear the gate.
                           Directionally right, insufficient -> a third signal or a different binding observable.
  ENTAILMENT_LIFT_EXHAUSTED (THE FALSIFIER) : fa_op >= 0.1667. The accept arm gives NO gain over reject-only over
                           the FROZEN (A, C, B_floor) grids. => entailment-lift does NOT rescue -> the per-candidate
                           accept/reject organ CLASS is DONE -> pivot to a structurally different verifier
                           (cross-source CONSISTENCY over the candidate SET, not per-candidate). TYPE A.
  VOID_*                 : any sec 5 guard trips -> discard run, fix wiring, re-run. Not a verdict.

EXPLICIT FALSIFIER (one line): if at NO (A in A_GRID, C in C_obs, B_floor in B_FLOOR_GRID) does the combined organ
reach fa <= 0.10 AND B2 >= 0.90 AND a non-trivial bf-band, the entailment-lift accept organ is FALSIFIED as the
lever and the per-candidate organ class is escalated out.

--------------------------------------------------------------------------------
## 7 BUILD CONTRACT FOR run_E35_probe.py (enforced at diff-proof)

NO model change (CE_MODEL inherited, untouched). The FROZEN reject path is byte-identical: reject predicate
(con>=C AND B>=B_floor), binding lever B, cosine rho VOID-guard, S1 cosine diagnostics, from_finding counter,
ordering guard, contradiction_idx-from-id2label, fixture/heldout loaders, the C=+inf baseline path, the 0.2333
anchor. DECLARED ZONES = the ONLY edits vs run_E34b_probe.py (emit reports/E35_vs_E34b.diff showing ONLY these):

  A1  header rationale (comments only) -- the E35 second-organ block.
  A2  constants : A_GRID (frozen coarse), E34B_REJECT_OP_FA=0.1667, ACCEPT_TOL=0.02, ENT_DIR_NOTE.
  A3  _ce_load  : locate entailment_idx from id2label (single, asserted), alongside contradiction_idx. ce_scores
                  RETURN ARITY UNCHANGED (3-tuple) -- _ent_idx is a module global; ce_scores byte-identical.
  A4  ce_entail : NEW sibling of ce_scores reading _ent_idx; separate forward pass; ce_scores untouched.
  A5  precompute_item : add ents = ce_entail(query, prems); resolution tuple (cos, con, B) -> (cos, con, ENT, B).
                  The diag/decorr(rho) collection is byte-identical (reads con, cos). docstring note updated.
  A6  item_label_at_C : add A param (default +inf = accept off); unpack 4-tuple; reject (FROZEN predicate) + accept
                  (ent>=A AND bound); effective_veto = reject AND NOT accept. A=+inf degenerates to E34b binary.
  A7  metrics_at_C : thread A.
  A8  s2_band_at_bfloor + s2_perBfloor_summary : thread A (read at op-point A).
  A9  s3_attribution : thread A; wire (c) n_by_entailment = GOLD items rescued by accept (toggle A +inf->op_A);
                  add n_spoof_rescued leak counter (spoofs wrongly rescued). reject noauth/veto split unchanged.
  A10 main : (a) 4-tuple unpacks in ordering guard + observed grids; (b) A_sweep = A_GRID; (c) select_op gains A
                  axis (A x B_floor x C; tie-break adds highest-A = safest accept; returns A); (d) ADD accept-off
                  regression anchor (A=+inf reject-only op == 0.1667); INHERIT the B_floor=0,A=+inf 0.2333 anchor
                  byte-identical; (e) thread chosen_A through op/S2/S3/margin; (f) verdict-fork REWRITE to the sec6
                  forks + VOID_ACCEPT_REGRESSION; (g) --out default reports/report_E35.md; report text -> E35.

FORBIDDEN: re-introducing cos<=K into any predicate; editing run_E34b / PRE_REGISTER_E34 / PRE_REGISTER_E34b in
  place; changing grid CONSTANTS unrelated to the A axis, thresholds, substrate, fixtures, the C=+inf baseline path,
  from_finding counter, the rho guard, contradiction_idx-from-id2label, fixture/heldout loaders, the ordering guard,
  S1 cosine diagnostics. run_E28 ANY-veto footgun (line 153) is a DIFFERENT file -- untouched. semantic_retrieve
  FLOOR default 0.55!=0.45 -- env-override asserted (run_E35 line ~5), untouched.

PROOF (already produced this design session): py_compile OK ; ASCII-only ; reports/E35_vs_E34b.diff shows ONLY
  A1-A10 (CLEAN, audited: reject predicate byte-identical, no cos<=K, no loader/rho/baseline drift) ; pure-logic
  unit proof of (A=+inf == E34b reject) + (accept rescues bound-entailed) + (spoof w/o bound-ent NOT rescued).
  run_E35_probe.py + E35_vs_E34b.diff ON DISK UNCOMMITTED -> commit PAIRED with report_E35 at the run.

COMPUTE NOTE (for the run): select_op is now a triple grid (|A_GRID|=21 x |C_obs| x |B_obs|) x metrics_at_C over
  ~139 items -> roughly 21x the E34b op-selection cost. Tractable on the RunPod A5000; size the run accordingly
  (single supervised pass). A=+inf anchors are separate cheap loops.

--------------------------------------------------------------------------------
## 8 DESIGN-GATE PASS CRITERIA (this session)

  [x] PRE_REGISTER_E35 frozen: falsifiable forks (sec 6) + EXPLICIT FALSIFIER + oracle-leak gate (sec 4) explicit + md5 in pack v78.
  [x] accept signal OBSERVABLE; oracle-leak check passes on paper before any data (A single scalar, frozen grid, no per-class).
  [x] run_E35_probe.py py_compile OK + ASCII + E35_vs_E34b.diff CLEAN (A1-A10 only); reject predicate byte-identical; cos<=K NOT re-introduced.
  [x] two degeneracy anchors stated (0.2333 inherited + 0.1667 accept-off regression) + matching VOID guards.
  [x] PRE_REGISTER_E34 + PRE_REGISTER_E34b UNTOUCHED.
  [x] on-disk uncommitted per protocol ; pack v78 routes to the E35 supervised run (TYPE C).
  NO data touched, NO model loaded, NO eval run.

FREEZE: md5 of this file = recorded in pack v78. This file is the E35-run contract.
