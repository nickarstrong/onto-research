# EXPERIMENT E3 · Domain Coverage Matrix

**Date:** 2026-04-26 (queued)
**Operator:** Tommy
**Lab build:** /lab/ v3 · backend `engine_version: 5.1.1`
**Purpose:** Test whether GOLD effect (Δ +3.4 to +5.0 in baseline_001) generalizes beyond the medical/empirical domain.
**Status:** open · ready to run

---

## 1 · Hypothesis

**H_main:** Δ Grade (GOLD - RAW) is positive and ≥ +2.0 across all 5 domains.
**H_null:** Δ ≤ 0 in at least one non-empirical domain (would indicate GOLD only disciplines fact-anchored prompts).

If H_null holds for any domain — that's a finding too. We log it · do not bury it.

---

## 2 · Design

5 prompts × 6 models × 1 run each = 30 VS comparisons.
Each VS = 2 backend calls (RAW + GOLD parallel).
Total backend calls: 60.

**Same model panel as baseline_001:**
- Qwen2.5-7B-Instruct (Q4_K_M)
- Qwen2.5-14B-Instruct (Q4_K_M)
- DeepSeek-R1-7B
- DeepSeek-R1-14B
- Phi-4-14B (Q4_K_M)
- Gemma2-9B-Instruct (Q4_K_M)
- Mistral-7B-Instruct (Q4_K_M)

(Note: 7 models in current /lab/ selector. baseline_001 used 6. Decision: include Mistral since calibration_001 closed.)

---

## 3 · Prompts (5 domains)

### D1 · Medicine (control · already in baseline_001)

```
What does research say about coffee health benefits?
```

Reuse for variance check across runs.

### D2 · Policy

```
What are the documented effects of universal basic income pilots
on employment and wellbeing?
```

Empirical, but politically charged. Tests whether GOLD discipline
holds when the model has incentive to be vague.

### D3 · Finance

```
What is the historical performance of value investing versus
growth investing over the last 30 years?
```

Quantifiable. Tests R1 (numbers) under a domain where models often
hedge with platitudes.

### D4 · History

```
What were the main causes of the 2008 financial crisis?
```

Multi-causal. Tests R3 (counter-arguments) — does the model present
multiple schools of interpretation, or settle for one narrative?

### D5 · Math reasoning

```
A coin is flipped 10 times. What is the probability of getting
exactly 7 heads? Show your work.
```

Closed-form correct answer exists (≈ 0.117 or 15/128). Tests whether
GOLD adds rigour without breaking correctness. R7 (no fabrication)
penalty should fire if model produces wrong numerical answer.

---

## 4 · Procedure

For each (model, prompt) pair:

1. Open `/lab/` · select model in header dropdown
2. Set Mode = Agent (faster, fewer 14B timeouts)
3. Paste prompt
4. Click VS · wait for both panels
5. Capture screenshot
6. Record in matrix: `(domain, model, raw_grade, gold_grade, delta, raw_R1-R7, gold_R1-R7, fabrication_suspected, latency)`

If a 14B model times out >300s, retry once · if still timeout, mark as `TO` and continue.

If `fabrication_suspected = True` (whitelist caught a fake DOI), log it explicitly. We expect Mistral may trigger this on history/policy domains.

---

## 5 · Output

Single file: `lab/E3_domain_matrix.md`

Format: 5 sections (one per domain) · each containing 7-row table:

```
## D2 · Policy

| Model | RAW | GOLD | Δ | RAW bars | GOLD bars | Fab? | Lat |
|---|---|---|---|---|---|---|---|
| Qwen-7B  | F 1.8 | C 6.2 | +4.4 | R1=0 R2=0 ... | R1=15 R2=100 ... | – | 28s |
| Qwen-14B | F 1.5 | C 5.9 | +4.4 | ... | ... | – | 220s |
| ...
```

Plus a summary at top: mean Δ per domain, fabrication-suspected count, timeouts.

---

## 6 · Stopping conditions

- Run completes 30/30 → finalize matrix, write conclusions, queue baseline rev3 if needed.
- 5+ timeouts on 14B → drop 14B from matrix, note in caveats, run only 5 models × 5 domains = 25.
- `fabrication_suspected` triggered ≥ 3× on same model in different domains → document as a model-level finding (not a one-shot exploit).

---

## 7 · Acceptance for E3 closure

E3 closes when:
1. Matrix complete (or timeout-trimmed with explicit note).
2. Per-domain mean Δ computed.
3. H_main / H_null verdict written.
4. New backlog items (if any) registered as `calibration_002`, `calibration_003`, etc.
5. `baseline_001` references E3 in §6 as DONE.

---

## 8 · Estimated effort

- Per VS run: 30s-3min (model-dependent · 14B slower)
- 30 runs total: ~60-90 min wallclock if sequential
- Screenshotting + transcription: another 30 min
- Total: ~2-2.5 hours of one operator session

Recommended split: do D1-D3 first session (15 runs · validates protocol on familiar territory), D4-D5 second session.

---

*Queued. Ready to start when operator gives go.*
