# RESULT v285 - POST-SWAP VALIDATION - GREEN

date: 2026-06-25
plane: post-swap validation (rollback-window close)
canonical under test: o0_verdicts.jsonl md5=e886bc2a (360 lines; ABSTAIN=97)
prereg: PREREG_v285_postswap.md md5=bd8507bf (sealed before run)

CONDITIONED RUN (run_step6_live.py md5=96337833, canonical e886bc2a, k=3):
  verdict PASS | f_blind 0.333 -> f_cond 0.000 (drop 0.333 >= bar 0.25)
  fa_cond 0.000 | novelty_cond 1.000 >= 0.75

SEALED FALSIFIER (falsifier_v282_quarantine.py md5=ac62437b):
  R-SEAL  GREEN  q97 seal 45259b37 (97 ids)
  R-EXCL  GREEN  quarantine hits 0 (8 distinct retrieved disjoint from 97)
  R-MECH  GREEN  11 audit lines = conditioning calls; novelty path untapped
  honest caveat (R17): R-EXCL structurally guaranteed at load layer (feed=176
  disjoint from 97); its live job = catch code-path bypass (none). Discriminative
  signal = conditioning drop 0.333, not R-EXCL.

SWAP INTEGRITY: canonical vs v284pre diff = 22 lines = 11 c2-flips x 2 sides.
  ABSTAIN 86 -> 97 (+11) = the 11 both-empty rows now honest.

OUTCOME: validation GREEN -> rollback window CLOSED.
  v284pre (91f442a0) + v280pre (755d81c3) content-verified + deleted (single-path).
  canonical e886bc2a sole live pool.