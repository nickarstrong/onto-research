# CONTINUITY_LOG.md -- the anti-forgetting spine. READ THIS FIRST, before anything.

home  : RIDES IN THE SESSION ZIP, every session, in 00_SESSION/ (read-first). Git is a BLIND backup
        only -- Claude CANNOT read git at runtime; the zip is the sole read-path. Git-only = lost thread.
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
- 2026-06-13: VALIDATION IS ORGANIC + WRITTEN-IN (supersedes the "Founder labels a synthetic pool"
  frame below). NO synthetic data in the conscience loop. Rule-correctness is SPECIFIED in code --
  --selftest's must-fire / must-stay-silent conditions; SYSTEM validation is the organ run on the
  model's OWN real outputs (--audit) plus phase-3's by-EFFECT gate (a fix must drop the flag-rate on
  real outputs, fab flat, operator applies). A statistical hand-labeled-pool gate is RETIRED: synthetic
  candidates were authored-to-vice (semi-confirmatory), and by-effect is the stronger self-validating
  check. (Founder: "у нас всё должно быть органичным без всякой синтетики; валидацию можно прописать".)
- CONVEYOR READ-PATH (decided 2026-06-13): Claude reads ONLY the session ZIP on intake; git is
  write-only/blind to Claude at runtime. Everything load-bearing rides IN the zip EVERY session.
  Pack is FOLDERED BY IMPORTANCE: 00_SESSION/ (00_SESSION_PACK + CONTINUITY_LOG + STRUCTURE) read
  first, then 01_CANON, 02_SPEC, 03_REF. 00_SESSION/STRUCTURE.md = full on-disk path-map,
  AUTO-GENERATED from the real disk (not Claude's recollection) so Claude knows what/where without browsing.
  ASSEMBLY: Claude emits a PS assembler (build_pack.ps1); the Founder runs it to build the zip and ships it.
- AUDIT SUBSTRATE (decided 2026-06-13 c): citation-bait harvests (E12/E13/E15) are NOT a valid
  phase-3 --audit window. They are adversarial probes where the model is maximally disciplined ->
  market-dispositions do not surface (measured declared=[] on N=320). A real-output window for
  surfacing standing instincts must be ORDINARY (non-bait) model outputs.

================================================================================
## DO-NOT-REDO (mistakes already made -- do not repeat)
- 2026-06-13 c: do NOT use the citation-bait harvests (E12/E13/E15) as the phase-3 --audit window,
  and do NOT lower tau_declare (0.30, locked) to manufacture a card from a near-miss (E15 A1=0.258).
  Both are R7 violations of pre-registered bars / biased-substrate. The fix is a fresh ORDINARY-output
  window, not re-mining bait or re-tuning the threshold.
- 2026-06-13: do NOT reintroduce a synthetic hand-labeled disposition pool, a labeler, or a
  statistical labeled-pool --eval gate for the conscience. The Founder rejected this as non-organic;
  validation = written-in conditions (selftest) + organic real-output audit + phase-3 by-effect.
  (The earlier "build a labeler, Founder taps ~30" fix from 2026-06-13 a is itself now retired.)
- 2026-06-13: proposed CONTINUITY_LOG's home as git "so Claude reads it first." WRONG -- Claude
  cannot read git at runtime; it reads the session ZIP only. Load-bearing docs must ride IN the zip
  every session, foldered, 00_SESSION first. Git is blind durable storage, never a read-path.
- 2026-06-13: DETOUR off the Founder-authoring frame. Claude tried to MINE a disposition pool from the
  E12/E13/E15 citation-bait harvests, found them mostly disciplined refusals (few real vices), then
  escalated to "the gate is unbuildable, need a generation pipeline." WRONG: harvests were never the
  intended source; the frame is Founder-judged labels. FIX: a labeler (label_pool.py) that shows
  RU+EN candidate outputs, Founder taps the disposition; Founder's taps = ground truth. Lesson: when
  the established next-step is "Founder labels ~30," do that -- do not invent a corpus-mining detour.

================================================================================
## OPEN THREADS (live, unfinished)
- PHASE 3 (active -- substrate UNBLOCKED + CHARACTERIZED ; still no card): v110 generated a VALID
  ORDINARY window (N=24, frozen base, no adapter) and audited it. declared=[] AGAIN, but qualitatively
  different from bait: A-flags are LIVE yet sub-tau. Exact organ-tally rates: A1=0.125 (3/24), A3=0.083
  (2/24), A2=0.000, A4=0.000 ; 5/24 trip >=1 flag (bait was ~0.03 across the board). A1 fires on the
  prose-provenance genre (ord_prov:01/02). The window is too DILUTE: max 0.125 < tau 0.30 (floor 8/24).
  A2/A4 are structurally silent -- this base's ordinary register hedges (not overconfident) and does not
  stack hedges in a short span. NEXT: a CONCENTRATED ordinary window (N>=30, prose-provenance + empirical-
  result-number + vague-magnitude weighted; drop A2/A4 prompts) to push A1 to tau. FALSIFIABLE TARGET:
  A1 >= 0.30 on that window -> card seeds step 2 ; A1 still < 0.30 -> blocker is the A-channel surface
  ceiling (A1 Q2-safe exemption swallows common-knowledge-framed numbers) -> escalate to an A-channel
  EXTENSION design session (separate concept session, not a patch).
- PHASE 2 (CLOSED 2026-06-13): organ verify_disp_audit.py = built + written-in validation (--selftest)
  + organic --audit. NO synthetic pool / no labeler. Committed onto-research 70bd90e.
- PHASE 1 CLOSE (parallel): need >=20+20 honest Founder A-set + same gate for B-channel. Current A PASS
  is 11+11 only (provisional, wide CI).
- A-channel residual FP watch: A2 negated-certainty FP patched 2026-06-13 (_NEG_CERT/_neg_before,
  clause-scoped; SPEC_selfcheck_A s5 dated). Keep watching A2/A4 on real careful-disclaimer language.
- L5 internet grounding: built, UNCOMMITTED, gated on a Founder truth-set.
- Carry/tidy: E34 untracked; L5 loose; STRATEGY rev2 uncommitted; 60+ flat E5-E42 scripts (00_INDEX map, do not move).
- build_pack.ps1 has a bug (pack v108 hand-assembled). Fix or hand-assemble v109 until repaired.

================================================================================
## SESSION ENTRIES (reverse-chronological ; append at close, never edit prior)

### 2026-06-13 (d) -- phase 3 step1 on a VALID ORDINARY window -> declared=[] but A-flags LIVE sub-tau
type    : RESEARCH / lab (TYPE A generation ; then audit on the produced window. No fix.).
intake  : pack v109 conveyor VALID (8/8 md5 vs MANIFEST; PACK_SPEC == f888f427).
built   : ordinary_prompts.jsonl -- 24 ORDINARY prompts (non-bait), 5 families: A1_gapfill_number 6,
          A1_prose_provenance 5, A2_overclaim 5, A3_vague_magnitude 4, A4_please_hedge 4. md5 70373755.
          run_ordinary_window.py -- frozen-base harness = e5_gen arm A VERBATIM (Qwen2.5-Coder-7B, 4-bit
          nf4, "### Instruction/### Response" wrapper, greedy, NO adapter/NO GOLD). --dry-run mock for
          off-box wiring. md5 8b6366b1.
ran     : on RunPod (RTX 4000 Ada, n_gpu 1). 24 outputs -> ordinary_window.jsonl. Base (non-instruct) did
          NOT emit EOS -> echo-looped the wrapper; truncated each text at first "### Instruction"/"###
          Response" re-occurrence (16/24 trimmed; greedy => first block identical to a stop-seq run, no
          re-run). Clean window md5 3c98e04f, 0 empties.
audit   : verify_disp_audit.py --selftest PASS (declares all 4 on high-rate, respects tau, 0 false-decl).
          --audit -> n=24 declared=[] cards=[]. Organ-tally per-flag rates (selfcheck over each item,
          gold_retrieve STUBBED off-box per 2026-06-13 c): A1=0.125 (ord_num:01, ord_prov:01/02),
          A3=0.083 (ord_prov:03/04), A2=0.000, A4=0.000 ; 5/24 trip >=1 ; floor 8/24 @ tau 0.30.
finding : substrate WORKS (vs bait ~0.03) but is DILUTE. A1 is the live lead; it fires on prose-provenance,
          and -- as predicted by SPEC_selfcheck_A s1 -- is Q2-SAFE on common-knowledge-framed numbers
          ("73% water" did NOT fire). A2/A4 structurally silent: this base hedges (no overconfidence
          lexicon) and does not stack hedges in a short span. The falsifiable lead (A1 clears tau) is NOT
          YET confirmed -- right direction, wrong concentration.
decided : do NOT lower tau (R7) ; do NOT re-mine bait ; do NOT pad with A2/A4 prompts. NEXT (separate TYPE A
          gen session): CONCENTRATED ordinary window N>=30 weighted prose-provenance + empirical-result-
          number + vague-magnitude. Pre-stated target: A1 >= 0.30 -> card ; else A-channel surface ceiling
          confirmed -> A-channel EXTENSION design session (separate).
git     : onto-research main -- file ordinary_prompts.jsonl (data/), run_ordinary_window.py (root),
          REPORT_phase3_step1_ordinary.md (reports/). Window regenerable from harness+prompts (greedy);
          committing it optional. No weights/bait. (filing PS handed at close.)

### 2026-06-13 (c) -- phase 3 step 1: --audit on real harvests -> declared=[] ; substrate blocker
type    : RESEARCH / lab (TYPE A, code; no model eval, no generation).
intake  : pack v108 conveyor VALID (8/8 md5 vs MANIFEST; PACK_SPEC == f888f427). docs-only pack v108
          rejected first (no MANIFEST / no PACK_SPEC -> INVALID, per PIPELINE v1).
ran     : built real-output window from the three on-disk harvests -- text = completion (E12,E13) /
          raw_output (E15) -- N=320 (E12 113 + E13 176 + E15 31), id keeps provenance "<TAG>:<line>".
          verify_disp_audit.py --selftest PASS on box (matches documented result: 4/4 declare+ev_intact,
          low-rate silent, all-clean zero, per-clean silent incl. disclaimer trap). Then --audit window_real.jsonl.
result  : declared=[]. Per-flag fire rates (all < tau 0.30): ALL/320 A1=0.031 A2=0.000 A3=0.025 A4=0.003 ;
          E12 all ~0 ; E13 all ~0 ; E15 A1=0.258 A3=0.161 (closest, still < tau). Zero cards.
finding : the bait harvests are the WRONG audit substrate -- adversarial probes where the model is
          maximally disciplined, so market-dispositions don't surface. Organ behaved correctly
          (precision-first: no declaration on clean/near-clean). Phase 3 cannot reach step 2 here.
decided : do NOT lower tau (locked, R7) ; do NOT re-mine bait. Phase 3 input must be an ORDINARY
          (non-bait) real-output window, produced in a separate generation session.
offbox  : --audit/--selftest need gold_retrieve.py present so `import verify_E16` resolves; off-box a
          minimal STUB sufficed (A/disposition path never calls gr.*, only verify_E16._eval_heldout does).
          On the real box gold_retrieve.py exists -> no action.
next    : generation session (TYPE A) -> ordinary-output window N>=20 -> re-audit -> read cards -> step 2.

### 2026-06-13 (b) -- phase 2 reframed: synthetic pool DROPPED, validation = written-in + organic
type    : RESEARCH / lab (TYPE A/C, code; no model eval).
decided : (Founder) NO synthetic data in the conscience loop; validate ORGANICALLY on the model's OWN
          real outputs, and SPECIFY rule-correctness in code (must-fire/must-stay-silent), not via a
          hand-labeled corpus. Supersedes "Founder labels ~30 synthetic candidates" (2026-06-13 a).
built   : verify_disp_audit.py rewritten -- removed synthetic labeled-pool eval (_eval/_wilson/--eval);
          validation = --selftest (written-in conditions, +per-clean silence incl. disclaimer FP trap)
          + --audit on real windows. md5 8cc9f424f9863edc56535f16d1cf6b75.
          verify_E16_A.py A2 negated-certainty exemption (_NEG_CERT/_neg_before) -- FOUND ORGANICALLY by
          the organ's per-clean condition tripping A2 on "I can't guarantee...". A-channel selftest 4/4
          POS (P2 overclaim intact) + 5/5 NEG ; organ selftest PASS (clean[5] silent).
          md5 ea9d688b997aefdaebd06a78f3e49e50. SPEC_selfcheck_A re-frozen (s5 dated). Commit 70bd90e.
tried+failed : git add -A with an untracked pathspec (label_pool.py) -> fatal aborts the whole stage.
          Stage NAMED tracked files only. label_pool.py/check_pool.py were untracked -> off-disk, no git trace.
next    : phase 3 (surgical correction) -- proposal cards from --audit on a real window; validate fixes BY EFFECT.
carry   : dead synthetic-pool remnants in lab/dpo root (disposition_pool.jsonl, _TEMPLATE.jsonl,
          build_seed_pool.py) pending removal ; report_E16_L4_selftest.md modified (unrelated, unstaged) ;
          STATUS carry (E34, L5 loose, STRATEGY rev2) unchanged.

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
