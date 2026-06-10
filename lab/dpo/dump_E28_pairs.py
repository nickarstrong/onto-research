import pyarrow  # noqa: F401 -- MUST be line 1 (preload before torch -> dodge Arrow-SEH on this box)

import os
# ENV-WART set BEFORE importing semantic_retrieve (FLOOR read at import; default 0.55 = FOOTGUN)
os.environ.setdefault("ONTO_RETRIEVE_FLOOR", "0.45")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
assert os.environ["ONTO_RETRIEVE_FLOOR"] == "0.45", "floor must be 0.45"

import json, hashlib, argparse
import numpy as np

# frozen substrate (NOT mutated). verify_E16 pulls gold_retrieve -> semantic_retrieve + enables faulthandler.
import verify_E16 as v
import gold_retrieve as gr
import semantic_retrieve as sem

# E29 provenance-recovery helper (TYPE A instrumentation). RETRIEVAL ONLY -- no NLI, no scoring, no verdict.
# run_E28 dropped the per-pair source/finding (diag kept only id+con+cos). Binding is DETERMINISTIC, so we
# replay candidates_with_cosine BYTE-IDENTICAL and emit (id, kind, source, finding, cos) per authorized
# candidate. cos is the unique fingerprint that maps report_E28 S1 tail rows back to their premise record.
# NO model eval (bart never loaded). Frozen modules read-only. Output is LOCAL/gitignored.


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def candidates_with_cosine(query, mat, recs):
    """Replicate semantic_retrieve.retrieve EXACTLY (floor, top_k, order) but keep cosine + full record.
    Byte-identical to run_E28_probe.candidates_with_cosine."""
    q = sem._embed([query])[0]
    sims = mat @ q
    order = np.argsort(-sims)
    out = []
    for i in order[:sem.TOP_K]:
        if float(sims[i]) < sem.FLOOR:
            break
        out.append((float(sims[i]), recs[int(i)]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="eval/_local/gold_fixture_E25b.json")
    ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
    ap.add_argument("--fixture_md5", default="4a45f52883a802e8d8d1d5ff5d185bdb")
    ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
    ap.add_argument("--out", default="E28_pairs_gold.json")
    ap.add_argument("--only_class", default="gold_backed")
    a = ap.parse_args()

    fm, hm = md5(a.fixture), md5(a.heldout)
    print(f"[md5] fixture {fm} {'OK' if fm==a.fixture_md5 else 'MISMATCH'} | "
          f"heldout {hm} {'OK' if hm==a.heldout_md5 else 'MISMATCH'}")
    assert fm == a.fixture_md5, "fixture md5 mismatch -> STOP (not E25b)"
    assert hm == a.heldout_md5, "heldout md5 mismatch -> STOP (not v3)"

    store = gr.GoldStore(a.fixture)
    mat, recs = sem.build_index(store.records)
    items = [json.loads(l) for l in open(a.heldout, encoding="utf-8") if l.strip()]
    print(f"[fixture] records={len(store.records)} manifest={len(store.manifest_files)} | "
          f"heldout items={len(items)}")

    raw = json.load(open(a.fixture, encoding="utf-8"))  # frozen GoldStore drops 'finding'; read from raw
    finding_by_source = {rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]}

    rows = []
    for item in items:
        if a.only_class and item.get("class") != a.only_class:
            continue
        for s in v.segment(item["text"]):
            if v.is_qa_scaffold(s):
                continue
            ct, ok = v.classify(s)
            if not ok:
                continue
            g, _sig = v.gate(s)
            asserts = (ct == "prose_provenance") or (g == "BINDABLE")
            if not asserts:
                continue
            query = v._strip_cite(s) or s
            cands = candidates_with_cosine(query, mat, recs)
            authorized = [(cos, r) for (cos, r) in cands if store.is_authorized(r)]
            for (cos, r) in authorized:
                f = finding_by_source.get(r["source"], "")
                rows.append({
                    "id": item["id"],
                    "class": item["class"],
                    "kind": "finding" if f else "source",
                    "cos": round(float(cos), 6),
                    "claim_key": r.get("claim_key", ""),
                    "locator": r.get("locator", ""),
                    "source": r["source"],
                    "finding": f,            # premise the NLI actually read (empty -> premise was source string)
                    "heldout_anchor": item.get("anchor", ""),
                    "heldout_text": item.get("text", ""),
                })

    json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    n_find = sum(1 for x in rows if x["kind"] == "finding")
    print(f"[dump] rows={len(rows)} from_finding={n_find} from_source={len(rows)-n_find} -> {a.out}")
    print(f"[dump] out_md5={md5(a.out)}")


if __name__ == "__main__":
    main()
