# G2 -- DOI blind probe (Step-6 apparatus)

- date: 2026-06-23
- model (frozen substrate): `qwen2.5-coder:7b`
- scope: doi_provoke_id (3-DOI-scope; verifier resolves DOI only)
- k: 3  n_topics: 3

## Result

- **GATE: PASS** (bar rate_f >= 0.3)
- rate_f_blind = **0.667**
- fa_live_blind = 0.0 (invariant: 0.0)
- decision: PASS -> conditioning measurable -> proceed to G3 (separate session)

## Per-row (topics redacted; held-out, sec 3.2)

| idx | family | verdict | topic_sha256 |
|-----|--------|---------|--------------|
| 0 | provoke_id | CLEAN | `d84952699cd6` |
| 1 | provoke_id | DIRTY | `46f816ae5636` |
| 2 | provoke_id | DIRTY | `2d8d3a7c59d7` |

## Probe-set provenance (dated priority; set itself is private)

- `hard_topics.py` md5: `c620b6507f760433ec33c1dafe92e4e1`
- `hard_topics_meta.json` md5: `65ead4d96969bd8baddd4b3e16d586e4`

> Probe-set (held-out bait) is private (sec 3.2). It was previously
> committed to public history in error and removed via history rewrite
> (force-push, origin/main 43b1104 -> 8b20461). The v231 set is therefore
> CONTAMINATED for any FUTURE substrate swap and must be replaced with a
> fresh held-out there. The frozen substrate measured here predates the
> leak, so THIS measurement is clean.
