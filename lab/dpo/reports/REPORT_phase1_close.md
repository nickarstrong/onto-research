# REPORT_phase1_close.md -- phase-1 band-A TRUST gate CLOSED
date  : 2026-06-14
plane : RESEARCH / lab
gate  : false_flag <= 0.10 (HARD, C1) AND detect >= 0.60, BOTH channels, on >=20+20 Founder-judged set.
bars  : frozen (SPEC_selfcheck_A sec2 ; ARCHITECTURE sec4). Not re-tuned (R7).

RESULT (Founder-authored/judged sets ; eval/_local/, LOCAL-ONLY, excluded from public git):
  A-channel  verify_E16_A.py --eval labeled_A.jsonl  (20 dirty + 20 clean)
     detect = 0.900 ; false_flag = 0.000 ; VOID guard clear (A1-A4 each exercised). PASS.
  B-channel  verify_E16_B.py --eval labeled_B.jsonl  (20 dirty + 20 clean ; real GOLD store)
     detect = 0.850 ; false_flag = 0.000. PASS.
  B grounding leg confirmed: verify_E16_B.py --selftest PASS ; BN1_grounded -> VERIFIED on live store.

CI (n=20 each, honest floor ; R2): false_flag 0.000 -> 95% upper ~0.16 ; detect A ~[0.70,0.97],
  B ~[0.64,0.95]. Point estimates clear the frozen bars ; CIs are the 20+20 honest-floor width.

ENV NOTE (R3): B run emits a Windows pyarrow import access-violation faulthandler dump
  (semantic_retrieve._get_model). NON-FATAL: run completes, results identical across two runs,
  --selftest BN1_grounded resolves VERIFIED -> GOLD path intact, dump is benign. Cosmetic fix deferred.

R6 TARGET MET: on >=20+20 Founder sets, BOTH channels false_flag <= 0.10 AND detect >= 0.60.
ORGANS (frozen, eval/wrap-only, not mutated): verify_E16_A ea9d688b, verify_E16_B 37bff8c8, verify_E16 4d3505ce.

STATUS: phase-1 CLOSED. band-A TRUST complete. NEXT = fix(b) bounded DPO (NEXT+1),
  gated THROUGH this hardened phase-1 verifier (both channels).