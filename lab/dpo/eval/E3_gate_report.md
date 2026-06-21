# E3 — P5_refusal_on_unknown · build + gate report

**Session:** E3 (TYPE A — data only, no eval, no training)
**Closed:** stage E3.1
**Source of truth:** ONTO_SESSION_PACK_v10 + uploaded sft_P5_refusal_draft.jsonl

## Input
- Draft: 24 pairs (`sft_P5_refusal_draft.jsonl`).
- Locked sets (untouched): `sft_reflex_236.jsonl` (236), `heldout_v1.3.jsonl` (36).

## Audit (E3.0)
- Schema match (instruction/output/category): PASS.
- New category `P5_refusal_on_unknown`, distinct from P3/P4/P1: PASS.
- Intra-draft dup: 0.
- **Contamination FAIL:** draft#6 (turmeric/OA "exact 95% CI from latest meta-analysis") = structural twin of held-out `bait_07` (saffron/PMS, same template) → dropped.

## Build (E3.1)
- Dropped 1 contaminated draft pair → 23 clean kept.
- Recast #6 off the CI/meta-analysis template → odds-ratio frame (no heldout twin).
- Authored 36 new pairs across diverse fabrication-trap classes:
  - fake-entity (no verifiable record) · wrong-premise (false "single value"/"first") · real-but-recite-trap (false precision on real constants).
  - refusal spectrum varied on purpose: pure "no record", labelled honest range (R8), reject-premise + verified pointer (R4), compute-at-source.
- **Total P5 = 59** (target band 50–70).

## Gate (full 59-pair block)
| check | result |
|---|---|
| intra-dup questions | 0 |
| 7-gram contamination vs heldout_v1.3 | 0 |
| 7-gram echo vs reflex_236 outputs | 0 |
| R7 fabricated-specifics scan (DOI/p-value/CI/rsID/RFC) | 1 flag → reviewed, by-design (real caveated RFC pointer), 0 real |

## Output
- `sft_P5_refusal_v1.jsonl` — 59 P5 pairs (gated).
- `sft_reflex_295.jsonl` — combined training set = 236 reflex + 59 P5.
  - P3_discipline_format 162 · P4_conversational_style 40 · P1_method_recast 34 · P5_refusal_on_unknown 59.

## Falsifier (carried from E2 → E3 verdict, NOT run here)
If after retraining on the 295-set bait_fab(C) does NOT drop ≤10% at composite ≥5.5 → problem is deeper than the data hole; reconsider method, not corpus.

## Manual (Tommy)
- `ONTO_STRATEGIC_MAP.md` Research→NEXT: "E3 P5 block built (59), gated clean; ready for retrain on sft_reflex_295."
- git: commit `data/sft_P5_refusal_v1.jsonl` + `data/sft_reflex_295.jsonl` + this report. Adapters/weights — not.

## NOT done in E3 (stage discipline)
- No training (Kaggle/Colab, Tommy side).
- No eval / onto_eval run (that's the eval stage after retrain).
- heldout_v1.3 / sft_reflex_236 untouched.
