# DESIGN -- Greenfield Model Propose-Side v1 (the autonomous-entity front, design-open)

status   : v1 DESIGN. The construction that runs ON TOP of the frozen grounded provenance verifier.
           sec 0-4 = design (durable). sec 5 = rung-1 PRE-REGISTRATION (FROZEN before any data, R7).
date     : 2026-06-17
plane    : GREENFIELD MODEL PROPOSE-SIDE (NORTH STAR). NEW front. The verifier is built-AGAINST,
           not relitigated (keystone sec3 ; STANDARD_grounded_verifier_v1 sec12 FREEZE MARKER).
home     : onto-research/reports (dateable priority + reproducibility). PUBLIC-SAFE: architecture +
           bars + falsifier only. NO held-out labels / DOIs / abstracts / bait / weights (3.2).
binds    : STANDARD_grounded_verifier_v1.md (md5 3626ddd9, FROZEN instrument) ;
           STRATEGY_verifier_keystone.md sec0/sec3 (NORTH STAR + gate-ladder) ;
           report_step2b.md / SPEC_verifier_v1.md (f7433706) (live intake contract).
           No bar in any bound artifact is reopened here.

--------------------------------------------------------------------------------
## 0 FRAME -- proposes/disposes split

NORTH STAR = a disciplined AUTONOMOUS entity on a FROZEN substrate + GOLD + R1-R18, where epistemic
discipline is enforced EXTERNALLY (keystone sec0). The verifier v1 (FROZEN) is the DISPOSES half:
it gates every citation emission through extract -> resolve+status -> contradiction-veto -> tier,
external to the weights (tier-independent). This document specifies the PROPOSES half: the substrate
that emits a claim + candidate source, shaped to enter the verifier's intake.

KEYSTONE (do not relitigate): NORTH STAR properties 1-4 (tier-independent discipline / self-learning /
initiative / knowledge-tiering) are all FUNCTIONS of the one grounded verifier. The propose-side adds
no new judge -- it adds an emitter and a loop that ride the frozen disposer. Faking the judge =
a fluent hallucinating "Entity" (keystone sec0 ; the E15 second-order-hallucination failure).

--------------------------------------------------------------------------------
## 1 WHAT PROPOSES (the emitter)

substrate : a FROZEN base model under an R1-R18 system prompt. Substrate identity (which base) is a
            BUILD-time choice, NOT a design parameter -- discipline is external, so the design is
            substrate-agnostic by construction (that is the whole NORTH STAR claim). On-disk proposer
            scaffolding already exists (data/proposer_prompts_v01.jsonl ; make_proposals_v01.py ;
            run_full_turn_s2b_v0.py ; loop_e2e_v0.py) -- rung-1 BUILD reuses it, does not rebuild.

emission contract : on a prompt, the substrate emits ONE of
  (a) a CHECKABLE proposal = (claim_text, candidate_source_locator)  -- the formal-locator channel
      the verifier intake consumes (claim + a DOI / resolvable identifier) ; OR
  (b) an explicit ABSTENTION = "[no verified source]"  -- R4 behaviour when it cannot ground.
The substrate NEVER mints a locator to satisfy form (R7 cardinal). Abstention is first-class and is
NOT a verifier input (nothing to dispose) -- it is counted, not scored.

--------------------------------------------------------------------------------
## 2 HOW A PROPOSAL ENTERS THE FROZEN VERIFIER (intake = step2b, verbatim contract)

A (claim, candidate-DOI) proposal enters the FROZEN intake unchanged (STANDARD sec5 step2 + step2b ;
run_step2b_intake.py md5 d93a64e3 -- a thin adapter that reimplements NO organ):

  proposal (claim, DOI)
    -> L1 existence + title-MATCH (token-Jaccard >= MATCH_TAU 0.5 ; mis-attrib resolve-only LEAK closed)
    -> L2 status (retraction ; RWD 59011 + publisher crossmark)
    -> pre_demoted gate (non-resolve / L1 mismatch / retracted -> T4, NLI NEVER runs ; gate-before-model)
    -> [if PASS-TO-L4] L4 contradiction-veto organ over bound subset S :
         D_lambda = (n_con - n_ent)/|S|  (lambda 1.0)  ;  reject iff D_lambda >= tau 0.67
       S_size == 0        -> T1_BIND_UNCHECKED
       D_lambda >= 0.67   -> T1_BIND_CONTRADICTED   (REJECT)
       D_lambda <  0.67   -> T0_ELIGIBLE            (operating ceiling T1 until L5 closes)
    -> tier T4..T0

DISPOSITION the propose-side reads off the intake:
  ABSORB  = reaches the organ AND not pre_demoted AND D_lambda < 0.67   (T0_ELIGIBLE / T1 bound-clean)
  REJECT  = pre_demoted (T4) OR D_lambda >= 0.67 (T1_BIND_CONTRADICTED)
The verifier is a CALLED frozen substrate (organ md5 asserted unchanged ; byte-identity to the frozen
anchor before any live trust -- STANDARD sec5 / keystone E16 SHIP PATTERN). The propose-side edits it
NEVER.

--------------------------------------------------------------------------------
## 3 FIRST MEASURABLE PROPERTY -- self-refinement (the recommended rung-1)

Gate-ladder is STRICT (keystone sec3): prove the verifier [DONE] -> self-refinement -> initiative.
No layer N+1 before N clears its falsifier. The FIRST rung = SELF-REFINEMENT (NORTH STAR property 2):

  proposer emits self-samples -> the FROZEN verifier selects the ABSORB subset (rejection sampling)
  -> RFT cements weights around verifier-clean outputs only. The judge is grounded + EXTERNAL,
  never the model judging itself (else 2nd-order hallucination = E15).

WHY self-refinement first, not initiative (R3 counter, steel-manned):
  Initiative (property 3: IGR-gap -> retrieve -> verify -> propose) also rides the frozen verifier
  with no weight update, so it LOOKS like a valid first rung. But ANY self-generated pipeline --
  initiative included -- feeds proposals to the verifier-AS-SELECTOR, and the precondition for trusting
  that pipeline is that the verifier's curated-set false-accept TRANSFERS to a live-proposer
  distribution. Self-refinement is the MINIMAL construction that isolates exactly that measurement
  (no IGR-gap detector, no retrieval loop to confound). Initiative stacks machinery on an unmeasured
  selector. -> self-refinement first regardless of which property is the eventual headline.

WHAT self-refinement actually tests : the verifier was frozen on CURATED spoof/gold sets and on a
SINGLE planted 4-item e2e draw (STANDARD sec7). Its own named limit #5 (STANDARD sec9) is exactly:
"a fabrication/wrong-binding RATE over a LIVE proposer on n>30 is NOT yet measured." Rung-1 is the
direct closure of that disclosed gap -- the first measurement of the frozen verifier's false-accept
when the spoofs are the proposer's OWN organic fabrications, not the bait-set. That number is the
precondition for using the verifier to build any training pool.

--------------------------------------------------------------------------------
## 4 SCOPE BOUNDARIES (R2/R10 -- named, so rung-1 is not over-claimed)

- PROSE -> claim EXTRACTION is OUT of rung-1 scope. S1 (keystone sec1) names prose as the ~100%-open
  channel ; claim extraction from free prose is a SEPARATE upstream organ, NOT part of the frozen
  verifier. Rung-1 tests the verifier-as-SELECTOR conditional on the proposer emitting checkable
  (claim, locator) tuples. The keystone whole-program falsifier (prose-extraction recall) is a LATER,
  harder front, not this rung.
- Operating ceiling is T1 (L5 not closed). ABSORB = bound + not-contradicted, NOT "gold". Rung-1
  needs no L5 / T0.
- Binding the claim against the cited DOI's OWN text (vs the bind-corpus) is a different organ, out of
  scope for v1 (STANDARD sec5 DISCLOSED).
- GOLD bind-corpus is NOT needed at design-open. It enters at the rung-1 BUILD as the resolver
  substrate (the proposer's candidate sources resolve against it) -- pulled ROUTED (named module(s)),
  never wholesale (3.8). Flag at BUILD.

--------------------------------------------------------------------------------
## 5 RUNG-1 PRE-REGISTRATION (FROZEN before any data ; R7 ; no bar reopened)

name      : self-refinement yield-or-floor (gate-2 ACCEPTANCE).
principle : self-learning is PRECISION-bound, not recall-bound (keystone GATE-2 ACCEPTANCE). A passed
            fabrication CONTAMINATES weights (cardinal R7) ; a discarded clean sample only costs yield,
            and self-generated yield is cheap. -> accept-PRECISION is the safety GATE ; yield is
            reported, never a pass/fail bar.

### 5.1 Construction (BUILD = a separate TYPE C / TYPE A session)
  1. Proposer emits N proposals over a held-out prompt set (LOCAL-ONLY). Each is (claim, locator) or
     an explicit abstention. Abstentions counted separately, not scored.
  2. Each non-abstaining proposal enters the FROZEN intake (sec 2) -> ABSORB or REJECT.
  3. GROUND TRUTH (Founder-judged, LOCAL-ONLY, R7 -- the established sourcing frame): each proposal
     labeled CLEAN (claim true AND correctly bound to a real supporting source) or DIRTY (fabricated
     locator / wrong-binding / non-supporting). Labels are never faked to clear a bar.

### 5.2 Metrics
  fa_live   = (# DIRTY proposals ABSORBED) / (# DIRTY proposals emitted)        -- the GATE
              (mirrors the verifier's frozen fa_op definition: spoof-acceptance rate, max-based ;
              applied to the live-proposer dirty distribution. NOT a new bar -- the SAME ceiling on
              a NEW input distribution.)
  pool_contam = (# DIRTY ABSORBED) / (# ABSORBED)                               -- RFT-relevant readout
  yield     = (# CLEAN proposals ABSORBED) / (# CLEAN proposals emitted)        -- DIAGNOSTIC, reported
  abstain_rate, reject-by-arm (T4 prov / contradiction-veto) -- reported context.

### 5.3 Bars (FROZEN)
  G-RUNG1 (HARD, precision) : fa_live <= 0.10 over a DIRTY subset of n >= 30.
      0.10 = the verifier's OWN frozen fa_op ceiling (STANDARD sec4 ; recorded curated fa_op 0.0333).
      n >= 30 dirty with 0 absorbed -> CI upper ~0.10 (rule of three ; matches STANDARD sec2 A-channel
      CI-clear logic). The DIRTY subset, not total N, is the sample that bounds fa.
  YIELD : reported only. Low yield = throughput-starved but SAFE ; self-yield is cheap. NOT a fail.

### 5.4 Falsifier (retires the cheap path ; DESTINATION FALSIFIABILITY, keystone)
  PRIMARY : fa_live > 0.10 over the n>=30 dirty subset -> the frozen verifier's curated-set precision
      does NOT transfer to the live-proposer distribution -> self-refinement is UNSAFE on this
      substrate (a fabrication contaminates the RFT pool, cardinal R7) -> the cheap-Entity path STALLS
      at rung-1. Honest terminal = "fabrication-closure over a live proposer needs model scale or a
      stronger gate." BANK the negative ; do NOT iterate RFT blindly, do NOT tune the gate to pass.
  VOID guards (carry the verifier's own, STANDARD sec10) : if the frozen anchor fa_op != 0.0333 (byte)
      on a clean re-run of the verifier against its frozen fixture -> env/version drift -> STOP (this
      is not a rung-1 result). The verifier must reproduce its freeze before its live-selector verdict
      is trusted. rho(reject-signal, upstream bind) >= 0.95 on the live set -> retrieval proxy -> VOID.

### 5.5 PASS / outcome
  PASS = G-RUNG1 holds (fa_live <= 0.10, n>=30 dirty). -> the frozen verifier transfers as a live
      selector -> self-refinement (rejection-sampling RFT) is SAFE to run ; yield reported as the
      throughput readout ; NEXT rung = the RFT loop itself, then (after it clears) initiative.
  FAIL = falsifier PRIMARY hit -> bank negative per 5.4.

--------------------------------------------------------------------------------
## 6 CONSISTENCY CHECK (R15/R17 -- no frozen bar reopened)
  - G-RUNG1 0.10 = the verifier's frozen fa_op ceiling, applied to a new distribution. NOT a relitigation.
  - intake (sec 2) is the verbatim step2b contract ; organ called frozen, never edited.
  - operating ceiling T1 respected (L5 open) ; rung-1 claims nothing about T0.
  - prose-extraction excluded by scope (sec 4), consistent with keystone S1 + whole-program falsifier.
  - self-refinement-before-initiative is the keystone strict ladder, justified in sec 3.

--------------------------------------------------------------------------------
## 7 BUILD-READINESS (for the next session, not built here)
  rung-1 = BUILD (TYPE C: wire proposer -> frozen intake -> adjudicate) + DATA (TYPE A: held-out prompt
  set + Founder CLEAN/DIRTY labels). Wiring exists on disk (loop_e2e_v0.py / run_full_turn_s2b_v0.py /
  run_step2b_intake.py d93a64e3). FREEZE this pre-registration (sec 5) BEFORE any proposer is run.
  GOLD routed pull (resolver bind-corpus) flagged at BUILD. eval+fix never share a session (R7).
