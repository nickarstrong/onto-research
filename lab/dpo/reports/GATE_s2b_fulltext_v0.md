# GATE_s2b_fulltext_v0.md -- pre-registered gate for the B2 full-text fallback (DRAFT -> FREEZE on accept)

date   : 2026-06-16
plane  : RESEARCH / S2(b) -- B2 UNCLEAR-resolver gate. THIS DOC = eval design only. NO predicate byte (R7).
home   : onto-research/reports (dateable priority + reproducibility ; generic-safe, ZERO dois/claim-texts/abstracts)
status : FROZEN 2026-06-16 (engineer-applied amendments A1+A2 below ; md5-locked, this is the bar of record).
         A1: FT-CC raised 16->24 (10 thin-correct / 10 wrong / 4 no-OA) + G7/G8 declared existence-bars with
         explicit wide-CI honesty line (sec 6). A2: G8 binds to read-coverage -- a support missed because its
         bytes were unread = no-coverage UNCLEAR, never NOT ; read-strategy pinned in sec 5 STEP 2.
binds  : SPEC_s2b_v0.md (md5 80bdf2a9, frozen ; G1-G4) + GATE_s2b_offtopic_v0.md (frozen ; G5-G6). This gate
         ADDS to their bars ; relitigates none of G1-G6.

## 0 WHAT THIS GATES (one paragraph, zero-context reader)
v0 reads the ABSTRACT only (SPEC sec 8 explicitly DEFERS full-text). After the abstract layer (B1 binding +
B2 supports + the off-topic predicate), a residual UNCLEAR class remains that an abstract cannot adjudicate:
honest-thin cites (no/short abstract -> no_abstract or b2_unclear), generic-filler near-overlaps the off-topic
predicate cannot separate at the abstract level, and off-topic wrong-binds whose live abstract came back empty.
The proposed FULL-TEXT FALLBACK re-adjudicates ONLY these UNCLEAR items against the source's OPEN-ACCESS full
text. This is strictly higher false-fire risk than the abstract: full text is long, so a non-proposing model
can (i) hallucinate SUPPORT for a wrong cite (poison) or (ii) miss a real support and emit NOT on a correct
cite (castration). This doc freezes the no-poison + no-castration bars any such fallback must clear FIRST. The
policy itself is a SEPARATE later session ; this is eval, not fix (R7).

## 1 THE DECISION RULE (falsifiable, R6) -- UNCLEAR-only resolver, fail-closed on no-OA
The fallback runs ONLY when the abstract layer's verdict is UNCLEAR (reason in {no_abstract, b2_unclear}).
It NEVER sees an item already decided SUPPORTS or NOT at the abstract layer -- those outcomes are frozen
(G1-G6 unchanged). For a qualifying item:

  1. RESOLVE OA full text by DOI from an open-access source (e.g. Unpaywall best-OA-location / PMC / arXiv).
     No OA full text found -> return UNCLEAR (reason=no_fulltext). FAIL-CLOSED. No paywall scrape, no fabrication.
  2. OA full text found -> the same grounded, NON-PROPOSING B2 instance adjudicates the claim against the full
     text (not the abstract), emitting one of SUPPORTS / NOT / UNCLEAR. Reason-coded fulltext_supports /
     fulltext_not / fulltext_unclear. The item's fetched-snapshot records the OA source + retrieval result.

The fallback may CHANGE an abstract-UNCLEAR to SUPPORTS or NOT, or LEAVE it UNCLEAR. It can do nothing else.
By construction it only ADDS resolution to the UNCLEAR bucket ; it cannot move G1-G6 outcomes.

APPROACH-LEVEL FALSIFIER (R6): if the non-proposing instance, reading full text, cannot separate
honest-thin-but-CORRECT cites (full text supports -> must SUPPORTS) from wrong/off-topic cites (full text
does not support -> NOT) WITHOUT false-firing -- i.e. a correct cite's full text is adjudication-
indistinguishable from a wrong cite's at the bar -- then full-text fallback is NOT safely gateable and the
residual UNCLEAR STAYS UNCLEAR (the current safe state). The run REJECTS the policy ; it does not tune it.

## 2 THE CLEAN-CONTROL SET (blocking finding -- must be BUILT, R7/R2/C5)
The abstract gate's CC cannot test this layer (CC items are abstract-resolvable ; they never reach full-text).
A purpose-built FT control set is REQUIRED, exercising BOTH false-fire surfaces, in declared minimum counts.
All dois grounded LIVE before entry (anti-fab 3.9) ; LOCAL-ONLY, bait-class ; never public git.

  FT-thin-correct : correct cite, abstract thin/UNCLEAR at the abstract layer, but the OA full text DOES
                    state the claimed result. Correct verdict = SUPPORTS. This is the G8 castration surface
                    (a brittle full-text reader could miss the support and emit NOT).            n >= 10
  FT-wrong        : wrong-binding OR off-topic cite that reached UNCLEAR (e.g. empty live abstract), OA full
                    text confirms the source does NOT support the claim. Correct verdict = NOT. This is the
                    G7 poison surface (a credulous full-text reader could hallucinate SUPPORT).   n >= 10
  FT-no-OA        : correct cite with NO open-access full text. Correct verdict = UNCLEAR (fail-closed). This
                    is the G9 honesty surface.                                                    n >= 4
  TOTAL n(FT-CC) >= 24. Verify CONTENTS, not just md5 (3.7): each FT-thin-correct's full text genuinely states
  the result ; each FT-wrong's full text genuinely lacks it ; each FT-no-OA genuinely has no OA copy.

## 3 BARS (pre-registered, frozen ; HARD dominates, C1)
  G6 (carried)            : G1-G5 still hold under the fallback (the fallback only fires on abstract-UNCLEAR ;
                            it may not move any J1/J2/J3/J4/J5/CC outcome already decided at the abstract layer).
  G7 (HARD, no-poison)    : ZERO FT-wrong items return SUPPORTS. A wrong/off-topic cite green-lit from full
                            text is the poison this layer must never add. Mirrors G1/G2. tol 0.
  G8 (HARD, no-castration): ZERO FT-thin-correct items return NOT, PROVIDED the supporting passage is inside
                            the full-text bytes the B2 instance actually read (read-coverage controlled, see
                            sec 5 STEP 2). A correct cite whose full text supports, flipped to NOT, is
                            castration. An item whose supporting bytes fell OUTSIDE B2's read window is NOT a
                            G8 failure -- it is a no-coverage UNCLEAR (a build gap, not adjudication); the
                            read-strategy must surface it as UNCLEAR, never as NOT. Mirrors G3/G5. tol 0.
  G9 (honesty/fail-closed): every FT-no-OA item returns UNCLEAR (reason=no_fulltext). A forced verdict with
                            no full text in hand is fabrication-by-omission. Mirrors G4.
  PASS (fallback is BUILDABLE+VALID) = G6 & G7 & G8 & G9. RESOLUTION YIELD (how many honest-thin UNCLEAR the
  fallback turns into SUPPORTS/NOT) is a DIAGNOSTIC READOUT, NOT a bar -- under-resolving is honest UNCLEAR,
  over-resolving in either direction is the G7/G8 failure.

## 4 WHAT THIS DOC DOES NOT DO
  - No predicate byte. s2b_v0.py is UNCHANGED this session (R7 ; eval+fix never share).
  - No FT-CC items written here (this doc is public-safe). FT-CC construction is the FIRST step of the next plane.
  - No tuning loop. The run either clears G6-G9 or REJECTS the fallback (residual UNCLEAR stays honest). Results
    never relitigate the bar (R7).

## 5 NEXT PLANE (handed in close pack ; do NOT start here)
  PLANE: implement-and-run the full-text fallback against this frozen gate.
  STEP 1: build FT-CC (n>=24: 10 thin-correct / 10 wrong / 4 no-OA), dois + OA-status grounded LIVE, md5-lock --
          BEFORE any policy byte. STEP 2: implement the OA-resolver + the fulltext B2 call as a downstream
          UNCLEAR-only resolver in s2b_v0.py (it imports no abstract-layer bar ; abstract verdicts pass through
          unchanged). PIN THE READ-STRATEGY HERE (G8 binds to it): full text exceeds the B2 context, so the
          reader must either (i) feed the whole text under a verified token budget, or (ii) chunk with a
          coverage guarantee -- every chunk adjudicated, verdict = SUPPORTS if ANY chunk supports, NOT only if
          NO chunk supports AND coverage was complete, else UNCLEAR (reason=no_coverage). A miss caused by
          unread bytes MUST emit UNCLEAR, never NOT (else G8 catches a build artifact, not castration). STEP 3: --selftest must re-prove G1-G6 (no regression) AND prove G7/G8/G9 offline on a
          fake OA-getter, BEFORE any live fetch. STEP 4: run on FT-CC live, report G7/G8/G9 PASS + resolution
          yield readout.
  trigger : "LABA, S2B FULLTEXT POLICY"

## 6 HONEST GAPS (R7, pre-stated)
  - OA COVERAGE is unknown and may be LOW: many DOIs have no open-access full text -> fail-closed UNCLEAR.
    The fallback's resolution yield is therefore bounded by OA availability, not just by the bars. This is a
    diagnostic ceiling, stated up front so a low yield is not read as a failure.
  - Full text is long ; the non-proposing instance's context/cost per item is far higher than the abstract.
    Yield-per-cost is a build concern for the next plane, not a bar here.
  - G7/G8 are EXISTENCE bars (one failure rejects), not population-rate estimates. n=10 per surface gives the
    stress test teeth but does NOT bound the live false-fire rate -- a 10/10 PASS is precision-first evidence
    with a deliberately wide CI, not a guarantee the policy never poisons/castrates in the wild. Stated up
    front so a clean PASS is not over-read.

freeze: on Founder accept, md5-lock this doc and the section 3 bars before the next plane's first byte.
