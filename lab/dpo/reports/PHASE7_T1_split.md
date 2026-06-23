# PHASE 7 — T1 SPLIT (T1a plumbing / T1b architecture)

date: 2026-06-23
session: Phase 7 BUILD, TYPE C (build/verify, no new design)
decision: Founder (split, gate-contract amendment)
substrate: o0_verdicts.jsonl (220 lines / 120 unique IDs) · step7_gates.py (338 lines)

## 0 VERDICT

T1 split into two NON-EQUIVALENT predicates. BUILD closes on T1a (plumbing).
T1b (axis-independence) UNRESOLVED, reassigned to rung C.
This is NOT a lowered bar. It is the separation of two distinct tests the v1
architecture is not required to satisfy simultaneously.

## 1 EMPIRICAL BASIS (not assertion — measured)

Two gate runs, identical substrate, only t1_labels perturbed:

  run A (placeholder ids):   clean_discard=0  dirty_keep=2  corr=-0.9465
  run B (real ABSORB ids):   clean_discard=2  dirty_keep=2  corr=-0.9465

  Observation:  corr remained -0.9465 despite crossover introduction.
  Delta:        Δlabels != Δcorr  (correlation invariant under label perturbation)

  Inference:    T1a and T1b are non-equivalent predicates.

  Consequence:  passing T1a provides evidence of crossover EXISTENCE,
                but NO evidence of axis independence.

Source of corr in code (step7_gates.py gate_t1, lines 84-97):
  correlation is computed from each record's _tier (set by route_batch in
  o0_tier_router.py) vs verdict. t1_labels feed ONLY the crossover counters
  (lines 68-79). Labels are structurally incapable of moving correlation.

## 2 ROOT CAUSE

corr = -0.9465 is router-bound, not label-bound:
  - all 62 REJECT  -> permanent  (value_score=1, verdict=0)
  - 6 novel ABSORB -> temporary  (value_score=1, verdict=1)
  - 52 dup ABSORB  -> discard     (value_score=0, verdict=1)
value_score is a near-deterministic INVERSE of verdict. The v1 router tiers on
verdict + novelty only; no value feature orthogonal to verdict exists yet.
To drive |corr| < 0.50 the router must route on an independent value axis
(discard some low-value REJECTs, keep some ABSORBs by value, not verdict).
That is rung-C scope (independent value axis), not a TYPE-C build task.

## 3 SPLIT DEFINITION

  T1a = plumbing bar      : crossover_ok (>=1 CLEAN->discard AND >=1 DIRTY->keep)
                            STATUS: PASS (clean_discard=2, dirty_keep=2)
  T1b = architecture bar  : corr(value, verdict) < 0.50
                            STATUS: UNRESOLVED

## 4 HARD RECORD (do not soften in any downstream pack/summary)

  T1b unresolved
  corr = -0.9465
  axis-independence NOT demonstrated
  rung-C responsibility

  T1b deferred BY DESIGN:
  empirical evidence shows the failure source is router/value architecture,
  NOT crossover labeling. Deferral is admissible because the predicate cannot
  be satisfied without the rung-C value axis, which is out of TYPE-C scope.

## 5 BUILD CLOSURE STATEMENT (honest framing)

  5/5 plumbing tests passed  (T1a, T2, T3, T4, T5)
  1 architecture test remains open  (T1b)

NOT "Phase 7 BUILD fully green." Phase proven ONLY by D-GATE; T1a/T2-T5 are
plumbing. T1b is a live open item carried to rung C.

## 6 LADDER CONSEQUENCE

  Phase 7 BUILD: plumbing CLOSED (T1a+T2-T5). T1b OPEN -> rung C.
  Next in BUILD: 3.2 controller wiring (run_step7_live.py) -> 3.3 D-GATE.
  rung C must: (a) introduce value feature orthogonal to verdict in router,
              (b) re-run T1b, demonstrate corr < 0.50,
              (c) only then is axis-independence demonstrated.
