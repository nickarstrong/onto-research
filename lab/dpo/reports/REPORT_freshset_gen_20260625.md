# REPORT -- FRESH HELD-OUT GEN (TYPE A) -- 2026-06-25

- type: TYPE A (Data/Code). Generate fresh blind claim set for the v4 (C-1+C-2) ff re-measure. NO eval, no verifier read.
- substrate: HEAD `1f213e6` (v4 build CLOSED). gen_heldout.py patched this session (see below).
- reason: prior held-out SPENT + TERMINAL (claims_blind_ev* / heldout_raw.jsonl consumed). Re-measure needs a disjoint fresh set.

## GENERATOR (committed -- provenance)
- `gen_heldout.py` md5 `bf130548c0140f44aad6d004268ea68b` (AST OK, pure ASCII).
- Patched from prior under SEALED STEP 1: dated NEW out-path + VIOLATION-A abort-guard (refuses to overwrite
  pre-existing state) + optional TOPIC_LIMIT arg (smoke/timing instrument). id scheme `held2_{kk}_{v}` UNCHANGED
  (downstream label/measure schema not on disk -> no guess; disjointness carried by dated filename + regenerated claims).
- input: `fresh_topics.txt` (24 topics). 2 generations / topic. model `qwen2.5-coder:7b` local (RTX 4070).

## RUN
- route: LOCAL. Smoke 6.6s/gen cold; full batch 2.1s/gen warm, 100.1s total for 48. Falsifier (>tens-of-min -> RunPod) NOT triggered.
- output: `heldout_raw_20260625.jsonl` -- 48 claims. LOCAL/gitignored (`*heldout*`), NOT committed (public set eaten by pretrains -> ruins measure).
- CONTENTS verified: 48/48 parsed, empty_claim 0, missing_fields 0, ids `held2_00_0..held2_23_1`, old set intact (not mutated).

## LABELS (Founder owns -- R7)
- Claude does NOT fabricate labels. Founder authors `sealed_labels_heldout_20260625.jsonl`, keyed by `id`
  (`founder_label` CLEAN|DIRTY ; for DIRTY `dirty_class` specifics|other). LOCAL/gitignored. Claims stay blind/reusable.

## NOT DONE (out of scope -- NEXT+1 TYPE B)
- No verifier run over the fresh set. ff re-measure partitioned per v4 falsifiers (C-1 year-only; C-2 empty-abstract ABSTAIN / non-empty DIRTY) = separate session.
- HEADROOM v4 stays DEFERRED until that re-measure PASSES.

---
*TYPE A fresh-set gen -- 2026-06-25 -- 48 claims, route LOCAL, contents-verified. Set + labels LOCAL/gitignored. Only generator + this report committed.*
