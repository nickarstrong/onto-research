# PHASE 7 — D-GATE rung-C reassignment + 3.2 controller wiring

date: 2026-06-23
session: Phase 7 BUILD, TYPE C (build/verify against on-disk substrate)
decision: Founder (B1 — wire now, D-GATE -> rung C)
substrate read: run_step7_live.py (350 lines) · controller.py (397 lines)

## 0 VERDICT

3.2 controller wiring: DONE (subprocess -> controller.py --live, real interface).
3.3 D-GATE: NOT a meaningful falsifier at v1. Reassigned to rung C.
This is NOT a lowered bar. The v1 architecture lacks the mechanism D-GATE requires,
exactly as T1b lacks the value axis. Both are rung-C.

## 1 WIRING (3.2) — what was wired

run_step7_live._run_one_controller_cycle() previously raised NotImplementedError.
Now: subprocess [python controller.py --live --cycles 1 --n 1], cwd = lab/dpo.
  - controller's live absorb writes to eval/o0/o0_verdicts.jsonl == VERDICTS_RAW.
  - --n 1 => 1 generated claim => 1 appended record => lossless 1:1 routing,
    matching the function's single-record return contract.
  - generate-adapter-AGNOSTIC: forward-compatible. When rung C swaps
    live_adapters().generate for a retrieval-conditioned generator, this
    invocation is unchanged.
Edit was surgical: only the WIRE block changed; remaining 350 lines byte-identical
(diff retained). py_compile PASS.

Value delivered now: run_step7_live can run REAL cycles (not mock) through tier
routing — curated-view write, TTL tick, tombstones on live records. That is a
genuine live-plumbing path. What it does NOT deliver: arm differentiation.

## 2 WHY D-GATE IS INERT AT v1 (measured from source, not asserted)

run_dgate's entire A/B contrast flows through verdicts_source (curated vs raw)
passed into _run_one_controller_cycle. But controller.live_adapters().generate
(controller.py 299-305) generates from DOMAIN_TOPICS[cursor] via generate_claim();
it reads NO memory, and controller.py exposes NO CLI arg to inject a curated view
into generation.

  Consequence 1: no causal path curated -> generation. Arm A and Arm B generate
                 identically => rate_f improvement ~ 0 => D-GATE FAIL by
                 construction. That is a FALSE FAIL (measures nothing), not a
                 disproof.
  Consequence 2: _matches_weakness returns True for all records (no per-weakness
                 tag), and rate_f is computed over the whole growing VERDICTS_RAW
                 (220 + N). Any new-batch signal is diluted ~220:N.

## 3 SAME CLASS AS T1b

  T1b:    needs a value axis orthogonal to verdict in the router.
  D-GATE: needs (a) retrieval-conditioned generation — generate() consuming the
          curated memory view (this is Step-6 generate_step6.py, NOT wired into
          live_adapters().generate), AND
          (b) per-weakness record tagging so _matches_weakness can filter.
Both require controller/router architecture work = rung C. Confirmed by in-code
notes (_matches_weakness, _compute_arm_stats: "requires controller tagging rung
C/D") and pack Sec 5 (weakness_relevance STUB, activates rung C).

## 4 HARD RECORD (do not soften downstream)

  D-GATE unresolved at v1
  arms non-differentiable: generate() ignores curated memory
  rate_f overall + diluted (220:N), no per-weakness filter
  axis of improvement NOT demonstrated
  rung-C responsibility

  D-GATE deferred BY DESIGN: failure source is controller-generation architecture
  (unconditioned generate + untagged records), NOT wiring quality. Wiring is
  complete and forward-compatible; the falsifier cannot fire meaningfully until
  rung C adds conditioned generation + weakness tagging.

## 5 OPERATIONAL CONSEQUENCE

  DO run: python run_step7_live.py --gate t2   (live firewall byte-identity)
          python run_step7_live.py            (live plumbing: real cycles routed)
  DO NOT run for a verdict: --gate d  (inert; will report ~0 improvement = false
          fail). If run for plumbing-smoke, label output NON-PROBATIVE.

## 6 LADDER

  Phase 7 BUILD: plumbing CLOSED (T1a + T2-T5). 3.2 wiring DONE.
  OPEN -> rung C: T1b (value axis) + D-GATE (conditioned generate + weakness tag).
  rung C is the real North-Star rung: discipline generalized via an independent
  value/weakness axis, then D-GATE fired as the true phase proof.
