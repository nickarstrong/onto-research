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

# E27 = full-gate + ROBUSTNESS SWEEP of the E26 contradiction-veto reject organ. PRE_REGISTER_E27.md (FROZEN,
#   md5 20dde8b3f6d54b9417ea1007a12210d4). E26 PASSed as a SINGLE readout: fa 0.0667 <= gate 0.10 at B2 0.90,
#   movement 0.400, but the op-point was TIGHT (B2 exactly at floor, C~0.9949, 1/74 gold false-veto). E27 keeps
#   the SAME frozen gate + SAME trust gates + SAME iso-recall op-point rule (reproduce E26 = regression check)
#   and ADDS three pre-registered secondaries: S1 per-class contradiction distribution, S2 C-sweep / lift-off
#   robustness (the primary E27 question), S3 reject-vs-lift demotion attribution. NO new data. Frozen substrate
#   (verify_E16, gold_retrieve, semantic_retrieve, run_E26) untouched; footgun fixes folded into THIS file only.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "facebook/bart-large-mnli")   # model-scale NLI; override via env
E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
PARTIAL_BAND = 0.20           # 0.10 < fa < 0.20 = PARTIAL ; fa >= 0.20 = plateau (contradiction insufficient)
RECALL_FLOOR = 0.90           # iso-recall pin (B2 >= 0.90); selection peeks ONLY recall
DEGENERATE_RHO = 0.95         # contradiction vs cosine Spearman >= this => collinear lever => VOID (FROZEN E26 guard)
PREREG_RHO_ADVISORY = 0.50    # PRE_REGISTER_E27 sec4 advisory tightness (|rho| < this); REPORTED, not a VOID trigger
B1_CLASS, B2_CLASS, B3_CLASS = "spoof_cuestripped_entitied", "gold_backed", "negctrl_common"
B2_EXCLUDE = {"ho_23"}        # frozen exclusion (matches verify_E16._eval_heldout); no-op on heldout_E17

# --- S2 robustness sweep grid (FROZEN pre-data, PRE_REGISTER_E27 sec3-S2) ----------------------------------
#   coarse [0.90, 0.995] step 0.005 + fine [0.990, 0.999] step 0.001 ; C=+inf reported separately as anchor.
S2_GRID = sorted(set([round(0.900 + 0.005 * i, 3) for i in range(0, 20)] +
                     [round(0.990 + 0.001 * i, 3) for i in range(0, 10)]))
S2_BAND_MIN_WIDTH = 0.01      # joint (fa<=0.10 AND B2>=0.90) band must span >= this in C
S2_BAND_MIN_POINTS = 3        # AND contain >= this many grid points (not a single knife-edge)
S3_REJECT_SHARE_BAR = 0.50    # reject organ must own > this share of baseline false-accepts eliminated

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
    BYTE-IDENTICAL to run_E26.precompute_item -- it is agnostic to ent/con; ce_scores returns contradiction."""
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
    Rollup identical to run_E26 (UNVERIFIABLE dominates -> DEMOTE)."""
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

# ===== E27 NEW: S2 robustness sweep, S3 demotion attribution ==============================================

def s2_sweep(items_pre):
    """S2 -- evaluate fa(C) and B2(C) over the FROZEN fixed grid; locate the joint (fa<=0.10 AND B2>=0.90) band.
    Returns (rows, band) where rows = [(C, fa, B2, joint_ok)...] and band = dict with width/points/liftoff/robust."""
    rows = []
    for C in S2_GRID:
        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C))
        fa = (1.0 - B1) if not np.isnan(B1) else float("nan")
        joint = (not np.isnan(fa)) and (not np.isnan(B2)) and (fa <= GATE_FA) and (B2 >= RECALL_FLOOR)
        rows.append((float(C), float(fa), float(B2), bool(joint)))
    joint_Cs = [C for (C, _fa, _b2, ok) in rows if ok]
    joint_B2 = [b2 for (_C, _fa, b2, ok) in rows if ok]
    if joint_Cs:
        width = max(joint_Cs) - min(joint_Cs)
        points = len(joint_Cs)
        liftoff = max(joint_B2) - RECALL_FLOOR     # does B2 rise above the floor anywhere in the band?
        robust = (width >= S2_BAND_MIN_WIDTH) and (points >= S2_BAND_MIN_POINTS) and (liftoff > 0.0)
        band = dict(c_lo=min(joint_Cs), c_hi=max(joint_Cs), width=width, points=points,
                    b2_liftoff=liftoff, robust=robust)
    else:
        band = dict(c_lo=None, c_hi=None, width=0.0, points=0, b2_liftoff=0.0, robust=False)
    return rows, band

def s3_attribution(items_pre, op_C, fa_base, fa_op):
    """S3 -- decompose B1-class (spoof) demotions at the op-point into:
       (a) noauth baseline  : demotes already at C=+inf (no veto needed),
       (b) contradiction-veto reject organ : demotes at op_C but NOT at C=+inf (an auth claim crossed the veto),
       (c) accept/entailment-lift organ    : NOT wired in this standalone probe -> structurally 0
                                              (lives in the verifier-integration step, Tommy-go gated).
    reject_share = fraction of BASELINE false-accepts the veto eliminated = (fa_base - fa_op)/fa_base.
    Bar (PRE_REGISTER_E27 sec3-S3): reject_share > 0.50 == the veto, not coverage/baseline, owns the gain."""
    spoofs = [r for (it, r) in items_pre if it["class"] == B1_CLASS]
    n_total = len(spoofs)
    n_demote_op = n_by_noauth = n_by_veto = n_survive = 0
    for r in spoofs:
        base = item_label_at_C(r, float("inf"))
        op = item_label_at_C(r, float(op_C))
        if op == "DEMOTE":
            n_demote_op += 1
            if base == "DEMOTE":  n_by_noauth += 1   # would demote without the veto
            else:                 n_by_veto += 1      # demoted specifically because veto fired
        else:
            n_survive += 1
    reject_share = (fa_base - fa_op) / fa_base if fa_base > 0 else float("nan")
    return dict(n_total=n_total, n_demote_op=n_demote_op, n_by_noauth=n_by_noauth,
                n_by_veto=n_by_veto, n_survive=n_survive, n_by_entailment=0,
                reject_share=reject_share, bar_met=(not np.isnan(reject_share) and reject_share > S3_REJECT_SHARE_BAR))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="eval/_local/gold_fixture_E25b.json")
    ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
    ap.add_argument("--fixture_md5", default="4a45f52883a802e8d8d1d5ff5d185bdb")
    ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
    ap.add_argument("--out", default="reports/report_E27.md")
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
    degenerate = (not np.isnan(rho)) and rho >= DEGENERATE_RHO            # FROZEN E26 VOID guard (0.95, one-sided)
    rho_advisory_ok = (not np.isnan(rho)) and abs(rho) < PREREG_RHO_ADVISORY   # PRE_REGISTER sec4 advisory (reported)
    print(f"[guard] spearman(contradiction,cosine) rho={rho:.3f} pairs={len(decorr)} degenerate={degenerate} "
          f"|rho|<{PREREG_RHO_ADVISORY}={rho_advisory_ok}")

    # baseline sanity (NO veto, C=+inf): MUST reproduce the no-veto false-accept ~0.467 (model-INDEPENDENT)
    B1b, B2b, B3b, ns = metrics_at_C(items_pre, float("inf"))
    fa_base = 1.0 - B1b
    print(f"[baseline C=+inf] B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (expect ~0.467) n={ns}")
    base_ok = 0.40 <= fa_base <= 0.53
    if not base_ok:
        print(f"[WARN] baseline false-accept {fa_base:.3f} != no-veto 0.467 -> harness wiring mismatch, STOP and reconcile")

    # iso-recall veto threshold = LOWEST C (most aggressive veto) that still holds gold recall B2 >= 0.90.
    # FROZEN E26 rule: select over OBSERVED contradiction scores (ascending) -> reproduces E26 op-point (regression).
    grid = sorted({s for (_it, r) in items_pre for x in r if isinstance(x, tuple) for s in x[1]})
    chosen_C = chosen_B2 = None
    for C in grid:  # ascending = most aggressive first
        _b1, b2, _b3, _ = metrics_at_C(items_pre, C)
        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
            chosen_C, chosen_B2 = float(C), float(b2); break

    if chosen_C is None:
        op_verdict = "FAIL_RECALL_UNUSABLE"; B1=B2=B3=fa=move=float("nan")
    else:
        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if   fa <= GATE_FA:           op_verdict = "PASS"
        elif fa < PARTIAL_BAND:       op_verdict = "FAIL_PARTIAL_VETO"
        else:                         op_verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"

    # ---- S2 robustness sweep (fixed grid) + S3 attribution (only meaningful with a usable op-point) ----------
    s2_rows, band = s2_sweep(items_pre)
    if chosen_C is not None and base_ok:
        s3 = s3_attribution(items_pre, chosen_C, fa_base, fa)
    else:
        s3 = dict(n_total=0, n_demote_op=0, n_by_noauth=0, n_by_veto=0, n_survive=0, n_by_entailment=0,
                  reject_share=float("nan"), bar_met=False)

    # ---- E27 verdict (PRE_REGISTER_E27 sec6, the ONLY operative fork) ----------------------------------------
    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"
    elif degenerate:                verdict = "VOID_DEGENERATE_LEVER"
    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"   # veto destroys gold recall (no op-point)
    elif fa > GATE_FA:              verdict = "REGRESSION"             # E26 op-point did NOT reproduce
    elif band["robust"] and s3["bar_met"]:
        verdict = "PASS_ROBUST"
    elif not band["robust"]:
        verdict = "PASS_KNIFE_EDGE"
    else:                           # band robust but reject organ doesn't own the gain
        verdict = "PASS_MISATTRIBUTED"

    # ---- S1 per-class contradiction distribution (formalized E26 diag) ---------------------------------------
    def _summ(vals):
        if not vals: return "n=0"
        arr = np.array(vals, float)
        return (f"n={len(arr)} mean={arr.mean():.4f} p10={np.percentile(arr,10):.4f} "
                f"p50={np.percentile(arr,50):.4f} p90={np.percentile(arr,90):.4f}")
    groups = {}
    for c_, k, sc in diag: groups.setdefault((c_, k), []).append(sc)
    gc  = [sc for c_, k, sc in diag if k == "finding" and c_ == B2_CLASS]   # gold,  content (want LOW contradiction)
    spc = [sc for c_, k, sc in diag if k == "finding" and c_ == B1_CLASS]   # spoof, content (want HIGH contradiction)
    gc_p50  = float(np.percentile(gc, 50)) if gc else float("nan")
    spc_p50 = float(np.percentile(spc, 50)) if spc else float("nan")
    sep = spc_p50 - gc_p50
    s1_sep_ok = (not np.isnan(sep)) and sep > 0.5   # PRE_REGISTER sec3-S1 expectation (diagnostic, NOT a gate)
    Cn = chosen_C if chosen_C is not None else float("nan")
    gv = sum(s >= Cn for s in gc) if (gc and chosen_C is not None) else float("nan")   # gold falsely vetoed
    sv = sum(s >= Cn for s in spc) if (spc and chosen_C is not None) else float("nan")  # spoof correctly vetoed

    # ---- report --------------------------------------------------------------------------------------------
    L = [
        "# report_E27 -- contradiction-veto reject organ: full gate + robustness sweep (S1/S2/S3)",
        "",
        f"- pre-register   : PRE_REGISTER_E27.md (FROZEN md5 20dde8b3f6d54b9417ea1007a12210d4) -- sec2/3/5/6 operative",
        f"- lever          : {CE_MODEL} -- P(CONTRADICTION), premise=source.FINDING (fallback source) / hypothesis=claim",
        f"- premise content: from_finding={n_find}/{n_prem} (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)",
        f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
        f"- fixture md5    : {fm} (E25b) | heldout md5 : {hm}",
        f"- heldout classes: {cls}",
        "",
        "## trust gates (else VOID)",
        f"- baseline (C=+inf) B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (no-veto 0.467) reproduced={base_ok}",
        f"- decorrelation spearman(contradiction,cosine) rho = {rho:.3f} over {len(decorr)} pairs | VOID-guard rho>={DEGENERATE_RHO} -> degenerate={degenerate}",
        f"- advisory (PRE_REGISTER sec4): |rho| < {PREREG_RHO_ADVISORY} -> {rho_advisory_ok} (REPORTED ONLY; FROZEN substrate VOID-guard is {DEGENERATE_RHO}; see CONFLICT note)",
        f"- contradiction_idx read from id2label (single, asserted) ; from_finding={n_find} asserted > 0",
        "",
        "## op-point gate (FROZEN E26 rule: iso-recall LOWEST observed-C with B2>=0.90 ; reproduces E26 = regression check)",
        f"- chosen C = {chosen_C} | B2 at op-point = {chosen_B2}",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}  (gate <= {GATE_FA})",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        f"- op-point verdict  = {op_verdict}",
        "",
        "## S2 -- C-sweep / lift-off robustness (PRIMARY E27 question; FROZEN fixed grid)",
        f"- joint (fa<={GATE_FA} AND B2>={RECALL_FLOOR}) band: C_lo={band['c_lo']} C_hi={band['c_hi']} "
        f"width={band['width']:.4f} points={band['points']}",
        f"- B2 lift-off within band (max B2 - floor) = {band['b2_liftoff']:.4f}  (>0 == not pinned to floor)",
        f"- robustness bar: width>={S2_BAND_MIN_WIDTH} AND points>={S2_BAND_MIN_POINTS} AND liftoff>0 -> robust={band['robust']}",
        "- sweep (C, false-accept, B2, joint_ok):",
    ]
    for (C, faC, b2C, ok) in s2_rows:
        L.append(f"    C={C:.3f}  fa={faC:.4f}  B2={b2C:.4f}  joint={'Y' if ok else '.'}")
    L += [
        "",
        "## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions at op-point)",
        f"- spoofs total={s3['n_total']} | demoted@op={s3['n_demote_op']} | survived(false-accept)={s3['n_survive']}",
        f"- (a) noauth baseline (demote @ C=+inf)         = {s3['n_by_noauth']}",
        f"- (b) contradiction-veto reject organ           = {s3['n_by_veto']}  (demoted ONLY because veto fired)",
        f"- (c) accept/entailment-lift organ              = {s3['n_by_entailment']}  (NOT wired in standalone probe; verifier-integration step)",
        f"- reject_share = (fa_base - fa_op)/fa_base = ({fa_base:.4f} - {fa:.4f})/{fa_base:.4f} = {s3['reject_share']:.4f}",
        f"- S3 bar: reject_share > {S3_REJECT_SHARE_BAR} -> {s3['bar_met']}  (== veto, not coverage, owns the fa-reduction)",
        "",
        "## S1 -- per-class contradiction distribution (formalized E26 diagnostic)",
    ]
    for key in sorted(groups): L.append(f"- {key[0]:28s} premise={key[1]:7s} : {_summ(groups[key])}")
    L += [
        "",
        f"## contradiction separation (chosen_C={Cn:.5f}; veto when contradiction >= C)",
        f"- gold-content  (want LOW)  : {_summ(gc)} | vetoed(>=C, false): {gv}/{len(gc)}",
        f"- spoof-content (want HIGH) : {_summ(spc)} | vetoed(>=C, true): {sv}/{len(spc)}",
        f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
        f"- S1 expectation: separation > 0.5 -> {s1_sep_ok} (diagnostic only; verdict reads max-based fa, not sep)",
        "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
        "  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E27.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate):",
        "  PASS_ROBUST (op fa<=0.10 reproduced AND S2 band width>=0.01/>=3pts/B2 lifts off AND S3 reject_share>0.50)",
        "    -> reject organ ROBUST -> graduate into the verifier (verify_E16 integration; TOMMY GO REQUIRED, frozen",
        "       substrate is edited) + per-class secondaries.",
        "  PASS_KNIFE_EDGE (op fa<=0.10 but band knife-edge: single C / B2 pinned to floor) -> NOT robust -> tune",
        "    premise quality / per-class C, ONE more readout, NO new data.",
        "  PASS_MISATTRIBUTED (band robust but reject_share<=0.50) -> gain not owned by the reject organ -> tune.",
        "  REGRESSION (op fa>0.10 on re-run) -> E26 single readout did not reproduce -> reconcile before anything.",
        "  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.",
        "",
        "CONFLICT note (R15 / proto 3.10): PRE_REGISTER_E27 sec4 froze advisory |rho|<0.50; the REUSED frozen E26",
        "  substrate VOID-guard is rho>=0.95 (one-sided). Both pass at observed rho=-0.237 (no functional delta this",
        "  run). This file keeps the FROZEN 0.95 as the VOID trigger (does not fork frozen behavior) and reports the",
        "  0.50 advisory separately. Reconcile the bar at verifier-integration; do NOT silently edit the pre-register.",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
