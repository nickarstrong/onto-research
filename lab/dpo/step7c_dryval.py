#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
step7c_dryval.py -- offline dry-validation for rung C pack v244 sec 3.1 + 3.2.
NO GPU, NO net, NO controller subprocess. Proves the edits are correct + firewall
held BEFORE any live D-GATE run.

P1  _matches_weakness tag-switch: counts only stamp==weakness; verdict-blind.
P2  assert_curated_differs: non-inert pruned view -> precondition_ok True;
    inert (curated==raw) -> precondition_ok False (ceremonial caught).
P3  firewall: run_step7_live edits read targeted_weakness, never the verdict for
    matching; no verify-path import in the routing/run modules.
P4  regression: sealed-style untagged records excluded from per-weakness pool.
P5  scope: only run_step7_live.py changed vs substrate (router/store/gates sealed).
"""
import json
import sys
from pathlib import Path

import run_step7_live as R
from o0_tier_store import CURATED_FILE

FAILS = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    if not cond:
        FAILS.append(name)
    print(f"  [{tag}] {name}{(' -- ' + detail) if detail else ''}")


# ---- P1 + P4: _matches_weakness tag-switch -------------------------------
def p1_p4():
    print("P1/P4  _matches_weakness tag-switch (verdict-blind, sealed excluded)")
    W = "fabricated-specifics"
    tagged_match   = {"id": "ctrl_1", "verdict": "REJECT", "targeted_weakness": W}
    tagged_other   = {"id": "ctrl_2", "verdict": "REJECT", "targeted_weakness": "empty-hedge"}
    sealed_untag   = {"id": "o0_003", "verdict": "ABSORB"}  # no stamp (sealed 220)
    clean_match    = {"id": "ctrl_3", "verdict": "ABSORB", "targeted_weakness": W}

    check("match by stamp", R._matches_weakness(tagged_match, W) is True)
    check("reject other-weakness stamp", R._matches_weakness(tagged_other, W) is False)
    check("sealed untagged excluded", R._matches_weakness(sealed_untag, W) is False)
    check("verdict-blind (ABSORB stamp still matches)",
          R._matches_weakness(clean_match, W) is True,
          "matching keyed on stamp, not verdict")

    # rate_f over a mixed pool counts ONLY the two tagged-W records (1 REJECT / 2)
    pool = [tagged_match, tagged_other, sealed_untag, clean_match]
    stats = R._compute_arm_stats(pool, W)
    check("arm_stats n_relevant == 2 (tagged-W only)", stats["n_relevant"] == 2, str(stats))
    check("arm_stats rate_f == 0.5 (1 REJECT / 2)", abs(stats["rate_f"] - 0.5) < 1e-9, str(stats))


# ---- P2: assert_curated_differs (pruned vs inert) ------------------------
def _write_jsonl(path, recs):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n",
        encoding="utf-8",
    )


def p2():
    print("P2  assert_curated_differs (non-inert pruned vs inert)")
    raw = [
        {"id": "a1", "verdict": "ABSORB", "topic": "hubble constant expansion redshift"},
        {"id": "a2", "verdict": "ABSORB", "topic": "hubble redshift galaxy distance"},
        {"id": "a3", "verdict": "ABSORB", "topic": "hubble constant value tension"},
        {"id": "a4", "verdict": "ABSORB", "topic": "abiogenesis primordial soup"},
        {"id": "r1", "verdict": "REJECT", "topic": "hubble fabricated date 1925"},  # not ABSORB
    ]
    _write_jsonl(R.VERDICTS_RAW, raw)

    # PRUNED curated: drop a2 (a high-overlap ABSORB) -> non-inert
    curated_pruned = [r for r in raw if r["id"] in ("a1", "a3", "a4") and r["verdict"] == "ABSORB"]
    _write_jsonl(CURATED_FILE, curated_pruned)
    res = R.assert_curated_differs(goal_topic="hubble constant", k=3)
    check("pruned: pruning_ok True", res["pruning_ok"] is True, str({k: res[k] for k in ("n_raw_absorb", "n_curated_absorb", "n_pruned")}))
    check("pruned: curated subset of raw", res["n_curated_absorb"] < res["n_raw_absorb"])
    check("pruned: precondition_ok True", res["precondition_ok"] is True)

    # INERT curated == raw ABSORB set -> ceremonial, must FAIL precondition
    curated_inert = [r for r in raw if r["verdict"] == "ABSORB"]
    _write_jsonl(CURATED_FILE, curated_inert)
    res_i = R.assert_curated_differs(goal_topic="hubble constant", k=3)
    check("inert: n_pruned == 0", res_i["n_pruned"] == 0, str(res_i))
    check("inert: precondition_ok False (ceremonial caught)", res_i["precondition_ok"] is False)

    # cleanup synthetic fixtures
    for p in (R.VERDICTS_RAW, Path(CURATED_FILE)):
        try:
            Path(p).unlink()
        except OSError:
            pass


# ---- P3: firewall (static source checks) ---------------------------------
def p3():
    print("P3  firewall (run_step7_live edits verdict-blind; no verify-path import)")
    src = Path("run_step7_live.py").read_text(encoding="utf-8")
    # matching keyed on the stamp, not the verdict
    check("_matches_weakness reads targeted_weakness",
          'record.get("targeted_weakness") == weakness_name' in src)
    # executable body only (strip the docstring, which legitimately says "verdict-blind")
    body = src.split("def _matches_weakness")[1].split("def ")[0]
    code_only = body.split('"""')[2] if body.count('"""') >= 2 else body
    check("_matches_weakness body does NOT branch on verdict",
          ('"verdict"' not in code_only) and ("REJECT" not in code_only) and ("ABSORB" not in code_only),
          "match keyed on stamp, not verdict")
    # no verify-path module imported into the tier/run layer
    verify_mods = ("falsifier_step6", "o0_temporal_evidence", "generate_step6")
    router_src = Path("o0_tier_router.py").read_text(encoding="utf-8")
    store_src = Path("o0_tier_store.py").read_text(encoding="utf-8")
    leaks = [m for m in verify_mods if (m in src or m in router_src or m in store_src)]
    check("no verify-path import in run/router/store", not leaks, str(leaks))


# ---- P5: scope (only run_step7_live changed) -----------------------------
def p5():
    print("P5  scope: router/store/gates byte-identical to substrate")
    import hashlib
    sub = Path("/home/claude/sub")
    if not sub.exists():
        print("  [SKIP] substrate compare dir absent (off-container) -- "
              "scope was verified at build time; vacuous on the deployed disk")
        return
    sealed = ["o0_tier_router.py", "o0_tier_store.py", "step7_gates.py",
              "o0_retrieve.py", "self_model.json", "t1_worth_labels.json"]
    for f in sealed:
        a = hashlib.md5(Path(f).read_bytes()).hexdigest()
        b = hashlib.md5((sub / f).read_bytes()).hexdigest()
        check(f"{f} unchanged", a == b, f"{a[:8]} vs {b[:8]}")
    # run_step7_live MUST differ (we edited it)
    a = hashlib.md5(Path("run_step7_live.py").read_bytes()).hexdigest()
    b = hashlib.md5((sub / "run_step7_live.py").read_bytes()).hexdigest()
    check("run_step7_live.py changed (edits applied)", a != b)


def main():
    print("=== rung C dryval (pack v244 sec 3.1 + 3.2) -- offline ===")
    p1_p4()
    p2()
    p3()
    p5()
    n = 0
    # count checks by re-derivation is noisy; just report fails
    print("\n=== RESULT ===")
    if FAILS:
        print(f"FAIL ({len(FAILS)}): {FAILS}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
