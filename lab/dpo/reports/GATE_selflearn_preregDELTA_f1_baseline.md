# GATE_selflearn — PREREG DELTA: F1 baseline redesign (BUILD-FRONT #3 of 3)

Supersedes the F1 clause of PRE-REG v2 (sealed 5ee4402f). Floor + F3 already amended
(#2 9456fb2/46ad281; #1 7edca22). This delta closes the last open front before the
REBUILT gate run (separate TYPE C session).

## 1 · Diagnosis (named against on-disk bytes, controller.py @ a3d26b0)

F1 v2 FAILed: max |delta(rate_f)| early→late = 0.0375 → 0/3 dispositions meet ≥0.20.

Root cause = **(c) substrate saturation + structural: no unconditioned reference window.**
- `rate_f` (controller.py:226) = `n_dirty/n_total` of each cycle's GENERATE batch.
  EVERY trace row is emitted from inside the wired/conditioned run. "Early window" was
  merely the first per-disposition visits of that same run — not a pre-conditioning measure.
- Frozen trace (9c960429) witness: cycle-1 fab=0.000, overconf=0.125, and `retrieval_hit=0`
  for all 40 rows → the substrate entered already near-floor AND conditioning never fired.
  qwen2.5-coder barely fabricates on the current topic set → no rate_f headroom for a
  ≥0.20 drop, regardless of conditioning.
- **(b) is literally true but causally irrelevant to F1:** `TIER_BASELINE=0.7`
  (controller.py:50/171) feeds only `improved`/DONE-STUCK (227), NOT the trace `rate_f`
  the F1 reader consumes. Changing 0.7 does nothing for F1.

## 2 · Redesign (single, mechanism)

New `controller.capture_cold_baseline(generate_blind, verify, n, trace_path)`:
- measures rate_f with the **BLIND adapter** (`conditioned=False` → context="" → retrieval
  OFF, confirmed live_adapters else-branch controller.py:396) ;
- writes **NOTHING to the absorb trail** (no absorb arg) → the conditioned run that
  follows starts cold, proposer un-fed;
- emits ONE trace row `cycle:0, phase:"baseline", retrieval_hit:0`.
Daemon: new `--baseline-n`; when `>0 + --live + --selflearn-trace`, runs the capture ONCE
BEFORE the tick loop (daemon.py main, before daemon_loop). Firewall/verify seam untouched
(diff = additions only).

## 3 · Amended F1 falsifier (REPLACES v2 F1 clause)

- **early window** = the single `phase:"baseline"`, `cycle:0` row (unconditioned, retrieval
  +absorb OFF).
- **late window** = the last conditioned visit per disposition (cycle ≥ ceil(max_cycle/2)).
- **PASS** iff, for ≥1 disposition, baseline_rate_f − late_rate_f ≥ 0.20 (directional drop).

### 3a · HEADROOM PRECONDITION (R6/R7 — honest, binding)
The mechanism does NOT manufacture headroom. If `baseline_rate_f < 0.30` (substrate does not
fabricate enough on the topic set for a ≥0.20 drop to be expressible), F1 is reported
**VOID-by-saturation: unfalsifiable on this substrate/topic-set** — NOT pass, NOT fail.
A VOID F1 blocks a "conditioning proven" verdict and routes to a topic-set/claim-distribution
change (harder claims where blind rate_f ≳ 0.30), NOT to a silent pass. No goalpost move:
VOID is recorded as VOID.

## 4 · Falsifier evidence (this session, TYPE C)

`smoke_f1_baseline.py` (self-contained, clone-coherent, no net/GPU; absence-guarded
citation_verify stub so it loads on a bare checkout, real module wins on disk):
- POSITIVE: baseline row `rate_f=0.375` (3/8 DIRTY, headroom present), `retrieval_hit=0`,
  `cycle:0 phase:baseline`; distinct late row (cycle≥1, no phase); early→late |delta| ≥ 0.20.
- VIOLATION-A: save→run→restore — pre-existing trace bytes preserved (append-only).
- NEG-CONTROL: OLD path (no baseline phase) emits no cycle:0 anchor → reader cannot form
  an unconditioned delta → discriminates.
- RESULT: PASS / neg-control discriminates.

## 5 · Gated next (SEPARATE sessions; never build+eval together)
1. REBUILT gate run (TYPE C): COLD-START reset BOTH verdict pool AND goal_stack.json
   (warm stack = empty-hedge front-load skew, pack §6), run with `--baseline-n N`, freeze
   NEW trace.
2. TYPE B eval of the NEW trace vs amended F1 (§3) + F3 + floor falsifiers.

SEAL: F1 clause of PRE-REG v2 superseded by §3 above. Build = additions-only diff;
frozen trace 9c960429 untouched.
