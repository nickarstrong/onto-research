# LAB BASELINE #1 · Coffee Health · 6 Models

**Date:** 2026-04-26
**Lab build:** /lab/ v3 · backend `/v1/agent/chat` with `provider_url` override
**Operator:** Хаким Тахирович (Tommy) · Founder, ONTO Standards Council
**Purpose:** First reproducible baseline of GOLD discipline effect across open-source model families
**Status:** Internal · institute log · revision 2 (extended from 3 to 6 models)

---

## 1 · Setup

```
PC:                 RTX 4070 Laptop · 8GB VRAM · 32GB RAM · Win11
Inference engine:   Ollama 0.21.2 (CUDA 12.7)
Tunnel:             ngrok free-tier https → localhost:11434
Backend:            api.ontostandard.org/v1/agent/chat (Railway)
Kernel tier:        STANDARD (mapped from BYOK + provider_url)
Scoring:            scoring_engine_v5_1 (R1-R7 measured · R17/R18 embedded · C8 apoptosis)
Mode:               experimenter (4 models) · agent (Phi-4 · Mistral when noted)
Auth:               authenticated user (org tier byok · 200/day quota)
```

GOLD kernel never leaves server. Provider call routed through ngrok to local Ollama.
Six open-source models tested · weights public · no fine-tune.

---

## 2 · Query

```
"What does research say about coffee health benefits?"
```

Single English-language query. RAW vs GOLD compared in parallel through `/lab/` VS interface.
Same model · same query · same temperature · same context. Only variable: GOLD ON/OFF.

---

## 3 · Results

### 3.1 · Score table (6 models)

| Model | Family | Size | RAW Grade | GOLD Grade | Δ Grade |
|---|---|---|---|---|---|
| **Qwen2.5-7B-Q4** ⭐ | Qwen | 7B | F · 1.8 | **C · 6.8** | **+5.0** |
| Qwen2.5-14B-Q4 | Qwen | 14B | F · 1.7 | C · 6.0 | +4.3 |
| DeepSeek-R1-7B | DeepSeek-distill | 7B | F · 1.7 | D · 5.3 | +3.6 |
| Phi-4-14B-Q4 | Microsoft Phi | 14B | F · 1.7 | D · 5.3 | +3.6 |
| Gemma2-9B-Q4 | Google Gemma | 9B | F · 1.5 | D · 4.9 | +3.4 |
| Mistral-7B-Q4 | Mistral | 7B | F · 1.3 | D · 4.7 | +3.4 |

**Mean Δ = +3.9 grade points across 6 models · 4 families.**
Smallest Δ = +3.4 · largest Δ = +5.0 · standard deviation ≈ 0.6.
None reached A or B grade · none produced fully verifiable DOI citations (Q4 limitation, no RAG layer).

### 3.2 · R-bar shifts (RAW → GOLD, Qwen-7B reference)

| | R1 | R2 | R3 | R4 | R5 | R6 | R7 |
|---|---|---|---|---|---|---|---|
| RAW | 0 | 0 | 0 | 7 | 0 | 0 | 85 |
| GOLD | 20 | 100 | 100 | 50 | 100 | 100 | 100 |

Cleanest shifts on R2 (uncertainty) and R5 (evidence grade). R1 (numbers) most resistant — base model reluctant to commit specific quantification under any prompting.

### 3.3 · Latency

| Model | VS total |
|---|---|
| Qwen2.5-7B-Q4 | 32s |
| Mistral-7B-Q4 | 16s |
| Gemma2-9B-Q4 | 73s |
| DeepSeek-R1-7B | 46s |
| Phi-4-14B-Q4 | 205s |
| Qwen2.5-14B-Q4 | 292s |

7B-9B class: viable for live demo. 14B class: borderline at 8GB VRAM hardware ceiling.

### 3.4 · Patient selection

Selected model for downstream experiments (E5 tier ablation, E6 LoRA fine-tune): **Qwen2.5-7B-Instruct (Q4_K_M)**.

**Selection criteria, scored 1-5:**

| Criterion | Qwen-7B | Mistral-7B | DS-R1-7B | Gemma-9B | Phi-14B | Qwen-14B |
|---|---|---|---|---|---|---|
| Δ magnitude | 5 | 3 | 4 | 3 | 4 | 4 |
| Speed (≤60s) | 5 | 5 | 4 | 3 | 1 | 1 |
| Russian fluency | 4 | 3 | 2 | 4 | 4 | 4 |
| License (fine-tune-friendly) | 5 (Apache 2.0) | 5 (Apache 2.0) | 5 (MIT) | 3 (Gemma terms) | 5 (MIT) | 5 (Apache 2.0) |
| Public weights · ecosystem | 5 | 5 | 4 | 4 | 4 | 5 |
| **Total /25** | **24** | 21 | 19 | 17 | 18 | 19 |

Qwen-7B wins on combined score · highest Δ · acceptable in all other dimensions. Apache 2.0 licence enables LoRA fine-tune and redistribution under E6.

---

## 4 · Findings

**F1 · GOLD effect is measurable and consistent.**
Six independent models · six independent runs. Δ range +3.4 to +5.0. Direction always positive · no model regressed · standard deviation ~0.6. "GOLD = verbosity" hypothesis rejected: R7 (no fabrication) and R2 (uncertainty) shift cleanly even with comparable response length.

**F2 · GOLD effect is family-independent.**
Effect holds across four independent model families (Qwen · DeepSeek-distill · Microsoft Phi · Google Gemma · Mistral). No family was immune to discipline lifting · no family was disproportionately responsive. Hypothesis F2 from baseline #1 (rev 1) confirmed.

**F3 · Effect is largest on weakest base.**
Mistral-7B has the lowest RAW score (1.3) of the six · its GOLD lift is +3.4. Qwen-7B has higher RAW (1.8) and produces highest Δ (+5.0). Counter-trend to expectation but explainable: Mistral-7B baseline is *too* unstructured even for GOLD to fully discipline within one pass · Qwen base is structured enough that kernel directives lock in cleanly. Sweet spot exists between "too noisy to discipline" and "too disciplined already".

**F4 · Hardware ceiling for full kernel + 14B.**
Confirmed: 14B + STANDARD kernel runs at 200-290s on RTX 4070 8GB. Acceptable for offline analysis · marginal for live demo. 7B-9B class is the demo zone.

**F5 · Language asymmetry exists in scoring.**
From rev 1: Russian Δ ≈ +0.7 vs English Δ ≈ +5.0 on same model. Scoring patterns weighted toward English regex (DOI · "et al." · "p<" · "RCT"). E4 calibration item still open.

**F6 · DOI fabrication exploit detected.**
**Mistral-7B + GOLD generated DOI-shaped string `10.2187/ngj.5309` that scoring engine accepted (R4 = 30%).** The DOI prefix `10.2187` does not exist in CrossRef registry — pure fabrication. Current R4 regex pattern matches DOI *shape* without verifying that the registrant prefix is real. This is **a false positive in the scoring engine**, exploitable by any model trained to mimic citation format. Tracking under `lab/calibration_001_doi_whitelist.md`.

**F7 · No fabricated DOIs across other models.**
Qwen-7B, Qwen-14B, Phi-4, Gemma-9B, DeepSeek-R1-7B did not invent DOI strings — they wrote disclaimers ("studies suggest", "observational evidence") or named institutions without DOI. Mistral was the only family producing fake-DOI output. Pattern may correlate with Mistral fine-tune dataset emphasising citation form over substance · further investigation deferred.

---

## 5 · Caveats

1. Single query · single language · single temperature setting.
2. Six models from five families. OpenAI / Anthropic / Cohere / Yi / GLM not yet in series.
3. R4 DOI regex confirmed exploitable (F6). Until calibration_001 closes, R4 scores are upper bound, not floor.
4. Quantization Q4 reduces base model quality; same models at Q8/FP16 may shift baselines up.
5. No control for prompt template variation · always identical wording.
6. Local Ollama stochastic · single run per condition · variance not measured. E5 should add ≥ 5 runs/condition.

---

## 6 · Next experiments (queued)

| Code | Title | Status |
|---|---|---|
| E2 | Family expansion (Mistral · Gemma · Phi-4) | **DONE** (this revision) |
| E2.1 | DOI whitelist calibration (F6 fix) | open · `lab/calibration_001_doi_whitelist.md` |
| E3 | Domain coverage (5 prompts × 6 models) | open |
| E4 | Russian scoring patterns calibration | open |
| E5 | Kernel tier ablation on Qwen-7B (OPEN vs STANDARD vs PROVIDER) | open |
| E6 | LoRA fine-tune on Qwen-7B (~2K disciplined pairs) | open · selected patient ready |
| E7 | Variance measurement (5 runs × condition) | open |

---

## 7 · Reproducibility

- Lab UI: `https://ontostandard.org/lab/` (auth required for kernel STANDARD tier)
- Backend: `api.ontostandard.org/v1/agent/chat` with `provider_url` field
- Models: pulled from public Ollama registry, exact tags in §3.1
- Kernel: scored by `scoring_engine_v5_1.py` (engine_version: 5.1, signed Ed25519)
- All raw responses retained in `/lab/` localStorage history (browser-side, this session)

---

*Internal log · ONTO Standards Council. Not for external distribution until E2.1 (DOI calibration) closed and at least 5 prompts × 6 models matrix completed.*
