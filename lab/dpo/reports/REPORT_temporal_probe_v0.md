# REPORT_temporal_probe_v0.md -- temporal channel CONCEPT probe (live Wikidata/Wikipedia)

session : LABA, TEMPORAL CHANNEL CONCEPT
date    : 2026-06-21
type    : C (probe + verify) -- out-of-band year verification, 5 frozen S4 SUPPORTS
binds   : CONCEPT_temporal_channel_v1.md sec7 (pre-registered bars) ;
          pack v207 (claim-granularity year-coverage "STRUCTURAL ceiling") ;
          ARCHITECTURE_master sec2 ("flag on CLEAN = castration; false-flag <= 0.10").
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ; o0_s4_founder_labels.jsonl (banked v199).
oracle  : Wikidata wbsearchentities + EntityData date predicates (P577/P571/P575/P585/P580)
          + Wikipedia REST summary text. No Crossref/Ollama/embed. Local HTTP.
status  : PROBE DONE -- result banked. OVERALL = PARTIAL (pre-registered outcome).

## 0  ONE NUMBER
P1 (HARD) heldout_03 REFUTE = PASS ; P2 = FAIL (09 ABSTAIN, 16 CONFIRM) -> OVERALL PARTIAL.
But trace shows the REFUTE MECHANISM is unsafe (F3 live) -> REFUTE not shippable as-gate.

## 1  CLAIM VERDICTS (trace-grounded)
| id         | label | year(s)   | temporal | reason (from trace)                                   |
|------------|-------|-----------|----------|-------------------------------------------------------|
| heldout_03 | DIRTY | 1925      | REFUTE   | quoted paper Q24563361 P577=1929 (REAL date) != 1925. SOUND anchor. |
| heldout_09 | CLEAN | 1887      | ABSTAIN  | 1887 absent from Hertz REST *summary* lead; not in WD predicates. FIXABLE (article body). |
| heldout_14 | CLEAN | 1900      | N/A      | 1900 already in abstract (covered) -> not load-bearing. Matches v1_pass. |
| heldout_16 | CLEAN | 1847      | CONFIRM  | Semmelweis Wikipedia summary co-locates 1847. SOUND. Breaks v207 ceiling. |
| heldout_18 | DIRTY | 1950,2014 | REFUTE   | 1950 covered; 2014 linked to "Alan Turing" -> book Q34308373 P577=1983 != 2014. WRONG-REASON refute (F3). |

## 2  WHAT IS BANKED (true, trace-verified)
- B1 CONFIRM PATH VIABLE. heldout_16 (1847 Semmelweis): Wikidata date predicates empty,
  but the entity's own Wikipedia article text co-locates the event-year. This is the
  reliable out-of-band CONFIRM oracle for historical event-years -- the exact fact-class
  abstracts cannot carry. v207's "heldout_16 STRUCTURAL ceiling, never confirmed at claim
  granularity" is BROKEN by out-of-band verification. Concept core proven for this subclass.
- B2 REFUTE OUTCOME-CORRECT ON 03, MECHANISM SOUND THERE. The claim's actual subject (the
  named paper) resolved to its true P577=1929; 1925 != 1929 -> REFUTE on a real anchor.
- B3 14 covered-detection correct (1900 in abstract -> temporal n/a).

## 3  WHAT IS NOT BANKED -- the defect (R7 / precision-dominates)
- D1 REFUTE MECHANISM UNSAFE AS WRITTEN (falsifier F3 LIVE). Rule = "REFUTE if ANY structured
  year != claim_year on ANY same-label candidate". Trace proves it misfires:
  - heldout_18: year 2014 linked to "Alan Turing" (Cleverbot is single-word, not captured) ->
    an unrelated 1983 book-about-Turing -> spurious REFUTE. The year was never linked to its
    real subject (Goostman/Cleverbot event).
  - heldout_03: junk title-fragments injected 1988/2000 into REFUTE_YEARS alongside the
    correct 1929.
  Consequence: a CLEAN claim whose subject shares a label with any dated work would be
  FALSE-REFUTED = castration. REFUTE is NOT safe to ship as the gate until anchored.
- D2 P1 "PASS" is outcome-only. 03 happened to have a sound anchor; the rule that passed it
  is the same rule that spuriously refuted 18. Do NOT read P1 PASS as "safety holds".

## 4  DESIGN CONSEQUENCE (for CONCEPT v2, not built this session)
- CONFIRM gate: ship as designed -- Wikipedia article text (full, not just summary) as the
  primary CONFIRM oracle; Wikidata predicates as secondary. (Fixes 09 too: query article
  body, where 1887/Hertz lives.)
- REFUTE gate: REQUIRES entity-anchoring before it is safe:
  (a) link the year to the entity that is its grammatical/semantic subject in the claim,
      not any capitalized token (single-word entities like "Cleverbot" must be captured);
  (b) REFUTE only when THAT anchored entity, on a date-of-the-claimed-event relation, carries
      a confirmed different year -- never on an incidental same-label dated work.
  Until (a)+(b): REFUTE stays advisory/logged, NOT an absorb-blocking gate. fa_live safety in
  production still rests on name/place binding (which independently rejects 03 and 18 upstream).

## 5  DENOMINATOR (unchanged, R15 flag from CONCEPT sec6 stands)
S4-frozen G3>=0.20 remains denominator-dead (max 0.150; 5/20 SUPPORTS, 2 DIRTY). Temporal
CONFIRM recovers heldout_16 -> combined S4 absorb = 14 + 16 = 2/20 = 0.100, still < ceiling.
The S4 yield demonstration is a held-out RE-CUT plane (Founder-owned), not this channel's gate.

## 6  NEXT PLANE (named, NOT opened)
CONCEPT v2 temporal channel: (1) CONFIRM via full Wikipedia article text (closes 09);
(2) REFUTE entity-anchoring per sec4 (closes F3 before any gate role); (3) capture single-word
named entities in subject extraction. Pre-register a probe that includes a CLEAN same-label
trap (a clean claim whose subject shares a name with a dated work) to falsify F3-fix.
Trigger: "LABA, TEMPORAL CHANNEL V2".
Parallel Founder decision: S4 held-out re-cut for a real G3 yield denominator (sec5).

## 7  FALSIFIER STATUS (from CONCEPT sec8)
- F1 (REFUTE cannot catch wrong years): NOT triggered -- 03 refuted on a real anchor.
- F2 (oracle abstains on event-years): PARTIAL -- 16 confirmed (Wikipedia text), 09 abstained
  on summary-depth only (fixable, not structural).
- F3 (entity-link injects wrong kb_year -> false refute): TRIGGERED LIVE (18, 03 noise).
  This is the load-bearing finding. REFUTE-as-gate blocked on F3-fix.

---
*REPORT_temporal_probe_v0 - 2026-06-21 - CONFIRM viable (16 breaks v207 ceiling via Wikipedia text); REFUTE outcome-correct on 03 but mechanism unsafe (F3 live on 18). REFUTE not shippable as gate until entity-anchored. 09 ABSTAIN fixable (article body). OVERALL PARTIAL.*
