# REPORT — S4 specifics-coverage gate (BUILD + re-run)

session : LABA SPECIFICS FILTER BUILD
date    : 2026-06-21
type    : C (build) — integrate specifics_check post-B2 + re-run S4 gate
binds   : CONCEPT_organism0_v1.md sec 3 (validation gate, frozen) ;
          pack v201 sec2 S4 (v199 GATE FAIL, banked).
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ;
          eval/o0/o0_s4_b2_verdicts.jsonl (frozen, 5 SUPPORTS) ;
          eval/o0/o0_s4_founder_labels.jsonl (Founder v199 banked labels).

## 0  ONE NUMBER

G1 fa_live = 0/17 = 0.000  -> PASS  (was 2/17 = 0.118 FAIL at v199)

## 1  WHAT WAS BUILT

- o0_specifics_filter.py : specifics_check(claim, abstract) lifted to production module.
- o0_accumulator.py      : specifics gate wired into integrate_verdicts(). After
  B2=SUPPORTS, run specifics_check; unverified specifics -> downgrade ABSORB->REJECT
  (reason: unverified_specifics). Flag self.specifics_gate, default ON (safety-first).
- o0_s4_gate.py          : reproducible gate recompute (no model calls, no retrieval).

Smoke: live integrate path verified — clean claim ABSORB, fabricated (Cleverbot/2014)
REJECT.

## 2  S4 RE-RUN (deterministic, frozen data)

| id          | Founder | filter | absorbed | driver of FAIL |
|-------------|---------|--------|----------|----------------|
| heldout_03  | DIRTY   | FAIL   | no       | year 1925 (fabricated) — CORRECT catch |
| heldout_18  | DIRTY   | FAIL   | no       | Cleverbot / 33 (fabricated) — CORRECT catch |
| heldout_09  | CLEAN   | FAIL   | no       | 1887 / Heinrich Hertz absent from abstract — FALSE reject |
| heldout_16  | CLEAN   | FAIL   | no       | 1847 / Vienna / 30 absent from abstract — FALSE reject |
| heldout_14  | CLEAN   | PASS   | yes      | all specifics present — CORRECT keep |

Gate (pre-registered, frozen denominators v199):
- G1 fa_live = 0/17 = 0.000  (<= 0.10) -> PASS
- G3 yield   = 1/20 = 0.050  (>= 0.20) -> FAIL  (was 0.250)
- COMBINED (G1 AND G3) = FAIL

## 3  FINDING

The specifics gate closes the partial-fabrication hole that failed S4 v199:
both DIRTY claims (wrong date, wrong name) are now caught, fa_live -> 0.000.

It does so by conflating "specific absent from the retrieved abstract" with
"specific unverified". On CLEAN claims this over-rejects: heldout_09 (Hertz, 1887)
and heldout_16 (1847, Vienna, mortality numbers) carry CORRECT specifics that the
topic-level abstract simply does not mention. Result: CLEAN precision 1/3, yield
collapses 0.250 -> 0.050, G3 FAIL.

The v200 "VIABLE under precision-first" label does NOT survive the pre-registered
G3 bar. Under the frozen gate the combined result is FAIL, driven entirely by yield,
not by fabrication.

R6 falsifier status: RFT-through-Crown remains FALSIFIED at claim granularity
(unchanged). The specifics gate fixes G1 but the yield cost makes it unusable as a
drop-in without a precision pass.

## 4  WHY DEFAULT ON ANYWAY

ONTO priority: safety (no fabrication absorbed) > capability (yield). fa_live=0.000
is the safety bar (R6 falsifier guard); yield=0.05 is a supply problem fixable by
retrieval coverage or filter precision. The gate ships ON so the autonomous loop
never absorbs a partial fabrication. The G3 cost is documented and named as the next
plane — NOT opened this session (STOP rule: one number, frozen=frozen).

## 5  NEXT PLANE (named, not opened)

Recover yield without reopening the fabrication hole. Two non-exclusive levers:
- filter precision: restrict specifics to fabrication-class tokens (named entities +
  dates that are the load-bearing claim subject), drop incidental numbers / secondary
  names / sentence-fragment proper-noun junk ("The Doppler", "Subsequent").
- retrieval coverage: pull full-text or multiple abstracts so correct specifics are
  present to verify against (current single topic-level abstract under-covers).

Decision after that probe: integrate (if yield recovers >= 0.20 at fa_live <= 0.10)
or escalate Crown granularity.

---
*REPORT_S4_specifics_gate.md · 2026-06-21 · G1 PASS (0.000) / G3 FAIL (0.050) / combined FAIL.*
