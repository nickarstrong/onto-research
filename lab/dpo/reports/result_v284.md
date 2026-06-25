# result_v284 - CANONICAL-SWAP (DECISION plane)

date: 2026-06-25
plane: v284 = canonical-swap decision (Founder-gated, DECISION; no generation/eval)
precondition: conditioned-run GREEN at 748165e (v283)
Founder ruling: SWAP sanctioned.

## SWAP (IRREVERSIBLE, single-path, verified)
canonical pool rotated: 91f442a0 -> e886bc2a (c2-migrated feed)

| artifact | md5 | note |
|---|---|---|
| o0_verdicts.jsonl (canonical, post-swap) | e886bc2a | was 91f442a0 |
| split | 176/87/97 (360 lines) | c2 gate (was 187/87/86) |
| o0_verdicts.jsonl.bak.v284pre (swap-rollback) | 91f442a0 | armed |
| o0_verdicts.jsonl.bak.v280pre (retained) | 755d81c3 | one cycle |
| o0_verdicts.jsonl.bak.20260625 (273-bak) | 9cfe3e51 | DELETED (rotated first, per ruling) |

## DISCIPLINE
- Step 0 anchors 4/4 == expected; HEAD 748165e at swap time.
- bak old canonical -> overwrite -> verify md5 == e886bc2a + lines == 360 -> delete 273.
- separation-of-planes: no generation/eval this plane.
- pool/verdicts/cand/bak = local-only; this report = md5/counts/ruling only (R15 privacy).
