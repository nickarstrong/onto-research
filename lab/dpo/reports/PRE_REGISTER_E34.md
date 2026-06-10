# PRE_REGISTER_E34

experiment : E34 -- REFRAME the per-candidate contradiction-veto reject task
type       : TYPE A DESIGN (pre-registration). No run, no eval, no data this session.
base       : run_E32_probe.py @ git 435d62f (E33 run). run_E34 = copy-with-declared-zones of this file.
model      : INHERITED from run_E32, UNCHANGED -- CE_MODEL default = MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-
             ling-wanli (the E33 ANLI head). NLI-swap family is EXITED (E33): E34 holds the SCORER fixed and changes
             the reject TASK (adds a binding gate). bart-large-mnli scope=any 0.0667 is a CROSS-MODEL comparison bar,
             NOT the running model. contradiction_idx read from id2label (single, asserted), never hardcoded.
fixtures   : gold_fixture_E25b.json md5 4a45f52883a802e8d8d1d5ff5d185bdb ; heldout_E17.jsonl md5 7e9fe030646d5671952e7a9fe9437e37
             (LOCAL/gitignored, md5-gated at E35 run; not seen this session).
status     : FROZEN. md5 of this file recorded in the E34 readout = the E35 contract. No edit after freeze.

--------------------------------------------------------------------------------
## 0 DERIVATION (why this lever -- not a choice)

E33 falsified "NLI model class is the ceiling": ANLI-hardened DeBERTa-v3-large scored fa 0.1667 -- WORSE than
bart-large-mnli 0.0667 on the same fixture. A bigger/adversarial NLI head cannot fix the defect. => NLI-swap
family EXHAUSTED. The constraint is the reject TASK, not the scorer.

E29 located the defect: the gold contradiction tail is RETRIEVAL MISBINDING under an ANY-CANDIDATE veto. Each
tail premise is FAITHFUL to its OWN source while contradicting a claim about a DIFFERENT co-surfaced source.
The wrong-source candidate carries high contradiction and vetoes a gold claim it should never have scored ->
gold falsely demoted -> recall floor forces C up -> spoofs leak -> fa rises.

E31 falsified the naive binding fix (veto SCOPE = rank-top1): top1 LOSES non-top1 spoof rejections, fa
0.0667 -> 0.2333. Retrieval RANK is NOT the binding signal.

=> E34 lever: gate the veto to candidates BOUND to the claim's subject by an OBSERVABLE binding signal that is
NOT retrieval rank. The binding gate sits UPSTREAM of the contradiction veto: a wrong-source (unbound) candidate
is excluded from the veto, so it can no longer falsely demote the gold claim.

--------------------------------------------------------------------------------
## 1 LEVER

Binding score B(candidate, claim) in [0,1], OBSERVABLE TEXT ONLY:
  B = lexical subject-overlap between the claim string and the candidate's premise content (the source's finding
  text already used as the NLI premise; falls back to the source string when finding is empty). Concretely:
  containment overlap of stopword-stripped, lowercased, alphanumeric content tokens --
      B = |tokens(claim) INTERSECT tokens(premise)| / |tokens(claim)|   (0 if claim has no content tokens).
  B is topical (shared subject/entities), ORTHOGONAL to the NLI contradiction signal (logical opposition):
  a wrong-source candidate can score HIGH contradiction yet LOW B (different subject). That orthogonality is
  what the gate exploits. B conditions ONLY on (claim string, candidate premise text). It NEVER reads the
  held-out true class label, the gold/spoof tag, or any per-class quantity (oracle-leak gate, sec 4).

VETO CONDITION (replaces the E32 cos<=K gate):
  a candidate vetoes  iff  P(CON) >= C  AND  B(candidate, claim) >= B_floor
  scope stays = ANY over the BOUND candidate subset only (candidates with B >= B_floor).

SWEEP:
  - primary lever swept: B_floor over B_FLOOR_GRID (replaces the E28 cosine-K sweep; cosine FALSIFIED E28).
  - C inherited from run_E32 sweep range (S2_GRID + observed C unchanged). The new axis is B_floor, not C.

--------------------------------------------------------------------------------
## 2 BARS + DEGENERACY ANCHOR

  bart-large-mnli scope=any   fa = 0.0667   CROSS-MODEL bar (what plain-best looked like; E26 op point, later
                                            shown knife-edge E27). NOT reproduced by E34 (E34 runs deberta).
  deberta scope=any (E33)     fa = 0.1667   the running model's plain veto -> the bar E34 must BEAT, and the
                                            DEGENERACY anchor below.

DEGENERACY ANCHOR (asserted, the one reproduce-assert under E34):
  B_floor = 0 admits all candidates (B >= 0 always true) => veto reduces to (P(CON)>=C) under scope=any =>
  run_E32's plain deberta veto. At B_floor = 0 the probe MUST reproduce fa 0.1667 (E33). Pass => the binding
  gate is a CLEAN SUPERSET that collapses to the known operating point at the floor. Fail => VOID_DEGENERACY.

ANCHOR-REPURPOSE (hard): under the new lever 0.0667 and 0.1667 are COMPARISON bars, not reproduce-asserts (except
the 0.1667 degeneracy assert at B_floor=0). The verdict-fork block is REWRITTEN to sec 6 (a bare "change the lever
line" mis-fires the old gate -- E32 lesson).

--------------------------------------------------------------------------------
## 3 METRIC DISCIPLINE

  - Verdict reads GATE fa = max-over-candidates false-accept rate. NOT sep (p50). sep does NOT predict
    robustness (E25b 0.084 -> 0.008).
  - B2 = gold recall on the bound subset (>= 0.90; enforced by op-point feasibility, RECALL_FLOOR).
  - reject_share + bf-band reported for robustness; band non-triviality IS a verdict input (sec 6).

--------------------------------------------------------------------------------
## 4 ORACLE-LEAK GATE (pre-data, on paper)

ADMISSIBLE   : B reads claim string + candidate premise text (observable at inference).
INADMISSIBLE : B reads the held-out true class label, the gold/spoof tag, or any per-class quantity.
RULE         : any per-class binding term = oracle leak -> REJECT before freeze (E28 per-class C was a leak,
               caught pre-data). B is computable on a single (claim, candidate) pair with no class knowledge.
CHECK (passes): containment overlap of content tokens uses only the two text strings. No label, no tag, no
               per-class statistic enters B. PASS on paper.

--------------------------------------------------------------------------------
## 5 VOID GUARDS (carry; trip -> VOID, not a result)

  - BASELINE SANITY: no-veto (C=+inf) MUST reproduce fa 0.467 (model-INDEPENDENT). Fail -> VOID_BASELINE.
  - from_finding > 0 (manipulation fired; not VOID-by-construction, E23). 0 -> VOID_NOFIRE.
  - rho VOID-guard frozen 0.95 on spearman(contradiction, cosine) (UNCHANGED; cos retained for this guard).
    advisory |rho|<0.50 reported SEPARATELY (CONFLICT carried, reconcile at integration). Trip -> VOID_RHO.
  - DEGENERACY: B_floor=0 reproduces deberta scope=any fa 0.1667 (sec 2). Fail -> VOID_DEGENERACY.

--------------------------------------------------------------------------------
## 6 FALSIFIABLE FORKS (verdict at E35)

  BINDING_IS_THE_LEVER   : fa_op <= 0.10 AND B2 >= 0.90 over a NON-TRIVIAL B_floor band (>= S2_BAND_MIN_POINTS
                           B_floor grid points clear the joint gate; not a single point -- avoids E27 knife-edge).
                           => reject-task reframe works; proceed to robustness + verifier-integration (Tommy GO).
  BINDING_HELPS_PARTIAL  : 0.10 < fa_op < 0.1667. Beats deberta-plain, does not clear the gate. Directionally
                           right, insufficient alone -> combine with a second organ (design, next).
  BINDING_NOT_THE_LEVER  : fa_op >= 0.1667. No gain over E33. The per-candidate contradiction-veto organ is
                           EXHAUSTED even reframed -> escalate to a DIFFERENT reject/accept organ class
                           (e.g. accept/entailment-lift three-way), TYPE A.
  VOID_*                 : any sec 5 guard trips -> discard run, fix wiring, re-run. Not a verdict.

--------------------------------------------------------------------------------
## 7 BUILD CONTRACT FOR run_E34_probe.py (STEP 2; enforced at diff-proof)

NO model change (CE_MODEL inherited from run_E32, untouched). DECLARED ZONES = the ONLY edits vs run_E32 @ 435d62f:
  Z1  binding_score(claim, premise) helper (containment overlap, stopword-stripped) + per-candidate B in
      precompute_item; resolution tuple ("auth", [(cos, sc, B), ...]). cos RETAINED (rho/S1/ordering unchanged).
  Z2  item_label_at_C: unpack 3-tuples; veto condition -> (sc >= C AND B >= B_floor); scope=any over bound subset.
      top1/margin arms updated to 3-tuple + B gate (reported arms; verdict reads scope=any).
  Z3  B_floor sweep: K_GRID -> B_FLOOR_GRID; K_obs -> B_obs (observed B values); the swept-axis threading
      (s2_band_at_K/s2_perK/s3/select_op) reads B_floor in place of cosine-K. C-grid sweep within band unchanged.
  Z4  degeneracy anchor: explicit eval at B_floor=0 must reproduce deberta scope=any fa 0.1667 (sec 2) -> flag.
  Z5  bf-band non-triviality + verdict-fork block rewrite -> sec 6 forks (anchor-repurpose).
  Z6  --out default = reports/report_E34.md (NOT a frozen-report path; no clobber).
  Z7  comments only (header rationale, zone markers).

FORBIDDEN: any change to grid CONSTANTS unrelated to the B_floor axis, thresholds, substrate, fixtures, the
  baseline C=+inf path, from_finding counter, the rho guard (spearman on cosine), contradiction_idx-from-id2label,
  fixture/heldout loaders, the ordering guard, S1 cosine diagnostics. run_E28 ANY-veto footgun (line 153) is a
  DIFFERENT file -- untouched. semantic_retrieve FLOOR default 0.55!=0.45 -- env-override asserted, untouched.

PROOF: py_compile OK ; ASCII-only ; produce reports/E34_vs_E32.diff ; diff shows ONLY Z1-Z7 (CLEAN).
  run_E34_probe.py + E34_vs_E32.diff ON DISK UNCOMMITTED -> commit PAIRED with report_E34 at E35.

--------------------------------------------------------------------------------
## 8 DESIGN-GATE PASS CRITERIA (this session)

  [x] PRE_REGISTER_E34 frozen: falsifiable forks (sec 6) + oracle-leak gate (sec 4) explicit + md5 recorded.
  [x] binding signal OBSERVABLE; oracle-leak check passes on paper before any data.
  [x] run_E34_probe.py py_compile OK + ASCII + E34_vs_E32.diff CLEAN (Z1-Z7 only).
  [x] on-disk uncommitted per protocol ; pack v73 routes to E35.
  NO data touched, NO model loaded, NO eval run.

FREEZE: md5 of this file = recorded in the E34 readout. This file is the E35 contract.
