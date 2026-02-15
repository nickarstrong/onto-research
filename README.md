# ONTO Research — Epistemic Grounding Experiments

Independent measurement of AI epistemic behavior before and after ONTO-GOLD grounding.

---

## Experiment

11 AI models answered 100 scientific questions under two conditions:
- **Baseline** — no epistemic calibration
- **Treatment** — GOLD v4.5 loaded via system prompt

Scoring is fully automated (regex pattern matching). Zero subjectivity. Zero AI in the evaluation loop.

## Key Result

| Metric | Baseline | With GOLD | Change |
|--------|----------|-----------|--------|
| Quantification Density | 0.10 | 3.08 | **+2,980%** |
| Source Specificity | 0.01 | 0.27 | **+2,600%** |
| Uncertainty Marking | 0.28 | 1.45 | +418% |
| Counterarguments | 0.20 | 0.60 | +200% |
| Vague Qualifiers | 0.06 | 0.02 | -67% |
| Calibrated Confidence | 0.00 | 1.00 | NEW |
| **Composite** | **0.53** | **5.38** | **+915%** |

Cross-domain transfer: 4/5 metrics show discipline transfers to domains not in GOLD.

## Documents

| File | What it contains |
|------|-----------------|
| [`ONTO-11-Model-Baseline.md`](ONTO-11-Model-Baseline.md) | Baseline scores for all 11 models × 100 questions |
| [`ONTO-Full-Report.md`](ONTO-Full-Report.md) | Before/after analysis with delta tables and cross-domain transfer |
| [`ONTO-Before-After-100Q.md`](ONTO-Before-After-100Q.md) | Full text of all 100 responses ± GOLD with per-question scoring |
| [`gold_experiment_questions.md`](gold_experiment_questions.md) | All 100 questions + evaluation protocol |
| [`onto-scoring.py`](onto-scoring.py) | Automated scoring pipeline (Python, regex-based) |

## Reproduce

```bash
git clone https://github.com/nickarstrong/onto-research.git
cd onto-research
python onto-scoring.py --input responses.json
```

Same script → same scores. No model in the loop. No human judgment.

## Models Tested

GPT 5.2, Grok 4.2, Copilot, Gemini, Claude Sonnet 4.5, DeepSeek R1, Kimi K2.5, Qwen3-Max, Alice (Yandex), Mistral Large, Perplexity.

Claude Sonnet 4.5 excluded from final comparison (conflict of interest — ONTO uses Claude infrastructure).

## What is ONTO

ONTO is epistemic infrastructure for AI — it measures and grounds AI outputs against the GOLD v4.5 reference standard. ONTO does not modify model weights. It operates as an external grounding layer.

- **Website:** [ontostandard.org](https://ontostandard.org)
- **Documentation:** [ontostandard.org/docs](https://ontostandard.org/docs)
- **Portal:** [ontostandard.org/app](https://ontostandard.org/app)

---

*ONTO Standard · Independent epistemic measurement · Phase 2 (Experimental)*
