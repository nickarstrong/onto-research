# GATE_selflearn — PRE-REGISTRATION (sealed)

- pre-registered: 2026-06-24 (BEFORE build; falsifier-first)
- front: autonomous self-learning loop (rotation ON, no gate-pin, multi-weakness, Step5 daemon)
- builds on: rung C PHASE PROOF == PROVEN (commit 0af1770) — "tiering adds value" proven in
  controlled pinned-gate A/B. THIS gate tests the next capability: the organism, AS IT LIVES
  IN THE WILD (free SELECT rotation, no pin), actually LEARNS.
- GOLD need: NONE.
- self_model.json (disk authoritative) = 3 weaknesses:
  fabricated-specifics (high), overconfident-no-source (high), empty-hedge (med).

## CLAIM (H_learn)
Under free rotation (no pin), per-weakness rate_f falls along that weakness's own experience,
and its confirmed-clean conditioning pool grows monotonically. Learning = trend, measured per
weakness, not a one-shot controlled contrast.

## TIME AXIS
Per-weakness VISIT INDEX, NOT global cycle. Global cycle mixes rotating weaknesses; trend is
computed over visits of weakness w in isolation. early/late = first/last K/2 visits of w.

## SIGNALS (both mandatory — anti-ceremonial pairing)
- OUTCOME  rate_f(w): fraction of generated candidates at a visit that verify() sends to REJECT.
- MECHANISM clean-count(w): number of confirmed-clean records in w's conditioning pool at a visit.
- Pairing rule: pool grows but rate_f flat -> no learning. rate_f falls but pool not cleaning ->
  confound, suspect. Both must move together for a probative PASS.

## PRE-REGISTERED FALSIFIERS
| F  | condition                                                      | verdict                          |
|----|----------------------------------------------------------------|----------------------------------|
| F1 | rate_f(late) > rate_f(early) - Delta on >=1 active weakness     | FAIL                             |
| F2 | clean-count(w) flat/decreasing (pool not cleaning)             | FAIL                             |
| F3 | rate_f falls BUT clean-count not rising / pool < floor F       | INVALID (non-probative), re-spec |
| F4 | fa_live > 0 on any cycle                                       | HARD ABORT, run void             |

F3 carries the v247 §5 learning ("a pre-registered bar can be unsatisfiable by construction"):
if a weakness fails to reach K visits OR its pool collapses < F, that bin is under-sampled ->
run declared non-probative and RE-RUN LONGER. Goalposts are NOT moved; not silently greened.

## PASS-BAR (SEALED 2026-06-24)
- N_cycles: sized so each of 3 weaknesses gets >= K visits. K = 6 (early/late windows of 3 each).
  Under free 3-way rotation -> N ~= 40 cycles target.
- Delta (rate_f drop) >= 0.20 on M = 2 of 3 weaknesses; 3rd at minimum non-rising.
- clean-count(w): late-window > early-window on the same M weaknesses.
- floor F = 5 clean records in pool at every measured visit (below = under-sampled bin -> F3).
- fa_live = 0 across ALL N cycles (structural at controller, not post-hoc).
- SELECT visited all 3 weaknesses (no single-weakness lock) — verified in log.

## WILD-PURITY DECISION (Founder-sealed)
Rotation stays FULLY FREE. SELECT is NEVER nudged/round-robined. N is set with coverage margin;
if a weakness misses K visits its bin is non-probative for THIS run and we re-run longer. Honesty
of the claim ("learns AS IT LIVES") > measurement convenience. A round-robin nudge would
contaminate the wildness the claim is about — rejected.

## FIREWALL INVARIANTS (carried, non-negotiable)
- verify() seam SEALED (md5 bb2e8a71). This gate touches SELECT/run/measure ONLY, never verify().
- GOLD/episodic memory never enter the verification path.
- fa_live=0 enforced structurally at controller level.
- DISK WINS: restore from .bak.pristine between measurement contexts; pre-run-check md5.

## WATCH (not a gate blocker)
empty best_abstract subset on novel conditioned CONFIRMs (§6 FIX-OWED) — clean-count is computed
from verdict, not abstract, so the count is sound; but manual "why is this record clean" audit is
blind on those rows. Note when reading results.

## ROUTING (decided at BUILD, not now)
N ~= 40 autonomous cycles. Step5 daemon = local unattended cross-reboot (non-blocking by design)
-> lean local daemon (native env). If per-cycle wall-time read at BUILD says otherwise -> RunPod
fallback. Routed on measured wall-time per §3.7, not guessed here.

## STATE
[STAGE: CONCEPT CLOSED — pre-reg sealed]
NEXT: BUILD (TYPE C) — instrument the daemon to log per-visit {weakness, rate_f, clean-count,
fa_live, select_target}; no bar tuning, no eval in same session.

---
*GATE_selflearn pre-reg v1 - 2026-06-24 - sealed before build. Falsifier-first: F1-F4 + numeric
bar (N~40, K=6, Delta>=0.20, M=2/3, floor F=5, fa_live=0) fixed prior to any run. Free rotation,
no SELECT nudge (Founder). Builds on rung C PROVEN (0af1770).*
