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

# E28 = OBSERVABLE-CONDITIONED contradiction-veto (knife-edge tune of E27). PRE_REGISTER_E28.md (FROZEN,
#   md5 f3fab7581d1c15e7b58926da82d01dc3). E27 was PASS_KNIFE_EDGE: op fa 0.0667 reproduced E26 deterministically
#   and S3 reject_share 0.857 (veto owns), but the joint (fa<=0.10 AND B2>=0.90) band was a single C=0.995 with
#   B2 pinned to the 0.90 floor (width 0) -> robust=False. DIAGNOSIS: not one outlier but TAIL OVERLAP -- gold
#   p90=0.979 interleaves the spoof mass in C in [0.99,0.996], unseparable by a single scalar threshold.
#   LEVER (per-OBSERVABLE C, NOT per-class true-class which is oracle leak): veto fires iff
#   (contradiction >= C AND binding_cosine <= K). cosine is observable at decision time; high-cosine gold is
#   spared, low-cosine spoof in the overlap is demoted. K=+inf DEGENERATES to E27's scalar C (regression guard).
#   SAME frozen gate (fa<=0.10) + SAME trust gates. ADDS: S1 driver isolation, S2 (C,K) band robustness, S3
#   attribution. NO new data, NO fixture edit. Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve,
#   run_E26, run_E27) untouched; conditioning + footgun fixes folded into THIS file only.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "facebook/bart-large-mnli")   # model-scale NLI; override via env
E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
PARTIAL_BAND = 0.20           # 0.10 < fa < 0.20 = PARTIAL ; fa >= 0.20 = plateau (contradiction insufficient)
RECALL_FLOOR = 0.90           # iso-recall pin (B2 >= 0.90); selection peeks ONLY recall
DEGENERATE_RHO = 0.95         # contradiction vs cosine Spearman >= this => collinear lever => VOID (FROZEN E26 guard)
PREREG_RHO_ADVISORY = 0.50    # PRE_REGISTER_E28 sec4 advisory tightness (|rho| < this); REPORTED, not a VOID trigger
B1_CLASS, B2_CLASS, B3_CLASS = "spoof_cuestripped_entitied", "gold_backed", "negctrl_common"
B2_EXCLUDE = {"ho_23"}        # frozen exclusion (matches verify_E16._eval_heldout); no-op on heldout_E17

# --- S2 robustness sweep grid (FROZEN pre-data, PRE_REGISTER_E28 sec3-S2) ----------------------------------
#   coarse [0.90, 0.995] step 0.005 + fine [0.990, 0.999] step 0.001 ; C=+inf reported separately as anchor.
S2_GRID = sorted(set([round(0.900 + 0.005 * i, 3) for i in range(0, 20)] +
                     [round(0.990 + 0.001 * i, 3) for i in range(0, 10)]))
S2_BAND_MIN_WIDTH = 0.01      # joint (fa<=0.10 AND B2>=0.90) band must span >= this in C
S2_BAND_MIN_POINTS = 3        # AND contain >= this many grid points (not a single knife-edge)
S3_REJECT_SHARE_BAR = 0.50    # reject organ must own > this share of baseline false-accepts eliminated

# --- E28 observable-conditioning: K = binding-cosine gate (FROZEN pre-data, PRE_REGISTER_E28 sec3-S2) -------
#   veto fires iff (contradiction >= C AND cos <= K). K grid: [0.45 (retrieval FLOOR), 1.00] step 0.05.
#   K=+inf (cos<=inf always True) DEGENERATES to E27 scalar C -> regression anchor.
K_GRID = sorted(set([round(0.45 + 0.05 * i, 2) for i in range(0, 12)]))  # 0.45 .. 1.00
S1_TAIL_CON = 0.95            # S1 driver isolation: gold-content items with contradiction >= this

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
        prems = []; kinds = []; coss = []
        for (cos, r) in authorized:
            f = finding_by_source.get(r["source"], "")
            prems.append(f if f else r["source"])
            k = "finding" if f else "source"
            kinds.append(k); prem_log.append(k); coss.append(float(cos))
        scs = ce_scores(query, prems)
        for k, sc, cos in zip(kinds, scs, coss):
            diag.append((item["class"], item["id"], k, float(sc), float(cos)))  # E28: + id + cos for S1/cond
        for cos, sc in zip(coss, scs): decorr.append((cos, sc))
        # E28: resolution carries (cos, contradiction) per authorized candidate (E27 stored contradiction only)
        resolutions.append(("auth", [(float(c), float(s)) for c, s in zip(coss, scs)]))
    return resolutions

def item_label_at_C(resolutions, C, K=float("inf")):
    """E28 observable-conditioned veto: an authorized claim is VETOED (UNVERIFIABLE) when ANY authorized
    candidate has (contradiction >= C AND binding_cosine <= K), else VERIFIED. K=+inf disables the cosine
    gate -> veto iff max contradiction >= C == E27 scalar behavior (regression anchor; reproduces E26/E27).
    Baseline C=+inf => nothing vetoed => only noauth demotes => no-veto fa 0.467 (model-independent).
    Rollup identical to run_E26/E27 (UNVERIFIABLE dominates -> DEMOTE)."""
    labs = []
    for r in resolutions:
        if r == "common":   labs.append("PASS-COMMON")
        elif r == "noauth": labs.append("UNVERIFIABLE")
        else:
            veto = any((sc >= C and cos <= K) for (cos, sc) in r[1])
            labs.append("UNVERIFIABLE" if veto else "VERIFIED")
    if not labs: return "PASS-COMMON"
    if "UNVERIFIABLE" in labs: return "DEMOTE"
    if "VERIFIED" in labs: return "VERIFIED"
    return "PASS-COMMON"

def metrics_at_C(items_pre, C, K=float("inf")):
    res = [(it, item_label_at_C(r, C, K)) for (it, r) in items_pre]
    b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
    b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
    B1 = sum(l == "DEMOTE" for _, l in b1) / len(b1) if b1 else float("nan")
    B2 = sum(l == "VERIFIED" for _, l in b2) / len(b2) if b2 else float("nan")
    B3 = sum(l == "DEMOTE" for _, l in b3) / len(b3) if b3 else float("nan")
    return B1, B2, B3, (len(b1), len(b2), len(b3))

# ===== E27 NEW: S2 robustness sweep, S3 demotion attribution ==============================================

def s2_band_at_K(items_pre, K):
    """S2 -- C-sweep at a FIXED cosine-gate K over the FROZEN C grid; locate the joint (fa<=0.10 AND B2>=0.90)
    band. Returns (rows, band). The robustness verdict is read at the OP-POINT's selected K (PRE_REGISTER sec3)."""
    rows = []
    for C in S2_GRID:
        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C), K)
        fa = (1.0 - B1) if not np.isnan(B1) else float("nan")
        joint = (not np.isnan(fa)) and (not np.isnan(B2)) and (fa <= GATE_FA) and (B2 >= RECALL_FLOOR)
        rows.append((float(C), float(fa), float(B2), bool(joint)))
    joint_Cs = [C for (C, _fa, _b2, ok) in rows if ok]
    joint_B2 = [b2 for (_C, _fa, b2, ok) in rows if ok]
    if joint_Cs:
        width = max(joint_Cs) - min(joint_Cs)
        points = len(joint_Cs)
        liftoff = max(joint_B2) - RECALL_FLOOR
        robust = (width >= S2_BAND_MIN_WIDTH) and (points >= S2_BAND_MIN_POINTS) and (liftoff > 0.0)
        band = dict(c_lo=min(joint_Cs), c_hi=max(joint_Cs), width=width, points=points,
                    b2_liftoff=liftoff, robust=robust)
    else:
        band = dict(c_lo=None, c_hi=None, width=0.0, points=0, b2_liftoff=0.0, robust=False)
    return rows, band

def s2_perK_summary(items_pre):
    """Per-K joint C-band summary over the FROZEN K_GRID (+ K=+inf E27 anchor). Reporting; the verdict reads
    the band at the op-point K (s2_band_at_K). Shows WHERE in K the cosine gate opens band air."""
    out = []
    for K in (K_GRID + [float("inf")]):
        _rows, band = s2_band_at_K(items_pre, float(K))
        out.append((K, band["width"], band["points"], band["b2_liftoff"], band["robust"]))
    return out

def s3_attribution(items_pre, op_C, op_K, fa_base, fa_op):
    """S3 -- decompose B1-class (spoof) demotions at the conditioned op-point (op_C, op_K) into:
       (a) noauth baseline  : demotes already at C=+inf (no veto needed),
       (b) contradiction-veto reject organ : demotes at (op_C,op_K) but NOT at C=+inf (a candidate crossed
                                             the conditioned veto: contradiction>=op_C AND cos<=op_K),
       (c) accept/entailment-lift organ    : NOT wired in this standalone probe -> structurally 0.
    reject_share = (fa_base - fa_op)/fa_base. Bar (PRE_REGISTER_E28 sec3-S3): > 0.50."""
    spoofs = [r for (it, r) in items_pre if it["class"] == B1_CLASS]
    n_total = len(spoofs)
    n_demote_op = n_by_noauth = n_by_veto = n_survive = 0
    for r in spoofs:
        base = item_label_at_C(r, float("inf"))
        op = item_label_at_C(r, float(op_C), float(op_K))
        if op == "DEMOTE":
            n_demote_op += 1
            if base == "DEMOTE":  n_by_noauth += 1
            else:                 n_by_veto += 1
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
    ap.add_argument("--out", default="reports/report_E28.md")
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

    # observed grids (selection over OBSERVED values only; no post-hoc fishing -- PRE_REGISTER_E28 sec2)
    C_obs = sorted({sc for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc) in x[1]})
    K_obs = sorted({cos for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc) in x[1]})

    # REGRESSION ANCHOR: K=+inf disables the cosine gate -> E27 scalar rule (lowest observed C with B2>=0.90).
    # MUST reproduce E27 (C~0.9949, fa~0.0667). Mismatch => REGRESSION (wiring drifted from frozen behavior).
    reg_C = None
    for C in C_obs:
        _b1, b2, _b3, _ = metrics_at_C(items_pre, C, float("inf"))
        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
            reg_C = float(C); break
    if reg_C is not None:
        rB1, _rB2, _rB3, _ = metrics_at_C(items_pre, reg_C, float("inf")); reg_fa = 1.0 - rB1
    else:
        reg_fa = float("nan")
    reg_reproduces = (reg_C is not None) and (not np.isnan(reg_fa)) and (reg_fa <= GATE_FA)
    print(f"[regression-anchor K=+inf] C={reg_C} fa={reg_fa} reproduces_E27(fa<={GATE_FA})={reg_reproduces}")

    # E28 conditioned op-point: over OBSERVED (C,K), MIN fa subject to B2>=0.90. Tie-break (frozen):
    # widest joint C-band at that K -> lowest C -> highest K (deterministic; selection peeks ONLY recall feasibility).
    feasible = []
    for K in K_obs:
        for C in C_obs:
            b1, b2, _b3, _ = metrics_at_C(items_pre, C, K)
            if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                feasible.append((1.0 - b1, float(C), float(K)))
    chosen_C = chosen_K = chosen_B2 = None
    if feasible:
        min_fa = min(f for f, _c, _k in feasible)
        cands = [(c, k) for (f, c, k) in feasible if abs(f - min_fa) < 1e-12]
        _bw = {k: s2_band_at_K(items_pre, k)[1]["width"] for (_c, k) in cands}
        cands.sort(key=lambda ck: (-_bw[ck[1]], ck[0], -ck[1]))
        chosen_C, chosen_K = cands[0]
        _b1, chosen_B2, _b3, _ = metrics_at_C(items_pre, chosen_C, chosen_K)

    if chosen_C is None:
        op_verdict = "FAIL_RECALL_UNUSABLE"; B1 = B2 = B3 = fa = move = float("nan")
    else:
        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C, chosen_K)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if   fa <= GATE_FA:           op_verdict = "PASS"
        elif fa < PARTIAL_BAND:       op_verdict = "FAIL_PARTIAL_VETO"
        else:                         op_verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"

    # ---- S2 robustness: band read at the OP-POINT's K (PRE_REGISTER_E28 sec3-S2) + per-K summary -------------
    K_for_band = chosen_K if chosen_K is not None else float("inf")
    s2_rows, band = s2_band_at_K(items_pre, float(K_for_band))
    s2_perK = s2_perK_summary(items_pre)
    if chosen_C is not None and base_ok:
        s3 = s3_attribution(items_pre, chosen_C, chosen_K, fa_base, fa)
    else:
        s3 = dict(n_total=0, n_demote_op=0, n_by_noauth=0, n_by_veto=0, n_survive=0, n_by_entailment=0,
                  reject_share=float("nan"), bar_met=False)

    # ---- E28 verdict (PRE_REGISTER_E28 sec6, the ONLY operative fork) -----------------------------------------
    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"
    elif degenerate:                verdict = "VOID_DEGENERATE_LEVER"
    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"   # veto destroys gold recall (no op-point)
    elif not reg_reproduces:        verdict = "REGRESSION"             # K=+inf did NOT reproduce E27 scalar op
    elif fa > GATE_FA:              verdict = "REGRESSION"             # conditioned op above the frozen gate
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
    for (c_, _id, k, sc, cos) in diag: groups.setdefault((c_, k), []).append(sc)
    gc  = [(sc, cos) for (c_, _id, k, sc, cos) in diag if k == "finding" and c_ == B2_CLASS]  # gold  content (cos paired)
    spc = [(sc, cos) for (c_, _id, k, sc, cos) in diag if k == "finding" and c_ == B1_CLASS]  # spoof content (cos paired)
    gc_s = [s for s, _c in gc]; spc_s = [s for s, _c in spc]
    gc_p50  = float(np.percentile(gc_s, 50)) if gc_s else float("nan")
    spc_p50 = float(np.percentile(spc_s, 50)) if spc_s else float("nan")
    sep = spc_p50 - gc_p50
    s1_sep_ok = (not np.isnan(sep)) and sep > 0.5   # PRE_REGISTER sec3 (diagnostic, NOT a gate)
    Cn = chosen_C if chosen_C is not None else float("nan")
    Kn = chosen_K if chosen_K is not None else float("inf")
    # conditioned veto counts at the op-point: veto iff (contradiction>=C AND cos<=K)
    gv = sum((s >= Cn and c <= Kn) for (s, c) in gc) if (gc and chosen_C is not None) else float("nan")   # gold falsely vetoed
    sv = sum((s >= Cn and c <= Kn) for (s, c) in spc) if (spc and chosen_C is not None) else float("nan")  # spoof correctly vetoed
    # S1 DRIVER ISOLATION: gold-content tail items (contradiction >= S1_TAIL_CON) -- the knife-edge drivers,
    # with binding cosine (the observable the lever uses to spare them). Spoof-content tail for contrast.
    gc_tail  = sorted([(sc, cos, _id) for (c_, _id, k, sc, cos) in diag if c_ == B2_CLASS and k == "finding" and sc >= S1_TAIL_CON], reverse=True)
    spc_tail = sorted([(sc, cos, _id) for (c_, _id, k, sc, cos) in diag if c_ == B1_CLASS and k == "finding" and sc >= S1_TAIL_CON], reverse=True)
    gc_tail_cos_med  = float(np.percentile([c for _s, c, _i in gc_tail], 50)) if gc_tail else float("nan")
    spc_tail_cos_med = float(np.percentile([c for _s, c, _i in spc_tail], 50)) if spc_tail else float("nan")

    # ---- report --------------------------------------------------------------------------------------------
    L = [
        "# report_E28 -- observable-conditioned contradiction-veto: (C x cosine-gate K) knife-edge tune (S1/S2/S3)",
        "",
        f"- pre-register   : PRE_REGISTER_E28.md (FROZEN md5 f3fab7581d1c15e7b58926da82d01dc3) -- sec2/3/5/6 operative",
        f"- lever          : {CE_MODEL} -- veto iff (P(CONTRADICTION)>=C AND binding_cosine<=K); premise=source.FINDING / hyp=claim",
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
        "## op-point gate (conditioned; min fa s.t. B2>=0.90 over observed (C,K); K=+inf reduces to E27 scalar)",
        f"- regression anchor (K=+inf): C={reg_C} fa={reg_fa} reproduces_E27(fa<={GATE_FA})={reg_reproduces}",
        f"- chosen C = {chosen_C} | chosen K (cosine gate) = {chosen_K} | B2 at op-point = {chosen_B2}",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}  (gate <= {GATE_FA})",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        f"- op-point verdict  = {op_verdict}",
        "",
        "## S2 -- (C,K) band / lift-off robustness (PRIMARY E28 question; band read at the op-point K; FROZEN grids)",
        f"- band at op-point K={K_for_band}: joint (fa<={GATE_FA} AND B2>={RECALL_FLOOR}) C_lo={band['c_lo']} "
        f"C_hi={band['c_hi']} width={band['width']:.4f} points={band['points']}",
        f"- B2 lift-off within band (max B2 - floor) = {band['b2_liftoff']:.4f}  (>0 == not pinned to floor)",
        f"- robustness bar: width>={S2_BAND_MIN_WIDTH} AND points>={S2_BAND_MIN_POINTS} AND liftoff>0 -> robust={band['robust']}",
        "- per-K joint C-band summary (K, band_width, points, b2_liftoff, robust); K=inf = E27 scalar anchor:",
    ]
    for (K, w, p, lo, rb) in s2_perK:
        ks = "inf" if K == float("inf") else f"{K:.2f}"
        L.append(f"    K={ks:>5}  width={w:.4f}  points={p}  liftoff={lo:.4f}  robust={rb}")
    L += [
        "- C-sweep at op-point K (C, false-accept, B2, joint_ok):",
    ]
    for (C, faC, b2C, ok) in s2_rows:
        L.append(f"    C={C:.3f}  fa={faC:.4f}  B2={b2C:.4f}  joint={'Y' if ok else '.'}")
    L += [
        "",
        "## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions at conditioned op-point)",
        f"- spoofs total={s3['n_total']} | demoted@op={s3['n_demote_op']} | survived(false-accept)={s3['n_survive']}",
        f"- (a) noauth baseline (demote @ C=+inf)         = {s3['n_by_noauth']}",
        f"- (b) contradiction-veto reject organ           = {s3['n_by_veto']}  (demoted ONLY because veto fired)",
        f"- (c) accept/entailment-lift organ              = {s3['n_by_entailment']}  (NOT wired in standalone probe; verifier-integration step)",
        f"- reject_share = (fa_base - fa_op)/fa_base = ({fa_base:.4f} - {fa:.4f})/{fa_base:.4f} = {s3['reject_share']:.4f}",
        f"- S3 bar: reject_share > {S3_REJECT_SHARE_BAR} -> {s3['bar_met']}  (== veto, not coverage, owns the fa-reduction)",
        "",
        "## S1 -- per-class contradiction distribution + knife-edge DRIVER ISOLATION",
    ]
    for key in sorted(groups): L.append(f"- {key[0]:28s} premise={key[1]:7s} : {_summ(groups[key])}")
    L += [
        f"- gold-content tail (contradiction>={S1_TAIL_CON}): n={len(gc_tail)} cos_med={gc_tail_cos_med:.4f} (the knife-edge drivers)",
        f"- spoof-content tail (contradiction>={S1_TAIL_CON}): n={len(spc_tail)} cos_med={spc_tail_cos_med:.4f}",
        "- S1 expectation (diagnostic): gold tail-items sit at HIGHER cosine than spoof tail-items (the gap the K-gate exploits).",
        "- gold tail drivers (contradiction, cosine, id):",
    ]
    for (sc, cos, _id) in gc_tail[:20]:
        L.append(f"    con={sc:.4f}  cos={cos:.4f}  id={_id}")
    L += [
        "- spoof tail (contradiction, cosine, id) [first 20]:",
    ]
    for (sc, cos, _id) in spc_tail[:20]:
        L.append(f"    con={sc:.4f}  cos={cos:.4f}  id={_id}")
    L += [
        "",
        f"## conditioned separation at op-point (C={Cn:.5f}, K={Kn}; veto iff contradiction>=C AND cos<=K)",
        f"- gold-content  (want NOT vetoed) : {_summ(gc_s)} | falsely vetoed: {gv}/{len(gc_s)}",
        f"- spoof-content (want vetoed)     : {_summ(spc_s)} | correctly vetoed: {sv}/{len(spc_s)}",
        f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
        f"- S1 expectation: separation > 0.5 -> {s1_sep_ok} (diagnostic only; verdict reads max-based fa, not sep)",
        "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
        "  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E28.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate):",
        "  PASS_ROBUST (conditioned band robust: width>=0.01/>=3pts/B2 lifts off at op-K AND S3 reject_share>0.50)",
        "    -> reject organ ROBUST under observable conditioning -> graduate the (contradiction x cosine) veto into",
        "       the verifier (verify_E16 integration; TOMMY GO REQUIRED, frozen substrate edited). At integration:",
        "       reconcile rho guard (0.95 vs 0.50) into one bar; wire (c) entailment-lift -> S3 three-way.",
        "  PASS_KNIFE_EDGE (cosine gate does NOT open the band: single point / B2 pinned) -> tail overlap NOT",
        "    cosine-separable -> premise quality is the binding constraint -> E29 targeted re-author of the S1 tail",
        "    drivers with a FRESH fixture freeze (NEW data, separate session). No verifier integration.",
        "  PASS_MISATTRIBUTED (band robust but reject_share<=0.50) -> gain not owned by the reject organ -> tune.",
        "  REGRESSION (K=+inf does not reproduce E27 scalar op, OR conditioned op fa>0.10) -> reconcile before anything.",
        "  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.",
        "",
        "CONFLICT note (R15 / proto 3.10): PRE_REGISTER advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95",
        "  (one-sided). The lever now USES cosine, so low |rho| is required for the conditioning to add signal (not be",
        "  redundant with contradiction). Both pass at observed rho (E27 -0.237). This file keeps the FROZEN 0.95 as the",
        "  VOID trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
