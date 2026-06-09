# report_E18_nli - NLI claim-support layer above frozen E16 bind

VERDICT: **NO-GO** (frozen bars, heldout_E17.jsonl n=75; adjudicated gold=27, NN-swap=14;
3 anchors nulled R4; fab=15 + negctrl=15 = bind-stage control).

| bar | metric | result | target | |
|-----|--------|--------|--------|--|
| B1 | gold VERIFY (with-finding) | 17/27 = 0.630 | >= 0.90 | FAIL |
| B2 | NN-swap DEMOTE             | 11/14 = 0.786 | >= 0.80 | FAIL |
| B3 | fab+neg over-bind          | 0/30 = 0.000  | <= 0.10 | PASS |

Model cross-encoder/nli-deberta-v3-small, CPU. tau=0.50. Retrieval floor 0.55. Gate =
max(P(finding,claim), P(finding,proposition)) i.e. NLI of the bound source finding against
the claim and its provenance-stripped proposition.

## Oracle vs eval - causal decomposition (diag_oracle_E18)
Oracle = premise forced to the item's OWN-anchor finding (retrieval bypassed). Isolates NLI
quality from the bind.

| | B1 gold | B2 NN |
|--|--------|-------|
| ORACLE (own-anchor premise) | 20/27 = 0.741 | 14/14 = 1.000 |
| EVAL (real retrieval bind)  | 17/27 = 0.630 | 11/14 = 0.786 |

Two distinct failures, neither a clean "bigger NLI fixes it":

1. **Retrieval mis-bind (frozen E16/E17 retrieval) breaks BOTH bars.**
   - B1: 0.741 -> 0.630. Gold binds to the wrong authorized source -> wrong premise -> demote.
   - B2: 1.000 -> 0.786. Under oracle every NN-swap contradicts its own-anchor finding (P~0).
     Under real bind, 3 NN-swaps retrieve a NON-anchor authorized source whose finding the false
     claim ENTAILS -> VERIFY (leak). A bigger NLI does not fix binding to the wrong source.

2. **Entailment-recall ceiling 0.74 even at oracle.** NLI contradiction-detection is reliable
   (B2_oracle 1.00; every near-miss caught given the right premise). Entailment of faithful
   paraphrase is fragile: deberta-v3-small under-fires when lexical/entity overlap is low. A
   provenance-frame confound ("a paper argued X" is not entailed by a bare statement of X) cost
   ~0.33 and was recovered by proposition extraction (0.41 -> 0.74); the stripper is brittle
   (per-claim structure), but the 0.74 ceiling is stable across stripper variants -> it is real,
   not an artifact. Residual oracle failures: g00 (10^1000), g02, g10 (bits) = premise omits a
   source specific the claim asserts (findings kept deliberately number-free, R7); g08, g11 =
   pre-registered spin; g22 = held-out anchor<->claim defect; g24 = stripper fragility.

3. **Held-out v2 defects (frozen, not regenerated).** g22: anchor 10.1016/j.resmic.2009.06.004
   is a primitive-MEMBRANE paper but the held-out claim asserts "minimal viable cell ~5000
   nucleotides" -> claim mis-assigned to the DOI. g08/g11: claim framed beyond source.

## Key learning (R16, novel, falsifiable) - bank this
Retrieve-then-entail does NOT close fabrication on this substrate. A plausible FALSE claim can be
ENTAILED by some authorized source that is not its topic anchor; entailment-as-acceptance is
permissive across the corpus, so stacking it ABOVE an imprecise bind can INCREASE false-accepts
(the B2 leak), not only catch the near-miss it was added for. Asymmetry surfaced: NLI
CONTRADICTION-detection is reliable (sharp, B2_oracle=1.0); NLI ENTAILMENT-acceptance is fragile
(recall) AND gameable (precision under imprecise bind).
Falsifier for E19: a CONTRADICTION-VETO (demote a bound claim if ANY top-K authorized finding
contradicts it) over a precise bind should remove the NN leak (B2->1.0 under real bind) without
harming gold. If it does not, the bind itself is the limit.

## Not terminal-for-model-scale (R2/R6)
The NO-GO decomposes into addressable parts (bind precision; premise richness; held-out v3) PLUS
a genuine model-recall component (~0.74 paraphrase entailment at oracle). Escalating verifier
model scale is justified ONLY for the recall component, and ONLY after the addressable parts are
fixed and oracle B1 is re-measured. Declaring scale-terminal now would confound bind defects and
held-out defects with model capacity.

## E19 punch-list (no generate+eval+fix in one session; this is the next session's design)
1. Contradiction-veto over top-K authorized bind: demote if any top-K finding CONTRADICTS;
   accept only on entailment with no contradiction. Target: B2 -> 1.0 under real bind.
2. Source-faithful premise enrichment: add the verified specifics the terse findings omit
   (R4 from the source, never copied from the held-out claim). Lifts oracle B1.
3. Held-out v3: fix g22 anchor; re-state g08/g11 to their source. Frozen after rebuild.
4. Re-measure oracle + eval. If oracle B1 < 0.90 after (2)(3) -> model-scale branch (recall),
   recorded as the keystone DESTINATION-FALSIFIABILITY hit. Until then: open, not terminal.

## Artifacts (git: scripts + reports + pre-register; fixture/heldout PRIVATE)
build_fixture_E18.py - additive `finding` (27; 5 search / 22 canonical; 3 nulled R4); sha256(source)
authorization frozen (asserted). nli_verify.py - wraps frozen resolve_claim; max-gate entailment.
sanity_E18.py, diag_oracle_E18.py - instrument sanity (NOT bars). PRE_REGISTER_E18.md.
gold_fixture_E18.json + heldout_E17.jsonl = LOCAL/private (eval/_local, gitignored).
