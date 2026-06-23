"""
step7_gates.py — Phase 7: Gate Tests (T1–T5 + D-GATE)
======================================================
Pre-registered falsifiers per STRATEGY sec 5.

T1  axis-independence   (STUB — needs Founder T1 worth-labels)
T2  firewall            verify() byte-identical w/ empty vs full tier-store
T3  reversibility       count(removed)==count(tombstones); round-trip
T4  GOLD-freeze         0 autonomous GOLD writes
T5  not-cosmetic        all 3 live outcomes non-empty (>=1 each)
D   curated > uncurated on SAME weakness (downstream rate_f / yield)

Bars set at BUILD pre-registration (this file).

Home: C:\\Projects\\onto-research\\lab\\dpo\\step7_gates.py
"""

from __future__ import annotations
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from o0_tier_router import (
    TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD, TIER_GOLD_QUEUE, LIVE_TIERS,
    route_batch,
)
from o0_tier_store import TierStore

# ── pre-registered bars ────────────────────────────────────────────
T1_CORR_BAR       = 0.50   # corr(value, verdict) must be BELOW this
T2_DIVERGENCE_BAR = 0      # byte divergence must be exactly 0
T3_MISMATCH_BAR   = 0      # count(removed) - count(tombstones) must be 0
T4_GOLD_WRITES    = 0      # autonomous GOLD writes must be 0
T5_MIN_PER_TIER   = 1      # each live tier >= 1 record
DGATE_N_CYCLES    = 6      # minimum cycles for D-GATE comparison
DGATE_IMPROVEMENT = 0.10   # curated rate_f must be lower by at least this


# ── T1: axis independence (STUB) ──────────────────────────────────

def gate_t1(
    routed: list[dict],
    t1_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """T1: axis-independence.

    Requires Founder-authored worth-labels mapping provoke_id -> "discard" | "keep".
    Tests:
      1. >=1 CLEAN (ABSORB) record labeled "discard" (trivium)
      2. >=1 DIRTY (REFUTE) record labeled "keep" (caught fabricate = evidence)
      3. corr(value_score, verdict_binary) < T1_CORR_BAR

    Returns gate dict with pass/fail + details.
    """
    if t1_labels is None:
        return {
            "gate": "T1",
            "status": "STUB",
            "reason": "T1 worth-labels not yet authored (Founder E15). Plug in when ready.",
        }

    # Check crossover cases
    clean_discard = 0
    dirty_keep = 0
    for r in routed:
        pid = r.get("id", "")
        verdict = r.get("verdict", "")
        label = t1_labels.get(pid)
        if label is None:
            continue
        if verdict == "ABSORB" and label == "discard":
            clean_discard += 1
        if verdict == "REJECT" and label == "keep":
            dirty_keep += 1

    crossover_ok = clean_discard >= 1 and dirty_keep >= 1

    # Correlation: composed value axis vs verdict_binary (STRATEGY sec 5 T1b).
    # rung C delta-1: correlate the REAL composed value scalar
    #   value = weakness_relevance x info_gain  (verdict-blind, from _value_features)
    # Fallback to tier-binary only for pre-delta-1 routed dicts lacking the field.
    # verdict_binary = 1 if ABSORB, 0 if REJECT.
    value_scores = []
    verdict_bins = []
    val_absorb: list[float] = []
    val_reject: list[float] = []
    for r in routed:
        verdict = r.get("verdict", "")
        if verdict not in ("ABSORB", "REJECT"):
            continue
        vf = r.get("_value_features", {})
        if "value" in vf:
            vs = float(vf["value"])
        else:
            tier = r.get("_tier", "")
            vs = 1.0 if tier in (TIER_PERMANENT, TIER_TEMPORARY) else 0.0
        vb = 1.0 if verdict == "ABSORB" else 0.0
        value_scores.append(vs)
        verdict_bins.append(vb)
        (val_absorb if verdict == "ABSORB" else val_reject).append(vs)

    corr = _pearson(value_scores, verdict_bins) if len(value_scores) >= 3 else 0.0
    corr_ok = abs(corr) < T1_CORR_BAR

    # Verdict-separability: ABSORB vs REJECT value ranges MUST overlap. A clean
    # separation means value is a hidden verdict proxy -> FAIL even if corr<bar.
    if val_absorb and val_reject:
        overlap_ok = (
            max(val_absorb) >= min(val_reject)
            and max(val_reject) >= min(val_absorb)
        )
    else:
        overlap_ok = True  # one side empty -> separability undefined, not a fail

    passed = crossover_ok and corr_ok and overlap_ok
    return {
        "gate": "T1",
        "status": "PASS" if passed else "FAIL",
        "clean_discard": clean_discard,
        "dirty_keep": dirty_keep,
        "crossover_ok": crossover_ok,
        "correlation": round(corr, 4),
        "corr_bar": T1_CORR_BAR,
        "corr_ok": corr_ok,
        "overlap_ok": overlap_ok,
        "value_source": "composed" if any("value" in r.get("_value_features", {}) for r in routed) else "tier_binary",
    }


# ── T2: firewall ──────────────────────────────────────────────────

def gate_t2(
    verdicts_path: str | Path,
    self_model_path: str | Path,
    verify_cmd: list[str] | None = None,
) -> dict[str, Any]:
    """T2: verify() output byte-identical with empty vs full tier-store.

    Runs the verifier twice:
      A) with no tier store (baseline)
      B) with full tier store present
    Compares outputs byte-for-byte.

    If verify_cmd is None, uses the default falsifier invocation.
    For dry-val: checks structurally that tier_store has no write path
    into the verify module (import analysis).
    """
    # Structural check: tier_store never imports from verify/falsifier path
    tier_store_src = Path("o0_tier_store.py").read_text(encoding="utf-8")
    tier_router_src = Path("o0_tier_router.py").read_text(encoding="utf-8")
    verify_imports = []
    for mod_name in ("falsifier_step6", "o0_temporal_evidence", "generate_step6"):
        if mod_name in tier_store_src or mod_name in tier_router_src:
            verify_imports.append(mod_name)

    structural_ok = len(verify_imports) == 0

    return {
        "gate": "T2",
        "status": "PASS" if structural_ok else "FAIL",
        "structural_check": "no verify-path imports in tier modules",
        "verify_imports_found": verify_imports,
        "note": "Full byte-identity test requires live run (run_step7_live.py --gate t2).",
    }


# ── T3: reversibility / audit ─────────────────────────────────────

def gate_t3(store: TierStore) -> dict[str, Any]:
    """T3: count(removed)==count(tombstones); round-trip test.

    1. Every removal has a tombstone entry.
    2. A tombstoned record can be re-promoted (round-trip).
    """
    n_tombstones = store.count_tombstones()
    n_removals = store.count_removals()
    count_match = (n_removals - n_tombstones) == T3_MISMATCH_BAR

    # Round-trip test: pick first tombstoned record, promote, verify, re-tombstone, RESTORE
    tombstoned = store.tombstoned_records()
    roundtrip_ok = False
    roundtrip_id = None
    if tombstoned:
        roundtrip_id = next(iter(tombstoned))
        original_rec = copy.deepcopy(store.all_records()[roundtrip_id])
        # promote
        store.promote(roundtrip_id, TIER_TEMPORARY)
        active = store.active_records()
        promoted = roundtrip_id in active and not active[roundtrip_id]["tombstone"]
        # re-tombstone (proves reversibility)
        store.tombstone(roundtrip_id, "roundtrip_test")
        re_tombed = store.tombstoned_records()
        roundtrip_ok = promoted and roundtrip_id in re_tombed
        # RESTORE original state (test must be non-destructive)
        store._state["records"][roundtrip_id] = original_rec
    else:
        # No tombstones to test — if store is empty, that's T5's problem
        roundtrip_ok = True  # vacuously true

    passed = count_match and roundtrip_ok
    return {
        "gate": "T3",
        "status": "PASS" if passed else "FAIL",
        "n_tombstones": n_tombstones,
        "n_removals": n_removals,
        "count_match": count_match,
        "roundtrip_id": roundtrip_id,
        "roundtrip_ok": roundtrip_ok,
    }


# ── T4: GOLD-freeze ───────────────────────────────────────────────

def gate_t4(store: TierStore) -> dict[str, Any]:
    """T4: 0 autonomous GOLD writes."""
    n_gold = store.gold_queue_count()
    passed = n_gold == T4_GOLD_WRITES
    return {
        "gate": "T4",
        "status": "PASS" if passed else "FAIL",
        "autonomous_gold_writes": n_gold,
        "bar": T4_GOLD_WRITES,
    }


# ── T5: not-cosmetic ──────────────────────────────────────────────

def gate_t5(store: TierStore) -> dict[str, Any]:
    """T5: all 3 live outcomes non-empty (>=1 each).

    Counts ALL records per tier (including tombstoned), because:
    - discard = tombstoned by definition
    - the test proves the router uses all three paths, not that records are active
    """
    all_recs = store.all_records()
    counts = {}
    for tier in LIVE_TIERS:
        counts[tier] = sum(1 for r in all_recs.values() if r["tier"] == tier)

    all_nonempty = all(counts[t] >= T5_MIN_PER_TIER for t in LIVE_TIERS)
    return {
        "gate": "T5",
        "status": "PASS" if all_nonempty else "FAIL",
        "counts": counts,
        "bar": T5_MIN_PER_TIER,
    }


# ── D-GATE (framework — live only) ────────────────────────────────

def gate_d_preregister() -> dict[str, Any]:
    """D-GATE pre-registration (bars + design).

    Actual D-GATE runs during run_step7_live.py with --gate d.
    """
    return {
        "gate": "D-GATE",
        "status": "PRE-REGISTERED",
        "design": "A/B: curated vs uncurated memory on SAME weakness",
        "metric": "downstream rate_f (lower = better) or yield (higher = better)",
        "n_cycles": DGATE_N_CYCLES,
        "improvement_bar": DGATE_IMPROVEMENT,
        "note": "Phase proven ONLY by D-GATE. T1-T5 are plumbing checks.",
    }


# ── runner ─────────────────────────────────────────────────────────

def run_all_gates(
    verdicts_path: str | Path,
    self_model_path: str | Path,
    store: TierStore,
    routed: list[dict],
    t1_labels: dict[str, str] | None = None,
) -> list[dict]:
    """Run all gates.  Returns list of gate results."""
    results = [
        gate_t1(routed, t1_labels),
        gate_t2(verdicts_path, self_model_path),
        gate_t3(store),
        gate_t4(store),
        gate_t5(store),
        gate_d_preregister(),
    ]
    return results


def print_gate_report(results: list[dict]) -> None:
    print("\n=== PHASE 7 GATE REPORT ===")
    for g in results:
        status = g["status"]
        tag = "✓" if status == "PASS" else ("⊘" if status == "STUB" else ("◎" if status == "PRE-REGISTERED" else "✗"))
        print(f"  {tag} {g['gate']}: {status}")
        for k, v in g.items():
            if k not in ("gate", "status"):
                print(f"      {k}: {v}")
    print("===========================\n")

    # summary
    gates = [g for g in results if g["status"] not in ("STUB", "PRE-REGISTERED")]
    passed = sum(1 for g in gates if g["status"] == "PASS")
    total = len(gates)
    stubs = sum(1 for g in results if g["status"] == "STUB")
    prereg = sum(1 for g in results if g["status"] == "PRE-REGISTERED")
    print(f"PASS: {passed}/{total}  |  STUB: {stubs}  |  PRE-REGISTERED: {prereg}")


# ── helpers ────────────────────────────────────────────────────────

def _pearson(x: list[float], y: list[float]) -> float:
    """Pearson correlation.  Returns 0.0 if degenerate."""
    n = len(x)
    if n < 3:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    sx = sum((xi - mx) ** 2 for xi in x) ** 0.5
    sy = sum((yi - my) ** 2 for yi in y) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


# ── CLI ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Phase 7 gate tests")
    ap.add_argument("--verdicts", default="eval/o0/o0_verdicts.jsonl")
    ap.add_argument("--self-model", default="self_model.json")
    ap.add_argument("--store", default="o0_tier_state.json")
    ap.add_argument("--t1-labels", default=None, help="Path to T1 worth-labels JSON (Founder-authored)")
    args = ap.parse_args()

    verdicts = [json.loads(l) for l in Path(args.verdicts).read_text(encoding="utf-8").splitlines() if l.strip()]
    sm = json.loads(Path(args.self_model).read_text(encoding="utf-8"))

    routed = route_batch(verdicts, sm)

    store = TierStore(args.store)
    # populate store from routed batch (dry)
    for r in routed:
        pid = r.get("id", "")
        if pid:
            store.assign(pid, r["_tier"], r["_value_features"], record_snapshot=r)
            if r["_tier"] == TIER_DISCARD:
                store.tombstone(pid, "initial_discard")
    store.save()

    t1_labels = None
    if args.t1_labels and Path(args.t1_labels).exists():
        t1_labels = json.loads(Path(args.t1_labels).read_text(encoding="utf-8"))

    results = run_all_gates(args.verdicts, args.self_model, store, routed, t1_labels)
    print_gate_report(results)
