#!/usr/bin/env python3
# o0_tiering_gate_v324.py
# Knowledge-tiering ADMISSION GATE (v324, TYPE-A).
# Pure routing policy OVER existing certified verdicts. Adds NO verdict logic.
# Frozen verifier seam (discriminator 92D46A55 + L2 oracle/numprop/driver) NOT touched.
# Authority: GENGAP_tiering_design_v323.md sec 1.
#
# Hermetic: no network, no GPU, no oracle re-run. Deterministic pure function.
# Monotone vs naive admit-all: can ONLY down-route (GOLD->MEMORY, MEMORY->REJECT),
# NEVER promote an unverified/contradicted claim to GOLD.

from __future__ import annotations

# --- tiers (routing targets) -------------------------------------------------
GOLD = "GOLD"        # durable substrate
MEMORY = "MEMORY"    # temporary memory (re-admittable later when grounded)
REJECT = "REJECT"    # never written; admission error (contradicted claim)

TIERS = frozenset({GOLD, MEMORY, REJECT})

# --- verdicts consumed (produced by the FROZEN certified verifier stack) ------
DIRTY = "DIRTY"
ABSTAIN = "ABSTAIN"
CLEAN = "CLEAN"

VERDICTS = frozenset({DIRTY, ABSTAIN, CLEAN})


def route(verdict, grounded):
    """Map a verifier verdict tuple to an admission tier.

    Policy (design sec 1, immovable DIRTY/ABSTAIN floors):
      DIRTY              -> REJECT   (contradicted claim = frameshift, R7/C8)
      ABSTAIN            -> MEMORY   (honest floor; unverified != GOLD; B0-ABSOLUTE)
      CLEAN + grounded   -> GOLD     (CLEAN necessary, grounding sufficient, R4)
      CLEAN + ungrounded -> MEMORY   (R4 admission not satisfied)

    Fail-closed:
      - unrecognized verdict          -> ValueError (build fault, never silent admit).
      - CLEAN with non-True grounded   -> MEMORY (only `grounded is True` admits;
                                          None/missing/falsey never reaches GOLD).
    """
    if verdict not in VERDICTS:
        raise ValueError("unrecognized verdict: %r (expected one of %s)"
                         % (verdict, sorted(VERDICTS)))

    if verdict == DIRTY:
        return REJECT
    if verdict == ABSTAIN:
        return MEMORY
    # verdict == CLEAN
    return GOLD if grounded is True else MEMORY


def route_row(row):
    """Route a held-out row dict {'verdict', 'grounded'}. Strict, fail-closed.

    Missing 'verdict' -> ValueError. Missing 'grounded' on a CLEAN row -> ungrounded.
    """
    if "verdict" not in row:
        raise ValueError("row missing 'verdict': %r" % (row,))
    return route(row["verdict"], row.get("grounded", False))


# --- invariant self-test (run at import-as-script; cheap, hermetic) -----------
def _self_test():
    # 4 policy lines
    assert route(DIRTY, True) == REJECT
    assert route(DIRTY, False) == REJECT
    assert route(ABSTAIN, True) == MEMORY    # grounded ignored for ABSTAIN
    assert route(ABSTAIN, False) == MEMORY
    assert route(CLEAN, True) == GOLD
    assert route(CLEAN, False) == MEMORY

    # fail-closed: only CLEAN+True reaches GOLD -> the ONLY GOLD-admitting input
    gold_inputs = [(v, g) for v in VERDICTS for g in (True, False)
                   if route(v, g) == GOLD]
    assert gold_inputs == [(CLEAN, True)], gold_inputs

    # fail-closed: non-True grounded never admits CLEAN to GOLD
    for g in (False, None, 0, "", "true", 1):
        assert route(CLEAN, g) == (GOLD if g is True else MEMORY)

    # unrecognized verdict raises (never silent admit)
    for bad in ("dirty", "Clean", "", None, "GOLD"):
        try:
            route(bad, True)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for verdict=%r" % (bad,))

    # monotonicity: every routed tier is a valid tier
    for v in VERDICTS:
        for g in (True, False):
            assert route(v, g) in TIERS
    return True


if __name__ == "__main__":
    assert _self_test()
    # 1-row smoke (design sec, Step 4 pass criterion: imports + runs on 1 row)
    smoke = {"id": "smoke:0", "verdict": CLEAN, "grounded": True}
    print("SELF-TEST: PASS")
    print("SMOKE route_row(%s) -> %s" % (smoke, route_row(smoke)))
