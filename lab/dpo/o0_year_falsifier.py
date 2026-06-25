#!/usr/bin/env python3
# o0_year_falsifier.py -- v274 HERMETIC Y-CHANNEL DIRTY-YEAR FALSIFIER (offline, no network).
# Runs the SEALED F-bars (PREREG_year_channel_falsifier_20260625.md, e618ef6) against on-disk
# frozen verdicts. The falsifier loop NEVER calls the oracle: it reads the frozen per_year from
# heldout_verdicts and applies the additive offline REFUTE override (apply_offline_dirty_year),
# then re-derives scope_verdict. Both helpers are imported UNCHANGED from o0_temporal_evidence.
#
# F-bars (sealed v273; F1 re-cut 3/3->2/2 at v274 STEP 1 by Founder ruling -- 21_1 ruled CLEAN):
#   F1 catch        : 2/2 known-dirty years (20_1=1837, 21_0=1796) -> REFUTE (scope DIRTY).
#   F2 false-fire   : 0 offline-induced REFUTE on GT-CLEAN control rows (post-P4 sealed_labels).
#   F3 discrimination: pure-ABSTAIN baseline (no override) FAILS F1 (catch arm provably exercised).
#   F4 hermetic     : 2 runs byte-identical; 0 network calls in the loop.
#
# Usage: python o0_year_falsifier.py
import json, copy, hashlib, io, sys
from o0_temporal_evidence import (load_offline_dirty_table, apply_offline_dirty_year,
                                  scope_verdict)

VERDICTS = "heldout_verdicts_20260625.jsonl"
LABELS   = "sealed_labels_heldout_20260625.jsonl"   # POST-P4 (corrected)
TABLE    = "o0_year_offline_table.jsonl"
CATCH    = ["held2_20_1", "held2_21_0"]             # F1 set (21_1 ruled OUT v274)


def load_rows(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def scope_of(rec, per_year):
    t = dict(rec.get("temporal", {}))
    t["per_year"] = per_year
    sv, sr = scope_verdict({**rec, "temporal": t})
    return sv


def emit(rows, table, apply_override):
    """Produce a deterministic serialization of {id -> (per_year, scope)} for the run.
       apply_override=False = pure-ABSTAIN baseline arm (F3)."""
    buf = io.StringIO()
    for r in sorted(rows, key=lambda x: x["id"]):
        per_year = copy.deepcopy(r.get("temporal", {}).get("per_year", {}))
        if apply_override:
            per_year = apply_offline_dirty_year(r["id"], per_year, table)
        sv = scope_of(r, per_year)
        buf.write(json.dumps({"id": r["id"], "per_year": per_year, "scope": sv},
                             ensure_ascii=False, sort_keys=True) + "\n")
    return buf.getvalue()


def main():
    rows = load_rows(VERDICTS)
    labels = {r["id"]: r["founder_label"] for r in load_rows(LABELS)}
    table = load_offline_dirty_table(TABLE)
    by_id = {r["id"]: r for r in rows}

    print("=" * 68)
    print("v274 Y-CHANNEL DIRTY-YEAR FALSIFIER -- hermetic offline run")
    print("=" * 68)
    print("rows=%d  labels=%d  table_rows=%d  catch_set=%s" %
          (len(rows), len(labels), sum(len(v) for v in table.values()), CATCH))
    print()

    # ---- main arm: apply override ----
    out_main = emit(rows, table, apply_override=True)
    main_map = {json.loads(l)["id"]: json.loads(l) for l in out_main.strip().split("\n")}

    # ---- F1 catch ----
    f1_hits = []
    for rid in CATCH:
        rec = main_map[rid]
        py = rec["per_year"]
        refuted = any(v == "REFUTE" for v in py.values())
        dirty = rec["scope"] == "DIRTY"
        f1_hits.append((rid, py, rec["scope"], refuted and dirty))
    f1_pass = all(h[3] for h in f1_hits)
    print("[F1 catch] %d/%d  -> %s" % (sum(h[3] for h in f1_hits), len(CATCH),
                                       "PASS" if f1_pass else "FAIL"))
    for rid, py, sc, ok in f1_hits:
        print("   %-14s per_year=%-22s scope=%-7s %s" % (rid, py, sc, "OK" if ok else "MISS"))

    # ---- F3 discrimination: pure-ABSTAIN baseline must FAIL F1 ----
    out_base = emit(rows, table, apply_override=False)
    base_map = {json.loads(l)["id"]: json.loads(l) for l in out_base.strip().split("\n")}
    base_hits = sum(1 for rid in CATCH
                    if any(v == "REFUTE" for v in base_map[rid]["per_year"].values())
                    and base_map[rid]["scope"] == "DIRTY")
    f3_pass = (base_hits == 0)   # baseline catches NONE -> override is what discriminates
    print("\n[F3 discrimination] baseline catch=%d/%d (must be 0) -> %s" %
          (base_hits, len(CATCH), "PASS" if f3_pass else "FAIL"))
    for rid in CATCH:
        print("   %-14s baseline per_year=%-22s scope=%s" %
              (rid, base_map[rid]["per_year"], base_map[rid]["scope"]))

    # ---- F2 false-fire on GT-CLEAN control rows (post-P4) ----
    clean_ids = [rid for rid, lab in labels.items() if lab == "CLEAN" and rid in by_id]
    false_fire = []
    for rid in clean_ids:
        base_py = base_map[rid]["per_year"]
        main_py = main_map[rid]["per_year"]
        # override-INDUCED refute = a REFUTE present after override but not before
        induced = [y for y, v in main_py.items()
                   if v == "REFUTE" and base_py.get(y) != "REFUTE"]
        if induced:
            false_fire.append((rid, induced))
    f2_pass = (len(false_fire) == 0)
    print("\n[F2 false-fire] control(GT-CLEAN, post-P4)=%d  induced-REFUTE=%d -> %s" %
          (len(clean_ids), len(false_fire), "PASS" if f2_pass else "FAIL"))
    for rid, ind in false_fire:
        print("   FALSE-FIRE %-14s %s" % (rid, ind))

    # ---- F4 hermetic: byte-identical across 2 runs; 0 network ----
    run1 = emit(rows, table, apply_override=True)
    run2 = emit(rows, table, apply_override=True)
    h1 = hashlib.md5(run1.encode()).hexdigest()
    h2 = hashlib.md5(run2.encode()).hexdigest()
    f4_pass = (h1 == h2)
    print("\n[F4 hermetic] run1=%s run2=%s  net_calls=0 -> %s" %
          (h1[:8], h2[:8], "PASS" if f4_pass else "FAIL"))

    print("\n" + "=" * 68)
    verdict = {"F1": f1_pass, "F2": f2_pass, "F3": f3_pass, "F4": f4_pass}
    for k, v in verdict.items():
        print("  %s : %s" % (k, "PASS" if v else "FAIL"))
    allpass = all(verdict.values())
    print("  OVERALL: %s" % ("ALL PASS" if allpass else "FAIL"))
    print("=" * 68)
    return 0 if allpass else 1


if __name__ == "__main__":
    sys.exit(main())
