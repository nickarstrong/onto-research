# GATE_selflearn -- TYPE B READ v2 (verdict, read-only)

*Read-only eval of frozen trace `selflearn_trace.jsonl` md5 C1CA1025697FEBE68424085DC649A323
(41 rows = 1 baseline cycle:0 + 40 conditioned), committed e6ee5b0. Sealed falsifier defs
applied: PRE-REG v2 (5ee4402f) + DELTAs F1-baseline / retrieval-wiring / select-rotation.
No build, no re-run, no targets. Diagnose only.*

## STEP 1 -- identity (disk-wins, re-verified container-side)
- md5 == C1CA1025697FEBE68424085DC649A323  PASS
- rows == 41  PASS
- sealed defs present: base prereg v2 + 3 deltas  PASS
- HEAD e6ee5b0 not re-pasted by Tommy; trace byte-identity is the binding substrate check (passed).

## GATE-LEVEL VERDICT: NOT CLEARED (F1 VOID-by-saturation is binding)

The two wiring build-fronts are PROVEN live (F3 retrieval + FLOOR rotation). But the substrate
does not fabricate enough on the current topic-set for the learning effect to be expressible,
so F1 is VOID, not pass. Route = harder claim-distribution (SEPARATE build session). No silent
pass, no goalpost move.

## PER-FALSIFIER

### F4 -- fa_live = 0 across all cycles
max(fa_live) over 41 rows = 0.0. **PASS** (structural, no live-oracle false-accept).

### F1 (amended, supersedes v2 clause) -- HEADROOM checked FIRST
- baseline_rate_f (cycle:0, phase:baseline, blind, retrieval+absorb OFF) = **0.000**.
- HEADROOM precondition (delta sec 3a, R6/R7, binding): baseline_rate_f < 0.30 -> the substrate
  cannot express a >= 0.20 directional drop on this topic-set.
- **VERDICT: F1 = VOID-by-saturation.** Unfalsifiable on this substrate/topic-set. NOT pass,
  NOT fail. Blocks a "conditioning proven" verdict. Routes to a harder claim-distribution where
  blind rate_f >~ 0.30.
- Directional-drop numbers are NON-PROBATIVE (computed off a saturated-floor baseline) and shown
  for transparency only -- none meet 0.20 regardless:
  - fabricated-specifics   late c40 rate_f=0.500 -> baseline-late = -0.500 (ROSE)
  - overconfident-no-source late c38 rate_f=0.000 -> baseline-late = +0.000 (flat)
  - empty-hedge            late c39 rate_f=0.125 -> baseline-late = -0.125 (< 0.20)

### F3 (amended retrieval-wiring) -- STRUCTURAL WITNESS, build-front #1
- F3a: sum(retrieval_hit) over run = **723** > 0. PASS.
- F3b: retrieval_hit==0 only in the single cold cycle (c1); >0 continuously c2..c40 (12..24/cycle).
  PASS on the available witness.
- **VERDICT: F3 = PASS.** v1 was structural 0 across all 40 rows; the live-absorb-trail re-read
  fix (7edca22 / 67862c7) is witnessed working.
- CAVEAT (honest, R2): the trace carries `weakness`/`select_target` (disposition), NOT the
  DOMAIN_TOPIC. So F3b's strict "retrieval_hit>0 on a cycle whose SELECTed topic has a prior
  same-topic ABSORB" cannot be confirmed from the trace alone -- the retrieval_hit>0-from-c2
  timing is the witness available; topic-level pairing would need the absorb trail
  (`eval/o0/o0_verdicts.jsonl`), not shipped. Wiring is live; exact same-topic pairing unverified.

### FLOOR (coverage) -- STRUCTURAL WITNESS, build-front #2
- dispositions SELECTed = 3/3, each >= K=6:
  fabricated-specifics 14 · overconfident-no-source 13 · empty-hedge 13.
- **VERDICT: FLOOR = PASS (coverage).** v1 had empty-hedge 0x (severity-primary lock); the
  least-worked-primary fix (9456fb2 / 46ad281) is witnessed -- empty-hedge now 13x. PLATEAU drops
  (c3 empty-hedge, c32 overconfident) still count as visited.

### F2 (clean-count accumulation) -- UNDER-WITNESSED by this trace
- The trace field `clean_count` = clean generations in the n=8 batch (clean = n*(1-rate_f));
  confirmed: clean+dirty ~= 8 every row. It is a PER-CYCLE clean-gen count, NOT the cumulative
  conditioning-pool size. So it co-moves with (1 - rate_f) and does NOT independently witness
  "pool accumulating".
- Per-disposition early/late (first/last 3 visits): fab 5.33->5.67 (up) · empty-hedge 5.00->6.33
  (up) · overconfident 7.00->5.67 (down). 2/3 "up", but confounded with rate_f.
- **VERDICT: F2 = UNDER-WITNESSED.** True pool accumulation needs absorb-trail length over time
  (absent from trace). Not a clean PASS; not a FAIL. Routed to instrument (emit pool-size per
  visit) in a future run, OR read off the absorb trail directly. Subordinate to F1 VOID either way.
- Clean-record floor=5 breached at 6 cycles (min clean=2 @ c32 overconfident; also c3/c7/c19/c28/c40)
  -> those bins are under-sampled per the floor rule; weakens overconfident's late reads specifically.

## ROOT + ROUTE (hand to SEPARATE build session, not this one)
- ROOT: substrate saturation. qwen2.5-coder barely fabricates on the current 100-topic
  DOMAIN_TOPICS set -> blind baseline 0.000 -> no rate_f headroom. The learning claim is
  untestable here, not disproven.
- ROUTE (NEXT+1, build-only, one plane): harder claim-distribution / topic-set where blind
  rate_f >~ 0.30 (HEADROOM precondition satisfiable), then re-run + re-gate. Secondary: emit
  cumulative pool-size per visit so F2 is directly witnessed; carry the same-topic ABSORB tag into
  the trace so F3b is exactly checkable.

## NO RE-FIRE
TYPE B read = one verdict. Fix = separate build. Not relitigated, not patched here.

---
*GATE_selflearn TYPE B read v2 - 2026-06-24 - trace C1CA1025 (e6ee5b0). F4 PASS · F1
VOID-by-saturation (binding) · F3 PASS (witness, topic-pairing caveat) · FLOOR PASS (coverage) ·
F2 under-witnessed. GATE NOT CLEARED -> route to harder claim-distribution. Build = separate.*
