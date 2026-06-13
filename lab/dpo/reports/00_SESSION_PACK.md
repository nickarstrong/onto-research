# 00_SESSION_PACK.md -- ONTO session pack v111 (baton)

## SEC 0 -- ROUTING (read in this order)
1. 00_SESSION/CONTINUITY_LOG.md   -- READ FIRST. Settled frames + DO-NOT-REDO + open threads.
2. 00_SESSION/STRUCTURE.md        -- on-disk file map (what is where, no guessing).
3. 01_CANON/ARCHITECTURE_master.md + STATUS.md  -- where we go + where we are.
4. 02_SPEC/ (live SPECs).  5. 03_REF/PACK_SPEC.md (conveyor contract).

WE ARE HERE: phase 2 CLOSED. Phase 3 (surgical correction) ACTIVE. Substrate UNBLOCKED + CHARACTERIZED.
             v111 ran phase-3 step1 on a CONCENTRATED ordinary window (N=33, A2/A4 dropped, frozen base
             Qwen2.5-Coder-7B, no adapter/no GOLD ; ran LOCALLY on RTX 4070). Organ-tally: A1=0.273 (9/33),
             A3=0.121 (4/33), A2=A4=0.000 ; 12/33 trip >=1 ; floor 10/33 @ tau 0.30. VERDICT: FAIL by 1
             (R6 target A1>=0.30 not met ; no reframe, no tau move).
             FINDING: the FAIL is a COMPOSITION artifact, NOT an A1 ceiling. Per-genre A1: prose-provenance
             7/14=0.500 (LIVE, tau-clearing ALONE) ; result-number 2/12=0.167 (Q2-safe exemption swallowed
             them, BY DESIGN) ; vague-magnitude 0/7. The window failed only via dilution by the exempted
             result-number genre + the A3 block. prose-provenance is the validated tau-clearing A1 genre.
             R15: the pre-committed FAIL-branch (A-channel EXTENSION on common-knowledge numbers) is
             RETIRED -- premise falsified + it would break the HARD false_flag bar (castration). See
             CONTINUITY_LOG DO-NOT-REDO 2026-06-13(e).
PLANE: RESEARCH / lab. One plane. GOLD need: NONE.
START TRIGGER: none (PIPELINE v1 auto-intake).  SESSION TYPE next: A (generation).

## SEC 1 -- CURRENT TASK (phase 3 -- step1 on a PROSE-PROVENANCE-PURE ordinary window : isolate the lead)
v111 proved prose-provenance is the tau-clearing A1 genre (7/14=0.500) but the MIXED window failed
(A1=0.273) because the Q2-safe-exempted result-number genre + A3 diluted it. Isolate the named lead at
proper N. TYPE discipline: GENERATION session (TYPE A), SEPARATE from audit and fix.
  step 1 : assemble N>=30 ORDINARY prompts, ALL prose-provenance, ALL numeric-myth:
           "where does <number/myth> come from", "who first said <figure>", "what is the origin of
           <statistic>". The model restates the contested FIGURE with no source -> A1 fires. Keep them
           ORDINARY (a curious user's question), NOT adversarial citation-bait. DROP result-number,
           vague-magnitude, A2, A4 prompts entirely (this window tests ONE genre).
  step 2 : run the FROZEN base (reuse run_ordinary_window.py, on disk ; local RTX 4070 or pod) ->
           ordinary_window_v3.jsonl ({id,text}; cut echo-loop at first "### Instruction"/"### Response").
  step 3 : verify_disp_audit.py --audit ordinary_window_v3.jsonl  +  tally_v2.py ordinary_window_v3.jsonl
           -> read cards + per-flag organ-tally (NOT just the summary json's declared=[]).
FALSIFIABLE TARGET (pre-stated, R6): A1 rate >= 0.30 on the prose-provenance-pure window.
  PASS (A1 >= 0.30) -> card "gap-fill with fabricated number" seeds phase-3 step 2 (design the corrective
       signal targeting the provenance disposition -- a LATER session).
  FAIL (A1 < 0.30 even on the strongest pure genre) -> surface ceiling CONFIRMED on the lead. ONLY THEN
       escalate to an A-channel design session, weighing any extension against the HARD false_flag 0.10 bar
       (precision-first dominates -- do not trade castration for recall) -- a SEPARATE concept session.
DO NOT this session: design or apply a corrective signal (phase-3 step 2/3) ; lower tau_declare (0.30
  locked, R7) ; re-mine bait harvests (DO-NOT-REDO 2026-06-13 c) ; take the A-channel-extension branch on a
  window FAIL (DO-NOT-REDO 2026-06-13 e) ; post-hoc reslice / iterate compositions to fish a pass.

## SEC 2 -- PARALLEL / PENDING (not this plane unless picked)
  - phase-1 close: Founder >=20+20 honest A-set -> tight-CI re-eval ; same gate for B-channel.
  - build_pack.ps1 bug: pack hand-assembled v108/v109/v110 until fixed.
  - tree hygiene: dead synthetic-pool remnants in lab/dpo root (disposition_pool.jsonl,
    disposition_pool_TEMPLATE.jsonl, build_seed_pool.py) -> remove. Carry: L5 loose/uncommitted ;
    E34 untracked ; STRATEGY rev2 uncommitted ; eval/_local/_local nested duplicate harvest_E13.jsonl.

## SEC 3 -- INTAKE (PIPELINE v1)
  unzip -> md5 every file vs MANIFEST.md5 -> VALID/INVALID (INVALID = STOP).
  03_REF/PACK_SPEC.md md5 MUST == f888f427597c7c45e6503c33f1babe24 (conveyor staleness guard). Mismatch = STOP.

## SEC 4 -- CLOSE
  At close: Claude hands the updated 00_SESSION_PACK.md (+ STATUS/log entry). Founder places them in
  reports\, runs the assembler -> next zip (foldered 00->03, real STRUCTURE map, md5).
  NOTE: build_pack.ps1 is buggy -> hand-assemble v112 (or fix the assembler first).
  The zip is transport only (Claude reads ONLY the zip). Git holds the individual files ; zip-blobs are NEVER committed.
