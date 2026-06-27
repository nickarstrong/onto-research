# Initiative Emission Filter -- Mechanism Specification

Public mechanism + reproducibility record for the certified initiative emission filter:
the rule by which a self-learning entity decides, unprompted, whether to SPEAK a candidate
contribution or hold it. This document is the datable provenance for the initiative
property at WIRING grade: a trigger layer that opens the floor, gated by the same certified
emission filter that governs substrate admission, so that an unprompted utterance is held to
a standard at least as strict as a prompted one.

Scope of this document: trigger semantics, the emission floor and its asymmetry, the
non-verdict status of the trigger layer, the pre-registered falsifier bars with their
aggregate pass results, and an explicit evidence-grade statement bounding the claim to
wiring (not behavior). It contains NO held-out candidate text, NO held-out row identifiers,
NO trigger/claim tokens, and NO fixture markers. The held-out evaluation set remains
local-only and is never published, to keep the measurement uncontaminated by future
pretraining corpora. Reproducibility artifacts (the mechanism-only measure driver and this
aggregate record) are public; the held-out set, per-row report, and build harness are not.

---

## 1. Substrate consumed (not re-derived here)

The initiative filter is a pure routing policy over verdicts produced by an
already-certified verifier stack. It adds no new verdict logic. The load-bearing input is
the Layer-1 structural discriminator over the verdict vocabulary {DIRTY, CLEAN, ABSTAIN},
with any Layer-2 oracle verdicts already materialized on the candidate record, plus a single
boolean `grounded` (R4: an independent source is present and sufficient).

Frozen substrate (md5_8, intake-verified, never edited by this plane):

| file                            | md5_8     | role                              |
|---------------------------------|-----------|-----------------------------------|
| o0_structural_discriminator.py  | 92D46A55  | Layer-1 discriminator (frozen seam) |
| o0_tiering_gate_v324.py         | C26D5146  | certified `route()` (unmodified)  |
| o0_initiative_harness.py        | BEEE0E99  | frozen build harness (unmodified) |

The emission filter is downstream-only. The certified `route()` and the frozen
discriminator are inherited verbatim; the initiative property adds a TRIGGER and a SCOPE,
never a new verdict.

---

## 2. Initiative semantics

| action  | meaning                                                              |
|---------|---------------------------------------------------------------------|
| EMIT    | the entity speaks the candidate unprompted                           |
| SUPPRESS| the entity holds the candidate; no unprompted utterance             |

The failure mode the filter guards is unprompted noise: an autonomous entity that speaks
contributions which are contradicted, ungrounded, or out-of-channel pollutes its own output
stream and any downstream consumer with exactly the dirt the verifier exists to catch --
now emitted on the entity's own initiative rather than in answer to a prompt. Because an
unprompted utterance carries no prompt to constrain it, the bar to speak must be at least as
strict as the bar to admit a prompted claim to the durable substrate.

---

## 3. Emission gate -- routing policy

Emission is a pure function of two inputs: whether the trigger fired validly, and what the
certified filter says about the candidate.

```
emission_decision(trigger_valid, verdict, grounded):
    if not trigger_valid          -> SUPPRESS   (no valid occasion to speak)
    elif route(verdict,grounded) admits to GOLD -> EMIT
    else                          -> SUPPRESS   (candidate not substrate-worthy)
```

`route(verdict, grounded)` is the certified admission policy, re-used verbatim. Its sole
GOLD-admitting input is `(CLEAN, grounded=True)`. Therefore the sole EMIT-admitting input is
`(trigger_valid=True, CLEAN, grounded=True)`. Any DIRTY, any ABSTAIN, any CLEAN-ungrounded
candidate -- and any candidate under an invalid trigger -- SUPPRESSES.

### 3.1 Emission floor is stricter than retention floor

"Speak unprompted" is a strictly stronger gate than "hold in memory". A candidate that
`route()` would park in MEMORY (e.g. CLEAN-ungrounded, or ABSTAIN) is retainable but NOT
emittable: only a GOLD-admitting verdict opens the emission floor. The asymmetry is realised
as a SCOPE restriction on emission -- emit only on the GOLD-admitting input -- with ZERO new
verdict logic. The discipline floor is inherited from `route()` unchanged.

### 3.2 Monotonicity

The emission filter can only down-route relative to a naive speak-everything baseline. It
never emits a contradicted, ungrounded, or out-of-channel candidate, and never emits on an
invalid trigger. It is never more permissive than the `(trigger_valid, CLEAN, True)` floor.

---

## 4. Trigger layer -- a non-verdict, uncertified surface

The trigger predicate decides whether there is a valid occasion to speak at all. It is NOT
part of the certified verdict path: the certified guarantee covers ONLY the emission floor
(what may be spoken once an occasion is granted), never the quality of the occasion itself.

Consequences, stated explicitly so the certification is not over-read:

- A trigger that under-fires shows up as a LIVENESS failure (the entity is mute when it
  should speak), never as a discipline breach.
- A trigger that over-fires shows up as OVER-EMISSION pressure on the floor, which the
  emission floor must still absorb -- an invalid-occasion candidate that the filter WOULD
  otherwise pass must still SUPPRESS on the trigger arm.
- The trigger layer never relaxes a floor. Trigger quality and discipline are orthogonal.

This is the sharp guard the measurement targets: a candidate that `route()` would admit to
GOLD, presented under an INVALID trigger, must SUPPRESS. The trigger gates initiation
independently of gate-pass.

---

## 5. Pre-registered falsifier bars (definitions)

Bars are fixed before any measurement (falsifier-first). A RED result triggers redesign,
never a threshold relaxation. Held-out instances are local-only and not reproduced here;
only the bar definitions are public.

| bar                  | binds                  | falsifier (any one = design refuted)                 |
|----------------------|------------------------|------------------------------------------------------|
| I-hermetic           | routing determinism    | two cold offline runs not byte-identical             |
| I-discipline-floor   | substrate-grade floor  | any non-GOLD-admitting candidate EMITs (ABSOLUTE)    |
| I-liveness           | anti-mute              | any valid-trigger GOLD-admitting candidate SUPPRESSes |
| I-no-noise           | grounded-only speech   | any emitted row not (verdict==CLEAN AND grounded)    |

I-discipline-floor is the non-negotiable safety floor: zero false-emit on the adversarial
held-out is required; no liveness/recall consideration may trade against it.

---

## 6. Aggregate results -- four bars GREEN (wiring grade)

Held-out composition (aggregate counts only): 15 rows across three buckets --
Bucket-A (5): valid trigger + GOLD-admitting candidate (expected EMIT);
Bucket-B (5): valid trigger + non-GOLD candidate, split B1 (3) + B2 (2) (expected SUPPRESS);
Bucket-C (5): INVALID trigger + candidate `route()` WOULD admit to GOLD (expected SUPPRESS).

- I-hermetic: GREEN. Two cold offline runs byte-identical; decision-hash (md5)
  `ce2a7eb55027b0efba2e89b2da0c85a5`. Fixture integrity 15/15. Bucket counts A:5 B1:3 B2:2
  C:5 exact.
- I-discipline-floor (ABSOLUTE): GREEN. 0 EMIT on any Bucket-B or Bucket-C row.
- I-liveness: GREEN. All 5 Bucket-A rows EMIT; Bucket-A non-empty.
- I-no-noise: GREEN. Every emitted row has verdict==CLEAN AND grounded==True.

Confusion (counts only):

- rows: 15
- emit: 5 (all Bucket-A) / suppress: 10 (all Bucket-B + Bucket-C)
- false_emit: 0 / false_suppress: 0
- per-row join emit==expected_emit: 15/15 match

Sharp-guard confirmation: every Bucket-C row carries a candidate `route()` WOULD pass (GOLD)
under an INVALID trigger and still SUPPRESSed (0 EMIT on C). This confirms the trigger layer
gates initiation independently of gate-pass; the discipline floor holds regardless of
trigger quality.

Frozen held-out checksum (md5): `419d3a0d5e8cb46b41b96d30795ccb47` (15-row set, local-only).

---

## 7. Evidence-grade (R5) -- WIRING, NOT BEHAVIORAL

This certification is bounded and stated explicitly so it is not over-read.

The GREEN result is TRUE-BY-CONSTRUCTION. The measure runs a deterministic harness over a
self-consistent fixture whose verifier output (verdict / grounded) is HARDCODED from design,
and the build plane already proved emission_decision==expected_emit on all 15 rows.
Therefore what is certified is the EMISSION-FILTER WIRING -- the trigger arm and the
`route()`-derived emission floor are correctly composed; `route()` gates emission; there is
zero false-emit on the adversarial held-out; the routing is deterministic and hermetic.

What is NOT certified here is a live model's initiative behavior. The candidate text, the
trigger occasion, and the verifier verdict are fixtures, not generated by a model under
test. The strong/behavioral sense of "initiative" -- a live model that, unprompted,
GENERATES a trigger and a candidate which the certified filter then admits or suppresses --
requires a separate plane that wires a live model into the loop (replacing the hardcoded
fixture) and re-derives the bars for model-in-loop measurement. This document must not be
cited as evidence that the initiative property holds behaviorally. It is evidence that the
filter that would govern such behavior is correctly wired and discipline-tight.

---

## 8. Coverage limitations

- Channel-inherited coverage. The emission floor is only as strong as the verdict it
  consumes. It guards the output stream against the internal-contradiction failure mode the
  certified channel catches. Out-of-channel dirt (anachronism, numeric false-precision,
  misattribution) arrives as ABSTAIN and is correctly suppressed (ABSTAIN is non-GOLD-
  admitting), never emitted; the filter does not claim full output purity, only that nothing
  below the substrate-admission floor is ever spoken unprompted. Cross-channel coverage
  remains terminal and is not reopened here.
- Trigger quality is uncertified. The certification bounds what may be spoken once an
  occasion is granted; it does not certify that occasions are well-chosen. A persistently
  under-firing trigger yields a mute-but-disciplined entity; a persistently over-firing
  trigger places more load on the floor but cannot breach it. Both are liveness/occasion
  concerns, orthogonal to discipline.
- Conservative emission cost. A genuinely worthwhile contribution the verifier abstains on is
  never spoken unprompted unless a certifying channel for its dirt type is built. This is a
  deliberate safety-first trade: zero noisy unprompted utterance is preferred over emission
  recall. The candidate survives in memory and remains emittable if its channel is ever built
  and it later passes as CLEAN-grounded.
- Grounding-trust boundary. The filter trusts the upstream `grounded` flag. A bad source on a
  false candidate would pass the floor -- identical exposure to first-admission; emission adds
  no new exposure. Source soundness is an upstream R4 concern.

---

## 9. Provenance

Lineage (priority/provenance record): initiative design and bar pre-registration; build and
frozen held-out; measurement (four bars GREEN at wiring grade, public). Generate and
evaluate were held in separate planes -- the build plane never grades its own output, and the
held-out carries pre-registered expected-emit values hardcoded from design, never derived by
calling `route()`. Public reproducibility artifacts: the mechanism-only measure driver and
this aggregate record. Held-out set, per-row report, and build harness are local-only and
never published.
