# STRATEGY — Generalization gap: layered discriminator

Status: DECIDED (CONCEPT). Implementation pending (separate Type C session).
Scope: architectural direction for the temporal-evidence verifier's generalization ceiling.

## Problem (restated)
The verifier emits a REFUTE verdict only from a finite offline lookup. A fabrication that
is not in that lookup cannot be refuted and falls to ABSTAIN. Growing the lookup raises
recall but leaves the ceiling intact: the next unseen fabrication abstains again. The gap
is structural (lookup-bound verification), not a coverage shortfall.

## Direction
Layered discriminator, structural-first:
1. Structural layer (primary): derivation-based, hermetic, no external oracle. Targets
   anachronism, false-precision, and internal-inconsistency — classes catchable from the
   claim's own structure under the R1-R18 discipline.
2. Oracle layer (gated add-on): consulted only where ground truth is required; emits a
   refute verdict only under unique-entity resolution with a single authoritative value;
   otherwise abstains. Never produces a refute under ambiguity.
3. Abstain floor: retained as the honest verdict for genuinely-unseen claims with no
   accessible truth. Compressed by layers 1-2, never forced to zero.

The offline lookup is demoted from authority to a cache / regression fixture.

## Keystone
The failure to avoid is not abstention — it is a fabricated refute verdict. A verifier that
invents a verdict violates its own no-fabrication discipline. Abstention is honest; an
unfounded refute is not. This makes the discipline tier-independent: correctness comes from
derivation and gated truth, not from memorized answers.

## Acceptance discipline (summary)
A frozen, pre-registered falsifier governs implementation. The hard, non-negotiable bound
is zero false-refute on the clean control set; this does not trade against catch-rate. A
class that cannot be caught structurally is declared non-discriminative rather than tuned
into an apparent pass. Detailed thresholds are sealed locally before code (not public).

## Dependency surfaced
The oracle false-refute defect on a specific true-year claim moves from tail debt onto the
critical path: any reliance on the oracle layer for generalization must close that defect
first, or generalization is bought at the cost of fabricated verdicts.
