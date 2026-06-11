# E39 RECONCILE DEFECT -- frozen contract unreproducible against E37 decision composition

date        : 2026-06-11
caught at   : v86 intake, RECONCILE-AT-PAIRING (pre-run; no data scored, no VOID-by-construction)
status      : E39 v1 BLOCKED. redesign routed to v87 (noauth-split rung). NOT a run failure -- a design defect.
artifacts   : run_E39_probe.py md5 bf8e96762a7dc40298d667436f2c42fb (FROZEN v85)
              reports/PRE_REGISTER_E39.md md5 a78919237ca2335a945b968e971b418f (FROZEN v85)
              -> both remain ON DISK, UNCOMMITTED; SUPERSEDED by the v87 redesign (do not commit v1).

## 0 two-layer finding

LAYER 1 -- readout substrate never existed.
  run_E37_probe.py (15e694a6, 88489f8) emits report_E37.md ONLY. grep json.dump / with open / .json over the
  whole file = md5-helper + argparse(--fixture/--heldout/--out) and nothing else. E37 computed per-candidate
  con/ent IN MEMORY (item_label_at_C) and NEVER serialized them. gate_E37.log is captured stdout, not a readout.
  The file present at eval/_local/E37_boundset.json is a RETRIEVAL MAP { item_id : [source strings] } (|S| members
  as raw citations), NOT the scored { item_id, n_con, n_ent, S_size, true_class } the E39 adapter requires.
  => the "frozen E37 readout" the v86 pack assumed does not exist.

LAYER 2 -- the anchor is structurally unreachable by a pure con/ent statistic (the real blocker).
  E39 anchor (hardcoded): E37_FA_OP = 0.0333, FA_DP = 4 ; reject iff D_lambda >= tau ; fa = spoof_acc / spoof_n.
  Reproduction requires: 30 spoofs, 29 rejected via D_0 >= 0.67 (tau_E37), 1 survives -> 1/30 = 0.0333.
  E37 S3 attribution (gate_E37.log, 88489f8) decomposes the 29 op-point spoof demotions DISJOINTLY:
      noauth baseline (demote @ C=+inf) = 16   <- unauthorized source -> UNVERIFIABLE; model-independent; NO con_share
      contradiction-veto reject organ  = 13   <- auth spoofs, vetoed by contradiction
      survived (false-accept)          =  1   <- auth spoof, not vetoed
  => auth spoofs = 30 - 16 = 14 ; con-veto fa over the auth subset = 1/14 = 0.0714.

  E39's statistic D_lambda = (n_con - lambda*n_ent)/|S| reads ONLY con/ent over a non-empty bound set S.
  It has NO noauth channel and VOIDs on S_size <= 0 (load_records guard). Therefore:
    - full readout (30 spoofs): the 16 noauth items have empty S and zero contradiction. Rejecting them via
      D_0 >= 0.67 would require fabricating con_share >= 0.67 -> R7 violation. NOT DONE.
    - auth-only readout (14 spoofs): D_0 honestly reproduces 13/14 reject = 1/14 = 0.0714, which != the hardcoded
      E37_FA_OP 0.0333 -> anchor_check VOIDs (run_E39_probe.py:109).
  Either branch fails. 0.0333 is a con-veto(13)+noauth(16) COMPOSITE, not the output of a pure con statistic.

## 1 why this is not an adapter-only fix

The v86 pack authorized fixing the ADAPTER block ONLY, leaving the "frozen statistic/anchor/fork core untouched".
The required fix touches the CORE: (a) the E37_FA_OP anchor constant + its reproduction model, (b) a noauth
pre-demotion channel absent from the statistic, (c) the readout SCHEMA. Editing a frozen pre-registered contract
inside its own run-session = drift (proto R11 / 3.10). Escalated instead.

## 2 resolution -- v87 noauth-split rung (recommended, honest)

readout schema (per item) gains an explicit unconditional-demotion flag:
    record = { item_id, n_con, n_ent, S_size, true_class, pre_demoted }
      pre_demoted = True  iff the item carries a noauth (or otherwise unconditional, C=+inf) demotion;
                          S may be empty; D_lambda is SKIPPED for these (no fabricated con).
E39 reject rule becomes:  reject = pre_demoted OR (D_lambda >= tau).
anchor (full-fixture, faithful):
    lambda=0, tau=tau_E37=0.67 -> reject = 16 pre_demoted + 13 con-veto = 29/30 -> fa_op 0.0333 (4dp) REPRODUCES.
diagnostic (auth-only): con-veto fa over the 14 auth spoofs = 0.0714 (reported, not the gate anchor).
the cross-source-statistic question (does net-consensus D lift the bf-band) is then asked ONLY where con/ent
actually vary -- the auth subset -- which is the only place the statistic can move anything.

requires: NEW PRE_REGISTER_E39.md (re-freeze; old a7891923 retired) + patched run_E39_probe.py (new md5) +
an E37 readout emitter (emit_E37_readout.py) that imports run_E37_probe scoring, replays the FROZEN op-point
(C=0.0012960433959960938, A=0.35, B_floor=0.1, scope=any, W=0), and writes the 6-field per-item readout incl.
pre_demoted (noauth claims -> True). emitter self-checks by the same anchor (0.0333 over 30 at 4dp) before freeze.

## 3 falsifier (post-redesign)

If, after the noauth-split, lambda=0 @ tau_E37 does NOT reproduce 0.0333 over 30 at 4dp, OR any pre_demoted item
carries a fabricated con_share, the redesign is wrong -> VOID, do not proceed. The auth-only 0.0714 must also
hold as an internal cross-check (13/14).

## 4 load-bearing learning (carried into pack sec5, referenced not duplicated)

A regression anchor copied from a COMPOSITE decision (con-veto + a model-independent channel) cannot be
reproduced by a statistic that models only one channel. Verify the anchor's DECOMPOSITION at pairing, not just
its value -- RECONCILE-AT-PAIRING must check channel composition, not only field shapes. (E39 v1: 0.0333 looked
like a con-statistic target; it was 13 con + 16 noauth.)
