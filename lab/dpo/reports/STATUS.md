# STATUS.md -- current-state snapshot (read after the canon, before the task spec)

date  : 2026-06-13 (e)
plane : RESEARCH / lab. self-checkup loop.

================================================================================
## WE ARE HERE
Phase 2 (disposition-audit) CLOSED. Phase 3 (surgical correction) ACTIVE; substrate UNBLOCKED + CHARACTERIZED.
v111 ran phase-3 step1 on a CONCENTRATED ordinary window (N=33, A2/A4 dropped, frozen base Qwen2.5-Coder-7B,
no adapter/no GOLD; ran LOCALLY on RTX 4070). Organ-tally: A1=0.273 (9/33), A3=0.121 (4/33), A2=A4=0.000;
12/33 trip >=1; floor 10/33 @ tau 0.30. VERDICT: FAIL by 1 (R6 target A1>=0.30 not met; no reframe/tau move).
The FAIL is a COMPOSITION artifact, NOT an A1 ceiling: per-genre A1 = prose-provenance 7/14=0.500 (live,
tau-clearing ALONE) ; result-number 2/12=0.167 (Q2-safe exemption, BY DESIGN) ; vague-magnitude 0/7. prose-
provenance is the validated tau-clearing A1 genre. R15: the pre-committed "A-channel EXTENSION" FAIL-branch
is RETIRED (premise falsified + would break the HARD false_flag 0.10 bar = castration). NEXT: a prose-
provenance-PURE window N>=30 to clear tau on the isolated lead.
Ladder + gates: ARCHITECTURE_master.md sec 4. Control: operator-applies (phases 1-3).

================================================================================
## BUILT + VERIFIED (in git, commit hashes)
- A-channel  (verify_E16_A.py): false_flag 0.000, detect 0.818 on an 11+11 Founder set
  (SMALL -> wide CI, provisional). A2 weakness found by real eval + fixed (patch_A2.py),
  SPEC re-frozen. commit f445390 (eval+A2) ; build cdd3072 ; A2 negated-certainty exemption 70bd90e.
- B-channel grounding: L1-L3 (verify_E16.py) + L4 GOLD contradiction-veto (verify_E16_L4.py,
  fa 0.0333) + live intake (run_step2b_intake.py, gate-before-model). commit c7b242b + earlier.
- Canon: reports/canon/ARCHITECTURE_master.md. commit c973757.
- Phase-2 spec FROZEN: reports/SPEC_disposition_audit.md. commit 117dd9a.
- Phase-2 ORGAN (verify_disp_audit.py): synthetic labeled-pool eval REMOVED; validation = --selftest
  (written-in must-fire/must-stay-silent, +per-clean silence incl. disclaimer FP trap) + --audit on real
  windows. md5 8cc9f424f9863edc56535f16d1cf6b75. commit 70bd90e.

================================================================================
## PARTIAL / PENDING
- phase-1 gate NOT fully closed: need >=20+20 honest A-set (Founder) + the SAME gate run for the
  B-channel. Current A PASS is on 11+11 only.
- L5 internet grounding: built, UNCOMMITTED, gated on a Founder truth-set.

================================================================================
## IMMEDIATE NEXT ACTION (phase 3 -- prose-provenance-PURE window, clear tau on the isolated lead)
v111 proved prose-provenance is the tau-clearing A1 genre (7/14=0.500) but the MIXED window FAILED
(A1=0.273) via dilution by the Q2-safe-exempted result-number genre + A3. Do NOT lower tau (R7), do NOT
re-mine bait, do NOT take the A-channel-extension branch on a window FAIL (DO-NOT-REDO 2026-06-13 e), do
NOT post-hoc reslice / iterate compositions to fish a pass. To get a card:
- NEXT (separate generation session, TYPE A): assemble N>=30 ORDINARY prompts, ALL prose-provenance /
  numeric-myth ("where does <number/myth> come from", "who first said <figure>"). Reuse
  run_ordinary_window.py (on disk) on the frozen base -> ordinary_window_v3.jsonl (cut echo-loop).
- THEN: verify_disp_audit.py --audit + tally_v2.py ordinary_window_v3.jsonl -> cards + organ-tally rates.
  FALSIFIABLE TARGET: A1 >= 0.30. PASS -> card "gap-fill fabricated number" seeds step 2 (LATER session).
  FAIL (even on the pure lead) -> surface ceiling CONFIRMED -> A-channel design session weighing any
  extension against the HARD false_flag 0.10 bar. generate/audit/fix stay SEPARATE sessions.

================================================================================
## CODE LOCATIONS (on disk, onto-research/lab/dpo/)
- verify_E16_A.py    -- the A-channel ; disposition-audit imports its selfcheck().
- verify_E16.py      -- base (segment/classify/gate/_norm/PROVEN/ABSTAIN); imports gold_retrieve at load.
- verify_E16_L4.py   -- L4 GOLD contradiction-veto (B-channel).
- gold_retrieve.py   -- GOLD store accessor (needed only so `import verify_E16` resolves; A/disposition path never calls it).
- run_step2b_intake.py -- live intake.
- verify_disp_audit.py -- phase-2 organ (--selftest / --audit).
- specs: reports/SPEC_disposition_audit.md (task) ; reports/SPEC_selfcheck_A.md (A-channel).
- canon: reports/canon/ARCHITECTURE_master.md.
- real outputs on disk: data/harvest_hits_E12.jsonl (completion) ; eval/_local/harvest_E13.jsonl
  (completion) ; eval/_local/harvest_E15.jsonl (raw_output). ALL bait -> not a valid audit window.

================================================================================
## CONTROL POSITION
phases 1-3 = operator APPLIES (we are here). 4-5 supervise. 6-8 review. 9 system, within locks.
immutable + constitutional layers touched at NO phase.

================================================================================
## CARRY (not blocking; tidy later, NOT now)
- build_pack.ps1 bug: pack v108 + v109 hand-assembled until fixed.
- loose/untracked: E34 (run_E34_probe.py, report_E34.md, E34_vs_E32.diff), L5 (build_l5_truth.py,
  run_L5_partI_validate.py, SCHEMA_l5_coupling_truth.md), STRATEGY rev2 uncommitted.
- dead synthetic-pool remnants in lab/dpo root (disposition_pool.jsonl, _TEMPLATE.jsonl, build_seed_pool.py) -> remove.
- tree hygiene: 60+ E5-E42 ladder scripts sit flat in lab/dpo/ (they import each other -- do NOT
  move; an 00_INDEX.md map is the safe way to make it legible). Cleanup is a separate later task.
