# REPORT: v188 Session — CL Crown Filter + Source Retrieval

## Track A Phase 2: BPW-as-Filter — CLOSED (FAIL)

**Hypothesis:** R18 linguistic prompt can be replaced by BPW filtering (generate N=5 bare, keep top-1 by lowest BPW, compare to R18-prompted output).

**Substrate:** Qwen-coder:7b via ollama (42 tok/s). Gemma E4B attempted first but unusable (see below).

### Gemma E4B Thinking Mode Finding

Gemma 4 E4B produces 78% empty bare outputs (0 words) without a system prompt at temp=0.7. With R18 system prompt: 80% non-empty. Root cause: thinking mode consumes the generation budget on internal reasoning tokens. Increasing `num_predict` from 512 to 4096 did not resolve — the model still exhausts budget on thinking.

**Implication for Crown:** thinking-mode substrates REQUIRE a minimal anchor prompt (system prompt) to produce visible output. The planned ~500 tok kernel (identity + R8 + R13) serves this function. R18 replaceability is a separate question from generation stability.

### BPW Filter Results (Qwen-coder:7b)

- 10 prompts × 5 bare (temp=0.7) → top-1 by lowest BPW → vs 1 R18-prompted (temp=0.7)
- BPW comparison: filtered BPW <= prompted BPW in 10/10 (expected: filtered outputs longer → better gzip compression → lower BPW, partly a length artifact)
- **Blinded discipline eval (Claude as judge):**
  - Prompted wins: 6 (filtered outputs contained filler: "It's important to note that", "Overall, while X...", intro padding)
  - Filtered wins: 0
  - Ties: 4
  - Effective rate: 0.20 → **FAIL**

### Root Cause

BPW measures COMPRESSION EFFICIENCY (lexical diversity, gzip compressibility), NOT DISCIPLINE (filler removal, hedge removal). A long text with varied vocabulary compresses well (low BPW) but can still contain filler and factual errors. R18 targets specific semantic patterns (empty hedges, unnecessary qualifications) that BPW does not detect.

### Banked

- BPW = valid DETECTOR of discipline (20/20 pair discrimination, Step 1) but NOT a valid ENFORCER
- BPW as pre-screen: can reject obviously bloated outputs, but discipline = separate mechanism
- Mathematical R18 replacement requires formalizing SPECIFIC patterns (filler markers, hedge detection), not generic compression
- Gemma E4B thinking mode: needs anchor prompt for bare generation stability

---

## Track B: Source Retrieval — CLOSED (VIABLE)

**Hypothesis:** retrieval-grounded locator channel produces >0 verifier-SUPPORTED (claim, real_source) pairs.

### Step 1: Retrieval

- 20 embedded factual claims (model-like, diverse domains)
- Search: Crossref + OpenAlex APIs (free, no auth)
- Selection: best match by longest abstract
- Result: 20/20 matched with abstracts

### Step 2: B2 Supports Verification

- Verifier: Claude (same model as s2b `B2_MODEL_DEFAULT = claude-sonnet-4-6`)
- Prompt: exact B2_SYS from frozen s2b_v0.py
- Method: ONLY title + abstract, no outside knowledge

**Results:**

| Verdict | Count | IDs |
|---------|-------|-----|
| SUPPORTS | 13 | c01,c02,c03,c05,c06,c07,c10,c11,c12,c15,c16,c18,c19 |
| NOT | 6 | c00,c04,c08,c09,c13,c17 |
| UNCLEAR | 1 | c14 |

**support_supply = 13/20 = 0.65 → VIABLE (>0)**

### Analysis of NOT Cases

All 6 NOT cases are RETRIEVAL mismatches, not verifier errors:
- c00: diet type comparison ≠ intermittent fasting
- c04: quantum repeater theory ≠ 1000 km demonstration
- c08: microplastic health review ≠ blood samples finding
- c09: time-series forecasting ≠ NLP
- c13: sodium-ion batteries ≠ lithium-ion degradation
- c17: atmospheric brown carbon ≠ solar panels

Root cause: `pick_best` selects by longest abstract, not relevance. Title-similarity scoring would improve retrieval precision.

### Falsifier

support_supply = 0 on N≥20 with improved retrieval (relevance scoring) → channel dead.

### Banked

- Retrieval channel WORKS: claim → Crossref/OpenAlex search → DOI + abstract → s2b SUPPORTS
- Even with naive keyword search + longest-abstract selection, 65% supply
- Retrieval quality improvable: relevance scoring > longest abstract
- Both Crown halves now have working components: form = R18 prompt, truth = retrieval + verifier

---

## Architecture Status Post-Session

```
Substrate (Qwen-coder primary, Gemma E4B needs anchor prompt)
    ↓ generates freely
CL Crown (form-half)
    R18 prompt = WORKS (not yet externalized as code)
    BPW = DETECTOR only (20/20), not enforcer
    Next: filler-pattern detection as code-based R18
    ↓
Source Crown (truth-half)
    Retrieval = VIABLE (13/20 SUPPORTS)
    Verifier = FROZEN, working
    Next: model-generated claims, relevance scoring
    ↓
GOLD Core = proof depot + personality foundation
```

---

*v188 session · 2026-06-20*
*Scripts: cl_crown_filter_v1.py, retrieval_proposer_v1.py, retrieval_dispose_v1.py*
*Git HEAD pre-session: a20b117*
