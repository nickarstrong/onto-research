# PRE_REGISTER_E25b -- fuller-coverage content-premise separation readout

FROZEN BEFORE DATA. Authored at E25b open, before any new finding is written, so the bar and decision
cannot be tuned to the result. Supersedes nothing; extends PRE_REGISTER_E25 (same metric, same gate).

## 0 CONTEXT
E25 read out WEAK: sep = 0.0837 (gold-content p50 0.0838 vs spoof-content p50 0.0001), gold 27/34 >= T,
spoof 1/17 >= T. Directionally clean, gold p50 NOT pinned ~0 -> not the PIVOT case. But sep < 0.20 bar.
E25 content-premise coverage was sparse: gold-content n=34, spoof-content n=17; only 51/139 premises
from_finding; 27/217 records carry a real finding. E25b tests whether WEAK is a coverage artifact.

## 1 HYPOTHESIS + FALSIFIER (R6)
H : WEAK (sep < 0.20) is COVERAGE-LIMITED. Raising real-provenance finding coverage raises the gold-content
    premise n and lifts sep toward / over 0.20 at iso-recall.
FALSIFIER : at full real coverage, sep stays in (0,0.20) -> coverage was NOT the limiter -> WEAK CONFIRMED
    -> reject organ cannot separate cue-stripped+entitied spoofs by content entailment at iso-recall -> PIVOT.

## 2 METHOD (only the fixture content changes; everything else byte-frozen)
- Runner   : run_E25_probe.py (in git ca0b4ad), re-pointed at enriched fixture gold_fixture_E25b.json.
- Gate     : frozen E20-B (false-accept <= 0.10 == B1 >= 0.90). NOT touched.
- Metric   : sep = p50(gold-content entailment) - p50(spoof-content entailment).
- Model    : facebook/bart-large-mnli, P(entailment), premise=source.FINDING / hypothesis=claim.
- Env      : ONTO_RETRIEVE_FLOOR=0.45, KMP_DUPLICATE_LIB_OK=TRUE, pyarrow preload, NO sentence_transformers.
- Invariant: E18 records + manifest UNCHANGED so baseline (T=-inf, fa 0.467) reproduces. New findings enter
             via the side-map only. gold_fixture_E25b.json LOCAL-only, gitignored, never public.

## 3 COVERAGE TARGET + PROVENANCE RULE (R4 / R7 -- HARD)
- Raise gold-content premise n from 34 toward full gold class. MINIMUM for a valid fuller-coverage readout:
  gold-content n >= 60 (else readout is INSUFFICIENT-COVERAGE, not WEAK-CONFIRMED).
- Every authored finding MUST come from a REAL primary source (real author/year; DOI where it exists; no
  DOI -> source confidence capped 0.5 per R4). Unverifiable -> "no source found", record EXCLUDED from the
  finding-set. ZERO fabricated findings (R7 cardinal, no exceptions). A fabricated finding to hit n>=60
  voids the entire readout.
- Grounding split (R8 / 3.9): Claude grounds findings via web_search against primary sources; Tommy supplies
  record source identities (extraction) and injects the verified side-map.

## 4 TRUST GATES (must hold, else VOID; do not read readout)
- [baseline T=-inf] false-accept = 0.467 reproduced = True   (E18 records/manifest intact)
- [guard] spearman(support,cosine) degenerate = False
- [premise] from_finding >> 51  (assert in run log; E23 lesson: verify CONTENTS, not md5)

## 5 DECISION (frozen bar = 0.20; do not relitigate after seeing the number)
- sep >= 0.20 AND gold-content p50 > spoof-content p50  -> CORPUS JUSTIFIED -> E26 full-content build (TOMMY GO).
- sep in (0, 0.20) AT n >= 60                           -> WEAK CONFIRMED  -> PIVOT (passage-NLI / contra-veto).
- sep in (0, 0.20) AT n < 60                            -> INSUFFICIENT-COVERAGE -> raise coverage, re-read.
- sep <= 0  OR  gold-content p50 ~0                     -> PIVOT passage-NLI / contradiction-veto.

## 6 ANTI-FISH
Bar 0.20 frozen pre-data. iso-recall T rule (highest T with B2>=0.90; peek only recall). NEVER post-hoc
fish a lower-recall T to clear the bar. Stale "FAIL_PARTIAL -> architectural" boilerplate in the runner is
superseded by the keystone (content-bound, not architectural) -- fold-fix into the script, never read it.
