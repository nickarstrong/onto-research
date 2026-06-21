# REPORT_temporal_probe_v2.md -- temporal channel V3 probe (live Wikidata/Wikipedia)

session : LABA, TEMPORAL CHANNEL V3
date    : 2026-06-21
type    : CONCEPT (design + probe, no build). Probe RUN live (Tommy-side), trace-grounded.
binds   : REPORT_temporal_probe_v1.md sec3 (D1/D2/D3 named) + sec5 (V3 design consequence) ;
          REPORT_temporal_probe_v0.md (CONFIRM viable) ;
          ARCHITECTURE_master sec2 ("flag on CLEAN = castration; false-flag <= 0.10").
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ; o0_s4_founder_labels.jsonl (v199) ; +3 clean traps.
oracle  : Wikidata wbsearchentities + EntityData (date predicates + P31) + FULL Wikipedia plaintext
          (action=query prop=extracts explaintext). Local HTTP.
probe   : o0_temporal_probe_v2.py ; trace o0_temporal_probe_v2_trace.json.
status  : PROBE DONE -- banked. OVERALL = FAIL on pre-registered bars. Decomposition:
          D2 CLOSED, D3 CLOSED, D1 NOT CLOSED (residual is a DIFFERENT mechanism than v1's D1).

## 0  ONE NUMBER
P1 = PASS (D2 closed). P2 = FAIL (D3 closed; D1 residual: 18 CONFIRM). P3 = PASS but R15-narrow.
OVERALL FAIL. Net: 2 of 3 defects closed; D1 reopened at a deeper layer (incidental-event-verb
co-location, not subject-name).

## 1  CLAIM VERDICTS (trace-grounded)
| id          | label | year | verdict | trace reason                                                       |
|-------------|-------|------|---------|--------------------------------------------------------------------|
| heldout_03  | DIRTY | 1925 | REFUTE  | D3 CLOSED. Person-name "Edwin Hubble" BLOCKED from refute; work title "A Relation..." -> Q24563361 P577=1929 != 1925. refute_anchor.qid = Q24563361 (the 1929 paper), NOT the 2011 decoy Q54281574. |
| heldout_09  | CLEAN | 1887 | CONFIRM | D2 CLOSED. "Heinrich Hertz" person-dominant fallback -> human Q123372 -> full text -> 1887 co-located with event verb. |
| heldout_14  | CLEAN | 1900 | N/A     | 1900 in abstract -> not load-bearing. Correct.                     |
| heldout_16  | CLEAN | 1847 | CONFIRM | Semmelweis Q59736 full-text co-locates 1847 + event verb. Sound (G-d held: "Hungarian"->journal P571=1857 did NOT refute, 1847-sentence licenses P575/P585 not P571). |
| heldout_18  | DIRTY | 2014 | CONFIRM | **D1 RESIDUAL (F-D1 TRIGGERED).** False CONFIRM. Anchor = substring "develop" from the SECTION HEADER "== Developments ==" within +-200 of "In 2014, Cleverbot was upgraded to use GPU" (an incidental, UNCLAIMED event). |
| TRAP_python | CLEAN | 1991 | CONFIRM | Python Q28865 P571=1991, WD predicate. Correct entity. Sound.       |
| TRAP_titanic| CLEAN | 1997 | CONFIRM | Titanic Q44578 P577=1997, WD predicate. Correct entity. Sound.      |
| TRAP_norefute|CLEAN | 1910 | CONFIRM | "Bertrand Russell" person-dominant -> full text co-locates 1910 + "publish". Not refuted (P3 holds) but via CONFIRM short-circuit -> R15-narrow (refute-restraint not exercised here). |

## 2  WHAT IS BANKED (true, trace-verified)
- B1 D2 CLOSED -- person-dominant resolution. resolve_subject() now resolves a person-name label
  via the dominant human (P31=Q5) top wbsearch hit even at ctx-overlap 0. heldout_09 reached full
  text and CONFIRMED 1887; full-text-depth was never the failure, disambiguation was (v1 F2').
- B2 D3 CLOSED -- type-gated REFUTE. A person-name label can never anchor a refute. heldout_03
  refuted on the WORK title (Q24563361, 1929 paper), and the same-label PERSON decoy
  (Q54281574, a 2011 Nature article) was correctly REJECTED as a refute anchor. This is a DIRECT
  refute-restraint demonstration on a confirmable-wrong-year same-label entity (carries the P3
  load that the trap could not -- see R15).
- B3 G-d (event-predicate match) holds under live data. heldout_16 "Hungarian"->medical journal
  (P571=1857) did NOT refute the 1847 claim: the 1847 sentence's verb ("observed") licenses
  P575/P585, not P571. Event-type gating prevented a CLEAN castration even without CONFIRM masking.

## 3  WHAT IS NOT BANKED -- D1 residual (R7, precision-dominates)
- D1 NOT CLOSED (deeper mechanism). v1->v3 D1 fix = "drop subject name from CONFIRM anchors". That
  was necessary (the v1 18-confirm anchored on the subject title "Cleverbot") but INSUFFICIENT.
  The v3 CONFIRM anchor set is "ANY EVENT_PREDICATES substring present in the article, within
  +-WINDOW of the year". heldout_18 false-confirmed because the substring "develop" appears in a
  WIKI SECTION HEADER ("== Developments ==") next to an incidental 2014 sentence. So the residual
  defect is INCIDENTAL-EVENT-VERB CO-LOCATION (incl. markup / section headers / unrelated events),
  not subject-name. A CONFIRM channel that fires on a section header is NOT an absorb-enabler.
  FIX (V4): restrict the CONFIRM co-location anchor to the CLAIM SENTENCE's event keywords (the
  verbs that licensed the year's predicate), with word-boundary matching and wiki section-header
  ("== ... ==") stripping. Re-validate heldout_16 + heldout_09 do NOT regress (both must still find
  their claim-event verb co-located with the year in full text).

## 4  R15 -- P3 "PASS" IS STILL NARROW on the trap (but carried by 03)
TRAP_norefute CONFIRMED (Russell full text, 1910) -> it passed P3 via the CONFIRM short-circuit, NOT
via refute-restraint. The v1 R15 gap (no CLEAN same-label trap with NO confirmable year) is NOT yet
closed by the trap. HOWEVER refute-restraint is now demonstrated directly by heldout_03: the channel
saw a same-label entity (the 2011 Nature article) carrying a confirmable WRONG year and refused to
anchor on it. The remaining open item is a trap whose CORRECT year is unconfirmable AND whose decoy
is confirmable-wrong, to force ABSTAIN-not-CONFIRM (a famous-subject trap keeps confirming the
correct year). Carry to V4.

## 5  DESIGN CONSEQUENCE (for V4, NOT built this session)
- CONFIRM: anchor on the CLAIM-SENTENCE event keyword(s) only (not any article verb); word-boundary;
  strip "== header ==" markup before scanning. Re-test 18 -> expect ABSTAIN; re-validate 16 + 09
  still CONFIRM (regression guard is now a HARD bar, since claim-kw tightening was the risk we
  deferred in v3).
- REFUTE: unchanged (D3 closed). Keep person-name block + event-predicate match.
- DISAMBIGUATION: unchanged (D2 closed). Keep person-dominant fallback.
- PROBE: add a CLEAN same-label trap with NO confirmable correct year (still-open R15 falsifier).

## 6  GATE ROLE (precision-first, unchanged priority)
- CONFIRM: NOT shippable as an absorb-enabler while D1 is open (false-confirms a DIRTY claim).
- REFUTE: anchor-correct now (D3 closed), but stays ADVISORY until the no-confirmable-year trap
  passes REFUTE-restraint (R15). 03 decoy-rejection is supporting, not sufficient, evidence.

## 7  DENOMINATOR (R15, unchanged)
S4-frozen G3>=0.20 stays dead (max 0.150; CONFIRM would add heldout_16 -> 2/20 = 0.100 < 0.20). Real
G3 yield = Founder-owned held-out RE-CUT, not this channel's gate.

## 8  FALSIFIER STATUS
- F-D1 (18 CONFIRM): TRIGGERED -- load-bearing. Mechanism = section-header "develop" co-location.
- F-D2 (09 ABSTAIN on full text): clear (09 CONFIRMED).
- F-D3 (03 anchor != 1929, or a trap REFUTED): clear (03 anchor = Q24563361; no trap refuted).

## 9  NEXT PLANE (named, NOT opened)
CONCEPT temporal channel V4 (design + probe, no build): close D1 residual = CONFIRM anchored on the
CLAIM-SENTENCE event keyword(s), word-boundary, "== header ==" stripped; HARD regression guard
16 + 09 stay CONFIRM; add a CLEAN same-label NO-confirmable-year trap (R15). Re-run the same 8.
Bars: 18 ABSTAIN, 16 + 09 CONFIRM (no regression), 03 REFUTE@1929 (hold), traps not refuted incl.
the no-confirm trap reaching ABSTAIN.
Trigger: "LABA, TEMPORAL CHANNEL V4".
Parallel Founder decision (still open): S4 held-out RE-CUT for a real G3 yield denominator.

---
*REPORT_temporal_probe_v2 - 2026-06-21 - OVERALL FAIL, decomposed: D2 CLOSED (09 CONFIRM via
person-dominant resolve), D3 CLOSED (03 REFUTE anchored on the 1929 paper Q24563361, person decoy
rejected; no trap refuted). D1 NOT CLOSED -- reopened at a deeper layer: CONFIRM still fires on an
incidental article event-verb, here the substring "develop" from a wiki SECTION HEADER
"== Developments ==" co-located with the incidental "2014 GPU upgrade" sentence (18 false-CONFIRM).
P3 narrow (trap via CONFIRM) but refute-restraint carried by 03 decoy-rejection. Next: V4 = claim-
sentence-kw CONFIRM anchor + header stripping + regression guard 16/09 + no-confirm trap. Trigger
"LABA, TEMPORAL CHANNEL V4".*
