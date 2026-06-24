# GATE_selflearn — PRE-REG DELTA: SELECT rotation floor (BUILD-FRONT #2)

*Sealed 2026-06-24 · TYPE C build · supersedes nothing; amends SELECT coverage only.*

## 0 Scope
Fixes the FLOOR FAIL in the frozen TYPE B verdict (trace `9c960429`, 40 rows):
only 2/3 weaknesses visited; `empty-hedge` NEVER SELECTed. No eval, no gate run this
session. The rebuilt gate run remains GATED behind all 3 build-fronts.

## 1 Root cause (named against on-disk bytes, commit base md5 controller.py 8533364c)
`select_weakness` (controller.py) sorted eligible candidates by
`(TIER_RANK[severity], cycles_used, idx)` — **severity primary**. self_model carries two
`high` weaknesses (fabricated-specifics, overconfident-no-source) and one `med`
(empty-hedge). `REGRIND_COOLDOWN=1` removes at most ONE weakness from `eligible` per
cycle, so at least one `high` is always eligible and always sorts ahead of the lone
`med`. The two high dispositions ping-pong (A,B,A,B,…) and permanently shield
empty-hedge. cycles_used/idx are secondary keys; they never cross the tier gap.

## 2 Fix (single site, surgical)
`eligible.sort(key=lambda c: (c[0], c[1], c[2]))`  ->
`eligible.sort(key=lambda c: (c[1], c[0], c[2]))`  # (cycles_used, TIER_RANK, idx)

Least-worked PRIMARY guarantees every weakness rotates; worst-severity preserved as the
tiebreak among equally-worked cards. Robust to arbitrary n / tier mix (no magic number).
Firewall (verify path), `--pin-weakness` D-GATE path, and frozen trace untouched.

## 3 Falsifier (PASS-BAR, met)
Isolated smoke `smoke_select_rotation.py` (VIOLATION-A safe: temp CWD + temp goal_stack,
no pre-existing-state mutate). Drives 9 synthetic SELECT->mark_worked cycles, verdict-blind.
- PASS-BAR (1): empty-hedge SELECTed >= 1.
- PASS-BAR (2): all 3 weakness names appear in the SELECT sequence.

Result (patched): `fabricated-specifics overconfident-no-source empty-hedge` x3 ->
empty-hedge x3, all-3-rotate=True -> **SMOKE PASS**.
Negative control (original key): empty-hedge x0, all-3-rotate=False -> **SMOKE FAIL**
(reproduces the frozen floor verdict) -> smoke discriminates.

Disproof condition for the fix: any run of >= 2*n cycles where a non-cooling weakness is
never SELECTed, OR empty-hedge stays at 0 over a full rotation window.

## 4 Carry
- One assumption (R2): the floor is a COVERAGE requirement (each weakness visited), not
  severity-proportional airtime. Fix delivers fair rotation, worst-first tiebreak. If
  proportional weighting is later wanted, that is a separate design (not a floor fix).
- Next: BUILD-FRONT #3 (F1 baseline redesign), then the rebuilt gate run (separate TYPE
  C) + its TYPE B eval (further separate). Never build+eval together.
