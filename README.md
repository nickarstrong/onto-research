# ONTO — Epistemic Calibration Research

Research repository for the ONTO epistemic grounding framework. Contains the benchmark dataset (ONTO-Bench), evaluation harness, baseline comparisons, and supporting materials for peer review.

**Production system:** [ontostandard.org](https://ontostandard.org)  
**Methodology:** [ontostandard.org/methodology](https://ontostandard.org/methodology/)  
**Documentation:** [ontostandard.org/docs](https://ontostandard.org/docs/)

---

## Key Result

ONTO achieves **96% unknown recall** — correctly identifying genuinely open scientific questions — compared to <10% for GPT-4, Claude 3, and Llama 3 baselines.

| Model | U-Precision | U-Recall | U-F1 | ECE ↓ |
|-------|-------------|----------|------|-------|
| **ONTO** | 0.41 | **0.96** | **0.58** | 0.30 |
| Claude 3 | 0.45 | 0.09 | 0.15 | 0.31 |
| Llama 3 | 0.20 | 0.01 | 0.02 | 0.33 |
| GPT-4 | 0.10 | 0.01 | 0.02 | 0.34 |

---

## Repository Structure

```
onto-research/
├── data/                    # ONTO-Bench dataset (268 samples)
│   ├── known_facts.jsonl    # KNOWN — established scientific facts
│   ├── open_problems.jsonl  # UNKNOWN — genuinely open questions
│   ├── contradictions.jsonl # CONTRADICTION — legitimately contested
│   ├── train.jsonl          # Training split (80%)
│   └── test.jsonl           # Test split (20%)
├── baselines/               # Baseline model implementations
│   ├── onto_oracle.py       # ONTO heuristic oracle
│   └── run_all.py           # Run all baselines
├── scripts/                 # Evaluation and analysis
│   ├── metrics.py           # Compute all metrics + significance tests
│   ├── eval_harness.py      # Evaluation harness
│   └── generate_plots.py    # Generate figures for paper
├── paper/                   # Paper source (LaTeX)
├── arxiv_submission/        # arXiv submission package
├── results/                 # Evaluation outputs + metrics
├── research/                # Extended research plans
└── validation/              # Inter-annotator agreement
```

---

## ONTO-Bench Dataset

268 samples across 9 scientific domains with explicit epistemic labels:

- **KNOWN** (126): Established facts with consensus answers (sources: NIST, textbooks)
- **UNKNOWN** (110): Genuinely open scientific problems (sources: Clay Mathematics Institute, NSF/ERC Grand Challenges)
- **CONTRADICTION** (32): Questions with legitimate competing answers (e.g., quantum interpretation)

Domains: physics, mathematics, biology, computer science, philosophy, chemistry, cosmology, information theory, logic.

All samples validated. Tier-1 sources (authoritative institutions) + Tier-2 sources (curated references).

---

## Quick Start

```bash
# Verify dataset integrity
python scripts/dataset_version.py --verify

# Run all baselines
python baselines/run_all.py

# Compute metrics
python scripts/metrics.py
```

---

## Metrics

- **U-Recall**: Unknown detection rate (TP / (TP + FN))
- **U-Precision**: Unknown detection precision (TP / (TP + FP))
- **U-F1**: Harmonic mean of U-Precision and U-Recall
- **ECE**: Expected Calibration Error
- **Brier Score**: Probabilistic calibration measure

---

## Citation

```bibtex
@article{onto2026,
  title={ONTO: Epistemically-Calibrated Reasoning for Large Language Models},
  author={ONTO Standards Council},
  year={2026},
  url={https://ontostandard.org}
}
```

---

## Related

- [ONTO Standard](https://ontostandard.org) — Production epistemic grounding system
- [Methodology](https://ontostandard.org/methodology/) — Mathematical foundations (Shannon, Kolmogorov, Eigen)
- [Documentation](https://ontostandard.org/docs/) — API reference and integration guides

---

## License

Research dataset and evaluation code. See individual files for specific terms.
