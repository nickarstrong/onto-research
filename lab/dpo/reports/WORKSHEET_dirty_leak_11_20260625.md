# WORKSHEET -- DIRTY-LEAK-11 DIAGNOSE (v269, TYPE B, read-only)

- date: 2026-06-25 | HEAD at analysis: fa49a30 | session: TYPE B (Analysis), no build/oracle/gen/fix
- inputs (LOCAL, gitignored, NOT staged): heldout_raw_20260625.jsonl (48), heldout_verdicts_20260625.jsonl (48), sealed_labels_heldout_20260625.jsonl (48)
- scope: the 11 GT-DIRTY claims that leaked CLEAN in v268 ff re-measure (DIRTY x scope.CLEAN)
- read-only: source files not mutated (VIOLATION-A clean). ESC codes stripped for DISPLAY only.

## VERDICT (decisive)
- **E = 0/11.** No claim carries a non-year numeric token. Every numeric token present is a YEAR; every year routed to per_year. per_specific={} is BY DESIGN, NOT extractor-miss.
- **=> the 11 leaks are NOT a number-extractor regression.** Extractor-patch track is OFF the table.
- Leak mechanism: no channel returned REFUTE. per_year gave ABSTAIN/CONFIRM only -> harness computed scope=CLEAN. (scope is not a stored field in verdicts; null for all 11 -- derived by v268 ff_partition harness.)

## R15 -- sharpen v268 hypothesis
v268 pack stated "dirty content never reached the gate / never tokenized (per_specific={})."
Dump REFUTES the strong reading: dirty content (years) DID reach the per_year channel for all 11.
Only the NUMBER gate (per_specific) is empty, and correctly so (specifics are years).
v270 framing shifts: "extractor missed numbers" -> "specifics are years; per_year did not refute."

## TAGS (E/Y/S/R) -- structurally evidenced only; R7: R where dirty token not localizable without Founder rationale
| id | year tok | per_year | non-yr num | visible dirty signal (text+struct) | TAG |
|---|---|---|---|---|---|
| held2_01_1 | 1687 | ABSTAIN | none | none localizable; Newton/1687 consistent with topic | R |
| held2_06_1 | 1905 | CONFIRM | none | year CONFIRMED; no non-numeric anomaly | R |
| held2_07_0 | 1678 | CONFIRM | none | year CONFIRMED; "Robert Hooke" canonical | R |
| held2_07_1 | 1678 | ABSTAIN | none | "John Hooke" vs pair 07_0 "Robert" -> name specific | S |
| held2_13_0 | 1850,1852 | ABSTAIN,CONFIRM | none | attribution "Joule" vs topic Carnot/2nd-law -> misattribution | S |
| held2_19_0 | 1912 | ABSTAIN | none | venue "Geological Society of London" vs pair 19_1 -> venue specific | S |
| held2_19_1 | 1912 | ABSTAIN | none | venue "British Association..." vs pair 19_0 -> venue specific | S |
| held2_20_1 | 1837 | ABSTAIN | none | candidates: year 1837 OR finch-narrative; not isolable | R |
| held2_21_0 | 1796 | ABSTAIN | none | year differs from pair 21_1 (1789) -> year is dirty axis | Y |
| held2_21_1 | 1789 | ABSTAIN | none | year differs from pair 21_0 (1796) -> year is dirty axis | Y |
| held2_23_1 | 1924,1927 | ABSTAIN,ABSTAIN | none | candidates: years; no isolating signal | R |

TALLY: E=0 | Y=2 | S=4 | R=5

## TAG RATIONALE
- E (extractor-miss): NONE. Requires a non-year number present-in-text but absent-from-per_specific. No claim has a non-year number. Extractor dropped nothing.
- Y (year-routed): 21_0, 21_1. Intra-pair conflict (same topic, year differs 1796 vs 1789) proves the YEAR is the dirty/load-bearing specific. per_specific empty by design; leaked via per_year ABSTAIN (no refute).
- S (out-of-scope, non-numeric): 07_1 (name "John" vs pair "Robert"), 13_0 (author "Joule" vs topic concept Carnot/2nd-law), 19_0 + 19_1 (venue differs across pair). Dirty axis is a named entity/relation -> number gate never in scope -> SCOPE ruling, not extractor patch.
- R (ruling-required): 01_1, 06_1, 07_0, 20_1, 23_1. Only specifics present are years with no isolating structural signal (no intra-pair conflict, no topic-vs-claim mismatch). Which token the Founder flagged dirty cannot be evidenced from text+struct. R7: not guessed. Founder rationale required.

## v270 ROUTING (decision input)
- Extractor-patch (TYPE C): OFF. E=0.
- S=4 -> CONCEPT scope-amendment candidate: number-gate out of scope for name/venue/attribution dirt.
- Y=2 -> year-channel catch-rate question: per_year ABSTAIN on a dirty year is the real catch gap (separate from number gate).
- R=5 -> back to Founder: supply per-claim dirty-token rationale (sealed_labels carries label+class, not token). Largest bucket; blocks final routing.
- HEADROOM v4 un-defer stays BEHIND the 5 R-rulings. v268 PASS stays literal + non-discriminative; NOT auto-unblocked.

## R12 adjacent flag (not this session)
WATCH-G escape codes (\u001b[...K, \u001b[ND) live INSIDE stored claim text (e.g. "Ne<ESC>Newton"). Stripped here for display; SOURCE still carries them. If verifier tokenizes raw text, codes sit adjacent to word fragments and may corrupt tokenization/oracle lookups. Next gen must strip at source. Flag only -- read-only session.

## METHOD / REPRO (read-only dump over local jsonl; source not mutated)
ESC = \x1b\[[0-9;]*[A-Za-z] ; TOK = \d+(?:[.,]\d+)?(?:\s*[-/]\s*\d+(?:[.,]\d+)?)?
Per id: join raw.claim + verdicts.temporal{per_specific,per_year} + sealed_labels{founder_label,dirty_class};
strip ESC for display; TOK over cleaned text; DELTA = tokens present in text but absent from per_specific.
Result for all 11: TOK = year(s) only; per_specific = {}; years present in per_year. -> E=0 by construction.