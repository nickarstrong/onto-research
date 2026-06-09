# PRE_REGISTER_E25 - content-premise separation readout (no-train, no new data)

date: 2026-06-10
plane: RESEARCH
type: B (analysis readout; no generation, no new data, no fix)
substrate: frozen (verify_E16 / gold_retrieve / semantic_retrieve byte-identical; bart-large-mnli frozen)
gate: SAME E20-B gate, frozen (false-accept <= 0.10 at iso-recall, B2 >= 0.90). NOT re-opened.

## 0 Why (carried from E22/E24, in git 7e83522)
Gate-2 reject organ is bind-corpus-content-bound, not scale-bound and not architectural. False-accept
drops monotonically as the NLI premise is enriched, at iso-recall:
  E21 topicality/relevance       false-accept 0.467  (movement 0.0003)
  E22 entailment, citation-string 0.333             (movement 0.134)
  E24 entailment, 37%-content     0.20              (movement 0.267)
Lever independent (rho 0.13-0.20), falsifier live, baseline reproduced byte-exact (B1 0.533 / B2 0.933
/ fa 0.467 at T=-inf). Open residual: at E24 the threshold T is still pinned ~0 and the 0.467->0.20
gain may be spoof-REJECTION only (gold-content entailment may also sit low). Building a full-content
bind-corpus is expensive; this readout decides whether it is justified BEFORE that spend.

## 1 Hypothesis (falsifiable)
H: on the 51 content-premise pairs already scored in E24, GOLD-content entailment separates from
   SPOOF-content entailment (gold mass clearly above spoof mass).
   - H true  -> the content lever lifts gold, not only sinks spoof -> full-content corpus will move
     false-accept toward the gate -> JUSTIFIED to build E26 (author content + run SAME gate).
   - H false -> gold-content entailment is also pinned ~0; the E24 gain was spoof-rejection only ->
     a pure-entailment gate over a content corpus will keep T near zero -> corpus ALONE insufficient
     -> PIVOT to a passage-level / contradiction-veto reject primitive (E19 revisited at content scale).

## 2 Method (exact)
run_E25_probe.py = E24 with an additive diagnostics block. SAME fixture (gold_fixture_E18.json,
md5 493b8ada955edd89c0f169609a121887), SAME held-out (heldout_E17.jsonl, md5 7e9fe030646d5671952e7a9fe9437e37),
SAME model (facebook/bart-large-mnli), SAME content side-map (raw-fixture source->finding). Verdict
logic byte-stable from E24; the readout is additive and changes no metric.
Emits: per-(item-class, premise-kind) entailment distribution (n, mean, p10/p50/p90); content-premise
gold vs spoof at chosen_T; gold-vs-spoof content p50 separation.

## 3 Pre-registered readout bars (no post-hoc fishing)
- TRUST (must hold, else VOID): baseline T=-inf reproduces E20-B (fa 0.467); degenerate=False (rho<0.95);
  from_finding > 0 (content actually reached scorer).
- READOUT METRIC: sep = p50(gold-content entailment) - p50(spoof-content entailment).
- DECISION:
    sep >= 0.20 AND gold-content p50 > spoof-content p50  -> CORPUS JUSTIFIED (build E26).
    sep in (0, 0.20)                                       -> WEAK; one more readout at fuller coverage before commit.
    sep <= 0 OR gold-content p50 ~0                         -> PIVOT (passage-NLI / contradiction-veto); corpus alone insufficient.
  Bars fixed here BEFORE the run. The gate (fa<=0.10) is unchanged and is NOT the readout target.

## 4 What this does NOT do
No new corpus, no fixture mutation, no threshold re-fishing, no model swap. It is the cheapest
discriminator on data already on disk, gating the expensive full-content build either way.

## 5 NEXT+1 (conditional, not pre-committed)
- CORPUS JUSTIFIED -> E26: author full-content bind-corpus for the eval cluster with REAL provenance
  (R4/R7; no fabricated findings - where no real finding sources, leave + log), as a NEW content fixture
  (E18 records+manifest unchanged so baseline still reproduces). Run SAME gate + the 3 secondary readouts.
- PIVOT -> design a non-pure-entailment reject primitive (passage-level NLI or contradiction-veto at
  content scale); separate pre-register.
