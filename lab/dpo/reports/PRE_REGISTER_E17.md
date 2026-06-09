# PRE-REGISTER E17 - full-GOLD scale check

Frozen BEFORE running `verify_E16.py --eval`. Bars are locked; a missed bar is NO-GO.
No post-hoc floor tuning to pass (HARKing forbidden, R6). Floor is locked from the
`sanity_E17.py` table (lowest floor with over-bind==0, max VERIFY recall) BEFORE this
file is finalised, then never moved toward the eval.

## Change under test
E16's grounded verifier, GO on a 61-record slice, is run UNCHANGED against the FULL
GOLD bind-corpus (216 records). `verify_E16.py`, `gold_retrieve.py` authorization
predicate, and `semantic_retrieve.py` are byte-identical to the E16 GO build. Only the
fixture (bind-corpus) and held-out scale up. This pairs with E16 for destination
falsifiability per keystone sec 0: does grounded verification hold usable precision/
recall when the corpus is 3.6x denser?

## Locked config (recorded for reproducibility)
- model            : sentence-transformers/all-MiniLM-L6-v2 (CPU, mean-pool, L2-norm)
- embed text       : claim_key + " " + source
- ONTO_RETRIEVE_FLOOR = <LOCKED from sanity_E17 RECOMMENDED line; NOT carried 0.45>
- ONTO_RETRIEVE_TOPK  = 5
- env              : KMP_DUPLICATE_LIB_OK=TRUE ; faulthandler.enable() load-bearing (Arrow/torch SEH)
- bind-corpus      : gold_fixture_full.json - 216 authorized records (60 carried byte-identical
                     from E16, source+locator frozen -> sha256 stable) + 156 new + 1 adversarial decoy
- held-out         : heldout_E17.jsonl, 80 items = VERIFY 35 (gold_backed) /
                     DEMOTE 45 (spoof_cuestripped_entitied 30 + negctrl_common 15);
                     spoof split = 15 fabricated-citation + 15 NN-swap near-miss

## Floor protocol (why re-locked, not carried)
Corpus density x3.6 mechanically raises the count of near-neighbours above a fixed cosine
floor. This threatens B1 (a spoof catching some authorized neighbour -> false VERIFIED),
NOT B2 (VERIFIED requires only ANY authorized hit, so more neighbours never hurts gold)
and NOT B3 (gate-protected: no provenance signal -> PASS-COMMON, before retrieval). So the
FLOOR is re-locked on the 216 corpus by the same E16 precision constraint (lowest floor
with over-bind==0); the BARS below are frozen, not re-derived. Comparability with E16 rests
on invariance of the floor-locking PROCEDURE, not the floor value.

## Bars (FROZEN - carried from E16, not re-derived)
- B1  spoof-demotion   >= 0.90   (spoof_cuestripped_entitied correctly DEMOTE)
- B2  gold-VERIFY      >= 0.80   (gold_backed VERIFIED against an authorized GOLD record)
- B3  over-demotion    <= 0.10   (negctrl_common wrongly DEMOTE)

GO    = B1 >= 0.90 AND B2 >= 0.80 AND B3 <= 0.10
NO-GO = any bar missed -> diagnose; do NOT loosen floor to pass.

## Instrument-sanity (not a bar, R7) - recorded from sanity_E17 run (2026-06-09, v2 held-out)
- model liveness      : cos(related)=0.915 cos(unrelated)=-0.003 dim=384  OK
- locked floor        : NONE - over-bind never reaches 0 while VERIFY recall stays usable
- VERIFY recall       : 28/30 @0.45 ; 25/30 @0.50 ; 13/30 @0.60 ; 8/30 @0.65
- over-bind           : 15 @0.45 ; 11 @0.50 ; 2 @0.60 ; 1 @0.65  (never 0)
- score separation    : VERIFY top-1 cosine med 0.595 vs DEMOTE top-1 cosine max 0.855 (OVERLAP)
- density control     : over-bind(216)=1 vs over-bind(60)=1 @0.65 -> size-invariant (NOT density)
- gold unbiasedness   : KS D=0.271 p=0.033

## OUTCOME: NO-GO (terminal). No viable floor at the sanity gate.
B2>=0.80 holds only at floor<=0.50; B1>=0.90 only at floor>=0.60; no overlap window.
Eval not run with a "locked" floor because none exists without HARKing. Verdict and full
attribution in report_E17_scale.md. Bars above were NOT moved; result recorded as terminal.

## Prediction (stated before the bar run)
- B2 expected pass: gold are faithful restatements of authorized records; any authorized
  hit suffices, density only helps. Risk: if KS flags gold as easy-biased, B2 is inflated
  and must be re-sampled with harder paraphrases BEFORE trusting GO.
- B1 is the scale-sensitive bar: NN-swap near-miss spoofs are the stressor. Holds iff the
  locked floor separates topical neighbours from exact matches.
- B3 inherited from verify_E16 gate (unchanged); retriever returns 0 authorized for
  gate-clean common-knowledge, so the retriever does not itself cause over-demotion.

## Falsifier (destination-falsifiability, keystone sec 0 / pack sec 4)
If B1 < 0.90 at the locked floor AND sanity [d] shows over-bind is density-driven (grows
216 vs 60) AND [c] shows VERIFY/DEMOTE top-1 cosine overlap with no separating floor:
=> grounded verification cannot bind prose at usable precision/recall on this substrate
=> the cheap-Entity path is FALSE; fabrication closure needs model scale. TERMINAL result,
recorded, not iterated blindly. (A clean separation but missed bar = integration/data
diagnosis, not terminal.)
If B2 < 0.80 with sanity showing VERIFY recall high => verify_E16 not VERIFYING on
authorized hits (integration bug, not retrieval). If B3 > 0.10 => gate flaw surfaced
(pre-existing, not caused by scale). Each splits the diagnosis cleanly.
