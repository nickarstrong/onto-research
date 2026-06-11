#!/usr/bin/env python3
# run_E40_probe.py -- E40 robustness / feasible-region sweep over the FROZEN E37 readout.
# Contract: reports/PRE_REGISTER_E40.md v2 (FROZEN, md5 3f0ae4eb386548ef566621862beee95f).
#
# IMPORT-ONLY statistic: reuses run_E39_probe.load_records / d_lambda / evaluate. NO re-derivation.
# Maps R = {(lambda,tau): fa_op<=0.10 AND B2>=0.90} over the refined grid; decides
# REGION_ROBUST | REGION_SLIVER | FLOOR_BOUND. No perturbation of con/ent/|S|. no-GPU.
#
# Anchors (byte-exact, else VOID): best_op (1.0,0.67)->fa 0.0333/B2 0.9000 ;
# lambda=0 spoof con_share (tau_e37)->fa 0.0333 ; noauth ceiling max_B2_grid==0.9333.

import os, sys, json, argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from run_E39_probe import load_records, d_lambda, evaluate, void  # verified interface (md5 e8a6fec9)

# ---- FROZEN GRID (PRE_REGISTER_E40 sec4; integer-indexed to kill float drift) ----
LAMBDA = [round(0.5 + 0.1 * i, 1) for i in range(11)]      # 0.5..1.5  (11)
TAU    = [round(0.50 + 0.01 * j, 2) for j in range(26)]    # 0.50..0.75 (26)  -> 286 points
FA_GATE = 0.10
B2_GATE = 0.90
FA_DP = 4
# decision rule (sec6, LOCKED before sweep):
K = 12
SPAN_LAMBDA_MIN = 2   # grid steps
SPAN_TAU_MIN    = 2   # grid steps
# anchors (sec8)
ANCHOR_LAM, ANCHOR_TAU = 1.0, 0.67
ANCHOR_FA, ANCHOR_B2 = 0.0333, 0.9000
NOAUTH_CEIL = 0.9333  # 28/30
SPOOF_ANCHOR_FA = 0.0333

OUT_REPORT = "reports/report_E40.md"
OUT_GATE   = "reports/gate_E40.log"
OUT_JSON   = "reports/E40_region.json"


def r4(x):
    return round(x, FA_DP)


def readout_gate(recs, tau_e37, log):
    # G1-G4 (sec2). load_records already loud-fails missing fields (G3). Here: counts + spoof anchor.
    n = len(recs)
    gold_n = sum(1 for r in recs if r["true_class"] == "gold")
    spoof_n = sum(1 for r in recs if r["true_class"] == "spoof")
    log.append("G1 rows           : %d (expect 60) -> %s" % (n, "PASS" if n == 60 else "FAIL"))
    log.append("G2 split          : gold %d / spoof %d (expect 30/30) -> %s"
               % (gold_n, spoof_n, "PASS" if (gold_n == 30 and spoof_n == 30) else "FAIL"))
    if n != 60:
        void("G1: rows=%d != 60" % n)
    if gold_n != 30 or spoof_n != 30:
        void("G2: split gold=%d spoof=%d != 30/30" % (gold_n, spoof_n))
    # G4: D_0 (lambda=0 == con_share) spoof-side fa reproduces E39 spoof anchor 0.0333.
    m0 = evaluate(recs, 0.0, tau_e37)
    log.append("G3 schema         : load_records enforced 6 fields (item_id,n_con,n_ent,S_size,true_class,pre_demoted) -> PASS")
    log.append("G4 spoof anchor   : lambda=0 tau=%.2f fa_op=%.4f (expect %.4f) -> %s"
               % (tau_e37, m0["fa_op"], SPOOF_ANCHOR_FA, "PASS" if r4(m0["fa_op"]) == SPOOF_ANCHOR_FA else "FAIL"))
    if r4(m0["fa_op"]) != SPOOF_ANCHOR_FA:
        void("G4: lambda=0,tau=%.2f spoof fa_op=%.6f (4dp %.4f) != %.4f -- readout content drifted"
             % (tau_e37, m0["fa_op"], r4(m0["fa_op"]), SPOOF_ANCHOR_FA))


def sweep(recs):
    grid = []
    for lam in LAMBDA:
        for tau in TAU:
            m = evaluate(recs, lam, tau)
            grid.append({"lambda": lam, "tau": tau, "fa_op": m["fa_op"], "B2": m["B2"]})
    return grid


def feasible(m):
    return (m["fa_op"] <= FA_GATE) and (m["B2"] >= B2_GATE)


def fork(R, max_b2_in_R, lam_span, tau_span):
    # ordered, total (sec6). R is non-empty here (anchor feasible by construction).
    if r4(max_b2_in_R) == round(B2_GATE, FA_DP):          # FLOOR_BOUND: no feasible point exceeds 0.90
        return "FLOOR_BOUND"
    if len(R) >= K and lam_span >= SPAN_LAMBDA_MIN and tau_span >= SPAN_TAU_MIN:
        return "REGION_ROBUST"
    return "REGION_SLIVER"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", default=os.environ.get("E37_READOUT", "eval/_local/E37_boundset.json"))
    ap.add_argument("--tau-e37", type=float, default=0.67,
                    help="E37 recorded con_share threshold (spoof anchor). default 0.67 per pack v89.")
    ap.add_argument("--out-report", default=OUT_REPORT)
    ap.add_argument("--out-json", default=OUT_JSON)
    ap.add_argument("--out-gate", default=OUT_GATE)
    args = ap.parse_args()

    log = ["E40 gate"]

    # --- V1 readout gate (load_records enforces schema; readout_gate adds counts + spoof anchor) ---
    recs = load_records(args.readout)            # void on missing/malformed (G3)
    readout_gate(recs, args.tau_e37, log)        # G1,G2,G4

    # --- V4 grid-range guard (defensive; enumeration is in-range by construction) ---
    if not all(0.5 <= l <= 1.5 for l in LAMBDA) or not all(0.50 <= t <= 0.75 for t in TAU):
        void("V4: grid emitted out-of-range lambda/tau")
    if any(l < 0.0 for l in LAMBDA):
        void("V4: negative lambda in grid (spoof-rescue path)")

    # --- sweep ---
    grid = sweep(recs)
    max_b2_grid = max(m["B2"] for m in grid)

    # --- V3 noauth ceiling (STRICT upper bound; below is a valid result, not a void -- v2 fix) ---
    log.append("V3 noauth ceiling : max_B2_grid=%.4f (ceiling %.4f, strict-upper) -> %s"
               % (max_b2_grid, NOAUTH_CEIL, "PASS" if r4(max_b2_grid) <= NOAUTH_CEIL else "FAIL"))
    if r4(max_b2_grid) > NOAUTH_CEIL:
        void("V3: max_B2_grid=%.6f (4dp %.4f) > ceiling %.4f -- noauth-gold wrongly rescued "
             "(pre_demoted unconditional-reject broke)" % (max_b2_grid, r4(max_b2_grid), NOAUTH_CEIL))

    # --- V2 best_op anchor (must be feasible + byte-exact) ---
    am = evaluate(recs, ANCHOR_LAM, ANCHOR_TAU)
    anchor_ok = (feasible({"fa_op": am["fa_op"], "B2": am["B2"]})
                 and r4(am["fa_op"]) == ANCHOR_FA and r4(am["B2"]) == ANCHOR_B2)
    log.append("V2 best_op anchor : lambda=%.1f tau=%.2f fa_op=%.4f B2=%.4f (expect %.4f/%.4f) -> %s"
               % (ANCHOR_LAM, ANCHOR_TAU, am["fa_op"], am["B2"], ANCHOR_FA, ANCHOR_B2,
                  "PASS" if anchor_ok else "FAIL"))
    if not anchor_ok:
        void("V2: best_op (%.1f,%.2f) fa_op=%.6f B2=%.6f != %.4f/%.4f or infeasible"
             % (ANCHOR_LAM, ANCHOR_TAU, am["fa_op"], am["B2"], ANCHOR_FA, ANCHOR_B2))

    # --- region R + bounding box ---
    R = [m for m in grid if feasible(m)]
    if not R:
        void("R empty -- impossible (anchor feasible) -> substrate inconsistent")
    lams = sorted(set(m["lambda"] for m in R))
    taus = sorted(set(m["tau"] for m in R))
    lam_span = round((max(lams) - min(lams)) / 0.1) if len(lams) > 1 else 0
    tau_span = round((max(taus) - min(taus)) / 0.01) if len(taus) > 1 else 0
    max_b2_in_R = max(m["B2"] for m in R)
    min_b2_in_R = min(m["B2"] for m in R)

    verdict = fork(R, max_b2_in_R, lam_span, tau_span)

    log.append("region |R|        : %d (K=%d)" % (len(R), K))
    log.append("bbox lambda       : [%.1f .. %.1f] span_steps=%d (min %d)"
               % (min(lams), max(lams), lam_span, SPAN_LAMBDA_MIN))
    log.append("bbox tau          : [%.2f .. %.2f] span_steps=%d (min %d)"
               % (min(taus), max(taus), tau_span, SPAN_TAU_MIN))
    log.append("B2 in R           : [%.4f .. %.4f]" % (min_b2_in_R, max_b2_in_R))
    log.append("VERDICT           : %s" % verdict)

    out = {
        "experiment": "E40",
        "contract_md5": "3f0ae4eb386548ef566621862beee95f",
        "n_records": len(recs),
        "grid_points": len(grid),
        "R_count": len(R),
        "R": [{"lambda": m["lambda"], "tau": m["tau"], "fa_op": round(m["fa_op"], 6),
               "B2": round(m["B2"], 6)} for m in R],
        "bbox": {"lambda": [min(lams), max(lams)], "tau": [min(taus), max(taus)],
                 "lambda_span_steps": lam_span, "tau_span_steps": tau_span},
        "max_B2_in_R": round(max_b2_in_R, 6),
        "min_B2_in_R": round(min_b2_in_R, 6),
        "max_B2_grid": round(max_b2_grid, 6),
        "anchor": {"lambda": ANCHOR_LAM, "tau": ANCHOR_TAU,
                   "fa_op": round(am["fa_op"], 6), "B2": round(am["B2"], 6), "byte_exact": True},
        "K": K, "span_min": {"lambda": SPAN_LAMBDA_MIN, "tau": SPAN_TAU_MIN},
        "verdict": verdict,
    }
    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    with open(args.out_gate, "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")

    with open(args.out_report, "w", encoding="utf-8") as f:
        f.write("# report_E40 -- robustness / feasible-region sweep\n\n")
        f.write("## sec0 contract\nPRE_REGISTER_E40 v2 md5 3f0ae4eb386548ef566621862beee95f ; "
                "import-only from run_E39_probe (md5 e8a6fec9). no-GPU; frozen readout.\n\n")
        f.write("## sec1 anchors\n")
        f.write("best_op (lambda=1.0, tau=0.67): fa_op=%.4f B2=%.4f == 0.0333/0.9000 (byte-exact PASS)\n"
                % (am["fa_op"], am["B2"]))
        f.write("lambda=0 spoof anchor (tau=%.2f): reproduces 0.0333 (PASS)\n" % args.tau_e37)
        f.write("noauth ceiling: max_B2_grid=%.4f <= 0.9333 (PASS)\n\n" % max_b2_grid)
        f.write("## sec5 region\n")
        f.write("|R|=%d ; lambda bbox [%.1f..%.1f] span=%d steps ; tau bbox [%.2f..%.2f] span=%d steps\n"
                % (len(R), min(lams), max(lams), lam_span, min(taus), max(taus), tau_span))
        f.write("B2 in R: [%.4f .. %.4f]\n\n" % (min_b2_in_R, max_b2_in_R))
        f.write("## sec6 verdict\n")
        f.write("K=%d span_min(lambda=%d,tau=%d) -> **%s**\n"
                % (K, SPAN_LAMBDA_MIN, SPAN_TAU_MIN, verdict))

    print("E40 %s | |R|=%d lam_span=%d tau_span=%d | anchor PASS | max_B2_grid=%.4f"
          % (verdict, len(R), lam_span, tau_span, max_b2_grid))


if __name__ == "__main__":
    main()
