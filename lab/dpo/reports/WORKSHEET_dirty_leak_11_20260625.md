# WORKSHEET -- DIRTY-LEAK-11 DIAGNOSE (v269 diagnose + v270/v271 Founder-rule, TYPE B, read-only)

- date: 2026-06-25 | HEAD at v269: fa49a30 | v270 ruling: 43c72a6 -> 2656240 | v271 ruling: 06_1/07_0/23_1 -> CLEAN | session: TYPE B, no build/oracle/gen/fix
- inputs (LOCAL, gitignored, NOT staged): heldout_raw/verdicts/sealed_labels_20260625.jsonl (48 each)
- scope: the 11 GT-DIRTY claims that leaked CLEAN in v268 ff re-measure (DIRTY x scope.CLEAN)
- read-only: source files not mutated (VIOLATION-A clean). ESC codes stripped for DISPLAY only.

## VERDICT (decisive, v269)
- **E = 0/11.** No claim carries a non-year numeric token. Every numeric token is a YEAR; every year routed to per_year. per_specific={} BY DESIGN, NOT extractor-miss.
- **=> the 11 leaks are NOT a number-extractor regression.** Extractor-patch track OFF.
- Leak mechanism: no channel returned REFUTE. per_year gave ABSTAIN/CONFIRM only -> harness computed scope=CLEAN (scope not a stored field; derived by ff_partition).

## R15 -- sharpen v268 hypothesis
v268 "dirty content never reached the gate" is the WEAK reading. Dirty content (years) DID reach per_year for all 11. Only the NUMBER gate (per_specific) is empty, correctly. Frame: "extractor missed numbers" -> "specifics are years; per_year did not refute."

## TAGS (E/Y/S/CLEAN/R) -- v269 structural + v270/v271 Founder ruling
| id | year tok | per_year | non-yr num | dirty signal / FOUNDER RULING | TAG |
|---|---|---|---|---|---|
| held2_01_1 | 1687 | ABSTAIN | none | FOUNDER: dirty="Sir" -- Newton knighted 1705, not 1687 (anachronistic title) | S |
| held2_06_1 | 1905 | CONFIRM | none | FOUNDER: CLEAN -- raw=claim, 1905/Einstein/photoelectric all correct; no injected dirt. GT mislabel. | CLEAN |
| held2_07_0 | 1678 | CONFIRM | none | FOUNDER: CLEAN -- 1678/Hooke/F=kx all correct; no injected dirt. GT mislabel. (raw carries ESC, see WATCH-G) | CLEAN |
| held2_07_1 | 1678 | ABSTAIN | none | "John Hooke" vs pair 07_0 "Robert" -> name specific | S |
| held2_13_0 | 1850,1852 | ABSTAIN,CONFIRM | none | attribution "Joule" vs topic Carnot/2nd-law -> misattribution | S |
| held2_19_0 | 1912 | ABSTAIN | none | venue "Geological Society of London" vs pair 19_1 -> venue specific | S |
| held2_19_1 | 1912 | ABSTAIN | none | venue "British Association..." vs pair 19_0 -> venue specific | S |
| held2_20_1 | 1837 | ABSTAIN | none | FOUNDER: dirty="1837" -- Beagle returned Oct 1836; Galapagos visited 1835, not 1837 | Y |
| held2_21_0 | 1796 | ABSTAIN | none | year differs from pair 21_1 (1789) -> year is dirty axis | Y |
| held2_21_1 | 1789 | ABSTAIN | none | year differs from pair 21_0 (1796) -> year is dirty axis | Y |
| held2_23_1 | 1924,1927 | ABSTAIN,ABSTAIN | none | FOUNDER: CLEAN -- 1924/1927/de Broglie/Davisson-Germer all correct; no injected dirt. GT mislabel. (raw carries ESC, see WATCH-G) | CLEAN |

TALLY (v271 FINAL): E=0 | Y=3 | S=5 | CLEAN=3 | R=0 -- leak-set 11 -> 8 (3 CLEAN removed)

## v270 FOUNDER RULING (2 of 5 R-rows resolved)
- held2_01_1 -> S. dirty_token "Sir". Reason: Newton knighted 1705, not 1687; title anachronism. (R7 OK: "Sir" present in claim text, non-numeric.)
- held2_20_1 -> Y. dirty_token "1837". Reason: HMS Beagle returned Oct 1836; Galapagos visited 1835. (R7 OK: 1837 is a year token in text.)
- held2_06_1, held2_07_0, held2_23_1 -> STAYED R (no rationale supplied at v270; years CONFIRM/correct). NOT guessed (R7).
- No E asserted by Founder. E=0 holds (no non-year number named; dump confirms none in text).

## v271 FOUNDER RULING (final 3 R-rows -> CLEAN) -- leak-set CLOSED
- held2_06_1 -> CLEAN. dirty_token empty. Reason: raw == claim, 1905/Einstein/photoelectric correct; no injected specific. GT (DIRTY/specifics) wrong.
- held2_07_0 -> CLEAN. dirty_token empty. Reason: 1678/Hooke/F=kx correct; no injected specific. GT (DIRTY/specifics) wrong. raw carries ESC codes (WATCH-G).
- held2_23_1 -> CLEAN. dirty_token empty. Reason: 1924/1927/de Broglie/Davisson-Germer correct; no injected specific. GT (DIRTY/specifics) wrong. raw carries ESC codes (WATCH-G).
- **R7 / 3.9 lead-to-verify:** an alternate rationale variant asserted raw contained "June 30" (06_1), "John Pell" (07_0), "December 22" (23_1). regex/grep over heldout_raw_20260625.jsonl: NONE present. Variant REJECTED, not recorded. Only the dump-verified CLEAN ruling entered.
- **GT label correction OWED (BINDING):** sealed_labels marks 06_1/07_0/23_1 founder_label=DIRTY, dirty_class=specifics -- the specific was never materialized into the generated claim. This is a gen/labeling defect (the dirty_class is asserted but no dirty token exists in text), adjacent to WATCH-G. Correct sealed_labels (DIRTY->CLEAN x3) at next gen/label pass; until then these 3 are out of the leak denominator.

## v271 ROUTING (FINAL -- R=0, leak-11 routing CLOSED)
- **R = 0.** No un-flagged R remains. Leak-set resolved: E0 / Y3 / S5 / CLEAN3. Routing UNBLOCKED.
- Extractor-patch (TYPE C): **OFF.** E=0; no Founder rationale named a dropped non-year number; dump confirms none in text.
- S=5 -> **v272 CONCEPT scope-amendment:** number-gate out of scope for title/name/venue/attribution dirt
  (01_1 title, 07_1 name, 13_0 attribution, 19_0/19_1 venue). Declared out-of-class for the number gate.
  Decide separately whether an entity/relation gate is in roadmap or explicitly deferred.
- Y=3 -> **v272 year-channel catch-rate:** per_year ABSTAIN on a KNOWN-dirty year is the real catch gap
  (20_1, 21_0, 21_1). Hermetic offline year falsifier (KNOWN-dirty year MUST be refuted, not abstained). Separate re-measure.
- CLEAN=3 -> **removed from leak set; GT label correction owed** (06_1, 07_0, 23_1). Not a verifier miss -- claims are genuinely clean, verifier correctly returned non-REFUTE.
- HEADROOM v4 un-defer: now HONEST -- all 11 resolved (E-fixed:0 / S-out:5 / Y-routed:3 / CLEAN:3). Becomes clean at R=0. v268 PASS remains literal + non-discriminative; un-defer is a separate decision, not auto-fired here.

## R12 adjacent flag (not this session)
WATCH-G (UPGRADED): ESC codes (\u001b[...K, \u001b[ND) live INSIDE stored claim text -- confirmed in held2_01_1 ("Ne<ESC>\nNewton"), held2_07_0, held2_23_1 (raw dump v271). Stripped here for display; SOURCE still carries them. Next gen must strip at source -- tokenization/oracle corruption risk if raw is tokenized. Flag only.

## METHOD / REPRO (read-only over local jsonl; source not mutated)
ESC = \x1b\[[0-9;]*[A-Za-z] ; TOK = \d+(?:[.,]\d+)?(?:\s*[-/]\s*\d+(?:[.,]\d+)?)?
Per id: join raw.claim + verdicts.temporal{per_specific,per_year} + sealed_labels{founder_label,dirty_class};
strip ESC for display; TOK over cleaned text; DELTA = tokens in text absent from per_specific.
All 11: TOK = year(s) only; per_specific={}; years in per_year -> E=0 by construction.
v270: Founder rationale ingested for 2/5 R-rows (01_1 S, 20_1 Y); 3 stayed R (no rationale, not guessed, R7).
v271: final 3 R-rows ruled CLEAN by Founder, dump-verified against raw (no injected specific; alternate "specific present" variant grep-rejected, 3.9). leak-set 11 -> 8. R=0. Routing CLOSED.
