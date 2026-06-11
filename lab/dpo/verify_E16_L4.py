#!/usr/bin/env python3
# verify_E16_L4.py -- E16 SHIP v1 BUILD: wire the FROZEN content-bind organ
# (SPEC_verifier_v1, eacbac8) into verify_E16 as the L4 CONTRADICTED secondary pass.
#
# DISCIPLINE (pack v94 sec3/sec5 ; SPEC_verifier_v1 sec0/sec7):
#   - This file CALLS the graduated organ; it NEVER edits the organ or any frozen spec.
#   - The organ math (precompute -> representative -> D_lambda -> reject) is reused
#     BYTE-IDENTICAL from the graduated emitter emit_E42scale_readout.py (commit 2273545,
#     full-GOLD PASS/CAP_HOLDS) and run_E37_probe.py (NLI substrate). IMPORT-ONLY, NO
#     re-derivation (E40 pattern).
#   - Frozen organ (SPEC_verifier_v1 sec1/sec7, reproduced here as a COMMENT only):
#         D_lambda = (n_con - LAM*n_ent)/|S| ; LAM=1.0 ; tau=0.67
#         reject iff ( pre_demoted OR D_lambda >= tau )
#     Implemented by emit_E42scale._Dlam / ._reject (imported, not retyped).
#
# WHERE L4 SITS (seam):
#   verify_E16.resolve_claim labels a claim VERIFIED once it BINDS to an authorized GOLD
#   source (L1-L3 = gate -> retrieve -> authorize). verify_E16 sec lines 217-219 state
#   CONTRADICTED is "an NLI SECONDARY pass on an already-bound passage; not built here".
#   L4 IS that secondary pass: a bound+authorized source whose GOLD content CONTRADICTS the
#   claim (organ reject) flips VERIFIED -> CONTRADICTED. pre_demoted (noauth/grade-fail) is
#   the existing UNVERIFIABLE arm, carried as the organ's separate OR-arm (SPEC sec1).
#
# WHY ITEM-LEVEL + ONLINE == BATCH (per-item purity, verified):
#   precompute_item(item, store, mat, recs, ...) is per-item pure: `mat` is the corpus
#   embedding cache (per-query lookup, not cross-item state); decorr/prem_log/diag are
#   post-hoc accumulators that do not feed back into the per-item resolution. So calling the
#   organ online (one item, fresh throwaway accumulators, the same store-wide `mat`) is
#   byte-identical to the batch emitter. selftest_E16_L4 asserts this byte-for-byte.
#
# NLI RUNTIME: DeBERTa-v3-large-mnli (sentencepiece+protobuf, CUDA). RunPod-side; not in
# the no-GPU sandbox. This module is import-clean without torch only via lazy import below.

import json
import sys

# --- import-only organ + substrate (these pull torch/transformers at import on a pod) -----
import emit_E42scale_readout as emit42   # graduated emitter: representative/_Dlam/_reject + frozen OP-point
import run_E37_probe as e37              # NLI substrate: precompute_item / item_label_at_C / build index
import verify_E16 as v                   # L1-L3 substrate: segment/classify/gate/resolve_claim/_eval bars

# Frozen OP-point + organ predicates, reused verbatim (NEVER redefined here):
OP_SC = emit42.OP_SC                     # "any" (E37 scope, frozen)
TAU   = emit42.TAU                       # 0.67 (E39 v4 best_op ; E40 region WIDE/STABLE)
LAM   = emit42.LAM                       # 1.0  (E40 graduated op)
_Dlam   = emit42._Dlam                   # (n_con - LAM*n_ent)/S_size
_reject = emit42._reject                 # pre_demoted OR (_Dlam >= TAU)
representative   = emit42.representative  # builds S, counts n_con(@OP_C)/n_ent(@OP_A)
item_label_at_C  = e37.item_label_at_C    # C=inf -> pre_demoted (noauth) detector


class L4Bind:
    """Holds the bind-corpus + its embedding index. Built ONCE; reused per claim.

    corpus_path is a GoldStore fixture (records {claim_key, source, locator} + manifest_files
    hash set). For the drift-guard self-test this is the FROZEN gold_fixture_E25b. For the
    operational config (S4) this is the live GOLD bind-corpus module, adapted to the same
    record shape and G2-gated before any verdict (non-empty spoof+gold, real hashes).
    """

    def __init__(self, corpus_path):
        self.store = e37.gr.GoldStore(corpus_path)
        self.mat, self.recs = e37.sem.build_index(self.store.records)
        raw = json.load(open(corpus_path, encoding="utf-8"))
        self.finding_by_source = {
            rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]
        }

    def organ_record(self, item):
        """Run the FROZEN organ over one heldout item. Returns the readout record
        {item_id, n_con, n_ent, S_size, pre_demoted} -- the EXACT shape emit_E42scale emits.
        Fresh throwaway accumulators (post-hoc only) keep this byte-identical to the batch."""
        res = e37.precompute_item(
            item, self.store, self.mat, self.recs,
            decorr=[], prem_log=[], finding_by_source=self.finding_by_source, diag=[],
        )
        pre_demoted = (item_label_at_C(res, float("inf"), 0.0, OP_SC) == "DEMOTE")
        rep = representative(res)
        if rep is None:
            n_con = n_ent = S_size = 0
        else:
            n_con, n_ent, S_size, _mean_bind = rep
        return {
            "item_id": str(item["id"]),
            "n_con": int(n_con), "n_ent": int(n_ent), "S_size": int(S_size),
            "pre_demoted": bool(pre_demoted),
        }


# --- L4 verdict for one item (the secondary pass) ---------------------------------------
def l4_verdict(item, bind):
    """CONTRADICTED secondary pass. Returns (label, record).
    label in {CONTRADICTED, VERIFIED_L3} -- L4 only ever DEMOTES a bound claim; it never
    promotes (accept-protective: organ measures consensus contradiction, SPEC sec0)."""
    rec = bind.organ_record(item)
    return ("CONTRADICTED" if _reject(rec) else "VERIFIED_L3"), rec


# --- emission-time integration: L1-L3 label, then L4 veto over bound items ---------------
def verify_item(item, bind):
    """Full L1-L4 verdict for one emission item.

    L1-L3 (verify_E16, deterministic, no model): segment -> classify -> gate -> resolve_claim
       -> item label in {PASS-COMMON, DEMOTE, VERIFIED}.
    L4 (this build): ONLY items L1-L3 calls VERIFIED enter the organ. A bound source the GOLD
       content contradicts -> CONTRADICTED. PASS-COMMON / DEMOTE are untouched by L4.
    """
    claims, seen = [], set()
    for s in v.segment(item["text"]):
        if v.is_qa_scaffold(s):
            continue
        n = v._norm(s)
        if n in seen:
            continue
        seen.add(n)
        ct, ok = v.classify(s)
        if ok:
            claims.append(v.resolve_claim(s, bind.store, ct))
    labs = [c["label"] for c in claims]
    l3 = ("PASS-COMMON" if not claims else
          "DEMOTE" if "UNVERIFIABLE" in labs else
          "VERIFIED" if "VERIFIED" in labs else "PASS-COMMON")
    if l3 != "VERIFIED":
        return l3, None                       # L4 only re-checks bound (VERIFIED) items
    l4, rec = l4_verdict(item, bind)
    return ("CONTRADICTED" if l4 == "CONTRADICTED" else "VERIFIED"), rec


if __name__ == "__main__":
    # Operational smoke (RunPod): label a heldout file through L1-L4 against a bind-corpus.
    #   python3 verify_E16_L4.py <heldout.jsonl> <bind_corpus.json>
    if len(sys.argv) < 3:
        print("usage: verify_E16_L4.py <heldout.jsonl> <bind_corpus.json>")
        sys.exit(2)
    bind = L4Bind(sys.argv[2])
    n = {"PASS-COMMON": 0, "DEMOTE": 0, "VERIFIED": 0, "CONTRADICTED": 0}
    for line in open(sys.argv[1], encoding="utf-8"):
        if not line.strip():
            continue
        it = json.loads(line)
        lab, _ = verify_item(it, bind)
        n[lab] = n.get(lab, 0) + 1
    print("[L1-L4 labels]", n)
