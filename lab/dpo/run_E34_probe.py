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

# E34 = REFRAME the reject TASK (NLI-swap family EXITED at E33). PRE_REGISTER_E34.md (FROZEN; record its md5 in
#   the readout). E33 (report_E32.md, VERDICT CEILING_NOT_MODEL_SCALE) proved the NLI MODEL CLASS is NOT the ceiling:
#   the ANLI-hardened deberta head scored fa 0.1667 -- WORSE than bart 0.0667 -- on the same fixture. The constraint
#   is the reject TASK, not the scorer. E29 located the defect: the gold contradiction tail is RETRIEVAL MISBINDING
#   under an ANY-CANDIDATE veto (each premise faithful to its OWN source, contradicting a claim about a DIFFERENT
#   co-surfaced source -> the wrong-source candidate falsely demotes a gold claim). E31 proved rank-top1 is NOT the
#   binding signal (top1 LOSES non-top1 spoof rejections, fa 0.0667->0.2333).
#   LEVER (E34): gate the veto to candidates BOUND to the claim's subject by an OBSERVABLE binding signal that is NOT
#   retrieval rank. A candidate vetoes iff (contradiction >= C AND B >= B_floor), where B = lexical subject-overlap
#   (claim vs candidate premise) in [0,1]; B_floor=0 admits all candidates (gate off). scope stays 'any' over the
#   BOUND subset. The MODEL is UNCHANGED (inherited deberta below); the binding gate is the ONLY new variable, and B
#   conditions only on observable text (no held-out class label) -> oracle-clean.
#   ANCHOR REPURPOSE: bart 0.0667 = CROSS-MODEL comparison bar (NOT the running model). deberta scope=any 0.1667 =
#   the bar E34 must BEAT and the DEGENERACY anchor: at B_floor=0 the gate is off -> probe MUST reproduce 0.1667
#   (clean-superset check; else VOID_DEGENERACY). No REGRESSION verdict at E34 except that single anchor.
#   Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26/E27/E28, rho guard, S1 cosine diag,
#   ordering guard) untouched. cosine RETAINED for the rho VOID-guard + S1 diagnostics; B is a NEW parallel quantity.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")   # INHERITED from run_E32, UNCHANGED; override via env
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

# --- E34 observable-conditioning: B_floor = binding gate (FROZEN pre-data, PRE_REGISTER_E34.md sec1-2) -------
#   veto fires iff (contradiction >= C AND B >= B_floor), B = lexical subject-overlap(claim, premise) in [0,1].
#   B_floor grid: [0.0, 1.0] step 0.05. B_floor=0 (B>=0 always True) DEGENERATES to deberta scope=any -> the
#   0.1667 degeneracy anchor (clean-superset check; sec2). The swept-axis variable replaces E28's cosine-K.
B_FLOOR_GRID = sorted(set([round(0.0 + 0.05 * i, 2) for i in range(0, 21)]))  # 0.00 .. 1.00
S1_TAIL_CON = 0.95            # S1 driver isolation: gold-content items with contradiction >= this

# --- E34 veto geometry (FROZEN pre-data, PRE_REGISTER_E34.md sec1-2) ----------------------------------------
#   scope='any' over the BOUND subset (B>=B_floor). The MODEL is held fixed (deberta); the binding gate is the lever.
PRIMARY_SCOPE = "any"
ANCHOR_SCOPE  = "any"        # == PRIMARY_SCOPE; anchor-compare prints fa_op vs the bars
MARGIN_GRID = [0.00, 0.02, 0.05, 0.10, 0.20]   # delta grid for the reported robustness arm (bound-neighborhood)
E28_OP_FA   = 0.0667         # bart CROSS-MODEL comparison bar (sec6 forks); NOT the running model, NOT reproduced
DEBERTA_ANCHOR_FA = 0.1667   # deberta scope=any (E33) = bar to BEAT + DEGENERACY anchor at B_floor=0 (sec2)
ANCHOR_TOL  = 0.02           # tolerance for the B_floor=0 degeneracy reproduce-assert vs DEBERTA_ANCHOR_FA

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

# E34 Z1: OBSERVABLE binding signal B(claim, premise) in [0,1] -- lexical subject-overlap (containment).
#   B = |content_tokens(claim) INTERSECT content_tokens(premise)| / |content_tokens(claim)|.
#   Observable text ONLY (claim string + candidate premise) -> oracle-clean (no class label, no per-class term).
#   Topical (shared subject/entities), ORTHOGONAL to NLI contradiction (logical): a wrong-source candidate can
#   score high contradiction yet low B. cosine is UNTOUCHED (rho guard / S1 diag); B is a NEW parallel quantity.
_STOP = frozenset((
    "the a an of to in on at for and or but if then with without by from as is are was were be been being this "
    "that these those it its their his her our your my we you they he she i not no nor so than too very can may "
    "might will would should could has have had do does did about into over under between within across per such "
    "which who whom whose what when where why how also more most some any all each both other same own".split()))
def _content_tokens(text):
    toks = []
    cur = []
    for ch in str(text).lower():
        if ch.isalnum():
            cur.append(ch)
        elif cur:
            toks.append("".join(cur)); cur = []
    if cur: toks.append("".join(cur))
    return {t for t in toks if len(t) > 2 and t not in _STOP}
def binding_score(claim, premise):
    cset = _content_tokens(claim)
    if not cset: return 0.0
    pset = _content_tokens(premise)
    return float(len(cset & pset)) / float(len(cset))

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
        bnds = [binding_score(query, p) for p in prems]    # E34 Z1: observable binding per candidate (oracle-clean)
        for k, sc, cos in zip(kinds, scs, coss):
            diag.append((item["class"], item["id"], k, float(sc), float(cos)))  # E28: + id + cos for S1/cond (cos UNTOUCHED)
        for cos, sc in zip(coss, scs): decorr.append((cos, sc))   # rho guard on (cos, contradiction) UNCHANGED
        # E34: resolution carries (cos, contradiction, B) per authorized candidate (cos kept for diag; B = the gate)
        resolutions.append(("auth", [(float(c), float(s), float(b)) for c, s, b in zip(coss, scs, bnds)]))
    return resolutions

def item_label_at_C(resolutions, C, B_floor=0.0, scope=PRIMARY_SCOPE):
    """E34 binding-gate veto. A candidate vetoes iff (contradiction >= C AND B >= B_floor); scope='any' fires if
    ANY candidate in the BOUND subset (B>=B_floor) crosses. B_floor=0 admits all candidates (gate off) ->
    degenerates to plain scope=any (the deberta 0.1667 anchor). `scope` selects WHICH candidate(s) may veto:
       'any'             : any bound candidate (E34 PRIMARY).
       'top1'            : only r[1][0] (highest-cosine bound support) -- reported arm (E31 falsified as the lever).
       ('margin', delta) : bound candidates within cosine cos0-delta of the support -- reported arm.
    Baseline C=+inf => nothing crosses under ANY scope/B_floor => only noauth demotes => no-veto fa 0.467
    (scope/B_floor-independent, model-independent). Rollup identical to run_E26/E27/E28 (UNVERIFIABLE -> DEMOTE).
    r[1] is ordered top-1-cosine-first (asserted in main); r[1][0] is the bound support. Tuples = (cos, contradiction, B)."""
    labs = []
    for r in resolutions:
        if r == "common":   labs.append("PASS-COMMON")
        elif r == "noauth": labs.append("UNVERIFIABLE")
        else:
            cands = r[1]                                   # [(cos, contradiction, B), ...] top-1 cosine first
            if scope == "top1":
                cos0, sc0, b0 = cands[0]
                veto = (sc0 >= C and b0 >= B_floor)
            elif scope == "any":
                veto = any((sc >= C and b >= B_floor) for (cos, sc, b) in cands)
            elif isinstance(scope, tuple) and scope[0] == "margin":
                delta = float(scope[1]); cos0 = cands[0][0]
                veto = any((sc >= C and b >= B_floor and cos >= cos0 - delta) for (cos, sc, b) in cands)
            else:
                raise ValueError(f"unknown scope {scope!r}")
            labs.append("UNVERIFIABLE" if veto else "VERIFIED")
    if not labs: return "PASS-COMMON"
    if "UNVERIFIABLE" in labs: return "DEMOTE"
    if "VERIFIED" in labs: return "VERIFIED"
    return "PASS-COMMON"

def metrics_at_C(items_pre, C, B_floor=0.0, scope=PRIMARY_SCOPE):
    res = [(it, item_label_at_C(r, C, B_floor, scope)) for (it, r) in items_pre]
    b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
    b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
    B1 = sum(l == "DEMOTE" for _, l in b1) / len(b1) if b1 else float("nan")
    B2 = sum(l == "VERIFIED" for _, l in b2) / len(b2) if b2 else float("nan")
    B3 = sum(l == "DEMOTE" for _, l in b3) / len(b3) if b3 else float("nan")
    return B1, B2, B3, (len(b1), len(b2), len(b3))

# ===== E27 NEW: S2 robustness sweep, S3 demotion attribution ==============================================

def s2_band_at_bfloor(items_pre, B_floor, scope=PRIMARY_SCOPE):
    """S2 -- C-sweep at a FIXED binding gate B_floor over the FROZEN C grid; locate the joint (fa<=0.10 AND
    B2>=0.90) band. Returns (rows, band). The robustness verdict is read at the OP-POINT's selected B_floor."""
    rows = []
    for C in S2_GRID:
        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C), B_floor, scope)
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

def s2_perBfloor_summary(items_pre, scope=PRIMARY_SCOPE):
    """Per-B_floor joint C-band summary over the FROZEN B_FLOOR_GRID. The bf-band (sec6) non-triviality is the
    count of B_floor points whose min-fa (over C, at B2>=0.90) clears GATE_FA -- read in main for the verdict."""
    out = []
    for B_floor in B_FLOOR_GRID:
        rows, band = s2_band_at_bfloor(items_pre, float(B_floor), scope)
        min_fa = min((fa for (_C, fa, b2, _ok) in rows if (not np.isnan(b2)) and b2 >= RECALL_FLOOR), default=float("nan"))
        clears = (not np.isnan(min_fa)) and (min_fa <= GATE_FA)
        out.append((B_floor, band["width"], band["points"], band["b2_liftoff"], band["robust"], min_fa, clears))
    return out

def s3_attribution(items_pre, op_C, op_B_floor, fa_base, fa_op, scope=PRIMARY_SCOPE):
    """S3 -- decompose B1-class (spoof) demotions at the op-point (op_C, op_B_floor, scope) into:
       (a) noauth baseline  : demotes already at C=+inf (no veto needed; gate-independent),
       (b) contradiction-veto reject organ : demotes at (op_C,op_B_floor,scope) but NOT at C=+inf (a candidate in
                                             the BOUND subset crossed: contradiction>=op_C AND B>=op_B_floor),
       (c) accept/entailment-lift organ    : NOT wired in this standalone probe -> structurally 0.
    reject_share = (fa_base - fa_op)/fa_base. Bar (carried): > 0.50."""
    spoofs = [r for (it, r) in items_pre if it["class"] == B1_CLASS]
    n_total = len(spoofs)
    n_demote_op = n_by_noauth = n_by_veto = n_survive = 0
    for r in spoofs:
        base = item_label_at_C(r, float("inf"), 0.0, scope)            # gate off (B_floor=0) == no-veto baseline
        op = item_label_at_C(r, float(op_C), float(op_B_floor), scope)
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
    ap.add_argument("--out", default="reports/report_E34.md")   # NEVER a frozen-report path (no clobber E32/E30/E28/E27)
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
                cs = [c for (c, _s, _b) in x[1]]
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

    # observed grids (selection over OBSERVED values only; no post-hoc fishing). tuples are (cos, sc, B).
    C_obs = sorted({sc for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc, b) in x[1]})
    B_obs = sorted({b for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc, b) in x[1]})

    # ---- op-point selector (FROZEN selection; B_floor replaces the cosine-K axis) ----------------------------
    # over OBSERVED (C, B_floor): MIN false-accept subject to B2>=0.90. Tie-break (frozen): widest joint C-band at
    # that B_floor -> lowest C -> highest B_floor. selection peeks ONLY recall feasibility (no fishing on fa).
    def select_op(scope):
        feasible = []
        for Bf in B_obs:
            for C in C_obs:
                b1, b2, _b3, _ = metrics_at_C(items_pre, C, Bf, scope)
                if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                    feasible.append((1.0 - b1, float(C), float(Bf)))
        if not feasible:
            return None, None, None, float("nan")
        min_fa = min(f for f, _c, _bf in feasible)
        cand = [(c, bf) for (f, c, bf) in feasible if abs(f - min_fa) < 1e-12]
        _bw = {bf: s2_band_at_bfloor(items_pre, bf, scope)[1]["width"] for (_c, bf) in cand}
        cand.sort(key=lambda cb: (-_bw[cb[1]], cb[0], -cb[1]))
        c_, bf_ = cand[0]
        _b1, b2_, _b3, _ = metrics_at_C(items_pre, c_, bf_, scope)
        return float(c_), float(bf_), float(b2_), float(min_fa)

    # E34 DEGENERACY ANCHOR (Z4): B_floor=0 (gate off) MUST reproduce deberta scope=any fa 0.1667 (clean superset).
    _degen_feas = []
    for C in C_obs:
        b1, b2, _b3, _ = metrics_at_C(items_pre, C, 0.0, "any")
        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
            _degen_feas.append(1.0 - b1)
    degen_fa = min(_degen_feas) if _degen_feas else float("nan")
    degen_ok = (not np.isnan(degen_fa)) and abs(degen_fa - DEBERTA_ANCHOR_FA) <= ANCHOR_TOL
    print(f"[degeneracy B_floor=0 scope=any] fa={degen_fa} vs deberta anchor {DEBERTA_ANCHOR_FA} +/-{ANCHOR_TOL} -> ok={degen_ok}")

    # ANCHOR-COMPARE: primary scope='any'. fa_op read against bart 0.0667 (cross-model) + deberta 0.1667 (beat-bar).
    anc_C, anc_Bf, anc_B2, anc_fa = select_op(ANCHOR_SCOPE)   # ANCHOR_SCOPE == PRIMARY_SCOPE == 'any'
    anchor_below_bar = (anc_C is not None) and (not np.isnan(anc_fa)) and (anc_fa < E28_OP_FA)
    print(f"[anchor-compare scope=any] C={anc_C} B_floor={anc_Bf} fa_op={anc_fa} "
          f"vs bart bar {E28_OP_FA} / deberta bar {DEBERTA_ANCHOR_FA} -> below_bart={anchor_below_bar}")

    # E34 PRIMARY op-point: scope='any' over the BOUND subset (B>=B_floor).
    chosen_C, chosen_Bf, chosen_B2, _min_fa = select_op(PRIMARY_SCOPE)
    if chosen_C is None:
        op_verdict = "FAIL_RECALL_UNUSABLE"; B1 = B2 = B3 = fa = move = float("nan")
    else:
        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C, chosen_Bf, PRIMARY_SCOPE)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if   fa <= GATE_FA:           op_verdict = "PASS"
        elif fa < PARTIAL_BAND:       op_verdict = "FAIL_PARTIAL_VETO"
        else:                         op_verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"

    # ---- S2 robustness: band read at the op-point B_floor + per-B_floor summary (the bf-band feeds the verdict) -
    Bf_for_band = chosen_Bf if chosen_Bf is not None else 0.0
    s2_rows, band = s2_band_at_bfloor(items_pre, float(Bf_for_band), PRIMARY_SCOPE)
    s2_perBf = s2_perBfloor_summary(items_pre, PRIMARY_SCOPE)
    bf_clearing = [row for row in s2_perBf if row[6]]          # B_floor points whose min-fa clears GATE_FA
    bf_band_points = len(bf_clearing)
    bf_band_nontrivial = bf_band_points >= S2_BAND_MIN_POINTS  # sec6: not a single-point knife-edge
    if chosen_C is not None and base_ok:
        s3 = s3_attribution(items_pre, chosen_C, chosen_Bf, fa_base, fa, PRIMARY_SCOPE)
    else:
        s3 = dict(n_total=0, n_demote_op=0, n_by_noauth=0, n_by_veto=0, n_survive=0, n_by_entailment=0,
                  reject_share=float("nan"), bar_met=False)

    # ---- MARGIN robustness arm (REPORTED ONLY; NOT the verdict) -- op-point per delta over the FROZEN grid ---
    margin_rows = []
    for delta in MARGIN_GRID:
        mC, mBf, mB2, mfa = select_op(("margin", float(delta)))
        if mC is None:
            margin_rows.append((delta, None, None, float("nan"), float("nan"), False, float("nan")))
        else:
            _r, mband = s2_band_at_bfloor(items_pre, float(mBf), ("margin", float(delta)))
            ms3 = s3_attribution(items_pre, mC, mBf, fa_base, mfa, ("margin", float(delta))) if base_ok else \
                  dict(reject_share=float("nan"))
            margin_rows.append((delta, mC, mBf, mfa, mB2, mband["robust"], ms3["reject_share"]))

    # ---- E34 verdict (PRE_REGISTER_E34.md sec5-6; reads scope=any fa_op vs deberta 0.1667 + GATE 0.10 + bf-band) -
    # VOID guards: baseline mismatch / degenerate rho / recall-unusable / degeneracy-anchor mismatch (B_floor=0
    # must reproduce 0.1667). The forks read fa_op (primary scope=any); B2>=0.90 guaranteed by select_op feasibility.
    # BINDING_IS_THE_LEVER additionally requires a NON-TRIVIAL bf-band (>= S2_BAND_MIN_POINTS clearing points).
    s3rej = s3["reject_share"]
    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"   # noauth path broke (model-independent)
    elif degenerate:                verdict = "VOID_RHO"                 # contradiction~cosine collinear (rho>=0.95)
    elif not degen_ok:              verdict = "VOID_DEGENERACY"          # B_floor=0 did NOT reproduce deberta 0.1667
    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"     # no op-point holds B2>=0.90 -> fa unreadable
    elif (fa <= GATE_FA) and bf_band_nontrivial:
                                    verdict = "BINDING_IS_THE_LEVER"     # fa<=0.10 AND B2>=0.90 over a real bf-band
    elif fa <= GATE_FA:             verdict = "BINDING_KNIFE_EDGE"       # clears gate but bf-band trivial (E27-class)
    elif fa < DEBERTA_ANCHOR_FA:    verdict = "BINDING_HELPS_PARTIAL"    # 0.10 < fa < 0.1667 (beats deberta, not gate)
    else:                           verdict = "BINDING_NOT_THE_LEVER"    # fa >= 0.1667 -> reframe fails, escalate organ

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
    Bfn = chosen_Bf if chosen_Bf is not None else 0.0
    # conditioned candidate counts at op-point: contradiction crossing (con>=C). NOTE: the op-point veto also gates
    # on B>=B_floor, but diag carries cosine (S1 diagnostic, UNTOUCHED), not B -> this count is contradiction-only.
    gv = sum((s >= Cn) for (s, c) in gc) if (gc and chosen_C is not None) else float("nan")   # gold con-crossing
    sv = sum((s >= Cn) for (s, c) in spc) if (spc and chosen_C is not None) else float("nan")  # spoof con-crossing
    # S1 DRIVER ISOLATION: gold-content tail items (contradiction >= S1_TAIL_CON) -- the knife-edge drivers,
    # with binding cosine (the observable the lever uses to spare them). Spoof-content tail for contrast.
    gc_tail  = sorted([(sc, cos, _id) for (c_, _id, k, sc, cos) in diag if c_ == B2_CLASS and k == "finding" and sc >= S1_TAIL_CON], reverse=True)
    spc_tail = sorted([(sc, cos, _id) for (c_, _id, k, sc, cos) in diag if c_ == B1_CLASS and k == "finding" and sc >= S1_TAIL_CON], reverse=True)
    gc_tail_cos_med  = float(np.percentile([c for _s, c, _i in gc_tail], 50)) if gc_tail else float("nan")
    spc_tail_cos_med = float(np.percentile([c for _s, c, _i in spc_tail], 50)) if spc_tail else float("nan")

    # ---- report --------------------------------------------------------------------------------------------
    L = [
        "# report_E34 -- reframe reject task: binding-gate veto (scope=any over BOUND subset) vs deberta 0.1667 bar (S1/S2/S3)",
        "",
        f"- pre-register   : PRE_REGISTER_E34.md (FROZEN md5 91ae26c51ee794fa6f5c94497d109be0) -- sec1/2/4/5/6 operative",
        f"- lever          : BINDING GATE -- veto SCOPE=any over BOUND subset iff (P(CON)>=C AND B>=B_floor); B=lexical overlap(claim,premise); premise=source.FINDING / hyp=claim ; MODEL={CE_MODEL} (UNCHANGED)",
        f"- premise content: from_finding={n_find}/{n_prem} (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)",
        f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
        f"- fixture md5    : {fm} (E25b) | heldout md5 : {hm}",
        f"- heldout classes: {cls}",
        "",
        "## trust gates (else VOID)",
        f"- baseline (C=+inf) B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (no-veto 0.467) reproduced={base_ok}",
        f"- degeneracy (B_floor=0 scope=any) fa={degen_fa} vs deberta anchor {DEBERTA_ANCHOR_FA} +/-{ANCHOR_TOL} -> ok={degen_ok} (clean-superset check)",
        f"- decorrelation spearman(contradiction,cosine) rho = {rho:.3f} over {len(decorr)} pairs | VOID-guard rho>={DEGENERATE_RHO} -> degenerate={degenerate}",
        f"- advisory: |rho| < {PREREG_RHO_ADVISORY} -> {rho_advisory_ok} (REPORTED ONLY; FROZEN substrate VOID-guard is {DEGENERATE_RHO}; see CONFLICT note)",
        f"- contradiction_idx read from id2label (single, asserted) ; from_finding={n_find} asserted > 0",
        "",
        "## op-point gate (scope=any; min fa s.t. B2>=0.90 over observed (C,B_floor)). bars: bart 0.0667 (cross-model) / deberta 0.1667 (beat)",
        f"- anchor-compare (scope=any): C={anc_C} B_floor={anc_Bf} fa_op={anc_fa} vs bart {E28_OP_FA} / deberta {DEBERTA_ANCHOR_FA} -> below_bart={anchor_below_bar}",
        f"- chosen C = {chosen_C} | chosen B_floor (binding gate) = {chosen_Bf} | B2 at op-point = {chosen_B2}",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}  (gate <= {GATE_FA})",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        f"- op-point verdict  = {op_verdict}",
        "",
        "## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=any). delta gates a cosine bound-neighborhood on top of B",
    ]
    for (delta, mC, mBf, mfa, mB2, mrob, mrej) in margin_rows:
        L.append(f"    delta={delta:.2f}  C={mC}  B_floor={mBf}  fa={mfa}  B2={mB2}  band_robust={mrob}  reject_share={mrej}")
    L += [
        "",
        "## S2 -- (C, B_floor) band / lift-off robustness (band read at op-point B_floor; FROZEN grids)",
        f"- band at op-point B_floor={Bf_for_band}: joint (fa<={GATE_FA} AND B2>={RECALL_FLOOR}) C_lo={band['c_lo']} "
        f"C_hi={band['c_hi']} width={band['width']:.4f} points={band['points']}",
        f"- B2 lift-off within band (max B2 - floor) = {band['b2_liftoff']:.4f}  (>0 == not pinned to floor)",
        f"- robustness bar: width>={S2_BAND_MIN_WIDTH} AND points>={S2_BAND_MIN_POINTS} AND liftoff>0 -> robust={band['robust']}",
        f"- bf-band non-triviality (verdict input): {bf_band_points} B_floor points clear GATE_FA -> nontrivial={bf_band_nontrivial} (bar >= {S2_BAND_MIN_POINTS})",
        "- per-B_floor summary (B_floor, C-band_width, points, b2_liftoff, robust, min_fa, clears_gate):",
    ]
    for (Bf, w, p, lo, rb, mfa, cl) in s2_perBf:
        L.append(f"    B_floor={Bf:.2f}  width={w:.4f}  points={p}  liftoff={lo:.4f}  robust={rb}  min_fa={mfa}  clears={cl}")
    L += [
        "- C-sweep at op-point B_floor (C, false-accept, B2, joint_ok):",
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
        "- S1 expectation (diagnostic): cosine is RETAINED only for the rho guard + this diagnostic; the E34 lever is",
        "  lexical binding B, not cosine (E28 cosine-separability FALSIFIED). gold/spoof cos shown for continuity.",
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
        f"## candidate-level separation at op-point (C={Cn:.5f}, B_floor={Bfn}; counts finding candidates -- DIAGNOSTIC)",
        f"- gold-content candidates  : {_summ(gc_s)} | cross (con>=C; B not paired in diag): {gv}/{len(gc_s)}",
        f"- spoof-content candidates : {_summ(spc_s)} | cross (con>=C; B not paired in diag): {sv}/{len(spc_s)}",
        f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
        f"- S1 expectation: separation > 0.5 -> {s1_sep_ok} (diagnostic only; verdict reads max-based fa, not sep)",
        "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
        "  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E34.md sec6, the operative forks -- read scope=any fa_op vs deberta bar 0.1667 + gate 0.10):",
        "  BINDING_IS_THE_LEVER (fa_op <= 0.10 AND B2>=0.90 AND bf-band nontrivial) -> the reject-task reframe WORKS;",
        "    the binding gate fixes the E29 retrieval-misbinding defect -> proceed to robustness sweep + verifier-",
        "    integration (rho 0.95-vs-0.50 reconcile, entailment-lift -> S3 three-way, full-GOLD scale). TOMMY GO REQUIRED.",
        "  BINDING_KNIFE_EDGE (fa_op <= 0.10 but bf-band trivial) -> clears the gate on a single B_floor point (E27-class",
        "    fragility) -> tighten the binding signal / widen the grid before claiming the lever.",
        "  BINDING_HELPS_PARTIAL (0.10 < fa_op < 0.1667) -> binding beats deberta-plain but does NOT clear the gate ->",
        "    directionally right, insufficient alone -> combine with a second organ (design, next).",
        "  BINDING_NOT_THE_LEVER (fa_op >= 0.1667) -> no gain over E33; the per-candidate contradiction-veto organ is",
        "    EXHAUSTED even reframed -> escalate to a DIFFERENT reject/accept organ class (accept/entailment-lift three-way).",
        "  VOID_* -> trust gate failed (baseline mismatch / rho degenerate / recall unusable / B_floor=0 != 0.1667) -> reconcile, re-run.",
        "",
        "CONFLICT note (R15 / proto 3.10): advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95 (one-sided),",
        "  spearman on (contradiction, cosine). The E34 lever is BINDING (lexical), NOT cosine -- cosine is retained ONLY",
        "  for this rho guard + S1 diagnostics. Both pass at observed rho. This file keeps the FROZEN 0.95 as the VOID",
        "  trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
