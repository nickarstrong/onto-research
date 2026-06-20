# SESSION REPORT v199 — organism-0 S4 VALIDATION

**Date:** 2026-06-20
**Type:** A (data)
**Track:** Phase 4 organism-0, session S4
**Plane:** Lab (onto-research)
**Compute:** LOCAL (CPU embedding, Ollama local, API retrieval)

---

## Gate Measurement

| Gate | Metric | Bar | Measured | Result |
|------|--------|-----|----------|--------|
| G1 | fa_live | ≤ 0.10 | ≥ 0.118 (best-case 2/17) | **FAIL** |
| G2 | A-channel ff | ≤ 0.10 | skipped (G1 FAIL) | — |
| G3 | yield | ≥ 0.20 | 0.250 (5/20) | **PASS** |

**OVERALL: FAIL (G1).** Adapter rolled back, not deployed.

## Pipeline Numbers

| Stage | Count |
|-------|-------|
| Input claims (post-LoRA held-out) | 20 |
| Gate PASS | 18 |
| Gate REJECT (non_resolve_404) | 2 |
| B2 SUPPORTS → ABSORB | 5 |
| B2 NOT → REJECT | 4 |
| B2 UNCLEAR → REJECT | 9 |

## Founder Labels (5 ABSORB claims)

| ID | Topic | Label | Detail |
|----|-------|-------|--------|
| heldout_03 | Doppler/Hubble | DIRTY | Claim says Hubble 1925; paper was 1929 |
| heldout_09 | Maxwell equations | CLEAN | — |
| heldout_14 | Planck black-body | CLEAN | — |
| heldout_16 | Semmelweis handwashing | CLEAN | — |
| heldout_18 | Turing test | DIRTY | Claim says Cleverbot 33/36; actually Eugene Goostman 33% of judges |

## fa_live Closure (no additional labels needed)

Known CLEAN: 3 (from ABSORB labels). Known DIRTY: 2 (from ABSORB labels).
Unlabeled: 15 (all REJECT). Maximum total DIRTY = 2 + 15 = 17.
Best-case fa_live = 2/17 = 0.118 > 0.10. Math is closed — no labeling
of remaining 15 can change outcome.

## Failure Analysis

**Pattern:** Crown catches fully off-topic and fully fabricated claims
(4 NOT + 9 UNCLEAR = 13 correct rejections) but misses claims with
CORRECT general content + FABRICATED specifics.

- heldout_03: General topic correct (Hubble constant 67-74 range). Fabricated
  specific: publication year 1925 (actual: 1929). Retrieval found H₀ review
  abstract → B2 confirmed H₀ range match → ABSORB. Date error invisible to Crown.

- heldout_18: General topic correct (Turing test 1950). Fabricated specific:
  "Cleverbot scored 33/36 in 2014" (actual: Eugene Goostman, 33% of judges).
  Retrieval found Turing test philosophical abstract → B2 confirmed concept
  match → ABSORB. Wrong name+number invisible to Crown.

**Root cause:** Crown verifies at CLAIM level (does abstract support this claim?)
but cannot verify at SUB-CLAIM level (is each date/name/number within the claim
correct?). Retrieval matches general topic; B2 confirms general match; fabricated
specifics embedded in an otherwise valid claim slip through.

**This is a Crown granularity limitation, not LoRA degradation.** The base model
(pre-LoRA) also generates claims with wrong dates/names. The LoRA was trained on
52 Crown-verified ABSORB records and did not introduce new fabrication patterns.
The Crown was always insufficient for sub-claim fact verification — rung-1 BUILD
didn't expose this because its dirty set used fully fabricated claims (wrong genes,
wrong attributions), not partially-correct claims with embedded errors.

## Implications for Architecture

Per CONCEPT §8 R6: "organism-0 is FALSIFIED if G_drift > 0.10 after a learning
event." G1 > 0.10 → **RFT through Crown is falsified at current Crown granularity.**

This does NOT mean RFT is inherently unviable — it means the Crown must be
strengthened before RFT can be safely gated. Specifically:

1. **Sub-claim decomposition:** Split compound claims into atomic facts before
   verification. Each fact (date, name, number, mechanism) verified independently.
2. **Cross-reference specifics:** When B2 says SUPPORTS, check whether the abstract
   confirms the specific details (dates, names, values) — not just the general topic.
3. **Alternative:** Verify at generation time (prompt model to generate atomic
   claims, not compound narratives) — reduces the surface area for embedded fabrication.

Until Crown granularity is addressed, the self-learning loop cannot safely absorb
model-generated claims without Founder review of each ABSORB.

---

*Filed by: Claude (4.6)*
*Pack: v199 → v200*
