# WORKSHEET -- DIRTY-LEAK-11 DIAGNOSE (v269 diagnose + v270 Founder-rule, TYPE B, read-only)

- date: 2026-06-25 | HEAD at v269: fa49a30 | v270 ruling at HEAD: 43c72a6 | session: TYPE B, no build/oracle/gen/fix
- inputs (LOCAL, gitignored, NOT staged): heldout_raw/verdicts/sealed_labels_20260625.jsonl (48 each)
- scope: the 11 GT-DIRTY claims that leaked CLEAN in v268 ff re-measure (DIRTY x scope.CLEAN)
- read-only: source files not mutated (VIOLATION-A clean). ESC codes stripped for DISPLAY only.

## VERDICT (decisive, v269)
- **E = 0/11.** No claim carries a non-year numeric token. Every numeric token is a YEAR; every year routed to per_year. per_specific={} BY DESIGN, NOT extractor-miss.
- **=> the 11 leaks are NOT a number-extractor regression.** Extractor-patch track OFF.
- Leak mechanism: no channel returned REFUTE. per_year gave ABSTAIN/CONFIRM only -> harness computed scope=CLEAN (scope not a stored field; derived by ff_partition).

## R15 -- sharpen v268 hypothesis
v268 "dirty content never reached the gate" is the WEAK reading. Dirty content (years) DID reach per_year for all 11. Only the NUMBER gate (per_specific) is empty, correctly. Frame: "extractor missed numbers" -> "specifics are years; per_year did not refute."

## TAGS (E/Y/S/R) -- v269 structural + v270 Founder ruling
| id | year tok | per_year | non-yr num | dirty signal / FOUNDER RULING | TAG |
|---|---|---|---|---|---|
| held2_01_1 | 1687 | ABSTAIN | none | FOUNDER: dirty="Sir" -- Newton knighted 1705, not 1687 (anachronistic title) | S |
| held2_06_1 | 1905 | CONFIRM | none | year CONFIRMED; no Founder rationale supplied -> STAYS R | R |
| held2_07_0 | 1678 | CONFIRM | none | year CONFIRMED; no Founder rationale supplied -> STAYS R | R |
| held2_07_1 | 1678 | ABSTAIN | none | "John Hooke" vs pair 07_0 "Robert" -> name specific | S |
| held2_13_0 | 1850,1852 | ABSTAIN,CONFIRM | none | attribution "Joule" vs topic Carnot/2nd-law -> misattribution | S |
| held2_19_0 | 1912 | ABSTAIN | none | venue "Geological Society of London" vs pair 19_1 -> venue specific | S |
| held2_19_1 | 1912 | ABSTAIN | none | venue "British Association..." vs pair 19_0 -> venue specific | S |
| held2_20_1 | 1837 | ABSTAIN | none | FOUNDER: dirty="1837" -- Beagle returned Oct 1836; Galapagos visited 1835, not 1837 | Y |
| held2_21_0 | 1796 | ABSTAIN | none | year differs from pair 21_1 (1789) -> year is dirty axis | Y |
| held2_21_1 | 1789 | ABSTAIN | none | year differs from pair 21_0 (1796) -> year is dirty axis | Y |
| held2_23_1 | 1924,1927 | ABSTAIN,ABSTAIN | none | both years correct; no Founder rationale supplied -> STAYS R | R |

TALLY (v270): E=0 | Y=3 | S=5 | R=3

## v270 FOUNDER RULING (2 of 5 R-rows resolved)
- held2_01_1 -> S. dirty_token "Sir". Reason: Newton knighted 1705, not 1687; title anachronism. (R7 OK: "Sir" present in claim text, non-numeric.)
- held2_20_1 -> Y. dirty_token "1837". Reason: HMS Beagle returned Oct 1836; Galapagos visited 1835. (R7 OK: 1837 is a year token in text.)
- held2_06_1, held2_07_0, held2_23_1 -> STAY R. No rationale supplied; years CONFIRM/correct externally. NOT guessed (R7). Founder rationale still owed.
- No E asserted by Founder. E=0 holds (no non-year number named; dump confirms none in text).

## v271 ROUTING (decision input -- PARTIAL: 3 R still open)
- Extractor-patch (TYPE C): OFF. E=0, no Founder rationale named a dropped non-year number.
- S=5 (DOMINANT) -> CONCEPT scope-amendment: number-gate out of scope for title/name/venue/attribution dirt
  (01_1 title, 07_1 name, 13_0 attribution, 19_0/19_1 venue). These declared out-of-class for the number gate.
- Y=3 -> year-channel catch-rate: per_year ABSTAIN on a KNOWN-dirty year is the real catch gap
  (20_1, 21_0, 21_1). Separate falsifier on the YEAR channel, not the number gate.
- R=3 (06_1, 07_0, 23_1) -> back to Founder for per-claim rationale. BLOCKS full routing.
- HEADROOM v4 un-defer stays BEHIND the 3 remaining R. v268 PASS literal + non-discriminative; NOT auto-unblocked.

## R12 adjacent flag (not this session)
WATCH-G: ESC codes (\u001b[...K, \u001b[ND) live INSIDE stored claim text (e.g. held2_01_1 "Ne<ESC>\nNewton"). Stripped here for display; SOURCE still carries them. Next gen must strip at source -- tokenization/oracle corruption risk if raw is tokenized. Flag only.

## METHOD / REPRO (read-only over local jsonl; source not mutated)
ESC = \x1b\[[0-9;]*[A-Za-z] ; TOK = \d+(?:[.,]\d+)?(?:\s*[-/]\s*\d+(?:[.,]\d+)?)?
Per id: join raw.claim + verdicts.temporal{per_specific,per_year} + sealed_labels{founder_label,dirty_class};
strip ESC for display; TOK over cleaned text; DELTA = tokens in text absent from per_specific.
All 11: TOK = year(s) only; per_specific={}; years in per_year -> E=0 by construction.
v270: Founder rationale ingested for 2/5 R-rows (01_1 S, 20_1 Y); 3 stay R (no rationale, not guessed, R7).