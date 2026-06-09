#!/usr/bin/env python3
"""sanity_E16.py - instrument-sanity for the E16 semantic retriever (NOT a bar, R7).

Confirms, BEFORE the frozen verify_E16 eval and BEFORE pre-registering:
  0. model liveness  : embeddings are real (dim 384, related>unrelated cosine).
  a. VERIFY recall   : gold-backed faithful restatements retrieve an AUTHORIZED record.
  b. over-bind == 0  : DEMOTE-class items (spoof/common/attributed/bare) retrieve
                       NOTHING authorizable. A false authorized hit HIDES a fabrication,
                       so this is the precision constraint that locks the floor.

Sweeps the similarity floor and reports, per floor:
    per-expect authorized-hit rate  +  total over-bind on DEMOTE-expect items.
Pick the LOWEST floor with over-bind == 0 while VERIFY recall is maximised.
That floor (env ONTO_RETRIEVE_FLOOR) is locked, then pre-registered, then eval.

Run with `python` (not python3 -> Windows Store stub). Reads held-out from _local.
"""
import json
import os
import sys
from collections import defaultdict

from gold_retrieve import GoldStore
import semantic_retrieve as sr

HELDOUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "eval", "_local", "heldout_E16.jsonl")
FLOORS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65]


def model_liveness():
    rel = sr._embed(["error threshold in replication", "the error threshold of replication"])
    unrel = sr._embed(["error threshold in replication", "a recipe for chocolate cake"])
    dim = rel.shape[1]
    cos_rel = float(rel[0] @ rel[1])
    cos_unrel = float(unrel[0] @ unrel[1])
    ok = dim == 384 and cos_rel > cos_unrel and cos_rel > 0.5
    print(f"[0] LIVENESS dim={dim} cos(related)={cos_rel:.3f} cos(unrelated)={cos_unrel:.3f} "
          f"-> {'OK' if ok else 'FAIL'}")
    if not ok:
        sys.exit("MODEL LIVENESS FAILED - embeddings not real; fix before sanity.")


def load_heldout():
    items = []
    with open(HELDOUT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def main():
    store = GoldStore()
    print(f"GOLD slice: {len(store.records)} records, {len(store.manifest_files)} authorized hashes")
    model_liveness()

    items = load_heldout()
    # distribution by expect and by class
    by_expect = defaultdict(int)
    for it in items:
        by_expect[it.get("expect", "?")] += 1
    print(f"held-out: {len(items)} items  by expect={dict(by_expect)}")

    print("\n[floor sweep]  authorized-hit rate per expect  |  over-bind = authorized hit on a DEMOTE item")
    print(f"{'floor':>6} | " + " | ".join(f"{e:>8}" for e in sorted(by_expect)) + " | overbind")
    best = None
    per_floor = {}
    for fl in FLOORS:
        sr._index = None  # rebuild not needed (same records) but reset cache defensively
        authok = defaultdict(int)
        overbind_items = []
        for it in items:
            hits = sr.retrieve(it["text"], store.records, floor=fl)
            has_auth = any(store.is_authorized(h) for h in hits)
            if has_auth:
                authok[it.get("expect", "?")] += 1
                if it.get("expect") == "DEMOTE":
                    overbind_items.append(it["id"])
        per_floor[fl] = (dict(authok), overbind_items)
        rates = []
        for e in sorted(by_expect):
            rates.append(f"{authok[e]}/{by_expect[e]}")
        overbind = len(overbind_items)
        print(f"{fl:>6.2f} | " + " | ".join(f"{r:>8}" for r in rates) + f" | {overbind}")
        # candidate floor = overbind 0 and max VERIFY recall
        verify_recall = authok.get("VERIFY", 0)
        if overbind == 0:
            if best is None or verify_recall > best[1]:
                best = (fl, verify_recall)

    print("\n[over-bind detail per floor] (DEMOTE items that got an AUTHORIZED hit - must be empty at locked floor)")
    for fl in FLOORS:
        ob = per_floor[fl][1]
        print(f"  floor={fl:.2f}: {ob if ob else 'none'}")

    if best:
        print(f"\nRECOMMENDED floor (lowest with over-bind==0, max VERIFY recall): {best[0]:.2f} "
              f"(VERIFY authorized {best[1]})")
        print(f"  -> set:  $env:ONTO_RETRIEVE_FLOOR = \"{best[0]:.2f}\"   before pre-register + eval")
    else:
        print("\nNO floor in sweep achieves over-bind==0 -> tighten FLOORS upward and re-sweep "
              "(do NOT loosen toward eval).")


if __name__ == "__main__":
    main()
