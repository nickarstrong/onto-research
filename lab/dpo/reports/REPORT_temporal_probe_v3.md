# REPORT_temporal_probe_v3.md -- temporal channel V4 probe (live Wikidata/Wikipedia)

session : LABA, TEMPORAL CHANNEL V4
date    : 2026-06-21
type    : CONCEPT (design + probe, no build). Probe RUN live (Tommy-side), trace-grounded.
          CONFIRM logic ALSO unit-tested offline against frozen V3 snippets before the live run.
binds   : REPORT_temporal_probe_v2.md sec3 (D1 residual named) + sec5 (V4 design consequence) ;
          REPORT_temporal_probe_v1.md (D1/D2/D3) ; ARCHITECTURE_master sec2
          ("flag on CLEAN = castration; false-flag <= 0.10").
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ; eval/o0/o0_s4_founder_labels.jsonl (v199) ; +4 traps.
oracle  : Wikidata wbsearchentities + EntityData (date predicates + P31) + FULL Wikipedia plaintext
          (action=query prop=extracts explaintext). Pure stdlib HTTP, local.
probe   : o0_temporal_probe_v3.py ; trace o0_temporal_probe_v3_trace.json.
status  : PROBE DONE -- banked. Pre-registered bars OVERALL = PASS. D1 (header/off-class) CLOSED.
          BUT a same-family soundness residual (D1'') surfaced via the R15 trap; R15 still OPEN.

## 0  ONE NUMBER
OVERALL = PASS (P1 AND P2 AND P3). D1 residual (incidental event-verb / section-header
co-location) CLOSED: heldout_18 -> ABSTAIN, regression guard 16+09 -> CONFIRM held.
Caveat (load-bearing): the CONFIRM co-location mechanism is NOT yet sound -- TRAP_unconfirm
spuriously CONFIRMed via a cross-sentence +-WINDOW bleed. 18's ABSTAIN is real but data-dependent,
not structural. CONFIRM stays advisory (not an absorb-enabler) until same-sentence co-location (V5).

## 1  CLAIM VERDICTS (trace-grounded)
| id            | label | year      | verdict | trace reason                                                    |
|---------------|-------|-----------|---------|-----------------------------------------------------------------|
| heldout_03    | DIRTY | 1925      | REFUTE  | D3 holds. Person "Edwin Hubble" (Q54281574) BLOCKED; work title -> Q24563361 P577=1929 != 1925. refute_anchor.qid = Q24563361. |
| heldout_09    | CLEAN | 1887      | CONFIRM | Regression guard. "Heinrich Hertz" person-dominant -> full text; 1887 co-located with "observing" (P575/P585, claim class). |
| heldout_14    | CLEAN | 1900      | N/A     | 1900 in abstract -> not load-bearing. Correct.                  |
| heldout_16    | CLEAN | 1847      | CONFIRM | Regression guard. Semmelweis Q59736 full text; 1847 co-located with "demonstrated"/"proposed" (P575/P585, claim class). |
| heldout_18    | DIRTY | 1950,2014 | ABSTAIN | **D1 CLOSED.** 1950 abstract-covered (N/A). 2014: Cleverbot Q1100860 resolved, NO P585-class verb co-located post header-strip -> no CONFIRM, no REFUTE. |
| TRAP_python   | CLEAN | 1991      | CONFIRM | Python Q28865 P571=1991 (WD predicate). Sound. Not refuted.     |
| TRAP_titanic  | CLEAN | 1997      | CONFIRM | Titanic Q44578 P577=1997 (WD predicate). Sound. Not refuted.    |
| TRAP_norefute | CLEAN | 1910      | CONFIRM | Russell/Principia full text 1910 ("publish", P577). Not refuted; CONFIRM short-circuit (narrow). |
| TRAP_unconfirm| CLEAN | 1968      | CONFIRM | **R15 trap CONFIRMED, SPURIOUSLY.** "Solaris" -> Q261281 *Solaris (novel)*. 1968 (filmography line "Solaris (1968), a Soviet TV play...") co-located within +-200 of an UNRELATED "published" (a 2024 fine-press edition). Cross-sentence window bleed. |

## 2  WHAT IS BANKED (true, trace-verified)
- **D1 (header / off-class) CLOSED.** Two-part fix landed:
  (a) PREDICATE-CLASS anchor: admissible co-location verbs = those whose WD predicate is in the
      CLAIM SENTENCE's licensed set (event_predicates_for). heldout_18's 2014 claim class = {P585};
      "develop" = P571 (off-class) -> not admissible.
  (b) "== header ==" strip + LEFT word-boundary match. The only "develop" near 2014 lived in the
      section header "== Developments ==" -> removed.
  -> heldout_18 ABSTAIN. F-D1 clear.
- **Regression guard HELD (the V3-deferred risk, now a HARD bar).** The literal report-sec5 fix
  ("exact claim keyword") was FALSIFIED on frozen V3 trace BEFORE the live run: 16 confirms on
  article "demonstrated/proposed" (claim verb "observed"); 09 on "observing/paper" (claim verbs
  "confirmed/generated/detected"). Exact-kw would regress BOTH. Predicate-class anchoring keeps
  16+09 (all P575/P585) and still kills 18. Verified offline (unit test on the 3 frozen snippets:
  09 CONFIRM, 16 CONFIRM, 18 ABSTAIN) and live (same).
- **D2 + D3 frozen and holding.** 09 person-dominant CONFIRM; 03 REFUTE anchored on the 1929 paper
  Q24563361, person decoy Q54281574 rejected.

## 3  WHAT IS NOT BANKED -- D1'' residual (R7, precision dominates)
- **D1'' (NEW, same family, deeper).** The CONFIRM co-location uses a +-WINDOW=200 CHAR span, which
  bleeds ACROSS sentences. TRAP_unconfirm CONFIRMed 1968 because an admissible verb ("published",
  about a 2024 edition) sat within +-200 of a filmography "1968" in the *novel's* article -- two
  unrelated events, one window. On a CLEAN claim this is harmless to fa_live, but the CONFIRM is
  UNSOUND (fired for the wrong reason). The same mechanism could false-confirm a DIRTY year that
  happens to land near an admissible verb in the resolved entity's article. heldout_18's ABSTAIN
  held only because Cleverbot's text had no P585 verb near 2014 -- data-dependent, not structural.
  FIX (V5): co-location must be SAME-SENTENCE (the year and the event verb in one sentence of the
  article), not +-200 chars. Re-validate 16 + 09 still CONFIRM same-sentence; 18 stays ABSTAIN;
  TRAP_unconfirm flips CONFIRM -> ABSTAIN (then it finally exercises the refute path / restraint).

## 4  R15 -- STILL OPEN (trap CONFIRMED, did not reach ABSTAIN)
The V4 R15 trap was meant to have an UNCONFIRMABLE correct year so CONFIRM cannot short-circuit,
forcing ABSTAIN and exercising refute-restraint against a same-label WORK decoy. It FAILED its
purpose two ways: (1) the correct year 1968 WAS confirmable (spuriously, via window bleed -- see
D1''), so it CONFIRMed instead of ABSTAINing; (2) the refute path never engaged, so work-decoy
refute-restraint (D4) remains UNTESTED, not cleared. A famous-or-adjacent subject keeps confirming.
Carry to V5 AFTER the same-sentence fix: with same-sentence co-location, 1968 should NOT confirm
(the 1968 filmography line carries no release verb in-sentence) -> the trap should reach ABSTAIN or
engage refute, finally testing restraint. Refute-restraint is still evidenced ONLY by heldout_03's
decoy-rejection (supporting, not sufficient).

## 5  DESIGN CONSEQUENCE (for V5, NOT built this session)
- CONFIRM: change co-location scope from +-WINDOW chars to SAME-SENTENCE (split article into
  sentences; require year + an admissible-class event verb in the SAME sentence). Keep predicate-
  class + header-strip + word-boundary. HARD regression guard: 16 + 09 stay CONFIRM same-sentence
  (16 "In 1847, he proposed..." OK; 09 "...November 1887 with his paper..." -- check "paper"/an
  observ verb shares the 1887 sentence; if not, this is the new regression risk to watch).
- TRAP_unconfirm: keep; expect CONFIRM -> ABSTAIN under same-sentence (then it tests restraint).
- REFUTE + DISAMBIG: unchanged (D2/D3 closed).

## 6  GATE ROLE (precision-first, unchanged priority)
- CONFIRM: NOT shippable as an absorb-enabler. D1-header is closed but D1'' (cross-sentence bleed)
  leaves CONFIRM UNSOUND. fa_live on this set = 0 (03 REFUTE, 18 ABSTAIN -- neither DIRTY absorbed),
  but soundness, not just this set's fa, is the bar.
- REFUTE: anchor-correct (D3 closed), stays ADVISORY until a no-confirm trap actually engages and
  is restrained (R15).

## 7  DENOMINATOR (R15, unchanged)
S4-frozen G3 >= 0.20 stays dead (max 0.150; a sound CONFIRM would add heldout_16 -> 2/20 = 0.100).
Real G3 yield = Founder-owned held-out RE-CUT, not this channel's gate. (Parallel decision still open.)

## 8  FALSIFIER STATUS
- F-D1 (18 CONFIRM): clear (18 ABSTAIN).
- F-regress (16 or 09 ABSTAIN): clear (both CONFIRM).
- F-D3 (03 anchor != Q24563361): clear (anchor = Q24563361).
- F-D4 (TRAP_unconfirm REFUTED): clear -- but UNINFORMATIVE (trap CONFIRMed, refute path never ran).
- NEW F-D1'' (CONFIRM via cross-sentence bleed): TRIGGERED by TRAP_unconfirm. Load-bearing.

## 9  NEXT PLANE (named, NOT opened)
CONCEPT temporal channel V5 (design + probe, no build): close D1'' = SAME-SENTENCE co-location for
CONFIRM (year + admissible-class event verb in one article sentence), predicate-class + header-strip
+ word-boundary retained. HARD regression guard 16 + 09 stay CONFIRM same-sentence. TRAP_unconfirm
expected CONFIRM -> ABSTAIN (then refute-restraint finally testable). Re-run the same 9.
Bars: 18 ABSTAIN, 16 + 09 CONFIRM (no regression), 03 REFUTE@Q24563361, traps not refuted,
TRAP_unconfirm reaching ABSTAIN (R15 close) or engaging+restraining refute (D4 test).
Trigger: "LABA, TEMPORAL CHANNEL V5".
Parallel Founder decision (still open): S4 held-out RE-CUT for a real G3 yield denominator.

---
*REPORT_temporal_probe_v3 - 2026-06-21 - OVERALL PASS on pre-registered bars; D1 (header/off-class)
CLOSED (18 ABSTAIN, regression guard 16+09 CONFIRM held, proven offline + live). Predicate-class
anchor replaced the report-sec5 literal "exact keyword" fix, which frozen trace falsified (would
regress 16+09). NEW same-family residual D1'' surfaced via R15 trap: CONFIRM co-location bleeds
across sentences (+-200 chars) -> TRAP_unconfirm spuriously CONFIRMed 1968 (a 2024-edition
"published" near a filmography "1968" in Solaris-novel article). CONFIRM unsound -> not an
absorb-enabler. R15 still open (trap confirmed, refute path never engaged; D4 untested). Next:
V5 = same-sentence co-location. Trigger "LABA, TEMPORAL CHANNEL V5".*
