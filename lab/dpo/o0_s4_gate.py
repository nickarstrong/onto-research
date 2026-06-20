#!/usr/bin/env python3
"""o0_s4_gate.py -- recompute S4 gate (G1 fa_live / G3 yield) with specifics filter.

Reads frozen S4 artifacts + Founder-banked labels, applies the post-B2
specifics-coverage filter, and reports the pre-registered gate.

NO model calls, NO retrieval, NO generation. Pure deterministic recompute over
already-collected data (Ollama/retrieval frozen). One number: fa_live.

Inputs (all frozen):
  --enriched   eval/o0/o0_s4_enriched.jsonl     (claim + best_abstract)
  --verdicts   eval/o0/o0_s4_b2_verdicts.jsonl  (B2 b2_verdict)
  --labels     eval/o0/o0_s4_founder_labels.jsonl (Founder CLEAN/DIRTY, v199 banked)

Gate (CONCEPT_organism0_v1.md sec 3, pre-registered/frozen):
  G1 fa_live = dirty_absorbed / N_live   <= 0.10   (N_live = banked 17)
  G3 yield   = total_absorbed / M_heldout >= 0.20  (M_heldout = 20)
  PASS = G1 AND G3.

Usage:
  python o0_s4_gate.py --enriched eval/o0/o0_s4_enriched.jsonl \
      --verdicts eval/o0/o0_s4_b2_verdicts.jsonl \
      --labels eval/o0/o0_s4_founder_labels.jsonl
"""

import argparse
import json

from o0_specifics_filter import specifics_check

# Pre-registered denominators (frozen, v199). Do not move to make gate pass.
N_LIVE = 17       # gate-passed live set used for fa_live denominator (v199)
M_HELDOUT = 20    # total held-out claims for yield denominator
G1_BAR = 0.10
G3_BAR = 0.20


def load_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enriched", required=True)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--labels", required=True)
    args = ap.parse_args()

    enriched = {r["id"]: r for r in load_jsonl(args.enriched)}
    verdicts = {r["id"]: r for r in load_jsonl(args.verdicts)}
    labels = {r["id"]: r["label"] for r in load_jsonl(args.labels)}

    supports = [rid for rid, v in verdicts.items()
                if (v.get("b2_verdict") or v.get("s2b_verdict") or v.get("verdict"))
                == "SUPPORTS"]
    supports.sort()

    rows = []
    for rid in supports:
        rec = enriched.get(rid, {})
        chk = specifics_check(rec.get("claim", "") or "",
                              rec.get("best_abstract", "") or "")
        rows.append({
            "id": rid,
            "label": labels.get(rid, "?"),
            "filter": "PASS" if chk["pass"] else "FAIL",
            "absorbed": chk["pass"],
            "unverified": [u["value"] for u in chk.get("unverified", [])],
        })

    n_dirty_total = sum(1 for r in rows if r["label"] == "DIRTY")
    dirty_absorbed = sum(1 for r in rows if r["label"] == "DIRTY" and r["absorbed"])
    clean_absorbed = sum(1 for r in rows if r["label"] == "CLEAN" and r["absorbed"])
    total_absorbed = sum(1 for r in rows if r["absorbed"])

    fa_live = dirty_absorbed / N_LIVE
    yield_rate = total_absorbed / M_HELDOUT

    print("=" * 70)
    print("S4 GATE RECOMPUTE -- specifics filter (post-B2)")
    print("=" * 70)
    print(f"{'id':14s} {'label':6s} {'filter':6s} {'absorbed':9s} unverified")
    print("-" * 70)
    for r in rows:
        uv = ",".join(r["unverified"][:4]) + ("..." if len(r["unverified"]) > 4 else "")
        print(f"{r['id']:14s} {r['label']:6s} {r['filter']:6s} "
              f"{str(r['absorbed']):9s} {uv}")
    print("-" * 70)
    print(f"  SUPPORTS in:        {len(rows)}")
    print(f"  DIRTY total:        {n_dirty_total}")
    print(f"  DIRTY absorbed:     {dirty_absorbed}")
    print(f"  CLEAN absorbed:     {clean_absorbed}")
    print(f"  TOTAL absorbed:     {total_absorbed}")
    print("-" * 70)
    g1 = "PASS" if fa_live <= G1_BAR else "FAIL"
    g3 = "PASS" if yield_rate >= G3_BAR else "FAIL"
    gate = "PASS" if (fa_live <= G1_BAR and yield_rate >= G3_BAR) else "FAIL"
    print(f"  G1 fa_live = {dirty_absorbed}/{N_LIVE} = {fa_live:.3f}  (<= {G1_BAR})  -> {g1}")
    print(f"  G3 yield   = {total_absorbed}/{M_HELDOUT} = {yield_rate:.3f}  (>= {G3_BAR})  -> {g3}")
    print(f"  COMBINED (G1 AND G3): {gate}")
    print("=" * 70)


if __name__ == "__main__":
    main()
