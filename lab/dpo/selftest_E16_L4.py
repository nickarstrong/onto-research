#!/usr/bin/env python3
# selftest_E16_L4.py -- E16 SHIP v1 self-test (RunPod; CUDA + DeBERTa).
#
# PURPOSE (pack v94 sec3 step4): prove the L4 organ, AS WIRED into verify_E16_L4, reproduces
# its FROZEN anchor inside the harness -- the integration drift guard. Mismatch = STOP
# (integration drift), NOT a re-measure.
#
# Runs the FROZEN graduated emitter (emit_E42scale, 2273545) over the md5-gated E25b + heldout,
# then asserts FOUR guards from SPEC_verifier_v1 sec2 + the new integration guard:
#
#   G3 ANCHOR     : fa_op == 0.0333 (byte) AND auth-only == 0.0714. version/env drift guard.
#   G2 CONTENTS   : spoof set non-empty AND gold set non-empty (md5 pass != usable artifact).
#   G1 RHO VOID   : one-sided rho(D_lambda, upstream_bind) < 0.95 (else organ = retrieval proxy).
#   G4 (implicit) : verdict = max-based gate fa, never p50 sep (this script reads only fa).
#   G-INTEGRATION : verify_E16_L4.L4Bind.organ_record(item) == frozen emit_records(item) byte
#                   per (n_con, n_ent, S_size, pre_demoted) -> inline path == batch emitter.
#
# Also reports F2 recall (cap 0.9000 structural) as a sanity readout (not a graduation gate).
#
# Run from lab/dpo/ :   python3 selftest_E16_L4.py
# PRE-RUN: assert CUDA (no silent CPU), sentencepiece+protobuf present (deberta-v3 tokenizer).

import os
import sys
import json

import torch
assert torch.cuda.is_available(), "CUDA unavailable -> refusing to run the organ on CPU (silent-CPU guard)"

import emit_E42scale_readout as emit42
import verify_E16_L4 as L4

FA_DP       = emit42.FA_DP
ANCHOR_FA   = emit42.ANCHOR_FA        # 0.0333
AUTHONLY_FA = emit42.AUTHONLY_FA      # 0.0714
RHO_BAR     = emit42.RHO_BAR          # 0.95 one-sided
CAP_RECALL  = emit42.CAP_RECALL       # 0.90
TAU         = emit42.TAU
LAM         = emit42.LAM
FIXTURE     = emit42.FIXTURE
REPORT      = os.environ.get("E16_REPORT", "reports/report_E16_L4_selftest.md")


def _fa(recs, auth_only=False):
    spoofs = [r for r in recs if r["true_class"] == "spoof"]
    if auth_only:
        spoofs = [r for r in spoofs if not r["pre_demoted"]]
    if not spoofs:
        return None, 0
    accepted = sum(1 for r in spoofs if not emit42._reject(r))   # false-accept = spoof NOT rejected
    return round(accepted / len(spoofs), FA_DP), len(spoofs)


def _recall(recs):
    golds = [r for r in recs if r["true_class"] == "gold"]
    if not golds:
        return None, 0
    kept = sum(1 for r in golds if not emit42._reject(r))        # gold survives the veto
    return round(kept / len(golds), 4), len(golds)


def _rho_void(recs):
    xs, ys = [], []
    for r in recs:
        ub = r.get("upstream_bind")
        if r["pre_demoted"] or r["S_size"] <= 0 or ub is None:
            continue
        xs.append(emit42._Dlam(r))
        ys.append(float(ub))
    rho, n = emit42._spearman(xs, ys)
    return rho, n


def main():
    print("== E16 SHIP v1 self-test ==")
    # 1) FROZEN batch emitter over md5-gated E25b + heldout (build_items_pre dies on md5 mismatch).
    items_pre = emit42.build_items_pre()
    batch = emit42.emit_records(items_pre)
    batch_by_id = {r["item_id"]: r for r in batch}

    # 2) G-INTEGRATION: inline L4 path (verify_E16_L4) must reproduce the batch record byte.
    bind = L4.L4Bind(FIXTURE)
    drift = []
    for (it, _res) in items_pre:
        if str(it["id"]) not in batch_by_id:
            continue                      # negctrl etc. -> not in the spoof/gold readout
        online = bind.organ_record(it)
        b = batch_by_id[online["item_id"]]
        for k in ("n_con", "n_ent", "S_size", "pre_demoted"):
            if online[k] != b[k]:
                drift.append((online["item_id"], k, online[k], b[k]))
    g_integration = (len(drift) == 0)

    # 3) G2 CONTENTS
    n_spoof = sum(1 for r in batch if r["true_class"] == "spoof")
    n_gold  = sum(1 for r in batch if r["true_class"] == "gold")
    g2 = (n_spoof > 0 and n_gold > 0)

    # 4) G3 ANCHOR
    fa_op, n_sp   = _fa(batch, auth_only=False)
    fa_auth, n_ap = _fa(batch, auth_only=True)
    g3 = (fa_op == ANCHOR_FA) and (fa_auth == AUTHONLY_FA)

    # 5) G1 RHO VOID
    rho, n_rho = _rho_void(batch)
    g1 = (rho < RHO_BAR)        # one-sided; measured -0.5481 INDEPENDENT

    # readout-only: F2 recall cap
    recall, n_g = _recall(batch)

    lines = []
    def out(s):
        print(s); lines.append(s)

    out("records        : %d (spoof %d / gold %d)" % (len(batch), n_spoof, n_gold))
    out("organ          : D_lambda=(n_con-%.1f*n_ent)/|S| @ tau %.2f ; reject = pre_demoted OR D>=tau" % (LAM, TAU))
    out("G1 rho VOID    : rho=%.4f (n=%d) < %.2f -> %s" % (rho, n_rho, RHO_BAR, "PASS" if g1 else "FAIL"))
    out("G2 contents    : spoof>0 AND gold>0 -> %s" % ("PASS" if g2 else "FAIL"))
    out("G3 anchor fa   : fa_op=%.4f (exp %.4f) ; auth-only=%.4f (exp %.4f) -> %s"
        % (fa_op, ANCHOR_FA, fa_auth, AUTHONLY_FA, "PASS" if g3 else "FAIL"))
    out("G-integration  : inline L4 == frozen batch (n_con/n_ent/S_size/pre_demoted) -> %s"
        % ("PASS" if g_integration else "FAIL %s" % drift[:5]))
    out("F2 recall (ro) : %.4f (n=%d ; cap %.2f structural)" % (recall, n_g, CAP_RECALL))

    verdict = g1 and g2 and g3 and g_integration
    out("VERDICT        : %s" % ("PASS -- organ reproduces anchor inside harness, no drift"
                                 if verdict else "FAIL -- STOP, do not commit"))

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# E16 SHIP v1 -- L4 self-test readout\n\n")
        f.write("```\n" + "\n".join(lines) + "\n```\n")
    print("[report] ->", REPORT)
    sys.exit(0 if verdict else 1)


if __name__ == "__main__":
    main()
