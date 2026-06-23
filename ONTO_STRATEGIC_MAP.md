# ONTO STRATEGIC MAP
*single source of truth: NEXT / BLOCKED / IDEAS per plane. v2026-06-23b.*

## PHASE 7 RESULT (2026-06-23)
> Plumbing validated. Architecture hypothesis remains untested.

Phase 7 BUILD plumbing CLOSED. The infrastructure exists in a working live loop
(not mock, not paper): T1a + T2-T5 PASS, 3.2 wiring PASS, fa_live=0, one real
SELECT->...->ABSORB cycle routed end-to-end. What is NOT yet demonstrated is the
appearance of the new CAPABILITY — that lives entirely in T1b + D-GATE, both
reassigned to rung C.

Critical distinction (do not collapse in future sessions):
  T1a PASS        = crossover EXISTS (plumbing).
  T1b OPEN        = axis-independence NOT demonstrated (architecture).
  D-GATE BLOCKED  = NOT failed. The falsifier cannot fire meaningfully at v1
                    (arms non-differentiable). Blocked != disproved.
Some gates measure infrastructure; others measure the emergence of a new ability.
They must never be summed into one score.

## NEXT -- rung C (value/weakness axis) [CONCEPT, new design]
Phase 7 collapsed to ONE architectural problem (good: one gap, not five). The two
unproven areas share one missing mechanism:
    value ⟂ verdict   +   conditioned generation   +   weakness tagging
Deliverables:
  1. Value feature in router INDEPENDENT of verdict -> unblocks T1b
     (target corr(value,verdict) < 0.50; currently -0.9465, INVARIANT under labels).
  2. Wire Step-6 conditioned generate (generate_step6.py) into the live controller
     path so curated memory causally shapes generation (curated arm != raw arm).
  3. Per-record targeted_weakness tag so _matches_weakness filters per-weakness
     (kills the 220:N rate_f dilution). -> together (2)+(3) unblock D-GATE.
Then T1b + D-GATE fire as the TRUE phase proof. This is CONCEPT (changes
architecture), NOT TYPE C.
Triggers: "rung C" (open concept).

## BLOCKED
- T1b (corr < 0.50): blocked on value axis (NEXT.1). Root: router tiers on
  verdict+novelty only -> value ~ inverse(verdict). Proof + record:
  reports/PHASE7_T1_split.md.
- D-GATE (curated rate_f < uncurated by >=0.10): blocked on conditioned generation
  + weakness tagging (NEXT.2/3). DO NOT run --gate d for a verdict (inert ~0
  improvement = false fail). Record: reports/PHASE7_DGATE_rungC.md.

## IDEAS
- relevance-verify on top of existence-verify ("DOI real but wrong source").
  CONNECTS to the rung-C verifier-precision miss below — both are attribution/
  relevance level, not existence level. Candidate separate gate.
- verifier attribution-granularity (NEW 2026-06-23): live ABSORB conflated
  Cornell/Wieman (JILA, Rb) with Ketterle (MIT, Na) as one BEC experiment;
  verifier passed it (granularity = year+subject, not attribution). Attribution-
  level falsification = rung-C verifier scope.
- gate-imprecision (NEW): gate_t1 counts over 220 lines (dup-inclusive), not 120
  unique -> clean_discard inflated (o0_003 counted twice). Harmless at >=1
  threshold; tighten to unique-id dedup at rung C.
- cp1251 mojibake (NEW, cosmetic): generated claim text / contact-drop JSON
  ("В°C"). Source = controller write encoding, not router.

## CLOSED (ladder trail)
- Step 5 daemon PASS (79cfd65).
- Step 6 BUILD PASS; G1/G2/G3 PASS; A/B conditioning PASS (6010835).
- Phase 7 CONCEPT CLOSED (2b60fbf); STRATEGY_phase7_tiering.md locked.
- Phase 7 BUILD plumbing CLOSED:
    T1 split d0ab740 (T1a PASS / T1b->rungC).
    3.2 wiring + D-GATE->rungC 3d408a7 (smoke PASS, substrate restored 220,
      md5 7C9662EE...AAA5).
    T1 worth-labels E15 provenance 4d1cc6c (1 CLEAN->discard + 2 DIRTY->keep).

## ARCHIVE
- "T3 escalation to GOLD_MINIMAL_T3" (pre-G3-close idea): superseded by rung-C
  conditioned-generate plan; revisit only if rung-C frame proves insufficient.
