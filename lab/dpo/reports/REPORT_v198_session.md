# SESSION REPORT v198 — organism-0 S3 BUILD

**Date:** 2026-06-20
**Type:** C (build)
**Track:** Phase 4 organism-0, session S3
**Plane:** Lab (onto-research)
**Compute:** RunPod A5000 24GB

---

## Deliverables

### 1. o0_learner.py (RFT LoRA learner)
3-mode CLI: --extract, --train, --generate. Verified on RunPod.
Fixes applied during RunPod run:
  - `total_mem` → `total_memory` (torch API)
  - `tokenizer=` → `processing_class=` (trl >= 0.15 API)
  - `max_seq_length` removed from SFTTrainer (moved to SFTConfig internally)
  - encoding="utf-8" on all open() calls (Windows cp1251 fix)

### 2. data/o0_sft_absorb.jsonl (SFT training data)
Extracted from o0_verdicts.jsonl (verdict trail, NOT o0_enriched.jsonl).
o0_enriched.jsonl has PENDING_B2 — verdicts live in trail only.

| Metric | Value |
|--------|-------|
| Trail records | 212 (duplicates from 2 integrate runs) |
| After ID dedup | 112 |
| ABSORB (unique) | 52 |
| Empty claims | 0 |
| Avg completion length | 135.5 words |

Prompt = exact copy of rung1_wiring_v0.py generate_claim() (lines 75-78).
No system prompt (matches Ollama /api/generate).

### 3. LoRA Training

| Param | Value | Ceiling |
|-------|-------|---------|
| r | 8 | ≤ 8 ✓ |
| alpha | 16 | 2×r ✓ |
| LR | 5e-6 | ≤ 5e-6 ✓ |
| epochs | 1 | ≤ 1 ✓ |
| dropout | 0.05 | — |
| targets | q,k,v,o_proj | — |
| merge | NO | — |

| Metric | Value |
|--------|-------|
| Training loss | 1.725 |
| Steps | 13 (52 / batch 4) |
| Time | 17.1s |
| Grad norm | 0.20-0.27 (stable) |
| Token accuracy | ~66% |
| Adapter size | 9.7 MB |

All fix(b) ceilings held. Adapter separable (adapter_model.safetensors only).

### 4. Post-LoRA Generation (held-out)

| Metric | Value |
|--------|-------|
| Topics generated | 20/20 |
| Non-empty | 20/20 |
| Avg claim length | 147.4 words |
| Unique topics | 20 |
| LoRA active | verified (anti silent-base guard) |

## Verification Chain

1. Extract: 212 trail → 112 dedup → 52 ABSORB → 52 SFT records
2. Train: bounds asserted → 4-bit load → LoRA → 13 steps → adapter saved
3. Generate: base+adapter loaded → LoRA active verified → 20 greedy claims
4. All artifacts byte-verified after RunPod download

## Key Findings

- **Verdict trail is the data source, not enriched file.** o0_enriched.jsonl retains
  PENDING_B2 after accumulator integration — verdicts live in o0_verdicts.jsonl only.
  The learner reads from the trail with ID-based dedup.
- **Qwen tokenizer inserts default system prompt** ("You are Qwen...") via chat template
  even when no system message specified. This matches Ollama behavior (Modelfile SYSTEM).
  Training-inference consistency maintained.
- **trl API moved fast.** Three patches needed for RunPod's trl version (processing_class,
  max_seq_length, total_memory). Canonical script carries all fixes.

---

*Filed by: Claude (4.6)*
*Pack: v198 → v199*
