# ONTO STRATEGIC MAP
*single source of truth: NEXT / BLOCKED / IDEAS per plane. v2026-06-24a.*

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

## NEXT -- rung C BUILD (value/weakness axis) [concept locked: reports/STRATEGY_rungC.md]
Concept CLOSED (variant C: value = weakness_relevance × info_gain, verdict-blind
inputs; build order 3->2->1). delta-3 DONE (8ed8e10). Remaining, order delta-2 -> delta-1:
  delta-2  Wire Step-6 conditioned generate (generate_step6.py) into the live
     controller path so curated memory causally shapes generation (curated arm !=
     raw arm). Surfaces retrieval distance for delta-1 info_gain. With delta-3
     (done) -> unblocks D-GATE.
  delta-1  value = weakness_relevance (delta-3) × info_gain (delta-2 retrieval
     distance), grafted into o0_tier_router; verdict-blind inputs. -> unblocks T1b
     (target corr(value,verdict) < 0.50 AND value NOT verdict-separable).
Then T1b + D-GATE fire as the TRUE phase proof. TYPE C (design locked, build only).
Triggers: "rung C delta-2" (next) OR "rung C BUILD".

## BLOCKED
- T1b (corr < 0.50): blocked on value axis (delta-1). Root: router tiers on
  verdict+novelty only -> value ~ inverse(verdict). Proof + record:
  reports/PHASE7_T1_split.md.
- D-GATE (curated rate_f < uncurated by >=0.10): blocked on conditioned generation
  (delta-2). Weakness tagging DONE (delta-3, 8ed8e10). DO NOT run --gate d for a
  verdict yet (arms non-differentiable until delta-2). Record: reports/PHASE7_DGATE_rungC.md.

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
- rung C CONCEPT CLOSED; reports/STRATEGY_rungC.md locked (variant C: value =
    weakness_relevance × info_gain, verdict-blind; build order 3->2->1).
- rung C delta-3 DONE 8ed8e10 (per-weakness tagging: controller stamps SELECTed
    disposition post-verify, router reads tag verdict-blind; dry-val PASS --
    no-regression sealed 220 wrel=0 + liveness tag->permanent; firewall+T2 held).

## ARCHIVE
- "T3 escalation to GOLD_MINIMAL_T3" (pre-G3-close idea): superseded by rung-C
  conditioned-generate plan; revisit only if rung-C frame proves insufficient.
