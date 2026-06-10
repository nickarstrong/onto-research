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

# E32 = MODEL-CLASS ESCALATION: NLI cross-encoder SWAP is the lever. PRE_REGISTER_E32.md (FROZEN,
#   md5 e25b801f3b6eb8ced194f47d4c488c66). E31 (report_E30.md, VERDICT FAIL_NOT_THE_DRIVER) proved candidate-SCOPE
#   is NOT the lever: top1 LOSES the spoof rejections living in non-top1 candidates (fa monotone 0.0667->0.2333);
#   bart-large-mnli is therefore the PROVEN ceiling. The only remaining in-family lever is NLI discriminative CLASS.
#   LEVER (E32): swap the cross-encoder bart-large-mnli -> a stronger ANLI-hardened head (default below), holding
#   the veto geometry FIXED at scope='any' (E30 proven-best). A candidate vetoes iff (contradiction >= C AND
#   cosine <= K); K carried from E28 (K=+inf disables the gate). The MODEL is the ONLY new variable; nothing held-out
#   conditions on it -> oracle-clean. SAME gate (fa<=0.10) + SAME grids + SAME trust gates + SAME substrate as run_E30.
#   ANCHOR REPURPOSE: under a NEW model fa is NOT expected to reproduce bart's 0.0667 -- 0.0667 is the bart-specific
#   COMPARISON BAR fa_new is read against (sec5 forks), NOT a regression gate. No REGRESSION verdict at E32.
#   Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26/E27/E28, scope logic) untouched.
#   ESCALATION is discriminative CLASS not param count: deberta-v3-large (~304M) < bart-large-mnli (~407M); the lift
#   is DeBERTa-v3 (RTD + disentangled attn) + ANLI/WANLI adversarial training. ANLI-hardened head not clearing 0.0667
#   => CEILING_NOT_MODEL_SCALE (task, not model, is the constraint) -- this SHARPENS falsifiability.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")   # ANLI-hardened NLI; override via env
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

# --- E32 veto geometry (FROZEN pre-data, PRE_REGISTER_E32.md sec3) -----------------------------------------
#   scope='any' (PRIMARY at E32) = E30 proven-best veto geometry (E31: top1 LOST non-top1 spoof rejections).
#   The model is the lever; the geometry is held fixed. scope=('margin',delta) robustness arm = reported only.
PRIMARY_SCOPE = "any"
ANCHOR_SCOPE  = "any"        # == PRIMARY_SCOPE at E32; anchor-compare prints fa_new vs the bart bar
MARGIN_GRID = [0.00, 0.02, 0.05, 0.10, 0.20]   # delta grid for the reported robustness arm
E28_OP_FA   = 0.0667         # bart-SPECIFIC COMPARISON BAR (sec5 forks); NOT a reproduce-assert at E32
ANCHOR_TOL  = 1e-3           # carried (unused as a gate at E32; kept for byte-stability of the constants block)

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

def item_label_at_C(resolutions, C, K=float("inf"), scope=PRIMARY_SCOPE):
    """E30 binding-discipline veto. `scope` selects WHICH authorized candidate(s) may veto:
       'top1'            : only r[1][0] (highest-cosine authorized candidate = bound support) -- E30 PRIMARY.
       'any'             : any candidate (== run_E28 line 153 verbatim) -- REGRESSION ANCHOR only.
       ('margin', delta) : any candidate with cos >= cos0 - delta (bound-neighborhood) -- robustness arm.
    A candidate vetoes iff (contradiction >= C AND binding_cosine <= K). K=+inf disables the cosine gate.
    Baseline C=+inf => nothing crosses under ANY scope => only noauth demotes => no-veto fa 0.467
    (scope-independent, model-independent). Rollup identical to run_E26/E27/E28 (UNVERIFIABLE dominates -> DEMOTE).
    r[1] is ordered top-1-cosine-first (asserted in main); r[1][0] is the bound support."""
    labs = []
    for r in resolutions:
        if r == "common":   labs.append("PASS-COMMON")
        elif r == "noauth": labs.append("UNVERIFIABLE")
        else:
            cands = r[1]                                   # [(cos, contradiction), ...] top-1 cosine first
            if scope == "top1":
                cos0, sc0 = cands[0]
                veto = (sc0 >= C and cos0 <= K)
            elif scope == "any":
                veto = any((sc >= C and cos <= K) for (cos, sc) in cands)
            elif isinstance(scope, tuple) and scope[0] == "margin":
                delta = float(scope[1]); cos0 = cands[0][0]
                veto = any((sc >= C and cos <= K and cos >= cos0 - delta) for (cos, sc) in cands)
            else:
                raise ValueError(f"unknown scope {scope!r}")
            labs.append("UNVERIFIABLE" if veto else "VERIFIED")
    if not labs: return "PASS-COMMON"
    if "UNVERIFIABLE" in labs: return "DEMOTE"
    if "VERIFIED" in labs: return "VERIFIED"
    return "PASS-COMMON"

def metrics_at_C(items_pre, C, K=float("inf"), scope=PRIMARY_SCOPE):
    res = [(it, item_label_at_C(r, C, K, scope)) for (it, r) in items_pre]
    b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
    b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
    B1 = sum(l == "DEMOTE" for _, l in b1) / len(b1) if b1 else float("nan")
    B2 = sum(l == "VERIFIED" for _, l in b2) / len(b2) if b2 else float("nan")
    B3 = sum(l == "DEMOTE" for _, l in b3) / len(b3) if b3 else float("nan")
    return B1, B2, B3, (len(b1), len(b2), len(b3))

# ===== E27 NEW: S2 robustness sweep, S3 demotion attribution ==============================================

def s2_band_at_K(items_pre, K, scope=PRIMARY_SCOPE):
    """S2 -- C-sweep at a FIXED cosine-gate K over the FROZEN C grid; locate the joint (fa<=0.10 AND B2>=0.90)
    band. Returns (rows, band). The robustness verdict is read at the OP-POINT's selected K (PRE_REGISTER sec4)."""
    rows = []
    for C in S2_GRID:
        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C), K, scope)
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

def s2_perK_summary(items_pre, scope=PRIMARY_SCOPE):
    """Per-K joint C-band summary over the FROZEN K_GRID (+ K=+inf E27 anchor). Reporting; the verdict reads
    the band at the op-point K (s2_band_at_K). Shows WHERE in K the cosine gate opens band air."""
    out = []
    for K in (K_GRID + [float("inf")]):
        _rows, band = s2_band_at_K(items_pre, float(K), scope)
        out.append((K, band["width"], band["points"], band["b2_liftoff"], band["robust"]))
    return out

def s3_attribution(items_pre, op_C, op_K, fa_base, fa_op, scope=PRIMARY_SCOPE):
    """S3 -- decompose B1-class (spoof) demotions at the op-point (op_C, op_K, scope) into:
       (a) noauth baseline  : demotes already at C=+inf (no veto needed; scope-independent),
       (b) contradiction-veto reject organ : demotes at (op_C,op_K,scope) but NOT at C=+inf (a candidate in
                                             scope crossed the veto: contradiction>=op_C AND cos<=op_K),
       (c) accept/entailment-lift organ    : NOT wired in this standalone probe -> structurally 0.
    reject_share = (fa_base - fa_op)/fa_base. Bar (PRE_REGISTER_E30 sec4-S3): > 0.50."""
    spoofs = [r for (it, r) in items_pre if it["class"] == B1_CLASS]
    n_total = len(spoofs)
    n_demote_op = n_by_noauth = n_by_veto = n_survive = 0
    for r in spoofs:
        base = item_label_at_C(r, float("inf"), float("inf"), scope)
        op = item_label_at_C(r, float(op_C), float(op_K), scope)
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
    ap.add_argument("--out", default="reports/report_E32.md")   # NEVER a frozen-report path (no clobber E30/E28/E27)
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

    # E30 ORDERING GUARD: r[1] MUST be top-1-cosine-first (r[1][0] = bound support). The TOP1 scope is invalid
    # otherwise. candidates_with_cosine returns argsort(-sims) + floor-break; authorized filter preserves order.
    for (_it, rr) in items_pre:
        for x in rr:
            if isinstance(x, tuple) and x[0] == "auth":
                cs = [c for (c, _s) in x[1]]
                assert all(cs[i] >= cs[i + 1] - 1e-9 for i in range(len(cs) - 1)), \
                    "r[1] not top-1-cosine-first -> TOP1 scope invalid -> STOP"

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

    # ---- op-point selector (FROZEN selection, byte-identical to E28; only `scope` added) ---------------------
    # over OBSERVED (C,K): MIN false-accept subject to B2>=0.90. Tie-break (frozen): widest joint C-band at that
    # K -> lowest C -> highest K. selection peeks ONLY recall feasibility (no post-hoc fishing on fa).
    def select_op(scope):
        feasible = []
        for K in K_obs:
            for C in C_obs:
                b1, b2, _b3, _ = metrics_at_C(items_pre, C, K, scope)
                if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                    feasible.append((1.0 - b1, float(C), float(K)))
        if not feasible:
            return None, None, None, float("nan")
        min_fa = min(f for f, _c, _k in feasible)
        cand = [(c, k) for (f, c, k) in feasible if abs(f - min_fa) < 1e-12]
        _bw = {k: s2_band_at_K(items_pre, k, scope)[1]["width"] for (_c, k) in cand}
        cand.sort(key=lambda ck: (-_bw[ck[1]], ck[0], -ck[1]))
        c_, k_ = cand[0]
        _b1, b2_, _b3, _ = metrics_at_C(items_pre, c_, k_, scope)
        return float(c_), float(k_), float(b2_), float(min_fa)

    # E32 ANCHOR-COMPARE (repurposed): scope='any' IS the primary veto geometry here (E30 proven-best). Under a
    # NEW model fa is NOT expected to reproduce 0.0667 -- the 0.0667 anchor is the bart-specific COMPARISON BAR
    # that fa_new is read against (sec5 forks), NOT a regression gate. No REGRESSION verdict at E32.
    anc_C, anc_K, anc_B2, anc_fa = select_op(ANCHOR_SCOPE)   # ANCHOR_SCOPE == PRIMARY_SCOPE == 'any' at E32
    anchor_below_bar = (anc_C is not None) and (not np.isnan(anc_fa)) and (anc_fa < E28_OP_FA)
    print(f"[anchor-compare scope=any] C={anc_C} K={anc_K} fa_new={anc_fa} "
          f"vs bar E28_OP_FA={E28_OP_FA} -> below_bar={anchor_below_bar}")

    # E30 PRIMARY op-point: scope='top1' (veto considers ONLY the bound support r[1][0]).
    chosen_C, chosen_K, chosen_B2, _min_fa = select_op(PRIMARY_SCOPE)
    if chosen_C is None:
        op_verdict = "FAIL_RECALL_UNUSABLE"; B1 = B2 = B3 = fa = move = float("nan")
    else:
        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C, chosen_K, PRIMARY_SCOPE)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if   fa <= GATE_FA:           op_verdict = "PASS"
        elif fa < PARTIAL_BAND:       op_verdict = "FAIL_PARTIAL_VETO"
        else:                         op_verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"

    # ---- S2 robustness: band read at the TOP1 OP-POINT's K + per-K summary (scope=top1) ---------------------
    K_for_band = chosen_K if chosen_K is not None else float("inf")
    s2_rows, band = s2_band_at_K(items_pre, float(K_for_band), PRIMARY_SCOPE)
    s2_perK = s2_perK_summary(items_pre, PRIMARY_SCOPE)
    if chosen_C is not None and base_ok:
        s3 = s3_attribution(items_pre, chosen_C, chosen_K, fa_base, fa, PRIMARY_SCOPE)
    else:
        s3 = dict(n_total=0, n_demote_op=0, n_by_noauth=0, n_by_veto=0, n_survive=0, n_by_entailment=0,
                  reject_share=float("nan"), bar_met=False)

    # ---- MARGIN robustness arm (REPORTED ONLY; NOT the verdict) -- op-point per delta over the FROZEN grid ---
    margin_rows = []
    for delta in MARGIN_GRID:
        mC, mK, mB2, mfa = select_op(("margin", float(delta)))
        if mC is None:
            margin_rows.append((delta, None, None, float("nan"), float("nan"), False, float("nan")))
        else:
            _r, mband = s2_band_at_K(items_pre, float(mK), ("margin", float(delta)))
            ms3 = s3_attribution(items_pre, mC, mK, fa_base, mfa, ("margin", float(delta))) if base_ok else \
                  dict(reject_share=float("nan"))
            margin_rows.append((delta, mC, mK, mfa, mB2, mband["robust"], ms3["reject_share"]))

    # ---- E32 verdict (PRE_REGISTER_E32.md sec5; reads scope=any fa_new vs bar 0.0667 + B2>=0.90) -------------
    # baseline-sanity + degenerate = model-INDEPENDENT VOID guards. chosen_C None = no (C,K) holds B2>=0.90 ->
    # fa unreadable -> VOID (not a clean CEILING). The 3 escalation forks read fa (primary scope=any under the NEW
    # model); B2>=0.90 is GUARANTEED by select_op feasibility (RECALL_FLOOR). S3 reject_share + band robustness are
    # DIAGNOSTIC here (deferred to the E33 robustness sweep), NOT verdict gates. 0.0667 = bart COMPARISON bar.
    s3rej = s3["reject_share"]
    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"    # noauth path broke (model-independent)
    elif degenerate:                verdict = "VOID_DEGENERATE_LEVER"     # contradiction~cosine collinear (rho>=0.95)
    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"      # no op-point holds B2>=0.90 -> fa unreadable
    elif fa < E28_OP_FA:            verdict = "ESCALATION_CONFIRMED"      # fa_new < 0.0667 strict (B2>=0.90 by select_op)
    elif fa <= GATE_FA:             verdict = "MODEL_HELPS_PARTIAL"       # 0.0667 <= fa_new <= 0.10 (B2>=0.90)
    else:                           verdict = "CEILING_NOT_MODEL_SCALE"   # fa_new > 0.10 -> task/data ceiling, exit family

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
        "# report_E32 -- model-class escalation: NLI cross-encoder SWAP (scope=any fixed) vs bart 0.0667 bar (S1/S2/S3)",
        "",
        f"- pre-register   : PRE_REGISTER_E32.md (FROZEN md5 e25b801f3b6eb8ced194f47d4c488c66) -- sec1/2/3/5 operative",
        f"- lever          : MODEL SWAP -> {CE_MODEL} -- veto SCOPE=any (E30 proven-best) iff (P(CON)>=C AND cos<=K); premise=source.FINDING / hyp=claim",
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
        "## op-point gate (scope=any; min fa_new s.t. B2>=0.90 over observed (C,K)). 0.0667 = bart COMPARISON bar (not regression)",
        f"- anchor-compare (scope=any): C={anc_C} K={anc_K} fa_new={anc_fa} vs bar E28_OP_FA={E28_OP_FA} -> below_bar={anchor_below_bar}",
        f"- chosen C = {chosen_C} | chosen K (cosine gate) = {chosen_K} | B2 at op-point = {chosen_B2}",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}  (gate <= {GATE_FA})",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        f"- op-point verdict  = {op_verdict}",
        "",
        "## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=top1). delta=+inf == any (anchor); delta=0 ~ top1",
    ]
    for (delta, mC, mK, mfa, mB2, mrob, mrej) in margin_rows:
        L.append(f"    delta={delta:.2f}  C={mC}  K={mK}  fa={mfa}  B2={mB2}  band_robust={mrob}  reject_share={mrej}")
    L += [
        "",
        "## S2 -- (C,K) band / lift-off robustness (PRIMARY E30 question at scope=top1; band read at op-point K; FROZEN grids)",
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
        f"## candidate-level separation at op-point (C={Cn:.5f}, K={Kn}; counts ALL finding candidates crossing -- DIAGNOSTIC, not the top1 item-veto)",
        f"- gold-content candidates  : {_summ(gc_s)} | cross (con>=C AND cos<=K): {gv}/{len(gc_s)}",
        f"- spoof-content candidates : {_summ(spc_s)} | cross (con>=C AND cos<=K): {sv}/{len(spc_s)}",
        f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
        f"- S1 expectation: separation > 0.5 -> {s1_sep_ok} (diagnostic only; verdict reads max-based fa, not sep)",
        "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
        "  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E32.md sec5, the operative forks -- read scope=any fa_new vs bart bar 0.0667):",
        "  ESCALATION_CONFIRMED (fa_new < 0.0667 strict AND B2>=0.90) -> model discriminative scale WAS the ceiling ->",
        "    E33 graduates to a robustness sweep + the verifier-integration question (rho guard 0.95-vs-0.50 reconcile,",
        "    entailment-lift -> S3 three-way, full-GOLD scale). TOMMY GO REQUIRED before integration.",
        "  MODEL_HELPS_PARTIAL (0.0667 <= fa_new <= 0.10 AND B2>=0.90) -> bigger model helps but does NOT clear E28 ->",
        "    decide deeper model class vs task reformulation at the E33 readout.",
        "  CEILING_NOT_MODEL_SCALE (fa_new > 0.10) -> the ceiling is task/data, not model scale -> the contradiction-veto",
        "    task itself is the constraint -> EXIT the NLI-swap family and reframe the reject task.",
        "  VOID_* -> trust gate failed (baseline mismatch / degenerate lever / recall unusable=fa unreadable) -> reconcile, re-run.",
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
