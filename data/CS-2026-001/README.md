# CS-2026-001 — Public Experimental Run

**Study:** ONTO GOLD Epistemic Discipline Measurement  
**Date:** 2026-02-14  
**Status:** Phase 2 — Public Experimental  
**Protocol:** ONTO-SPEC-001 v1.0  

## What This Is

100-question epistemic evaluation across 11 AI models. Measures how models communicate what they know vs. what they're guessing — independent of factual correctness.

## Files

| File | Description |
|------|-------------|
| `baseline_scores.json` | Aggregate metrics for all 11 models (no GOLD) |
| `final_ranking.json` | Final ranking, 10 models (Claude excluded, conflict of interest) |
| `anomalies.json` | Protocol violations and data quality notes |
| `treatment_gpt52_100q.jsonl` | All 100 questions: GPT 5.2 baseline vs GOLD treatment, full text + metrics |
| `treatment_summary.json` | Aggregate treatment results |

## Metrics

```
QD   Quantification Density  — numerical values per response       (higher = better)
SS   Source Specificity       — named sources with author/year/DOI  (higher = better)  
UM   Uncertainty Marking      — explicit unknowns acknowledged       (higher = better)
CP   Counterargument Presence — opposing views mentioned            (higher = better)
VQ   Vague Qualifiers         — empty words without specifics        (lower = better)
CONF Calibrated Confidence    — % confidence with methodology        (higher = better)

Composite = QD + SS + UM + CP - VQ
```

## Key Results

| Condition | Mean Composite | n |
|-----------|---------------|---|
| Baseline (no GOLD) | 0.53 | 10 models × 100Q |
| Treatment (GPT 5.2 + GOLD) | 5.38 | 100Q |
| Improvement | **10.2×** | — |

Per-question improvement (GPT 5.2): 0.08 → 3.91 (48.9×)  
Note: per-question mean lower than aggregate because aggregate weights stronger questions.

## Reproduce

```bash
git clone https://github.com/nickarstrong/onto-research
pip install onto-standard
```

Or test live: [ontostandard.org](https://ontostandard.org) — free Open tier, 10 req/day, no credit card.

## Anomalies

- **Grok 4.2:** ~30% GOLD contamination from prior conversations  
- **Perplexity:** Citation fraud — single PMC ID cited for 40+ unrelated topics  
- **Alice (Yandex):** Protocol violation — replaced 2 questions with own questions  
- **Claude Sonnet 4.5:** Excluded from ranking (conflict of interest — ONTO infrastructure runs on Anthropic API)  

## Citation

```
ONTO Standard, CS-2026-001: Public Experimental Run.
ONTO Standards Council, February 2026.
https://github.com/nickarstrong/onto-research
```
