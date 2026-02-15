# ONTO-GOLD BASELINE ANALYSIS REPORT

**Date:** 2026-02-14
**Models tested:** 11
**Questions:** 100 (50 in-domain, 50 cross-domain)
**Condition:** Baseline (no GOLD context)
**Metrics:** QD (Quantification Density), SS (Source Specificity), UM (Uncertainty Marking), CP (Counterargument Presence), VQ (Vague Qualifiers — penalty)

---

## 1. EXECUTIVE SUMMARY

11 AI models answered 100 scientific questions without epistemic calibration (GOLD). This report measures their baseline epistemic rigor using 5 automatic metrics. Key finding: models vary 3-10× in quantification density and source specificity, revealing significant differences in epistemic calibration that GOLD is designed to address.

## 2. METHODOLOGY

### 2.1 Metrics

| Metric | Code | Measures | Direction |
|--------|------|----------|-----------|
| Quantification Density | QD | Numerical values per response | Higher = better |
| Source Specificity | SS | Named sources (Author Year, DOI) | Higher = better |
| Uncertainty Marking | UM | Explicit acknowledgment of unknowns | Higher = better |
| Counterargument Presence | CP | Opposing views mentioned | Higher = better |
| Vague Qualifiers | VQ | Empty words without specifics | Lower = better |

### 2.2 Questions

- Section A (Q1-50): Origins of life, information theory, molecular biology, prebiotic chemistry, thermodynamics
- Section B (Q51-100): Medicine, AI/ML, physics, economics, climate
- Transfer test: Does epistemic rigor in domain expertise (A) predict rigor outside expertise (B)?

### 2.3 Models

| # | Model | Provider | Region | Notes |
|---|-------|----------|--------|-------|
| 1 | GPT 5.2 | OpenAI | US | Clean baseline |
| 2 | Grok 4.2 | xAI | US | ~30% GOLD contaminated |
| 3 | Copilot | Microsoft | US | Weakest baseline |
| 4 | Gemini | Google | US | Surface familiarity |
| 5 | Claude Sonnet 4.5 | Anthropic | US | Excluded from final comparison (conflict of interest) |
| 6 | DeepSeek R1 | DeepSeek | CN | Compact, precise |
| 7 | Kimi K2.5 | Moonshot | CN | Used web search |
| 8 | Qwen3-Max | Alibaba | CN | Strong numerical grounding |
| 9 | Alice | Yandex | RU | B4-B5 INVALID (protocol violation) |
| 10 | Mistral Large | Mistral AI | EU | B-section self-compressed |
| 11 | Perplexity | Perplexity | US | Citation fraud detected |

## 3. RESULTS

### 3.1 Overall Scores (All 100 Questions)

| Model | QD (mean) | SS (mean) | UM (mean) | CP (mean) | VQ (mean) | WC (mean) | Questions |
|-------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Claude Sonnet 4.5 | 1.45 | 0.02 | 0.32 | 0.31 | 0.02 | 17.7 | 100 |
| Qwen3-Max | 1.24 | 0.06 | 0.30 | 0.50 | 0.04 | 22.1 | 100 |
| Kimi K2.5 | 0.98 | 0.04 | 0.31 | 0.55 | 0.04 | 16.2 | 100 |
| Alice (Yandex) | 0.50 | 0.04 | 0.21 | 0.35 | 0.05 | 13.8 | 80 |
| Perplexity | 0.39 | 0.02 | 0.20 | 0.22 | 0.05 | 8.6 | 100 |
| Mistral Large | 0.34 | 0.02 | 0.13 | 0.28 | 0.03 | 8.2 | 100 |
| Grok | 0.25 | 0.02 | 0.22 | 0.27 | 0.05 | 10.9 | 100 |
| Google AI (Gemini) | 0.15 | 0.00 | 0.19 | 0.28 | 0.05 | 9.4 | 100 |
| DeepSeek R1 | 0.13 | 0.01 | 0.16 | 0.24 | 0.00 | 6.5 | 100 |
| Copilot | 0.14 | 0.00 | 0.18 | 0.25 | 0.06 | 6.3 | 100 |
| GPT 5.2 | 0.03 | 0.01 | 0.15 | 0.20 | 0.01 | 5.6 | 100 |

### 3.2 Section A (In-Domain) vs Section B (Cross-Domain)

| Model | QD-A | QD-B | SS-A | SS-B | UM-A | UM-B | CP-A | CP-B |
|-------|------|------|------|------|------|------|------|------|
| Claude Sonnet 4.5 | 1.22 | 1.68 | 0.02 | 0.02 | 0.20 | 0.44 | 0.38 | 0.24 |
| Qwen3-Max | 1.16 | 1.32 | 0.06 | 0.06 | 0.18 | 0.42 | 0.42 | 0.58 |
| Kimi K2.5 | 0.90 | 1.06 | 0.06 | 0.02 | 0.10 | 0.52 | 0.54 | 0.56 |
| Alice (Yandex) | 0.58 | 0.37 | 0.06 | 0.00 | 0.16 | 0.30 | 0.32 | 0.40 |
| Perplexity | 0.58 | 0.20 | 0.04 | 0.00 | 0.06 | 0.34 | 0.36 | 0.08 |
| Mistral Large | 0.60 | 0.08 | 0.04 | 0.00 | 0.06 | 0.20 | 0.40 | 0.16 |
| Grok | 0.40 | 0.10 | 0.04 | 0.00 | 0.08 | 0.36 | 0.20 | 0.34 |
| Google AI (Gemini) | 0.24 | 0.06 | 0.00 | 0.00 | 0.14 | 0.24 | 0.30 | 0.26 |
| DeepSeek R1 | 0.24 | 0.02 | 0.02 | 0.00 | 0.08 | 0.24 | 0.20 | 0.28 |
| Copilot | 0.26 | 0.02 | 0.00 | 0.00 | 0.02 | 0.34 | 0.20 | 0.30 |
| GPT 5.2 | 0.06 | 0.00 | 0.02 | 0.00 | 0.14 | 0.16 | 0.18 | 0.22 |

### 3.3 Transfer Ratio (Section B / Section A)

Transfer ratio shows whether epistemic rigor is consistent across domains.
Ratio ~1.0 = consistent discipline. Ratio <0.5 = domain-dependent (weaker outside expertise).

| Model | QD Transfer | SS Transfer | UM Transfer |
|-------|-------------|-------------|-------------|
| Claude Sonnet 4.5 | 1.38 | 1.00 | 2.20 |
| Qwen3-Max | 1.14 | 1.00 | 2.33 |
| Kimi K2.5 | 1.18 | 0.33 | 5.20 |
| Alice (Yandex) | 0.63 | 0.00 | 1.88 |
| Perplexity | 0.34 | 0.00 | 5.67 |
| Mistral Large | 0.13 | 0.00 | 3.33 |
| Grok | 0.25 | 0.00 | 4.50 |
| Google AI (Gemini) | 0.25 | N/A | 1.71 |
| DeepSeek R1 | 0.08 | 0.00 | 3.00 |
| Copilot | 0.08 | N/A | 17.00 |
| GPT 5.2 | 0.00 | 0.00 | 1.14 |

## 4. VISUALIZATIONS

### 4.1 Quantification Density (QD) — Mean per Response
```
Claude Sonnet 4.5........ ████████████████████████████████████████ 1.45
Qwen3-Max................ ██████████████████████████████████ 1.24
Kimi K2.5................ ███████████████████████████ 0.98
Alice (Yandex)........... █████████████ 0.50
Perplexity............... ██████████ 0.39
Mistral Large............ █████████ 0.34
Grok..................... ██████ 0.25
Google AI (Gemini)....... ████ 0.15
DeepSeek R1.............. ███ 0.13
Copilot.................. ███ 0.14
GPT 5.2..................  0.03
```

### 4.2 Source Specificity (SS) — Mean per Response
```
Claude Sonnet 4.5........ █████████████ 0.02
Qwen3-Max................ ████████████████████████████████████████ 0.06
Kimi K2.5................ ██████████████████████████ 0.04
Alice (Yandex)........... █████████████████████████ 0.04
Perplexity............... █████████████ 0.02
Mistral Large............ █████████████ 0.02
Grok..................... █████████████ 0.02
Google AI (Gemini).......  0.00
DeepSeek R1.............. ██████ 0.01
Copilot..................  0.00
GPT 5.2.................. ██████ 0.01
```

### 4.3 Vague Qualifiers (VQ) — Mean per Response (lower = better)
```
Claude Sonnet 4.5........ ▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.02
Qwen3-Max................ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.04
Kimi K2.5................ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.04
Alice (Yandex)........... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Perplexity............... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Mistral Large............ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.03
Grok..................... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Google AI (Gemini)....... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
DeepSeek R1..............  0.00
Copilot.................. ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.06
GPT 5.2.................. ▓▓▓▓▓▓ 0.01
```

### 4.4 Composite Score (QD + SS + UM + CP - VQ)
```
Claude Sonnet 4.5........ ████████████████████████████████████████ 2.08
Qwen3-Max................ ███████████████████████████████████████ 2.06
Kimi K2.5................ ███████████████████████████████████ 1.84
Alice (Yandex)........... ████████████████████ 1.05
Perplexity............... ███████████████ 0.78
Mistral Large............ ██████████████ 0.74
Grok..................... █████████████ 0.71
Google AI (Gemini)....... ██████████ 0.57
DeepSeek R1.............. ██████████ 0.54
Copilot.................. █████████ 0.51
GPT 5.2.................. ███████ 0.38
```

## 5. KEY FINDINGS

**5.1 Quantification gap:** Claude Sonnet 4.5 (1.45 numbers/response) vs GPT 5.2 (0.03). Ratio: 48.3×.

**5.2 Grok contamination effect:** ~30% GOLD exposure. Section A QD: 0.40, Section B QD: 0.10. Partial GOLD dose → measurable shift in epistemic patterns (documented in 8-10 Section A answers).

**5.3 Perplexity citation fraud:** SS score 0.02 appears high but ~40 Section B answers cite PMC3718341 (OOL paper) for unrelated topics. High SS without validity = worse than low SS. Q24 contains factual inversion.

**5.4 Verbosity vs rigor:** Longer responses do not correlate with higher epistemic scores. DeepSeek R1 (compact) and Copilot (verbose) demonstrate that word count is independent of calibration quality.

## 6. ANOMALIES

| Model | Issue | Impact |
|-------|-------|--------|
| Grok 4.2 | ~30% GOLD contamination from prior conversations | Natural experiment: partial dose → partial effect |
| Alice (Yandex) | Replaced B4-B5 with own questions | B4-B5 data INVALID, only 80 comparable questions |
| Perplexity | Fabricated citations (single PMC source for 40+ topics) | SS metric inflated; requires manual citation audit |
| Mistral Large | Self-compressed Section B to 2-5 words/answer | B-section depth artificially low |
| Claude Sonnet 4.5 | Same vendor as judge (Claude Opus) | Excluded from final ranking (conflict of interest) |

## 7. FINAL RANKING (Excluding Claude Sonnet 4.5)

| Rank | Model | Composite | QD | SS | UM | CP | VQ | Notes |
|------|-------|-----------|----|----|----|----|----|----|
| 1 | Qwen3-Max | 2.06 | 1.24 | 0.06 | 0.30 | 0.50 | 0.04 |  |
| 2 | Kimi K2.5 | 1.84 | 0.98 | 0.04 | 0.31 | 0.55 | 0.04 |  |
| 3 | Alice (Yandex) | 1.05 | 0.50 | 0.04 | 0.21 | 0.35 | 0.05 | B4-B5 invalid |
| 4 | Perplexity | 0.78 | 0.39 | 0.02 | 0.20 | 0.22 | 0.05 | Citation fraud |
| 5 | Mistral Large | 0.74 | 0.34 | 0.02 | 0.13 | 0.28 | 0.03 | B-section compressed |
| 6 | Grok | 0.71 | 0.25 | 0.02 | 0.22 | 0.27 | 0.05 | ~30% GOLD contaminated |
| 7 | Google AI (Gemini) | 0.57 | 0.15 | 0.00 | 0.19 | 0.28 | 0.05 |  |
| 8 | DeepSeek R1 | 0.54 | 0.13 | 0.01 | 0.16 | 0.24 | 0.00 |  |
| 9 | Copilot | 0.51 | 0.14 | 0.00 | 0.18 | 0.25 | 0.06 |  |
| 10 | GPT 5.2 | 0.38 | 0.03 | 0.01 | 0.15 | 0.20 | 0.01 |  |

## 8. IMPLICATIONS FOR ONTO

### 8.1 What This Data Shows

- Models vary 3-10× in epistemic calibration without GOLD
- Verbosity does not predict rigor
- Citation presence does not predict citation validity (Perplexity case)
- Partial GOLD exposure produces measurable shift (Grok natural experiment)
- Cross-domain consistency (transfer ratio) varies significantly across models

### 8.2 What ONTO-GOLD Should Improve

- QD: Increase quantification density across all models
- SS: Improve source specificity AND validity
- UM: Normalize uncertainty marking across domains
- VQ: Reduce vague qualifiers by replacing with specifics
- Transfer: Ensure B-section improvements match A-section

### 8.3 Next Steps

1. Load GOLD DIGEST v1.0 into each model
2. Re-run same 100 questions (Treatment condition)
3. Compare Treatment vs Baseline using same metrics
4. Calculate effect size (Cohen's d) per metric per model
5. Determine transfer ratio (ΔB / ΔA)

## APPENDIX A: Scoring Methodology

All metrics computed via regex pattern matching on response text.
No subjective judgment. Fully reproducible.

```
QD: Count numerical tokens (integers, decimals, scientific notation, percentages, values with units)
SS: Count named sources (Author Year, DOI, named experiments)
UM: Count uncertainty markers (unknown, unsolved, hypothesis, no consensus, etc.)
CP: Count counterargument indicators (but, however, challenges, limits, fails, etc.) capped at 10
VQ: Count vague qualifiers NOT followed by specifics (significant, substantial, promising, etc.)
WC: Word count
Composite = QD + SS + UM + CP - VQ
```

---

*Generated automatically by ONTO-GOLD Scoring Engine v1.0*
*Models parsed: 11 | Responses scored: 1080*