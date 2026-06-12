#!/usr/bin/env python3
# wire_provenance_L4.py
# SPEC sec9 step2 -- wire the provenance turnstile (L1/L2, step1) to the FROZEN content-bind organ (L4).
# Frozen organ: SPEC_verifier_v1.md (md5 f7433706). Apply rule REUSED from run_E39_probe.py (md5 e8a6fec9),
# NOT re-implemented -> if the frozen rule ever moves, this wiring follows it; zero divergence.
#
# CONTRACT (the only new logic here):
#   provenance verdict (step1)  ->  pre_demoted  ->  organ  ->  SPEC tier
#     T4_*           -> pre_demoted=True  -> organ rejects (no NLI)        -> T4 (failed/fabricated marker)
#     L1L2_PASS      -> pre_demoted=False -> organ runs D_lambda over S:
#        S_size==0                         (no candidates, bind not established) -> T1_BIND_UNCHECKED
#        D_lambda >= 0.67                  (source contradicts the claim)         -> T1_BIND_CONTRADICTED
#        D_lambda <  0.67                  (bind holds)                           -> T0_ELIGIBLE
#   T0_ELIGIBLE is NOT T0: L5 corroboration (step3) + G-floor (step4) still gate. Ceiling stays T1 until step3.
#
# ANCHOR (G3, drift guard): over the REAL frozen E42scale readout, evaluate(recs, lambda=1.0, tau=0.67)
#   MUST reproduce fa_op 0.0333 / recall(B2) 0.9000 byte-exact. Mismatch = env/version drift -> STOP, not re-measure.
#   The readout's OWN pre_demoted is used as-is for the anchor (the live L1/L2->pre_demoted path is intake-only).

import argparse, json, sys, os

# reuse the FROZEN rule + loader (same dir on disk: lab/dpo/)
try:
    from run_E39_probe import evaluate, d_lambda, load_records
except ImportError:
    sys.exit("wire_provenance_L4: run_E39_probe.py must be importable (same dir). Frozen apply is reused, not copied.")

LAMBDA_FROZEN = 1.0
TAU_FROZEN    = 0.67
ANCHOR_FA     = 0.0333
ANCHOR_RECALL = 0.9000

# ---------------------------------------------------------------- intake contract

def tier_of_live(prov_verdict, n_con, n_ent, S_size):
    """Map (step1 provenance verdict, organ inputs) -> SPEC tier. The new step2 logic."""
    if prov_verdict.startswith("T4"):
        return "T4"                                   # provenance failed -> fabricated/failed marker
    if prov_verdict != "L1L2_PASS":
        raise ValueError(f"unknown provenance verdict {prov_verdict!r}")
    if S_size <= 0:
        return "T1_BIND_UNCHECKED"                    # no candidate set -> bind not established
    rec = {"n_con": n_con, "n_ent": n_ent, "S_size": S_size}
    D = d_lambda(rec, LAMBDA_FROZEN)                  # frozen formula, reused
    if D >= TAU_FROZEN:
        return "T1_BIND_CONTRADICTED"                 # organ reject: source contradicts the claim
    return "T0_ELIGIBLE"                              # bind holds; pending L5 (step3) + G-floor (step4)

# ---------------------------------------------------------------- anchor (real readout)

def anchor_check(readout_path):
    recs = load_records(readout_path)                 # frozen loader (LOUD fail on shape mismatch)
    m = evaluate(recs, LAMBDA_FROZEN, TAU_FROZEN)     # frozen apply at the frozen op
    fa = round(m["fa_op"], 4)
    b2 = round(m["B2"], 4)
    ok_fa = (fa == ANCHOR_FA)
    ok_b2 = (b2 == ANCHOR_RECALL)
    return {"fa_op": fa, "recall_B2": b2, "gold_n": m["gold_n"], "spoof_n": m["spoof_n"],
            "ok_fa": ok_fa, "ok_b2": ok_b2, "ok": ok_fa and ok_b2}

# ---------------------------------------------------------------- selftest (logic only; no real anchor)

def selftest():
    cases = [
        ("T4_RETRACTED",     9, 9, 9, "T4"),                    # provenance fail -> T4 (organ not consulted)
        ("T4_L1_MISMATCH",   0, 9, 9, "T4"),
        ("L1L2_PASS",        0, 0, 0, "T1_BIND_UNCHECKED"),     # empty S
        ("L1L2_PASS",        4, 0, 4, "T1_BIND_CONTRADICTED"),  # D=1.0 (ho_g12-like pure contradiction)
        ("L1L2_PASS",        3, 0, 4, "T1_BIND_CONTRADICTED"),  # D=0.75 >= 0.67
        ("L1L2_PASS",        2, 1, 4, "T0_ELIGIBLE"),           # D=0.25 < 0.67 bind holds
        ("L1L2_PASS",        0, 3, 4, "T0_ELIGIBLE"),           # D=-0.75 strong entail
    ]
    allok = True
    for prov, nc, ne, s, want in cases:
        got = tier_of_live(prov, nc, ne, s)
        ok = got == want
        allok &= ok
        D = (nc - ne)/s if s > 0 else None
        print(f"  {'ok ' if ok else 'XX '} {prov:18} nc={nc} ne={ne} S={s} D={D}  -> {got:22} want={want}")
    assert allok, "tier mapping mismatch"
    # accept-path + reject-path both present (not collapsed)
    outs = {tier_of_live(p, nc, ne, s) for p, nc, ne, s, _ in cases}
    assert "T0_ELIGIBLE" in outs and "T4" in outs and "T1_BIND_CONTRADICTED" in outs, "path collapse"
    print("\nSELFTEST: PASS (tier contract sound; T4/T1/T0 paths all exercised)")
    print("NOTE: real anchor (fa 0.0333 / recall 0.9000) validated only against the live E42scale readout.")

# ---------------------------------------------------------------- cli

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--anchor", metavar="E42SCALE_READOUT_JSON",
                    help="validate wiring reproduces frozen fa 0.0333 / recall 0.9000 (G3 drift guard)")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.anchor:
        r = anchor_check(a.anchor)
        print(json.dumps(r, indent=2))
        print("ANCHOR:", "PASS" if r["ok"] else "FAIL -- env/version drift, STOP (G3)")
        sys.exit(0 if r["ok"] else 1)
    else:
        ap.print_help()
