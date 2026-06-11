# E39_V2_DEFECT.md -- PRE_REGISTER_E39 v2 contract defect (caught pre-write by emitter self-check)

status   : v2 RETIRED -> v3 (reports/PRE_REGISTER_E39.md md5 04b83e395a5c7f2cf9c0e29aba9bbfdc).
retired  : PRE_REGISTER_E39.md v2 md5 774f8e41e2461777da197e3e809d573a.
date     : 2026-06-11
trigger  : emit_E37_readout.py VOID on real heldout_E17 BEFORE writing any json:
           "item ho_g02 (gold) non-pre_demoted but S_size==0 -> empty bound set (sec2 HARD SHAPE GATE)".

## defect
v2 sec2 asserted: every non-pre_demoted B1/B2 row MUST have S_size >= 1, else VOID. This CONFLATED two distinct
shapes:
  (a) "no auth resolution" (pure PASS-COMMON), and
  (b) "has auth claim(s) but all candidates fall below B_floor=0.1" -> empty bound set S.
ho_g02 is shape (b): a gold with auth provenance whose support did not bind at the floor. In the FROZEN E37 scorer
(item_label_at_C) such an item gets n_con=0 -> no set_veto -> label VERIFIED -> ACCEPTED, and it counted toward
E37's B2. The v2 gate would VOID a row that E37 legitimately accepts -- i.e. the contract refused to reproduce the
substrate it is pre-registered against. The shape assumption was false pre-data; the spoof anchor, the D_lambda
statistic, the grids and the fork were NOT implicated.

## why it was a contract bug, not a result
- No E39 metric was seen (no band, no fork verdict). The VOID fired in the emitter's pre-write reconcile.
- The fix does not move any threshold or verdict: spoof anchor stays 16 pre_demoted + 13 con-veto = 29/30 = 0.0333;
  LAMBDA_GRID / TAU_GRID / FA_GATE / B2_GATE / fork unchanged (byte-identical).
- The correction makes E39 reproduce E37 MORE faithfully (empty-S gold now accepts, as E37 does), the opposite of
  a result-fudge. Same class of correction as v1->v2 (reports/E39_RECONCILE_DEFECT.md).

## correction (v3)
- non-pre_demoted AND S_size==0 (empty bound set OR pure PASS-COMMON) -> ACCEPT by construction (VERIFIED; no set
  to veto). representative returns (0,0,0). REPRODUCED, not VOIDed.
- The single universal correctness gate is sec6 (per-item: emit decision == E37 item_label_at_C op label),
  class-blind. Brittle shape gates removed from sec2/sec7.
- reject = pre_demoted OR (S_size>0 AND D_lambda >= tau) ; accept otherwise (incl. empty-S). (Unchanged in sec3;
  the bug was the redundant sec2 VOID + the evaluate empty-S branch, now both corrected.)

## artifacts (v3)
PRE_REGISTER_E39.md   md5 04b83e395a5c7f2cf9c0e29aba9bbfdc
emit_E37_readout.py   md5 343bf92ae20c9a7a1d0040c01842726a
run_E39_probe.py      md5 e8a6fec9b1ac72bc0bc69eafd82304e8

## lesson (filigree)
A shape assertion is not a reconcile. Enumerate every label the FROZEN scorer can emit (DEMOTE / VERIFIED /
PASS-COMMON, incl. empty-S VERIFIED) before asserting a shape gate. The decision-level reconcile (emit == E37 label)
subsumes and is safer than any count/shape gate.
