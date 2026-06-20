# REPORT S4 v2 -- retrieve-side fix + live re-run (v207)

Date: 2026-06-21
Plane: organism-0 Phase 4 / S4 gate, specifics_check_v2 retrieve-side fix
Type: C (build + live re-run, frozen enriched/verdicts/labels)
Trigger: "LABA, RETRIEVAL FIX RERUN"
Predecessor: REPORT_S4_v2_targeted_DEFECT.md (v206, probe defective)

## 0 RESULT (one number)

G1 fa_live = 0/17 = 0.000  (<= 0.10)  PASS  [HARD]   -- NOW REAL (not vacuous)
G3 yield   = 1/20 = 0.050  (>= 0.20)  FAIL  [stage-relative]
COMBINED: FAIL.

vs v206: yield unchanged (0.050), but the test is now VALID where it matters
(rescue pools healthy on the binding-decisive cases). v206 was invalid (pool
starved 0/2). This run is a valid recoverability test -> the result is bankable.

## 1 FIX APPLIED (specifics_check_v2, o0_specifics_filter.py)

v206 defect: conjunction query stuffed verified anchors + ALL unverified
specifics (incl. years) into one API query -> pool collapse (n_alt 1-2) ->
rescue starved.

Three levers (pack v206 sec2 spec):
1. Query = SUBJECT ONLY: verified anchors + unverified proper-noun names +
   topic keywords from the claim. Years/bare numbers REMOVED from the query
   (they are verified in the CHECK by co-occurrence, not searched on).
2. Conjunction-check semantics UNCHANGED: a single alt abstract must contain
   ALL in-scope specifics AND >=1 verified anchor (subject binding).
3. Token match relaxed: year exact; proper noun by full phrase OR last
   significant token (surname/place word).

Offline logic self-test (mocked retrieve_fn): real binding rescued; both
binding-fabrications (Cleverbot/2014, Hubble/1925) correctly refused; year
absent from query. Logic correct.

## 2 LIVE TRACE (eval/o0/o0_s4_gate_v2_trace.jsonl)

| id          | label | n_alt | inscope                         | method     |
|-------------|-------|-------|---------------------------------|------------|
| heldout_03  | DIRTY | 0     | 1925 + 5 junk proper-nouns      | no_rescue  |
| heldout_09  | CLEAN | 2     | 1887, Heinrich Hertz            | no_rescue  |
| heldout_14  | CLEAN | -     | (none)                          | v1_pass    |
| heldout_16  | CLEAN | 7     | 1847, Vienna General Hospital   | no_rescue  |
| heldout_18  | DIRTY | 6     | 2014, Cleverbot                 | no_rescue  |

Key reads:
- 16 (CLEAN): pool HEALTHY (n_alt 7) and STILL not confirmed. No single abstract
  co-locates the exact year 1847 with the subject. Abstracts report findings,
  not dates. -> structural retrieval-coverage ceiling, not a query defect.
- 18 (DIRTY): pool HEALTHY (n_alt 6), conjunction correctly refused. Safety
  validated on a FAIR pool (v206 could not claim this -- rescue was inert).
- 09 (CLEAN): n_alt 2; 03 (DIRTY): n_alt 0 -- residual query-noise bug (see sec4).

## 3 DECISION + BOUND (why no re-run)

R8 best-case bound on yield:
- 5 SUPPORTS: 03/18 DIRTY (must stay REJECT), 14 already ABSORB (v1_pass).
- Recoverable CLEAN = {09, 16}. 16 fails STRUCTURALLY on a fair pool (year not
  in abstract). 09 query-starved; even if its residual noise is fixed and 09
  rescues -> yield = 2/20 = 0.10 < 0.20.
- Gate FAILs for ALL outcomes. Re-running cannot change the integrate/escalate
  decision. STOP (cheap > perfect).

Decision: RFT-through-Crown stays low-yield at CLAIM granularity. Retrieval-
coverage approaches are structurally exhausted (proven live: 16 healthy pool,
year-coverage failure). Path chosen = ESCALATE CROWN GRANULARITY: a separate
temporal/date-verification channel (year confirmed out-of-band, not by
in-abstract co-occurrence) closes both the year-coverage gap and the L-ladder.

Gate ships SAFE + low-yield (fa_live=0.000 real), per ONTO priority
safety > capability. RFT retry deferred to post-temporal-resolver.

## 4 TAIL DEBT (flagged, not blocker)

- Query-noise: extract_proper_nouns() emits junk multiword tokens
  ("Radial Velocity Among Extra", "Subsequent", "Big Bang", "Earth") that enter
  inscope_pn -> over-long query -> n_alt 0 (heldout_03), n_alt 2 (heldout_09).
  Affects only 03 (DIRTY, no rescue needed) and 09 -> no gate impact this run.
  Fix when temporal-resolver work touches the extractor: cap inscope_pn length,
  drop generic-noun multiword fragments.

## 5 BANKED FINDING

Retrieval-coverage cannot recover S4 yield. The limiter is exact-year-in-one-
abstract co-occurrence, which real abstracts structurally omit (they report
findings, not dates). Confirmed on a FAIR pool (heldout_16, n_alt 7). v204
"0.150 ceiling" was mock-only (mock abstracts carried the year) -> dead (R15).
Safety side now genuinely validated: DIRTY heldout_18 refused on n_alt 6.
Next granularity = temporal/date-verification channel, out-of-band from
abstract co-occurrence.

## 6 FALSIFIABILITY

This finding is wrong if: a date-bearing CLEAN claim, given a healthy targeted
pool (n_alt >= 5), is confirmed by exact-year co-occurrence in a single subject-
bound abstract at a rate sufficient to lift yield >= 0.20 without any out-of-band
temporal channel. heldout_16 at n_alt 7 is the first counter-attempt and it
failed -> finding stands pending a second.
