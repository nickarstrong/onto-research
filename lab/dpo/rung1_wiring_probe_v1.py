#!/usr/bin/env python3
"""
rung1_wiring_probe_v1.py — Rung-1 Wiring Probe (Track R1)

End-to-end plumbing test: proposer output → retrieval (reform+embed) → s2b verifier → ABSORB/REJECT.

NOT a gate test (no Founder labels, no fa_live measurement). Verifies the pipeline runs
without errors and produces ABSORB/REJECT verdicts for all claims.

Two modes:
  --phase1   Retrieval + embedding + B1 binding (deterministic). No model, no API key.
             Outputs intermediate JSONL for external B2 judgment.
  (default)  Full pipeline including B2 (needs --b2 api + ANTHROPIC_API_KEY, or --b2 local + GPU).

Usage:
  python rung1_wiring_probe_v1.py --proposals proposals_v01b.jsonl --limit 15 --phase1
  python rung1_wiring_probe_v1.py --proposals proposals_v01b.jsonl --limit 15 --b2 api

Prereqs: torch, transformers (CPU). Phase1 needs no API key / GPU.
Lives in lab/dpo/ alongside retrieval_reform_embed_v1.py and s2b_v0.py.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# ── retrieval imports (from E-bis proven pipeline) ────────────────────────────
import retrieval_reform_embed_v1 as retr

# ── verifier imports (frozen s2b) ─────────────────────────────────────────────
import s2b_v0 as s2b

# ── auto-reform: deterministic keyword extraction (no model, no hand-craft) ──
# Domain-agnostic English function words. NOT tuned to any test set (R7).
_STOP = frozenset((
    "the a an is are was were has have had been being in on at to for of with by "
    "from as into through that this these those it its and or but not no can will "
    "may might must should would could about also more most some any all such both "
    "than very much between during after before their there here they them which "
    "what when where how over under above below among upon per via due each other "
    "only another does did done using used based while whether either neither so yet "
    "do be his her our your you one two been nor"
).split())


def auto_reform_query(claim_text, max_words=10):
    """Extract content keywords from a claim for reformulated search query.
    Deterministic, no model. Keeps words > 2 chars that aren't stop words."""
    words = re.findall(r"[A-Za-z0-9.]+", claim_text)
    content = []
    for w in words:
        wl = w.lower().rstrip(".")
        if wl in _STOP or len(wl) < 3:
            continue
        content.append(w)
    return " ".join(content[:max_words])


# ── disposition mapping (DESIGN_propose_side_v1 sec 2) ────────────────────────
def disposition(verdict):
    """SUPPORTS → ABSORB ; everything else → REJECT."""
    return "ABSORB" if verdict == "SUPPORTS" else "REJECT"


# ── main pipeline ────────────────────────────────────────────────────────────
def run_probe(proposals_path, limit, out_path, b2_backend, model,
              no_fulltext=False, phase1=False):
    # ── load proposals ──
    with open(proposals_path, encoding="utf-8") as f:
        proposals = [json.loads(l) for l in f if l.strip()]
    if limit and limit < len(proposals):
        proposals = proposals[:limit]

    n = len(proposals)
    mode_label = "PHASE-1 (retrieval + B1, no B2)" if phase1 else f"FULL (b2={b2_backend})"
    print(f"=== RUNG-1 WIRING PROBE v1 — {mode_label} ===")
    print(f"  proposals: {proposals_path} ({n} claims)")
    print(f"  output: {out_path}\n")

    # ── preflight ──
    if not phase1:
        if b2_backend == "api" and not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY not set (required for --b2 api)", file=sys.stderr)
            return 1

    # ── load embedding model (CPU) ──
    retr._load_model()

    # ── select B2 judge (only for full mode) ──
    b2_fn = None
    oa_getter = None
    if not phase1:
        b2_fn = s2b.select_b2(b2_backend, model)
        oa_getter = None if no_fulltext else s2b.resolve_oa_fulltext

    results = []
    errors = 0

    for i, prop in enumerate(proposals):
        pid = prop["id"]
        claim = prop["claim_text"]
        proposer_doi = prop.get("doi", "")
        print(f"[{i+1:2d}/{n}] {pid}: {claim[:70]}...")

        rec = {
            "id": pid,
            "claim_text": claim,
            "field": prop.get("field", ""),
            "proposer_doi": proposer_doi,
        }

        try:
            # ── STEP 1: dual-query retrieval ──
            reform = auto_reform_query(claim)
            print(f"  reform: {reform}")

            cr_raw = retr.query_crossref(claim, 10)
            time.sleep(0.4)
            oa_raw = retr.query_openalex(claim, 10)
            time.sleep(0.4)
            cr_ref = retr.query_crossref(reform, 10)
            time.sleep(0.4)
            oa_ref = retr.query_openalex(reform, 10)
            time.sleep(0.4)

            n_raw = len(cr_raw) + len(oa_raw)
            n_ref = len(cr_ref) + len(oa_ref)
            all_papers = retr.deduplicate_papers(cr_raw + oa_raw + cr_ref + oa_ref)
            print(f"  retrieval: raw={n_raw} reform={n_ref} dedup={len(all_papers)}")

            if not all_papers:
                rec.update({
                    "retrieval_status": "NO_CANDIDATES",
                    "n_raw": n_raw, "n_reform": n_ref, "n_dedup": 0,
                    "verdict": "REJECT", "reason": "no_retrieval_candidates",
                    "disposition": "REJECT",
                })
                results.append(rec)
                print(f"  -> NO CANDIDATES -> REJECT")
                continue

            # ── STEP 2: embedding scoring ──
            claim_emb = retr.encode([claim])
            abstracts = [p["abstract"] for p in all_papers]
            abs_embs = retr.encode(abstracts)
            sims = retr.cosine_scores(claim_emb, abs_embs)
            for j, p in enumerate(all_papers):
                p["similarity"] = sims[j]
            ranked = sorted(all_papers, key=lambda x: x["similarity"], reverse=True)
            best = ranked[0]

            rec.update({
                "retrieval_status": "MATCHED",
                "n_raw": n_raw, "n_reform": n_ref, "n_dedup": len(all_papers),
                "retrieved_doi": best["doi"],
                "retrieved_title": best["title"],
                "retrieved_sim": best["similarity"],
                "retrieved_source": best["source"],
                "reform_query": reform,
            })
            print(f"  best: sim={best['similarity']:.4f}  {best['title'][:60]}")

            # ── STEP 3a: s2b fetch + B1 binding (deterministic, always runs) ──
            meta = s2b.fetch_crossref(best["doi"])
            time.sleep(0.3)
            b1_v, b1_reason, b1_sig = s2b.b1_binding(
                claim, prop.get("star_quote", ""), meta)

            rec.update({
                "s2b_fetched_title": meta.get("title", ""),
                "s2b_abstract_present": bool((meta.get("abstract") or "").strip()),
                "s2b_abstract_len": len((meta.get("abstract") or "").strip()),
                "b1_verdict": b1_v,          # None (route to B2) or "NOT"
                "b1_reason": b1_reason,
            })

            if b1_v == "NOT":
                # B1 binding mismatch → REJECT without B2
                rec.update({
                    "verdict": "NOT", "leg": "binding", "reason": b1_reason,
                    "disposition": "REJECT",
                })
                print(f"  B1: NOT ({b1_reason}) -> REJECT")
                results.append(rec)
                continue

            print(f"  B1: route_b2 ({b1_reason})")

            if phase1:
                # ── PHASE-1 STOP: save data for external B2 judgment ──
                abstract_text = (meta.get("abstract") or "").strip()
                rec.update({
                    "b2_pending": True,
                    "b2_input_title": meta.get("title", ""),
                    "b2_input_abstract": abstract_text[:3000],
                })
                results.append(rec)
                print(f"  -> PHASE-1: saved for external B2")
                continue

            # ── STEP 3b: s2b B2 supports (model-based, full mode only) ──
            s2b_item = {
                "id": pid, "claim_text": claim,
                "doi": best["doi"], "star_quote": prop.get("star_quote", ""),
            }
            s2b_rec = s2b.judge(s2b_item, s2b.fetch_crossref, model, b2_fn,
                                oa_getter=oa_getter, b2_ft_fn=b2_fn)
            time.sleep(0.5)

            verdict = s2b_rec.get("verdict", "ERROR")
            rec.update({
                "verdict": verdict,
                "leg": s2b_rec.get("leg", ""),
                "reason": s2b_rec.get("reason", ""),
                "disposition": disposition(verdict),
            })
            print(f"  s2b: {verdict} (leg={rec['leg']}) -> {rec['disposition']}")

        except Exception as e:
            errors += 1
            rec.update({
                "verdict": "ERROR",
                "reason": f"pipeline_error: {type(e).__name__}: {e}",
                "disposition": "REJECT",
            })
            print(f"  ERROR: {e}", file=sys.stderr)

        results.append(rec)

    # ── write output ──
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ── summary ──
    from collections import Counter
    vc = Counter(r.get("verdict", r.get("b2_pending", "?")) for r in results)
    rc = Counter(r.get("retrieval_status", "?") for r in results)

    print(f"\n{'='*65}")
    print(f"RUNG-1 WIRING PROBE SUMMARY ({mode_label})")
    print(f"  Claims processed:  {len(results)}")
    print(f"  Pipeline errors:   {errors}")
    print(f"  Retrieval:         {dict(rc)}")

    matched = [r for r in results if r.get("retrieval_status") == "MATCHED"]
    if matched:
        avg_sim = sum(r["retrieved_sim"] for r in matched) / len(matched)
        print(f"  Avg best sim:      {avg_sim:.4f}")

    if phase1:
        b2_pending = sum(1 for r in results if r.get("b2_pending"))
        b1_reject = sum(1 for r in results if r.get("verdict") == "NOT" and r.get("leg") == "binding")
        no_cand = sum(1 for r in results if r.get("retrieval_status") == "NO_CANDIDATES")
        print(f"  B1 REJECT:         {b1_reject}")
        print(f"  NO_CANDIDATES:     {no_cand}")
        print(f"  B2 pending:        {b2_pending}")
        print(f"\n  PHASE-1: {'PASS' if errors == 0 else 'FAIL'} (retrieval + B1 wiring)")
        print(f"  NEXT: upload {out.name} for B2 judgment")
    else:
        dc = Counter(r.get("disposition", "?") for r in results)
        print(f"  Verdicts:          {dict(vc)}")
        print(f"  Dispositions:      {dict(dc)}")
        all_have_verdict = all(
            r.get("verdict") in ("SUPPORTS", "NOT", "UNCLEAR", "ERROR") or
            r.get("retrieval_status") == "NO_CANDIDATES"
            for r in results)
        plumbing_ok = errors == 0 and all_have_verdict
        print(f"\n  PLUMBING: {'PASS' if plumbing_ok else 'FAIL'}")

    print(f"\nOutput: {out}")
    print(f"{'='*65}")
    return 0 if errors == 0 else 1


def main():
    ap = argparse.ArgumentParser(
        description="Rung-1 Wiring Probe: proposer → retrieval → s2b → verdict")
    ap.add_argument("--proposals", required=True,
                    help="proposals JSONL (from make_proposals_v01.py)")
    ap.add_argument("--limit", type=int, default=15,
                    help="max claims to process (default 15)")
    ap.add_argument("--out", default="eval/rung1_wiring_v1.jsonl",
                    help="output JSONL path")
    ap.add_argument("--phase1", action="store_true",
                    help="phase-1 only: retrieval + B1, skip B2 (no API key / GPU needed)")
    ap.add_argument("--b2", choices=["api", "local"], default="api",
                    help="B2 backend (ignored in --phase1)")
    ap.add_argument("--model", default=None,
                    help="B2 model (ignored in --phase1)")
    ap.add_argument("--no-fulltext", dest="no_fulltext", action="store_true",
                    help="disable full-text fallback")
    args = ap.parse_args()

    if args.model is None:
        args.model = ("Qwen/Qwen2.5-7B-Instruct" if args.b2 == "local"
                      else s2b.B2_MODEL_DEFAULT)

    sys.exit(run_probe(
        args.proposals, args.limit, args.out,
        args.b2, args.model, args.no_fulltext, args.phase1))


if __name__ == "__main__":
    main()
