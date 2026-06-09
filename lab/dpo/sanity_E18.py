#!/usr/bin/env python3
"""sanity_E18.py - instrument-sanity for the E18 NLI claim-support gate (NOT a bar, R7).

Extends sanity_E17 with the entailment-separation falsifier the NLI layer needs.
Confirms, BEFORE nli_verify --eval and BEFORE locking tau:

  0. NLI liveness   : a faithful premise->claim pair scores ENTAIL high; an opposite
                      premise->claim pair scores ENTAIL low. If not, NLI is dead - stop.
  a. per-item trace : for each BOUND gold + BOUND NN-swap, the entailment prob of
                      (premise=bound finding, hypothesis=held-out text) + argmax label.
  b. tau lock       : tau = just above the MAX entail-prob among NN-swaps that argmax
                      to ENTAIL (i.e. the precision constraint NN-DEMOTE==1.0), NOT tuned
                      to pass B1. Reports the gold VERIFY-rate that survives at that tau.
                      If tau kills gold (mutually exclusive, E17-style) -> NO-GO signal here.
  c. separation     : entail-prob distribution gold vs NN-swap - do they separate?
  d. spin-gold flag : gold-with-finding items with low entail prob surfaced by id, so a
                      sub-bar B1 is attributable to held-out framing (R15), not silent.

Binding is the FROZEN path (GoldStore.retrieve + is_authorized = what resolve_claim uses).
Run with `python` after the retrieval floor is locked (sanity_E17). CPU.
Env: KMP_DUPLICATE_LIB_OK=TRUE ; ONTO_RETRIEVE_FLOOR (locked by sanity_E17) ; ONTO_NLI_MODEL.
"""
import json, os, sys
from collections import defaultdict

from gold_retrieve import GoldStore
import nli_verify as nv

HELDOUT = nv.HELDOUT
EPS = 0.01


def bound_locator(store, text):
    """Locator resolve_claim would bind to: top AUTHORIZED retrieved hit, else None."""
    hits = store.retrieve(text)
    auth = [h for h in hits if store.is_authorized(h)]
    return auth[0]["locator"] if auth else None


def nli_liveness():
    pe_ok, _ = nv.nli_entail_prob(
        "Erasing one bit of information has an irreducible minimum heat cost set by temperature.",
        "Discarding a bit of information dissipates a minimum amount of heat.")
    pe_bad, _ = nv.nli_entail_prob(
        "Erasing one bit of information has an irreducible minimum heat cost set by temperature.",
        "Information can be erased with no energy cost whatsoever.")
    ok = pe_ok > pe_bad and pe_ok > 0.5
    print(f"[0] NLI LIVENESS  entail(faithful)={pe_ok:.3f}  entail(opposite)={pe_bad:.3f} "
          f"-> {'OK' if ok else 'FAIL'}")
    if not ok:
        sys.exit("NLI LIVENESS FAILED - model not separating entail/contradict; fix before sanity.")


def main():
    store = GoldStore()
    findings = nv.load_findings()
    items = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    print(f"GOLD: {len(store.records)} records, {len(store.manifest_files)} authorized")
    nli_liveness()

    gold = [it for it in items if it["id"].startswith("ho_g")]
    nn   = [it for it in items if it["id"].startswith("ho_sn")]

    rows = []   # (id, expect, bound, p_entail, argmax_entail, prov)
    for it, expect in [(x, "VERIFY") for x in gold] + [(x, "DEMOTE") for x in nn]:
        loc = bound_locator(store, it["text"])
        prem = nv.lookup_finding(loc, findings) if loc else None
        if loc is None or prem is None:
            rows.append((it["id"], expect, bool(loc), None, None, "no-finding" if loc else "no-bind"))
            continue
        pe, am = nv.nli_entail_prob(prem, it["text"])
        prov = findings[0].get(loc, (None, "?"))[1]
        rows.append((it["id"], expect, True, round(pe, 4), am, prov))

    print("\n[a] per-item entailment (bound set)")
    print(f"  {'id':<9} {'expect':<7} {'bound':<5} {'P(entail)':<10} {'argmaxE':<8} prov")
    for r in rows:
        pe = "n/a" if r[3] is None else f"{r[3]:.3f}"
        am = "-" if r[4] is None else ("E" if r[4] else ".")
        print(f"  {r[0]:<9} {r[1]:<7} {str(r[2]):<5} {pe:<10} {am:<8} {r[5]}")

    g = [r for r in rows if r[1] == "VERIFY" and r[3] is not None]
    n = [r for r in rows if r[1] == "DEMOTE" and r[3] is not None]

    # [b] tau lock: NN that argmax to ENTAIL are the precision threat.
    nn_entail_probs = [r[3] for r in n if r[4]]
    tau = (max(nn_entail_probs) + EPS) if nn_entail_probs else 0.50
    nn_demoted = sum(not (r[4] and r[3] >= tau) for r in n)
    gold_verify = sum(r[4] and r[3] >= tau for r in g)
    print(f"\n[b] tau lock (NN-DEMOTE precision constraint)")
    print(f"  NN argmax-ENTAIL probs: {sorted(round(x,3) for x in nn_entail_probs) or 'none'}")
    print(f"  tau = {tau:.3f}")
    print(f"  at tau:  NN-swap DEMOTE = {nn_demoted}/{len(n)} = {nn_demoted/len(n):.3f}  (target 1.000)")
    print(f"           gold VERIFY   = {gold_verify}/{len(g)} = {gold_verify/len(g):.3f}")
    if gold_verify / len(g) < 0.90:
        print("  -> tau that demotes NN also kills gold (mutually exclusive, E17-style): "
              "entailment does NOT separate at this model size -> NO-GO signal, escalate model scale.")
    else:
        print(f"  -> separable. set:  $env:ONTO_NLI_TAU = \"{tau:.3f}\"  before nli_verify --eval")

    # [c] separation
    def stat(xs):
        xs = sorted(x[3] for x in xs)
        return f"min={xs[0]:.3f} med={xs[len(xs)//2]:.3f} max={xs[-1]:.3f}" if xs else "n/a"
    print(f"\n[c] entail-prob separation")
    print(f"  gold (VERIFY) : {stat(g)}")
    print(f"  NN   (DEMOTE) : {stat(n)}")

    # [d] spin-gold flag
    spin = {a.lower() for a in nv.SPIN_GOLD_ANCHORS}
    low_gold = [r for r in g if not (r[4] and r[3] >= tau)]
    print(f"\n[d] gold-with-finding that FAILS the gate at tau (would DEMOTE):")
    for r in low_gold:
        it = next(x for x in gold if x["id"] == r[0])
        is_spin = it.get("anchor", "").replace("DOI:", "").lower() in spin
        print(f"  {r[0]}  P(entail)={r[3]:.3f}  {'[pre-registered spin-gold]' if is_spin else '[CHECK: clean gold failing]'}")
    if not low_gold:
        print("  none - all gold-with-finding entail at tau.")


if __name__ == "__main__":
    main()
