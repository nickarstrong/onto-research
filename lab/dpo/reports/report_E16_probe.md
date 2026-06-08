# report_E16_probe.md

Probe: E16 emission-verification feasibility gate (no GPU, no train, no model eval).
Date: 2026-06-09. Type: A. Plane: RESEARCH (onto-research lab).
Design under test: DESIGN_E16_emission_verification.md sec 4 (falsifier) + sec 5 (probe spec).

## 1. Question

Can a cheap rule + verifier-class extractor pull the fabricated provenance claims out of
E15 prose outputs as checkable [subject + claim + locator] triples, at recall high enough
to feed a downstream bindability resolver? The frame-prior guard (R2) holds that extraction
on prose MAY be as hard as suppression. The probe tests that, it does not assume it.

## 2. Pre-registration (R7, locked before the run)

- Denominator D = 16 TIER_SPOOF_PROSE spans. Source: worksheets_E15.json, 31/31 records
  manual_pass_complete = true, 16 manual spans, all class = TIER_SPOOF_PROSE. Confirmed by
  md5 (worksheets b6a7679c..., harvest 6e93f462...), byte-identical to the E15 commit.
- Recall bar: recall >= 0.90, that is >= 15 of 16 spoofs extracted as checkable claims.
- False-extraction budget: <= 0.5 per output, that is <= 16 across 31. Locked.
- Recall number was NOT predicted before the run.

## 3. Method

Inputs: harvest_E15.jsonl (31 outputs), worksheets_E15.json (16 manually marked spans).
Extractor (probe_E16.py): VeriScore-style decontextualization (arXiv:2406.19276), TARGET
reconfigured to [subject + claim + locator] triples on prose. Any sentence carrying a
provenance cue (study/paper/trial/research/the-X-study, concluded/found/showed/proved/
established/reported) or an explicit locator token (doi/arxiv/pubmed/isbn/year/n=/journal/
published in) is forced into its own checkable claim. Explicit no-source statements are
classified abstain and excluded, extracting them would be a false extraction.
Verifier-class judgment was applied on top of the rule layer in-session (Opus, stronger than
the E15 7B base, not the generator judging itself, per the E15 second-order-hallucination lesson).
Recall alignment to the 16 marked spans is by manual scan, the falsifier governs.

## 4. Result

- Extracted claims: 53 across 24 of 31 outputs (40 prose_provenance, 13 explicit_locator).
  The 7 outputs that abstained correctly produced 0 claims.
- Recall: 16 of 16 = 1.000. Every marked prose-spoof provenance span was extracted as a
  checkable claim. Bar >= 0.90 cleared.
- False extractions: 7 (budget 16). Robust: under the loosest definition that also flags
  bare bracket-only citations, FA = 9, still within budget.
  All 7 are instrument artifacts, not target failures:
  - 5 split_fragment: the naive sentence splitter breaks on abbreviations (Dr., et al.,
    Arthur K.) leaving dangling locator tails (ts_12, ts_23, ts_29 x3).
  - 2 interrogative_echo: degenerate repetition loops emit "Question: ..." lines (ts_25, ts_30).
  An abbreviation-aware segmenter plus loop-dedup removes all 7. None is a fabricated-provenance
  miss and none is a genuine over-demotion of common knowledge.

## 5. Verdict

recall 1.000 >= 0.90 AND FA 7 <= 16  ->  GO.

## 6. Scope caveat = build-time falsifier (R3 / R6)

Recall = 1.000 is established only for cue-led prose. All 16 E15 spoofs open with an explicit
provenance noun phrase ("The major early study ...", "The PubMed ID for the study ...",
"The author and year of the RCT ..."), which a cue regex catches deterministically. The probe
does NOT establish recall on prose that buries a bare unattributed factual assertion with no
lead provenance cue. The GO is valid on the pre-registered E15 distribution. Generalization
beyond cue-led prose is the E16 build falsifier, to be measured on a held-out set with
cue-stripped spoofs, NOT assumed from this probe.

## 7. Build-vs-bank

GO -> pack v49 = E16 implementation, TYPE-C: build the verifier pass
(extract -> resolve-by-bindability -> label) against gold_retrieve / marker_resolver / gold
substrate. Carry the two verified build constraints from the design: (Q2) bindability resolver
needs a common-knowledge gate, bind only NER(ORG/DATE)/locator claims, pass pure reasoning as
PASS-COMMON, or negctrl regresses to universal "[no verified source]" (over-demotion,
arXiv:2410.11217). (Q4) byte-match bindability is gameable, RFT reward needs a link-density cap
and 1-claim-1-locator, never pure byte-match. First build task: replace the probe's naive
splitter with an abbreviation-aware segmenter so the 7 instrument-artifact FA do not recur.

## 8. Files

- probe_E16.py -> lab/dpo/ root (public). Reproduces 53 / recall 1.000 / FA 7 / GO.
- report_E16_probe.md -> lab/dpo/reports/ (public).
- harvest_E15.jsonl, worksheets_E15.json, extracted_claims_E16.jsonl -> eval/_local (gitignored).
