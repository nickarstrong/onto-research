#!/usr/bin/env python3
# wire_tier.py
# SPEC sec9 step4 -- tier assembly (T0-T4) + D2 G-FLOOR.
# Frozen SPEC: SPEC_provenance_verifier_v1.md (md5 b62aad2f), sec3 tier ladder + sec1/sec3 G-floor.
# Composes step2 (wire_provenance_L4.tier_of_live) -> adds AXIS-G grade + L5 corroboration -> final tier.
# No model, no GPU. The L4 rule stays sourced from the frozen organ via step2's import chain.
#
# TIER LADDER (SPEC sec3, AXIS-P):
#   T0 VERIFIED PRIMARY      L1 pass + L2 clean + L4 bind holds + L5 corroborated + AXIS-G >= floor
#   T1 VERIFIED BIND-UNCHK   L1 pass + L2 clean, bind not established / not yet corroborated  [CURRENT CEILING]
#   T2 GRADE-DEGRADED        L1 pass + L2 clean, AXIS-G low (preprint/fringe/ID-venue/EoC)
#   T3 MARKERLESS            no DOI / non-resolving marker  -> memory/low-tier (NOT false)
#   T4 FAILED/FABRICATED     L1 fails OR L2 retracted  -> reject.  ASYMMETRY: T4 < T3.
#
# D2 G-FLOOR (load-bearing): T0 REQUIRES AXIS-G >= observational/peer-reviewed. A clean-DOI preprint that
#   merely corroborates does NOT reach T0 -> caps T1/T2. Closes the tier-side axis collapse.
# CEILING NOTE: until step3 (L5 independence, D3) lands, l5_corroborated is never True in production ->
#   T0 is wired but UNREACHABLE -> operating ceiling = T1. step4 wires the path; step3 unlocks it.

import argparse, sys

try:
    from wire_provenance_L4 import tier_of_live   # step2 (which itself reuses frozen run_E39_probe)
except ImportError:
    sys.exit("wire_tier: wire_provenance_L4.py + run_E39_probe.py must be importable (same dir).")

# AXIS-G grade rank (SPEC sec1 hierarchy: RCT > observational > review > preprint > opinion).
# Venue-integrity flags (fringe / ID-venue / predatory / EoC) force LOW regardless of nominal grade.
GRADE_RANK = {
    "rct": 4, "observational": 3, "peer_reviewed": 3,
    "review": 2, "preprint": 1, "opinion": 0,
    "fringe": 0, "id_venue": 0, "predatory": 0, "eoc": 0,
}
G_FLOOR = 3   # SPEC D2: T0 requires >= observational/peer-reviewed

def grade_rank(grade):
    if grade is None:
        return None                      # unknown -> fail-closed (cannot confirm floor)
    return GRADE_RANK.get(str(grade).lower(), None)

def final_tier(prov_verdict, n_con, n_ent, S_size, grade, l5_corroborated, has_marker=True):
    """Assemble the SPEC tier from layer verdicts. The new step4 logic."""
    if not has_marker:
        return "T3"                      # markerless: ungrounded, not false (Central Law)
    l4 = tier_of_live(prov_verdict, n_con, n_ent, S_size)   # T4 / T1_BIND_* / T0_ELIGIBLE
    if l4 == "T4":
        return "T4"                      # provenance failed/fabricated/retracted
    # L1 pass + L2 clean from here.
    g = grade_rank(grade)
    if g is None:
        return "T1"                      # grade unknown -> fail-closed: cannot award T0; resolvable+clean -> T1
    if g < G_FLOOR:
        return "T2"                      # G-FLOOR fail -> grade-degraded (weak corroboration only)
    # grade passes floor:
    if l4 == "T0_ELIGIBLE" and l5_corroborated:
        return "T0"                      # all five layers + G-floor -> GOLD primary
    return "T1"                          # bind unchecked/contradicted OR not-yet-corroborated -> ceiling T1

# ---------------------------------------------------------------- selftest

def selftest():
    # (prov, n_con, n_ent, S, grade, l5_corrob, has_marker, want)
    cases = [
        ("T4_RETRACTED",  9,9,9, "rct",           True,  True,  "T4"),   # provenance fail dominates
        ("L1L2_PASS",     0,0,0, "rct",           True,  False, "T3"),   # markerless
        ("L1L2_PASS",     0,3,4, "preprint",      True,  True,  "T2"),   # G-FLOOR: bind holds + corrob but low grade -> T2
        ("L1L2_PASS",     0,3,4, "id_venue",      True,  True,  "T2"),   # venue-integrity low -> T2
        ("L1L2_PASS",     0,3,4, "observational", True,  True,  "T0"),   # the ONLY T0 path: grade>=floor + bind + L5
        ("L1L2_PASS",     0,3,4, "observational", False, True,  "T1"),   # grade+bind ok but NOT corroborated -> ceiling
        ("L1L2_PASS",     4,0,4, "rct",           True,  True,  "T1"),   # bind contradicted (D=1.0) -> T1 even at top grade
        ("L1L2_PASS",     0,0,0, "rct",           True,  True,  "T1"),   # empty S -> bind unchecked -> T1
        ("L1L2_PASS",     0,3,4, None,            True,  True,  "T1"),   # grade UNKNOWN -> fail-closed -> T1 (not T0)
    ]
    allok = True
    for prov, nc, ne, s, grade, l5c, mark, want in cases:
        got = final_tier(prov, nc, ne, s, grade, l5c, mark)
        ok = got == want
        allok &= ok
        print(f"  {'ok ' if ok else 'XX '} prov={prov:13} grade={str(grade):13} L5={int(l5c)} -> {got:3} want={want}")
    assert allok, "tier assembly mismatch"
    outs = {final_tier(*c[:7]) for c in cases}
    for t in ("T0", "T1", "T2", "T3", "T4"):
        assert t in outs, f"tier {t} unreachable in selftest (path collapse / VOID-by-construction)"
    # G-floor must block: same inputs, preprint vs observational -> T2 vs T0
    assert final_tier("L1L2_PASS",0,3,4,"preprint",True,True) == "T2", "G-floor not blocking preprint"
    assert final_tier("L1L2_PASS",0,3,4,"observational",True,True) == "T0", "T0 path broken"
    print("\nSELFTEST: PASS (all tiers T0-T4 reachable; G-floor blocks low-grade from T0; no collapse)")
    print("CEILING: in production l5_corroborated stays False until step3 -> T0 unreachable, ceiling T1 (by design).")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        ap.print_help()
