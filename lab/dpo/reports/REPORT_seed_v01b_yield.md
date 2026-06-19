# REPORT — Self-refinement seed yield (propose-side)

date: 2026-06-17
front: propose-side (autonomous-entity North Star), on top of the FROZEN grounded verifier v1
plane: SELF-REFINEMENT seed — measure the verifier-ABSORBED clean SUPPLY of the frozen base
status: CLOSED. clean-supply ≈ 0 across both honest elicitation variants. This is a measurement
        result, not a failure to fix (anti-digging STOP-rule 4).

## Question
rung-1 proved the frozen grounded verifier is SAFE as a rejection-sampling selector (it accepted
zero live fabrications). A rejection-sampling RFT loop additionally needs a non-trivial SUPPLY of
verifier-ABSORBED (provenance-clean) self-samples. This session measures that supply: under honest
elicitation, how many of the frozen base's self-proposals does the FROZEN intake absorb.

## Method
- Proposer: FROZEN base (Qwen2.5-Coder-7B, 4-bit nf4, greedy, no adapter, no GOLD), the lab's
  byte-exact generation wrapper. Discipline lives OUTSIDE the weights (North Star claim).
- Elicitation: 30 grounding topics × 2 honest variants, each emitting an asserted TITLE alongside
  the citation, and each offering an explicit abstention exit "[no verified source]":
  - V1 abstention-permitted: cite a real paper, else abstain.
  - V2 confident-binds: cite only the binding the model is most confident is correct, else abstain.
- Intake: the FROZEN provenance verifier (L1 existence + title-match ≥0.60 vs the model's asserted
  title; L2 retraction via Retraction Watch + publisher flag). Called byte-unchanged (R7).
  ABSORBED = L1 pass AND not retracted. expected_title = the model's OWN asserted title.

### Intake-interface precondition (resolved first, on already-collected data)
rung-1 fed claim-as-expected-title and rejected even its one correctly-bound CLEAN proposal. Before
measuring supply we confirmed the intake admits a correct binding when given the model's asserted
title: re-scoring the rung-1 CLEAN binding (a correctly-bound, non-retracted real paper) with its
REAL title as expected_title returns L1L2_PASS; the same binding scored claim-as-title returns
T4_L1_MISMATCH. So rung-1's rejection was a claim-as-title interface artifact, and 0 supply here is
a real ceiling, not an artifact. (Adding the asserted-TITLE field is a proposer-format change, not
an intake edit — the intake already takes expected_title; the frozen organ was not touched.)

## Result
clean-supply (ABSORBED) per variant, every number on-disk-sourced:

| variant | proposed | abstained | ABSORBED |
|---|---|---|---|
| V1 abstention-permitted | 30/30 | 0/30 | 0/30 |
| V2 confident-binds | 30/30 | 0/30 | 0/30 |
| total | 60/60 | 0/60 | 0/60 |

Two findings:
1. The frozen base NEVER used the abstention exit (0/60), in BOTH variants, despite the explicit
   "[no verified source]" option. It confidently emits a full (claim, title, DOI) for every prompt.
2. None of the 60 minted bindings absorbed: every one was rejected at L1 as either non-resolving or
   title-mismatch (no retractions). Rejection split mirrors rung-1 (the base mints plausible but
   non-binding citations from parametric memory).

## Verdict
The cheap self-refinement path is THROUGHPUT-STARVED at the proposer. A bare frozen language model
cannot be its own clean source: its parametric citation channel yields ≈0 verifier-clean bindings,
and honest abstention elicitation does not reduce fabrication (the model is miscalibrated — it
mints confidently rather than abstaining). The RFT pool is not seedable from this proposer/channel.

Self-learning was already framed as PRECISION-bound, not recall-bound; rung-1 proved the precision
(accept) side. This session reads the throughput (yield) side, which is DIAGNOSTIC — a low number is
honest and cheap, and must never be chased by loosening the verifier (that re-opens precision).

## Falsifier
A stronger base proposer, OR a RETRIEVAL-grounded locator channel (the proposer retrieves a real
locator from a corpus/index instead of generating a DOI from memory), yields >0 ABSORBED.

## Next (Founder-call)
Decide the locator channel before any further seed: (a) a stronger base proposer, or (b) open the
upstream retrieval/locator channel (L5 internet grounding / bind-corpus retrieval) so proposals
carry retrieved — not minted — locators. Parametric DOI minting is a dead channel for clean
self-supply.

## Discipline notes
- Verifier organ byte-unchanged (called, not edited). No bar moved; no new bar frozen.
- Coverage note (not a defect): arXiv DataCite DOIs (10.48550/arXiv.*) do not resolve via the
  Crossref-keyed intake — a known intake-coverage limit, logged, not in scope here.
- Reproducibility artifacts (this report, the elicitation prompts, the generation + intake scripts)
  are public. The proposal/intake row-level outputs carry minted DOIs (bait-class) and are
  LOCAL-ONLY.
