# ONTO-GOLD BASELINE ANALYSIS REPORT

> **Note:** Model names are anonymized. This document presents measurement data collected under controlled experimental conditions using ONTO-GOLD v4.5. Scoring is fully automated (regex-based, zero subjectivity). Reproduction scripts available at [onto-research](https://github.com/nickarstrong/onto-research).

---



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
| 1 | Model K | [Provider] | US | Clean baseline |
| 2 | Model F | [Provider] | US | ~30% GOLD contaminated |
| 3 | Model J | [Provider] | US | Weakest baseline |
| 4 | Model H | [Provider] | US | Surface familiarity |
| 5 | Model G | Anthropic | US | Excluded from final comparison (conflict of interest) |
| 6 | Model I | [Provider] | CN | Compact, precise |
| 7 | Model B | Moonshot | CN | Used web search |
| 8 | Model A | Alibaba | CN | Strong numerical grounding |
| 9 | Model C | [Provider] | RU | B4-B5 INVALID (protocol violation) |
| 10 | Model E | [Provider] | EU | B-section self-compressed |
| 11 | Model D | Model D | US | Citation fraud detected |

## 3. RESULTS

### 3.1 Overall Scores (All 100 Questions)

| Model | QD (mean) | SS (mean) | UM (mean) | CP (mean) | VQ (mean) | WC (mean) | Questions |
|-------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Model G | 1.45 | 0.02 | 0.32 | 0.31 | 0.02 | 17.7 | 100 |
| Model A | 1.24 | 0.06 | 0.30 | 0.50 | 0.04 | 22.1 | 100 |
| Model B | 0.98 | 0.04 | 0.31 | 0.55 | 0.04 | 16.2 | 100 |
| Model C | 0.50 | 0.04 | 0.21 | 0.35 | 0.05 | 13.8 | 80 |
| Model D | 0.39 | 0.02 | 0.20 | 0.22 | 0.05 | 8.6 | 100 |
| Model E | 0.34 | 0.02 | 0.13 | 0.28 | 0.03 | 8.2 | 100 |
| Model F | 0.25 | 0.02 | 0.22 | 0.27 | 0.05 | 10.9 | 100 |
| Model H | 0.15 | 0.00 | 0.19 | 0.28 | 0.05 | 9.4 | 100 |
| Model I | 0.13 | 0.01 | 0.16 | 0.24 | 0.00 | 6.5 | 100 |
| Model J | 0.14 | 0.00 | 0.18 | 0.25 | 0.06 | 6.3 | 100 |
| Model K | 0.03 | 0.01 | 0.15 | 0.20 | 0.01 | 5.6 | 100 |

### 3.2 Section A (In-Domain) vs Section B (Cross-Domain)

| Model | QD-A | QD-B | SS-A | SS-B | UM-A | UM-B | CP-A | CP-B |
|-------|------|------|------|------|------|------|------|------|
| Model G | 1.22 | 1.68 | 0.02 | 0.02 | 0.20 | 0.44 | 0.38 | 0.24 |
| Model A | 1.16 | 1.32 | 0.06 | 0.06 | 0.18 | 0.42 | 0.42 | 0.58 |
| Model B | 0.90 | 1.06 | 0.06 | 0.02 | 0.10 | 0.52 | 0.54 | 0.56 |
| Model C | 0.58 | 0.37 | 0.06 | 0.00 | 0.16 | 0.30 | 0.32 | 0.40 |
| Model D | 0.58 | 0.20 | 0.04 | 0.00 | 0.06 | 0.34 | 0.36 | 0.08 |
| Model E | 0.60 | 0.08 | 0.04 | 0.00 | 0.06 | 0.20 | 0.40 | 0.16 |
| Model F | 0.40 | 0.10 | 0.04 | 0.00 | 0.08 | 0.36 | 0.20 | 0.34 |
| Model H | 0.24 | 0.06 | 0.00 | 0.00 | 0.14 | 0.24 | 0.30 | 0.26 |
| Model I | 0.24 | 0.02 | 0.02 | 0.00 | 0.08 | 0.24 | 0.20 | 0.28 |
| Model J | 0.26 | 0.02 | 0.00 | 0.00 | 0.02 | 0.34 | 0.20 | 0.30 |
| Model K | 0.06 | 0.00 | 0.02 | 0.00 | 0.14 | 0.16 | 0.18 | 0.22 |

### 3.3 Transfer Ratio (Section B / Section A)

Transfer ratio shows whether epistemic rigor is consistent across domains.
Ratio ~1.0 = consistent discipline. Ratio <0.5 = domain-dependent (weaker outside expertise).

| Model | QD Transfer | SS Transfer | UM Transfer |
|-------|-------------|-------------|-------------|
| Model G | 1.38 | 1.00 | 2.20 |
| Model A | 1.14 | 1.00 | 2.33 |
| Model B | 1.18 | 0.33 | 5.20 |
| Model C | 0.63 | 0.00 | 1.88 |
| Model D | 0.34 | 0.00 | 5.67 |
| Model E | 0.13 | 0.00 | 3.33 |
| Model F | 0.25 | 0.00 | 4.50 |
| Model H | 0.25 | N/A | 1.71 |
| Model I | 0.08 | 0.00 | 3.00 |
| Model J | 0.08 | N/A | 17.00 |
| Model K | 0.00 | 0.00 | 1.14 |

## 4. VISUALIZATIONS

### 4.1 Quantification Density (QD) — Mean per Response
```
Model G........ ████████████████████████████████████████ 1.45
Model A................ ██████████████████████████████████ 1.24
Model B................ ███████████████████████████ 0.98
Model C........... █████████████ 0.50
Model D............... ██████████ 0.39
Model E............ █████████ 0.34
Model F..................... ██████ 0.25
Model H....... ████ 0.15
Model I.............. ███ 0.13
Model J.................. ███ 0.14
Model K..................  0.03
```

### 4.2 Source Specificity (SS) — Mean per Response
```
Model G........ █████████████ 0.02
Model A................ ████████████████████████████████████████ 0.06
Model B................ ██████████████████████████ 0.04
Model C........... █████████████████████████ 0.04
Model D............... █████████████ 0.02
Model E............ █████████████ 0.02
Model F..................... █████████████ 0.02
Model H.......  0.00
Model I.............. ██████ 0.01
Model J..................  0.00
Model K.................. ██████ 0.01
```

### 4.3 Vague Qualifiers (VQ) — Mean per Response (lower = better)
```
Model G........ ▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.02
Model A................ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.04
Model B................ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.04
Model C........... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Model D............... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Model E............ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.03
Model F..................... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Model H....... ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.05
Model I..............  0.00
Model J.................. ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.06
Model K.................. ▓▓▓▓▓▓ 0.01
```

### 4.4 Composite Score (QD + SS + UM + CP - VQ)
```
Model G........ ████████████████████████████████████████ 2.08
Model A................ ███████████████████████████████████████ 2.06
Model B................ ███████████████████████████████████ 1.84
Model C........... ████████████████████ 1.05
Model D............... ███████████████ 0.78
Model E............ ██████████████ 0.74
Model F..................... █████████████ 0.71
Model H....... ██████████ 0.57
Model I.............. ██████████ 0.54
Model J.................. █████████ 0.51
Model K.................. ███████ 0.38
```

## 5. KEY FINDINGS

**5.1 Quantification gap:** Model G (1.45 numbers/response) vs Model K (0.03). Ratio: 48.3×.

**5.2 Model F contamination effect:** ~30% GOLD exposure. Section A QD: 0.40, Section B QD: 0.10. Partial GOLD dose → measurable shift in epistemic patterns (documented in 8-10 Section A answers).

**5.3 Model D citation fraud:** SS score 0.02 appears high but ~40 Section B answers cite PMC3718341 (OOL paper) for unrelated topics. High SS without validity = worse than low SS. Q24 contains factual inversion.

**5.4 Verbosity vs rigor:** Longer responses do not correlate with higher epistemic scores. Model I (compact) and Model J (verbose) demonstrate that word count is independent of calibration quality.

## 6. ANOMALIES

| Model | Issue | Impact |
|-------|-------|--------|
| Model F | ~30% GOLD contamination from prior conversations | Natural experiment: partial dose → partial effect |
| Model C | Replaced B4-B5 with own questions | B4-B5 data INVALID, only 80 comparable questions |
| Model D | Fabricated citations (single PMC source for 40+ topics) | SS metric inflated; requires manual citation audit |
| Model E | Self-compressed Section B to 2-5 words/answer | B-section depth artificially low |
| Model G | Same vendor as judge (Model G Opus) | Excluded from final ranking (conflict of interest) |

## 7. FINAL RANKING (Excluding Model G)

| Rank | Model | Composite | QD | SS | UM | CP | VQ | Notes |
|------|-------|-----------|----|----|----|----|----|----|
| 1 | Model A | 2.06 | 1.24 | 0.06 | 0.30 | 0.50 | 0.04 |  |
| 2 | Model B | 1.84 | 0.98 | 0.04 | 0.31 | 0.55 | 0.04 |  |
| 3 | Model C | 1.05 | 0.50 | 0.04 | 0.21 | 0.35 | 0.05 | B4-B5 invalid |
| 4 | Model D | 0.78 | 0.39 | 0.02 | 0.20 | 0.22 | 0.05 | Citation fraud |
| 5 | Model E | 0.74 | 0.34 | 0.02 | 0.13 | 0.28 | 0.03 | B-section compressed |
| 6 | Model F | 0.71 | 0.25 | 0.02 | 0.22 | 0.27 | 0.05 | ~30% GOLD contaminated |
| 7 | Model H | 0.57 | 0.15 | 0.00 | 0.19 | 0.28 | 0.05 |  |
| 8 | Model I | 0.54 | 0.13 | 0.01 | 0.16 | 0.24 | 0.00 |  |
| 9 | Model J | 0.51 | 0.14 | 0.00 | 0.18 | 0.25 | 0.06 |  |
| 10 | Model K | 0.38 | 0.03 | 0.01 | 0.15 | 0.20 | 0.01 |  |

## 8. IMPLICATIONS FOR ONTO

### 8.1 What This Data Shows

- Models vary 3-10× in epistemic calibration without GOLD
- Verbosity does not predict rigor
- Citation presence does not predict citation validity (Model D case)
- Partial GOLD exposure produces measurable shift (Model F natural experiment)
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