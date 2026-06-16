# 00_SESSION_PACK.md -- ONTO session pack v171 (baton)

## RULE 0 -- HOW TO WRITE THIS PACK (applies to every line below)
Write every load-bearing line for an instance that has ZERO context. You know the project; the next-session
reader does not. If a line does not unpack into a concrete action for someone who knows nothing, it is a BUG.
Compressed != encrypted. Spell the action out.

## SESSION_FLOW -- the loop we run every session
  1. Founder sends the session zip. Claude auto-intakes (PIPELINE v1, SEC 4) and READS the pack: state,
     the one next task, how we work. No guessing from memory (memory is lossy, protocol 3.10).
  2. If Claude needs a local file not in the pack (out.jsonl / held-out / bait / FT-CC), Claude gives ONE PS
     line that zips exactly those into Downloads. Founder uploads that zip.
  3. Work, one step per message, each step = a command + its expected output + a pass/fail line.
  4. At close, Claude hands updated 00_SESSION_PACK.md + STATUS.md + CONTINUITY_LOG.md (append one entry).
     Founder runs build_pack.ps1 -> next zip. Zip is transport; git holds the files.

## SEC 0 -- ROUTING (read in this order)
1. 00_SESSION/CONTINUITY_LOG.md   -- READ FIRST. Settled frames + DO-NOT-REDO + the (wd) record at the tail.
2. 00_SESSION/STRUCTURE.md        -- on-disk file map (auto-generated).
3. 01_CANON/ARCHITECTURE_master.md  -- North Star.
4. 01_CANON/STATUS.md             -- current state in plain words. ACTIVE PLANE = NONE (full-text CLOSED).
5. 02_SPEC/SPEC_s2b_v0.md         -- the judge contract (frozen, md5 80bdf2a9).
6. 02_SPEC/GATE_s2b_offtopic_v0.md -- off-topic gate (frozen, CLEARED).
7. 02_SPEC/GATE_s2b_fulltext_v0.md -- full-text gate (frozen). ALL BARS PASS at (wd) ; reference only.
8. 03_REF/PACK_SPEC.md            -- conveyor contract (md5 f888f427).

WHERE WE ARE (plain): the s2b grounded verifier is COMPLETE end-to-end. B1 binding + B2 abstract (incl off-topic)
+ full-text fallback (getter wc + resolver wd) are all gate-valid. The G8 RESOLVER FIX is DONE: s2b_v0.py blob
35eefda12c0774ef6e13522febfe1447 (LF) on onto-research main HEAD fd2b9ba ; --selftest G1-G9 PASS (Qwen2.5-7B) ;
--score on frozen FT-CC = VERDICT PASS (G7/G8/G9) ; the 3 wc castrations (ftc02/03/08) now read UNCLEAR, never
NOT. Public report reports/REPORT_s2b_g8_resolver_fix.md committed (provenance + bars + yield, no eval data). The
s2b predicate has NO open defect. NEXT = Founder selects the next plane (SEC 1).

NO ACTIVE TRIGGER pre-set. The full-text plane is closed ; do NOT reopen it (getter, resolver, bars, gate all
settled). Pick a PARKED plane below.

## SEC 1 -- NEXT TASK (Founder picks ; the s2b predicate is done -- this is a fresh plane, not a continuation)
The full-text fallback is complete. Candidate next planes (Founder chooses ONE ; Claude does not open mid-session):

  (P1) RESOLUTION-YIELD / B2 SUPPORTS+CONTRA-leg at scale. 7/24 is the honest OA+contradiction-detection ceiling.
       Many FT-wrong land at honest UNCLEAR because per-chunk affirmative CONTRADICTS is rare under the grounded
       judge. A yield plane would strengthen the per-chunk SUPPORTS/CONTRA detection (better excerpt targeting /
       read-strategy), measured against the SAME frozen FT-CC + gate. R7 HARD: yield is diagnostic -- never raise
       it by tuning the G7/G8 bar ; only by a genuinely better read/judge. Needs a fresh measurement contract.
  (P2) L5 FIX. Behind a FRESH gate (write the gate before any byte). L5 truth-set LOCAL-ONLY. (hh) CLOSED prior.
  (P3) A-channel CI-clear : grow the clean A-set to ~30. Cheap polish.
  (P4) 4-bit GPU B2 restore : speed-only (bnb DLL was broken on new CUDA -> CPU offload via S2B_NO_4BIT). No bar
       impact, pure throughput.
  (P5) HYGIENE micro-plane : add .gitattributes `*.py text eol=lf` to onto-research so checkout EOL is stable and
       disk md5 == git-blob md5 (kills the recurring CRLF/md5 confusion seen at wd). One-file change + one commit.

ENGINEER RECOMMENDATION (one line, R12): take (P5) first as a 10-minute clean-up (it removes a recurring
  identity-drift hazard), THEN (P1) as the substantive next step toward a stronger grounded verifier. Founder
  overrides freely.

GOLD need next plane: NONE for P1/P3/P4/P5 ; P2 declares its own truth-set (LOCAL). SESSION TYPE depends on pick:
  P1 = eval+build (split honored, fresh contract) ; P2 = gate-then-build ; P3/P4/P5 = build/hygiene.

## SEC 2 -- PARKED HARVEST OPTIONS (folded into SEC 1 P1)
  (a) B2 SUPPORTS/CONTRA-leg at scale = P1. (c) 4-bit GPU B2 = P4.

## SEC 3 -- PARKED (not active unless Founder picks one)
  - L5 FIX = P2. A-channel CI = P3. EOL hygiene = P5.

## SEC 4 -- INTAKE (PIPELINE v1)
  unzip -> md5 every file vs MANIFEST.md5 -> VALID/INVALID (INVALID = STOP).
  03_REF/PACK_SPEC.md md5 MUST == f888f427597c7c45e6503c33f1babe24 (staleness guard). Mismatch = STOP.

## SEC 5 -- CLOSE
  At close Claude hands updated 00_SESSION_PACK.md + STATUS.md + CONTINUITY_LOG.md (STRUCTURE auto-gen by build_pack).
  Founder places those 3 in lab\dpo\reports\, then runs:
    .\build_pack.ps1 -N 171 -Spec SPEC_s2b_v0.md,GATE_s2b_offtopic_v0.md,GATE_s2b_fulltext_v0.md  -> onto_session_pack_v171.zip
  SEMANTICS (verified from build_pack.ps1): zip filename = -N DIRECTLY. NO offset. 02_SPEC = exactly the -Spec list.
  NOTE: input pack this session was v170 -> next = v171. If Founder's local counter differs, set -N accordingly
  (filename = -N, no offset).
  LOCAL-ONLY, never in pack, never public git: proposals/worksheet/rate_judgments/ledger(DOIs)/falsifier/
  ground_candidates/cc/j5/cc_j5_ground/g5_live/ft_resolve/resolve_ft.ps1/ft_cc_v0*/ft_cc_ground/ft_cc_v0_s2b_out*/
  all L5 truth-set.

  STANDING HYGIENE: R12 leak (audit_v2_stdout.txt + onto_index_harvest.txt) RESOLVED at wd (moved to eval/_local/,
  gitignored). Any future `git add .` stays explicit-path. The s2b plane git is CLEAN.
