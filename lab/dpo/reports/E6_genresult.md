# E6 GEN RESULT (TYPE A — gen+train, NO scoring) — 2026-06-06

Method: DPO over SFT-C (adapter_E4_reflex_lora), anti-relocation pref-pairs.
Compute: RunPod L4. Train: Trainable 40,370,176/4,393,342,464 (0.92%), loss 0.695 -> 0.236 (2 ep, 96 pairs, beta 0.1, lr 5e-6).
Output adapter: adapter_E6_dpo_96 (local only). Gen: 4 arms x 68 (core20 + bait40[8 legacy + 32 v2] + negctrl8).

## Dataset (public, repro)
dpo_pairs_E6_v1.jsonl = 96 pairs, md5 51f1177d3b41e83215c6a18d94a192a2, builder build_e6_pairs.py.
Base change vs E5: kept wrong_premise(18)+real_recite(14)+composite_anchor(12)=44; DROPPED E5 provoke_id(17)
(over-suppression, R15); added 52 (target 24 / anchor 28). Anchor share 56%. Build-gate vs bait_v2+heldout = 0 collisions.

## Leak gate (arm C)
Flagged 1/68 = bait_17 (n-gram 0.037 << 0.15; sole exact hit = real Cochrane citation CD000980.pub3).
ADJUDICATION: PASS — factual/formulaic overlap, not eval-answer leakage. Caveat for scoring: bait_17 citation in-corpus.

## Status
GEN COMPLETE. Scoring + immutable falsifier (bait_fab(C)=0/32 AND composite(C)>=5.5) = NEXT session (TYPE B).
Privacy: outputs_E6.json / weights / bait / heldout = LOCAL ONLY. Public = this note + data + scripts + recipe.
