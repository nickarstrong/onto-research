# S2B verifier loop - public ledger

Date: 2026-06-15
Repo: onto-research (public)
Run: automated end-to-end turn, CPU, B2 generation executed.

## What this records
The keystone loop: the substrate PROPOSES citations; an external gate plus an
independent judge DISPOSE. A citation enters the knowledge record only if it
survives every leg. This is one legible turn over four planted items.

## Result
VERDICT: PASS. Four items, four correct dispositions, automated, no human in the
resolve / retraction / binding path.

| Item                  | Class                                   | Disposition                  |
|-----------------------|-----------------------------------------|------------------------------|
| Fabricated citation   | does not resolve                        | HARD_REJECT at resolve gate  |
| Retracted citation    | flagged retracted                       | HARD_REJECT at retraction    |
| Wrong-binding citation| real source, does not support the claim | REJECT at judge              |
| Clean citation        | resolves and supports the claim         | ABSORBED                     |

## What each leg proves
- Fabrication is caught before it enters the record. A citation that does not
  resolve is rejected, not guessed around.
- Retraction is caught independently of resolution. A real but withdrawn source
  does not pass.
- Wrong-binding is caught by the judge. A real, resolving citation that does not
  support the claim is rejected, not waved through on surface validity.
- A clean citation that resolves and supports the claim is absorbed without
  manual review.

## Boundary (stated, not hidden)
The wrong-binding item was rejected via an abstain verdict from the judge, not an
affirmative contradiction. The loop is safe either way - abstain routes to
rejection - but a judge that affirmatively separates support from non-support is
the next measurement, not a closed result. A real fabrication / wrong-binding
RATE over a live proposer on n>30 is not yet measured; this turn is a single
planted draw.
