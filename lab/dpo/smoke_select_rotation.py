#!/usr/bin/env python
"""SMOKE: SELECT rotation floor (BUILD-FRONT #2).
VIOLATION-A safe: runs in a TEMP CWD with a TEMP goal_stack.json; never reads or
mutates the real goal_stack.json in place. SELF-CONTAINED: uses an EMBEDDED 3-weakness
fixture (high/high/med) mirroring the real self_model topology, so the smoke is
clone-coherent (no dependency on the ignored, held-out-adjacent self_model.json) and
privacy-clean. Drives N synthetic SELECT->mark_worked cycles (no GENERATE/VERIFY/ABSORB,
no oracle, verdict-blind) and asserts every weakness rotates and the lone med is picked.

PASS-BAR:
  (1) the lone med weakness ('empty-hedge') SELECTed >= 1 time
  (2) all 3 weakness names appear in the SELECT sequence
"""
import json, shutil, sys, tempfile, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
N_CYCLES = 9  # >= 3 full rotations for a 3-weakness model

# Embedded fixture: SAME topology as the real self_model (two 'high' + one 'med').
# This is the structural condition that starved the med under severity-primary sort.
FIXTURE = {
    "version": "smoke_fixture",
    "n_weaknesses": 3,
    "weaknesses": [
        {"name": "fabricated-specifics",    "severity": "high"},
        {"name": "overconfident-no-source", "severity": "high"},
        {"name": "empty-hedge",             "severity": "med"},
    ],
}

def main():
    sm = FIXTURE
    names = [w["name"] for w in sm["weaknesses"]]

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # isolate: copy controller into temp, run there; real CWD untouched
        shutil.copy2(HERE / "controller.py", td / "controller.py")
        # stub the one hard top-level dep (citation_verify) so import resolves; the
        # smoke exercises ONLY select_weakness/GoalStack, never verify -> firewall N/A.
        (td / "citation_verify.py").write_text(
            "DIRTY='DIRTY'\n"
            "def verify_citation(*a, **k):\n    raise NotImplementedError\n"
            "class CrossrefOracle:\n    pass\n", encoding="utf-8")
        sys.path.insert(0, str(td))
        old_cwd = os.getcwd()
        os.chdir(td)  # GoalStack() defaults to ./goal_stack.json -> temp only
        try:
            import importlib
            ctl = importlib.import_module("controller")
            gstack = ctl.GoalStack()  # fresh, temp-pathed
            selected = []
            for _ in range(N_CYCLES):
                gstack.state["cycle"] += 1
                w = ctl.select_weakness(sm, gstack)
                selected.append(w["name"])
                # synthetic outcome; verdict-blind, value irrelevant to SELECT
                gstack.mark_worked(w["name"], observed_rate_f=0.5,
                                   baseline=0.5, improved=False)
                gstack.save()
        finally:
            os.chdir(old_cwd)
            sys.path.remove(str(td))

    from collections import Counter
    counts = Counter(selected)
    eh = counts.get("empty-hedge", 0)
    all3 = set(names) <= set(selected)

    print("SELECT sequence :", " ".join(selected))
    print("counts          :", dict(counts))
    print(f"empty-hedge x{eh}  | all-3-rotate={all3}")
    p1 = eh >= 1
    p2 = all3
    print(f"PASS-BAR (1) empty-hedge>=1 : {'PASS' if p1 else 'FAIL'}")
    print(f"PASS-BAR (2) all-3-appear   : {'PASS' if p2 else 'FAIL'}")
    ok = p1 and p2
    print("SMOKE", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
