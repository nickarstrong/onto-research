# GATE_selflearn HEADROOM baseline v3 -- VERDICT: FAIL (STOP)

date: 2026-06-24
session: v260 (TYPE C run, HEAD 4046087)
substrate: qwen2.5-coder:7b (RTX 4070, LOCAL, oracle-bound network I/O)
method: blind pass (conditioned=False -> proposer retrieval OFF), --hard-topics ON, n=8 x 5 ticks = 40 hard claims

## Result
- blind rate_f per tick: [0.125, 0.0, 0.375, 0.125, 0.0]
- blind rate_f (mean): 0.125
- HEADROOM bar (P2, BINDING): rate_f >~ 0.30
- VERDICT: 0.125 < 0.30 -> FAIL

## Integrity (trace `topics` field = authority, not console header)
- topic source: 24/24 unique, subset(HARD_TOPICS)=True, stray=0 -> P1 --hard-topics threading PROVEN LIVE
- fa_live nonzero rows: 0 (want 0)
- pool_size: 245 -> 273 (warm trail; cold-reset was STEP 4, never reached. Non-load-bearing: retrieval OFF -> pool does not feed proposer)
- console header 'Topics: 65' = cosmetic, non-authoritative (trace witnesses 24 hard). FLAG: resolve source in next pack.

## Decision (R6/R7, no goalpost move)
- STEP 4 (cold-reset + 40-tick conditioned) DID NOT RUN.
- 24-topic fabrication-prone hard set too easy on this substrate when blind -> F1 not yet expressible.
- NEXT = HARDEN the set (separate build session) -> re-baseline. Only on mean rate_f >= 0.30 -> conditioned run -> read.

## Candidate cause (harden session; NOT acted on here)
- Blind proposer still carries the per-weakness audit prompt ("State only specifics...", "emit verifiable [AUTHORIZED_...]") -> discipline-prompt suppresses fabrication independent of retrieval. Fork: harden topics past the audit, OR capture a naive-headroom rate_f without the audit instruction.

## Provenance
- frozen trace (LOCAL-only, topic-bearing -> gitignored): hl_baseline_v3.jsonl.frozen555548d3.20260624-1957
- log (public if topic-free): hl_baseline_v3.log
- reader (public): read_hl_baseline_v3.py
