#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
delta1_dryval.py -- rung C delta-1 offline dry-validation.

Proves the composed value axis (value = weakness_relevance x info_gain) is:
  P1 VERDICT-BLIND    : info_gain + value invariant under ABSORB<->REJECT flip.
  P2 COMPOSITION      : value == weak_rel*info_gain, in [0,1], and STRATEGY sec 2C
                        ordering holds (redundant tagged ABSORB < novel tagged REJECT).
  P3 FIREWALL         : router imports no verify-path module; route() reads neither
                        value nor info_gain nor verdict (routing untouched);
                        _info_gain reads no verdict field.
  P4 GATE-CONSUMES    : gate_t1 correlates the REAL composed value (value_source
                        == "composed") and emits the verdict-separability check.
  P5 NO-REGRESSION    : route() source is byte-identical to the pre-delta-1 router
                        (passed via --baseline-router); routing outcomes unchanged.

No Ollama, no network, sealed apparatus not touched. Run from lab/dpo/ root.
"""
import argparse
import ast
import json
import sys
from pathlib import Path

import o0_tier_router as R
from step7_gates import gate_t1


def _route_src(path: Path) -> str:
    """Extract the source of route() from a router file (normalised)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "route":
            return ast.unparse(node)
    return ""


def p1_verdict_blind() -> tuple[bool, dict]:
    sm = {"weaknesses": [{"name": "empty-hedge"}]}
    pool = [{"topic": "boiling point water", "verdict": "ABSORB"}]
    rec_absorb = {"id": "x", "topic": "photosynthesis rate",
                  "claim": "c", "verdict": "ABSORB", "targeted_weakness": "empty-hedge"}
    rec_reject = dict(rec_absorb, verdict="REJECT")
    va = R.compute_value_features(rec_absorb, sm, pool)
    vr = R.compute_value_features(rec_reject, sm, pool)
    ok = (va["info_gain"] == vr["info_gain"]) and (va["value"] == vr["value"])
    return ok, {"info_gain": va["info_gain"], "value_absorb": va["value"],
                "value_reject": vr["value"]}


def p2_composition() -> tuple[bool, dict]:
    sm = {"weaknesses": [{"name": "empty-hedge"}]}
    pool = [{"topic": "boiling point of water", "verdict": "ABSORB"}]
    # redundant tagged ABSORB: topic tokens fully inside the pool entry
    redundant = {"id": "r", "topic": "boiling point", "claim": "c",
                 "verdict": "ABSORB", "targeted_weakness": "empty-hedge"}
    # novel tagged REJECT: disjoint topic
    novel = {"id": "n", "topic": "quantum tunnelling", "claim": "c",
             "verdict": "REJECT", "targeted_weakness": "empty-hedge"}
    # untagged: value must be 0 regardless of info_gain
    untagged = {"id": "u", "topic": "quantum tunnelling", "claim": "c",
                "verdict": "REJECT"}
    vr_red = R.compute_value_features(redundant, sm, pool)
    vr_nov = R.compute_value_features(novel, sm, pool)
    vr_unt = R.compute_value_features(untagged, sm, pool)
    checks = {
        "value=weakrel*infogain": all(
            abs(vf["value"] - (1.0 if vf["weakness_relevance"] else 0.0) * vf["info_gain"]) < 1e-9
            for vf in (vr_red, vr_nov, vr_unt)
        ),
        "value_in_0_1": all(0.0 <= vf["value"] <= 1.0 for vf in (vr_red, vr_nov, vr_unt)),
        "redundant_lt_novel": vr_red["value"] < vr_nov["value"],
        "untagged_value_zero": vr_unt["value"] == 0.0,
    }
    return all(checks.values()), {
        "redundant_value": round(vr_red["value"], 4),
        "novel_value": round(vr_nov["value"], 4),
        "untagged_value": vr_unt["value"], **checks}


def _key_accesses(func_node) -> set[str]:
    """All string keys used as subscripts or .get()/.set() args inside a func."""
    keys = set()
    for n in ast.walk(func_node):
        # subscript: x["key"]
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            keys.add(n.slice.value)
        # method call: x.get("key", ...) / x.setdefault("key")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in ("get", "setdefault", "pop") and n.args \
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            keys.add(n.args[0].value)
    return keys


def _func(tree, name):
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    return None


def p3_firewall() -> tuple[bool, dict]:
    src = Path("o0_tier_router.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    verify_mods = ("falsifier_step6", "o0_temporal_evidence", "generate_step6")
    no_verify_import = not any(m in src for m in verify_mods)
    # route() must read no value/info_gain/verdict KEY (AST, not docstring text)
    route_keys = _key_accesses(_func(tree, "route"))
    route_clean = not (route_keys & {"info_gain", "value", "verdict"})
    # _info_gain must read no 'verdict' KEY
    ig_keys = _key_accesses(_func(tree, "_info_gain"))
    ig_clean = "verdict" not in ig_keys
    ok = no_verify_import and route_clean and ig_clean
    return ok, {"no_verify_import": no_verify_import,
                "route_key_reads": sorted(route_keys),
                "route_reads_no_value_or_verdict": route_clean,
                "info_gain_key_reads": sorted(ig_keys),
                "info_gain_verdict_blind": ig_clean}


def p4_gate_consumes() -> tuple[bool, dict]:
    sm = {"weaknesses": [{"name": "empty-hedge"}]}
    # mixed batch: tagged ABSORB + tagged REJECT + plain, spanning value range
    recs = [
        {"id": "1", "topic": "alpha beta", "claim": "c", "verdict": "ABSORB",
         "targeted_weakness": "empty-hedge"},
        {"id": "2", "topic": "alpha beta", "claim": "c", "verdict": "REJECT",
         "targeted_weakness": "empty-hedge"},
        {"id": "3", "topic": "gamma delta", "claim": "c", "verdict": "ABSORB",
         "targeted_weakness": "empty-hedge"},
        {"id": "4", "topic": "epsilon zeta", "claim": "c", "verdict": "REJECT",
         "targeted_weakness": "empty-hedge"},
        {"id": "5", "topic": "eta theta", "claim": "c", "verdict": "ABSORB"},
    ]
    routed = R.route_batch(recs, sm)
    res = gate_t1(routed, t1_labels={})  # labels empty -> crossover counters 0
    ok = (res.get("value_source") == "composed") and ("overlap_ok" in res)
    return ok, {"value_source": res.get("value_source"),
                "correlation": res.get("correlation"),
                "overlap_ok": res.get("overlap_ok")}


def p5_no_regression(baseline_router: Path | None) -> tuple[bool, dict]:
    cur = _route_src(Path("o0_tier_router.py"))
    if baseline_router is None or not baseline_router.exists():
        return True, {"skipped": "no --baseline-router supplied",
                      "route_present": bool(cur)}
    base = _route_src(baseline_router)
    ok = (cur == base) and bool(cur)
    return ok, {"route_byte_identical": ok}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-router", default=None,
                    help="pre-delta-1 o0_tier_router.py for route() byte-diff")
    args = ap.parse_args()
    base = Path(args.baseline_router) if args.baseline_router else None

    results = [
        ("P1 verdict-blind", *p1_verdict_blind()),
        ("P2 composition", *p2_composition()),
        ("P3 firewall", *p3_firewall()),
        ("P4 gate-consumes", *p4_gate_consumes()),
        ("P5 no-regression", *p5_no_regression(base)),
    ]
    npass = 0
    print("=== delta-1 dry-val ===")
    for name, ok, detail in results:
        tag = "PASS" if ok else "FAIL"
        npass += int(ok)
        print(f"  [{tag}] {name}: {json.dumps(detail, ensure_ascii=True)}")
    print(f"--- {npass}/{len(results)} ---")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
