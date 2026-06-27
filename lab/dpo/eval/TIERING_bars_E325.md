# TIERING_bars_E325 -- tiering admission gate validation (PUBLIC, R15-clean)

Public reproducibility record for the knowledge-tiering admission gate. Aggregate-only:
mechanism + bar definitions + bucket/tier counts + provenance checksums. NO per-row ids,
NO claim text (the held-out set is LOCAL-only by design; see COVERAGE/PRIVACY below).

## Mechanism
Pure routing policy `route(verdict, grounded) -> {GOLD | MEMORY | REJECT}` over the Layer-1
structural-discriminator verdict vocabulary {DIRTY, CLEAN, ABSTAIN}. No new verdict logic; the
frozen verifier seam is untouched. The gate adds admission control only.

| verdict          | tier   | rationale                                            |
|------------------|--------|------------------------------------------------------|
| DIRTY            | REJECT | contradicted claim never enters the substrate        |
| ABSTAIN          | MEMORY | unverified != tier-worthy (honest floor)             |
| CLEAN + grounded | GOLD   | CLEAN necessary, source-grounding sufficient         |
| CLEAN, ungrounded| MEMORY | grounding absent -> not GOLD                          |

Fail-closed: unrecognized verdict raises (never silent admit). Only `grounded is True` admits CLEAN
to GOLD. Monotone: relative to an admit-all baseline the gate can only down-route; it can never
promote an unverified or contradicted claim to GOLD.

## Pre-registered bars (fixed BEFORE measurement; falsifier-first)
- T0-strict          : 0 DIRTY rows routed to GOLD            (ABSOLUTE; any leak = REFUTED)
- T-abstain          : 0 ABSTAIN rows routed to GOLD          (any leak = REFUTED)
- T-ungrounded-floor : 0 CLEAN-ungrounded rows routed to GOLD (any leak = REFUTED)
- T-clean-recall     : CLEAN-grounded -> GOLD recall >= 5/5   (collapse below floor = REFUTED)
- T-hermetic         : report byte-identical across two cold offline runs

## Result (E325, TYPE-B measurement over the frozen held-out)
- rows = 25 ; buckets = {DIRTY:5, ABSTAIN:10, CLEAN_GROUNDED:5, CLEAN_UNGROUNDED:5}
- routed tiers = {REJECT:5, MEMORY:15, GOLD:5}
- T0-strict          : GREEN (DIRTY->GOLD = 0)
- T-abstain          : GREEN (ABSTAIN->GOLD = 0)
- T-ungrounded-floor : GREEN (CLEAN_UNGROUNDED->GOLD = 0)
- T-clean-recall     : GREEN (CLEAN_GROUNDED->GOLD = 5/5)
- all rows match expected tier : GREEN
- OVERALL: ALL-GREEN -> gate validated.

## Provenance (checksums)
- held-out set md5 : CABA277117FCC121B5C00E49A27911D1 (25 rows; LOCAL-only, not in this repo)
- per-row report md5 : B057F9D014CC45CF720BDB750C420604 (deterministic; T-hermetic identical)

## Coverage / privacy (R3 limitation)
The gate protects the substrate against the internal-contradiction failure mode that the certified
Layer-1 channel catches. Out-of-channel content (anachronism, numeric false-precision, misattribution)
arrives as ABSTAIN and routes to MEMORY -- the honest floor -- it is not caught. This is a monotone
admission-control improvement on the certified channel, not a cross-channel coverage claim.

The held-out evaluation set and its construction script are LOCAL-only by design: publishing them
would let future pretraining corpora absorb the test items and invalidate the measurement. This
record carries the mechanism, bar definitions, aggregate counts, and checksums sufficient to
reproduce the result against an independently-constructed held-out following the same bucket spec.
