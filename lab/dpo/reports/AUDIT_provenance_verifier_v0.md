# AUDIT -- Source Provenance Verifier (DOI layer) v0

date      : 2026-06-11
auditor   : ONTO build (R1-R18 applied to the spec's own claims; Fixture C run for real)
target    : SPEC_provenance_verifier_v0.md  md5 d9c33937eb1b2fe6f30977f2514e00af  (audited byte-state; pin)
plane     : SURFACE / architecture review
home      : onto-research/reports  (dateable priority + reproducibility of the audit)
status    : AUDIT v0 CLOSED. 6 findings (4 defects + 2 minor). Facts L1-clean. Current operating ceiling = T1 (D3).
method    : Fixture C (sec8 of the spec) applied literally -- every load-bearing marker the spec emits run through
            L1 (existence/metadata) against the primary source before the spec is graded. A verifier whose own
            markers its own gate would not catch is not a verifier. This audit is that gate, run once, by hand.

--------------------------------------------------------------------------------
## 1 FIXTURE C WORKSHEET (frozen) -- the spec's own markers vs primary source

Each row: the spec's claim -> what L1/L2 must return -> what the primary source actually returns (source, date)
-> verdict. This is the enumerated oracle the spec's sec8-FixtureC lacked (D4). Freeze; regenerate on spec edit.

| # | spec claim                                  | expected         | actual (source, date)                                              | verdict |
|---|---------------------------------------------|------------------|--------------------------------------------------------------------|---------|
| 1 | Verfaillie real DOI = 10.1038/nature00870   | L1 pass          | Nature 418:41-49 (2002), title matches (nature.com/PubMed 12077603)| PASS    |
| 2 | ...retracted 2024, 22y, ~4500 cites         | L2 retracted     | Retracted 2024-06; most-cited retracted paper, ~4500 WoS cites (Retraction Watch 2024-06-18) | PASS |
| 3 | cheetah real DOI = 10.1073/pnas.0810435106  | L1 pass          | PNAS 106(2):512-515 (2009) (pnas.org)                              | PASS    |
| 4 | ...clean ~3y, Deng 2011 forgery, Mazak ack  | L2 retracted     | Retracted 2012-08-20 (~3y); Deng 2011 forgery, Mazak 2012 ack (Retraction Watch 2012-08-20; researchgate 271842876) | PASS |
| 5 | Crossref ~180M records                      | number holds     | "nearly 180 million records", 2025 public data file (crossref.org 2025-03)| PASS |
| 6 | Retraction Watch ~50-60K, ~0.03% of corpus  | number holds     | 61,645 records (RW DB, 2025-03); 61.6K/180M = 0.034%               | PASS*   |
| 7 | DataCite ~100M records                      | number holds     | NOT independently confirmed this pass                              | UNVERIFIED |

  * row 6: spec's "50-60K" is stale-LOW; current = 61,645 (Mar 2025). Magnitude + 0.03% fraction correct. See D5.
  Fixtures A/B fixture DOIs (nature00807, pnas.0811124106) are DELIBERATELY-WRONG test inputs -- consistent with
  the spec's stated expectations (T4 on mismatch/non-resolve); not audited as factual claims.

RESULT: every load-bearing factual marker the spec emits is L1/L2-clean except DataCite (row 7, unverified) and the
stale RW count (row 6). The spec passes its own Fixture C on facts. The defects below are ARCHITECTURAL, not factual.

--------------------------------------------------------------------------------
## 2 FINDINGS

### D1 -- L2 hides a COVERAGE failure mode, not only LAG  [defect, sourced]
The spec frames L2 (sec2) as deterministic with a single honest ceiling: retraction LAG. But retraction indexing
is inconsistent ACROSS registries: a 4-source study found only ~3% of retracted publications consistently indexed
across Crossref / RWD / Scopus / WoS; counts diverge -- RWD 39,301 vs Crossref 14,745 (Taylor & Francis,
10.1080/08989621.2025.2484555, 2025). So if L2 queries only Crossmark, it misses the MAJORITY of known retractions.
FIX: L2 must (a) name the concrete registry it queries, (b) own index-coverage gap as a SEPARATE ceiling beside lag.
FALSIFIER (add to sec8): feed a DOI retracted in RWD but absent from Crossmark; if L2 returns clean, the gap is real.

### D2 -- T0 has no AXIS-G floor -> back-door axis collapse  [defect]
sec1 states G cannot LIFT a failed P. Correct. But sec3 defines T0 = L1+L2+L4+L5 with NO minimum AXIS G. A clean-DOI
preprint that happens to corroborate (L5) formally reaches T0 = "GOLD, load-bearing" on provenance + corroboration
alone, with grade still preprint. That is the axis-collapse sec1 forbids, re-entering from the tier side.
FIX: state an explicit G-floor on T0 (T0 requires AXIS G >= grade-X, e.g. >= observational/peer-reviewed). Below it,
cap at T1/T2 regardless of corroboration.

### D3 -- L5 independence not operationalized -> T0 is currently UNREACHABLE  [defect, R2/R6]
T0 REQUIRES L5 corroboration. sec2-L5's central predicate is source INDEPENDENCE (provenance- and method-independent,
discounting citation). sec9 step3 itself admits "Define independence operationally" is still TODO. Therefore the T0
predicate has no test today -> T0 cannot be awarded -> the CURRENT OPERATING CEILING IS T1. This must be stated as
the system's present state, not left implicit. (Honest: the spec flags the TODO; the consequence -- ceiling = T1 --
is the part to make explicit.)

### D4 -- Fixture C declared without an oracle -> VOID-by-construction (E23 lesson)  [defect]
sec8 Fixture C is a slogan: "run the gate on this spec's own marked claims." Unlike Fixture A, it enumerates NO
claim -> expected-verdict rows. Un-runnable as written: it would pass md5 and fire on nothing (exactly the lab E23
near-miss: clean verdict, manipulation never fired). Section 1 of THIS audit is the missing worksheet, run once.
FIX: paste sec1 worksheet into the spec as Fixture C's frozen oracle; regenerate on every spec edit (md5-gated).

### D5 -- RW count stale-low + ungrounded  [minor, R1/R4]
sec6 "RW ~50-60K" -> current 61,645 (RW DB, Mar 2025). 0.03% fraction is correct. The figure carries no source/date
in the spec (its own R4). FIX: update to ~61.6K, attach source + date.

### D6 -- "verified" claimed over an unverified number  [minor, R7]
sec6 prints "corpus reality (verified)" over BOTH Crossref AND DataCite. This audit confirmed Crossref (~180M) only;
DataCite (~100M) was not independently checked this pass. FIX: drop "verified" from DataCite or mark "unverified",
until a primary check lands.

--------------------------------------------------------------------------------
## 3 LOAD-BEARING-CORRECT (do not touch)
- GATE-BEFORE-MODEL (sec4): L1/L2 deterministic before L4 inference -> model cannot rescue a fake. VOID-by-construction.
- ASYMMETRY T4 < T3 (sec3): fabricated marker ranked BELOW missing marker. Manufactured authority is the worse failure.
- OVER-PRUNING SPLIT (sec5): historical-basis (grade, not re-gate) vs incoming-digital (full L1-L5). Anti-castration.
These mirror lab lessons + Central Law (flag insufficiency, never assert false). Correct; keep verbatim.

--------------------------------------------------------------------------------
## 4 RESULT
Facts: L1-clean (sec1; 6/7 PASS, 1 UNVERIFIED, 0 FAIL). Architecture: 4 defects + 2 minor.
Operating ceiling TODAY = T1 (D3): T0 cannot be awarded until L5 independence is operationally defined (sec9 step3).

--------------------------------------------------------------------------------
## 5 RECOMMENDATION (one)
Before any sec9 build code: freeze sec1 worksheet into the spec as Fixture C's oracle (closes D4, already computed,
zero cost). THEN sec9 step1 (L1/L2 adapter on Fixture A) with the D1 fix folded in (L2 names its registry + owns the
coverage gap). Build order unchanged; the un-runnable test closes first. D2/D3/D5/D6 are spec-edits, fold at next spec rev.

AUDIT v0 -- CLOSED.
