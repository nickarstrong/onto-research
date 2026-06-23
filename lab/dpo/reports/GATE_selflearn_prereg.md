# GATE_selflearn — PRE-REGISTRATION (sealed)  [v2]

- v1 sealed: 2026-06-24 (committed 083649a, public, dated).
- v2 amend: 2026-06-24 -- review caught two design holes of the v247 class
  (unsatisfiable / hollow-witness). BUILD NOT yet run -> amend with dated note is a
  pre-build instrument-fix, NOT a goalpost move. Grounded on disk bytes
  (controller.py 4a31e7e1, o0_retrieve.py ef5d96a2, o0_verdicts head5), not memory.
- front: autonomous self-learning loop (rotation ON, no gate-pin, multi-weakness, Step5 daemon).
- GOLD need: NONE.
- self_model.json (disk authoritative) = 3 weaknesses:
  fabricated-specifics (high), overconfident-no-source (high), empty-hedge (med).

## CLAIM (H_learn) -- v2, mechanism-explicit, direction NOT assumed
Under FREE rotation (no pin), as a weakness accumulates a clean retrievable conditioning
pool, its rate_f changes along its own visit experience. v1 asserted rate_f FALLS via
"cleaner conditioning"; the rung-C signal (injected sealed facts -> rate_f 0.9 vs empty
context -> 0.0) shows that direction is UNESTABLISHED and possibly inverted. So v2 does NOT
assume the sign: the gate TESTS whether retrievable-clean conditioning lowers rate_f.
- H_learn (primary): rate_f(late) < rate_f(early) - Delta on M weaknesses AND clean
  retrievable pool grows -> organism learns through cleaner retrieval.
- H_null / inversion (pre-registered, falsifiable): retrievable-clean conditioning does
  NOT lower (or raises) rate_f -> organism does not learn via retrieval; the rung-C "empty
  context is cleaner" effect dominates. A clean FALSIFICATION of H_learn, not a failed run.
- Sub-hypothesis (separate, falsifiable): injecting ANY abstract-text into proposer context
  provokes over-elaboration -> fabricated specifics. Tested by comparing rate_f on visits
  with non-empty retrieval vs empty retrieval for the same weakness.

## P0 PRECONDITION (HARD) -- topic-on-absorb schema fix (was FIX-OWED, now blocks the gate)
GROUNDED on bytes. read-contract (o0_retrieve.py ef5d96a2):
  load_confirmed filters verdict=="ABSORB"; retrieve token-overlaps on TOP-LEVEL r["topic"]
  (string); returned fact = TOP-LEVEL r["claim"] (string) + r["best_abstract"].
schema-diff (CONFIRMED on disk):
  sealed o0_ (head5): top-level topic(str) + claim(str) + best_abstract -> FULLY retrievable.
  live ctrl_ (controller.absorb:375): topic NESTED in claim={topic,claim}; claim is a DICT
  not a string; NO best_abstract -> retrieve() over a curated ctrl_-only pool = [] (the §2b
  symptom). Root = impoverished WRITE schema, NOT a "drop".
FIX (absorb rewrite, grounded, ready for BUILD): lift topic to top-level string; flatten
  claim to its string; add best_abstract field (empty, see WATCH); harden id with a uuid
  suffix (closes dup-id by construction). verify() seam (bb2e8a71) UNTOUCHED -- the edit is a
  post-verify WRITE only (same contour as the targeted_weakness stamp); firewall holds.
P0 is a MEASURABILITY precondition: it makes the curated ctrl_ pool retrievable so the
  witness can be measured. It does NOT guarantee the SIGN of the effect -- that is the test
  (see H_null/inversion). P0 fixes the instrument; it does not pre-decide the result.

## TIME AXIS
Per-weakness VISIT INDEX, not global cycle. early/late = first/last K/2 visits of w.

## SIGNALS (all mandatory)
- OUTCOME  rate_f(w): REJECT / n_relevant of a visit's generated candidates.
- MECHANISM-PRESENCE clean-count(w): confirmed-clean records in w's conditioning pool / visit.
- MECHANISM-USE (Hole-3 fix) retrieval-hit(w): count of records retrieve() ACTUALLY returns
  for w's topic at generate time (k>0). volume in the pool != used in conditioning; without
  the P0 fix retrieval-hit is structurally 0, so it is the real use-witness.
- Pairing: rate_f drop with retrieval-hit>0 AND clean-count rising = learning. rate_f drop
  with retrieval-hit==0 = NOT via retrieval (empty-context effect) -> H_null region.

## COLD-START (Hole-1 fix) -- Founder-sealed: EMPTY
visit-1 curated pool = EMPTY (max headroom; born-saturated impossible). The organism
accumulates its own pool from zero in the fixed schema. Headroom precond: if rate_f(visit-1)
< floor + Delta for a weakness, that weakness has no room to fall -> its bin is non-probative
for this run (F3-class), re-run/re-seed, do NOT read as "did not learn".

## PRE-REGISTERED FALSIFIERS
| F  | condition                                                          | verdict                          |
|----|--------------------------------------------------------------------|----------------------------------|
| F1 | rate_f(late) > rate_f(early) - Delta on >=1 active weakness         | FAIL (H_null/inversion stands)   |
| F2 | clean-count(w) flat/decreasing (pool not accumulating)             | FAIL                             |
| F3 | rate_f moves BUT retrieval-hit==0 / pool < floor / w < K visits    | INVALID (non-probative), re-run  |
| F4 | fa_live > 0 on any cycle                                           | HARD ABORT, run void             |
F3 carries the v247 §5 learning: an unmeasurable/under-sampled bin is declared non-probative
and re-run, NOT silently moved or greened.

## PASS-BAR (SEALED 2026-06-24, unchanged numbers + Hole-fixes)
- N_cycles sized so each of 3 weaknesses gets >= K visits. K = 6 (early/late windows of 3).
  Free 3-way rotation -> N ~= 40 target.
- Delta (rate_f drop) >= 0.20 on M = 2 of 3 weaknesses; 3rd at minimum non-rising.
- clean-count(w): late > early on the same M. retrieval-hit(w) > 0 on measured visits.
- floor F = 5 clean records in pool at every measured visit (below = under-sampled -> F3).
- fa_live = 0 across ALL N cycles (structural at controller, not post-hoc).
- SELECT visited all 3 weaknesses (no single-weakness lock) -- verified in log.

## WILD-PURITY DECISION (Founder-sealed)
Rotation FULLY FREE. SELECT NEVER nudged/round-robined. Miss K visits -> bin non-probative
for THIS run -> re-run longer. Honesty of the claim ("learns AS IT LIVES") > measurement
convenience. A round-robin nudge contaminates the wildness the claim is about -- rejected.

## REBASELINE + ANCHOR CLASS (Founder-sealed, irreversible)
Clean rebaseline from scratch (mixed schema rejected: topic-richness would correlate with
sealed-vs-live = provenance/recency confound of the same class we cleared in PATH 2a).
- NEW anchor = machine-verified regen pool (controller.verify), in the fixed ctrl_ schema.
  "pristine" for GATE_selflearn = MACHINE-VERIFIED baseline, NOT Founder-sealed ground-truth.
  Two senses of "sealed" kept disjoint (avoids the topk_differs naming trap).
- E15 Founder-sealed ground-truth = old 220 @ md5 7c9662ee -> ARCHIVED DATED as the rung-C
  provenance artifact. NOT a working baseline. E15 (only Founder authors sealed truth) is
  NOT violated: the new anchor is explicitly NOT Founder-sealed.
- GATE_selflearn is a SINGLE autonomous run (no arm-swap) -> the rung-C pristine-restore-
  between-arms ritual does NOT apply. The "anchor" here = start-state (EMPTY) + fixed schema,
  not a 220-record restore pool.

## WATCH (not gate blockers)
- best_abstract structural-empty for ctrl_ (Founder-sealed A): live verify() = temporal
  oracle, produces no literature abstract. snippet_audit will flag ~100% of ctrl_ CONFIRMs as
  un-auditable. Witness unaffected (clean-count from verdict). Backfill = separate front
  (would need verify-side retrieval = sealed seam, or a post-verify enrichment step).
- dup-id (o0_045 et al.) CLOSED BY CONSTRUCTION in the new pool via the uuid id-suffix.

## FIREWALL INVARIANTS (carried, non-negotiable)
- verify() seam SEALED (md5 bb2e8a71). P0 + gate touch SELECT/run/measure/WRITE-schema ONLY,
  never verify(). absorb() confirmed OUTSIDE the sealed perimeter (grep, controller.py).
- GOLD/episodic memory never enter the verification path. fa_live=0 structural at controller.
- DISK WINS: pre-run md5; archive old anchor dated before regen.

## LADDER REORDER (consequence of the read-side audit)
immediate front = topic-on-absorb BUILD (TYPE C, schema change -> establishes the new
machine-verified empty-start baseline). GATE_selflearn instrument BUILD is GATED BEHIND it
(no point instrumenting a witness over a non-retrievable pool). Then the ~40-cycle run + read.

## STATE
[STAGE: CONCEPT CLOSED -- pre-reg v2 sealed, grounded]
NEXT: topic-on-absorb BUILD (TYPE C) -- patch controller.absorb() (grounded rewrite), verify
new ctrl_ records carry top-level topic(str)/claim(str)/best_abstract + retrieve() non-empty
over a fresh curated pool + uuid id unique + verify() md5 bb2e8a71 unchanged, archive 220
dated, confirm empty curated start. No eval, no gate run in that session.

---
*GATE_selflearn pre-reg v2 - 2026-06-24 - amended pre-build after read-side audit (grounded:
controller.py 4a31e7e1, o0_retrieve.py ef5d96a2, o0_verdicts head5). Holes closed: (1) cold-
start EMPTY + headroom precond; (2) H_learn direction NOT assumed (H_null/inversion + empty-
context sub-hypothesis), P0 = measurability not result; (3) retrieval-hit use-witness added.
P0 = topic-on-absorb promoted FIX-OWED->PRECONDITION (lift topic top-level, flatten claim,
best_abstract field, uuid id). Rebaseline clean; anchor = machine-verified (NOT Founder-sealed,
disjoint sense); 220@7c9662ee = dated rung-C archive. dup-id closed by construction. verify()
seam untouched (bb2e8a71); absorb() outside FROZEN. Numbers (N~40/K6/Delta0.20/M2-3/floor5/fa0)
unchanged. From v1 (083649a).*
