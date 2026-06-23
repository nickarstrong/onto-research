"""
step7_dryval.py — Phase 7: Dry Validation
==========================================
Routes existing o0_verdicts.jsonl through the tier router, populates
the tier store, writes curated view, runs T2-T5 gates (T1=STUB).

No GPU.  No network.  Reads on-disk substrate only.

Usage:
  cd C:\\Projects\\onto-research\\lab\\dpo
  python step7_dryval.py

Expected:
  - T2 PASS  (no verify-path imports)
  - T3 PASS  (tombstone count matches; round-trip succeeds)
  - T4 PASS  (0 GOLD writes)
  - T5 PASS  (all 3 live tiers non-empty)
  - T1 STUB  (awaiting Founder labels)
  - D  PRE-REGISTERED

Home: C:\\Projects\\onto-research\\lab\\dpo\\step7_dryval.py
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

from o0_tier_router import route_batch, TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD
from o0_tier_store import TierStore, CURATED_FILE
from step7_gates import run_all_gates, print_gate_report

# ── paths (canonical, disk-wins) ──────────────────────────────────
VERDICTS  = Path("eval/o0/o0_verdicts.jsonl")
SELF_MODEL = Path("self_model.json")
STORE_PATH = Path("o0_tier_state.json")


def main() -> int:
    print("=== PHASE 7 DRY VALIDATION ===\n")

    # ── 1. load substrate ──────────────────────────────────────────
    if not VERDICTS.exists():
        print(f"FAIL: verdicts not found at {VERDICTS}")
        return 1
    if not SELF_MODEL.exists():
        print(f"FAIL: self_model not found at {SELF_MODEL}")
        return 1

    verdicts = []
    for line in VERDICTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            verdicts.append(json.loads(line))
    print(f"Loaded {len(verdicts)} verdict records from {VERDICTS}")

    sm = json.loads(SELF_MODEL.read_text(encoding="utf-8"))
    n_cards = len(sm.get("weaknesses", []))
    print(f"Loaded self_model: {n_cards} weakness cards")

    # ── 2. route batch ─────────────────────────────────────────────
    routed = route_batch(verdicts, sm)
    counts = {}
    for r in routed:
        t = r["_tier"]
        counts[t] = counts.get(t, 0) + 1

    print(f"\nRouted {len(routed)} records:")
    for t in (TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD):
        print(f"  {t}: {counts.get(t, 0)}")
    print()

    # ── 3. populate tier store ─────────────────────────────────────
    store = TierStore(STORE_PATH)
    for r in routed:
        pid = r.get("id", "")
        if not pid:
            print(f"  WARN: record missing id, skipped: {r.get('topic','?')}")
            continue
        store.assign(pid, r["_tier"], r["_value_features"], record_snapshot=r)
        # discard = tombstoned from assignment (reversible, per strategy)
        if r["_tier"] == TIER_DISCARD:
            store.tombstone(pid, "initial_discard")
    store.save()
    print(f"Tier store written: {STORE_PATH}  ({len(store.all_records())} records)")

    # ── 4. curated view ────────────────────────────────────────────
    n_curated = store.write_curated_view(VERDICTS, CURATED_FILE)
    print(f"Curated view written: {CURATED_FILE}  ({n_curated} records)")

    # ── 5. gate tests ──────────────────────────────────────────────
    results = run_all_gates(VERDICTS, SELF_MODEL, store, routed, t1_labels=None)
    print_gate_report(results)

    # ── 6. summary ─────────────────────────────────────────────────
    active_gates = [g for g in results if g["status"] not in ("STUB", "PRE-REGISTERED")]
    failed = [g for g in active_gates if g["status"] != "PASS"]
    if failed:
        print(f"DRY-VAL: FAIL ({len(failed)} gate(s) failed)")
        for g in failed:
            print(f"  ✗ {g['gate']}: {g.get('reason', g.get('note', ''))}")
        return 1

    print("DRY-VAL: PASS (T2-T5 green, T1=STUB, D=PRE-REGISTERED)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
