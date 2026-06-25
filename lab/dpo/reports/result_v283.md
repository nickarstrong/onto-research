# v283 - CONDITIONED-RUN VALIDATION (RESULT)

Plane: retrieval-conditioned proposer GENERATE over the candidate 176-feed, with a
firewall-safe tap auditing every retrieved id. Sealed falsifier (prereg d00aaad) = GREEN.

## Run
- entrypoint: run_step6_live.py (tap wired on the conditioning retrieve_fn; novelty path untapped)
- feed: load_confirmed(candidate e886bc2a) = 176 (== canonical 91f442a0 at load layer)
- k=8, local Ollama substrate qwen2.5-coder:7b, wall ~200s (within S3.7 local tier)

## Sealed falsifier (frozen bars, not moved)
- R-MECH: audit lines = 8 (non-empty) -> conditioning retrieve exercised
- R-EXCL: quarantine hits = 0 (audit-ids intersect Q97 = empty)
- R-SEAL: Q97 sorted-set md5 = 45259b37 (== expected) ; Q97 = 97 ids (11 c2 + 86 prior-ABSTAIN)
- RESULT: GREEN

## Scope / honest caveat (sealed, unchanged)
- S1/S2 load-layer equality is tautology; discrimination = R-MECH (mechanism exercised)
  plus R-EXCL-as-bypass-trap. Adjudicate verdict NULL (drop=0) is the A/B novelty metric,
  separate from the sealed quarantine bar above.

## Provenance
- per-row ids / audit jsonl / Q97 enumeration = LOCAL ONLY (gitignored). This report carries
  counts + md5 + ruling only.
