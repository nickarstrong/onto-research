# READMISSION_bars_E328 -- MEMORY->GOLD re-admission MEASURE (TYPE-B, aggregate)

> Public-bound eval (E325 pattern): mechanism + aggregate counts + checksums ONLY.
> NO held-out claim text, NO row ids. Held-out + harness NEVER public.
> Re-run of certified gate route(verdict, grounded) (v324) over frozen held-out;
> compared to v326 PRE-REGISTERED expected_tier (not the build's reroute_actual).

## inputs
- held-out md5: 9CEC01392BFB991EBC92F967AD7A660F (expect 9CEC0139..., 25 rows)
- gate src md5: C26D5146C79E44036C15D3316294F67B (o0_tiering_gate_v324.py)
- rows: 25
- RA-bucket counts: {'RA-abstain': 10, 'RA-idempotent': 5, 'RA-reject': 5, 'RA-ungrounded': 5}
- routed-tier tally: {'GOLD': 10, 'MEMORY': 10, 'REJECT': 5}
- expected-tier match: 25/25

## bars (v326 sec 2, pre-registered; falsifier-first, no threshold weakening)
- RA-floor              : GREEN  (GOLD rows on tuple != (CLEAN,True) = 0; ABSOLUTE)
- RA-ungrounded-promote : GREEN  (RA-ungrounded -> GOLD = 5/5)
- RA-abstain-stays      : GREEN  (RA-abstain -> MEMORY = 10/10, -> GOLD = 0; ABSOLUTE)
- RA-reject-stays       : GREEN  (RA-reject -> REJECT = 5/5, leak = 0; ABSOLUTE)
- RA-idempotent         : GREEN  (RA-idempotent -> GOLD = 5/5, double-route identical = True, no MEMORY<-GOLD = True)
- RA-hermetic           : GREEN  (counts/shape consistent; report md5 below; CONFIRM by 2-cold-run md5 compare)

## formal result
- FORMAL (5 intrinsic bars + match): ALL-GREEN
- RA-hermetic final verdict: GREEN iff this report's md5 is identical across two cold runs.

## checksums
- per-row report md5 (LOCAL): 30E8311588011B363B7812FE17F8C2F9
- held-out md5: 9CEC01392BFB991EBC92F967AD7A660F
- gate src md5: C26D5146C79E44036C15D3316294F67B
