# PRE_REGISTER_E34b

experiment : E34b -- RE-ANCHOR the binding-gate reject task to the honest cosine-FREE baseline
type       : TYPE A DESIGN (pre-registration). No run, no eval, no data this session.
base       : run_E34_probe.py (on disk, UNCOMMITTED). run_E34b = copy-with-declared-zones of this file
             (5 declared edits only; diff-proof CLEAN). PRE_REGISTER_E34 (md5 91ae26c51ee794fa6f5c94497d109be0)
             is FROZEN and UNTOUCHED; E34b is a NEW frozen file, not an edit of E34.
model      : INHERITED from run_E32, UNCHANGED -- CE_MODEL default = MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-
             ling-wanli (the E33 ANLI head). NLI-swap family is EXITED (E33): E34b holds the SCORER fixed and changes
             ONLY the degeneracy/beat anchor (the LEVER is unchanged from E34). bart-large-mnli scope=any 0.0667 is a
             CROSS-MODEL comparison bar, NOT the running model. contradiction_idx read from id2label (single, asserted).
fixtures   : gold_fixture_E25b.json md5 4a45f52883a802e8d8d1d5ff5d185bdb ; heldout_E17.jsonl md5 7e9fe030646d5671952e7a9fe9437e37
             (LOCAL/gitignored, md5-gated at the E34b run; not seen this session).
status     : FROZEN. md5 of this file recorded in the E34b readout = the E34b-run contract. No edit after freeze.

WHY E34b (v74 RECONCILE): E34 ran as VOID_DEGENERACY -- at B_floor=0 (gate off) the probe produced fa 0.2333, NOT
the 0.1667 it was anchored to reproduce. v74 (TYPE B) reconciled this: the 0.1667 anchor was NEVER bare scope=any --
the E33 deberta op-point veto carried (con>=C AND cos<=K=0.5066235661506653) (report_E32.md:17-18, run_E32_probe.py:173).
The cosine gate spared 2 of 3 gold-tail drivers, holding fa at 0.1667. The honest COSINE-FREE bare scope=any baseline
= 0.2333. Since the E34 lever is lexical binding B (cosine FALSIFIED at E28, NOT re-introduced), the correct degeneracy
+ beat anchor is 0.2333. E34b re-anchors to 0.2333. The VOID was the ANCHOR, not the lever -- lever (sec 1) intact.

--------------------------------------------------------------------------------
## 0 DERIVATION (why this lever -- not a choice)

E33 falsified "NLI model class is the ceiling": ANLI-hardened DeBERTa-v3-large scored fa 0.1667 -- WORSE than
bart-large-mnli 0.0667 on the same fixture. A bigger/adversarial NLI head cannot fix the defect. => NLI-swap
family EXHAUSTED. The constraint is the reject TASK, not the scorer.
  (NOTE v74: that deberta 0.1667 op-point was cos<=K=0.5066 CONTAMINATED -- it is a historical E33 op-point, NOT
   the bare cosine-free baseline. The bare baseline = 0.2333. See sec 2. This does not change the E33 verdict
   (deberta still WORSE than bart), only the anchor E34b reproduces.)

E29 located the defect: the gold contradiction tail is RETRIEVAL MISBINDING under an ANY-CANDIDATE veto. Each
tail premise is FAITHFUL to its OWN source while contradicting a claim about a DIFFERENT co-surfaced source.
The wrong-source candidate carries high contradiction and vetoes a gold claim it should never have scored ->
gold falsely demoted -> recall floor forces C up -> spoofs leak -> fa rises.

E31 falsified the naive binding fix (veto SCOPE = rank-top1): top1 LOSES non-top1 spoof rejections, fa
0.0667 -> 0.2333. Retrieval RANK is NOT the binding signal.

=> E34 lever (UNCHANGED at E34b): gate the veto to candidates BOUND to the claim's subject by an OBSERVABLE binding
signal that is NOT retrieval rank. The binding gate sits UPSTREAM of the contradiction veto: a wrong-source (unbound)
candidate is excluded from the veto, so it can no longer falsely demote the gold claim.

--------------------------------------------------------------------------------
## 1 LEVER (UNCHANGED from E34 -- the VOID was the anchor, not this)

Binding score B(candidate, claim) in [0,1], OBSERVABLE TEXT ONLY:
  B = lexical subject-overlap between the claim string and the candidate's premise content (the source's finding
  text already used as the NLI premise; falls back to the source string when finding is empty). Concretely:
  containment overlap of stopword-stripped, lowercased, alphanumeric content tokens --
      B = |tokens(claim) INTERSECT tokens(premise)| / |tokens(claim)|   (0 if claim has no content tokens).
  B is topical (shared subject/entities), ORTHOGONAL to the NLI contradiction signal (logical opposition):
  a wrong-source candidate can score HIGH contradiction yet LOW B (different subject). That orthogonality is
  what the gate exploits. B conditions ONLY on (claim string, candidate premise text). It NEVER reads the
  held-out true class label, the gold/spoof tag, or any per-class quantity (oracle-leak gate, sec 4).

VETO CONDITION (replaces the E32 cos<=K gate; cosine NOT re-introduced at E34b):
  a candidate vetoes  iff  P(CON) >= C  AND  B(candidate, claim) >= B_floor
  scope stays = ANY over the BOUND candidate subset only (candidates with B >= B_floor).

SWEEP:
  - primary lever swept: B_floor over B_FLOOR_GRID (replaces the E28 cosine-K sweep; cosine FALSIFIED E28).
  - C inherited from run_E32 sweep range (S2_GRID + observed C unchanged). The new axis is B_floor, not C.

--------------------------------------------------------------------------------
## 2 BARS + DEGENERACY ANCHOR (RE-ANCHORED 0.1667 -> 0.2333, v74)

  bart-large-mnli scope=any   fa = 0.0667   CROSS-MODEL bar (what plain-best looked like; E26 op point, later
                                            shown knife-edge E27). NOT reproduced by E34b (E34b runs deberta).
  deberta bare scope=any      fa = 0.2333   the running model's plain COSINE-FREE veto -> the bar E34b must BEAT,
                                            and the DEGENERACY anchor below.

CONTAMINATION CORRECTION (the reason for the re-anchor):
  The E33-reported deberta op-point fa = 0.1667 was NOT bare scope=any. Its veto fired on (con>=C AND cos<=K),
  K=0.5066235661506653, C=0.978492021560669 (report_E32.md:17-18 ; predicate at run_E32_probe.py:173). The cosine
  gate excludes 2 of 3 gold-tail drivers (ho_g12 cos=0.5081, ho_g08 cos=0.6003 > K; ho_g05 cos=0.4801 <= K) -> golds
  spared -> B2 holds at low C -> 0.1667. Drop the cosine gate (as the cosine-FREE binding lever does at B_floor=0)
  and the bare scope=any baseline = 0.2333. The binding lever (sec 1) does NOT use cosine -> its degeneracy point
  is the cosine-free 0.2333, not the contaminated 0.1667. Anchoring to 0.1667 is what produced E34's VOID_DEGENERACY.

DEGENERACY ANCHOR (asserted, the one reproduce-assert under E34b):
  B_floor = 0 admits all candidates (B >= 0 always true) => veto reduces to (P(CON)>=C) under scope=any =>
  run_E32's COSINE-FREE plain deberta veto. At B_floor = 0 the probe MUST reproduce fa 0.2333 +/- ANCHOR_TOL(0.02).
  Pass => the binding gate is a CLEAN SUPERSET that collapses to the honest cosine-free operating point at the
  floor. Fail => VOID_DEGENERACY (if it STILL misfires, the confound is deeper than the reducer -> escalate, do
  NOT trust the lever reading).

ANCHOR-REPURPOSE (hard): under the binding lever 0.0667 and 0.2333 are COMPARISON bars, not reproduce-asserts
(except the 0.2333 degeneracy assert at B_floor=0). The contaminated 0.1667 is RETIRED as an anchor (kept only as
historical E33 provenance). The verdict-fork block is REWRITTEN to sec 6 (a bare "change the lever line" mis-fires
the old gate -- E32 lesson). HARD: cos<=K is NOT re-introduced into the veto predicate (E28 falsified cosine).

--------------------------------------------------------------------------------
## 3 METRIC DISCIPLINE (UNCHANGED)

  - Verdict reads GATE fa = max-over-candidates false-accept rate. NOT sep (p50). sep does NOT predict
    robustness (E25b 0.084 -> 0.008).
  - B2 = gold recall on the bound subset (>= 0.90; enforced by op-point feasibility, RECALL_FLOOR).
  - reject_share + bf-band reported for robustness; band non-triviality IS a verdict input (sec 6).

--------------------------------------------------------------------------------
## 4 ORACLE-LEAK GATE (pre-data, on paper) (UNCHANGED)

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
  - DEGENERACY: B_floor=0 reproduces deberta bare cosine-free scope=any fa 0.2333 +/- 0.02 (sec 2). Fail -> VOID_DEGENERACY.

--------------------------------------------------------------------------------
## 6 FALSIFIABLE FORKS (verdict at the E34b run)

  BINDING_IS_THE_LEVER   : fa_op <= 0.10 AND B2 >= 0.90 over a NON-TRIVIAL B_floor band (>= S2_BAND_MIN_POINTS
                           B_floor grid points clear the joint gate; not a single point -- avoids E27 knife-edge).
                           => reject-task reframe works; proceed to robustness + verifier-integration (Tommy GO).
  BINDING_KNIFE_EDGE     : fa_op <= 0.10 but bf-band TRIVIAL (single B_floor point, E27-class fragility) ->
                           tighten the binding signal / widen the grid before claiming the lever.
  BINDING_HELPS_PARTIAL  : 0.10 < fa_op < 0.2333. Beats bare cosine-free scope=any, does not clear the gate.
                           Directionally right, insufficient alone -> combine with a second organ (design, next).
  BINDING_NOT_THE_LEVER  : fa_op >= 0.2333. No gain over the bare cosine-free deberta baseline. The per-candidate
                           contradiction-veto organ is EXHAUSTED even reframed -> escalate to a DIFFERENT
                           reject/accept organ class (e.g. accept/entailment-lift three-way), TYPE A.
  VOID_*                 : any sec 5 guard trips -> discard run, fix wiring, re-run. Not a verdict.

--------------------------------------------------------------------------------
## 7 BUILD CONTRACT FOR run_E34b_probe.py (enforced at diff-proof)

NO model change (CE_MODEL inherited, untouched). NO lever change (binding gate sec 1 unchanged). DECLARED ZONES =
the ONLY edits vs run_E34_probe.py (the 5 re-anchor edits; emit reports/E34b_vs_E34.diff showing ONLY these):
  D1  DEBERTA_ANCHOR_FA : 0.1667 -> 0.2333 (bare cosine-free scope=any; the TRUE B_floor=0 degeneracy target).
  D2  degeneracy assert : reads DEBERTA_ANCHOR_FA -> auto-targets 0.2333 +/- ANCHOR_TOL(0.02). No logic edit.
  D3  verdict bands     : forks read DEBERTA_ANCHOR_FA -> BINDING_HELPS_PARTIAL = 0.10 < fa_op < 0.2333 ;
                          BINDING_NOT_THE_LEVER = fa_op >= 0.2333. GATE 0.10 + bf-band UNCHANGED. Inline band-text
                          literals 0.1667 -> 0.2333 (descriptive only; logic via constant).
  D4  --out default     : reports/report_E34.md -> reports/report_E34b.md (no clobber E34/E32/E30/E28).
  D5  comments/header + report title : re-anchor note + cite report_E32.md:17-18 K=0.5066 as the contamination
                          proof. Historical E33 op-point 0.1667 references RETAINED (sec0/contamination notes) --
                          NOT moved (they describe the contaminated number, not the anchor).

HARD: do NOT re-introduce the cos<=K gate (B is the ONLY lever; E28 falsified cosine). Do NOT edit run_E34/
  PRE_REGISTER_E34 in place. Do NOT change grid CONSTANTS, thresholds, substrate, fixtures, the C=+inf baseline
  path, from_finding counter, the rho guard, contradiction_idx-from-id2label, fixture/heldout loaders, the
  ordering guard, S1 cosine diagnostics. run_E28 ANY-veto footgun (line 153) is a DIFFERENT file -- untouched.

PROOF: py_compile OK ; ASCII-only ; reports/E34b_vs_E34.diff shows ONLY D1-D5 (CLEAN).
  run_E34b_probe.py + E34b_vs_E34.diff ON DISK UNCOMMITTED -> commit PAIRED with report_E34b at the run.

--------------------------------------------------------------------------------
## 8 DESIGN-GATE PASS CRITERIA (this session)

  [ ] PRE_REGISTER_E34b frozen: falsifiable forks (sec 6) + oracle-leak gate (sec 4) explicit + md5 recorded.
  [ ] re-anchor justified from primary source (report_E32.md:17-18 K=0.5066) -- contamination, not a choice.
  [ ] run_E34b_probe.py py_compile OK + ASCII + E34b_vs_E34.diff CLEAN (D1-D5 only); cos<=K NOT re-introduced.
  [ ] PRE_REGISTER_E34 UNTOUCHED (md5 91ae26c51ee794fa6f5c94497d109be0).
  [ ] on-disk uncommitted per protocol ; pack v76 routes to the E34b supervised run (TYPE C).
  NO data touched, NO model loaded, NO eval run.

FREEZE: md5 of this file = recorded in the E34b readout. This file is the E34b-run contract.
