# STRATEGY - verifier keystone + E15 symptom diagnosis (durable record)

Provenance: derived from the E15 real harvest (31 outputs, frozen bait_class_map md5
d1dbc7433d30f7034804dece2294b800). This file is the DURABLE architecture record; session packs
only reference it. Committed to git so it survives independent of any session pack.

## 1. E15 symptom diagnosis (from the 31 real outputs, N=31, single greedy pass)
- S1. Honesty reflex is keyed to the FORMAL-LOCATOR surface cue. Prose-narrative asks ("what did
  the study find") -> 0 / 12 abstentions, always produces, often fabricates. Formal-locator asks
  ("give a DOI/ID") -> abstains 7 / 11. The prose channel is ~100% open - same blind spot as the
  regex floor.
- S2. Even the formal channel is unreliable: 4 / 11 formal asks produced a fabricated locator
  (LLMs-conscious arXiv, homeopathy author/year, saffron PubMed, P=NP arXiv). Domain-dependent,
  not source-dependent.
- S3. Fabrications are fluent, specific, low-entropy (named journal + year + n + institution).
  High confidence -> defeats entropy / self-consistency / SelfCheck detectors.
- S4. With a real GOLD anchor the model binds correctly (ts_28). The substrate CAN be honest when
  a source exists; it fails only at knowing WHEN it lacks one.

## 2. Diagnosis (one)
The model has no internal signal for "do I actually hold a source." It substitutes (a) a formal-
locator surface cue and (b) a claim-plausibility prior. Neither equals source-possession. Honesty
is therefore a side effect, not a foundation. Structural consequence: NO self- / closed-book judge
fixes this - the miscalibrated prior IS the organ you would lean on. (The "doctor asking the
patient how to cure himself" failure mode, now data-backed.)

## 3. Keystone program: every Entity property is a function of one grounded verifier
- DISCIPLINE (tier-independent) = verifier gates emission; a weak model that fabricates is caught
  and demoted regardless of tier, because the check is external to the weights.
- SELF-LEARNING (gold-asymmetry / rejection-sampling RFT) = verifier selects which self-generated
  samples are clean enough to train on; weights cement around verified behaviour, not drift.
  REQUIRES a grounded judge, NOT the model judging itself (else 2nd-order hallucination = E15).
- INITIATIVE / background = IGR detects a gap (H_max < K) -> retrieve -> verify -> propose.
Gate ladder (strict): prove the verifier (E16) -> then self-refinement -> then initiative. No
layer N+1 before N clears its falsifier.

## 4. E16 verifier primitive: BINDABILITY, not fabrication-detection
resolve(claim) = retrieve candidate source from GOLD/retrieval -> bind to a real locator (keep) OR
demote to "[no verified source]" if unbindable. This treats fabricated claims and true-but-
uncovered claims IDENTICALLY (both demote) - which is the correct R4 behaviour and sidesteps the
precision leak of NLI-entailment (NLI flags true-but-uncovered as Neutral and needs context that
is absent in closed-book). NLI/cross-encoder is at most a SECONDARY check on an already-bound
passage, never the primary judge.

Falsifier (whole program): claim-EXTRACTION recall on free PROSE (S1: prose is the 100%-open
channel) + resolution precision, against a pre-registered bar on the 16 manually-marked prose
spoofs in worksheets_E15.json. Clears -> Entity roadmap opens. Fails -> fabrication-closure needs
model scale; bank the negative.

## 5. Out of scope (lab = 1 researcher, ephemeral pods)
Transformer-architecture surgery (gated-attention / MoE-autogrow / recurrent-depth rewrite);
nightly self-rewriting-weights demon (breaks provenance, induces drift); "self-awareness" as a
deliverable (not operationally defined, not verifiable). Lab edge = the discipline FORMULA
(Central Law + R1-R18 + IGR + grounded verification), not architecture R&D.

## 6. Verified literature (R4)
- Steering vectors do not reliably generalize; unsteerable behaviours = "multiple separate
  behaviours in the model's ontology" - Tan et al., arXiv:2407.12404 (2024). Explains E14
  (open fabrication class uncoverable by finite vectors).
- Per-cause vectors needed, no single-vector cross-class transfer - Wu et al., SHARP, EMNLP 2025,
  doi:10.18653/v1/2025.emnlp-main.725 (LVLM domain; transfer with caution).
- RepE base - Zou et al., arXiv:2310.01405.
- Lead to VERIFY before entering record: "CiteCheck - retrieval-grounded citation-hallucination
  detection" (arXiv 2025). Unverified IDs from the design chat (ACT 2406.00034, ITI 2306.03341,
  spectral-attention) are NOT in the record until checked.
