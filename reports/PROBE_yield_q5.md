# PROBE_yield_q5 — effective-positive-yield vs abstain-rate (Q5)

Durable home for the yield-collapse reframe (promoted from baton IDEA-TILE-3) and the
v277 empirical probe that gated the C-2 pool swap.

## 1. Reframe (keeper)
Conditioning collapse is governed by effective positive yield — absolute CONFIRM-mass
absorbed into substrate per cycle — not by ABSTAIN-rate %.

Counterexample: at a fixed 80% abstain rate, a pool emitting 100 CONFIRM/cycle is alive;
one emitting 1 CONFIRM/cycle is dead. Same rate, opposite health.
- H0: abstain-rate decides collapse.
- H1: absolute yield decides collapse.  <- prior weight here.

Probe measures confirmed_mass + pool diversity (lexical entropy, topic spread), never abstain%.
Failure modes at conditioning: rejection-sampling mode-collapse; reward-hacking-via-abstention.

## 2. v277 probe result (static, LOCAL CPU)
Sealed Step-0 gate (falsifier-first, Founder-owned, sealed before any number read):
- G1 MASS: candidate confirmed_mass >= 150 (absolute, not %).
- G2 DIVERSITY: retention >= 0.85 of source (binding = lowest component).

| metric              | source | candidate | retention |
|---------------------|--------|-----------|-----------|
| confirmed_mass      | 273    | 187       | n/a (abs) |
| lexical entropy     | 9.619  | 9.561     | 0.994     |
| topic-dist entropy  | 6.614  | 6.418     | 0.970     |
| distinct topics     | 104    | 93        | 0.894     |
| vocab size          | 3553   | 3110      | 0.875     |

Candidate split: ABSORB 187 / ABSTAIN 86 / REJECT 87. The 86 quarantined are the
fabricated-specifics that leaked into train-positive — removal is the swap goal, not loss;
187 is a clean count, not "68% survivors".

- G1: 187 >= 150 -> PASS (+37 headroom).
- G2: binding vocab_size 0.875 >= 0.85 -> PASS (thin, +0.0025); 11 topics dropped (104->93),
  consistent with fabrications being topic-clustered.

VERDICT: HOLDS -> swap grounded-YES. Executed: source 273 (9cfe3e51) backed up;
canonical o0_verdicts.jsonl re-pointed to candidate 187 (755d81c3).

Recovery note (not a blocker): if recall-recovery is later pursued, target the 11 dropped topics.

## 3. Prior art (IDs self-verified)
- Gao, Schulman, Hilton — Scaling Laws for Reward Model Overoptimization, arXiv:2210.10760.
- DAA overoptimization — arXiv:2406.02900 (NeurIPS 2024).
- LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking — arXiv:2604.15149 (2026):
  direct hit on the table-catch-vs-generalization carry-over.
- STaR — Zelikman 2022; model collapse — Shumailov et al., Nature 2024 (cited, not fetched).
