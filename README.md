# ONTO Standard — Deterministic Epistemic Quality Measurement for AI

[![Python](https://img.shields.io/badge/Python-993_lines-blue)](onto-scoring.py)
[![License](https://img.shields.io/badge/License-Open_Source-green)](onto-scoring.py)
[![Models](https://img.shields.io/badge/Models_Tested-11-orange)](ONTO-11-Model-Baseline.md)
[![Website](https://img.shields.io/badge/Web-ontostandard.org-2ec27e)](https://ontostandard.org)

## The Problem

Every AI model answers confidently. Even when it doesn't know.

We tested 11 production models (GPT-4o, GPT-4.5, Claude Sonnet, Claude Haiku, Gemini 2.0, DeepSeek R1, Grok, Mistral Large, Copilot, Kimi, Qwen) across 100 questions in 5 domains. Not a single baseline model provided numeric confidence levels. Zero models quantified what they didn't know.

## The Solution: ONTO GOLD

ONTO GOLD is an epistemic discipline layer for AI models. Not fine-tuning. Not knowledge injection. It teaches models *how* to reason — cite sources, quantify confidence, mark uncertainty, disclose gaps.

**Key result (CS-2026-001):**
- Composite score: 0.53 → 5.38 (**10× improvement**)
- Variance: SD 0.58 → SD 0.11 (**5.4× reduction**)
- Cross-domain transfer: **4/5 metrics** improve in domains not present in GOLD
- Baseline mean: M=0.92 across 10 models

## How Scoring Works

993 lines of Python. 5 regex counters. Zero AI judge. Fully deterministic.

```
1. Numbers    → regex: \d+\.?\d*%?         How many concrete numbers
2. Sources    → regex: (Author+Year)        How many real citations
3. Honesty    → regex: unknown|uncertain    Does it admit gaps
4. Balance    → regex: however|risk|but     Does it present counterarguments
5. Filler     → regex: moderate|significant Penalty for vague qualifiers
```

Same input = same score. Always. On any machine. In any language. `Var(Score) = 0`.

## What's in This Repository

| File | Description |
|------|-------------|
| [onto-scoring.py](onto-scoring.py) | Scoring engine v3.0 (993 lines, zero dependencies) |
| [ONTO-Full-Report.md](ONTO-Full-Report.md) | Complete experiment report with methodology |
| [ONTO-11-Model-Baseline.md](ONTO-11-Model-Baseline.md) | All 11 models scored and compared |
| [gold_experiment_questions.md](gold_experiment_questions.md) | 100 test questions across 5 domains |

## Quick Start

```bash
git clone https://github.com/nickarstrong/onto-research.git
cd onto-research
python onto-scoring.py --input response.txt
```

No dependencies. No API keys. No AI judge. Just regex.

## Results Summary

| Metric | Without ONTO | With ONTO | Change |
|--------|-------------|-----------|--------|
| Composite score | 0.53 | 5.38 | 10× |
| Over-confidence | high | controlled | ↓35% |
| Source citations | 0 per response | 2+ per response | new capability |
| Confidence calibration | 0 | 2+ numeric levels | new capability |
| Output variance (SD) | 0.58 | 0.11 | 5.4× reduction |
| Cross-domain transfer | 0/5 | 4/5 | 80% |

## Key Findings

1. **Behavioral transfer**: Models improve across domains not present in the discipline layer
2. **Hallucination Inside Apology (HIA)**: Models acknowledge errors at macro level while generating new fabrications at micro level — critical safety finding
3. **Convergence effect**: With GOLD, all models converge toward similar epistemic quality regardless of base capability
4. **Zero baseline citation**: Not a single model among 11 tested provides numeric confidence levels without intervention

## For Researchers

Reproduce our results:

```bash
# Score any AI response
python onto-scoring.py --input your_response.txt

# Compare with our baseline
# See ONTO-11-Model-Baseline.md for methodology
```

**Cite as:**
```
ONTO Standard, CS-2026-001. "Deterministic Measurement of Epistemic Quality
in Production LLM Systems." February 2026. https://ontostandard.org
```

**Grant program**: 1,000 proxy requests/day at no cost for qualifying academic institutions. Contact: research@ontostandard.org

## For AI Providers (TIER 1)

Integrate GOLD into your inference pipeline. Fixed annual license, unlimited scale. You receive GOLD once via SSE burst, cache locally, inject into every request. ONTO is not in your inference path — your traffic never touches our servers.

- GOLD Full Corpus
- $250,000/year fixed — no per-token, no per-request fees
- 100 providers × 10M req/day each = our load is 100 SSE connections
- <50ms latency overhead
- Any model architecture (GPT, Claude, Gemini, Llama, Mistral)
- EU AI Act compliance readiness

Contact: providers@ontostandard.org

## For Companies (TIER 2)

Production GOLD discipline for your AI. Server-side injection through ONTO proxy.

- 1,000 proxy requests/day
- GOLD Extended Corpus
- Unlimited SSE stream
- $30,000/year ($2,500/month)

## Open (TIER 3)

Evaluate ONTO on your AI before you commit.

- 10 proxy requests/day
- GOLD Core
- Free

## Links

- **Website**: [ontostandard.org](https://ontostandard.org)
- **Portal**: [ontostandard.org/app](https://ontostandard.org/app/)
- **Documentation**: [ontostandard.org/docs](https://ontostandard.org/docs/)
- **Field Observation (12-phase behavioral analysis)**: [ontostandard.org/encounter](https://ontostandard.org/encounter/)
- **PyPI**: [onto-standard](https://pypi.org/project/onto-standard/)

## Architecture

```
GOLD corpus (private) → Server-side injection → AI model system prompt
Client receives the EFFECT, not the document.
Analogy: Netflix — you watch the film, you don't download the file.
```

Scoring is fully open. GOLD corpus is proprietary.

## License

Scoring engine and research data: open source.
GOLD corpus: proprietary (ontostandard.org).
