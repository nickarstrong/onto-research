# CONTINUITY_LOG.md -- the anti-forgetting spine. READ THIS FIRST, before anything.

home  : onto-research/reports/CONTINUITY_LOG.md (git) + rides byte-referenced in every session pack.
why   : Claude starts each session with NO memory of prior sessions. The canon says WHERE we go;
        STATUS says WHERE we are; THIS log says WHAT IS ALREADY SETTLED, WHAT WAS ALREADY TRIED+FAILED,
        and WHAT NOT TO REDO -- so no session burns the Founder's time re-deciding or re-breaking.
rules : (1) Claude reads this FIRST on intake, before proposing anything.
        (2) Claude APPENDS one entry at session close (never deletes/rewrites prior entries).
        (3) On any "we already decided/did this" from the Founder -> the answer is HERE or in past chats; pull it, don't guess.
        (4) Settled frames are NOT relitigated. A new idea that contradicts one must say so explicitly and justify.

================================================================================
## SETTLED FRAMES (do NOT relitigate -- these are decided)
- NORTH STAR: autonomous entity on a FROZEN base; discipline (R1-R18) lives OUTSIDE the weights as a
  conscience; disposition migrates INTO weights only via gated corrective-learning. (ARCHITECTURE_master.)
- The conscience = A-channel (self-consistency, no source/model/net: A1 num-no-source, A2 overconfident,
  A3 vague-no-number, A4 empty-hedge) + B-channel (grounded: L1-L3 + L4 GOLD veto + L5 internet).
- PRECISION-FIRST is the spine: false-flag <= 0.10 HARD dominates detect. A flag on clean output = castration.
- 9-phase gated ladder; we are at phase 2 (disposition-audit). One gate at a time; no dressing a later
  phase as an earlier patch.
- The phase-2 + phase-1 LABELED SETS are **Founder-authored / Founder-judged** ground truth (R7).
  Labels are the Founder's judgment, NEVER faked to clear a bar. This is the established sourcing frame.
- Frozen organs are import-only and never mutated (verify_E16, verify_E16_A). New organs wrap them.
- Pre-registered bars are frozen BEFORE real-data eval; results never relitigate bars (R7).
- Conveyor: PACK_SPEC.md md5 == f888f427597c7c45e6503c33f1babe24 is the staleness guard.

================================================================================
## DO-NOT-REDO (mistakes already made -- do not repeat)
- 2026-06-13: DETOUR off the Founder-authoring frame. Claude tried to MINE a disposition pool from the
  E12/E13/E15 citation-bait harvests, found them mostly disciplined refusals (few real vices), then
  escalated to "the gate is unbuildable, need a generation pipeline." WRONG: harvests were never the
  intended source; the frame is Founder-judged labels. FIX: a labeler (label_pool.py) that shows
  RU+EN candidate outputs, Founder taps the disposition; Founder's taps = ground truth. Lesson: when
  the established next-step is "Founder labels ~30," do that -- do not invent a corpus-mining detour.

================================================================================
## OPEN THREADS (live, unfinished)
- PHASE 2 GATE (current): Founder labels the pool via label_pool.py -> disposition_pool.jsonl ->
  check_pool.py -> verify_disp_audit.py --eval. Bars (frozen SPEC_disposition_audit sec2):
  false_declaration <= 0.10 HARD AND detect_declaration >= 0.60 AND naming/evidence intact AND VOID clear.
- PHASE 1 CLOSE (parallel): need >=20+20 honest Founder A-set + same gate for B-channel. Current A PASS
  is 11+11 only (provisional, wide CI).
- A-channel residual FP watch: careful-disclaimer language ("can't guarantee", honest stacked hedges in
  refusals) can trip A2/A4. always/never + attribution already patched (SPEC_selfcheck_A sec5). If a
  clean-refusal set shows flag-rate > 0.10, exclude the disclaimer pattern (dated re-freeze, R7).
- L5 internet grounding: built, UNCOMMITTED, gated on a Founder truth-set.
- Carry/tidy: E34 untracked; L5 loose; STRATEGY rev2 uncommitted; 60+ flat E5-E42 scripts (00_INDEX map, do not move).

================================================================================
## SESSION ENTRIES (reverse-chronological ; append at close, never edit prior)

### 2026-06-13 -- phase 2: organ built + labeler handed to Founder
type    : RESEARCH / lab (TYPE A build).
built   : verify_disp_audit.py -- phase-2 disposition-audit organ, import-only over verify_E16_A.selfcheck,
          no store/model/net. --selftest PASS on box (real verify_E16). Wiring --eval PASS on a synthetic
          seed (NOT the gate). md5 e1be274ac93831cfea251f7cbd784c8b. Committed (onto-research main, 21e9688).
          label_pool.py -- offline Founder labeler (RU+EN candidates, blind, taps 1-5 -> disposition_pool.jsonl).
          check_pool.py -- pool validator (counts/labels/empty/floor).
decided : phase-2 pool = Founder-judged labels on RU-translated candidate outputs (Founder does NOT write EN).
          CONTINUITY_LOG.md created (this file) as the standing anti-forgetting spine, read-first on intake.
tried+failed : harvest-mining the pool (see DO-NOT-REDO).
next    : Founder runs label_pool.py -> validator -> verify_disp_audit.py --eval (the real phase-2 gate).

### 2026-06-12 -- phase 1 closing / phase 2 spec frozen (prior session, reconstructed from pack v105)
built   : A-channel verify_E16_A.py (false_flag 0.000, detect 0.818 @ 11+11; A2 patched, re-frozen).
          B-channel L1-L4 + live intake committed. Canon + STATUS + SPEC_disposition_audit FROZEN (commit 117dd9a).
next    : phase-2 disposition-audit organ build.
