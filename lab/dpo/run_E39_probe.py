#!/usr/bin/env python3
# run_E39_probe.py -- E39 cross-source statistic probe (net-consensus D_lambda)
# DESIGN DELIVERABLE. Laid on disk UNCOMMITTED at the v85 close; paired + committed at the v86 RUN.
# Contract: reports/PRE_REGISTER_E39.md v2 noauth-split (FROZEN, md5 774f8e41e2461777da197e3e809d573a).
#
# Reads ONLY frozen E37 per-candidate con/ent + |S| over the scope-filtered bound set (B>=B_floor).
# No NLI by default (load class NONE). NLI fallback path is explicit and must self-declare (sec0).
# Class-blind compute; true class joined ONLY for per-class reporting. Op-selection peeks ONLY B2>=0.90.
# Anchor: lambda=0 reduces D to E37 con_share over AUTH rows; reject = pre_demoted OR D>=tau.
# lambda=0 @ tau_E37 MUST reproduce E37 fa_op 0.0333 (16 pre_demoted + 13 con-veto = 29/30), else VOID.
#
# RECONCILE-AT-PAIRING: the ADAPTER block below is the ONLY interface seam. It MUST be reconciled
# against the real run_E37_probe.py / run_E38_Sdist_probe.py interface on disk BEFORE the v86 run.
# It fails LOUD on any shape mismatch. There is NO silent fallback (E38 v83 []-fallback faked branch A).

import os, sys, json, hashlib, argparse
from itertools import product

# ---- FROZEN GRIDS (declared pre-data; oracle gate: no data-driven threshold selection) ----
LAMBDA_GRID = [0.0, 0.25, 0.5, 1.0, 2.0]          # 0.0 mandatory = degenerate->E37 con_share anchor
TAU_GRID    = [0.20, 0.25, 0.30, 0.3333, 0.40, 0.50, 0.60]  # con_share-comparable fractions
FA_GATE     = 0.10                                 # joint gate: spoof false-accept ceiling
B2_GATE     = 0.90                                 # joint gate: gold-accept recall floor
E37_FA_OP   = 0.0333                               # E37 set-veto op anchor as RECORDED (4dp display, 88489f8)
FA_DP       = 4                                     # recorded precision for verdict reproduction
# E37_TAU is NOT hardcoded: it is the threshold E37 actually used (read from gate_E37.log at pairing).
# Supplied via --tau-e37 / E37_TAU env. The probe REFUSES to run without it (cannot fake the anchor).

# ---- DECLARED PATHS (relative to lab/dpo/) ----
E37_READOUT = os.environ.get("E37_READOUT", "eval/_local/E37_boundset.json")  # heldout-derived, LOCAL ONLY
OUT_REPORT  = "reports/report_E39.md"
OUT_JSON    = "reports/E39_Dnet.json"
OUT_GATE    = "reports/gate_E39.log"


def void(msg):
    sys.stderr.write("VOID: %s\n" % msg)
    sys.exit(2)


# ============================ ADAPTER (RECONCILE SEAM) ============================
# Assemble per-claim records from the FROZEN E37 readout:
#   record = {"item_id": str, "n_con": int, "n_ent": int, "S_size": int, "true_class": "gold"|"spoof", "pre_demoted": bool}
# n_con / n_ent are counts over the scope-filtered bound set S (B>=B_floor) from E37's frozen con/ent.
# The readout schema is whatever E37 actually emits -> reconcile here against run_E37_probe.py at pairing.
# LOUD FAIL on any missing field. NO default-fill (E38/E23 VOID-by-construction guard).
def load_records(path):
    if not os.path.exists(path):
        void("E37 readout not found at %s -- reconcile path or run NLI-fallback (sec0)" % path)
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Expected: list of per-claim dicts, OR {"claims":[...]}. Reconcile against real interface.
    items = raw["claims"] if isinstance(raw, dict) and "claims" in raw else raw
    if not isinstance(items, list) or len(items) == 0:
        void("E37 readout empty/!list -- VOID-by-construction guard (probe would run on nothing)")
    recs = []
    for i, it in enumerate(items):
        try:
            r = {
                "item_id":     str(it["item_id"]),
                "n_con":       int(it["n_con"]),
                "n_ent":       int(it["n_ent"]),
                "S_size":      int(it["S_size"]),
                "true_class":  str(it["true_class"]),
                "pre_demoted": bool(it["pre_demoted"]),
            }
        except (KeyError, TypeError, ValueError) as e:
            void("E37 readout row %d shape mismatch (%s) -- RECONCILE adapter against emit_E37_readout.py" % (i, e))
        if r["S_size"] < 0:
            void("row %s has S_size<0 -- impossible" % r["item_id"])
        # S_size==0 is LEGAL: pre_demoted (noauth) OR non-pre_demoted-with-empty-bound-set (VERIFIED/PASS -> accept).
        if r["true_class"] not in ("gold", "spoof"):
            void("row %s true_class=%r not in {gold,spoof}" % (r["item_id"], r["true_class"]))
        recs.append(r)
    return recs
# ========================== END ADAPTER (RECONCILE SEAM) ==========================


def d_lambda(rec, lam):
    # CLASS-BLIND: reads only observable counts. Never touches true_class.
    # Defined only for S_size>0; pre_demoted / empty-S rows SKIP D (reject unconditionally) -- never computed here.
    if rec["S_size"] <= 0:
        return float("nan")
    return (rec["n_con"] - lam * rec["n_ent"]) / rec["S_size"]


def evaluate(recs, lam, tau):
    # reject iff pre_demoted OR (S>0 AND D_lambda>=tau). empty-S non-pre_demoted -> accept (VERIFIED). D skipped there.
    # fa_op = spoof accepted / spoof total ; B2 = gold accepted / gold total. (max-based op gate; not p50 sep.)
    gold_n = gold_acc = spoof_n = spoof_acc = 0
    for r in recs:
        if r["pre_demoted"]:
            accepted = False                      # noauth -> unconditional reject; D skipped (no fabricated con)
        elif r["S_size"] <= 0:
            accepted = True                       # empty bound set -> never vetoed -> VERIFIED/PASS (reproduces E37)
        else:
            accepted = d_lambda(r, lam) < tau     # reject iff D_lambda >= tau
        if r["true_class"] == "gold":
            gold_n += 1; gold_acc += int(accepted)
        else:
            spoof_n += 1; spoof_acc += int(accepted)
    if gold_n == 0 or spoof_n == 0:
        void("one class empty in records (gold=%d spoof=%d) -- VOID guard" % (gold_n, spoof_n))
    fa = spoof_acc / spoof_n
    b2 = gold_acc / gold_n
    return {"lambda": lam, "tau": tau, "fa_op": fa, "B2": b2,
            "gold_n": gold_n, "spoof_n": spoof_n}


def anchor_check(recs, tau_e37):
    # TWO-PART byte-exact anchor at the FIXED recorded E37 threshold (no search -> no ambiguity).
    # (1) STRUCTURAL identity (exact float): at lambda=0, D_0 == con_share for every record, by formula.
    for r in recs:
        if r["pre_demoted"] or r["S_size"] <= 0:
            continue                              # pre_demoted rows carry no con_share (D skipped)
        d0 = d_lambda(r, 0.0)
        cs = r["n_con"] / r["S_size"]
        if d0 != cs:
            void("anchor: D_0 != con_share for %s (formula drift) -- %r vs %r" % (r["item_id"], d0, cs))
    # (2) VERDICT reproduction at the recorded E37 op (lambda=0, tau_e37) at recorded precision.
    m = evaluate(recs, 0.0, tau_e37)
    if round(m["fa_op"], FA_DP) != E37_FA_OP:
        void("anchor: lambda=0,tau_E37=%s gives fa_op=%.6f (4dp %.4f) != E37 %.4f -- read drifted (E23 guard)"
             % (tau_e37, m["fa_op"], round(m["fa_op"], FA_DP), E37_FA_OP))
    return tau_e37, m


def fork_verdict(band):
    # band = list of op-points clearing fa<=FA_GATE AND B2>=B2_GATE, with lambda>0 (lift requires the new axis).
    n_pts = len(band)
    n_lams = len(set(round(p["lambda"], 6) for p in band))
    if n_pts == 0:
        return "CROSS_SOURCE_EXHAUSTED", n_pts, n_lams
    # non-trivial band = >=2 distinct op-points across >=2 distinct lambda (not a single C-point, cf E27/E35)
    if n_pts >= 2 and n_lams >= 2:
        return "STATISTIC_LIFTS", n_pts, n_lams
    return "STATISTIC_KNIFE_EDGE", n_pts, n_lams


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", default=E37_READOUT)
    ap.add_argument("--tau-e37", type=float, default=None,
                    help="E37 recorded threshold (from gate_E37.log). REQUIRED; probe refuses without it.")
    ap.add_argument("--out-report", default=OUT_REPORT)
    ap.add_argument("--out-json", default=OUT_JSON)
    ap.add_argument("--out-gate", default=OUT_GATE)
    args = ap.parse_args()

    tau_e37 = args.tau_e37
    if tau_e37 is None and os.environ.get("E37_TAU"):
        tau_e37 = float(os.environ["E37_TAU"])
    if tau_e37 is None:
        void("E37 recorded tau not supplied (--tau-e37 / E37_TAU). Read it from gate_E37.log at pairing; "
             "the anchor cannot be evaluated without it (no fake default).")
    # effective tau set MUST contain the degenerate anchor threshold tau_E37
    tau_set = sorted(set(TAU_GRID) | {tau_e37})

    # sec0 LOAD CLASS (honest, self-declared): frozen-readout path => NONE; else NLI fallback (not impl here).
    load_class = "NONE (arithmetic over frozen E37 con/ent)"
    src_md5 = None
    if os.path.exists(args.readout):
        with open(args.readout, "rb") as f:
            src_md5 = hashlib.md5(f.read()).hexdigest()
    else:
        void("frozen E37 readout absent -> NLI-fallback path required; not built in this probe. "
             "Reconcile or supply --readout (sec0 must NOT claim no-model without the frozen path).")

    recs = load_records(args.readout)
    gold_n = sum(1 for r in recs if r["true_class"] == "gold")
    spoof_n = sum(1 for r in recs if r["true_class"] == "spoof")
    n_pre = sum(1 for r in recs if r["pre_demoted"])

    # ANCHOR (hard, pre-sweep): lambda=0 at recorded tau_E37 must reproduce E37 fa_op + structural identity.
    tau_e37, anchor_m = anchor_check(recs, tau_e37)

    # SWEEP: class-blind compute over declared grids (tau_set includes tau_E37).
    grid = []
    for lam, tau in product(LAMBDA_GRID, tau_set):
        grid.append(evaluate(recs, lam, tau))

    # OP-SELECTION: peek ONLY B2>=B2_GATE (recall feasibility) then fa<=FA_GATE. lambda>0 = lift axis.
    band = [m for m in grid
            if m["B2"] >= B2_GATE and m["fa_op"] <= FA_GATE and m["lambda"] > 0.0]
    verdict, n_pts, n_lams = fork_verdict(band)

    # best op-point on the band (min fa, then max B2), if any
    best = sorted(band, key=lambda m: (m["fa_op"], -m["B2"]))[0] if band else None

    out = {
        "experiment": "E39",
        "statistic": "D_lambda = (n_con - lambda*n_ent)/|S|",
        "load_class": load_class,
        "e37_readout_md5": src_md5,
        "n_records": len(recs), "gold_n": gold_n, "spoof_n": spoof_n, "n_pre_demoted": n_pre,
        "lambda_grid": LAMBDA_GRID, "tau_grid": tau_set, "tau_e37": tau_e37,
        "fa_gate": FA_GATE, "b2_gate": B2_GATE,
        "anchor": {"lambda": 0.0, "tau_E37": tau_e37, "fa_op": anchor_m["fa_op"],
                   "expected_E37_fa_op": E37_FA_OP, "byte_exact": True},
        "band": band, "band_pts": n_pts, "band_lambdas": n_lams,
        "best_op": best, "verdict": verdict,
        "full_grid": grid,
    }
    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    with open(args.out_gate, "w", encoding="utf-8") as f:
        f.write("E39 gate\n")
        f.write("load_class       : %s\n" % load_class)
        f.write("e37_readout_md5  : %s\n" % src_md5)
        f.write("records          : %d (gold %d / spoof %d ; pre_demoted %d)\n" % (len(recs), gold_n, spoof_n, n_pre))
        f.write("anchor lambda=0  : tau_E37=%s fa_op=%.4f (expect %.4f) byte_exact=PASS\n"
                % (tau_e37, anchor_m["fa_op"], E37_FA_OP))
        f.write("band_pts/lambdas : %d / %d\n" % (n_pts, n_lams))
        if best:
            f.write("best_op          : lambda=%s tau=%s fa_op=%.4f B2=%.4f\n"
                    % (best["lambda"], best["tau"], best["fa_op"], best["B2"]))
        f.write("VERDICT          : %s\n" % verdict)

    with open(args.out_report, "w", encoding="utf-8") as f:
        f.write("# report_E39 -- net-consensus cross-source statistic\n\n")
        f.write("## sec0 load class\n%s ; e37_readout md5 %s\n\n" % (load_class, src_md5))
        f.write("## sec1 anchor\nlambda=0 -> con_share ; tau_E37=%s ; fa_op=%.4f == E37 %.4f (byte-exact PASS)\n\n"
                % (tau_e37, anchor_m["fa_op"], E37_FA_OP))
        f.write("## sec6 fork\nVERDICT: %s (band_pts=%d, distinct_lambda=%d)\n" % (verdict, n_pts, n_lams))
        if best:
            f.write("best_op: lambda=%s tau=%s fa_op=%.4f B2=%.4f\n"
                    % (best["lambda"], best["tau"], best["fa_op"], best["B2"]))

    print("E39 %s | anchor PASS | band_pts=%d lambdas=%d" % (verdict, n_pts, n_lams))


if __name__ == "__main__":
    main()
