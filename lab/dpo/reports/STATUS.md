# STATUS.md -- ONTO lab current-state snapshot (pack v138)

PHASES   : phase 1 (band-A TRUST) CLOSED ; phase 2 (disposition-audit) CLOSED ; phase 3 (surgical correction)
           CLOSED (fix(a) RULE A1_GROUND_OR_DECLARE standing). fix(b) bounded-DPO leg CLOSED = GATE FAIL =
           honest NO-MIGRATION (HARD bars held ; adapter rolled back ; conscience EXTERNAL, RULE fix(a) stands).
CONSCIENCE: EXTERNAL (A-channel self-consistency + B-channel grounded L1-L4 GOLD + L5 internet). Frozen organs
           import-only, never mutated. Precision-first: false_flag <= 0.10 HARD dominates detect.

ACTIVE PLANE : L5 internet grounding (PART I independence predicate) -> predicate FIX. DISPOSITION CLOSED + GATE FROZEN.
  - predicate + validator = FROZEN (run_L5_partI_validate.py md5 b1f4aae4 ; AST anchors snapshotted in SPEC_L5_fixgate_v1
    sec1 ; NOT touched since (z) commit 6b06e61).
  - P4-edge disposition CLOSED (dd), 4/4, each pair's OWN reference list read from primary source (LOCAL-ONLY
    eval/_local/l5_C014_C015_P4_disposition.md):
      C015 S3xS4 Yan/Kirchdoerfer = CITATION-EXEMPLAR (Yan cites Kirchdoerfer 2018 ; relabel independent->citation).
      C015 S1xS2 Wrapp/Walls = DEFECT . C015 S1xS3 Wrapp/Yan = DEFECT . C014 S1xS2 Wu/Zhou = DEFECT (no direct cite).
    1 exemplar + 3 P4-over-couple defect. No relabel-to-pass (R7).
  - R16 ground for v1.1: P4 reads refs_all = Crossref `reference` UNION OpenCitations `cited` ; real cites are in
    Crossref `reference`, the 3 DEFECT edges enter via the OC union -> discriminator = Crossref-reference-only P4
    + P3 positive-signal (DESIGN HYPOTHESIS ; gate-agnostic).
  - FIX-GATE FROZEN (dd): eval/_local/SPEC_L5_fixgate_v1.md md5 c7c67593. G1 HARD P4-suppress 3 DEFECT ; G2 HARD
    P4-preserve (exemplar S3xS4 + Walls->Kirchdoerfer S2xS4 + Wrapp/Kirchdoerfer author S1xS4) ; G3 HARD P3-resolve ;
    G4 HARD no-castration (recall 1.0 + leak 0) ; G5 headline (over_prune<=0.10, bal_acc>=0.85). HARD G1-G4 dominate.

NEXT     : predicate FIX (SEPARATE TYPE B ; eval != source). PREREQ relabel C015 S3xS4->citation (SOURCE act, LOCAL).
           THEN snapshot AST -> apply predicate v1.1 (provenance_edge P4 source + pair_predict P3 positive-signal ;
           ONLY those + refs_all assembly may move ; scorer/verdict/clustering/contents/readout AST-identical) ->
           re-hash -> build->contents->net-precheck->--run on the accession-bearing set -> read G1-G5 (gate sec4) ->
           sec5 FAIL-semantics. Predicate FROZEN until the AST-snapshot step. Trigger "LABA, L5 FIX".
           After fix: sourcing increment 2 (institution + scale to 5).

HONEST GAPS (R7, no fabrication to hit counts):
  - INSTITUTION class still 1 (P3-masquerade C008) -- needs same-institution/different-author/distinct-accession.
  - author/citation each at 2 ; need +3 real-accession pairs each toward >=5 ; independents toward >=20.

INFRA    : conveyor PACK_SPEC.md md5 == f888f427 (staleness guard). Tree-hygiene remainder = COSMETIC, deferred
           EXCEPT per-pair emit id-collision (claim-qualify ids) -> LOAD-BEARING, now USED in the frozen gate (G1/G2).

GIT      : onto-research (public) holds reproducibility + dateable priority only. NEVER public: weights, bait-sets,
           held-out, GOLD/corpora, AND all L5 truth-set artifacts -- incl. l5_C014_C015_P4_disposition.md +
           SPEC_L5_fixgate_v1.md (carry truth-set pair identities). This session (dd): NOTHING committed (CONCEPT ;
           disposition + gate = LOCAL-ONLY).
