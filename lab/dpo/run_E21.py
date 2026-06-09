import pyarrow  # noqa: F401 -- MUST be line 1 (proven run_E20B pattern: preload before torch -> dodge SEH)

import os
# ENV-WART set BEFORE importing semantic_retrieve (its FLOOR is read at import time; default 0.55 = FOOTGUN)
os.environ.setdefault("ONTO_RETRIEVE_FLOOR", "0.45")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
assert os.environ["ONTO_RETRIEVE_FLOOR"] == "0.45", "floor must be 0.45"

import sys, json, hashlib, argparse
import numpy as np

# frozen substrate (NOT mutated). Importing verify_E16 pulls gold_retrieve -> semantic_retrieve,
# which enables faulthandler (load-bearing Arrow-SEH recovery on this box).
import verify_E16 as v
import gold_retrieve as gr
import semantic_retrieve as sem

# CE via transformers DIRECTLY (NOT sentence_transformers: ST drags datasets->pyarrow->SEH on this box)
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

CE_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"   # NLI-free passage-ranking cross-encoder
E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
RECALL_FLOOR = 0.90           # threshold-rule pin (B2 >= 0.90); selection peeks ONLY recall
DEGENERATE_RHO = 0.95         # rerank vs cosine Spearman >= this => collinear lever => VOID
B1_CLASS, B2_CLASS, B3_CLASS = "spoof_cuestripped_entitied", "gold_backed", "negctrl_common"
B2_EXCLUDE = {"ho_23"}        # frozen exclusion (matches verify_E16._eval_heldout)

_ce_tok = _ce_model = None
def _ce_load():
    global _ce_tok, _ce_model
    if _ce_model is None:
        _ce_tok = AutoTokenizer.from_pretrained(CE_MODEL)
        _ce_model = AutoModelForSequenceClassification.from_pretrained(CE_MODEL)
        _ce_model.eval()
    return _ce_tok, _ce_model

def ce_scores(query, sources):
    if not sources: return []
    tok, model = _ce_load()
    enc = tok([query] * len(sources), list(sources), padding=True, truncation=True,
              max_length=512, return_tensors="pt")
    with torch.no_grad():
        logits = model(**enc).logits
    return logits[:, 0].cpu().numpy().astype(float).tolist()  # ms-marco: single relevance logit

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3: return float("nan")
    ra, rb = np.argsort(np.argsort(a)).astype(float), np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra*rb).sum()/d) if d else float("nan")

def candidates_with_cosine(query, mat, recs):
    """Replicate semantic_retrieve.retrieve EXACTLY (floor, top_k, order) but keep cosine + full record."""
    q = sem._embed([query])[0]
    sims = mat @ q
    order = np.argsort(-sims)
    out = []
    for i in order[:sem.TOP_K]:
        if float(sims[i]) < sem.FLOOR: break
        out.append((float(sims[i]), recs[int(i)]))
    return out

def precompute_item(item, store, mat, recs, decorr):
    """Resolve each claim of an item into a T-independent shape; collect (cos,ce) for decorrelation."""
    resolutions = []  # 'common' | 'noauth' | ('auth', [ce...])
    for s in v.segment(item["text"]):
        if v.is_qa_scaffold(s): continue
        n = v._norm(s)
        ct, ok = v.classify(s)
        if not ok: continue
        g, _sig = v.gate(s)
        asserts = (ct == "prose_provenance") or (g == "BINDABLE")
        if not asserts:
            resolutions.append("common"); continue
        query = v._strip_cite(s) or s
        cands = candidates_with_cosine(query, mat, recs)
        authorized = [(cos, r) for (cos, r) in cands if store.is_authorized(r)]
        if not authorized:
            resolutions.append("noauth"); continue
        srcs = [r["source"] for (_c, r) in authorized]
        scs = ce_scores(query, srcs)
        for (cos, _r), sc in zip(authorized, scs): decorr.append((cos, sc))
        resolutions.append(("auth", scs))
    return resolutions

def item_label_at_T(resolutions, T):
    labs = []
    for r in resolutions:
        if r == "common":   labs.append("PASS-COMMON")
        elif r == "noauth": labs.append("UNVERIFIABLE")
        else:               labs.append("VERIFIED" if max(r[1]) >= T else "UNVERIFIABLE")
    if not labs: return "PASS-COMMON"
    if "UNVERIFIABLE" in labs: return "DEMOTE"
    if "VERIFIED" in labs: return "VERIFIED"
    return "PASS-COMMON"

def metrics_at_T(items_pre, T):
    res = [(it, item_label_at_T(r, T)) for (it, r) in items_pre]
    b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
    b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
    B1 = sum(l == "DEMOTE" for _, l in b1) / len(b1) if b1 else float("nan")
    B2 = sum(l == "VERIFIED" for _, l in b2) / len(b2) if b2 else float("nan")
    B3 = sum(l == "DEMOTE" for _, l in b3) / len(b3) if b3 else float("nan")
    return B1, B2, B3, (len(b1), len(b2), len(b3))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="eval/_local/gold_fixture_E18.json")
    ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
    ap.add_argument("--fixture_md5", default="493b8ada955edd89c0f169609a121887")
    ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
    ap.add_argument("--out", default="reports/report_E21.md")
    a = ap.parse_args()

    fm, hm = md5(a.fixture), md5(a.heldout)
    print(f"[md5] fixture {fm} {'OK' if fm==a.fixture_md5 else 'MISMATCH'} | heldout {hm} {'OK' if hm==a.heldout_md5 else 'MISMATCH'}")
    assert fm == a.fixture_md5, "fixture md5 mismatch -> STOP (not E18)"
    assert hm == a.heldout_md5, "heldout md5 mismatch -> STOP (not v3)"

    store = gr.GoldStore(a.fixture)
    mat, recs = sem.build_index(store.records)
    items = [json.loads(l) for l in open(a.heldout, encoding="utf-8") if l.strip()]
    print(f"[fixture] records={len(store.records)} manifest={len(store.manifest_files)} | heldout items={len(items)}")
    cls = {}
    for it in items: cls[it["class"]] = cls.get(it["class"], 0) + 1
    print(f"[classes] {cls}")
    assert B1_CLASS in cls and B2_CLASS in cls, "heldout missing B1/B2 classes -> wrong file"

    decorr = []
    items_pre = [(it, precompute_item(it, store, mat, recs, decorr)) for it in items]

    rho = spearman([c for c, _ in decorr], [s for _, s in decorr])
    degenerate = (not np.isnan(rho)) and rho >= DEGENERATE_RHO
    print(f"[guard] spearman(rerank,cosine) rho={rho:.3f} pairs={len(decorr)} degenerate={degenerate}")

    # baseline sanity (no rerank, T=-inf): MUST reproduce E20-B false-accept ~0.467
    B1b, B2b, B3b, ns = metrics_at_T(items_pre, float("-inf"))
    fa_base = 1.0 - B1b
    print(f"[baseline T=-inf] B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (expect ~0.467) n={ns}")
    base_ok = 0.40 <= fa_base <= 0.53
    if not base_ok:
        print(f"[WARN] baseline false-accept {fa_base:.3f} != E20-B 0.467 -> harness wiring mismatch, STOP and reconcile")

    # threshold grid = unique CE scores among authorized candidates
    grid = sorted({s for (_it, r) in items_pre for x in r if isinstance(x, tuple) for s in x[1]})
    chosen_T = chosen_B2 = None
    for T in reversed(grid):  # highest first = most conservative
        _b1, b2, _b3, _ = metrics_at_T(items_pre, T)
        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
            chosen_T, chosen_B2 = float(T), float(b2); break

    if chosen_T is None:
        verdict = "FAIL_RECALL_UNUSABLE"; B1=B2=B3=fa=move=float("nan")
    else:
        B1, B2, B3, _ = metrics_at_T(items_pre, chosen_T)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if not base_ok:        verdict = "VOID_BASELINE_MISMATCH"
        elif degenerate:       verdict = "VOID_DEGENERATE_LEVER"
        elif fa <= GATE_FA:    verdict = "PASS"
        elif abs(move) <= 0.05: verdict = "FAIL_NO_MOVEMENT"
        else:                  verdict = "FAIL_PARTIAL_MOVEMENT"

    L = [
        "# report_E21 -- cross-encoder binder-escalation, SAME E20-B gate (frozen)",
        "",
        f"- lever          : {CE_MODEL} (NLI-free), pre-authorize rerank-filter on retrieved candidates",
        f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
        f"- fixture md5    : {fm} (E18) | heldout md5 : {hm} (v3)",
        f"- heldout classes: {cls}",
        "",
        "## decorrelation guard (falsifiability)",
        f"- spearman(rerank,cosine) rho = {rho:.3f} over {len(decorr)} authorized pairs (VOID if >= {DEGENERATE_RHO})",
        "",
        "## baseline sanity (no rerank, T=-inf) -- must reproduce E20-B",
        f"- B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (E20-B 0.467) reproduced={base_ok}",
        "",
        "## threshold rule (frozen: highest T with B2>=0.90; peek only recall)",
        f"- chosen T = {chosen_T} | B2 at op-point = {chosen_B2}",
        "",
        "## gate (frozen E20-B: false-accept <= 0.10 == B1 >= 0.90)",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E21 sec6): PASS->reranker becomes gate-2 selector, design RFT loop |",
        "FAIL_NO_MOVEMENT->R6 confirmed, bindability insufficient, TERMINAL cheap-Entity, escalate substrate |",
        "FAIL_PARTIAL_MOVEMENT->lever right, substrate-bound, escalate substrate |",
        "FAIL_RECALL_UNUSABLE->reranker destroys recall | VOID_*->rebuild before any conclusion.",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
