# PRE_REGISTER_E36

experiment : E36 -- ANCHORED-BINDING REPLACE: sharpen the binding observable B on the FROZEN E35 three-way.
type       : TYPE A DESIGN (pre-registration). No run, no eval, no data this session.
base       : run_E35_probe.py @ git bf19da1 (md5 40cbebf348075a3ffa7dbfaf4511bb2e, TRUSTED; report_E35 committed).
             run_E36 = copy-with-declared-zones of this file (binding zones Z1-Z10 only; diff-proof CLEAN, audited).
             PRE_REGISTER_E35 (8c719b0bdc88250165bce434c9652eea) is FROZEN and UNTOUCHED; E36 is a NEW frozen file,
             not an edit of it. The E35 three-way reject/accept predicate is inherited byte-identical.
model      : INHERITED, UNCHANGED -- CE_MODEL default = MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli.
             NO new model. contradiction_idx AND entailment_idx BOTH read from id2label (single each, asserted).
             The anchored binding B_anchor is a PURE-TEXT quantity (no model call). bart 0.0667 = CROSS-MODEL bar.
fixtures   : gold_fixture_E25b.json md5 4a45f52883a802e8d8d1d5ff5d185bdb ; heldout_E17.jsonl md5 7e9fe030646d5671952e7a9fe9437e37
             (LOCAL/gitignored, md5-gated at the E36 run; NOT seen this session).
status     : FROZEN. md5 of this file recorded in pack v80 = the E36-run contract. No edit after freeze.

WHY E36 (the E35 RESULT forces it): E35 (TRUSTED, committed bf19da1) = TWO_ORGAN_KNIFE_EDGE. The accept arm RESCUED
the reject organ to fa_op 0.0667 (clears gate 0.10, beats reject-only 0.1667), c-leak 0, reject_share 0.857 -- a real
combined organ. BUT the bf-band was TRIVIAL: only 2 B_floor points cleared the gate, B2 lift-off 0.0000, the op sat
at B_floor=0.0. The knife-edge is in the BINDING-FLOOR dimension: the 3 gold-tail drivers (ho_g05 cos0.48, ho_g12
cos0.51, ho_g08 cos0.60; con>=0.99) are legitimately bound to their source.finding but carry LOW lexical overlap, so
the lexical B cannot rise above ~0.05 without dropping them -> B_floor is pinned to the floor. The C-band is already
WIDE (0.08 / 17 pts), so a grid re-tune cannot fix it. The fix is a SHARPER binding OBSERVABLE that scores the 3
drivers HIGH while leaving spoofs low -> B_floor lifts off the floor -> a non-trivial bf-band.

--------------------------------------------------------------------------------
## 0 DERIVATION (why ANCHORED binding -- not a choice)

The gold-tail drivers bind to their authorized source by SHARED NAMED ANCHORS -- the specific number, the quoted
span, the proper-noun/acronym entity that names the same finding -- even where bag-of-content-token overlap is low
(paraphrase, reordering, function-word dilution). Lexical containment under-counts exactly this binding: a claim and
its source.finding can share the load-bearing anchors (a statistic, an entity) while sharing few ordinary content
tokens. So an anchor-restricted containment is a STRICTLY sharper binding signal on the bound subset: it raises B for
the anchor-sharing gold-tail without raising it for candidates that merely share generic vocabulary. If the surviving
soft spoofs do NOT share the claim's anchors with their bound source, their anchored B stays low -> B_floor can rise
to exclude them from the veto's bound subset while still admitting the gold-tail. The anchor is oracle-clean (surface
text of claim + premise only) and needs no model call. Whether the spoof class (cue-stripped, ENTITIED) also carries
shared anchors is the run's open question -- and the explicit falsifier (sec 6).

--------------------------------------------------------------------------------
## 1 LEVER (E36 anchored-binding REPLACE -- on the FROZEN E35 three-way)

Per authorized candidate the resolution now carries (cos, contradiction, entailment, B_lexical, B_anchor). The
EFFECTIVE binding used by the (UNCHANGED) reject/accept predicate is a mix over a swept weight W:

  B(W)  =  (1 - W) * B_lexical  +  W * B_anchor          W in W_GRID (anchor-mix weight, the NEW 4th axis)

  B_lexical = |content_tokens(claim) INTERSECT content_tokens(premise)| / |content_tokens(claim)|   (E35, UNTOUCHED)
  B_anchor  = |anchors(claim) INTERSECT anchors(premise)| / |anchors(claim)|   (NEW; 0.0 if claim has no anchors)
  anchors(text) = { number-like tokens ; content tokens inside quoted spans ; CamelCase/ACRONYM entity tokens },
                  kind-tagged so a number never collides with an entity. Deterministic, ASCII, no regex, no model.

Over the BOUND subset (candidates with B(W) >= B_floor):
  REJECT(candidate)  iff  P(contradiction) >= C   AND  B(W) >= B_floor   (FROZEN E35 predicate -- operator byte-identical)
  ACCEPT(candidate)  iff  P(entailment)    >= A   AND  B(W) >= B_floor   (FROZEN E35 predicate -- operator byte-identical)
  effective_veto = (some bound candidate REJECTs) AND (no bound candidate ACCEPTs)   (accept-protective, UNCHANGED)
  label = UNVERIFIABLE if effective_veto else VERIFIED. Item rollup UNCHANGED (any UNVERIFIABLE -> DEMOTE).

scope = 'any' over the BOUND subset (E36 PRIMARY); top1/margin are REPORTED arms (UNCHANGED). The ONLY change vs E35
is the DEFINITION of the binding B that feeds `B >= B_floor`; the contradiction/entailment thresholds and precedence
are byte-identical.

SWEEP:
  - W swept over a FROZEN COARSE grid W_GRID = [0.00, 0.25, 0.50, 0.75, 1.00] (bounds the 4th selection axis ->
    tractable run). W=0 (anchor OFF) is NOT a free point -- it is the REGRESSION anchor (sec 2). W=1 = pure anchor.
  - A inherited FROZEN A_GRID [0..1 step 0.05]; A=+inf anchor (accept off). C observed. B_floor over FROZEN B_FLOOR_GRID.
  - SELECTOR (one declared refinement, tied to the new axis): op-point tie-break is BYTE-IDENTICAL to E35 (widest
    C-band -> lowest C -> highest B_floor -> highest A) with LOWEST-W appended as the FINAL key. Consequence: the
    anchor (W>0) is selected ONLY if it STRICTLY lowers min-fa or widens the C-band; W=0 wins all ties -> the W=0 op
    reproduces E35 exactly. The per-W bf-band lift is a REPORTED-ONLY diagnostic (sec 6 fork), never op-selection.

--------------------------------------------------------------------------------
## 2 BARS + DEGENERACY ANCHORS

  bart-large-mnli scope=any         fa = 0.0667   CROSS-MODEL bar (not the running model; not reproduced).
  deberta bare scope=any            fa = 0.2333   INHERITED B_floor=0,A=+inf,W=0 degeneracy anchor.
  E34b reject-only op               fa = 0.1667   INHERITED A=+inf,W=0 accept-off regression anchor.
  E35 TWO_ORGAN op                  fa = 0.0667   the E36 BINDING-REGRESSION anchor (W=0) AND the bar E36 must not regress.
  GATE                              fa <= 0.10    PASS target for the COMBINED organ under the sharpened binding.

THREE DEGENERACY ANCHORS (all asserted; any fail -> VOID):
  (I)   INHERITED -- B_floor=0, A=+inf, W=0 -> admits all candidates, accept off, lexical binding -> deberta bare
        scope=any. MUST reproduce fa 0.2333 +/- ANCHOR_TOL(0.02). Fail -> VOID_DEGENERACY.
  (II)  INHERITED -- A=+inf, W=0 -> three-way == E34b reject-only. Op over (C_obs,B_obs) MUST reproduce 0.1667 +/-
        ACCEPT_TOL(0.02). Fail -> VOID_ACCEPT_REGRESSION.
  (III) NEW BINDING REGRESSION -- W=0 -> B(0) = (1-0)*B_lexical + 0*B_anchor == B_lexical BYTE-IDENTICALLY (IEEE:
        x*1.0 exact for finite x; 0.0*finite == 0.0). The three-way collapses to the EXACT E35 path. The op over
        (A_GRID, C_obs, B_obs) at W=0 MUST reproduce the E35 TWO_ORGAN op fa 0.0667 +/- BIND_REG_TOL(0.02). This is
        the binding analog of E28 K=+inf->E27 and E35 A=+inf->E34b: it proves the sharpened binding is a CLEAN
        SUPERSET (at W=0, E36 == E35 bit-for-bit on the decision). Fail -> VOID_BINDING_REGRESSION (the anchor wiring
        perturbed the frozen path -> do NOT trust any E36 reading).

HARD: cosine is NOT introduced into either predicate (E28 falsified cosine separability). cos is retained ONLY for
the rho VOID-guard + S1 diagnostics + the inherited reported margin arm. The binding lever is lexical+anchor, not cosine.

--------------------------------------------------------------------------------
## 3 METRIC DISCIPLINE (UNCHANGED from E35)

  - Verdict reads GATE fa = max-over-candidates false-accept rate. NOT sep (p50). (E25b sep 0.084->0.008.)
  - B2 = gold recall on the bound subset (>= 0.90; enforced by op-point feasibility, RECALL_FLOOR).
  - reject_share + bf-band reported; bf-band non-triviality (at chosen W) IS a verdict input (sec 6).
  - LEAK-HONEST BY CONSTRUCTION: a spoof wrongly admitted by a sharpened B (anchor falsely binds a spoof) IS a
    false-accept -> it raises fa directly. A lever that "lifts the bf-band" only by binding spoofs cannot clear the
    gate -- fa pays. S3 n_spoof_rescued reported for transparency; the verdict needs no extra leak gate.

--------------------------------------------------------------------------------
## 4 ORACLE-LEAK GATE (pre-data, on paper)

ADMISSIBLE   : B_anchor and W are computed from (claim string, candidate premise text) only, both observable at
               inference. anchors() reads surface tokens (numbers, quoted spans, CamelCase/ACRONYM) -- no class tag.
               W is a SINGLE scalar mix weight, swept over a FROZEN grid; same admissibility class as A and C.
INADMISSIBLE : an anchor set conditioned on the held-out true class; a per-class W; W_GRID chosen post-hoc from fa;
               an anchor extractor that peeks at the gold/spoof label.
RULE         : any per-class binding term = oracle leak -> REJECT before freeze (E28 per-class C was exactly this
               leak, caught pre-data). B(W) is computable on a single (claim, candidate) pair with no class knowledge.
CHECK (passes): W_GRID FROZEN coarse pre-data; anchor functions take only (claim, premise)/(text) -- proven by the
               design-session unit-proof (signatures carry no class/label arg). op-point selection peeks ONLY recall
               feasibility (B2>=0.90), NEVER fa, NEVER a per-class statistic, NEVER the bf-band (the bf-band is read
               AFTER selection, for the verdict only). The per-W bf-band diagnostic reads class labels for
               ATTRIBUTION only, exactly as B1/B2/B3 do -- the DECISION (item_label_at_C) never reads a label. PASS.

--------------------------------------------------------------------------------
## 5 VOID GUARDS (carry; trip -> VOID, not a result)

  - BASELINE SANITY: no-veto (C=+inf) MUST reproduce fa ~0.467 (model-INDEPENDENT). Fail -> VOID_BASELINE_MISMATCH.
  - from_finding > 0 (manipulation fired; not VOID-by-construction, E23). 0 -> VOID (assert in main).
  - rho VOID-guard frozen 0.95 on spearman(contradiction, cosine) (UNCHANGED). advisory |rho|<0.50 reported
    SEPARATELY (CONFLICT carried, reconcile at integration). Trip -> VOID_RHO.
  - DEGENERACY (I):  B_floor=0,A=+inf,W=0 reproduces 0.2333 +/- 0.02. Fail -> VOID_DEGENERACY.
  - ACCEPT REGRESSION (II): A=+inf,W=0 reproduces 0.1667 +/- 0.02. Fail -> VOID_ACCEPT_REGRESSION.
  - BINDING REGRESSION (III): W=0 op reproduces 0.0667 +/- 0.02. Fail -> VOID_BINDING_REGRESSION.

--------------------------------------------------------------------------------
## 6 FALSIFIABLE FORKS (verdict at the E36 run)

Read scope=any fa_op (accept ON, W swept) vs GATE 0.10, the bf-band at the CHOSEN W, and the best-over-W bf-band
diagnostic. Because E36's sweep INCLUDES W=0, its min-fa <= E35's 0.0667 always -> fa cannot regress; the live
question is purely whether the SHARPENED binding lifts the bf-band off the floor.

  TWO_ORGAN_LEVER        : fa_op <= 0.10 AND B2 >= 0.90 AND the bf-band AT THE CHOSEN W is NON-TRIVIAL (>=
                           S2_BAND_MIN_POINTS B_floor grid points clear the joint gate; not a single point). =>
                           the anchored binding lifts the bf-band off the floor -> robustness sweep +
                           verifier-integration (rho 0.95-vs-0.50 reconcile, full-GOLD scale). TOMMY GO REQUIRED.
  TWO_ORGAN_KNIFE_EDGE   : fa_op <= 0.10, bf-band at chosen W TRIVIAL, BUT best-over-W bf-band NON-TRIVIAL (some W in
                           W_GRID lifts it, though the conservative op-selector did not pick that W because it did
                           not also lower fa / widen the C-band). => latent lever -> tighten W_GRID / promote the
                           bf-band into the selector / widen the grid before claiming the lever. (design, next.)
  BINDING_EXHAUSTED (THE FALSIFIER) : fa_op <= 0.10 but NO W in W_GRID yields a non-trivial bf-band (best-over-W
                           trivial). => the anchored binding does NOT lift the floor -> per-candidate binding is
                           EXHAUSTED as the lever -> PIVOT to a structurally different verifier: cross-source
                           CONSISTENCY over the candidate SET (not per-candidate). TYPE A.
  ANCHOR_BINDING_HELPS_PARTIAL : 0.10 < fa_op < 0.1667 -- kept for completeness; CANNOT occur while W=0 is in the
                           sweep (E36 is a clean superset of E35's 0.0667). If observed -> a wiring fault -> inspect.
  VOID_*                 : any sec 5 guard trips -> discard run, fix wiring, re-run. Not a verdict.

EXPLICIT FALSIFIER (one line): if at NO W in W_GRID does the combined organ reach fa<=0.10 AND B2>=0.90 AND a
non-trivial bf-band, the per-candidate anchored binding is FALSIFIED as the floor-lifting lever, and the
per-candidate organ class is escalated out to cross-source consistency over the SET.

--------------------------------------------------------------------------------
## 7 BUILD CONTRACT FOR run_E36_probe.py (enforced at diff-proof)

NO model change (CE_MODEL inherited, untouched). The FROZEN three-way is byte-identical: reject predicate operator
(con>=C), accept predicate operator (ent>=A), accept-protective rescue precedence, scope='any', the lexical
binding_score function, ce_scores / ce_entail, the cosine rho VOID-guard, S1 cosine diagnostics, from_finding
counter, ordering guard, contradiction_idx/entailment_idx-from-id2label, fixture/heldout loaders, the C=+inf
baseline path, the 0.2333 and 0.1667 anchors. DECLARED ZONES = the ONLY edits vs run_E35_probe.py (emit
reports/E36_vs_E35.diff showing ONLY these):

  Z1  header rationale (comments only) -- the E36 anchored-binding block.
  Z2  constants : W_GRID (frozen coarse incl. 0.0), E35_OP_FA=0.0667, BIND_REG_TOL=0.02, ANCHOR_NOTE.
  Z4  _anchor_tokens(text) + anchor_score(claim,premise) : NEW siblings of _content_tokens/binding_score; lexical
                  binding_score UNTOUCHED. Deterministic, ASCII, no regex, no model, oracle-clean.
  Z5  precompute_item : add ancs = [anchor_score(query,p)...]; resolution tuple (cos,con,ent,B) -> (cos,con,ent,
                  B_lex,B_anchor). diag/decorr(rho) collection byte-identical (reads con,cos). docstring note.
  Z6  item_label_at_C : add W param (default 0.0 = anchor off); unpack 5-tuple; effective b = (1-W)*B_lex+W*B_anchor;
                  reject/accept predicates use b (operators FROZEN). W=0 => b == B_lex byte-identical => E35 path.
  Z7  metrics_at_C : thread W.
  Z8  s2_band_at_bfloor + s2_perBfloor_summary : thread W (read at op-point W).
  Z9  s3_attribution : thread W (op + rescue toggles); C=+inf baseline calls stay W=0 (reject False regardless).
  Z10 main : (a) 5-tuple unpacks in ordering guard + observed grids (B_obs from LEXICAL b -> B_floor grid == E35);
                  (b) W_sweep = W_GRID; (c) select_op gains W axis (W x A x B_floor x C; tie-break appends LOWEST-W;
                  returns W); (d) ADD binding-regression anchor (W=0 op == 0.0667) + INHERIT the 0.2333 and 0.1667
                  anchors byte-identical (W=0); (e) thread chosen_W through op/S2/S3/margin; (f) verdict-fork REWRITE
                  to the sec6 forks + VOID_BINDING_REGRESSION + per-W bf-band diagnostic (best-over-W); (g) --out
                  default reports/report_E36.md; report text -> E36 + W lines.

FORBIDDEN: re-introducing cos<=K into any predicate; editing run_E35 / PRE_REGISTER_E35 in place; changing grid
  CONSTANTS unrelated to the W axis, the contradiction/entailment thresholds, substrate, fixtures, the C=+inf
  baseline path, from_finding counter, the rho guard, idx-from-id2label, loaders, the ordering guard, S1 cosine
  diagnostics, the lexical binding_score. semantic_retrieve FLOOR default 0.55!=0.45 -- env-override asserted, untouched.

PROOF (produced this design session): py_compile OK ; ASCII-only (0 non-ASCII bytes) ; reports/E36_vs_E35.diff shows
  ONLY Z1-Z10 (CLEAN, audited: reject/accept operators byte-identical, no new cos<=K, no loader/rho/baseline drift) ;
  W=0 BINDING-REGRESSION unit-proof: (1-0)*B_lex + 0*B_anchor == B_lex byte-identical over a 10-pair battery + 81
  IEEE corners, anchor scores in [0,1], anchor signatures carry no class/label arg (oracle-clean). run_E36_probe.py +
  E36_vs_E35.diff + PRE_REGISTER_E36.md ON DISK UNCOMMITTED -> commit PAIRED with report_E36 at the E36 run.

COMPUTE NOTE (for the run): select_op is a 4-axis grid (|W_GRID|=5 x |A_GRID|=21 x |C_obs| x |B_obs|) x metrics_at_C
  over ~139 items -> ~5x the E35 op-selection cost (which was ~21x E34b). NLI precompute is UNCHANGED (one forward
  pass per candidate); the anchor precompute is pure-CPU. Tractable on the RunPod A5000; size the run accordingly.
