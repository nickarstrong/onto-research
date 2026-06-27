# Self-Learning Admission Loop -- Mechanism Specification

Public mechanism + reproducibility record for the certified knowledge-tiering admission
gate and its MEMORY->GOLD re-admission path. This document is the datable provenance for
the self-learning loop: admit a candidate claim, park it in temporary memory when its
grounding is incomplete, and re-admit it to the durable substrate once it is independently
grounded -- with the safety floors held immovable at every step.

Scope of this document: gate policy, tier semantics, the immovable floors, the
re-admission-as-re-run principle, and the pre-registered falsifier bars with their
aggregate pass results. It contains NO held-out claim text, NO held-out row identifiers,
NO source/provenance tokens, and NO fixture markers. The held-out evaluation sets remain
local-only and are never published, to keep the measurement uncontaminated by future
pretraining corpora. Reproducibility artifacts (gate code, scoring scripts, gate logs,
aggregate eval reports) are public; the held-out sets and per-row reports are not.

---

## 1. Substrate consumed (not re-derived here)

The admission gate is a pure routing policy over verdicts produced by an already-certified
verifier stack. It adds no new verdict logic. The load-bearing input is the Layer-1
structural discriminator over the verdict vocabulary {DIRTY, CLEAN, ABSTAIN}, with any
Layer-2 oracle verdicts already materialized on the claim record.

The frozen verifier seam (structural discriminator, md5_8 `92D46A55`) is never edited by
the gate or by the re-admission path. The gate is downstream-only.

---

## 2. Tier semantics

| tier   | meaning                                                                     | durability |
|--------|-----------------------------------------------------------------------------|------------|
| GOLD   | durable substrate; ground truth for downstream inference and self-learning  | permanent  |
| MEMORY | temporary store; held but not treated as durable fact                       | temporary  |
| REJECT | not admitted; logged as an admission error                                  | none       |

The failure mode the gate guards is substrate poisoning: a contradicted or unverified
claim written into GOLD becomes self-reinforcing ground truth for every later inference
and every self-learning step. A permanent substrate makes a false admission strictly more
costly than a missed admission, so the gate is conservative by design.

---

## 3. Admission gate -- routing policy

The gate is a pure function `route(verdict, grounded) -> {GOLD | MEMORY | REJECT}`,
hermetic at gate time (no network, no oracle re-run). `grounded` is an R4 grounding check:
an independent source is present and sufficient.

```
DIRTY                 -> REJECT    (contradicted claim = frameshift; never substrate)
ABSTAIN               -> MEMORY    (honest floor; unverified is not tier-worthy)
CLEAN + grounded      -> GOLD      (CLEAN necessary; grounding sufficient)
CLEAN + ungrounded    -> MEMORY    (R4 not satisfied; eligible later if grounded)
unrecognized verdict  -> error     (fail-closed; never a silent admit)
```

Sole GOLD-admitting input = `(CLEAN, grounded=True)`. Any falsey/missing `grounded` routes
CLEAN to MEMORY, never GOLD.

### 3.1 Three immovable floors

1. DIRTY -> REJECT. A contradicted claim never reaches the substrate. ABSOLUTE.
2. ABSTAIN -> MEMORY. An unverified (out-of-channel) claim never reaches GOLD, even with a
   source attached, because the floor is verdict-driven and grounding-independent. ABSOLUTE.
3. CLEAN-ungrounded -> MEMORY. CLEAN alone is necessary but not sufficient for GOLD; without
   independent grounding the claim is held in temporary memory. ABSOLUTE.

These floors are non-negotiable. Tuning the grounding predicate is permitted; relaxing a
floor is not.

### 3.2 Monotonicity

Relative to a naive admit-all baseline, the gate can only down-route (GOLD -> MEMORY,
MEMORY -> REJECT). It never promotes an unverified or contradicted claim to GOLD. The gate
is never more permissive than the `(CLEAN, True)` floor.

---

## 4. Re-admission -- the same gate re-run, not a second path

A self-learning entity does not admit only once. A claim parked in MEMORY because it was
ungrounded at admission time may later acquire an independent source. It must then be
re-presentable for GOLD -- without weakening any floor and without opening a second,
looser admission code path.

Core principle: re-admission introduces zero new gate logic, zero new verdict logic, and
zero new GOLD-admission predicate. Re-admission is the same certified `route(verdict,
grounded)` re-applied to the same claim record after a grounding-arrival event updates its
input tuple. Every floor, the monotonicity, and the sole GOLD-admitting input are inherited
verbatim.

### 4.1 Eligibility by MEMORY sub-population

A claim sits in MEMORY for one of two reasons, with different re-admission eligibility:

- MEMORY-ungrounded `(CLEAN, False)`: internally consistent, source absent. The only missing
  variable is grounding. This is the legitimate re-admission population. When an independent
  source arrives the tuple flips `(CLEAN, False) -> (CLEAN, True)` and re-running the gate
  routes it to GOLD. Sound: the verdict did not change; grounding is exactly the gate's
  sufficiency condition over a CLEAN verdict.

- MEMORY-abstain `(ABSTAIN, *)`: out-of-channel; the verifier correctly cannot adjudicate
  it. Attaching a source sets `grounded=True` but does not change the verdict. Re-running
  the gate on `(ABSTAIN, True)` still routes to MEMORY. The floor enforces this with no
  special case. The only way this population could become GOLD-eligible is a verdict flip
  ABSTAIN -> CLEAN, which requires building a certifying channel for that dirt type -- out
  of scope here (cross-channel coverage is terminal).

DIRTY claims are REJECTED and have no MEMORY population. Re-presenting an unrepaired DIRTY
claim re-emits DIRTY -> REJECT (idempotent). A DIRTY claim can only reach the substrate by
being repaired, which makes it a different claim with a fresh verdict entering admission for
the first time -- a new admission, not a re-admission of the rejected one. This closes the
re-presentation side-door.

### 4.2 Grounding-arrival is two-phase (hermeticity preserved)

The gate must stay a pure offline routing function, so grounding is split:

- Phase 1 (out-of-band; may use network / oracle / external lookup): grounding acquisition.
  An independent source is found and materialized on the claim record, and `grounded` is set
  True. Not the gate, not hermetic, not at gate time.
- Phase 2 (hermetic; gate time): the certified gate reads the now-updated `(verdict,
  grounded)` tuple and re-routes. No network, no oracle. Byte-identical to first-admission
  gate semantics.

The grounding-arrival event is exactly the `grounded` False->True transition with a valid
independent source attached. "Independent" means the source is not the artifact that produced
the claim (no self-citation, no circular grounding). Grounding never touches the verdict --
this is what keeps the ABSTAIN floor intact with no special case.

### 4.3 Termination -- the re-admission relation is a DAG, not a cycle

Claim state = `(verdict, grounded, tier)`. Within re-admission scope:

- `grounded` is monotone: the only event is False->True. There is no spontaneous
  de-grounding, so no oscillation on the grounding axis.
- `verdict` is frozen: verdict transitions require channel construction, which is
  out-of-scope. Within re-admission the verdict never changes.

Therefore the only reachable transition is `(CLEAN, False, MEMORY) -> (CLEAN, True, GOLD)`:
a single one-way step. `(ABSTAIN, *, MEMORY)` is a fixed point under grounding. `(DIRTY, *,
REJECT)` is not in the population. GOLD is absorbing: no MEMORY<-GOLD edge exists;
re-presenting an already-grounded claim re-emits GOLD. The loop is idempotent (re-run yields
the same tier), terminating (at most one MEMORY->GOLD step per claim), and free of poison
loops.

---

## 5. Pre-registered falsifier bars (definitions)

Bars are fixed before any measurement (falsifier-first). A RED result triggers redesign,
never a threshold relaxation. Held-out instances are local-only and not reproduced here;
only the bar definitions are public.

### 5.1 Tiering-gate bars (five)

| bar               | binds                | falsifier (any one = design refuted)                    |
|-------------------|----------------------|---------------------------------------------------------|
| T0-strict         | substrate purity     | any DIRTY row routed to GOLD                             |
| T-abstain         | honest floor         | any ABSTAIN row routed to GOLD                           |
| T-ungrounded-floor| R4 admission         | any CLEAN-ungrounded row routed to GOLD                  |
| T-clean-recall    | anti-collapse        | grounded-CLEAN recall to GOLD below the pre-set floor F  |
| T-hermetic        | routing determinism  | two cold offline runs not byte-identical                |

T0-strict and T-abstain are the non-negotiable safety floors.

### 5.2 Re-admission bars (six)

| bar                  | binds                | falsifier (any one = design refuted)                  |
|----------------------|----------------------|-------------------------------------------------------|
| RA-floor             | immovable floor       | any non-(CLEAN,True) tuple routed to GOLD             |
| RA-ungrounded-promote| liveness / anti-dead  | any newly-grounded CLEAN row stays MEMORY            |
| RA-abstain-stays     | cross-channel terminal| any grounded-ABSTAIN routed to GOLD                  |
| RA-reject-stays      | poison-loop guard     | any unrepaired DIRTY routed to MEMORY or GOLD        |
| RA-idempotent        | termination           | any tier change on re-run, or any MEMORY<-GOLD edge  |
| RA-hermetic          | hermetic survival     | network/oracle at re-route, or non-identical output  |

RA-floor, RA-abstain-stays, RA-reject-stays are the non-negotiable safety floors.

---

## 6. Aggregate results

Held-out composition (aggregate counts only): four buckets totaling 25 rows --
known-DIRTY (5), known-ABSTAIN (10), known-CLEAN-grounded (5), known-CLEAN-ungrounded (5).
The re-admission set re-uses the same frozen 25-row substrate with a grounding-arrival field
added per row.

### 6.1 Tiering gate -- all five bars GREEN

- gate verdict tally: {DIRTY: 5, ABSTAIN: 10, CLEAN: 10}
- expected tier distribution: {REJECT: 5, MEMORY: 15, GOLD: 5}
- pre-registered match: 25/25 rows route to the pre-registered tier
- sole GOLD-admitting input observed: `(CLEAN, True)` only
- hermetic: two cold offline runs byte-identical
- frozen held-out checksum (md5): `CABA277117FCC121B5C00E49A27911D1`

### 6.2 Re-admission loop -- all six bars GREEN

- re-route tally: {GOLD: 10, MEMORY: 10, REJECT: 5}
- RA-floor: GOLD-routed tuples = `(CLEAN, True)` only; no `(ABSTAIN, True)`, no `(DIRTY, *)`
- RA-ungrounded-promote: 5 newly-grounded CLEAN rows route to GOLD
- RA-abstain-stays: 10 grounded-ABSTAIN rows route to MEMORY, 0 to GOLD
- RA-reject-stays: 5 unrepaired DIRTY rows route to REJECT, 0 to MEMORY/GOLD
- RA-idempotent: 25/25 rows tier-stable on re-run; no MEMORY<-GOLD edge
- RA-hermetic: two cold offline runs byte-identical
- frozen re-admission held-out checksum (md5): `9CEC01392BFB991EBC92F967AD7A660F`

The self-learning loop is closed and certified: admit -> park-in-MEMORY-when-ungrounded ->
re-admit-on-grounding, with the floors immovable, cross-channel coverage terminal, the loop
idempotent and terminating, and hermeticity preserved through the two-phase grounding split.

---

## 7. Coverage limitations

- Channel-inherited coverage. The gate is only as strong as the verdict it consumes. It
  protects the substrate against the internal-contradiction failure mode the certified
  channel catches. Out-of-channel dirt (anachronism, numeric false-precision, misattribution)
  arrives as ABSTAIN and is correctly floored to MEMORY, never GOLD; the gate does not claim
  full GOLD purity, only monotone improvement on the certified channel plus a strict honest
  floor. This is not a cross-channel reopen; cross-channel coverage remains terminal.
- Conservative recall cost. A genuinely tier-worthy claim the verifier abstains on is denied
  GOLD permanently unless a certifying channel for its dirt type is built. This is a
  deliberate safety-first trade: zero false admission to a permanent substrate is preferred
  over recall on the GOLD side. The claim survives in memory and remains re-admittable if its
  channel is ever built and it later passes as CLEAN.
- Grounding-trust boundary. The gate trusts the Phase-1 `grounded` flag. A bad source on a
  false claim would be admitted -- but this is the identical exposure first admission already
  has; re-admission adds no new exposure. Source soundness is an upstream R4 concern.

---

## 8. Provenance

Lineage (priority/provenance record): tiering-gate design and pre-registration; gate build
and frozen held-out; gate measurement (five bars GREEN, public); re-admission design and
pre-registration; re-admission build and frozen held-out; re-admission measurement (six bars
GREEN, public). Generate and evaluate were held in separate planes at every step -- a build
plane never grades its own output. Public reproducibility artifacts: gate code, the two
measurement scripts, and the two aggregate eval reports. Held-out sets, per-row reports, and
harnesses are local-only and never published.
