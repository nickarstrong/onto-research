"""
run_step7_live.py — Phase 7: Live Runner
=========================================
Wraps the existing SELECT→GENERATE→VERIFY→ABSORB cycle with post-verdict
tier routing.  Does NOT reopen the sealed cycle or verify path.

Modes:
  --dry          Route existing verdicts, run T2-T5 gates (delegates to step7_dryval)
  --live N       Run N cycles with tier routing after each verdict
  --gate t2      Run T2 live firewall check (verify byte-identity)
  --gate d       Run D-GATE A/B: curated vs uncurated, N cycles per arm

INTEGRATION ASSUMPTIONS (verify against on-disk code before first live run):
  A1. controller.py has run_one_cycle(verdicts_path=...) or equivalent
  A2. o0_retrieve.py reads from the path passed to it (not hardcoded)
  A3. o0_verdicts.jsonl is append-only; new verdict = last line after cycle
  A4. self_model.json and gold_frame.txt are in lab\\dpo\\ root

If any assumption fails, the INTEGRATION LAYER (marked below) must be
adapted. The tier-routing logic (router + store + gates) is substrate-
independent.

Home: C:\\Projects\\onto-research\\lab\\dpo\\run_step7_live.py
"""

from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

from o0_tier_router import (
    compute_value_features, route, route_batch,
    TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD,
)
from o0_tier_store import TierStore, CURATED_FILE, TOMBSTONE_LOG
from step7_gates import (
    run_all_gates, print_gate_report,
    gate_t2, gate_d_preregister, DGATE_N_CYCLES, DGATE_IMPROVEMENT,
)

# ── paths ──────────────────────────────────────────────────────────
VERDICTS_RAW    = Path("eval/o0/o0_verdicts.jsonl")
VERDICTS_BACKUP = Path("eval/o0/o0_verdicts_uncurated.jsonl")
SELF_MODEL      = Path("self_model.json")
STORE_PATH      = Path("o0_tier_state.json")
DGATE_LOG       = Path("eval/o0/dgate_log.jsonl")


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION LAYER — adapt to on-disk controller interface
# ═══════════════════════════════════════════════════════════════════

def _read_verdicts(path: Path) -> list[dict]:
    """Read verdict records from JSONL."""
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _run_one_controller_cycle(
    verdicts_source: Path,
    cycle_index: int,
    conditioned: bool = False,
) -> dict | None:
    """Run one SELECT→GENERATE→VERIFY→ABSORB cycle via the sealed controller.

    INTEGRATION POINT — verify on disk:
      Option A (import): from controller import Controller; c.run_one_cycle(...)
      Option B (subprocess): subprocess.run(["python", "run_step6_live.py", "--cycles", "1", ...])

    Returns the new verdict record (last line of verdicts file after cycle),
    or None if cycle produced no new verdict (e.g. CONTACT/skip).

    CURRENT: skeleton that reads the NEW last line after delegating.
    Tommy: wire to actual controller invocation before first live run.
    """
    before_count = _count_lines(VERDICTS_RAW)

    # ── WIRE (subprocess -> sealed controller, real interface) ──────
    # controller.py --live runs ONE SELECT->GENERATE->VERIFY->ABSORB cycle and
    # appends verdict record(s) to eval/o0/o0_verdicts.jsonl (== VERDICTS_RAW).
    # --n 1 => one generated claim => one appended record => lossless 1:1 routing
    # (matches this function's single-record return contract).
    #
    # rung C delta-2 (live): the curated view NOW causally shapes generation.
    # conditioned=True -> controller routes the CURATED view (verdicts_source) +
    # GOLD frame into the proposer ONLY; verify() stays sealed (firewall, pack 3.2).
    # conditioned=False -> BLIND proposer (no memory). Arms are thus differentiable.
    import subprocess
    argv = [sys.executable, "controller.py", "--live", "--cycles", "1", "--n", "1"]
    if conditioned:
        argv += ["--conditioned",
                 "--curated-path", str(verdicts_source),
                 "--gold-frame", "gold_frame.txt"]
    subprocess.run(
        argv,
        check=True,
        cwd=str(Path(__file__).resolve().parent),
    )
    # ── END WIRE ───────────────────────────────────────────────

    after_count = _count_lines(VERDICTS_RAW)
    if after_count > before_count:
        last_line = VERDICTS_RAW.read_text(encoding="utf-8").splitlines()[-1]
        return json.loads(last_line)
    return None


def _count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


# ═══════════════════════════════════════════════════════════════════
# TIER-ROUTING LOGIC (substrate-independent)
# ═══════════════════════════════════════════════════════════════════

def route_new_verdict(
    record: dict,
    store: TierStore,
    sm: dict,
) -> str:
    """Route a single new verdict through the tier router and update store."""
    existing = list(store.active_records().values())
    # use snapshots from store for novelty check
    absorb_pool = [
        r.get("snapshot", {}) for r in existing
        if r.get("snapshot", {}).get("verdict") == "ABSORB"
    ]

    vf = compute_value_features(record, sm, absorb_pool)
    tier = route(record, vf)

    pid = record.get("id", "")
    store.assign(pid, tier, vf, record_snapshot=record)

    # tombstone log for discards
    if tier == TIER_DISCARD:
        store.tombstone(pid, "initial_discard")
        store.append_tombstone_log(pid, "initial_discard")

    return tier


def run_live(n_cycles: int, curated: bool = True) -> None:
    """Run N cycles with post-verdict tier routing.

    Args:
        n_cycles: number of cycles to run
        curated: if True, proposer reads from curated view; else raw verdicts
    """
    sm = json.loads(SELF_MODEL.read_text(encoding="utf-8"))
    store = TierStore(STORE_PATH)

    verdicts_source = Path(CURATED_FILE) if curated else VERDICTS_RAW

    for i in range(n_cycles):
        cycle = store.cycle + 1
        print(f"\n── cycle {cycle} (curated={curated}) ──")

        # write curated view if curated arm
        if curated:
            n = store.write_curated_view(VERDICTS_RAW, CURATED_FILE)
            print(f"  curated view: {n} records")
            verdicts_source = Path(CURATED_FILE)

        # run controller cycle (conditioned arm == curated arm: delta-2)
        new_record = _run_one_controller_cycle(verdicts_source, cycle, conditioned=curated)

        if new_record is None:
            print("  no new verdict this cycle (CONTACT/skip)")
        else:
            tier = route_new_verdict(new_record, store, sm)
            pid = new_record.get("id", "?")
            print(f"  verdict: {new_record.get('verdict','?')} -> tier: {tier}  (id: {pid})")

        # tick TTL
        expired = store.tick_cycle()
        if expired:
            print(f"  TTL expired: {expired}")
            for eid in expired:
                store.append_tombstone_log(eid, "ttl_expiry")

        store.save()
        print(f"  store: {store.count_by_tier()}")

    # final curated view
    if curated:
        n = store.write_curated_view(VERDICTS_RAW, CURATED_FILE)
        print(f"\nFinal curated view: {n} records")


# ── D-GATE ─────────────────────────────────────────────────────────

def run_dgate(n_cycles: int = DGATE_N_CYCLES) -> dict:
    """D-GATE: curated vs uncurated A/B on the SAME weakness.

    1. Backup current state
    2. Run N cycles UNCURATED (baseline)
    3. Restore state
    4. Run N cycles CURATED
    5. Compare rate_f on targeted weakness
    """
    print(f"\n=== D-GATE: {n_cycles} cycles per arm ===")

    sm = json.loads(SELF_MODEL.read_text(encoding="utf-8"))
    weaknesses = sm.get("weaknesses", [])
    if not weaknesses:
        return {"gate": "D-GATE", "status": "FAIL", "reason": "no weakness cards in self_model"}

    target_weakness = weaknesses[0]["name"]  # target the highest-severity card
    print(f"Target weakness: {target_weakness}")

    # ── ARM A: uncurated (baseline) ────────────────────────────
    print(f"\n── ARM A: uncurated ({n_cycles} cycles) ──")
    state_backup = _backup_state()
    try:
        run_live(n_cycles, curated=False)
        arm_a_verdicts = _read_verdicts(VERDICTS_RAW)
        arm_a_stats = _compute_arm_stats(arm_a_verdicts, target_weakness)
    finally:
        _restore_state(state_backup)

    # ── ARM B: curated ─────────────────────────────────────────
    print(f"\n── ARM B: curated ({n_cycles} cycles) ──")
    run_live(n_cycles, curated=True)
    arm_b_verdicts = _read_verdicts(VERDICTS_RAW)
    arm_b_stats = _compute_arm_stats(arm_b_verdicts, target_weakness)

    # ── compare ────────────────────────────────────────────────
    improvement = arm_a_stats["rate_f"] - arm_b_stats["rate_f"]
    passed = improvement >= DGATE_IMPROVEMENT

    result = {
        "gate": "D-GATE",
        "status": "PASS" if passed else "FAIL",
        "target_weakness": target_weakness,
        "arm_a_uncurated": arm_a_stats,
        "arm_b_curated": arm_b_stats,
        "rate_f_improvement": round(improvement, 4),
        "bar": DGATE_IMPROVEMENT,
        "n_cycles_per_arm": n_cycles,
    }

    # log
    with open(DGATE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            **result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False) + "\n")

    print(f"\nD-GATE: {'PASS' if passed else 'FAIL'}")
    print(f"  rate_f uncurated: {arm_a_stats['rate_f']:.4f}")
    print(f"  rate_f curated:   {arm_b_stats['rate_f']:.4f}")
    print(f"  improvement:      {improvement:.4f} (bar: {DGATE_IMPROVEMENT})")
    return result


def _compute_arm_stats(verdicts: list[dict], weakness_name: str) -> dict:
    """Compute rate_f for a specific weakness across verdict records.

    v1 limitation: records don't carry 'targeted_weakness' field, so
    _matches_weakness is a heuristic.  D-GATE accuracy improves when
    the controller tags records (rung C/D).
    """
    relevant = [v for v in verdicts if _matches_weakness(v, weakness_name)]
    if not relevant:
        return {"rate_f": 1.0, "n_relevant": 0, "n_reject": 0}

    n_reject = sum(1 for v in relevant if v.get("verdict") == "REJECT")
    rate_f = n_reject / len(relevant)
    return {
        "rate_f": round(rate_f, 4),
        "n_relevant": len(relevant),
        "n_reject": n_reject,
    }


def _matches_weakness(record: dict, weakness_name: str) -> bool:
    """Check if a record is relevant to the target weakness.

    v1 heuristic: returns True for ALL records (cannot filter by weakness
    because records don't carry a 'targeted_weakness' tag and weakness cards
    have no domain anchors).  D-GATE thus compares OVERALL rate_f.
    Precise per-weakness filtering requires controller tagging (rung C/D).
    """
    # v1: all records count — overall rate_f comparison
    return True


def _backup_state() -> dict:
    """Backup verdicts + tier state for D-GATE arm restore."""
    backup = {}
    if VERDICTS_RAW.exists():
        backup["verdicts"] = VERDICTS_RAW.read_text(encoding="utf-8")
    if STORE_PATH.exists():
        backup["store"] = STORE_PATH.read_text(encoding="utf-8")
    return backup


def _restore_state(backup: dict) -> None:
    """Restore verdicts + tier state from backup."""
    if "verdicts" in backup:
        VERDICTS_RAW.write_text(backup["verdicts"], encoding="utf-8")
    if "store" in backup:
        STORE_PATH.write_text(backup["store"], encoding="utf-8")


# ── CLI ────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Phase 7 live runner")
    ap.add_argument("--dry", action="store_true", help="Dry validation only (no cycle)")
    ap.add_argument("--live", type=int, metavar="N", help="Run N live cycles with tier routing")
    ap.add_argument("--gate", choices=["t2", "d"], help="Run a specific gate test (live)")
    ap.add_argument("--curated", action="store_true", default=True, help="Use curated memory (default)")
    ap.add_argument("--uncurated", action="store_true", help="Use uncurated memory (baseline)")
    args = ap.parse_args()

    if args.dry:
        from step7_dryval import main as dryval_main
        sys.exit(dryval_main())

    if args.gate == "t2":
        # Live T2: run verify with empty vs full store, compare output bytes
        print("T2 live firewall check — requires wiring to verify(). See step7_gates.gate_t2.")
        result = gate_t2(VERDICTS_RAW, SELF_MODEL)
        print(json.dumps(result, indent=2))
        return

    if args.gate == "d":
        result = run_dgate()
        print(json.dumps(result, indent=2))
        return

    if args.live:
        curated = not args.uncurated
        run_live(args.live, curated=curated)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
