#!/usr/bin/env python3
# emit_E42scale_readout.py -- E42scale: 7-field readout (6-field + upstream_bind) over the FROZEN
# full-GOLD store (gold_fixture_E25b.json, 217 rec) + heldout_E17, then resolve F1 (rho posture) and
# F2 (recall cap) at scale. NO fixture build: E25b IS full-GOLD (build_fixture_E17 supersedes E16
# 61-slice; E17->E18->E25b grew `finding` 0->27->90, NOT records).
#
# Contract: reports/PRE_REGISTER_E42scale.md (FROZEN md5 a2f6bb5fd19fbfd1c08c6de4d111df6e).
# Substrate: imports run_E37_probe (15e694a6...) FROZEN; reuses _bound_subset / item_label_at_C /
# precompute_item BYTE-IDENTICAL. emit_E37_readout.py is the SEPARATE anchor reproducer (untouched).
# Deltas vs emit_E37: (1) representative() also returns mean beff over the rep S; (2) upstream_bind in
# recs_out; (3) F1 spearman + F2 recall-under-op + fork; (4) writes E42scale_readout.json +
# E42scale_region.json; does NOT touch the frozen E37_boundset.json.
#
# MODEL RUN (DeBERTa NLI via run_E37_probe). PRE-RUN: confirm CUDA + md5 (printed below).
# Run from lab/dpo/ :  python emit_E42scale_readout.py

import os, sys, json, math
import run_E37_probe as e37   # frozen substrate setup (ONTO_RETRIEVE_FLOOR=0.45, torch, NLI)

# ---- FROZEN E37 OP-POINT (identical to emit_E37; replayed, NOT re-selected) ----
OP_C   = 0.0012960433959960938
OP_A   = 0.35
OP_BF  = 0.1
OP_SC  = "any"
OP_W   = 0.0           # W FROZEN 0 (E36 BINDING_EXHAUSTED) -> beff == B_lex
OP_P   = 0.67
TAU    = OP_P
LAM    = 1.0           # E40 graduated op: D_lambda = (n_con - LAM*n_ent)/|S|
FA_DP  = 4
ANCHOR_FA   = 0.0333   # 29/30 (16 pre_demoted + 13 con-veto)
AUTHONLY_FA = 0.0714   # 13/14 auth-only

FIXTURE      = os.environ.get("E39_FIXTURE", "eval/_local/gold_fixture_E25b.json")
HELDOUT      = os.environ.get("E39_HELDOUT", "eval/_local/heldout_E17.jsonl")
FIXTURE_MD5  = "4a45f52883a802e8d8d1d5ff5d185bdb"
HELDOUT_MD5  = "7e9fe030646d5671952e7a9fe9437e37"
OUT_JSON     = os.environ.get("E42_READOUT", "eval/_local/E42scale_readout.json")
OUT_REGION   = os.environ.get("E42_REGION",  "reports/E42scale_region.json")

# F1/F2 forks (FROZEN, PRE_REGISTER_E42scale sec4-5)
RHO_BAR      = 0.95    # one-sided; rho >= RHO_BAR -> graduation reopen
CAP_RECALL   = 0.90    # recall >= CAP_RECALL (<=3 rejected golds) -> cap holds


def die(msg):
    sys.stderr.write("VOID: %s\n" % msg)
    sys.exit(2)


def build_items_pre():
    # byte-faithful mirror of emit_E37.build_items_pre (md5 gate -> store -> index -> precompute)
    fm, hm = e37.md5(FIXTURE), e37.md5(HELDOUT)
    print("[md5] fixture %s %s | heldout %s %s"
          % (fm, "OK" if fm == FIXTURE_MD5 else "MISMATCH", hm, "OK" if hm == HELDOUT_MD5 else "MISMATCH"))
    if fm != FIXTURE_MD5: die("fixture md5 mismatch -> not E25b (full-GOLD store drifted)")
    if hm != HELDOUT_MD5: die("heldout md5 mismatch -> not v3")

    store = e37.gr.GoldStore(FIXTURE)
    mat, recs = e37.sem.build_index(store.records)
    items = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    cls = {}
    for it in items: cls[it["class"]] = cls.get(it["class"], 0) + 1
    print("[classes] %s | heldout items=%d" % (cls, len(items)))
    if not (e37.B1_CLASS in cls and e37.B2_CLASS in cls):
        die("heldout missing B1/B2 classes -> wrong file")

    decorr = []; prem_log = []; diag = []
    raw = json.load(open(FIXTURE, encoding="utf-8"))
    finding_by_source = {rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]}
    items_pre = [(it, e37.precompute_item(it, store, mat, recs, decorr, prem_log, finding_by_source, diag))
                 for it in items]
    n_find = sum(p == "finding" for p in prem_log)
    print("[premise] from_finding=%d/%d" % (n_find, len(prem_log)))
    if n_find <= 0: die("from_finding=0 -> fixture dropped 'finding' (E23 guard)")

    # E30 ordering guard (top-1-cosine-first), byte-identical to E37 main
    for (_it, rr) in items_pre:
        for x in rr:
            if isinstance(x, tuple) and x[0] == "auth":
                cs = [c for (c, _s, _e, _b, _a) in x[1]]
                if not all(cs[i] >= cs[i + 1] - 1e-9 for i in range(len(cs) - 1)):
                    die("r[1] not top-1-cosine-first -> TOP1 scope invalid")
    return items_pre


def _beff(bl, ba):
    return (1.0 - OP_W) * bl + OP_W * ba


def representative(res):
    # max con_share auth claim @ frozen op; tie-break min n_ent (== emit_E37). DELTA: also mean beff over S.
    # returns (n_con, n_ent, S_size, mean_bind) or None. mean_bind=None when S empty.
    best = None
    for r in res:
        if isinstance(r, tuple) and r and r[0] == "auth":
            S = e37._bound_subset(r[1], OP_BF, OP_SC, OP_W)
            nS = len(S)
            n_con = sum(1 for (cos, sc, en, bl, ba) in S if sc >= OP_C)
            n_ent = sum(1 for (cos, sc, en, bl, ba) in S if en >= OP_A)
            cshare = (float(n_con) / float(nS)) if nS > 0 else 0.0
            mean_bind = (sum(_beff(bl, ba) for (cos, sc, en, bl, ba) in S) / nS) if nS > 0 else None
            key = (cshare, -n_ent)
            if best is None or key > best[0]:
                best = (key, n_con, n_ent, nS, mean_bind)
    if best is None:
        return None
    return best[1], best[2], best[3], best[4]


def emit_records(items_pre):
    recs_out = []
    for (it, res) in items_pre:
        cl = it["class"]
        if cl == e37.B1_CLASS:
            tc = "spoof"
        elif cl == e37.B2_CLASS and it["id"] not in e37.B2_EXCLUDE:
            tc = "gold"
        else:
            continue
        pre_demoted = (e37.item_label_at_C(res, float("inf"), 0.0, OP_SC) == "DEMOTE")
        rep = representative(res)
        if rep is None:
            n_con = n_ent = S_size = 0
            upstream_bind = None      # no auth resolution -> bind undefined
        else:
            n_con, n_ent, S_size, upstream_bind = rep
        recs_out.append({"item_id": str(it["id"]), "n_con": int(n_con), "n_ent": int(n_ent),
                         "S_size": int(S_size), "true_class": tc, "pre_demoted": bool(pre_demoted),
                         "upstream_bind": (None if upstream_bind is None else float(upstream_bind))})
    return recs_out


def self_check(items_pre, recs_out):
    # sec6 RECONCILE + sec4 ANCHOR -- byte-faithful to emit_E37 (anchor VOID guard; in-memory only).
    by_id = {r["item_id"]: r for r in recs_out}
    mism = []; n_chk = 0
    for (it, res) in items_pre:
        rid = str(it["id"])
        if rid not in by_id: continue
        r = by_id[rid]
        if r["true_class"] != "spoof": continue
        n_chk += 1
        con_share = (r["n_con"] / r["S_size"]) if r["S_size"] > 0 else 0.0
        emit_reject = r["pre_demoted"] or (con_share >= TAU)
        e37_demote = (e37.item_label_at_C(res, OP_C, OP_BF, OP_SC, OP_A, OP_W, OP_P) == "DEMOTE")
        if emit_reject != e37_demote:
            mism.append(rid)
    if mism:
        die("sec6 reconcile: %d SPOOF item(s) emit!=E37 op label (%s)" % (len(mism), ",".join(mism)))
    print("[sec6 reconcile] PASS (%d spoof items)" % n_chk)

    spoofs = [r for r in recs_out if r["true_class"] == "spoof"]
    n_spoof = len(spoofs)
    def reject0(r):
        cs = (r["n_con"] / r["S_size"]) if r["S_size"] > 0 else 0.0
        return r["pre_demoted"] or (cs >= TAU)
    n_rej0 = sum(reject0(r) for r in spoofs)
    fa0 = (n_spoof - n_rej0) / n_spoof if n_spoof else float("nan")
    auth = [r for r in spoofs if not r["pre_demoted"]]
    auth_veto = sum(((r["n_con"] / r["S_size"] if r["S_size"] > 0 else 0.0) >= TAU) for r in auth)
    fa_auth = (len(auth) - auth_veto) / len(auth) if auth else float("nan")
    print("[sec4 anchor] spoofs=%d reject=%d fa_op=%.4f (expect %.4f) | auth-only fa=%.4f (expect %.4f)"
          % (n_spoof, n_rej0, fa0, ANCHOR_FA, fa_auth, AUTHONLY_FA))
    if round(fa0, FA_DP) != ANCHOR_FA:
        die("VOID_ANCHOR: fa_op %.4f != %.4f" % (round(fa0, FA_DP), ANCHOR_FA))
    if round(fa_auth, FA_DP) != AUTHONLY_FA:
        die("VOID_ANCHOR: auth-only %.4f != %.4f" % (round(fa_auth, FA_DP), AUTHONLY_FA))
    print("[sec4 anchor] PASS")


def _Dlam(r):
    return ((r["n_con"] - LAM * r["n_ent"]) / r["S_size"]) if r["S_size"] > 0 else 0.0


def _reject(r):
    return r["pre_demoted"] or (_Dlam(r) >= TAU)


def _spearman(xs, ys):
    # dependency-free spearman rho (pearson on ranks; average ranks for ties)
    n = len(xs)
    if n < 3: return float("nan"), n
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        rk = [0.0] * n; i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]: j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1): rk[order[k]] = avg
            i = j + 1
        return rk
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx == 0 or dy == 0: return float("nan"), n
    return num / (dx * dy), n


def resolve_forks(recs_out):
    # CONTENTS counters (E15/E23) -- md5 pass != usable
    spoofs = [r for r in recs_out if r["true_class"] == "spoof"]
    golds  = [r for r in recs_out if r["true_class"] == "gold"]
    if not spoofs: die("CONTENTS: empty spoof set")
    if not golds:  die("CONTENTS: empty gold set")
    bad = [r["item_id"] for r in recs_out if r["S_size"] > 0 and r["upstream_bind"] is None]
    if bad: die("upstream_bind null where S_size>0 (%s) -> F1 void-by-construction" % ",".join(bad))
    print("[contents] spoofs=%d golds=%d | upstream_bind non-null where S>0: OK" % (len(spoofs), len(golds)))

    # apply frozen op at scale -> fa_op (explicit D_lambda, not con_share)
    n_rej = sum(_reject(r) for r in spoofs)
    fa_op = (len(spoofs) - n_rej) / len(spoofs)
    print("[apply] D_lambda(%.1f)>=%.2f : spoof reject=%d/%d -> fa_op=%.4f" % (LAM, TAU, n_rej, len(spoofs), fa_op))

    # F1: spearman(D_lambda, upstream_bind) one-sided, over auth-resolved items (non-null bind)
    pop = [r for r in recs_out if r["upstream_bind"] is not None and r["S_size"] > 0]
    xs = [_Dlam(r) for r in pop]; ys = [r["upstream_bind"] for r in pop]
    rho, n1 = _spearman(xs, ys)
    f1_reopen = (not math.isnan(rho)) and (rho >= RHO_BAR)
    print("[F1] spearman(D_lambda, upstream_bind)=%.4f n=%d (bar one-sided >=%.2f) -> %s"
          % (rho, n1, RHO_BAR, "GRADUATION_REOPEN" if f1_reopen else "INDEPENDENT"))

    # F2: recall under op = golds accepted / total golds
    acc = sum(not _reject(r) for r in golds)
    recall = acc / len(golds)
    cap_holds = recall >= CAP_RECALL
    print("[F2] recall=%d/%d=%.4f (cap bar >=%.2f) -> %s"
          % (acc, len(golds), recall, CAP_RECALL, "CAP_HOLDS" if cap_holds else "CAP_DROPS"))

    # fork resolution
    if f1_reopen:
        fork = "GRADUATION_REOPEN"          # F1 trips -> D_lambda collinear with retrieval
    elif cap_holds:
        fork = "CAP_HOLDS"                   # v1 freeze path + provenance-verifier SPEC fold
    else:
        fork = "CAP_DROPS"                   # open E42 noauth-channel recall organ
    print("[FORK] %s" % fork)

    return {
        "fixture_md5": FIXTURE_MD5, "heldout_md5": HELDOUT_MD5,
        "op": {"lambda": LAM, "tau": TAU}, "fa_op": round(fa_op, FA_DP),
        "anchor": {"fa": ANCHOR_FA, "auth_only": AUTHONLY_FA, "reproduced": True},
        "F1": {"spearman": (None if math.isnan(rho) else round(rho, 4)), "n": n1,
               "bar_one_sided": RHO_BAR, "reopen": f1_reopen},
        "F2": {"recall": round(recall, 4), "accepted": acc, "total": len(golds),
               "cap_bar": CAP_RECALL, "cap_holds": cap_holds},
        "fork": fork,
        "counts": {"spoof": len(spoofs), "gold": len(golds)},
    }


def main():
    try:
        import torch
        dev = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        dev = "unknown"
    print("[device] %s" % dev)
    items_pre = build_items_pre()
    recs_out = emit_records(items_pre)
    gold_n = sum(r["true_class"] == "gold" for r in recs_out)
    spoof_n = sum(r["true_class"] == "spoof" for r in recs_out)
    print("[emit] records=%d (gold %d / spoof %d)" % (len(recs_out), gold_n, spoof_n))
    self_check(items_pre, recs_out)              # VOID_ANCHOR before anything is read
    region = resolve_forks(recs_out)             # CONTENTS + apply + F1 + F2 + fork

    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(recs_out, f, indent=2)
    os.makedirs(os.path.dirname(OUT_REGION) or ".", exist_ok=True)
    with open(OUT_REGION, "w", encoding="utf-8") as f:
        json.dump(region, f, indent=2)
    print("[write] %s (%d records, 7-field) -- gitignored, LOCAL only" % (OUT_JSON, len(recs_out)))
    print("[write] %s (region verdict)" % OUT_REGION)


if __name__ == "__main__":
    main()
