# STRATEGY — rung C (value/weakness axis)
*concept locked 2026-06-23. BUILD reads this; do not relitigate the axis design here.*

## 0 PROBLEM (from Phase 7 result)
Phase 7 BUILD plumbing is CLOSED but the two PROBATIVE gates are blocked on one
missing mechanism:
  T1b   corr(value, verdict) < 0.50   -- blocked: router has no value axis ⟂ verdict
  D-GATE curated rate_f < uncurated   -- blocked: generate ignores curated memory,
                                          records carry no per-weakness tag
Both reduce to: there is no value/weakness signal independent of the verdict.

## 1 THE ONE MECHANISM (three consumers, one root)
Not three tasks. One substrate built from SELECT's weakness + o0_retrieve's signal,
feeding three consumers:

    weakness-tag (from SELECT)  +  retrieval-signal (from o0_retrieve)
              |                              |
              +--------------+---------------+
                             v
        delta-3  per-weakness tag      : stamp targeted_weakness on each record
        delta-2  conditioned generate  : retrieval-signal shapes generation
        delta-1  value axis            : value = f(weakness_relevance, info_gain)
                                          -- BOTH inputs verdict-blind

## 2 AXIS DESIGN — decision (R3: alternatives recorded, then one chosen)
How to define `value` so corr<0.5 is BY CONSTRUCTION, not by hope:

- (A) utility-driven: value = "was retrieved AND improved downstream". Naturally
      ⟂ verdict, but CIRCULAR (value defined by what D-GATE measures) and slow
      (needs cycles). REJECTED: circularity + cost.
- (B) feature-driven: value = specificity/falsifiability/novelty scored at
      write-time. Fast, deterministic, auditable, BUT the proxy can correlate with
      verdict (ABSORB tends more specific) -> corr<0.5 NOT guaranteed. REJECTED:
      no structural orthogonality guarantee.
- (C) composed-from-shared-substrate [CHOSEN]:
      value = weakness_relevance (delta-3 tag) × info_gain (delta-2 retrieval
      distance). Neither input reads verdict -> orthogonality is STRUCTURAL.
      REJECT on a targeted weakness = high value (evidence); redundant ABSORB =
      low value. No new oracle: the axis is composed from the outputs of 2 and 3.
      Scoring stays a thermometer, not DNA.

## 3 BUILD ORDER  3 -> 2 -> 1  (rationale)
- delta-3 FIRST: cheapest; precondition for measuring both T1b and D-GATE.
  Controller already selects the weakness in SELECT — just persist it onto the
  written record (targeted_weakness field). Unblocks _matches_weakness filtering.
- delta-2 SECOND: gives the causal arm separation (curated != raw) AND surfaces
  the retrieval distance that delta-1 needs as info_gain.
- delta-1 LAST: REUSES outputs of 3 and 2 -> literally one mechanism, not a
  separate scoring oracle.

## 4 INVARIANTS (load-bearing, not optional)
- FIREWALL: conditioned generate may read curated MEMORY; verify stays SEALED.
  The value axis NEVER feeds verify (else circular self-confirmation).
  generate() and verify() remain disjoint injected functions sharing no fields.
- GOLD write-FROZEN persists (propose-only, 0 autonomous writes; T4 bar=0).
- DISK WINS; substrate sealed md5 7C9662EE...AAA5 (220/120). BUILD reads real
  interfaces (o0_tier_router, generate_step6, o0_retrieve, self_model) BEFORE
  writing code. No guessed schemas (§3.7).

## 5 PRE-REGISTERED FALSIFIERS (set BEFORE build; falsifier-first)
- T1b:  corr(value, verdict) < 0.50
        AND value is NOT verdict-separable: the value distributions for ABSORB
        vs REJECT records must OVERLAP (if cleanly separable, value is a hidden
        verdict proxy -> FAIL even if corr happens < 0.50).
- D-GATE: arms genuinely differ. Sanity precondition: for the selected weakness,
        the curated view retrieves >=1 relevant record that the raw view lacks.
        Then curated rate_f <= uncurated rate_f - 0.10 over >=6 cycles/arm,
        fa_live=0 both arms.
- Verifier precision (carried IDEA, not a rung-C gate yet): attribution-level
  conflation (BEC Cornell/Wieman vs Ketterle) remains a known v1 verifier limit.

## 6 BUILD SUBSTRATE (pack these to read; do NOT guess interfaces)
- o0_tier_router.py   -- where the value axis is grafted (delta-1)
- generate_step6.py   -- conditioned generation (delta-2)
- o0_retrieve.py      -- retrieval signal / info_gain source (delta-2, delta-1)
- self_model.json     -- weakness cards for tagging (delta-3)
GOLD need: NONE (axis is composed from local signals, not GOLD corpus).

## 7 LADDER POSITION
rung C delivers value axis + conditioned generation + weakness tagging ->
T1b + D-GATE fire as the TRUE phase proof -> rung D = closed autonomous loop.
