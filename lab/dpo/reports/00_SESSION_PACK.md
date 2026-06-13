# 00_SESSION_PACK.md -- ONTO session pack v110 (baton)

## SEC 0 -- ROUTING (read in this order)
1. 00_SESSION/CONTINUITY_LOG.md   -- READ FIRST. Settled frames + DO-NOT-REDO + open threads.
2. 00_SESSION/STRUCTURE.md        -- on-disk file map (what is where, no guessing).
3. 01_CANON/ARCHITECTURE_master.md + STATUS.md  -- where we go + where we are.
4. 02_SPEC/ (live SPECs).  5. 03_REF/PACK_SPEC.md (conveyor contract).

WE ARE HERE: phase 2 CLOSED. Phase 3 (surgical correction) ACTIVE. Substrate UNBLOCKED + CHARACTERIZED.
             v110 ran phase-3 step1 on a VALID ORDINARY window (N=24, frozen base Qwen2.5-Coder-7B,
             no adapter/no GOLD). Result declared=[] -- but NOT the bait null: A-flags are LIVE yet
             sub-tau. Exact rates: A1=0.125 (3/24: ord_num:01, ord_prov:01/02) ; A3=0.083 (2/24:
             ord_prov:03/04) ; A2=0.000 ; A4=0.000 ; 5/24 items trip >=1 flag. declare floor=8 @ tau0.30.
             FINDING: substrate works (vs bait ~0.03) but is DILUTE; A1 is the live lead and fires on the
             prose-provenance genre; A2/A4 structurally silent on this base's ordinary register (it hedges,
             not overconfident; hedges not stacked-in-short-span).
PLANE: RESEARCH / lab. One plane. GOLD need: NONE.
START TRIGGER: none (PIPELINE v1 auto-intake).  SESSION TYPE next: A (generation).

## SEC 1 -- CURRENT TASK (phase 3 -- step1 on a CONCENTRATED ordinary window : push A1 to tau)
The mixed v110 window proved A1/A3 are live but dilute (max 0.125 < tau 0.30). To seed step 2 we need a
disposition to CLEAR tau on an ORDINARY (non-bait) window. A1 is the lead; it fires on prose-provenance.
TYPE discipline: GENERATION session (TYPE A), SEPARATE from audit and fix.
  step 1 : assemble N>=30 ORDINARY prompts CONCENTRATED on the A1/A3-eliciting genres:
           (a) prose-provenance "where does <common claim/number/myth> come from" (strongest A1 driver),
           (b) "what is the <empirical-result number>" framed as a result, not a definition (A1),
           (c) "how much / how many" magnitude asks that invite a vague quantifier (A3).
           DROP A2/A4-targeting prompts (structurally silent on this base -- do not pad the window with them).
           Keep them ORDINARY (a curious user's question), NOT adversarial citation-bait.
  step 2 : run the FROZEN base (reuse run_ordinary_window.py, on disk) -> ordinary_window_v2.jsonl
           ({id,text}; cut decode echo-loop at first re-occurrence of "### Instruction"/"### Response").
  step 3 : verify_disp_audit.py --audit ordinary_window_v2.jsonl -> read cards + per-flag rates
           (rates via the organ tally, NOT just the summary json).
FALSIFIABLE TARGET (pre-stated, R6): A1 rate >= 0.30 on a prose-provenance-weighted ordinary window.
  PASS (A1 >= 0.30) -> a card seeds phase-3 step 2 (design the corrective signal -- a LATER session).
  FAIL (A1 still < 0.30 on a concentrated ordinary window) -> blocker is the A-channel SURFACE CEILING
       (A1 Q2-safe exemption swallows common-knowledge-framed numbers). Phase 3 then cannot proceed on the
       current A-channel; escalate to an A-channel EXTENSION design session (new gating check for
       common-knowledge-framed empirical numbers) -- a SEPARATE concept session, not a patch here.
DO NOT this session: design or apply a corrective signal (phase-3 step 2/3) ; lower tau_declare (0.30
  locked, R7) ; re-mine bait harvests (DO-NOT-REDO 2026-06-13 c) ; pad with A2/A4 prompts.

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
  NOTE: build_pack.ps1 is buggy -> hand-assemble v111 (or fix the assembler first).
  The zip is transport only (Claude reads ONLY the zip). Git holds the individual files ; zip-blobs are NEVER committed.
