# report_tier -- SPEC sec9 step4 (tier assembly T0-T4 + D2 G-floor)

VERDICT: PASS. Tier ladder T0-T4 assembled; D2 G-floor enforced; all tiers reachable; no path collapse.

## composition (new step4 logic)
final_tier = step2 L4 tier (wire_provenance_L4.tier_of_live, which reuses frozen run_E39_probe)
             + AXIS-G grade + L5 corroboration  ->  SPEC tier (sec3).
No model, no GPU. The L4 rule remains sourced from the frozen organ via the import chain (zero duplication).

## tier mapping (SPEC sec3)
- no marker (no DOI)                                   -> T3 (markerless; ungrounded, NOT false)
- provenance T4_* (non-resolve/mismatch/retracted)    -> T4 (failed/fabricated; ASYMMETRY T4<T3)
- L1L2_PASS, grade UNKNOWN                             -> T1 (fail-closed on grade; cannot award T0)
- L1L2_PASS, grade < floor (preprint/fringe/ID/EoC)   -> T2 (grade-degraded; weak corroboration only)
- L1L2_PASS, grade >= floor, bind holds, L5 corrob.   -> T0 (GOLD primary) -- the ONLY T0 path
- L1L2_PASS, grade >= floor, bind unchk/contra OR not corroborated -> T1 (ceiling)

## D2 G-FLOOR (validated)
T0 requires AXIS-G >= observational/peer-reviewed. Identical inputs, preprint vs observational:
  preprint + bind-holds + L5-corroborated -> T2  (blocked)
  observational + bind-holds + L5-corroborated -> T0
Closes the tier-side axis collapse (a clean-DOI low-grade source cannot back-door T0 via corroboration).

## CEILING (by design, not a defect)
In production l5_corroborated stays False until step3 (L5 independence, D3) lands -> the T0 path is wired
but UNREACHABLE -> operating ceiling = T1. step4 wires the path; step3 unlocks it.

## grade source (flagged dependency)
AXIS-G is supplied per source (fixture grade field) or via the GRADE_RANK starter map (rct/observational/
peer_reviewed >= floor; review/preprint/opinion + venue-integrity flags fringe/ID-venue/predatory/EoC < floor).
A LIVE venue->grade resolver (publication-type + venue-integrity lookup) is a follow-on; unknown -> fail-closed.
ASSUMPTION (adjustable): "review" treated below the observational floor per SPEC sec1 hierarchy
(RCT > observational > review > preprint > opinion).

## selftest
All of T0,T1,T2,T3,T4 reached; G-floor blocks preprint from T0; unknown-grade fail-closed; no collapse (E23).

## artifacts
- wire_tier.py (committed alongside this report). Composes wire_provenance_L4 -> run_E39_probe (frozen).
