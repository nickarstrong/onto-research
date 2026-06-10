# PRE_REGISTER_E27 -- contradiction-veto reject organ: full-gate + robustness sweep

STATUS: FROZEN pre-data. Authored before run_E27_probe.py executes. Bars, secondaries,
falsifier, and decision rule are committed HERE and not edited after data is seen.
Any post-hoc change voids the run (no threshold fishing; iso-recall rule fixed below).

PRIOR: E26 (report_E26.md, commit 50b3154; PRE_REGISTER_E26 ea736a5) -- contradiction-veto
reject primitive PASS, fa 0.0667 <= gate 0.10 at B2 0.90, movement 0.400, B3 0.000,
single readout. E27 tests whether that op-point is ROBUST, not a knife-edge.

---

## 0 ONE-LINE CLAIM UNDER TEST
The contradiction-veto reject organ holds false-accept fa <= 0.10 over a non-trivial band
of the veto threshold C (not only at the single E26 op-point where B2 sat exactly on the
0.90 floor), and the fa-reduction is attributable to the reject organ itself, not the
no-auth baseline or the accept/entailment path.

## 1 SUBSTRATE (frozen, byte-identical to E26 -- no new data, no edit to frozen scripts)
- fixture   : eval/_local/gold_fixture_E25b.json   md5 4a45f52883a802e8d8d1d5ff5d185bdb
              (E18 baseline + 63 authored real-provenance findings; LOCAL, gitignored)
- heldout   : heldout_E17.jsonl                     md5 7e9fe030646d5671952e7a9fe9437e37
- model     : bart-large-mnli (contradiction read from id2label; cached). NEVER sentence_transformers.
- signal    : P(contradiction) of (premise = authorized finding, hypothesis = candidate),
              SAME premise as the entailment ladder; only the read index changes (E26 learning).
- env       : ONTO_RETRIEVE_FLOOR=0.45 (E16-locked; code default 0.55 is a footgun),
              KMP_DUPLICATE_LIB_OK=TRUE, pyarrow imported line 1 before torch.
- run_E27_probe.py = NEW file, reuses run_E26 skeleton (_ce_load / ce_scores(contradiction) /
  candidates_with_cosine / precompute). Frozen substrate (verify_E16, gold_retrieve,
  semantic_retrieve, run_E26) untouched; footgun fixes folded into run_E27 ONLY.

## 2 PRIMARY GATE (frozen, identical to E26 -- the verdict rests on this, not on sep)
- fa        : false-accept = max over candidates of accept-rate on spoof/neg-control content.
              READ GATE fa (max over candidates), NOT sep (p50). sep is confounded by finding
              phrasing-quality (E25b: sep 0.084 -> 0.008 under added findings) -- diagnostic only.
- B1        : gold-content recall (accept-rate on real findings) >= 0.90.
- B2        : iso-recall point -- the LOWEST C with B2 >= 0.90 (most aggressive veto that still
              holds gold recall). Direction is fixed here BEFORE data: contradiction signal -> the
              entailment ladder used HIGHEST T; with the contradiction signal the iso-recall rule
              takes the LOWEST C. This direction is frozen and not re-chosen post-hoc.
- B3        : 0.000 expected (held-out leakage check).
- PASS bar  : fa <= 0.10 AND B1 >= 0.90 at the iso-recall op-point.

## 3 PRE-REGISTERED SECONDARIES (3, frozen pre-data)

### S1 -- per-class contradiction distribution
Formalize the E26 H1 diagnostic. Report P(contradiction) percentiles (p10/p50/p90) split by
(class x premise-kind): class in {gold-content, spoof-content, neg-control}, premise-kind in
{authorized-finding}. E26 reference points (NOT the bar, context only):
  spoof-content contradiction p50 0.991 ; gold-content p50 0.038 ; gold-content p90 0.979.
Pre-registered expectation: spoof-content p50 - gold-content p50 separation reproduces > 0.5.
This is a corroborating diagnostic; the verdict still rests on max-based fa (sec 2), not on S1.

### S2 -- C-sweep / lift-off robustness (THE primary E27 question)
Sweep the veto threshold C across a grid; report fa(C) and B2(C). Report the C-band over which
BOTH fa <= 0.10 AND B2 >= 0.90 hold simultaneously.
- Grid: C in [0.90, 0.999] stepped at 0.005, plus a fine sweep [0.990, 0.999] at 0.001 around
  the E26 op-point (C~0.9949). C=+inf included as the no-veto baseline anchor.
- ROBUSTNESS BAR (frozen): the joint (fa<=0.10 AND B2>=0.90) band must have width >= 0.01 in C
  AND contain at least 3 grid points. A band that exists at exactly one C with B2 pinned to the
  0.90 floor = knife-edge = bar NOT met.
- Reference: E26 op-point was TIGHT (B2 exactly at floor 0.90, C~0.9949, 1/74 gold-content
  falsely vetoed). E27 decides whether width exists around it.

### S3 -- reject-vs-lift demotion attribution
Decompose each item demotion (candidate that moved from accept->reject vs baseline) into:
  (a) no-auth baseline (demoted with no organ),
  (b) contradiction-veto reject organ,
  (c) accept/entailment-lift organ.
Report the share of total fa-reduction owned by (b) the reject organ specifically.
- Reference: E26 no-auth baseline B1 0.533 -> veto added to 0.933 (the veto owned the lift).
- ATTRIBUTION BAR (frozen): the reject organ (b) must own > 50% of the fa-reduction from
  baseline fa 0.467 to the op-point fa. If (a)+(c) account for the majority, the reject organ
  is not the load-bearing primitive and the result is mis-attributed.

## 4 TRUST GATES (else VOID -- checked in code, not asserted in prose)
- baseline (no-veto, C=+inf) fa reproduces 0.467, reproduced=True (model-independent anchor).
- degenerate=False : rho(contradiction, cosine) reported; |rho| stays low (E26 -0.237) ->
  veto is NOT a relabel of the bind/cosine score. Frozen guard: |rho| < 0.50.
- contradiction_idx READ from model id2label (assert exactly one "contradiction" label) --
  NOT hardcoded. Verify CONTENTS, not md5 (E23 lesson).
- from_finding asserted > 0 in code (E23 VOID-by-construction guard; E26 was 109).
- input md5 logged every run: fixture 4a45f52883a802e8d8d1d5ff5d185bdb, heldout 7e9fe030646d5671952e7a9fe9437e37.

## 5 HYPOTHESIS / FALSIFIER (R6)
- H (E27): the reject organ holds fa <= 0.10 over a C band of width >= 0.01 (>= 3 grid points,
  B2 not pinned to floor across the whole band), AND S3 attributes > 50% of fa-reduction to it.
- FALSIFIER: fa <= 0.10 holds ONLY at a single C with B2 pinned to the 0.90 floor (knife-edge),
  OR S3 attributes the majority of fa-reduction to baseline/accept-organ -> op-point not robust
  / reject organ not load-bearing -> tune (premise quality / per-class C) before any verifier
  integration. fa > 0.10 on re-run at the E26 op-point = regression -> reconcile (E26 was a
  single readout; re-run must reproduce).

## 6 DECISION RULE (pre-registered, applied after data without modification)
- fa<=0.10 over a band (S2 bar met) AND S3 attributes the gain to the reject organ (S3 bar met)
  -> reject organ ROBUST -> graduate into the verifier (verify_E16 integration; Tommy go REQUIRED
     because frozen substrate is edited) + per-class secondaries.
- fa<=0.10 only at the knife-edge (single C, B2 at floor) -> NOT robust -> tune premise quality /
  per-class C, one more readout, NO new data.
- fa>0.10 on re-run -> regression -> reconcile before anything else.

## 7 SCOPE / NON-GOALS
- No new data authored. No edit to verify_E16 / gold_retrieve / semantic_retrieve / run_E26.
- No verifier integration this session (that step needs Tommy go -- frozen substrate edit).
- sep (p50) is reported as diagnostic only; it is NOT a gate and cannot override max-based fa.
- This pre-registration is frozen on commit; report_E27 cites ONLY this file's sec 2/3/5/6.

---
md5 of this file is logged in report_E27 to prove pre-data freeze.
