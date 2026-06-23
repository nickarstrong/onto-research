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
GOAL_STACK      = Path("goal_stack.json")   # pack v246 sec 3.3: arm-symmetric SELECT state
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
    pin_weakness: str | None = None,
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
    if pin_weakness:                      # pack v246 sec 3.1: gate-only SELECT pin
        argv += ["--pin-weakness", pin_weakness]
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


def run_live(n_cycles: int, curated: bool = True, pin_weakness: str | None = None) -> None:
    """Run N cycles with post-verdict tier routing.

    Args:
        n_cycles: number of cycles to run
        curated: if True, proposer reads from curated view; else raw verdicts
        pin_weakness: D-GATE only -- pin SELECT to this weakness every cycle (kills D1)
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

        # run controller cycle.
        # rung C (pack v244 sec 3.1 / sec 5): BOTH arms condition the proposer ->
        # the contrast is memory CONTENT, not wiring. curated arm reads the PRUNED
        # active-tier view (CURATED_FILE); uncurated arm reads the FULL raw pool
        # (VERDICTS_RAW). This proves TIERING adds value (pruned > full), which is
        # the phase capability — NOT the already-proven blind-vs-conditioned A/B
        # (6010835). conditioned=False (blind) here would re-skin Step 6 = ceremonial.
        new_record = _run_one_controller_cycle(verdicts_source, cycle,
                                                conditioned=True, pin_weakness=pin_weakness)

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
        run_live(n_cycles, curated=False, pin_weakness=target_weakness)
        arm_a_verdicts = _read_verdicts(VERDICTS_RAW)
        arm_a_stats = _compute_arm_stats(arm_a_verdicts, target_weakness)
    finally:
        _restore_state(state_backup)

    # ── ARM B: curated ─────────────────────────────────────────
    # arm A's finally restored verdicts+store+goal_stack to the pre-gate snapshot
    # (pack v246 sec 3.3), so ARM B starts from IDENTICAL SELECT state -> the only
    # difference between arms is memory CONTENT (full vs pruned), not controller phase.
    print(f"\n── ARM B: curated ({n_cycles} cycles) ──")
    run_live(n_cycles, curated=True, pin_weakness=target_weakness)
    arm_b_verdicts = _read_verdicts(VERDICTS_RAW)
    arm_b_stats = _compute_arm_stats(arm_b_verdicts, target_weakness)

    # ── 3.1 PRECONDITION: curated must be a PRUNED, non-inert view ──
    # The phase is proven only if tiering actually changed the retrievable pool.
    # If curated == raw (no pruning) the run is ceremonial -> FAIL regardless of
    # rate_f. Verdict-blind: ABSORB-set difference + optional top-k delta on the
    # SELECTed weakness's first evidence topic.
    precond = assert_curated_differs(goal_topic=_weakness_probe_topic(sm, target_weakness))

    # ── compare ────────────────────────────────────────────────
    improvement = arm_a_stats["rate_f"] - arm_b_stats["rate_f"]
    passed = improvement >= DGATE_IMPROVEMENT and precond["precondition_ok"]

    result = {
        "gate": "D-GATE",
        "status": "PASS" if passed else "FAIL",
        "target_weakness": target_weakness,
        "arm_a_uncurated": arm_a_stats,
        "arm_b_curated": arm_b_stats,
        "rate_f_improvement": round(improvement, 4),
        "bar": DGATE_IMPROVEMENT,
        "precondition_3_1": precond,
        "n_cycles_per_arm": n_cycles,
    }

    # log
    with open(DGATE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            **result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False) + "\n")

    print(f"\nD-GATE: {'PASS' if passed else 'FAIL'}")
    print(f"  rate_f uncurated: {arm_a_stats['rate_f']:.4f} (n_relevant={arm_a_stats['n_relevant']})")
    print(f"  rate_f curated:   {arm_b_stats['rate_f']:.4f} (n_relevant={arm_b_stats['n_relevant']})")
    print(f"  improvement:      {improvement:.4f} (bar: {DGATE_IMPROVEMENT})")
    print(f"  precond 3.1:      pruning_ok={precond['pruning_ok']} "
          f"topk_differs={precond.get('topk_differs')} "
          f"(pruned {precond['n_pruned']}/{precond['n_raw_absorb']} ABSORB)")
    print(f"  probe topic:      {precond.get('goal_topic')!r}")
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

    rung C (pack v244 sec 3.2): per-weakness-probative. Reads the delta-3
    controller stamp record['targeted_weakness'] (SELECT-side, written POST-verify
    -> verdict-blind, firewall held: verify() never sees this field). A record
    counts for weakness W iff its stamp == W.

    By construction this excludes the sealed 220/120 (no stamp -> None != W),
    so D-GATE compares ONLY the live tagged cycles on the SAME weakness.
    """
    return record.get("targeted_weakness") == weakness_name


def _weakness_probe_topic(sm: dict, weakness_name: str, k: int = 3) -> str | None:
    """A goal-topic to probe top-k retrieval for the SELECTed weakness.

    pack v246 PATH 1 re-cut (kills the v246-run-1 false negative): the probe MUST be
    a topic PRESENT in the CURATED pool. The prior cut ranked depth over the RAW pool
    and picked a topic pruned OUT of curated -> curated_topk=[] -> the top-k test never
    executed (curated_only is vacuously empty, not a measured False).

    Principled + verdict-blind selection (topic only; reads no verdict beyond the
    ABSORB pool definition load_confirmed already uses):
      1. raw = ABSORB pool in VERDICTS_RAW; cur = ABSORB pool in CURATED_FILE
         (cur is a STRICT subset; pruned = raw_ids - cur_ids).
      2. Candidate topics = topics of CURATED records (guarantees curated_topk != []).
      3. Rank each candidate by how many of ITS raw top-k are since-PRUNED records --
         the region where "pruning unburies a record raw top-k buries" makes its
         STRONGEST prediction (a surviving curated record sits below pruned crowders
         in raw, then rises once they are pruned). We select on the CAUSE (pruned
         crowding in raw top-k), not the OUTCOME (curated_only) -> not result-gaming.
         topk_differs is then measured honestly; PRE-COMMIT: False even here = a real
         negative on the top-k claim (escalate, do not re-fire).
      4. None only when the curated ABSORB pool is empty.
    """
    from o0_retrieve import load_confirmed, retrieve
    raw = load_confirmed(VERDICTS_RAW)
    cur = (load_confirmed(CURATED_FILE)
           if Path(CURATED_FILE).exists() else [])
    cur = [r for r in cur if (r.get("topic") or "").strip()]
    if not cur:
        return None
    pruned = {r["id"] for r in raw} - {r["id"] for r in cur}

    best_topic, best_key = None, None
    for c in sorted(cur, key=lambda r: str(r["id"])):          # deterministic
        topic = c["topic"]
        raw_tk = {r["id"] for r in retrieve(topic, raw, k)}
        # CAUSE proxy: pruned crowders occupying this topic's raw top-k.
        key = (len(raw_tk & pruned), len(raw_tk))
        if best_key is None or key > best_key:
            best_topic, best_key = topic, key
    return best_topic


def assert_curated_differs(goal_topic: str | None = None, k: int = 3) -> dict:
    """3.1 precondition: the CURATED (pruned) view must differ in CONTENT from
    the RAW (full) view. Inert (curated == raw) = ceremonial run -> FAIL.

    Primary guard (always): the curated ABSORB pool must be a STRICT subset of
    raw (>=1 record pruned). Secondary (when goal_topic given): the curated
    top-k must surface >=1 record the raw top-k lacks (pruning unburied it).

    Verdict-blind: o0_retrieve scores on topic token-overlap only; never reads
    the verdict. Reads no verify-path handle (firewall held).
    """
    from o0_retrieve import load_confirmed, retrieve
    raw = load_confirmed(VERDICTS_RAW)
    cur = load_confirmed(CURATED_FILE) if Path(CURATED_FILE).exists() else []
    raw_ids = {r["id"] for r in raw}
    cur_ids = {r["id"] for r in cur}
    pruned = raw_ids - cur_ids
    out: dict = {
        "n_raw_absorb": len(raw_ids),
        "n_curated_absorb": len(cur_ids),
        "n_pruned": len(pruned),
        "pruning_ok": len(pruned) >= 1 and cur_ids <= raw_ids,
    }
    if goal_topic:
        raw_tk = {r["id"] for r in retrieve(goal_topic, raw, k)}
        cur_tk = {r["id"] for r in retrieve(goal_topic, cur, k)}
        curated_only = sorted(cur_tk - raw_tk)
        out["goal_topic"] = goal_topic
        out["raw_topk"] = sorted(raw_tk)
        out["curated_topk"] = sorted(cur_tk)
        out["curated_only_topk"] = curated_only
        out["topk_differs"] = len(curated_only) >= 1
    # pack v246 PATH 2a (Founder, 2026-06-24): the PROBATIVE guard is content-
    # difference (pruning_ok): the curated view is a strict, non-inert subset of raw
    # (>=1 ABSORB pruned). topk_differs was an UNSATISFIABLE retrieval-difference
    # guard for this record schema -- controller.absorb() drops `topic`, so the
    # post-prune curated pool (live ctrl_ records only; sealed o0_ pruned) has no
    # topic surface to retrieve on. It is kept as DIAGNOSTIC output, not a pass bar.
    # The phase capability is proven by the rate_f delta (improvement, n=10/arm) x
    # pruning_ok; value flows through conditioning-pool cleanliness, not top-k order.
    out["precondition_ok"] = out["pruning_ok"]
    return out


def _backup_state() -> dict:
    """Backup verdicts + tier state + goal_stack for D-GATE arm restore.

    pack v246 sec 3.3: goal_stack.json carries SELECT's per-weakness cursor
    (cycle/cycles_used/last_worked_cycle). Omitting it desynced the arms (D3).
    A key maps to None when the file did not exist pre-gate -> restore deletes it.
    """
    backup = {}
    for key, p in (("verdicts", VERDICTS_RAW), ("store", STORE_PATH),
                   ("goal_stack", GOAL_STACK)):
        backup[key] = p.read_text(encoding="utf-8") if p.exists() else None
    return backup


def _restore_state(backup: dict) -> None:
    """Restore verdicts + tier state + goal_stack from backup.

    None == 'did not exist pre-gate' -> remove any artifact the arm created, so the
    next arm starts from the EXACT pre-gate snapshot (byte-identical SELECT state).
    """
    for key, p in (("verdicts", VERDICTS_RAW), ("store", STORE_PATH),
                   ("goal_stack", GOAL_STACK)):
        val = backup.get(key)
        if val is None:
            if p.exists():
                p.unlink()
        else:
            p.write_text(val, encoding="utf-8")


# ── CLI ────────────────────────────────────────────────────────────

def main():
    # pack v246 sec 1 (durable cp1251 fix): force UTF-8 stdio so decorative prints
    # cannot HARD-CRASH the live runner under a cp1251 console (was env-only before).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
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
