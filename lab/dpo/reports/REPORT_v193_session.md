# REPORT v193 SESSION — Track R1: Rung-1 Wiring Probe

**Date:** 2026-06-20
**Track:** R1 (Rung-1 Wiring Probe)
**Type:** TYPE C (build + verify), LOCAL, CPU + network
**Verdict:** PASS — pipeline runs without error, 15/15 claims produce ABSORB/REJECT verdicts

## Hypothesis

The end-to-end chain — proposer output → retrieval (dual-query + embedding) → s2b verifier
(B1 binding + B2 supports) → ABSORB/REJECT — runs without errors on live proposer claims.

## Method

Two-phase execution:
1. **Phase 1 (local, CPU + network):** `rung1_wiring_probe_v1.py --phase1` reads 15 claims
   from `proposals_v01b.jsonl` (V1 variant, frozen Qwen2.5-Coder-7B output). For each claim:
   dual-query retrieval (raw claim + auto-reform keywords → Crossref 10 + OpenAlex 10 each),
   embedding scoring (all-MiniLM-L6-v2, mean-pool, L2-norm, cosine similarity), best-match
   selection, s2b metadata fetch + B1 binding check (deterministic).
2. **Phase 2 (Claude Opus 4.6 as B2 judge):** frozen B2 protocol applied to each B2-pending
   item — ONLY title + abstract, no outside knowledge. Verdict: SUPPORTS / NOT / UNCLEAR.

Auto-reform query: deterministic keyword extraction (domain-agnostic stop words removed, top 10
content words). No hand-crafted queries, no model-generated reformulations.

Disposition: SUPPORTS → ABSORB ; NOT / UNCLEAR / ERROR → REJECT.

## Results

| Metric | Value |
|--------|-------|
| Claims processed | 15 |
| Pipeline errors | 0 |
| Retrieval coverage | 15/15 (100%, 0 NO_CANDIDATES) |
| Avg best cosine similarity | 0.6885 |
| B1 REJECT (wrong_binding_year) | 3 |
| B2 routed | 12 |
| B2 SUPPORTS → ABSORB | 9 |
| B2 NOT → REJECT | 2 |
| B2 UNCLEAR → REJECT | 1 |
| **Total ABSORB** | **9** |
| **Total REJECT** | **6** |

### Per-claim detail

| ID | Verdict | Leg | Reason | Disposition |
|----|---------|-----|--------|-------------|
| V1:01 | NOT | supports | off_topic (synthetic compound, not about DNA) | REJECT |
| V1:02 | SUPPORTS | supports | vaccine-induced B+T cell immune memory | ABSORB |
| V1:03 | SUPPORTS | supports | accelerating expansion addressed | ABSORB |
| V1:04 | SUPPORTS | supports | LTP synaptic plasticity + learning/memory | ABSORB |
| V1:05 | NOT | supports | ocean projections, not historical CO2 | REJECT |
| V1:06 | SUPPORTS | supports | CRISPR-Cas9 gene editing | ABSORB |
| V1:07 | NOT | binding | wrong_binding_year (claim year ≠ paper year) | REJECT |
| V1:08 | SUPPORTS | supports | Cochrane review: statins reduce CVD events | ABSORB |
| V1:09 | SUPPORTS | supports | selection pressure + antibiotic resistance | ABSORB |
| V1:10 | NOT | binding | wrong_binding_year | REJECT |
| V1:11 | SUPPORTS | supports | PD-1 inhibitors in cancer therapy | ABSORB |
| V1:12 | UNCLEAR | supports | abstract too thin for specific mechanism | REJECT |
| V1:13 | SUPPORTS | supports | rigid plates of lithosphere move | ABSORB |
| V1:14 | NOT | binding | wrong_binding_year | REJECT |
| V1:15 | SUPPORTS | supports | iPSCs from somatic cells via transcription factors | ABSORB |

## Key Findings

### 1. Pipeline runs end-to-end without errors
All 15 claims traversed: retrieval → embedding → B1 → B2 → disposition. Zero pipeline
errors, zero crashes, zero unhandled exceptions. PLUMBING PASS.

### 2. Auto-reform retrieval achieves 100% coverage
Simple keyword extraction (stop-word removal, no model) produces viable Crossref/OpenAlex
queries. 15/15 claims found candidates with abstracts. Avg best cosine similarity 0.6885
(comparable to hand-crafted reform on curated set: 0.7177).

### 3. B1 binding catches year mismatches (correct behavior)
3/15 claims contained year references (in star_quote or claim text) that did not match the
retrieved paper's publication year → B1 correctly flags wrong_binding_year → REJECT without
B2. This is the verifier WORKING: the proposer cited "X (2012)" but the best retrieved paper
is from a different year.

### 4. Diagnostic support_supply on proposer claims
B2 SUPPORTS rate on routed claims: 9/12 = 0.75. Higher than the curated test set (0.55 in
E-bis) because proposer claims are shorter, more focused, and map cleanly to well-studied
topics. This is a DIAGNOSTIC observation, NOT a gate metric (no CLEAN/DIRTY labels).

## Falsifier

The wiring probe does NOT test fa_live (the gate metric). It tests only that the pipeline
produces verdicts. The key unknown — whether the verifier passes fabrications from the live
proposer — requires Founder CLEAN/DIRTY labels on n≥30 dirty proposals (DESIGN sec 5.3).
If the wiring had FAILED (pipeline errors, crashes, no candidates), it would have blocked
the full rung-1 BUILD.

## Artifacts

- `rung1_wiring_probe_v1.py` — wiring probe script (md5 f02215d3, --phase1 + full modes)
- `eval/rung1_wiring_phase1.jsonl` — phase-1 intermediate output (retrieval + B1)
- `eval/rung1_wiring_final_v1.jsonl` — final results with B2 verdicts
- `proposals_v01b.jsonl` — input proposals (LOCAL-ONLY, bait-class)

## Next

Wiring PASS → full rung-1 BUILD is unblocked (DESIGN sec 7):
1. Generate N≥30 proposals with parseable claim+DOI from live proposer (TYPE A, GPU)
2. Founder labels CLEAN/DIRTY on each proposal (LOCAL-ONLY)
3. Run full pipeline → measure fa_live (GATE: ≤ 0.10 on dirty subset n≥30)
4. This is a SEPARATE session, not part of the wiring probe
