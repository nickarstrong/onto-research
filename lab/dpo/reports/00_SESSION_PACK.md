# 00_SESSION_PACK.md -- ONTO session pack v138 (baton)

## SEC 0 -- ROUTING (read in this order)
1. 00_SESSION/CONTINUITY_LOG.md   -- READ FIRST. Settled frames + DO-NOT-REDO + open threads (now incl. (dd)).
2. 00_SESSION/STRUCTURE.md        -- on-disk file map (what is where, no guessing).
3. 01_CANON/ARCHITECTURE_master.md  -- where we go (sec3 weight-migration endpoint ; sec4 phase-3 gate).
4. 01_CANON/STATUS.md             -- current state snapshot.
5. 02_SPEC/SPEC_selfcheck_A.md    -- A-channel frozen bars (the precision contract every gate rides on).
6. 03_REF/PACK_SPEC.md            -- conveyor contract (md5 f888f427).

WE ARE HERE: phase 1/2/3 CLOSED. fix(a) RULE standing. fix(b) DPO leg CLOSED.
   2026-06-14 (dd): L5 P4-edge disposition CLOSED (4/4) + predicate fix-gate FROZEN (CONCEPT). predicate UNTOUCHED.
   Disposition (each pair's OWN ref list, primary source ; LOCAL-ONLY eval/_local/l5_C014_C015_P4_disposition.md):
   C015 S3xS4 Yan/Kirchdoerfer = CITATION-EXEMPLAR (Yan cites Kirchdoerfer 2018 -> relabel independent->citation) ;
   C015 S1xS2 Wrapp/Walls = DEFECT ; C015 S1xS3 Wrapp/Yan = DEFECT ; C014 S1xS2 Wu/Zhou = DEFECT (no direct cite).
   1 exemplar + 3 P4-over-couple defect. No relabel-to-pass (R7).
   FIX-GATE FROZEN: eval/_local/SPEC_L5_fixgate_v1.md md5 c7c67593 (AST anchors of the frozen predicate in sec1).
   R16 ground: P4 reads refs_all = Crossref `reference` UNION OpenCitations -> real cites in Crossref `reference`,
   the 3 DEFECT edges enter via the OC union. v1.1 discriminator (DESIGN HYPOTHESIS, gate-agnostic) = Crossref-ref-only
   P4 + P3 positive-signal.
PLANE: RESEARCH / lab. GOLD need: NONE (predicate-fix is structural, label-only).
INTAKE TRIGGER: none (PIPELINE v1 auto-intake routes on upload).
WORK TRIGGER: "LABA, L5 FIX". No trigger = wait.
SESSION TYPE next: TYPE B (run the frozen fix-gate). eval != source: the C015 S3xS4 relabel is a SOURCE act done as
   PREREQ, NOT in the run session. Gate is ALREADY frozen (c7c67593) -- do NOT re-design or move a bar (R7).

## SEC 1 -- NEXT TASK (apply predicate v1.1 under the FROZEN gate ; one step/msg, TYPE B)
PREREQ (Founder, LOCAL-ONLY, SOURCE act, R7): relabel C015 S3xS4 (Yan/Kirchdoerfer) independent->citation in
   eval/_local/truth_input.txt, provenance = Yan cites Kirchdoerfer 2018 (recorded in l5_C014_C015_P4_disposition.md).
   The 3 DEFECT pairs STAY independent (no relabel).
THEN [one step/msg]:
  1. snapshot pre-edit AST-md5 (SPEC_L5_fixgate_v1 sec1) ; confirm MUST-stay set matches before touching a byte.
  2. apply predicate v1.1 -- provenance_edge (P4 source = Crossref `reference` only, drop OC union) + pair_predict
     (P3 = positive coupling signal, not fail-close-on-absent-DAS). ONLY these + the refs_all assembly may move.
  3. re-hash: MUST-stay set (score_dataset/verdict/clusters/contents/per_pair_readout/fetch_crossref) AST-identical ;
     MAY-change set changed. Mismatch in MUST-stay = INVALID, redo.
  4. build_l5_truth -> --contents -> net pre-check -> --run on the corrected accession-bearing set.
  5. read G1-G5 off the per-pair table + indep sub-split. Apply gate sec4 verdict + sec5 FAIL-semantics.
Conscience stays EXTERNAL (ARCHITECTURE sec1). North Star unaffected -- hardens the B-channel/L5 organ, migrates nothing.
Do NOT relabel any DEFECT pair to pass. Do NOT move a frozen bar after results (R7).

## SEC 2 -- NEXT+1 PREVIEW
TYPE A sourcing increment 2 -- INSTITUTION exemplar (same-institution / different-author / distinct-accession) +
scale author/citation each toward >=5 + independents toward >=20. Self-source live (proven viable (bb)) OR Founder
resolvable-DOIs ; every DOI Crossref-resolvable + every accession the REAL DAS line read LIVE. eval+source never
share a session (run the ladder in a separate TYPE B).

## SEC 3 -- PARALLEL / PENDING (not a plane unless picked)
  - L5 grounding: (x)+(y)+(z)+(aa)+(bb)+(cc) done ; (dd) disposition CLOSED + fix-gate FROZEN. Live next = apply
    predicate v1.1 under the frozen gate (SEC1). All L5 artifacts LOCAL-ONLY.
  - per-pair emit id-collision: claim-qualified ids (C015:S1xS2 etc.) are now LOAD-BEARING -- USED by the frozen gate
    G1/G2. If the emitter still prints bare ids, fix the emit before/with the fix run so each G1/G2 pair traces to its claim.
  - DEFECT + predicate v1.1: over_prune FAILs via TWO mechanisms (P3 fail-close 11/11 + P4-over-couple). The fix-gate
    (c7c67593) covers BOTH. Entry = SEC1.
  - tree hygiene: COSMETIC only (scoring_engine_v5_1 md5-dup ; e8 header mojibake/stale-"E7" ; .bak rollbacks ;
    adapter_sftc STRUCTURE-exclude widen ; E34 untracked ; STRATEGY rev2 uncommitted).
  - B-channel pyarrow access-violation dump on Win/Py3.12 -- benign, results stable, GOLD VERIFIED ; deferred.

## SEC 4 -- INTAKE (PIPELINE v1)
  unzip -> md5 every file vs MANIFEST.md5 -> VALID/INVALID (INVALID = STOP).
  03_REF/PACK_SPEC.md md5 MUST == f888f427597c7c45e6503c33f1babe24 (conveyor staleness guard). Mismatch = STOP.

## SEC 5 -- CLOSE
  At close: Claude hands the updated 00_SESSION_PACK.md + STATUS.md + CONTINUITY_LOG.md (STRUCTURE is AUTO-
  generated by the assembler). Founder places them in reports\, runs `build_pack.ps1 -N 139 -Spec
  SPEC_selfcheck_A.md` -> next zip.
  (3.10: this v138 pack was built by intake v137 -> -N 138 ; N is the NEXT version per PACK_SPEC "Claude builds
  pack v(N+1)" -> v139 next. Verify the assembler stamps v138 on THIS pack and v139 on the next.)
  The zip is transport only (Claude reads ONLY the zip). Git holds the individual files ; zip-blobs are NEVER committed.
  truth_input.txt + C009_C014_sourced.md + C015_sourced.md + l5_coupling_truth.jsonl + report_L5_partI.md +
  l5_C014_C015_P4_disposition.md + SPEC_L5_fixgate_v1.md + append scripts = LOCAL-ONLY, never in the pack, never public git.
