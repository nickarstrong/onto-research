# E16 verified inputs (R4) - Q1/Q2/Q3/Q4 audit, fabricated numbers stripped

Source: external-agent answers to 4 questions, each run through web_search verification. ONLY
verified facts are in-record. Every agent-supplied percentage was UNCONFIRMED in primary sources
and is EXCLUDED. Durable home for the verified design inputs; the session pack only references this.

## Q1 - prose claim extraction (de-risks the E16 extraction probe)
VERIFIED:
- No off-the-shelf extractor targets LOCATOR-BINDABILITY; all target semantic atomic facts.
- FActScore (Min et al. 2023, arXiv:2305.14251): biography-optimized; does NOT resolve pronouns;
  extracts everything (no verifiable/unverifiable split). Wrong target.
- SAFE (Wei et al. 2024): reuses FActScore's prompt; its relevance-check unexpectedly DROPS
  verifiable claims; only validated on biography data.
- VeriScore (Song/Kim/Iyyer, UMass; arXiv:2406.19276, EMNLP Findings 2024): best-structured base.
  Extracts ONLY verifiable claims, handles mixed verifiable/unverifiable content, sliding-window
  decontextualization (resolves referents), runs on open-weight LLMs. Reports F1@K (precision/recall
  vs median claim count K). Human-eval: extracted claims "more sensible" than FActScore/SAFE.
- VeriFastScore (Rajendhran et al., arXiv:2505.16973, May 2025): single-pass extract+verify; cheap
  probe option.
STRIPPED (unverified): "FActScore 85-88% / SAFE 91-94% / VeriScore 93-95% recall" - not in sources.
IMPLICATION: base the E16 extractor on VeriScore-style decontextualization, but RECONFIGURE the
target from generic atomic facts to [subject + claim + locator/source] triples; force any sentence
carrying a locator token (committee, protocol, journal, year, n=, doi, page) into its own isolated
claim. Off-the-shelf prompt as-is under-extracts on prose -> a probe failure could be the wrong
target, not a real wall. The probe must use the reconfigured target.

## Q2 - over-demotion / coverage (negctrl killer; applies at RESOLVE/build, not the extraction probe)
VERIFIED:
- ALCE (Gao et al., EMNLP 2023): citation recall (sentences entailed by cited passages) + citation
  precision, scored by NLI model TRUE (T5-11B).
- Over-penalization is REAL and documented: arXiv:2410.11217 finds ALCE metrics "excessively
  penalize responses that don't require citations," and REDEFINES the metric to EXCLUDE
  no-citation-needed statements. = the common-knowledge penalty, confirmed.
- 7B binds poorly: LLaMA-2-7B citation recall ~17 on ASQA (vs 70B ~44, ChatGPT ~73). Binding is hard
  at this scale.
STRIPPED (unverified): "30-50% true claims demoted", "ASQA 22-35%", "May 2026: 75% -> 40-50% drop".
IMPLICATION (build stage): the bindability resolver MUST carry a common-knowledge gate - bind only
claims with named-entity (ORG/DATE) or locator tokens; pass pure-reasoning / common-knowledge as
PASS-COMMON. Without it bindability produces universal "[no verified source]" = over-refusal
regression on negctrl. This mirrors real SOTA practice (2410.11217), not a guess.

## Q3 - closed-book confident-fabrication (confirms the keystone)
VERIFIED (consistent with our S3 and Tan et al. 2407.12404): no reliable closed-book method separates
confident fabrication from real knowledge. Entropy / self-consistency collapse to ~0 on confident
(low-entropy) fabrication; an honesty-probe ("Internal State Knows When Lying", Azaria & Mitchell)
does not hold at 7B. => retrieval-grounded verification is MANDATORY; no closed-book shortcut. Agent's
"layer-24 attractor" mechanism = unverified, NOT in-record; the conclusion stands on its own.

## Q4 - self-refinement failure modes (gate-2, FORWARD; do not build until E16 passes)
QUALITATIVE (taxonomy real; all agent numbers stripped):
- Diversity collapse / model collapse ("curse of recursion", Shumailov et al., Nature 2024): RFT on
  self-samples narrows to a few judge-approved templates. Mitigate: dedup (Levenshtein / n-gram)
  before the LoRA step.
- Reward hacking / verifier gaming: a BYTE-MATCH bindability judge is GAMEABLE - the model learns to
  spray valid locator tokens (decorative citation) to pass. Design constraint: link-density cap +
  atomic 1-claim-1-locator rule, never pure byte-match as the RFT reward.
- Drift: CoT can carry a hidden logical error the fact/locator judge misses. Mitigate: secondary
  CoT-consistency check before crystallizing weights.
STRIPPED (unverified): "40-60% variance collapse in 2-3 iters", "composite < 3.0 by iter 4".
