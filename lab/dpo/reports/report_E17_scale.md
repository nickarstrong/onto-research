# REPORT E17 - full-GOLD scale check  ::  VERDICT NO-GO (terminal)

Date: 2026-06-09. Pre-registered bars (PRE_REGISTER_E17.md, frozen before run):
B1 spoof-demotion >= 0.90 | B2 gold-VERIFY >= 0.80 | B3 over-demotion <= 0.10.
No post-hoc floor tuning (R6). verify_E16.py / gold_retrieve.py / semantic_retrieve.py byte-identical to E16 GO build.

## What was tested
E16's grounded verifier (GO on a 61-record slice) run UNCHANGED against the FULL GOLD
bind-corpus: gold_fixture_full.json = 216 authorized records (60 carried byte-identical
from E16 + 156 new structured-DOI, dedup by DOI; 1 adversarial decoy). Held-out
heldout_E17.jsonl = 75 items: gold_backed 30 (VERIFY) / spoof_cuestripped_entitied 30
(15 fabricated-citation + 15 NN-swap topical near-miss) / negctrl_common 15.
gold + spoof grounded on 30 real anchor DOIs (faithful reworded findings vs false
over-claims), no title/claim_key verbatim (confound removed; see Run history).

## Result: NO viable floor (instrument-sanity terminal, before eval)
Floor sweep over 0.40-0.65 - over-bind never reaches 0 while VERIFY recall stays usable.
Computed bar frontier (over-bind = spoof retrieving an authorized hit):

  floor | B2 gold-VERIFY | B1 spoof-demote | verdict
  0.45  | 28/30 = 0.93   | 16/30 = 0.53    | B1 FAIL
  0.50  | 25/30 = 0.83   | 19/30 = 0.63    | B1 FAIL
  0.55  | 22/30 = 0.73   | 23/30 = 0.77    | both FAIL
  0.60  | 13/30 = 0.43   | 28/30 = 0.93    | B2 FAIL
  0.65  |  8/30 = 0.27   | 29/30 = 0.97    | B2 FAIL

B2 >= 0.80 holds ONLY at floor <= 0.50; B1 >= 0.90 holds ONLY at floor >= 0.60.
No floor satisfies both -> NO-GO. (B3 inert: negctrl is gate-protected -> PASS-COMMON,
not demoted, regardless of raw-retrieve over-bind.)

## Attribution (terminal, not tuning, not density, not artifact)
- DENSITY CONTROL [d]: over-bind size-invariant (216 -> 1, 60 -> 1 at floor 0.65).
  NOT corpus density; the spoof binds its own topical target at any corpus size.
- SEPARATION [c]: DEMOTE top-1 cosine max = 0.855 EXCEEDS VERIFY median = 0.595.
  Distributions overlap; no cosine floor separates faithful gold from near-miss spoof.
- DECOMPOSITION: fabricated-citation spoofs (E16-comparable class) demote cleanly by
  floor 0.45 (ho_sf* clear). The failure is localized to NN-swap topical near-miss
  (ho_sn*): a FALSE over-claim on a real source's topic.
- ROOT CAUSE: bindability-only verifier, NLI/entailment not built (verify_E16 sec 2.4).
  A faithful paraphrase of a gold finding and a false over-claim on the same topic are
  equidistant from the source embedding (claim_key+source). Example ho_sn14: "propensity
  score removes all confounding with no assumptions" (false) binds the real Rosenbaum-
  Rubin record at cosine 0.855; the verifier cannot distinguish it from the faithful
  "propensity score plays a central role" because it checks topical bindability, not
  claim support.

## Meaning (keystone destination-falsifiability, pack sec 4 NO-GO branch)
Grounded verification by bindability ALONE does NOT close fabrication when the fabrication
is a topical near-miss of a real source. The cheap-Entity (bindability-only) path is FALSE
on this substrate. Fabrication closure requires an entailment / claim-support layer
(NLI as PRIMARY, not secondary) - i.e. model scale, per the pre-registered NO-GO branch.
This is a clean terminal result, recorded, not iterated by loosening the floor.

## What this does NOT say
- Not a regression of E16: fabricated-citation rejection and gold VERIFY both hold in
  their own ranges; B2 reaches 0.93 at floor 0.45.
- Not a density failure: [d] size-invariant.
- Not a held-out artifact: v1 verbatim-claim_key confound was removed (over-bind 5 -> 1
  at floor 0.65 from v1 to v2); the residual survives clean construction.

## Run history (reproducibility)
- v1 held-out: gold restated TITLE near-verbatim (KS p=0.000, B2 inflated), NN-spoof reused
  claim_key verbatim (trivial over-bind, 5 surviving at 0.65). Confound flagged by sanity
  [c]/[e], NOT carried into the verdict.
- v2 held-out: gold = reworded finding, NN-spoof = natural false over-claim; no verbatim
  title/claim_key (validated against frozen verify_E16 gate). KS D=0.271 p=0.033.
- Verdict drawn from v2 (confound-free).

## Next (gate 2 redesign, not gate 2 as planned)
Pack NEXT+1 self-learning loop assumed E17 GO. It does NOT fire. The verifier needs a
claim-support / entailment check ABOVE bindability before it can be a rejection-sampling
selector (else it would stamp topical near-miss fabrications as VERIFIED-clean). Next
experiment = add NLI-primary verification, re-run the SAME E17 held-out as the falsifier.
