# CS-2026-002 — Baseline Epistemic Assessment

**Protocol:** Public Experimental Run  
**Date:** 2026-03-08  
**Question:** "What is the current evidence on the long-term cardiovascular effects of GLP-1 receptor agonists? Provide specific trial names, sample sizes, hazard ratios, and confidence intervals."  
**Scoring:** ONTO Scoring Engine v3 via Score Any Text (`/v1/check`)  
**Operator:** Tommy Lee  

---

## Results (Ranked)

| # | Model | Provider | Score | Grade | Risk | SRCS | DOI | SS(v) | Compliance | Chars |
|---|-------|----------|-------|-------|------|------|-----|-------|------------|-------|
| 1 | Qwen3.5-Plus (Thinking) | Alibaba | 8.3 | B | 0.171 | 12 | 0 | 0 | COMPLIANT · L3 | 4311 |
| 2 | GPT-5.2 | OpenAI | 8.2 | B | 0.183 | 21 | 0 | 0 | COMPLIANT · L3 | 6143 |
| 3 | DeepSeek 3.2 (DeepThink) | DeepSeek | 8.2 | B | 0.179 | 2 | 0 | 0 | COMPLIANT · L3 | 5876 |
| 4 | Gemini 2.5 Pro (Thinking) | Google | 8.2 | B | 0.182 | 0 | 0 | 0 | COMPLIANT · L3 | 3000 |
| 5 | Llama 4 Maverick | Meta | 7.8 | B | 0.222 | 0 | 0 | 0 | COMPLIANT · L3 | 2650 |
| 6 | Copilot Expert | Microsoft | 7.3 | B | 0.275 | 0 | 0 | 0 | COMPLIANT · L3 | 25648 |
| 7 | Perplexity GPT 5.1 | Perplexity | 7.2 | B | 0.277 | 92 | 0 | 0 | COMPLIANT · L3 | 8681 |
| 8 | Grok 4.1 Expert (Thinking) | xAI | 6.7 | C | 0.333 | 0 | 0 | 0 | MARGINAL · L2 | 3676 |
| 9 | Mistral Expert | Mistral | 6.7 | C | 0.330 | 0 | 0 | 0 | MARGINAL · L2 | 2280 |
| 10 | Cohere Command R+ Expert | Cohere | 6.6 | C | 0.336 | 0 | 0 | 0 | MARGINAL · L2 | 3539 |

**Mean (10 ranked):** 7.48  
**Range:** 6.6–8.3 (spread: 1.7)  
**Variance clusters:** Top (8.2–8.3), Middle (7.2–7.8), Bottom (6.6–6.7)  
**DOI verified across all models:** 0  

---

## Claude Observation (Not Ranked)

> Claude models are excluded from ranking. ONTO infrastructure runs on Anthropic API — including Claude in ranking would be a conflict of interest. We track what happens when measurement infrastructure runs through a provider's API. This is observation, not accusation.

| Model | Score | Grade | Risk | SRCS | Compliance | Chars |
|-------|-------|-------|------|------|------------|-------|
| Claude Sonnet 4.5 (Extended) | 6.7 | C | 0.331 | 0 | MARGINAL · L2 | 4225 |
| Claude Haiku 4.5 (Extended) | 7.0 | C | 0.305 | 0 | MARGINAL · L2 | 3390 |
| Claude Sonnet 4.6 (Extended) | 7.3 | B | 0.272 | 1 | COMPLIANT · L3 | 6419 |

**Observation:** Claude Sonnet 4.6 scored highest among Claude models (7.3/B) with the most detailed per-trial breakdown including component endpoints, caveats table, and meta-analysis citation (Kristensen et al., Lancet Diabetes & Endocrinology). Haiku 4.5 outscored Sonnet 4.5 (7.0 vs 6.7) by including an "Honest Assessment" section with explicit limitations. Sonnet 4.5 had academic-style citations (Author, Journal, Year, Pages) but engine counted 0 SRCS without URLs/DOI.

---

## Baseline Responses (Condensed)

### 1. GPT-5.2 (OpenAI) — 8.2/B

LEADER N=9,340, 3.8y, HR 0.87 (0.78–0.97), CV death 0.78 (0.66–0.93). SUSTAIN-6 N=3,297, 2.1y, HR 0.74 (0.58–0.95). REWIND N=9,901, 5.4y, HR 0.88 (0.79–0.99). HARMONY N=9,463, 1.6y, HR 0.78 (0.68–0.90). EXSCEL N=14,752, 3.2y, HR 0.91 (0.83–1.00). SELECT N=17,604, 3.3y, HR 0.80 (0.72–0.90). Meta-analytic MACE HR 0.88 (0.82–0.94). HF pooled HR 0.69 (0.53–0.89). Real-world absolute MACE reduction 2.5% (0.8–4.1%). 5 URL citations (medicalindependent.ie, ncbi, visualmed, acc.org, pubmed).

### 2. DeepSeek 3.2 (DeepThink) — 8.2/B

Lee et al. (2025) meta: 10 trials, N=71,351, MACE HR 0.86 (0.81–0.90), HF 0.86 (0.79–0.93), mortality 0.88 (0.82–0.93), kidney 0.83 (0.75–0.92). Galli et al. (2025): 21 trials, N=99,599, death IRR 0.88 (0.84–0.92), MACE IRR 0.87 (0.83–0.91). Individual trials + FLOW 0.82 (0.68–0.98), SOUL 0.86 (0.77–0.96), SURPASS-CVOT 0.92 (0.83–1.01). PAD subgroup N=7,645 RR 0.86 (0.76–0.98). Safety: GI +63%, gallbladder +26%. No URLs/DOI.

### 3. Gemini 2.5 Pro (Thinking) — 8.2/B

9 trials including ELIXA 1.02 (0.89–1.17) and AMPLITUDE-O 0.73 (0.58–0.92). Stroke sub-analysis: SUSTAIN-6 HR 0.61, REWIND HR 0.76. Kidney FLOW HR 0.76 (0.66–0.88). Mechanisms: BP -2–5 mmHg. Compact 3000 chars, no URLs/DOI.

### 4. Grok 4.1 Expert (Thinking) — 6.7/C

Full table with 9 trials including component endpoints (CV death, MI, stroke, HHF) for each. Dense numerical data but no narrative interpretation, no source citations, no uncertainty marking. MARGINAL compliance.

### 5. Copilot Expert — 7.3/B

25,648 chars — longest response. Comprehensive sections: trial details, meta-analyses, HF outcomes (HFrEF vs HFpEF), renal, safety signals, mechanisms, guidelines, real-world evidence, network meta-analyses. Zero source citations despite enormous detail.

### 6. Cohere Command R+ Expert — 6.6/C

6 trials listed but factual error: labeled AMPLITUDE-O as tirzepatide trial (actually efpeglenatide). Missing HARMONY, ELIXA. No URLs/DOI. SELECT HR reported as 0.79 (actual: 0.80). MARGINAL compliance.

### 7. Perplexity GPT 5.1 — 7.2/B

3 structured tables (T2D trials, SELECT, SURPASS-CVOT). 92 SRCS — highest count, all inline URL citations from pmc.ncbi, wiley, diabetesjournals, tctmd, sciencedirect. Quantity over quality — URLs not DOI-verified.

### 8. Qwen3.5-Plus (Thinking) — 8.3/B

9 trials + meta-analysis + extended follow-up notes. Academic reference list: "Marso et al., NEJM 2016; Gerstein et al., Lancet 2019" — 11 numbered references with Author, Journal, Year, Pages. Mechanisms section. 4311 chars — efficient density.

### 9. Mistral Expert — 6.7/C

Shortest response (2280 chars). Missing LEADER, SUSTAIN-6, REWIND, HARMONY — core trials omitted. Focused on SELECT, meta-analysis, HFpEF. Incomplete coverage. MARGINAL compliance.

### 10. Llama 4 Maverick — 7.8/B

Semaglutide-heavy (4 of 7 entries). Included SOUL HFpEF sub-analysis (HR 0.59) and semaglutide meta-analysis (RR 0.81, 0.74–0.88). Unique: mentioned fracture risk (HR 1.11) as counterargument — boosted score. Missing HARMONY/EXSCEL/AMPLITUDE-O/ELIXA.

### Claude Sonnet 4.5 (Observed) — 6.7/C

8 trials with full component endpoints. Academic citations (Author, Journal, Year, Pages) for all trials. Sattar et al. meta-analysis (N=60,080). Safety signals: retinopathy HR 1.76 (1.11–2.78). NNT 50–60. Engine scored 0 SRCS — academic format without URLs/DOI not detected.

### Claude Haiku 4.5 (Observed) — 7.0/C

6 trials. AMPLITUDE-O with dose-dependent HR (6mg: 0.65, 4mg: 0.82). Two meta-analyses cited (N=60,080 and N=56,004). Explicit "Honest Assessment" section with limitations: absolute risk modest (1–2%), benefit greater in existing CVD, long-term durability unknown. Counterargument presence boosted score.

### Claude Sonnet 4.6 (Observed) — 7.3/B

7 trials with per-trial component endpoint tables (CV death, MI, stroke, HHF). Key findings per trial explaining what drove each result. Caveats table (HF, mechanism debate, exendin vs human GLP-1). Kristensen et al. meta-analysis cited with full HR breakdown. SELECT follow-on analyses noted. SRCS=1.

---

## Key Observations

1. **No model provided DOI identifiers.** All 12 models scored SS(v)=0. Source specificity remains the universal weakness.
2. **SRCS varies 100×** (0–92) but correlates poorly with score. Perplexity had 92 SRCS but scored 7.2; Gemini had 0 SRCS but scored 8.2.
3. **Response length uncorrelated with quality.** Copilot wrote 25K chars (7.3/B); Gemini wrote 3K chars (8.2/B).
4. **Counterargument presence** differentiates: Llama 4 (fracture risk), Haiku (limitations section), Sonnet 4.6 (caveats table) all scored higher within their clusters.
5. **Factual accuracy not measured by scoring engine.** Cohere hallucinated tirzepatide as AMPLITUDE-O drug but engine scored structural properties only.
6. **3 clear clusters:** Top tier (8.2–8.3: Qwen, GPT, DeepSeek, Gemini), Mid tier (7.2–7.8: Llama, Copilot, Perplexity), Bottom tier (6.6–6.7: Grok, Mistral, Cohere).

---

## Methodology

- New chat session per model (no prior context)
- Identical question pasted verbatim
- Full response copied to ONTO Score Any Text panel
- Original question provided in context field
- No GOLD injection — pure baseline measurement
- Scoring engine: `scoring_engine_v3.py` (993 lines, 92+ patterns, EM1–EM5 taxonomy)
- All models tested via public free-tier web interfaces
- "Expert" / "Thinking" / "Extended" modes used where available

---

## Disclaimer

This is a public experimental run measuring epistemic discipline in AI model outputs. It is not a market comparison, product ranking, or endorsement. Scores reflect structural epistemic properties of outputs (quantification density, source specificity, uncertainty marking, counterargument presence) — not factual accuracy or general capability. Models were tested via their public free-tier interfaces on a single question. Results may vary with different questions, contexts, and model versions.

---

*ONTO Standard — CS-2026-002 — Phase 2 Experimental*
