# REPORT -- S4 specifics_check_v2 targeted-rescue (BUILD + live run) -- DEFECT

session : LABA, TARGETED RETRIEVAL BUILD
date    : 2026-06-21
type    : C (build + verify) -- specifics_check_v2 + live S4 gate recompute
binds   : REPORT_S4_specifics_gate.md sec5 (yield recovery levers) ;
          pack v204 lever V3 (targeted retrieval + conjunction) ;
          CONCEPT_organism0_v1.md sec3 (gate, frozen denominators v199).
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ;
          eval/o0/o0_s4_b2_verdicts.jsonl (frozen, 5 SUPPORTS) ;
          eval/o0/o0_s4_founder_labels.jsonl (Founder v199 banked).
status  : PROBE DEFECTIVE -- re-run required before any yield conclusion.

## 0  ONE NUMBER

G1 fa_live = 0/17 = 0.000  PASS (HARD)   -- but vacuous: rescue fired 0/2.
G3 yield   = 1/20 = 0.050  unchanged vs v1 (v202). No recovery.

## 1  WHAT WAS BUILT

- o0_specifics_filter.py : specifics_check_v2(claim, abstract, retrieve_fn).
  v1 first pass; on FAIL, ONE targeted conjunction retrieval; confirm iff ALL
  in-scope unverified specifics co-occur in a SINGLE alt abstract + >=1 verified
  anchor. In-scope = years + proper nouns (article-led junk dropped); bare
  numbers incidental/non-blocking (REPORT_S4 sec5 lever1).
- o0_s4_gate_v2.py : live S4 gate recompute (Crossref+OpenAlex, no Ollama/embed).

Offline self-test (mocked binding abstracts): 09/14/16 ABSORB, 03/18 HELD,
fa_live 0.000, yield 0.150 = v204 ceiling. Logic correct under correct retrieval.

## 2  LIVE RUN (frozen data, live rescue retrieval)

| id          | Founder | absorbed | method     |
|-------------|---------|----------|------------|
| heldout_03  | DIRTY   | no       | no_rescue  | CORRECT hold (1925 not co-bound)
| heldout_18  | DIRTY   | no       | no_rescue  | CORRECT hold (Cleverbot/2014 not co-bound)
| heldout_09  | CLEAN   | no       | no_rescue  | FALSE reject -- rescue starved
| heldout_16  | CLEAN   | no       | no_rescue  | FALSE reject -- rescue starved
| heldout_14  | CLEAN   | yes      | v1_pass    | CORRECT keep

G1 fa_live = 0/17 = 0.000  -> PASS (HARD)
G3 yield   = 1/20 = 0.050  -> below 0.20 and below v204 ceiling 0.150
COMBINED = FAIL

## 3  DEFECT (root cause)

Trace (eval/o0/o0_s4_gate_v2_trace.jsonl):
- heldout_09 query "Maxwell James Clerk Maxwell 1887 Heinrich Hertz" -> n_alt=2
- heldout_16 query "Semmelweis Ignaz Semmelweis 1847 Vienna General Hospital" -> n_alt=1

The conjunction query stuffs anchors + ALL in-scope specifics into ONE API
query. Crossref/OpenAlex relevance over-constrains -> candidate pool collapses to
1-2 abstracts. The rescue cannot confirm what retrieval never returns. The
Hertz-1887 confirmation of Maxwell is among the most documented results in
physics; returning 2 candidates is a query-construction defect, NOT a coverage
limit. Secondary defect: exact-substring match on multiword specifics
("Vienna General Hospital", "Heinrich Hertz") is brittle vs abstracts that
carry only "Vienna" / "Hertz".

Consequence: the run measures rescue on a starved pool (n_alt 1-2 ~ empty
retrieval). Per ENOUGH-FOR-STAGE (ROADMAP sec0b) the measurability invariant
(non-empty data, E15) is violated. The yield number is INVALID as a test of
"is yield recoverable filter-side"; it is valid only as "v2-as-built absorbs
almost nothing, so fa_live trivially holds".

## 4  WHAT IS / IS NOT BANKED

BANKED (true):
- fa_live 0.000: v2-as-built absorbed 0 dirty (trivially -- rescue inert).
- Binding-hinge holds where rescue DID evaluate: 03 (1925) and 18
  (Cleverbot/2014) correctly not confirmed.

NOT banked (probe defective -- do NOT conclude):
- "yield unrecoverable filter-side" -- retrieval was never given a fair pool.
- "escalate Crown granularity" -- that branch is valid only if a CORRECT rescue
  still fails. Not reached.

FLAG (R15): pack v204 "V3 theoretical max 0.150 / fa_live 0.000" is a CEILING
(what yield WOULD be if retrieval surfaced the binding abstract), not an
achievable live number. Live build does not reach it; the gap is retrieval/query.

## 5  NEXT PLANE (named, not opened)

Fix retrieve-side of specifics_check_v2, then re-run S4 v2 (one number):
- query on SUBJECT only (anchors + topic keywords), NOT specifics-in-query
  (e.g. "Maxwell Hertz electromagnetic waves" ; "Semmelweis childbed fever Vienna"),
  top_k 10-15.
- conjunction-check across the broader returned pool (all in-scope co-occur in
  one abstract + >=1 anchor) -- unchanged safety semantics.
- relax token match: year exact ; proper noun by last significant token
  (surname / head noun), not full multiword exact-substring.
- re-run o0_s4_gate_v2 live -> valid yield. THEN integrate (if yield enough for
  stage at fa_live<=0.10) or escalate Crown granularity.

fa_live <= 0.10 stays HARD. Do NOT tune the gate or reopen a frozen bar.

---
*REPORT_S4_v2_targeted_DEFECT.md - 2026-06-21 - fa_live 0.000 (vacuous) / yield 0.050 / PROBE DEFECTIVE - re-run after retrieve-side fix.*
