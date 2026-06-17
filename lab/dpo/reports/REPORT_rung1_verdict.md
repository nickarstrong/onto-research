# REPORT -- RUNG-1 verdict: self-refinement yield-or-floor (propose-side, gate-2 ACCEPTANCE)

date    : 2026-06-17
plane   : GREENFIELD PROPOSE-SIDE / RUNG-1 (self-refinement safety gate, DESIGN_propose_side_v1 sec5)
status  : CLOSED. Headline safety gate MET ; L4-transfer sub-question banked as untested (honest).
home    : onto-research/reports (dateable priority + reproducibility). PUBLIC-SAFE: method + result + limits
          only. NO held-out prompts / claims / DOIs / labels (3.2 ; those stay LOCAL-ONLY).
binds   : DESIGN_propose_side_v1.md (rung-1 pre-registration, FROZEN sec5) ; STANDARD_grounded_verifier_v1.md
          (FROZEN instrument, a886378). No frozen bar relitigated or moved (R7).

--------------------------------------------------------------------------------
## 0 WHAT RUNG-1 TESTED

Does the FROZEN grounded verifier falsely ACCEPT the live proposer's organic fabrications into the
would-be self-refinement (RFT) pool? Accept-precision is the safety gate (a passed fabrication
contaminates weights, cardinal R7) ; yield is reported, never gated. This closes the verifier's own
disclosed limit #5 (STANDARD sec9): the live-proposer fabrication/wrong-binding rate over n>30 had
never been measured (the prior e2e was a single planted 4-item draw).

## 1 SETUP

- Proposer : FROZEN base (no adapter, no GOLD), greedy, 1 (claim, DOI) per prompt.
- Inputs   : N=120 held-out grounding prompts (LOCAL-ONLY), disjoint topics. 0 abstentions emitted
             (the base minted a DOI for every prompt).
- Ground truth : Founder-judged CLEAN/DIRTY per proposal (LOCAL-ONLY, R7), DOIs resolved vs Crossref.
             119 DIRTY (41 non-resolving / 77 wrong-bound / 1 non-supporting) ; 1 CLEAN. n_dirty >= 30.
- Instrument : FROZEN intake (run_step2b_intake, organ byte-unchanged ; STANDARD). L1 existence +
             title-match, L2 retraction, L4 GOLD-consensus contradiction-veto, tier chain. CALLED, not edited.

## 2 RESULT

fa_live = 0 / 119 DIRTY = 0.000.

The frozen verifier ACCEPTED ZERO fabrications. Mechanism (all rejections at the provenance layer L1):
  - 41 rejected: DOI does not resolve (T4_NONRESOLVE).
  - 79 rejected: DOI resolves but the real title does not match the claim (T4_L1_MISMATCH).
  - 0 proposals reached L4. The CLEAN proposal was also rejected at L1 (yield = 0 / 1).

## 3 VERDICT (against FROZEN G-RUNG1, sec5.3)

- Headline gate fa_live <= 0.10 : MET (0.000). The verifier absorbs no live fabrication -> self-refinement
  is SAFE on this substrate re pool contamination (the cardinal R7 concern is satisfied).
- VOID guard (sec5.4) FIRES on the L4-transfer sub-question: every rejection is a provenance decision
  (resolve / title), so rho(reject, upstream-bind) -> 1. The L4 contradiction-veto was NOT exercised
  (0 L1-survivors). Therefore curated->live transfer of L4 precision remains UNMEASURED. This is the
  pre-registered banked outcome, NOT a failure and NOT a gate to tune.

## 4 HONEST LIMITS (R2/R7)

- Title input: the proposer emits (claim, DOI) with no asserted title. L1 ran with expected_title = claim
  (strict), which also rejects topically-correct clean citations -> yield (0/1) is NOT a clean read.
  A faithful L4-transfer test needs the proposer to ASSERT the cited title (emission-contract gap, logged
  for the next rung). This does NOT affect the safety result: every DIRTY proposal is rejected regardless
  of title input (non-resolving fail existence ; wrong-bound fail real-title match).
- Interpretation: the live base proposer is too crude to produce L1-passing fabrications -> the provenance
  layer alone catches 100%. The deeper layers (L2/L4/L5) are latent insurance that earn their keep only
  once the proposer improves (cites real, correct, on-topic papers). That improvement is the next stage.

## 5 CLOSE + NEXT

Cheap-verifier rung CLOSED: the verifier does not let fabrications into a self-training pool.
NEXT = self-refinement RFT loop. First task there: elicit even a handful of L1-passing CLEAN outputs to
seed the pool (the base currently yields ~0). The L4-transfer measurement becomes live only once the
proposer is good enough to pass L1 -- at which point a TITLE-asserting emission re-enables the wrong-bind
check and L4 is finally exercised.
