# REPORT_temporal_probe_v1.md -- temporal channel V2 probe (live Wikidata/Wikipedia)

session : LABA, TEMPORAL CHANNEL V2
date    : 2026-06-21
type    : CONCEPT (design + probe). Probe RUN live (Tommy-side), trace-grounded.
binds   : CONCEPT_temporal_channel_v2.md sec3 (pre-registered bars) ;
          REPORT_temporal_probe_v0.md (F3 live, CONFIRM viable) ;
          ARCHITECTURE_master sec2 ("flag on CLEAN = castration; false-flag <= 0.10").
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ; o0_s4_founder_labels.jsonl (v199) ; +2 clean traps.
oracle  : Wikidata wbsearchentities + EntityData date predicates + FULL Wikipedia plaintext
          (action=query prop=extracts explaintext). Local HTTP.
probe   : o0_temporal_probe_v1.py ; trace o0_temporal_probe_v1_trace.json.
status  : PROBE DONE -- banked. OVERALL = FAIL on pre-registered bars, BUT see decomposition:
          concept core re-affirmed, 3 SEPARABLE FIXABLE defects block promotion (none structural).

## 0  ONE NUMBER
P3 (F3-fix on traps) = PASS but NARROW (R15); P1 = FAIL (09); P2 = FAIL (18). OVERALL FAIL.
Real result = the trace: CONFIRM concept sound (16), three mechanism defects (D1/D2/D3), all fixable.

## 1  CLAIM VERDICTS (trace-grounded)
| id         | label | year | verdict | trace reason                                                        |
|------------|-------|------|---------|---------------------------------------------------------------------|
| heldout_03 | DIRTY | 1925 | REFUTE  | OUTCOME-correct. Anchor recorded = WRONG entity ("Edwin Hubble" -> Q54281574, a 2011 Nature article, P577=2011). Real paper Q24563361 P577=1929 also fired (2nd). D3. |
| heldout_09 | CLEAN | 1887 | ABSTAIN | "Heinrich Hertz" resolve -> None (ctx-overlap 0). Full text NEVER fetched. Not a depth fail. D2. |
| heldout_14 | CLEAN | 1900 | N/A     | 1900 covered in abstract -> not load-bearing. Correct.              |
| heldout_16 | CLEAN | 1847 | CONFIRM | Semmelweis Q59736 full-text co-locates "In 1847, he proposed hand washing". SOUND. Concept core. |
| heldout_18 | DIRTY | 2014 | CONFIRM | FALSE CONFIRM. 2014 co-located with SUBJECT NAME ("In 2014, Cleverbot was upgraded to use GPU"), an incidental year, NOT the claimed Turing-test event. D1. |
| TRAP_python| CLEAN | 1991 | CONFIRM | Python Q28865 (programming language) P571=1991, WD predicate. Correct entity. SOUND. |
| TRAP_titanic| CLEAN| 1997 | CONFIRM | Titanic Q44578 ("1997 film by James Cameron") P577=1997, WD predicate. Correct entity. SOUND. |

## 2  WHAT IS BANKED (true, trace-verified)
- B1 CONCEPT CORE RE-AFFIRMED. heldout_16 CONFIRM via FULL Wikipedia article text (event-year that
  abstracts cannot carry). Breaks v207 claim-granularity ceiling, now twice-shown.
- B2 DISAMBIGUATION WORKS WHEN THE WD DESCRIPTION OVERLAPS CLAIM CONTEXT. Both traps resolved to the
  CORRECT same-label entity (Python language, 1997 Titanic film) and confirmed on WD predicates --
  the right-entity pick short-circuited any same-label decoy. This is the genuine F3-fix win, but
  it is conditional on the correct year being confirmable (see R15 narrowness below).
- B3 EVENT-TYPE PREDICATE MATCHING PREVENTS ONE F3 CLASS. heldout_16 "Hungarian" -> a medical journal
  with P571=1857; because the sentence event verb licensed P575/P585 (not P571), 1857 could NOT
  refute. Event-type gating held here.

## 3  WHAT IS NOT BANKED -- three separable defects (R7, precision-dominates)
- D1  CONFIRM FALSE-POSITIVE (safety-relevant). confirm_in_text() admits the SUBJECT NAME as a
      co-location anchor. So any year mentioned near the entity confirms -- even an unrelated event.
      heldout_18: "In 2014, Cleverbot was upgraded to use GPU" (a real but UNCLAIMED event) confirmed
      the claim's fabricated 2014 Turing-test pass. A CONFIRM channel that fires on incidental
      subject-name+year co-occurrence is NOT safe as an absorb-enabler.
      FIX: co-location anchor = EVENT-TYPE keywords ONLY (drop subject_title). -> 18 becomes ABSTAIN
      (correct: temporal cannot confirm the claimed event-year -> defers to upstream name-binding).
- D2  DISAMBIGUATION ABSTAINS ON PERSON SUBJECTS. resolve_subject() requires positive overlap between
      the WD description and claim tokens. "Heinrich Hertz" -> WD desc "German physicist" shares 0
      tokens with the claim -> ABSTAIN before full text is ever fetched. The 09 full-text fix was
      never reached; F2' is a DISAMBIGUATION failure, not a text-depth failure.
      FIX: entity-type-aware resolution (accept a confident type match -- e.g. instance-of human for a
      person-subject) + fallback to top wbsearch hit when overlap ties at 0 on a single dominant hit.
- D3  REFUTE ANCHORS ON A WRONG SAME-LABEL ENTITY (residual F3). heldout_03 refuted OUTCOME-correctly
      but the RECORDED anchor was "Edwin Hubble" -> Q54281574 (a 2011 Nature article), not the real
      1929 paper. ctx-overlap confidently picked a dated work for a person's name. F3 is REDUCED (the
      CONFIRM short-circuit protects CLEAN claims whose correct year IS confirmable) but NOT closed:
      a CLEAN claim whose correct year is NOT confirmable + subject name matching a dated work would
      still false-refute.
      FIX: require the refute anchor's ENTITY TYPE to match the claim's subject role (publication-event
      -> the entity must be the work the claim is about; person-subject -> human, which carries no
      publication date -> no refute). Type-match before refute.

## 4  R15 -- P3 "PASS" IS NARROW (mirrors v0 "P1 outcome-only")
Traps were not refuted ONLY because the correct entity CONFIRMED first (CONFIRM globally beats REFUTE).
This does NOT prove REFUTE-restraint for the load-bearing case: a CLEAN same-label claim whose correct
year is NOT confirmable (the exact 09 / 16 class). The probe lacked a CLEAN same-label trap with NO
confirmable year. v3 probe MUST add one (R6 falsifier gap).

## 5  DESIGN CONSEQUENCE (for v3, NOT built this session)
- CONFIRM: anchor on event-type keywords only (close D1). Re-test 18 -> expect ABSTAIN.
- DISAMBIGUATION: entity-type-aware + single-dominant-hit fallback (close D2). Re-test 09 -> expect
  CONFIRM via Hertz full text (1887 + "radio waves"/"demonstrated").
- REFUTE: type-matched anchor (close D3). Re-test 03 -> expect REFUTE anchored on the 1929 paper,
  not the 2011 Nature article.
- PROBE: add a CLEAN same-label trap with NO confirmable year (forces the REFUTE-restraint test).
- GATE ROLE unchanged: CONFIRM absorb-enabling once D1 closed; REFUTE advisory until D3 closed AND the
  no-confirmable-year trap passes.

## 6  DENOMINATOR (R15, unchanged)
S4-frozen G3>=0.20 stays dead (max 0.150; CONFIRM adds heldout_16 -> 2/20 = 0.100 < 0.20). Real G3
yield = Founder-owned held-out RE-CUT, not this channel's gate. Channel gate = fa_live-safety + CONFIRM
recovery, not G3.

## 7  FALSIFIER STATUS
- F3' (clean trap refuted): NOT triggered on the traps -- but only via CONFIRM short-circuit (sec4).
  D3 shows the underlying refute-anchor is still mis-resolvable. F3 reduced, not cleared.
- F2' (09 abstain on full text): TRIGGERED, but root cause is D2 (disambiguation), not text depth.
- F4 (18 anchor wrong on a DIRTY): NOT the failure mode seen; 18 instead FALSE-CONFIRMED (D1).
- NEW F5 (CONFIRM fires on incidental subject-name year): TRIGGERED (D1) -- load-bearing safety finding.

## 8  NEXT PLANE (named, NOT opened)
CONCEPT temporal channel V3 (design + probe, no build): close D1 (event-anchor-only CONFIRM),
D2 (type-aware resolution), D3 (type-matched REFUTE anchor); add a CLEAN same-label NO-confirmable-year
trap. Re-run the same 7 + new trap. Bars: 09 CONFIRM, 18 ABSTAIN, 03 REFUTE-on-1929-paper, traps not
refuted incl. the no-confirm trap.
Trigger: "LABA, TEMPORAL CHANNEL V3".
Parallel Founder decision (still open): S4 held-out RE-CUT for a real G3 yield denominator.

---
*REPORT_temporal_probe_v1 - 2026-06-21 - OVERALL FAIL, but decomposed: CONCEPT core re-affirmed (16
full-text CONFIRM); 3 separable fixable defects -- D1 CONFIRM false-positive on incidental
subject-name+year (18 GPU-upgrade), D2 disambiguation abstains on person-subjects (09 never reached
full text), D3 REFUTE anchors on wrong same-label entity (03 -> 2011 Nature article, not 1929 paper).
P3 PASS is narrow (CONFIRM short-circuit, not REFUTE-restraint). REFUTE not promotable, CONFIRM not
shippable as-is. Next: V3 fixes + no-confirmable-year trap.*
