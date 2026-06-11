import pyarrow  # noqa: F401 -- MUST be line 1 (E37/E20B pattern: preload before torch path -> dodge SEH)

import os
# match E37 env EXACTLY (semantic_retrieve reads FLOOR at import; default 0.55 = FOOTGUN)
os.environ.setdefault("ONTO_RETRIEVE_FLOOR", "0.45")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
assert os.environ["ONTO_RETRIEVE_FLOOR"] == "0.45", "floor must be 0.45"

import sys, json, hashlib, argparse, importlib.util, inspect
from statistics import quantiles

# ============================================================================
# run_E38_Sdist_probe.py  --  E38 corpus-vs-construction disambiguator
#   PAIRING-RECONCILED (v84 run) against the REAL E37/E25b/E17 interface.
#
# RECONCILE LOG (declared; supersedes the v83 frozen-probe schema ASSUMPTIONS,
#   sanctioned by that file's own header "reconcile at v84 pairing"):
#   R1. The v83 probe assumed heldout/fixture carry a per-item `candidates` list and
#       called bind(claim, cands). FALSE: heldout_E17 items are {text,class,id}; the
#       fixture is {records,manifest} (NOT keyed by id). The v83 fallback yields []
#       for EVERY item -> |S|=0 everywhere -> a FAKE A_CONSTRUCTION_CEILING
#       (VOID-by-construction, E23/E15 class). Caught PRE-DATA at pairing.
#   R2. |S| in E37 is NOT a "lexically-bound set, floor 0.45 top_k 5". It is the
#       AUTHORIZED COSINE-retrieved candidate set per asserting claim (sem.FLOOR 0.45,
#       sem.TOP_K 5 are the COSINE retrieval params; lexical binding_score in [0,1] is
#       a per-candidate score gated by the SWEPT B_floor, not a fixed floor).
#   R3. PRE_REGISTER sec0 "loads NO model" is corrected to "loads NO NLI model": the
#       cosine retrieval embedder (semantic_retrieve) IS required to reproduce E37's
#       bound set byte-identically. Still no-GPU, no-NLI, no pod.
#
#   INTEGRITY (unchanged contract):
#   - resolution is REPLAYED via E37's OWN imported callables (v.segment/classify/gate,
#     candidates_with_cosine, store.is_authorized) -> byte-identical BY CONSTRUCTION;
#     no reimplementation, no edit to the frozen E37 file.
#   - |S| computed CLASS-BLIND over ALL items; class joined ONLY for per-class reporting.
#   - all inputs md5-gated; any mismatch / empty pass -> VOID (no readout trusted).
#   - FORK sec6 UNCHANGED (decision on |S|); the per-class p50 (already a sec4 observable)
#     resolves the INDETERMINATE band at the mechanism level.
# ============================================================================

MD5_HELDOUT = "7e9fe030646d5671952e7a9fe9437e37"   # heldout_E17.jsonl
MD5_FIXTURE = "4a45f52883a802e8d8d1d5ff5d185bdb"   # gold_fixture_E25b.json
MD5_E37     = "15e694a6690a70b801431d64c0b5c368"   # run_E37_probe.py (binding/resolution source; imported)

CLASS_GOLD, CLASS_SPOOF, CLASS_NEGCTRL = "gold_backed", "spoof_cuestripped_entitied", "negctrl_common"
CLASSES = (CLASS_GOLD, CLASS_SPOOF, CLASS_NEGCTRL)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def gate(path, expect, name):
    got = md5_of(path)
    if got != expect:
        sys.exit("VOID: md5 mismatch on %s -- got %s expected %s" % (name, got, expect))
    return got


def import_e37(e37_path):
    if not os.path.isfile(e37_path):
        sys.exit("VOID: run_E37_probe.py not found at %s" % e37_path)
    spec = importlib.util.spec_from_file_location("e37_probe", e37_path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        sys.exit("VOID: run_E37_probe.py not import-safe (%s)." % exc)
    # provenance: the resolution callables must originate in the E37 module file.
    for fn_name in ("candidates_with_cosine",):
        fn = getattr(mod, fn_name, None)
        if not callable(fn):
            sys.exit("VOID: E37 missing callable %s -- resolution cannot be replayed." % fn_name)
        origin = inspect.getsourcefile(fn) or ""
        if os.path.realpath(origin) != os.path.realpath(e37_path):
            sys.exit("VOID: %s origin %s != run_E37_probe.py -- replay not byte-identical." % (fn_name, origin))
    for sub in ("v", "gr", "sem"):
        if getattr(mod, sub, None) is None:
            sys.exit("VOID: E37 did not expose substrate handle '%s'." % sub)
    return mod


def pcts(vals):
    if not vals:
        return {"p10": None, "p50": None, "p90": None, "max": None, "min": None, "n": 0}
    s = sorted(vals)
    if len(s) == 1:
        q = [s[0]] * 9
    else:
        q = quantiles(s, n=10, method="inclusive")
    return {"p10": q[0], "p50": s[len(s) // 2], "p90": q[8], "max": s[-1], "min": s[0], "n": len(s)}


def share_le(vals, t):
    if not vals:
        return None
    return sum(1 for v in vals if v <= t) / len(vals)


def _fork(p50, share_le1):
    """PRE_REGISTER_E38 sec6 -- UNCHANGED. Diagnostic only; no fa/bf verdict."""
    if p50 is None:
        return "VOID"
    if p50 <= 1 or (share_le1 is not None and share_le1 >= 0.50):
        return "A_CONSTRUCTION_CEILING"
    if p50 >= 3:
        return "B_STATISTIC_WRONG"
    return "INDETERMINATE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heldout", required=True)
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--e37", required=True, help="run_E37_probe.py (resolution source; imported)")
    ap.add_argument("--boundset", default="", help="optional E37 P=0 bound-set dump for byte-identity anchor")
    ap.add_argument("--dump-boundset", default="reports/E37_boundset.json",
                    help="write the per-item authorized bound set (future byte-exact anchor)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # --- md5 gate (VOID on mismatch) ---
    gate(args.heldout, MD5_HELDOUT, "heldout_E17.jsonl")
    gate(args.fixture, MD5_FIXTURE, "gold_fixture_E25b.json")
    gate(args.e37, MD5_E37, "run_E37_probe.py")

    e37 = import_e37(args.e37)
    v, gr, sem = e37.v, e37.gr, e37.sem

    items = [json.loads(l) for l in open(args.heldout, encoding="utf-8") if l.strip()]
    if not items:
        sys.exit("VOID: heldout has 0 items (E23 empty-pass guard).")

    store = gr.GoldStore(args.fixture)
    mat, recs = sem.build_index(store.records)
    raw = json.load(open(args.fixture, encoding="utf-8"))
    finding_by_source = {rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]}
    print("[fixture] records=%d | heldout items=%d" % (len(store.records), len(items)))

    # --- CLASS-BLIND resolution replay (E37's OWN callables; no NLI) ---
    # per ASSERTING claim: |S| = number of AUTHORIZED cosine-retrieved candidates (the SET con_share divides by).
    per_item = []            # {id, class, claim_S_sizes:[...], item_bound_ids:[...]}
    boundset_dump = {}
    n_assert_total = 0
    for it in items:
        claim_S = []
        item_ids = set()
        for s in v.segment(it["text"]):
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
            cands = e37.candidates_with_cosine(query, mat, recs)
            authorized = [(cos, r) for (cos, r) in cands if store.is_authorized(r)]
            if not authorized:
                continue
            ids = sorted(str(r["source"]) for (cos, r) in authorized)
            claim_S.append(len(ids))
            item_ids.update(ids)
            n_assert_total += 1
        per_item.append({"id": it["id"], "class": it.get("class"),
                         "claim_S_sizes": claim_S, "item_bound_ids": sorted(item_ids)})
        boundset_dump[str(it["id"])] = sorted(item_ids)

    if n_assert_total == 0:
        sys.exit("VOID: 0 asserting authorized claims -> empty-by-construction (E23 guard).")
    if not any(r["class"] == CLASS_GOLD and r["claim_S_sizes"] for r in per_item):
        sys.exit("VOID: 0 gold_backed asserting claims -> empty-by-construction (E23 guard).")

    # --- regression anchor: P=0 bound set byte-identical to E37 (sec5) ---
    anchor = {"mode": "by-construction (imported E37 resolution callables)", "boundset_diff": None}
    if args.boundset and os.path.isfile(args.boundset):
        ref = json.load(open(args.boundset, encoding="utf-8"))
        diffs = [r["id"] for r in per_item
                 if sorted(str(x) for x in ref.get(str(r["id"]), ref.get(r["id"], []))) != r["item_bound_ids"]]
        anchor["boundset_diff"] = diffs
        if diffs:
            sys.exit("VOID: P=0 bound set diverges from E37 on %d items." % len(diffs))

    # --- |S| distributions: PER ASSERTING CLAIM (the set con_share reads) ---
    S_claim_all = [n for r in per_item for n in r["claim_S_sizes"]]
    by_class_claim = {c: [] for c in CLASSES}
    by_class_claim["_unlabeled"] = []
    for r in per_item:
        by_class_claim.setdefault(r["class"] if r["class"] in CLASSES else "_unlabeled", []).extend(r["claim_S_sizes"])
    # PER ITEM (sec4 wording): union of bound sources per item
    S_item_all = [len(r["item_bound_ids"]) for r in per_item if r["claim_S_sizes"]]
    # n_sources for gold == |S| over gold-bound claims (each authorized source = one independent gold source)
    n_sources_gold = by_class_claim[CLASS_GOLD]

    p50_claim = pcts(S_claim_all)["p50"]
    out = {
        "experiment": "E38",
        "reconcile": "pairing-reconciled v84 (imported E37 resolution; no NLI; embedder required)",
        "n_items": len(per_item),
        "n_asserting_claims": n_assert_total,
        "S_per_claim_overall": {**pcts(S_claim_all), "share_le_1": share_le(S_claim_all, 1)},
        "S_per_item_overall": {**pcts(S_item_all), "share_le_1": share_le(S_item_all, 1)},
        "S_per_claim_by_class": {c: {**pcts(by_class_claim.get(c, [])),
                                     "share_le_1": share_le(by_class_claim.get(c, []), 1)} for c in CLASSES},
        "n_sources_gold": {**pcts(n_sources_gold), "share_le_1": share_le(n_sources_gold, 1)},
        "anchor": anchor,
        "fork_global": _fork(p50_claim, share_le(S_claim_all, 1)),
        "fork_mechanism_spoof": _fork(pcts(by_class_claim[CLASS_SPOOF])["p50"],
                                      share_le(by_class_claim[CLASS_SPOOF], 1)),
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(out, open(args.out, "w", encoding="utf-8"), indent=2)
    if args.dump_boundset:
        os.makedirs(os.path.dirname(os.path.abspath(args.dump_boundset)), exist_ok=True)
        json.dump(boundset_dump, open(args.dump_boundset, "w", encoding="utf-8"), indent=2)

    print("[S per claim overall]", json.dumps(out["S_per_claim_overall"]))
    for c in CLASSES:
        print("[S per claim %-26s]" % c, json.dumps(out["S_per_claim_by_class"][c]))
    print("FORK_global   :", out["fork_global"])
    print("FORK_spoof_mech:", out["fork_mechanism_spoof"])
    print("[written]", args.out, "+", args.dump_boundset)


if __name__ == "__main__":
    sys.exit(main())
