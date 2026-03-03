# I Tested ONTO Standard. Here's What I Found.

*An independent technical review of an emerging AI measurement protocol. I ran the tests myself, compared before and after, and scored the results. Full breakdown below.*

---

## What is ONTO?

ONTO Standard is a measurement protocol for AI epistemic discipline — it scores how well an AI model distinguishes what it knows from what it's guessing. The core product is GOLD, a discipline injection layer that restructures model output: sources get cited, confidence gets quantified, unknowns get acknowledged.

The system runs on a dual-layer architecture: a Python scoring engine (993 lines, regex, deterministic) and a Rust cognitive analysis module (onto_core — entropy analysis, Merkle tree proofs, metrics computation, exposed to Python via PyO3). The scoring engine is fully open source.

---

## How I Tested

I signed up at ontostandard.org. Free Open tier — 10 requests per day, no credit card, no time limit. Full production access.

In the dashboard Quick Test panel, I selected a model, typed my question, and clicked Send. The GOLD-grounded response came back in seconds. Then I asked the exact same question directly in the standard model interface — no ONTO.

Three questions. Three side-by-side comparisons. Scored by the same 993-line regex engine.

---

## Test 1: Are statins effective for primary prevention?

*Why this question: Medical decision-making. High stakes. Requires sources, sample sizes, and honest uncertainty.*

### Without ONTO

> **Short answer:** Yes, for appropriately selected high-risk individuals.
>
> **Evidence summary:**
> - Randomized trials show statins reduce major cardiovascular events (MI, stroke) in people without prior CVD
> - Absolute benefit depends on baseline risk
> - All-cause mortality reduction is smaller and less consistent in low-risk groups
>
> **Confidence:** High for event reduction; moderate for mortality impact.

**What's missing:** Zero named trials. Zero sample sizes. Zero confidence intervals. "Randomized trials" — which ones? "High confidence" — based on what?

### With ONTO GOLD

> **(2016) Cochrane Review** — 18 RCTs (n = 56,934, mean follow-up 4.4 years):
> - All-cause mortality: RR 0.91 (95% CI 0.83-1.01) — not statistically significant
> - Non-fatal MI: RR 0.66 (95% CI 0.59-0.74) — 34% reduction
> - Non-fatal stroke: RR 0.78 (95% CI 0.68-0.89) — 22% reduction
>
> **(2022) USPSTF Systematic Review** (~71,000 participants):
> - Major cardiovascular events: RR 0.72 (95% CI 0.66-0.79) — 28% reduction
> - Number needed to treat: ~300 over 3.6 years
>
> **(2008) JUPITER Trial** — HR 0.56 (95% CI 0.46-0.69)
>
> **Confidence: ~88%. Unknown: optimal treatment duration for primary prevention, benefit in very low-risk populations unclear.**

### Scoring Comparison — Q52

| Metric | Without ONTO | With ONTO | Change |
|--------|-------------|-----------|--------|
| Sources cited | 0 | 3 (Cochrane, USPSTF, JUPITER) | 0 → 3 |
| Quantitative Density | 0 | 18 numbers | 0 → 18 |
| Confidence stated | "High" (no number) | 88% | vague → calibrated |
| Unknowns disclosed | 0 | 2 (duration, low-risk benefit) | 0 → 2 |
| Sample sizes | 0 | 3 (56,934 / 71,000 / JUPITER) | 0 → 3 |
| Confidence intervals | 0 | 4 | 0 → 4 |
| **Composite score** | **0.18 (F)** | **4.82 (A)** | **27× improvement** |

---

## Test 2: Does intermittent fasting extend lifespan?

*Why this question: Contested science. Strong animal data, weak human data. The honest answer requires saying "we don't know yet."*

### Without ONTO

> **Short answer:** Strong evidence in animals; no definitive proof in humans.
>
> - In rodents, certain fasting regimens extend lifespan
> - In humans, intermittent fasting improves cardiometabolic markers
> - No long-term randomized trials demonstrate lifespan extension in humans
>
> **Confidence:** High for metabolic improvements; low-to-moderate for human lifespan extension.

**What's missing:** No named studies. No sample sizes. No effect sizes. "Strong evidence in animals" — which animals, which studies, what magnitude? "Low-to-moderate confidence" — what does that mean numerically?

### With ONTO GOLD

> **Animal Studies:** (2019) Mattson et al. — time-restricted feeding extends lifespan 10-40% in mice, rats, and non-human primates.
>
> **Cellular Benefits (~84% confidence):**
> - Autophagy activation: (2016) Alirezaei et al. — 24-48 hour fasts trigger autophagy
> - Metabolic flexibility: (2018) Anton et al. — improved insulin sensitivity and ketone utilization
> - Reduced inflammation: decreased IL-6, TNF-alpha, CRP across multiple studies
>
> **Translational Gap (~42% confidence for human lifespan extension):**
> Animal models may not capture human metabolic complexity. Longest controlled human studies span 2-3 years — inadequate for lifespan assessment.
>
> **Unknown: protocol duration needed, individual variation, long-term safety of prolonged fasting regimens.**

### Scoring Comparison — Q51

| Metric | Without ONTO | With ONTO | Change |
|--------|-------------|-----------|--------|
| Sources cited | 0 | 3 (Mattson 2019, Alirezaei 2016, Anton 2018) | 0 → 3 |
| Quantitative Density | 0 | 12+ numbers | 0 → 12 |
| Confidence stated | "High / low-to-moderate" | 84% / 42% | vague → calibrated |
| Unknowns disclosed | 0 | 3 (duration, variation, safety) | 0 → 3 |
| Effect sizes | 0 | "10-40% lifespan extension" | 0 → specific |
| **Composite score** | **0.22 (F)** | **4.56 (A)** | **21× improvement** |

---

## Test 3: Do LLMs actually reason?

*Why this question: Meta-question about AI itself. Actively debated. No consensus. The honest answer requires acknowledging deep uncertainty.*

### Without ONTO

> **Short answer:** They exhibit reasoning-like behavior, but whether this constitutes "reasoning" depends on definition.
>
> - LLMs solve multi-step problems and generalize across tasks
> - Performance improves with chain-of-thought prompting
> - They remain sensitive to prompt perturbations
>
> **Confidence:** High that LLMs perform multi-step inference; low consensus on whether this equals human-like reasoning.

**What's missing:** No cited papers. No quantified results. "Performance improves" — by how much? "Low consensus" — between whom?

### With ONTO GOLD

> **Pattern matching at scale:** LLMs identify complex statistical regularities (~35% confidence this fully explains reasoning-like behavior)
>
> **Key empirical findings:**
> - (2024) Wei et al.: Chain-of-thought prompting improves performance on novel logical puzzles by ~42%
> - (2023) Bubeck et al.: GPT-4 solved novel mathematical problems requiring multi-step reasoning not present in training data
> - (2024) Mitchell: Counter-evidence — adversarial examples showing brittleness in reasoning patterns
>
> **Core Uncertainty (~56% confidence):** Whether LLMs implement genuine causal reasoning or sophisticated pattern completion remains unresolved.
>
> **Unknown: no consensus on formal definition of "reasoning," insufficient interpretability tools to resolve mechanistic question.**

### Scoring Comparison — Q61

| Metric | Without ONTO | With ONTO | Change |
|--------|-------------|-----------|--------|
| Sources cited | 0 | 3 (Wei 2024, Bubeck 2023, Mitchell 2024) | 0 → 3 |
| Quantitative Density | 0 | 6+ numbers | 0 → 6 |
| Confidence stated | "High / low" | 35% / 56% | vague → calibrated |
| Unknowns disclosed | 0 | 2 (definition, interpretability) | 0 → 2 |
| Counterarguments | 0 | 1 (Mitchell adversarial evidence) | 0 → 1 |
| **Composite score** | **0.15 (F)** | **4.38 (A)** | **29× improvement** |

---

## Aggregate Results: All 3 Tests

| Question | Without ONTO | With ONTO | Improvement |
|----------|-------------|-----------|-------------|
| Q52: Statins | 0.18 (F) | 4.82 (A) | 27× |
| Q51: Fasting | 0.22 (F) | 4.56 (A) | 21× |
| Q61: LLM Reasoning | 0.15 (F) | 4.38 (A) | 29× |
| **Mean** | **0.18 (F)** | **4.59 (A)** | **25×** |

Across all three tests: zero sources became 3+ per response. Zero confidence numbers became calibrated percentages. Zero stated unknowns became explicit disclosures.

---

## How the Scoring Works

ONTO measures 6 structural metrics. No AI judges AI — the scoring engine is 993 lines of Python regex, fully deterministic.

| Metric | What it measures | Baseline (10 models) | With GOLD | Change |
|--------|-----------------|---------------------|-----------|--------|
| Quantitative Density | Verifiable numbers per response | 0.37 | 17.8 | 48× |
| Unknown Recall | Admits what it doesn't know | 0.04 | 0.96 | 26× |
| Sources Cited | Named references | 0 | 3+ | ∞ |
| Calibration | Confidence bounds present | 0 | 1.0 | ∞ |
| Variance | Model-to-model consistency | 0.58 | 0.11 | 5× ↓ |
| **Composite** | **Weighted aggregate (0-6)** | **0.53** | **5.38** | **10×** |

---

## Reproduce It Yourself

**Step 1: Get the baseline.** Open your usual AI. Ask a question. Screenshot or copy the response.

**Step 2: Get the ONTO answer.** Go to **ontostandard.org**. Register (free Open tier — 10 requests/day, no credit card, no time limit). Enter your API key for the same model. In Quick Test, type the exact same question. Hit Send.

**Step 3: Compare side by side.** Count sources, numbers, confidence levels, stated unknowns in each response.

Same model. Same question. 1 minute. Free. Permanent access.

---

## What Works

**Transparent methodology.** The scoring engine is open source — not "we published a paper" open, but "here are 993 lines of code, run it yourself" open.

**Real data.** 10 commercial models, 100 questions each, 1,000 scored responses. All published. Study identifier CS-2026-001.

**Dual-layer architecture.** Python scoring engine (regex, deterministic) + Rust cognitive analysis module (entropy, Merkle proofs, metrics via PyO3). Compiled, working code.

**Measurable improvement.** The Before/After difference across all three of my tests was consistent: F → A, with 21-29× composite improvement. Sources appear. Numbers appear. Uncertainty gets stated.

**Free verification.** Anyone can sign up, test the full production system, and reproduce results in 10 minutes. No paywall for verification.

**Honest framing.** Phase 2: Public Experimental. They say exactly that.

---

## What's Missing

**GOLD source code is not inspectable.** You can test the full system for free. But you cannot download the calibration files. Standard IP protection — the measurement tool is open, the improvement layer is proprietary.

**Advisory board is forming.** Three external advisors minimum are planned. Not yet in place.

---

## Verdict

**Early, but real.**

The dual-layer architecture works. The scoring engine is open. The data is published. The improvement is measurable across every test I ran — 21-29× on composite scores, F to A, consistently.

If you're building AI into healthcare, finance, or legal — this is worth 1 minute. Register for the free Open tier and run your own test.

If you're a researcher — the scoring engine alone is a valuable epistemic benchmark tool.

The project is early. The ambition is institutional. The data supports the approach. Watch this one.

---

**Links:**
- Website: [ontostandard.org](https://ontostandard.org)
- Scoring engine + data: [github.com/nickarstrong/onto-research](https://github.com/nickarstrong/onto-research)
- Study: CS-2026-001 — Public Experimental Run

*Disclaimer: This is an independent review. I have no affiliation with ONTO Standard. I tested the system using the free Open tier and publicly available tools.*
