#!/usr/bin/env python3
# emit_E37_readout.py -- regenerate the E37 6-field per-item readout (E39 v2 noauth-split contract).
# Contract: reports/PRE_REGISTER_E39.md v2 (FROZEN md5 774f8e41e2461777da197e3e809d573a).
#
# E37 (run_E37_probe.py, 88489f8) emits report_E37.md ONLY; con/ent live in-memory (item_label_at_C). This
# emitter IMPORTS the frozen scorer, replays the FROZEN op-point over heldout_E17, and serializes:
#     { item_id, n_con, n_ent, S_size, true_class, pre_demoted }   (per B1/B2 item)
# It SELF-CHECKS (sec6 reconcile + sec4 anchor) BEFORE writing the json. VOID on any mismatch -- no fabricated con.
#
# MODEL RUN (DeBERTa NLI via run_E37_probe.ce_scores/ce_entail). PRE-RUN: confirm CUDA/CPU + md5 (printed below).
# Run from lab/dpo/ :  python emit_E37_readout.py

import os, sys, json
import run_E37_probe as e37   # executes its module setup (ONTO_RETRIEVE_FLOOR=0.45, torch, NLI, frozen substrate)

# ---- FROZEN E37 OP-POINT (gate_E37.log; replayed, NOT re-selected) ----
OP_C   = 0.0012960433959960938
OP_A   = 0.35
OP_BF  = 0.1
OP_SC  = "any"
OP_W   = 0.0
OP_P   = 0.67          # == tau_E37 ; consensus-share at the E37 op-point
TAU    = OP_P          # anchor threshold (lambda=0 -> con_share >= TAU)
FA_DP  = 4
ANCHOR_FA   = 0.0333   # 29/30 (16 pre_demoted + 13 con-veto) at 4dp
AUTHONLY_FA = 0.0714   # 13/14 auth-only diagnostic at 4dp

FIXTURE      = os.environ.get("E39_FIXTURE", "eval/_local/gold_fixture_E25b.json")
HELDOUT      = os.environ.get("E39_HELDOUT", "eval/_local/heldout_E17.jsonl")
FIXTURE_MD5  = "4a45f52883a802e8d8d1d5ff5d185bdb"
HELDOUT_MD5  = "7e9fe030646d5671952e7a9fe9437e37"
OUT_JSON     = os.environ.get("E37_READOUT", "eval/_local/E37_boundset.json")


def die(msg):
    sys.stderr.write("VOID: %s\n" % msg)
    sys.exit(2)


def build_items_pre():
    # mirror run_E37_probe.main setup byte-faithfully (md5-gate -> store -> index -> precompute_item)
    fm, hm = e37.md5(FIXTURE), e37.md5(HELDOUT)
    print("[md5] fixture %s %s | heldout %s %s"
          % (fm, "OK" if fm == FIXTURE_MD5 else "MISMATCH", hm, "OK" if hm == HELDOUT_MD5 else "MISMATCH"))
    if fm != FIXTURE_MD5: die("fixture md5 mismatch -> not E25b")
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

    # E30 ordering guard (top-1-cosine-first) -- byte-identical to E37 main
    for (_it, rr) in items_pre:
        for x in rr:
            if isinstance(x, tuple) and x[0] == "auth":
                cs = [c for (c, _s, _e, _b, _a) in x[1]]
                if not all(cs[i] >= cs[i + 1] - 1e-9 for i in range(len(cs) - 1)):
                    die("r[1] not top-1-cosine-first -> TOP1 scope invalid")
    return items_pre


def representative(res):
    # max con_share auth claim at the frozen op-point ; tie-break min n_ent. con_share=0 for empty S.
    # returns (n_con, n_ent, S_size) or None if the item has NO auth resolution.
    best = None  # (con_share, -? ) -> we sort by (con_share desc, n_ent asc)
    for r in res:
        if isinstance(r, tuple) and r and r[0] == "auth":
            S = e37._bound_subset(r[1], OP_BF, OP_SC, OP_W)
            nS = len(S)
            n_con = sum(1 for (cos, sc, en, bl, ba) in S if sc >= OP_C)
            n_ent = sum(1 for (cos, sc, en, bl, ba) in S if en >= OP_A)
            cshare = (float(n_con) / float(nS)) if nS > 0 else 0.0
            key = (cshare, -n_ent)
            if best is None or key > best[0]:
                best = (key, n_con, n_ent, nS)
    if best is None:
        return None
    return best[1], best[2], best[3]


def emit_records(items_pre):
    recs_out = []
    for (it, res) in items_pre:
        cl = it["class"]
        if cl == e37.B1_CLASS:
            tc = "spoof"
        elif cl == e37.B2_CLASS and it["id"] not in e37.B2_EXCLUDE:
            tc = "gold"
        else:
            continue  # B3 / excluded -> not in the E39 readout
        pre_demoted = (e37.item_label_at_C(res, float("inf"), 0.0, OP_SC) == "DEMOTE")
        rep = representative(res)
        if rep is None:
            n_con = n_ent = S_size = 0   # no auth resolution (all-common) -> PASS-COMMON in E37 -> accept. reproduced.
        else:
            n_con, n_ent, S_size = rep   # S_size==0 (auth claims all below B_floor) -> VERIFIED in E37 -> accept. reproduced.
        recs_out.append({"item_id": str(it["id"]), "n_con": int(n_con), "n_ent": int(n_ent),
                         "S_size": int(S_size), "true_class": tc, "pre_demoted": bool(pre_demoted)})
    return recs_out


def self_check(items_pre, recs_out):
    # sec6 RECONCILE: emit decision == E37 op-point label, per item (class-blind). The real pairing gate.
    # SPOOF-ONLY: D_lambda at lambda=0 (= con_share) reproduces E37's spoof DEMOTE side (con-veto claims have
    # n_ent==0). Golds are EXCLUDED from per-item reconcile by design: an entailer-rescued gold (con_share>=P AND
    # n_ent>=1) is VERIFIED in E37 but rejected by D_0 -- that divergence at lambda=0 is exactly the gap the n_ent
    # term closes for lambda>0 (the LIFT, measured via B2 in the sweep, NOT anchored here).
    by_id = {r["item_id"]: r for r in recs_out}
    mism = []
    n_chk = 0
    for (it, res) in items_pre:
        rid = str(it["id"])
        if rid not in by_id:
            continue
        r = by_id[rid]
        if r["true_class"] != "spoof":
            continue
        n_chk += 1
        con_share = (r["n_con"] / r["S_size"]) if r["S_size"] > 0 else 0.0
        emit_reject = r["pre_demoted"] or (con_share >= TAU)
        e37_demote = (e37.item_label_at_C(res, OP_C, OP_BF, OP_SC, OP_A, OP_W, OP_P) == "DEMOTE")
        if emit_reject != e37_demote:
            mism.append((rid, r["true_class"], emit_reject, e37_demote,
                         r["n_con"], r["n_ent"], r["S_size"], r["pre_demoted"]))
    if mism:
        for m in mism:
            sys.stderr.write("  MISMATCH id=%s class=%s emit_reject=%s e37_demote=%s "
                             "n_con=%d n_ent=%d S=%d pre_demoted=%s\n" % m)
        die("sec6 reconcile: %d SPOOF item(s) where emit decision != E37 op label (representative unfaithful)" % len(mism))
    print("[sec6 reconcile] emit decision == E37 op label for all %d SPOOF items -> PASS" % n_chk)

    # sec4 ANCHOR: lambda=0, tau=0.67 over the 30 spoofs.
    spoofs = [r for r in recs_out if r["true_class"] == "spoof"]
    n_spoof = len(spoofs)
    def reject0(r):
        cs = (r["n_con"] / r["S_size"]) if r["S_size"] > 0 else 0.0
        return r["pre_demoted"] or (cs >= TAU)
    n_rej = sum(reject0(r) for r in spoofs)
    fa = (n_spoof - n_rej) / n_spoof if n_spoof else float("nan")
    n_pre = sum(r["pre_demoted"] for r in spoofs)
    n_con_veto = sum((not r["pre_demoted"]) and ((r["n_con"] / r["S_size"] if r["S_size"] > 0 else 0.0) >= TAU)
                     for r in spoofs)
    auth = [r for r in spoofs if not r["pre_demoted"]]
    auth_veto = sum(((r["n_con"] / r["S_size"] if r["S_size"] > 0 else 0.0) >= TAU) for r in auth)
    fa_auth = (len(auth) - auth_veto) / len(auth) if auth else float("nan")
    print("[sec4 anchor] spoofs=%d pre_demoted=%d con_veto=%d reject=%d -> fa_op=%.4f (expect %.4f)"
          % (n_spoof, n_pre, n_con_veto, n_rej, fa, ANCHOR_FA))
    print("[sec4 auth-only] auth_spoofs=%d con_veto=%d -> fa=%.4f (expect %.4f)"
          % (len(auth), auth_veto, fa_auth, AUTHONLY_FA))
    # structural D_0 == con_share is exact by formula (n_con/S_size); nothing to assert separately.
    if round(fa, FA_DP) != ANCHOR_FA:
        die("anchor fa_op %.6f (4dp %.4f) != E37 %.4f -- composite anchor not reproduced" % (fa, round(fa, FA_DP), ANCHOR_FA))
    if round(fa_auth, FA_DP) != AUTHONLY_FA:
        die("auth-only fa %.6f (4dp %.4f) != %.4f -- decomposition drift" % (fa_auth, round(fa_auth, FA_DP), AUTHONLY_FA))
    print("[sec4 anchor] PASS")


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
    self_check(items_pre, recs_out)   # VOIDs before any write
    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(recs_out, f, indent=2)
    print("[write] %s (%d records) -- gitignored, LOCAL only" % (OUT_JSON, len(recs_out)))


if __name__ == "__main__":
    main()
