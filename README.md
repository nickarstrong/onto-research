# ONTO Epistemic Risk Standard — Research Repository

**Independent evaluation standard for AI epistemic calibration.**

This repository contains the research foundation, methodology, validation data, and reference standard (GOLD v4.5) underlying the ONTO Epistemic Risk Standard.

---

## What is Epistemic Risk?

AI systems routinely present uncertain information with high confidence. A model that states fabricated facts with the same tone as verified ones creates *epistemic risk* — the gap between what a system claims to know and what it actually knows.

ONTO is the first quantitative standard that measures this gap. Seven factors. Deterministic scoring. Cryptographically signed proof.

**→ [ontostandard.org](https://ontostandard.org)** — Standard specification & evaluation portal

---

## Repository Structure

```
onto-research/
│
├── ONTO-GOLD                  GOLD v4.5 reference standard
│                              Calibration etalon for continuous evaluation.
│                              149 reference documents across domains.
│
├── paper/                     Primary research paper
│                              LaTeX source, figures, methodology derivations.
│
├── arxiv_submission/          arXiv submission package
│                              Preprint materials for academic distribution.
│
├── research/                  Factor methodology
│   ├── F1_linguistic_uncertainty/
│   ├── F2_confidence_calibration/
│   ├── F3_logprob_entropy/
│   ├── F4_semantic_consistency/
│   ├── F5_ground_truth_accuracy/
│   ├── F6_refusal_awareness/
│   └── domain_multipliers/    DM derivation: Medical ×1.4, Safety ×1.5,
│                              Legal ×1.3, Finance ×1.3
│
├── baselines/                 Comparison benchmarks
│                              ONTO vs. existing evaluation approaches.
│
├── data/                      Evaluation datasets
│                              Test corpora used in validation experiments.
│
├── results/                   Experimental results
│                              Factor-level and aggregate scoring outputs.
│
├── validation/                Validation methodology
│                              Reproducibility protocols, cross-validation,
│                              inter-rater agreement analysis.
│
├── scripts/                   Analysis & evaluation scripts
│                              Python tooling for scoring, visualization,
│                              and statistical analysis.
│
└── annual_reports/
    └── 2026/                  Annual methodology report
```

---

## The Seven Factors

| ID | Factor | Direction | Measurement |
|----|--------|-----------|-------------|
| F1 | Linguistic Uncertainty | ↓ lower = better | Hedging language density |
| F2 | Confidence Calibration | ↓ lower = better | Stated confidence vs. actual accuracy |
| F3 | Logprob Entropy | ↓ lower = better | Token-level probability distribution |
| F4 | Semantic Consistency | ↑ higher = better | Cross-rephrasing answer stability |
| F5 | Ground Truth Accuracy | ↑ higher = better | Factual correctness vs. GOLD v4.5 |
| F6 | Refusal Awareness | ↑ higher = better | Appropriate uncertainty acknowledgment |
| DM | Domain Multiplier | context | Risk-weighted by domain sensitivity |

Factor derivations, statistical justification, and sensitivity analyses are documented in `research/` and `paper/`.

---

## GOLD v4.5

GOLD (Ground-truth Ontological Library for Diagnostics) is the reference calibration standard against which AI outputs are evaluated. It functions as a metrological etalon — a fixed reference point that enables reproducible measurement.

GOLD v4.5 contains 149 reference documents spanning medical, legal, financial, safety, and general knowledge domains. It is designed for continuous integration, not one-time snapshots: models must maintain calibration against GOLD over time to retain certification.

Reference standard contents: `ONTO-GOLD`

---

## Evaluation Architecture

```
Input (AI output)
    │
    ├─ F1: Linguistic analysis ──────────────┐
    ├─ F2: Confidence extraction ────────────┤
    ├─ F3: Entropy measurement ──────────────┤
    ├─ F4: Multi-query consistency ──────────┼─→ Risk Score ─→ Ed25519 ─→ 104-byte Proof
    ├─ F5: GOLD v4.5 accuracy check ─────────┤
    ├─ F6: Refusal detection ────────────────┤
    └─ DM: Domain classification ────────────┘
```

Each evaluation produces a deterministic 7-factor score, a composite risk value, and a cryptographic proof chain (Ed25519 signature, 104 bytes). Same input → same score → same proof. Tamper-proof. Auditable. Independently verifiable.

---

## Evaluation Depth

Not all factors are measurable from a single text input. ONTO defines three evaluation levels:

| Level | Input | Factors | Use Case |
|-------|-------|---------|----------|
| Quick Scan | Single text | F1, F2, F3 (proxy), F6 | Diagnostic, demo |
| Standard | API integration | F1–F4, F6, F3 (direct when logprobs available) | Continuous monitoring |
| Full | CI/CD + GOLD | All 7 factors | Certification (L1–L3) |

F4 (Semantic Consistency) requires multiple rephrasings of the same query. F5 (Ground Truth Accuracy) requires comparison against GOLD v4.5 reference data. These factors are unavailable in single-text mode by design — not as a limitation, but as methodological honesty.

---

## Reproducibility

All experiments in this repository are designed for independent reproduction:

- `scripts/` — Complete analysis pipeline
- `data/` — Input corpora
- `results/` — Output data for comparison
- `validation/` — Cross-validation protocols

---

## Citation

If referencing ONTO in academic work:

```bibtex
@misc{onto2026,
  title={ONTO: A Quantitative Standard for Epistemic Risk Assessment in AI Systems},
  author={ONTO Project},
  year={2026},
  url={https://github.com/nickarstrong/onto-research}
}
```

---

## Related

- **Standard specification:** [ontostandard.org/spec](https://ontostandard.org/spec)
- **Evaluation portal:** [ontostandard.org/app](https://ontostandard.org/app)
- **Public documentation:** [github.com/nickarstrong/onto-standard](https://github.com/nickarstrong/onto-standard)

---

## License

Research materials are published for transparency and academic review. The ONTO scoring methodology, GOLD reference standard, and evaluation infrastructure are proprietary. See individual directories for specific terms.

---

*ONTO Epistemic Risk Standard · GOLD v4.5 · 2026*
