# report_E16_e2e -- END-TO-END L1-L2-L4 (one coherent pipe)

corpus    : eval\_local\gold_corpus_live.json
turnstile : provenance_turnstile.turnstile_gate (FROZEN 4b04fe73)
organ     : verify_E16_L4.verify_item (FROZEN 544c9a7b, import-only)

| id | expect | verdict | ok | reached_L4 | L1 | L2 | sec |
|---|---|---|---|---|---|---|---|
| e2e_koonin_contra | CONTRADICTED | CONTRADICTED | Y | Y | resolve+match(jaccard=1.00) | clean(crossmark; RWD=crossref-integrated only -- coverage gap owned) | 54.98 |
| e2e_koonin_clean | VERIFIED | VERIFIED | Y | Y | resolve+match(jaccard=1.00) | clean(crossmark; RWD=crossref-integrated only -- coverage gap owned) | 31.76 |
| e2e_misattrib | REJECT-L1 | REJECT-L1 | Y | n/a(gated) | metadata-mismatch(jaccard=0.08 < 0.50) | n/a(gated) | 0.82 |
| e2e_unresolvable | REJECT-L1 | REJECT-L1 | Y | n/a(gated) | non-resolve(status=404) | n/a(gated) | 0.77 |

pass=4 fail=0  gate_leak=0  false_veto=0
legs: bad_rejected_pre_model=True  clean_contra->CONTRADICTED=True  clean_agree->VERIFIED=True  all_clean_reach_L4=True

VERDICT: PASS
