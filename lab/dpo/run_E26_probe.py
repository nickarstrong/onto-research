import pyarrow  # noqa: F401 -- MUST be line 1 (proven run_E20B/run_E21 pattern: preload before torch -> dodge SEH)

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

# Scorer via transformers DIRECTLY (NOT sentence_transformers: ST drags datasets->pyarrow->SEH on this box)
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# E26 = PIVOT. PRE_REGISTER_E26.md (frozen, committed ea736a5). E25b falsified COVERAGE as the limiter and
#   established the pure-ENTAILMENT reject organ ceiling fa~0.20 > gate 0.10 (architectural). E26 changes the
#   reject SIGNAL, not the data: premise=authorized finding (content-binding kept; NECESSARY, proven E22->E24),
#   hypothesis=claim, read P(CONTRADICTION) instead of P(entailment). PRIMITIVE = contradiction-veto: a claim
#   is VETOED (demoted) when any authorized premise CONTRADICTS it above threshold C. Hypothesis H1: cue-
#   stripped+entitied spoofs are CONTRADICTED by the real finding even where not ENTAILED -> contradiction-max
#   separates where entailment-max plateaued. SAME frozen gate (fa<=0.10), SAME baseline-sanity trust gate
#   (no-veto fa 0.467), iso-recall T rule (B2>=0.90), decorrelation guard. NEW file; frozen substrate untouched.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "facebook/bart-large-mnli")   # model-scale NLI; override via env
E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
PARTIAL_BAND = 0.20           # 0.10 < fa < 0.20 = PARTIAL ; fa >= 0.20 = plateau (contradiction insufficient)
RECALL_FLOOR = 0.90           # iso-recall pin (B2 >= 0.90); selection peeks ONLY recall
DEGENERATE_RHO = 0.95         # contradiction vs cosine Spearman >= this => collinear lever => VOID
B1_CLASS, B2_CLASS, B3_CLASS = "spoof_cuestripped_entitied", "gold_backed", "negctrl_common"
B2_EXCLUDE = {"ho_23"}        # frozen exclusion (matches verify_E16._eval_heldout); no-op on heldout_E17

_ce_tok = _ce_model = _con_idx = None
def _ce_load():
    global _ce_tok, _ce_model, _con_idx
    if _ce_model is None:
        _ce_tok = AutoTokenizer.from_pretrained(CE_MODEL)
        _ce_model = AutoModelForSequenceClassification.from_pretrained(CE_MODEL)
        _ce_model.eval()
        # READ contradiction index from the model card (label order differs across NLI models) -- never hardcode.
        id2label = {int(k): str(lbl).lower() for k, lbl in _ce_model.config.id2label.items()}
        con = [i for i, lbl in id2label.items() if "contradic" in lbl]
        assert len(con) == 1, f"cannot locate a single contradiction label in id2label={id2label}"
        _con_idx = con[0]
        print(f"[ce] model={CE_MODEL} id2label={id2label} contradiction_idx={_con_idx}")
    return _ce_tok, _ce_model, _con_idx

def ce_scores(claim, sources):
    """NLI contradiction. premise=source(finding), hypothesis=claim -> P(contradiction) per source.
    Direction is load-bearing (E26 PIVOT): 'does the authorized source CONTRADICT the claim'. Probs in [0,1]."""
    if not sources: return []
    tok, model, con_idx = _ce_load()
    enc = tok(list(sources), [claim] * len(sources), padding=True, truncation=True,
              max_length=512, return_tensors="pt")   # arg0 = premise = source ; arg1 = hypothesis = claim
    with torch.no_grad():
        logits = model(**enc).logits                 # (n, num_labels)
    probs = torch.softmax(logits, dim=-1)[:, con_idx]
    return probs.cpu().numpy().astype(float).tolist()

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

def precompute_item(item, store, mat, recs, decorr, prem_log, finding_by_source, diag):
    """Resolve each claim of an item into a C-independent shape; collect (cos,contradiction) for decorrelation.
    premise = source.finding if non-empty else source (content-binding probe). prem_log records which was used.
    BYTE-IDENTICAL to run_E25.precompute_item -- it is agnostic to ent/con; ce_scores now returns contradiction."""
    resolutions = []  # 'common' | 'noauth' | ('auth', [contradiction...])
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
        prems = []; kinds = []
        for (_c, r) in authorized:
            f = finding_by_source.get(r["source"], "")
            prems.append(f if f else r["source"])
            k = "finding" if f else "source"
            kinds.append(k); prem_log.append(k)
        scs = ce_scores(query, prems)
        for k, sc in zip(kinds, scs): diag.append((item["class"], k, float(sc)))
        for (cos, _r), sc in zip(authorized, scs): decorr.append((cos, sc))
        resolutions.append(("auth", scs))
    return resolutions

def item_label_at_C(resolutions, C):
    """Contradiction-veto: an authorized claim is VETOED (UNVERIFIABLE) when max contradiction >= C, else VERIFIED.
    Baseline C=+inf => nothing vetoed => only noauth demotes => reproduces the no-veto fa 0.467 (model-independent).
    Rollup identical to run_E25 (UNVERIFIABLE dominates -> DEMOTE)."""
    labs = []
    for r in resolutions:
        if r == "common":   labs.append("PASS-COMMON")
        elif r == "noauth": labs.append("UNVERIFIABLE")
        else:               labs.append("UNVERIFIABLE" if max(r[1]) >= C else "VERIFIED")
    if not labs: return "PASS-COMMON"
    if "UNVERIFIABLE" in labs: return "DEMOTE"
    if "VERIFIED" in labs: return "VERIFIED"
    return "PASS-COMMON"

def metrics_at_C(items_pre, C):
    res = [(it, item_label_at_C(r, C)) for (it, r) in items_pre]
    b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
    b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
    B1 = sum(l == "DEMOTE" for _, l in b1) / len(b1) if b1 else float("nan")
    B2 = sum(l == "VERIFIED" for _, l in b2) / len(b2) if b2 else float("nan")
    B3 = sum(l == "DEMOTE" for _, l in b3) / len(b3) if b3 else float("nan")
    return B1, B2, B3, (len(b1), len(b2), len(b3))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="eval/_local/gold_fixture_E25b.json")
    ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
    ap.add_argument("--fixture_md5", default="4a45f52883a802e8d8d1d5ff5d185bdb")
    ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
    ap.add_argument("--out", default="reports/report_E26.md")
    a = ap.parse_args()

    fm, hm = md5(a.fixture), md5(a.heldout)
    print(f"[md5] fixture {fm} {'OK' if fm==a.fixture_md5 else 'MISMATCH'} | heldout {hm} {'OK' if hm==a.heldout_md5 else 'MISMATCH'}")
    assert fm == a.fixture_md5, "fixture md5 mismatch -> STOP (not E25b)"
    assert hm == a.heldout_md5, "heldout md5 mismatch -> STOP (not v3)"

    store = gr.GoldStore(a.fixture)
    mat, recs = sem.build_index(store.records)
    items = [json.loads(l) for l in open(a.heldout, encoding="utf-8") if l.strip()]
    print(f"[fixture] records={len(store.records)} manifest={len(store.manifest_files)} | heldout items={len(items)}")
    cls = {}
    for it in items: cls[it["class"]] = cls.get(it["class"], 0) + 1
    print(f"[classes] {cls}")
    assert B1_CLASS in cls and B2_CLASS in cls, "heldout missing B1/B2 classes -> wrong file"

    decorr = []; prem_log = []; diag = []
    raw = json.load(open(a.fixture, encoding="utf-8"))   # frozen GoldStore drops "finding"; read it from raw
    finding_by_source = {rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]}
    n_with_finding = sum(1 for v_ in finding_by_source.values() if v_)
    print(f"[sidemap] sources={len(finding_by_source)} with_finding={n_with_finding}")
    items_pre = [(it, precompute_item(it, store, mat, recs, decorr, prem_log, finding_by_source, diag)) for it in items]
    n_prem = len(prem_log); n_find = sum(p == "finding" for p in prem_log)
    print(f"[premise] from_finding={n_find}/{n_prem} from_source(fallback)={n_prem-n_find}")
    assert n_find > 0, "from_finding=0 -> fixture dropped 'finding' -> VOID-by-construction (E23 guard)"

    rho = spearman([c for c, _ in decorr], [s for _, s in decorr])
    degenerate = (not np.isnan(rho)) and rho >= DEGENERATE_RHO
    print(f"[guard] spearman(contradiction,cosine) rho={rho:.3f} pairs={len(decorr)} degenerate={degenerate}")

    # baseline sanity (NO veto, C=+inf): MUST reproduce the no-veto false-accept ~0.467 (model-INDEPENDENT)
    B1b, B2b, B3b, ns = metrics_at_C(items_pre, float("inf"))
    fa_base = 1.0 - B1b
    print(f"[baseline C=+inf] B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (expect ~0.467) n={ns}")
    base_ok = 0.40 <= fa_base <= 0.53
    if not base_ok:
        print(f"[WARN] baseline false-accept {fa_base:.3f} != no-veto 0.467 -> harness wiring mismatch, STOP and reconcile")

    # iso-recall veto threshold = LOWEST C (most aggressive veto) that still holds gold recall B2 >= 0.90.
    # B2 is monotone increasing in C (higher C = less veto = more gold VERIFIED) -> first ascending C with B2>=floor.
    grid = sorted({s for (_it, r) in items_pre for x in r if isinstance(x, tuple) for s in x[1]})
    chosen_C = chosen_B2 = None
    for C in grid:  # ascending = most aggressive first
        _b1, b2, _b3, _ = metrics_at_C(items_pre, C)
        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
            chosen_C, chosen_B2 = float(C), float(b2); break

    if chosen_C is None:
        verdict = "FAIL_RECALL_UNUSABLE"; B1=B2=B3=fa=move=float("nan")
    else:
        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if not base_ok:               verdict = "VOID_BASELINE_MISMATCH"
        elif degenerate:              verdict = "VOID_DEGENERATE_LEVER"
        elif fa <= GATE_FA:           verdict = "PASS"
        elif fa < PARTIAL_BAND:       verdict = "FAIL_PARTIAL_VETO"
        else:                         verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"

    L = [
        "# report_E26 -- contradiction-veto reject primitive (PIVOT), SAME frozen gate",
        "",
        f"- lever          : {CE_MODEL} -- P(CONTRADICTION), premise=source.FINDING (fallback source) / hypothesis=claim",
        f"- pivot rationale: E25b falsified coverage; pure-entailment reject organ ceiling fa~0.20 > gate 0.10 (architectural).",
        f"                   E26 changes the SIGNAL not the data: veto a claim when an authorized premise CONTRADICTS it.",
        f"- premise content: from_finding={n_find}/{n_prem} (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)",
        f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
        f"- fixture md5    : {fm} (E25b) | heldout md5 : {hm}",
        f"- heldout classes: {cls}",
        "",
        "## decorrelation guard (falsifiability)",
        f"- spearman(contradiction,cosine) rho = {rho:.3f} over {len(decorr)} authorized pairs (VOID if >= {DEGENERATE_RHO})",
        "",
        "## baseline sanity (NO veto, C=+inf) -- model-independent, must reproduce no-veto fa 0.467",
        f"- B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (no-veto 0.467) reproduced={base_ok}",
        "",
        "## iso-recall veto rule (frozen: LOWEST C with B2>=0.90; peek only recall)",
        f"- chosen C = {chosen_C} | B2 at op-point = {chosen_B2}",
        "",
        "## gate (frozen: false-accept <= 0.10 == B1 >= 0.90)",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E26.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate): "
        "PASS (fa<=0.10 at B2>=0.90) -> contradiction-veto IS the reject primitive -> integrate + full gate + 3 "
        "secondaries | FAIL_PARTIAL_VETO (0.10<fa<0.20) -> tune veto threshold/direction, ONE more readout, no new "
        "data | FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT (fa>=0.20) -> contradiction signal ALSO insufficient -> "
        "FALLBACK branch: passage-NLI (Tommy go for passage authoring) OR ACCEPT/REJECT as separate organs (NORTH "
        "STAR reframe) | FAIL_RECALL_UNUSABLE -> veto destroys gold recall | VOID_* -> rebuild before any conclusion.",
    ]
    # --- E26 diagnostics (additive; verdict above unchanged) ------------------------------
    def _summ(vals):
        if not vals: return "n=0"
        arr = np.array(vals, float)
        return (f"n={len(arr)} mean={arr.mean():.4f} p10={np.percentile(arr,10):.4f} "
                f"p50={np.percentile(arr,50):.4f} p90={np.percentile(arr,90):.4f}")
    groups = {}
    for cls, k, sc in diag: groups.setdefault((cls, k), []).append(sc)
    L += ["", "## E26 diagnostics -- CONTRADICTION score by (item-class, premise-kind)"]
    for key in sorted(groups): L.append(f"- {key[0]:28s} premise={key[1]:7s} : {_summ(groups[key])}")
    gc  = [sc for cls, k, sc in diag if k == "finding" and cls == B2_CLASS]   # gold, content (want LOW contradiction)
    spc = [sc for cls, k, sc in diag if k == "finding" and cls == B1_CLASS]   # spoof, content (want HIGH contradiction)
    gc_p50  = float(np.percentile(gc, 50)) if gc else float("nan")
    spc_p50 = float(np.percentile(spc, 50)) if spc else float("nan")
    sep = spc_p50 - gc_p50   # veto-correct direction: spoof contradiction ABOVE gold
    C = chosen_C if chosen_C is not None else float("nan")
    gv = sum(s >= C for s in gc) if (gc and chosen_C is not None) else float("nan")   # gold falsely vetoed
    sv = sum(s >= C for s in spc) if (spc and chosen_C is not None) else float("nan")  # spoof correctly vetoed
    L += [
        "",
        f"## contradiction separation (chosen_C={C:.5f}; veto when contradiction >= C)",
        f"- gold-content  (want LOW)  : {_summ(gc)} | vetoed(>=C, false): {gv}/{len(gc)}",
        f"- spoof-content (want HIGH) : {_summ(spc)} | vetoed(>=C, true): {sv}/{len(spc)}",
        f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
        "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
        "  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
