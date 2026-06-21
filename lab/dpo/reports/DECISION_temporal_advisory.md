# DECISION: temporal channel stays ADVISORY (denominator re-cut closed)

Plane: organism-0 Phase 4, temporal-channel promotion. Closes SPEC_denominator_recut_v1.
Date: 2026-06-21. Decider: engineer (Founder-delegated). Trigger chain: LABA DENOMINATOR RECUT -> HELDOUT GEN -> labels.

## Input
- 40 fresh held-out candidates, BASE proposer (generate_claim, no LoRA), 20 HELD_OUT_TOPICS x k=2.
- Founder labels (ground truth, E15 -- not authored by the model): 7 CLEAN / 33 DIRTY (82% dirty).
- Held-out + labels = LOCAL ONLY (3.2); not reproduced here, not public.

## Acceptance (SPEC_denominator_recut_v1 sec 5)
- A1 N>=40 .......... PASS (40)
- A3 DIRTY-with-year>=4 ... PASS (29)
- A2 absorbable-CLEAN>=10 . FAIL (CLEAN ceiling = 7)
- M1 ceiling = CLEAN/N = 7/40 = 0.175 < 0.20 -> pipeline gate UNREACHABLE on any outcome.

## Decision
CONFIRM / REFUTE stay ADVISORY (non-gating). NOT promoted.
Rationale: M1 cannot clear 0.20 on a denominator we can cheaply build. Advisory is the safe default
under ONTO priority (safety > capability): an advisory channel absorbs nothing, so fa_live risk = 0
regardless of label quality. The channel is sound -- CONFIRM same-sentence (D1'' closed), REFUTE
restrained on person (D3) + source-work (D4) decoys, M2 recovery 2/2 on frozen S4 -- but not
load-bearing for the pipeline gate on this workload. This is spec sec 7's advisory outcome, not a
failure of the channel.

STOP-rule applied: generating + labeling more candidates to chase CLEAN>=10 is scope expansion
("to be rigorous we need more"). Not done. Cheap > perfect.

## Assumption (R2)
Founder labels taken as authored ground truth. The advisory decision is robust to label quality
because advisory absorbs nothing -- there is no risk path that label noise could open.

## Flagged finding (R16, parked -- NOT acted on)
Founder dirty-rate = 82% on famous textbook topics (PCR, Semmelweis/1847, Ohm, Maxwell, Rutherford).
Either (a) the base proposer hallucinates specifics at a far higher rate than S2 implied
(support_supply ~0.5), or (b) label strictness. Not separated this session. If the proposer's
true CLEAN-rate on date-bearing claims matters later, the move is a larger labeled sample, not a
re-label of these 40. Logged to tail debt.

## Residual
(B) V7 D5 (later-dated same-title sibling refute restraint) parked -- only relevant if REFUTE is
ever promoted to gating, which this decision defers. No work owed.

## What stays frozen / banked
- CONFIRM same-sentence sound; REFUTE D3+D4 restrained (carry byte-identical).
- Channel usable as ADVISORY signal in any future pipeline; never as an absorb-enabler without a
  fresh promotion decision on a clearing denominator.

---
*DECISION_temporal_advisory - 2026-06-21 - denominator re-cut closed. 40 base-proposer held-out,
Founder-labeled 7 CLEAN / 33 DIRTY -> A2 FAIL, M1 ceiling 0.175 < 0.20. CONFIRM/REFUTE stay ADVISORY
(safe default; channel sound but not load-bearing on this workload). STOP: no more cycles chasing
CLEAN>=10. Founder dirty-rate 82% flagged + parked. V7 D5 parked.*
