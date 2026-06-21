# REPORT_temporal_probe_v4.md -- temporal channel V5 probe (live Wikidata/Wikipedia)

session : LABA, TEMPORAL CHANNEL V5
date    : 2026-06-21
type    : CONCEPT (design + probe, no build). Probe RUN live (Tommy-side), trace-grounded.
          CONFIRM same-sentence logic ALSO unit-tested offline (--selftest) before the live run.
binds   : REPORT_temporal_probe_v3.md sec3 (D1'' named) + sec5 (V5 design consequence) ;
          REPORT_temporal_probe_v1.md (D1/D2/D3) ; ARCHITECTURE_master sec2
          ("flag on CLEAN = castration; false-flag <= 0.10").
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ; eval/o0/o0_s4_founder_labels.jsonl (v199) ; +4 traps.
oracle  : Wikidata wbsearchentities + EntityData (date predicates + P31) + FULL Wikipedia plaintext
          (action=query prop=extracts explaintext). Pure stdlib HTTP, local.
probe   : o0_temporal_probe_v4.py ; trace o0_temporal_probe_v4_trace.json.
status  : PROBE DONE -- banked. OVERALL = FAIL on bars, BUT the V5 target (D1'') is CLOSED and the
          fail is PRODUCTIVE: closing the cross-sentence CONFIRM bleed let the refute path engage
          for the first time, which exposed D4 (same-title WORK-decoy refute) on a CONCRETE CLEAN
          claim. R15 refute-restraint is now directly testable -- and currently fails.

## 0  ONE NUMBER
OVERALL = FAIL (P1 AND P2 PASS ; P3 FAIL). The single failing bar: TRAP_unconfirm -> REFUTE
(F-D4 TRIGGERED). Same-sentence CONFIRM did exactly its job (D1'' closed, F-D1'' clear,
regression guard held), so the spurious 1968 CONFIRM is gone; with the CONFIRM short-circuit
removed, the trap finally reached the refute path -- and REFUTED a CLEAN claim.

## 1  CLAIM VERDICTS (trace-grounded)
| id            | label | year      | verdict | trace reason                                                    |
|---------------|-------|-----------|---------|-----------------------------------------------------------------|
| heldout_03    | DIRTY | 1925      | REFUTE  | D3 holds. Work title -> Q24563361 P577=1929 != 1925. refute_anchor.qid = Q24563361. |
| heldout_09    | CLEAN | 1887      | CONFIRM | **P1 regression guard HELD.** "Heinrich Hertz" person-dominant -> full text; under SAME-SENTENCE, 1887's sentence carries an admissible P575/P585 verb (text beyond the old +-200 window). The live-only risk cleared. |
| heldout_14    | CLEAN | 1900      | N/A     | 1900 in abstract -> not load-bearing. Correct.                  |
| heldout_16    | CLEAN | 1847      | CONFIRM | **P1.** Semmelweis Q59736 full text; "In 1847, he proposed..." -- "propos" (P575/P585) same-sentence. Verified offline (selftest) + live. |
| heldout_18    | DIRTY | 1950,2014 | ABSTAIN | **P2.** 1950 abstract-covered (N/A). 2014: no admissible verb in any same sentence post header-strip -> no CONFIRM, no REFUTE. Same-sentence is tighter than +-200 -> 18 stays ABSTAIN. |
| TRAP_python   | CLEAN | 1991      | CONFIRM | Python Q28865 P571=1991 (WD predicate, not fulltext). Sound. Not refuted. |
| TRAP_titanic  | CLEAN | 1997      | CONFIRM | Titanic Q44578 P577=1997 (WD predicate). Sound. Not refuted.    |
| TRAP_norefute | CLEAN | 1910      | CONFIRM | Russell/Principia full text 1910 ("publish", P577 same-sentence). Not refuted. |
| TRAP_unconfirm| CLEAN | 1968      | REFUTE  | **F-D4 TRIGGERED.** 1968 no longer CONFIRMs (D1'' closed). Subject "Solaris" -> Q261281 the **1961 source NOVEL** (NOT a film decoy); P577=1961 != 1968 -> REFUTE. Persons Boris Nirenburg (Q4321483) + Lem D3-blocked; only the work-title refuted. refute_anchor = {Solaris, Q261281, P577, 1961}. |

## 2  WHAT IS BANKED (true, trace-verified)
- **D1'' CLOSED -- the V5 target.** CONFIRM co-location scope changed from +-WINDOW=200 chars to
  SAME-SENTENCE (year AND an admissible-class event verb in ONE article sentence; predicate-class
  anchor + "== header ==" strip + left word-boundary all retained from V4). The cross-sentence
  bleed is gone: TRAP_unconfirm's 1968 (filmography line, no in-sentence release verb) no longer
  confirms against the 2024-edition "published" two sentences away. F-D1'' clear.
- **CONFIRM is SOUND on this set.** Offline selftest (no network) 3/3: 16 -> CONFIRM
  ("In 1847, he proposed"), TRAP_unconfirm -> ABSTAIN (no same-sentence co-location), control 2024
  -> CONFIRM (proves the ABSTAIN is genuine scoping, not a dead matcher). Live agrees.
- **P1 regression guard HELD live (the V4-named watch item).** Same-sentence kept BOTH 16 and 09.
  16 was offline-provable; 09 was NOT (v3 snippet truncated mid-sentence) and was pre-registered as
  the live regression risk -- it cleared: the full 1887 sentence carries an admissible P575/P585
  verb beyond the old +-200 window. Had 09 ABSTAINed, P1 would have FAILed by design (-> V6
  sentence+governing-clause), not by tuning license. It did not.
- **P2 HELD.** 03 REFUTE anchored on the 1929 paper Q24563361 (D3); 18 ABSTAIN (no same-sentence
  admissible verb near 2014). Refute path + WD-predicate confirm path + D2/D3 untouched by V5.
- **WD-predicate CONFIRM unaffected.** TRAP_python/titanic confirm via P571/P577 in years_by_pred
  (not fulltext) -> same-sentence change cannot touch them.

## 3  WHAT IS NOT BANKED -- D4 (NEW, exposed; R7/R3 precision dominates)
- **D4 (same-title WORK-decoy refute).** With the CONFIRM short-circuit removed, TRAP_unconfirm
  reached the refute path and REFUTED a CLEAN claim. The claim is about the **1968 TV adaptation**;
  the subject extractor took the work-title "Solaris" and resolved it to **Q261281, the 1961 source
  NOVEL** -- a DIFFERENT work sharing the title -- whose P577=1961 != 1968 -> REFUTE. This is a
  CASTRATION on CLEAN (ARCHITECTURE_master sec2: flag-on-CLEAN is the forbidden failure).
  - D3 does NOT cover this: D3 blocks PERSON-name labels from anchoring a refute (it correctly
    blocked Boris Nirenburg Q4321483 and Lem here). A WORK-role label is structurally outside D3.
  - Root cause: refute requires only "resolved entity is a work AND has a date-predicate year !=
    claim year". It does NOT require the resolved work to BE the claim's event-subject. A same-title
    source/sibling/derivative work (novel vs. its adaptation; film remake vs. original) injects a
    confirmable wrong year.
- **REFUTE stays ADVISORY -- now with a CONCRETE CLEAN false-refute, not just a theoretical gap.**
  REFUTE must not be a gate output (must not down-rank / reject) until D4 is closed. fa_live on this
  set is still 0 (no DIRTY absorbed -- 03 REFUTE correct, 18 ABSTAIN), but the bar for REFUTE is
  CLEAN-precision, and a CLEAN was refuted.

## 4  R15 -- NOW DIRECTLY TESTABLE (and currently FAILING), no longer owed
The V2-V4 gap was that TRAP_unconfirm always CONFIRMed (short-circuit), so refute-restraint was
never exercised. V5's same-sentence CONFIRM removed the short-circuit -- the trap finally reached
refute. Outcome: it did NOT restrain (REFUTE on a CLEAN, confirmable-wrong-year, same-title work).
So R15 refute-restraint is now a concrete, falsifiable, OPEN target (was untested). The trap did its
designed job. Refute-restraint to date is evidenced ONLY by heldout_03's same-label PERSON-decoy
rejection (D3); the WORK-decoy case (D4) is now demonstrated UNSAFE.

## 5  DESIGN CONSEQUENCE (for V6, NOT built this session)
- D4 fix = WORK-decoy refute restraint. A refute may anchor on a work ONLY if the resolved work IS
  the claim's event-subject, not a same-title source/sibling. Candidate mechanisms (V6 to choose +
  probe one, engineer-owned):
    (a) event-type match between claim predicate-class and the resolved work's date predicate
        (claim "adaptation/released" = P577-of-the-ADAPTATION; refuting on the novel's P577 is a
        type/instance mismatch -- the refuting year must describe the SAME event the claim asserts);
    (b) require the resolved work's enwiki/description to share the claim's distinguishing tokens
        beyond the bare title (here: "television"/"1968"/"Nirenburg" absent from the 1961-novel
        entity) -- a work-side analogue of D2 ctx-overlap, with ABSTAIN on overlap 0;
    (c) block refute when a same-title sibling exists whose date matches the claim (disambiguation
        must be positive, not first-hit).
- CONFIRM, header-strip, word-boundary, predicate-class, D2, D3: FROZEN (closed).
- Re-run the same 9. Bars carry: 16+09 CONFIRM, 18 ABSTAIN, 03 REFUTE@Q24563361, traps not refuted,
  TRAP_unconfirm reaching ABSTAIN (D4 closed) -- now the LOAD-BEARING bar.

## 6  GATE ROLE (precision-first, unchanged priority)
- CONFIRM: D1'' closed, sound on this set. Still NOT promoted to absorb-enabler -- promotion needs
  broader validation + a real denominator (sec 7). But the specific unsoundness that blocked it is
  now closed; CONFIRM is bankable as "same-sentence sound, D1'' clear".
- REFUTE: NOT shippable (advisory). D3 holds for persons; D4 (works) demonstrated UNSAFE on CLEAN.
  Refute must remain non-gating until V6 closes D4.

## 7  DENOMINATOR (R15, unchanged)
S4-frozen G3 >= 0.20 stays dead (max 0.150; a sound CONFIRM adds heldout_16 -> 2/20 = 0.100).
Real G3 yield = Founder-owned held-out RE-CUT, not this channel's gate. (Parallel decision open.)

## 8  FALSIFIER STATUS
- F-D1'' (TRAP_unconfirm CONFIRM via cross-sentence bleed): clear (1968 no longer confirms).
- F-regress (16 or 09 ABSTAIN under same-sentence): clear (both CONFIRM live; 09 the live risk, held).
- F-D3 (03 anchor != Q24563361): clear (anchor = Q24563361).
- F-D4 (TRAP_unconfirm REFUTED = work-title decoy refute): **TRIGGERED.** Load-bearing. Anchor =
  Q261281 (1961 source novel), P577 1961 != 1968. -> V6.

## 9  NEXT PLANE (named, NOT opened)
CONCEPT temporal channel V6 (design + probe, no build): close D4 = same-title WORK-decoy refute
restraint (resolved work must be the claim's event-subject, not a same-title source/sibling; pick +
probe ONE of 5(a)/(b)/(c)). CONFIRM + header-strip + word-boundary + predicate-class + D2 + D3
FROZEN. Re-run the same 9. Bars: 16+09 CONFIRM, 18 ABSTAIN, 03 REFUTE@Q24563361, traps not refuted,
TRAP_unconfirm -> ABSTAIN (D4 closed, load-bearing). Falsifier F-D4' = TRAP_unconfirm still REFUTED.
Trigger: "LABA, TEMPORAL CHANNEL V6".
Parallel Founder decision (still open): S4 held-out RE-CUT for a real G3 yield denominator.

---
*REPORT_temporal_probe_v4 - 2026-06-21 - OVERALL FAIL on bars, V5 target (D1'') CLOSED. Same-sentence
CONFIRM co-location (predicate-class + header-strip + word-boundary retained) closed the
cross-sentence bleed: F-D1'' clear, regression guard 16+09 HELD live (09 was the pre-registered
live-only risk -- the full 1887 sentence carries an admissible verb beyond the old +-200), 18
ABSTAIN, offline selftest 3/3. Removing the CONFIRM short-circuit let the refute path engage for the
first time on TRAP_unconfirm -> it REFUTED a CLEAN claim: "Solaris" resolved to Q261281 the 1961
SOURCE NOVEL (P577=1961 != claim's 1968 adaptation year). NEW D4 = same-title WORK-decoy refute,
structurally outside D3 (which blocks only person-name labels). REFUTE stays advisory/non-gating;
R15 refute-restraint now directly testable and currently failing. Next: V6 = work-decoy refute
restraint. Trigger "LABA, TEMPORAL CHANNEL V6".*
