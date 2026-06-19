# REPORT v189 SESSION — Track C: Model-Generated Claims + Reformulation Probe
**Date:** 2026-06-20
**Pack:** v189
**Type:** TYPE A (code + measure), LOCAL, CPU + network
**Plane:** Source Crown truth-half — retrieval channel on realistic model output

## Track C: Model-Generated Claims through Retrieval Pipeline

### Objective
Test retrieval channel on MODEL-GENERATED claims (not hand-written).
Prior result: v188 Track B = 13/20 SUPPORTS (0.65) on hand-written claims.

### Method
1. **Claim generation:** Qwen-coder:7b via ollama, 20 diverse prompts, system prompt
   requesting specific factual claims with numbers/dates. temp=0.3, num_predict=256.
   Output: 20/20 non-empty, 111s total.
2. **Retrieval:** retrieval_proposer_v1.py --claims (Crossref + OpenAlex, pick_best
   by longest abstract). 20/20 matched, 16/20 with abstract.
3. **B2 verification:** Claude 4.6 inline (same as s2b B2_MODEL_DEFAULT), strict
   title+abstract only.

### Results
- SUPPORTS: 3/16 (mc03 Mpemba, mc07 universe age, mc09 dopamine)
- NOT SUPPORTED: 12/16 (ALL retrieval mismatches — wrong paper found)
- UNCLEAR: 1/16 (mc17 quantum error correction)
- SKIP (no abstract): 4/20

**support_supply = 3/16 = 0.1875**

### Root Cause
Model-generated claims are generic/textbook ("Metformin lowers glucose production").
Keyword search matches thematically related but non-supporting papers (dairy fat study
instead of metformin mechanism). Hand-written claims in v188 were more specific → higher
keyword match precision.

---

## Track C-bis: Query Reformulation Probe

### Objective
Test whether targeted search queries (claim → 6-8 keywords) improve retrieval for
the 12 NOT-supported claims.

### Method
Manual reformulation of 12 queries (e.g., "metformin mechanism hepatic glucose
production insulin sensitivity" instead of full claim text). Same retrieval pipeline.

### Results — Retrieval
12/12 matched with abstracts (was 0/12 relevant matches with raw claims).

### Results — B2 Verification
- FLIPPED to SUPPORTS: 4 (mc04 PM2.5 cardiovascular, mc08 Cas13 diagnostic,
  mc10 dark matter rotation curves, mc11 OTEC mechanism)
- Remain NOT: 7 (mc02 metformin, mc05 Higgs, mc06 mRNA 95%, mc12 Arctic ice rate,
  mc14 lithium, mc18 glyphosate, mc19 Hubble constant)
- FLIPPED to UNCLEAR: 1 (mc00 C-14 half-life)

### Combined Track C Result (all 20 claims)
| Metric | Raw | + Reformulation |
|--------|-----|-----------------|
| SUPPORTS | 3/16 | 7/16 |
| support_supply | 0.1875 | 0.4375 |
| Δ | — | +0.25 (×2.3) |

### Remaining 7 NOT — Failure Taxonomy
1. **Keyword confusion** (2): mc02 metformin vs general insulin studies, mc14 lithium
   vs valproate — shared medical terminology confounds keyword search
2. **Landmark vs derivative** (2): mc05 Higgs discovery gets analysis paper, mc06
   original 95% trial gets Omicron-era effectiveness study
3. **Number mismatch** (2): mc12 claims 12.8%/decade but paper says 4%/decade (different
   era), mc19 claims H₀=74 but Planck says 67.4 (Hubble tension — retrieval found the
   other measurement)
4. **Topic dilution** (1): mc18 glyphosate gets general EDC review

### Architectural Conclusions
1. Query reformulation = working lever for retrieval improvement (0.19 → 0.44)
2. Remaining failures require semantic relevance scoring, not keyword optimization
3. Verifier works correctly throughout — rejects non-supporting papers, including
   thematically related ones and papers with contradicting numbers
4. For production Source Crown: retrieval needs (a) automated query reformulation
   and (b) semantic scoring layer

---

## Artifacts Produced
- generate_model_claims_v1.py (claim generator via ollama)
- retrieval_reformulation_probe.py (reformulation probe, 12 targeted queries)
- model_claims_v1.jsonl (20 model-generated claims)
- retrieval_results_v1.jsonl (Track C retrieval matches)
- retrieval_reformulated_v1.jsonl (reformulated retrieval matches)

## Banked Findings (do not redo)
- Model-generated claims: support_supply = 0.19 raw, 0.44 reformulated
- Query reformulation viable (×2.3 improvement)
- Remaining 7 NOT cases = structural (keyword confusion, landmark vs derivative,
  number mismatch, topic dilution) — need semantic scoring
- Verifier (s2b B2) works correctly on model-generated claims — bottleneck is retrieval

---
*v189 · 2026-06-20*
