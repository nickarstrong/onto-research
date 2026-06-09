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

# E24 = corrected E23. Same gate, same frozen model, same intended variable (premise = source CONTENT).
#   E23 was VOID: GoldStore.__init__ (frozen) drops the fixture "finding" field, so r.get("finding") was always
#   empty -> from_finding=0/139 -> premise never changed -> result byte-identical to E22 (no content test).
#   E24 keeps GoldStore frozen and injects content via a RAW-fixture side-map source->finding, looked up by the
#   authorized record's source string. premise = finding if mapped+non-empty else source (logged by prem_log).
#   Falsifier: fa<=0.10 -> the E16-E21 wall was premise-impoverishment (citation-string binding), fix = content-
#   binding (GOLD as bind-corpus), NOT scale/architecture. Still partial/no -> architectural reframe earned.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "facebook/bart-large-mnli")   # model-scale NLI; override via env
E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
RECALL_FLOOR = 0.90           # threshold-rule pin (B2 >= 0.90); selection peeks ONLY recall
DEGENERATE_RHO = 0.95         # support vs cosine Spearman >= this => collinear lever => VOID
B1_CLASS, B2_CLASS, B3_CLASS = "spoof_cuestripped_entitied", "gold_backed", "negctrl_common"
B2_EXCLUDE = {"ho_23"}        # frozen exclusion (matches verify_E16._eval_heldout); no-op on heldout_E17

_ce_tok = _ce_model = _ent_idx = None
def _ce_load():
    global _ce_tok, _ce_model, _ent_idx
    if _ce_model is None:
        _ce_tok = AutoTokenizer.from_pretrained(CE_MODEL)
        _ce_model = AutoModelForSequenceClassification.from_pretrained(CE_MODEL)
        _ce_model.eval()
        # READ entailment index from the model card (label order differs across NLI models) -- never hardcode.
        id2label = {int(k): str(lbl).lower() for k, lbl in _ce_model.config.id2label.items()}
        ent = [i for i, lbl in id2label.items() if "entail" in lbl]
        assert len(ent) == 1, f"cannot locate a single entailment label in id2label={id2label}"
        _ent_idx = ent[0]
        print(f"[ce] model={CE_MODEL} id2label={id2label} entailment_idx={_ent_idx}")
    return _ce_tok, _ce_model, _ent_idx

def ce_scores(claim, sources):
    """NLI claim-support. premise=source, hypothesis=claim -> P(entailment) per source.
    Direction is load-bearing: 'does the authorized source ENTAIL the claim'. Returns list of probs in [0,1]."""
    if not sources: return []
    tok, model, ent_idx = _ce_load()
    enc = tok(list(sources), [claim] * len(sources), padding=True, truncation=True,
              max_length=512, return_tensors="pt")   # arg0 = premise = source ; arg1 = hypothesis = claim
    with torch.no_grad():
        logits = model(**enc).logits                 # (n, num_labels)
    probs = torch.softmax(logits, dim=-1)[:, ent_idx]
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

def precompute_item(item, store, mat, recs, decorr, prem_log, finding_by_source):
    """Resolve each claim of an item into a T-independent shape; collect (cos,support) for decorrelation.
    premise = source.finding if non-empty else source (content-binding probe). prem_log records which was used."""
    resolutions = []  # 'common' | 'noauth' | ('auth', [support...])
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
        prems = []
        for (_c, r) in authorized:
            f = finding_by_source.get(r["source"], "")
            prems.append(f if f else r["source"])
            prem_log.append("finding" if f else "source")
        scs = ce_scores(query, prems)
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
    ap.add_argument("--out", default="reports/report_E24.md")
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

    decorr = []; prem_log = []
    raw = json.load(open(a.fixture, encoding="utf-8"))   # frozen GoldStore drops "finding"; read it from raw
    finding_by_source = {rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]}
    n_with_finding = sum(1 for v_ in finding_by_source.values() if v_)
    print(f"[sidemap] sources={len(finding_by_source)} with_finding={n_with_finding}")
    items_pre = [(it, precompute_item(it, store, mat, recs, decorr, prem_log, finding_by_source)) for it in items]
    n_prem = len(prem_log); n_find = sum(p == "finding" for p in prem_log)
    print(f"[premise] from_finding={n_find}/{n_prem} from_source(fallback)={n_prem-n_find}")

    rho = spearman([c for c, _ in decorr], [s for _, s in decorr])
    degenerate = (not np.isnan(rho)) and rho >= DEGENERATE_RHO
    print(f"[guard] spearman(support,cosine) rho={rho:.3f} pairs={len(decorr)} degenerate={degenerate}")

    # baseline sanity (no support-gate, T=-inf): MUST reproduce E20-B false-accept ~0.467 (model-INDEPENDENT)
    B1b, B2b, B3b, ns = metrics_at_T(items_pre, float("-inf"))
    fa_base = 1.0 - B1b
    print(f"[baseline T=-inf] B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (expect ~0.467) n={ns}")
    base_ok = 0.40 <= fa_base <= 0.53
    if not base_ok:
        print(f"[WARN] baseline false-accept {fa_base:.3f} != E20-B 0.467 -> harness wiring mismatch, STOP and reconcile")

    # threshold grid = unique support scores among authorized candidates
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
        "# report_E24 -- NLI support-gate over CONTENT premise (raw-fixture side-map), SAME E20-B gate (frozen)",
        "",
        f"- lever          : {CE_MODEL} -- P(entailment), premise=source.FINDING (fallback source) / hypothesis=claim",
        f"- vs E22/E23     : same model+gate; premise content injected via raw-fixture side-map (GoldStore frozen). premises_from_finding={n_find}/{n_prem}",
        f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
        f"- fixture md5    : {fm} (E18) | heldout md5 : {hm}",
        f"- heldout classes: {cls}",
        "",
        "## decorrelation guard (falsifiability)",
        f"- spearman(support,cosine) rho = {rho:.3f} over {len(decorr)} authorized pairs (VOID if >= {DEGENERATE_RHO})",
        "",
        "## baseline sanity (no support-gate, T=-inf) -- model-independent, must reproduce E20-B",
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
        "decision (probe-first fork, Tommy-authorized): "
        "PASS -> the E16-E21 wall was PREMISE-IMPOVERISHMENT (entailment judged against citation strings, not content); "
        "fix = content-binding (GOLD as bind-corpus, pack sec4) -- NOT scale, NOT architecture | "
        "FAIL_PARTIAL_MOVEMENT / FAIL_NO_MOVEMENT -> even content-premise model-scale entailment cannot separate the "
        "cue-stripped+entitied spoofs at iso-recall -> reject-organ failure is ARCHITECTURAL -> NORTH STAR reframe "
        "(ACCEPT/REJECT as separate organs; non-retrieval reject primitive) | FAIL_RECALL_UNUSABLE -> gate destroys "
        "gold recall | VOID_* -> rebuild before any conclusion.",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
