# STRATEGY - verifier keystone + E15 symptom diagnosis (durable record)

Provenance: derived from the E15 real harvest (31 outputs, frozen bait_class_map md5
d1dbc7433d30f7034804dece2294b800). This file is the DURABLE architecture record; session packs
only reference it. Committed to git so it survives independent of any session pack.

## 0. NORTH STAR - the final construction (what every experiment is FOR)
TARGET: a disciplined AUTONOMOUS entity on a FROZEN substrate + GOLD Core + R1-R18, where epistemic
discipline is enforced EXTERNALLY (not baked into weights). Not a Q&A bot. End-state properties:
  1. Tier-independent DISCIPLINE - every emission passes an external grounded verifier
     (extract -> bind-or-demote); no fabrication survives, regardless of model tier.
  2. SELF-LEARNING - verifier selects clean self-samples -> RFT cements weights around verified
     outputs. Judge is grounded + external, never the model judging itself.
  3. INITIATIVE / background - IGR detects a knowledge gap (H_max < K) -> retrieve -> verify ->
     propose, unprompted.
  4. KNOWLEDGE TIERING - claims meeting Central Law -> GOLD; else temporary / permanent memory.
  5. Full autonomy WITHIN the R1-R18 contract.
KEYSTONE: properties 1-4 are all FUNCTIONS OF ONE grounded verifier (sec 3). Build+prove the verifier
-> the rest is incremental. Fake the judge -> a fluent hallucinating "Entity". The destination
governs which experiment is worth running; the process is instrumental, never the point.
LADDER POSITION (2026-06): reflex class (E9-E15) FALSIFIED. E16 grounded verifier = GO. E17 full-GOLD scale = NO-GO terminal (bindability-only cannot separate topical near-miss). E18 NLI claim-support layer above bind = NO-GO (B1=0.63 B2=0.786 on frozen heldout_E17): retrieve-then-entail is gameable - a false claim can be ENTAILED by a non-anchor authorized source; NLI CONTRADICTION-detection is reliable (B2_oracle=1.0) but ENTAILMENT-acceptance is fragile (recall ceiling ~0.74) AND corpus-permissive. NOT yet model-scale-terminal: NO-GO decomposes into bind-precision + premise-richness + held-out-v3 (addressable) plus a genuine recall component. E19 = contradiction-veto over top-K authorized bind + source-faithful premise enrichment + held-out v3; re-measure oracle B1 before any model-scale escalation. E19 VERDICT = NO-GO; both axes hit a MODEL-SCALE ceiling (DESTINATION-FALSIFIABILITY HIT): B2 veto FALSIFIED (no gold-safe floor closes the NN leaks - bind/retrieval cannot surface the right contradicting source for adversarial input, E17 precision wall), B1 oracle = 0.889 (residual = NLI paraphrase-recall misses on source-faithful gold = model-bound). Next lever = model scale, not another cheap gate. E20 BRANCH = B (bindability-only gate-2), Branch A model-scale deferred/conditional.
DESTINATION FALSIFIABILITY (R2/R6): if E19 fixes (bind+premise+held-out) and oracle B1 still <0.90, the cheap-Entity path is FALSE -> fabrication closure needs model scale. Honest terminal, not a reason to iterate blindly.
GATE-2 ACCEPTANCE (precision = gate, recall = reported yield): self-learning is rejection-sampling RFT, which is PRECISION-bound, not recall-bound. A passed fabrication contaminates weights (cardinal R7 / E15); a discarded clean sample only costs yield, and self-generated yield is cheap. Therefore accept-PRECISION (false-accept rate) is the safety gate; recall (B1) is reported yield, NOT a pass/fail bar. The B1>=0.90 recall bar is a bindability-era carry and does not govern self-learning safety.

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

E22/E24 (no-train frozen probes, bart-large-mnli, SAME E20-B gate): the gate-2 reject organ is
BIND-CORPUS-CONTENT-BOUND - not scale-bound, not architectural. Monotone false-accept drop with
premise enrichment at iso-recall (B2=0.90): E21 topicality 0.467 (move 0.0003) -> E22 entailment/
citation-string 0.333 (0.134) -> E24 entailment/37%-content 0.20 (0.267). Lever independent
(rho 0.13-0.20, falsifier live, baseline reproduced byte-exact). Architectural wall would plateau;
movement accelerated with content. Residual: T pinned ~0, gain is spoof-rejection (gold entailment
barely lifts) -> full-content corpus MUST measure per-class entailment distribution + T lift-off.
E23 VOID-by-construction (GoldStore drops `finding`; from_finding=0 = byte-identical to E22) - caught
by the from_finding CONTENTS counter (md5/clean-run/verdict all passed, manipulation never occurred ->
verify CONTENTS, not md5). NEXT (pre-register, SAME gate): GOLD as full-content bind-corpus, frozen NLI.

## E25b readout (2026-06-10)
with_finding 27->90 / from_finding 51->109, GATE fa PLATEAUED at 0.20 (movement 0.267, byte-identical E24/E25). Content-binding NECESSARY (0.467->0.333->0.20) but INSUFFICIENT: the pure-entailment reject organ has an architectural ceiling fa~0.20 > gate 0.10. Confound: added findings lowered gold-content median entailment (sep 0.084->0.008); the gate-fa plateau (max-based) is confound-immune and is the load-bearing signal. -> PIVOT to non-pure-entailment reject primitive (contradiction-veto first, then passage-NLI / separate organs). Supersedes the earlier 'NOT architectural' line for the pure-entailment organ; content-binding remains a real, necessary gain.

## E26 readout (2026-06-10)
contradiction-veto reject primitive PASS. Same premise (authorized finding), same frozen gate; signal switched P(entailment) -> P(contradiction). fa 0.467(no-veto) -> 0.0667 at B2 0.90 (movement 0.400), B3 0.000. Trust gates green: baseline fa 0.467 reproduced, rho(contradiction,cosine) -0.237 (not a relabel of bind), from_finding 109, contradiction_idx read from card. H1 confirmed: cue-stripped+entitied spoofs are CONTRADICTED by the real finding (spoof-content contradiction p50 0.991 vs gold 0.038) even where NOT entailed. Resolves the E25b architectural ceiling: the pure-ENTAILMENT organ plateaued at fa~0.20; the reject organ is contradiction-veto, not entailment. OPEN: op-point is tight (B2 at floor, C~0.995, 1/74 gold false-veto) -> E27 robustness sweep before verifier integration.
