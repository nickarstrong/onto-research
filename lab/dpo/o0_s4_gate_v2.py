#!/usr/bin/env python3
"""o0_s4_gate_v2.py -- S4 gate recompute with specifics_check_v2 (targeted rescue).

Same frozen S4 inputs as o0_s4_gate.py, same pre-registered gate. The ONLY
difference: on v1 specifics FAIL, do a LIVE targeted-retrieval conjunction rescue
(Crossref + OpenAlex) before downgrading. Implements REPORT_S4_specifics_gate.md
sec5 (yield recovery: filter precision + retrieval coverage), pack v204 lever V3.

LIVE NETWORK (Crossref + OpenAlex). NO Ollama, NO embedding, NO generation.
Enriched + B2 verdicts + Founder labels stay frozen; only the rescue retrieval
is live. ~16 API calls for the S4 set -> LOCAL tier (couple minutes).

Gate (CONCEPT_organism0_v1.md sec3, frozen denominators v199):
  G1 fa_live = dirty_absorbed / 17  <= 0.10   (HARD -- ONTO safety bar)
  G3 yield   = total_absorbed  / 20  >= 0.20   (stage-relative per ROADMAP sec0b)

Usage (from onto-research/lab/dpo/):
  python o0_s4_gate_v2.py \
    --enriched eval/o0/o0_s4_enriched.jsonl \
    --verdicts eval/o0/o0_s4_b2_verdicts.jsonl \
    --labels   eval/o0/o0_s4_founder_labels.jsonl \
    --trace    eval/o0/o0_s4_gate_v2_trace.jsonl
"""

import argparse
import json
import time
from pathlib import Path

from o0_specifics_filter import specifics_check_v2

# Live retrieval reused from the frozen Rung-1 wiring (dual-query, no embedding).
from rung1_wiring_v0 import query_crossref, query_openalex, deduplicate_papers

# Pre-registered denominators (frozen, v199). Do not move to make the gate pass.
N_LIVE = 17
M_HELDOUT = 20
G1_BAR = 0.10
G3_BAR = 0.20


def live_retrieve(query, top_k=10):
    """Targeted dual-query fetch -> deduped list of {doi, abstract, ...}."""
    cr = query_crossref(query, top_k)
    time.sleep(0.4)
    oa = query_openalex(query, top_k)
    time.sleep(0.4)
    return deduplicate_papers(cr + oa)


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
    ap.add_argument("--trace", default="eval/o0/o0_s4_gate_v2_trace.jsonl")
    ap.add_argument("--top_k", type=int, default=10)
    args = ap.parse_args()

    enriched = {r["id"]: r for r in load_jsonl(args.enriched)}
    verdicts = {r["id"]: r for r in load_jsonl(args.verdicts)}
    labels = {r["id"]: r["label"] for r in load_jsonl(args.labels)}

    supports = sorted(
        rid for rid, v in verdicts.items()
        if (v.get("b2_verdict") or v.get("s2b_verdict") or v.get("verdict"))
        == "SUPPORTS"
    )

    print("=" * 78)
    print("S4 GATE RECOMPUTE v2 -- specifics_check_v2 (targeted conjunction rescue)")
    print("  LIVE retrieval: Crossref + OpenAlex (enriched/verdicts/labels frozen)")
    print("=" * 78)

    trace_log = []
    rows = []
    for rid in supports:
        rec = enriched.get(rid, {})
        claim = rec.get("claim", "") or ""
        best_ab = rec.get("best_abstract", "") or ""

        rlog = []
        chk = specifics_check_v2(claim, best_ab, live_retrieve,
                                 top_k=args.top_k, log=rlog)
        trace_log.append({"id": rid, "label": labels.get(rid, "?"),
                          "method": chk["method"], "rescued": chk["rescued"],
                          "rescue_doi": chk.get("rescue_doi"),
                          "inscope": chk.get("inscope", []),
                          "retrieval": rlog})
        rows.append({
            "id": rid,
            "label": labels.get(rid, "?"),
            "absorbed": chk["pass"],
            "method": chk["method"],
            "rescue_doi": chk.get("rescue_doi"),
            "inscope": chk.get("inscope", []),
        })
        tag = "ABSORB" if chk["pass"] else "REJECT"
        doi = (" via %s" % chk["rescue_doi"]) if chk.get("rescue_doi") else ""
        print("  [%s] %-12s %-6s %-18s%s" %
              (tag, rid, labels.get(rid, "?"), chk["method"], doi))

    n_dirty_total = sum(1 for r in rows if r["label"] == "DIRTY")
    dirty_absorbed = sum(1 for r in rows if r["label"] == "DIRTY" and r["absorbed"])
    clean_absorbed = sum(1 for r in rows if r["label"] == "CLEAN" and r["absorbed"])
    total_absorbed = sum(1 for r in rows if r["absorbed"])

    fa_live = dirty_absorbed / N_LIVE
    yield_rate = total_absorbed / M_HELDOUT

    # Write trace
    tp = Path(args.trace)
    tp.parent.mkdir(parents=True, exist_ok=True)
    with open(tp, "w", encoding="utf-8") as f:
        for t in trace_log:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print("-" * 78)
    print("  SUPPORTS in:        %d" % len(rows))
    print("  DIRTY total:        %d" % n_dirty_total)
    print("  DIRTY absorbed:     %d" % dirty_absorbed)
    print("  CLEAN absorbed:     %d" % clean_absorbed)
    print("  TOTAL absorbed:     %d" % total_absorbed)
    print("-" * 78)
    g1 = "PASS" if fa_live <= G1_BAR else "FAIL"
    g3 = "PASS" if yield_rate >= G3_BAR else "FAIL"
    gate = "PASS" if (fa_live <= G1_BAR and yield_rate >= G3_BAR) else "FAIL"
    print("  G1 fa_live = %d/%d = %.3f  (<= %.2f)  -> %s  [HARD]"
          % (dirty_absorbed, N_LIVE, fa_live, G1_BAR, g1))
    print("  G3 yield   = %d/%d = %.3f  (>= %.2f)  -> %s  [stage-relative]"
          % (total_absorbed, M_HELDOUT, yield_rate, G3_BAR, g3))
    print("  COMBINED (G1 AND G3): %s" % gate)
    print("  vs v1 (v202): fa_live 0.000 / yield 0.050   |   v204 V3 max: 0.150")
    print("  trace: %s" % tp)
    print("=" * 78)


if __name__ == "__main__":
    main()
