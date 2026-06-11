# E39_V3_DEFECT.md -- PRE_REGISTER_E39 v3 contract defect (caught pre-write by emitter self-check)

status   : v3 RETIRED -> v4 (reports/PRE_REGISTER_E39.md md5 95ca5dff96df959ac1b84fb688de2757).
retired  : PRE_REGISTER_E39.md v3 md5 04b83e395a5c7f2cf9c0e29aba9bbfdc.
date     : 2026-06-11
trigger  : emit_E37_readout.py VOID on real heldout_E17 BEFORE writing any json:
           sec6 reconcile, 4 GOLD items emit_reject != e37_demote:
             ho_g00 (n_con=1 n_ent=1 S=1), ho_g03 (2/1/2), ho_g04 (2/1/2), ho_g13 (3/1/4) -- all con_share>=0.67
             with n_ent>=1 ; E37 VERIFIED (entailer-rescued), D_0 rejects.

## defect
v3 sec6 asserted emit decision == E37 op label for EVERY B1/B2 item. That demanded D_0 (= con_share at lambda=0)
reproduce E37's GOLD-accept. But E37 accepts those golds via the set_veto n_ent==0 guard (a high-con_share claim
with an entailer is NOT vetoed). D_0 ignores n_ent, so it rejects them. The check therefore required the statistic
to AGREE with con_share on exactly the cases where E39's entire premise is that it must DISAGREE (the n_ent term).
A gold rejected at lambda=0 and rescued at lambda>0 is the LIFT being measured -- not a reconcile failure.

## why it was a contract bug, not a result
- No E39 metric/verdict seen; VOID fired in the emitter's pre-write reconcile.
- Spoof fa anchor (16 pre_demoted + 13 con-veto = 29/30 = 0.0333), auth-only 0.0714, D_lambda, LAMBDA/TAU grids,
  fork -- ALL unchanged. run_E39_probe.py UNCHANGED (md5 e8a6fec9b1ac72bc0bc69eafd82304e8); its anchor already
  gates on spoof fa only and tolerates low gold B2 at lambda=0.
- The fix removes an over-strong assertion; it does not move any threshold or verdict.

## correction (v4)
- sec6 per-item reconcile restricted to SPOOFS: emit_reject == e37_demote for all spoofs (con-veto claims have
  n_ent==0, so D_0 reproduces them; a spoof entailer-rescued at high con_share would also break the sec4 fa anchor).
- GOLDS excluded from per-item reconcile by design. The lambda=0 anchor reproduces the E37 SPOOF fa only; gold B2
  at lambda=0 is expected LOW and is measured (recovered) via the B2 lift in the sweep (sec5), not anchored.

## artifacts (v4)
PRE_REGISTER_E39.md   md5 95ca5dff96df959ac1b84fb688de2757
emit_E37_readout.py   md5 81bc538bd34009e29a7df73e85fc0485
run_E39_probe.py      md5 e8a6fec9b1ac72bc0bc69eafd82304e8  (unchanged from v3)

## lesson (filigree, compounds E39_V2_DEFECT)
A reconcile must assert ONLY what the experiment's premise requires. Twice now the gate over-specified faithfulness:
v2 imposed a shape E37 does not hold; v3 imposed agreement on the very axis the new statistic exists to exploit.
Minimal faithful reconcile = md5 (substrate) + structural D_0==con_share (formula) + SPOOF fa anchor 0.0333 +
auth-only 0.0714. Anything asserted about GOLDS at lambda=0 contradicts the lift. Do not gate on what you intend to move.
