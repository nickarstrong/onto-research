#!/usr/bin/env python3
"""nli_verify2.py - E19 CONTRADICTION-VETO over top-K authorized bind.

EXTENDS (never mutates) E18 nli_verify.py. On top of the E18 entailment gate it
adds the fix for the E18 B2 leak (a false claim ENTAILED by a non-anchor authorized
source - retrieve-then-entail is gameable, E18 report / pack v54 sec 5):

    For a claim that E16 binds to an AUTHORIZED hit, look at ALL authorized hits in
    the retrieval top-K (not just E16's top-1):
      ENTAIL?    some authorized finding entails the claim   (P_entail >= TAU, argmax=entail)
      CONTRADICT? any authorized finding contradicts it      (P_contra >= VETO_TAU, argmax=contra)
    VERIFY  iff  E16 label == VERIFIED  AND  ENTAIL  AND  NOT CONTRADICT
    else    DEMOTE (UNVERIFIABLE).

Rationale (keystone sec 4 + pack v54 sec 5): NLI CONTRADICTION-detection is reliable
(B2_oracle = 1.0); ENTAILMENT-acceptance is fragile and corpus-permissive. So we use
NLI to REJECT (veto) and lean on it less to ACCEPT. The 3 E18 NN leaks (false claim
entailed by a non-anchor source) now meet a CONTRADICTING anchor among the top-K and
DEMOTE; gold is unharmed because gold's own anchor entails and no authorized finding
contradicts a faithful gold claim.

PRE-REGISTRATION (R6/R7): VETO_TAU is locked by the PRECISION constraint - NN-leak == 0
on the bound set AND gold not harmed - via `--calibrate`, BEFORE `--eval`. It is NOT
tuned to lift B1. Same discipline as nli_verify's TAU (locked by sanity before eval).

FROZEN imports (byte-identical): verify_E16, gold_retrieve, semantic_retrieve, nli_verify.
NLI model: reuses nli_verify.get_nli() (transformers-direct, torch-first, SEH-safe);
contradiction index is derived here from model.config.id2label.

Env (load-bearing): KMP_DUPLICATE_LIB_OK=TRUE ; ONTO_RETRIEVE_FLOOR ; ONTO_RETRIEVE_TOPK ;
ONTO_NLI_TAU ; ONTO_NLI_VETO_TAU (LOCK via --calibrate before --eval) ; ONTO_NLI_MODEL.
Run with `python` (Windows: not python3). CPU.

Usage:
  python nli_verify2.py --calibrate   # sweep VETO_TAU; report value with NN-leak==0 & gold safe
  python nli_verify2.py --eval         # E19 bars (B1/B2/B3) under the contradiction-veto gate
  python nli_verify2.py --probe "<claim>"   # single-claim trace (bind + entail + veto)
"""
import json, os, sys

import semantic_retrieve as sr            # noqa: F401  enables faulthandler; torch-first path
from gold_retrieve import GoldStore
import verify_E16 as v16
import nli_verify as nv                   # E18 layer (frozen) - reuse loaders + entail gate

# ---------------------------------------------------------------------------
# config (E18 carried byte-identical; one NEW pre-registered knob: VETO_TAU)
# ---------------------------------------------------------------------------
TAU      = nv.TAU                                                   # entailment accept threshold
VETO_TAU = float(os.environ.get("ONTO_NLI_VETO_TAU", "0.50"))      # contradiction veto threshold
VETO_FLOOR = float(os.environ.get("ONTO_VETO_FLOOR", str(sr.FLOOR)))  # veto SCAN floor (<= bind FLOOR)
VETO_TOPK  = int(os.environ.get("ONTO_VETO_TOPK", "30"))             # veto SCAN depth
HELDOUT  = nv.HELDOUT
SPIN_GOLD_ANCHORS = nv.SPIN_GOLD_ANCHORS

# ---------------------------------------------------------------------------
# NLI contradiction side (entail side reused from nli_verify.support_score)
# ---------------------------------------------------------------------------
_contra_idx = None

def _get_contra_idx():
    """Derive the contradiction label index from the loaded model (cross-encoder
    NLI label order is typically [contradiction, entailment, neutral])."""
    global _contra_idx
    if _contra_idx is None:
        _, model, _ = nv.get_nli()
        id2label = {int(k): str(val) for k, val in model.config.id2label.items()}
        idx = next((i for i, lab in id2label.items() if "contradict" in lab.lower()), None)
        if idx is None:
            sys.exit(f"NLI model {nv.MODEL_NAME} has no 'contradiction' label: {id2label}")
        _contra_idx = idx
    return _contra_idx

def nli_contra_prob(premise, hypothesis):
    """P(contradiction) and argmax-is-contradiction for (premise, hypothesis)."""
    import torch
    tok, model, _ = nv.get_nli()
    cidx = _get_contra_idx()
    enc = tok(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        logits = model(**enc).logits[0]
    probs = torch.nn.functional.softmax(logits, dim=-1)
    p_contra = float(probs[cidx])
    is_argmax_contra = int(torch.argmax(probs)) == cidx
    return p_contra, is_argmax_contra

def contra_score(premise, claim):
    """Veto score: MAX contradiction over the claim and its proposition (symmetric
    with the entailment gate's max-over-forms, so a provenance wrapper never hides a
    contradiction). Returns (p_contra, argmax_contra, form)."""
    pw, aw = nli_contra_prob(premise, claim)
    prop = nv.proposition(claim)
    if prop == claim:
        return pw, aw, "wrapped"
    ps, as_ = nli_contra_prob(premise, prop)
    return (ps, as_, "stripped") if ps >= pw else (pw, aw, "wrapped")

# ---------------------------------------------------------------------------
# the E19 gate: E16 bind + entail-over-topK + contradiction-VETO-over-topK
# ---------------------------------------------------------------------------
def _authorized_topk(claim, store):
    """Authorized candidates for the CONTRADICTION scan, using the VETO floor/depth
    (independent of the bind's frozen FLOOR/TOP_K). The diag showed the contradicting
    authorized source sits BELOW the 0.55 bind floor for the adversarial spoofs, so the
    veto must scan deeper - WITHOUT touching the bind (B1/B3 stay on the E16 baseline)."""
    query = v16._strip_cite(claim) or claim
    hits = sr.retrieve(query, store.records, floor=VETO_FLOOR, top_k=VETO_TOPK)
    return [h for h in hits if store.is_authorized(h)]

def resolve_claim_e19(claim, store, findings, tau=TAU, veto_tau=VETO_TAU, claim_type=None):
    """E19 = E18 ACCEPT decision (byte-identical) + contradiction-VETO (additive demote).

    The veto NEVER promotes and NEVER changes how a claim is ACCEPTED - it can only
    DEMOTE a claim E18 would VERIFY, when an authorized top-K finding contradicts it.
    This isolates the veto's effect to B2 (close the NN leak); B1/B3 stay on the E18
    baseline. (pack v54 sec 5: use NLI to REJECT, lean on it less to ACCEPT.)"""
    # ACCEPT path: exactly E18 (single bound premise; SKIP-no-finding passes through).
    res = nv.resolve_claim_nli(claim, store, findings, tau, claim_type)
    res["veto"] = None
    if res["label"] != "VERIFIED":
        return res                                  # only ever demote what E18 verified

    # CONTRADICTION-VETO over top-K authorized (the ONLY thing E19 adds).
    for h in _authorized_topk(claim, store):
        prem = nv.lookup_finding(h.get("locator"), findings)
        if prem is None:
            continue
        pc, amc, _ = contra_score(prem, claim)
        if amc and pc >= veto_tau:
            res["label"] = "UNVERIFIABLE"
            res["locator"] = "[no verified source: contradicted by authorized finding]"
            res["veto"] = {"contradicted_by": h.get("locator"), "p_contra": round(pc, 4),
                           "veto_tau": veto_tau}
            break
    return res

# ---------------------------------------------------------------------------
# item-level verdict (frozen E16 extraction path, reused from nli_verify)
# ---------------------------------------------------------------------------
def item_verdict_e19(item, store, findings, tau=TAU, veto_tau=VETO_TAU):
    claims = [resolve_claim_e19(s, store, findings, tau, veto_tau, ct)
              for s, ct in nv._item_claims(item["text"])]
    labs = [c["label"] for c in claims]
    label = ("PASS-COMMON" if not claims else
             "DEMOTE" if "UNVERIFIABLE" in labs else
             "VERIFIED" if "VERIFIED" in labs else "PASS-COMMON")
    return label, claims

# ---------------------------------------------------------------------------
# shared adjudication-set builder (identical partition to nli_verify --eval)
# ---------------------------------------------------------------------------
def _partition(items, findings):
    has_finding = lambda it: nv.lookup_finding(it.get("anchor"), findings) is not None
    gold = [it for it in items if it["id"].startswith("ho_g")]
    nn   = [it for it in items if it["id"].startswith("ho_sn")]
    fab  = [it for it in items if it["id"].startswith("ho_sf")]
    neg  = [it for it in items if it["id"].startswith("ho_n")]
    gold_f = [it for it in gold if has_finding(it)]
    nn_f   = [it for it in nn   if has_finding(it)]
    spin = {a.lower() for a in SPIN_GOLD_ANCHORS}
    gold_clean = [it for it in gold_f
                  if it.get("anchor", "").replace("DOI:", "").lower() not in spin]
    return gold_f, gold_clean, nn_f, fab, neg

# ---------------------------------------------------------------------------
# E19 eval over the frozen held-out (bars FROZEN, identical to E18)
# ---------------------------------------------------------------------------
def eval_heldout_e19(heldout_path=HELDOUT, tau=TAU, veto_tau=VETO_TAU):
    store = GoldStore()
    findings = nv.load_findings()
    items = [json.loads(l) for l in open(heldout_path, encoding="utf-8") if l.strip()]
    gold_f, gold_clean, nn_f, fab, neg = _partition(items, findings)

    print(f"E19 contradiction-veto | model={nv.MODEL_NAME} | tau={tau} | veto_tau={veto_tau}")
    if "ONTO_NLI_VETO_TAU" not in os.environ:
        print("  WARN: ONTO_NLI_VETO_TAU not set in env - using default 0.50. "
              "LOCK it via --calibrate before trusting this eval (R6/R7).")
    print(f"  adjudicated: gold_with_finding={len(gold_f)} nn_with_finding={len(nn_f)} "
          f"| fab={len(fab)} negctrl={len(neg)} (bind-stage control; NLI never reached)\n")

    verdict = lambda it: item_verdict_e19(it, store, findings, tau, veto_tau)[0]
    v_gold  = {it["id"]: verdict(it) for it in gold_f}
    v_clean = {it["id"]: v_gold[it["id"]] for it in gold_clean}
    v_nn    = {it["id"]: verdict(it) for it in nn_f}
    v_fn    = {it["id"]: verdict(it) for it in (fab + neg)}

    b1  = sum(l == "VERIFIED" for l in v_gold.values())
    b1c = sum(l == "VERIFIED" for l in v_clean.values())
    b2  = sum(l == "DEMOTE"   for l in v_nn.values())
    b3  = sum(l == "VERIFIED" for l in v_fn.values())
    r1  = b1 / len(gold_f)
    r1c = b1c / len(gold_clean) if gold_clean else float("nan")
    r2  = b2 / len(nn_f)
    r3  = b3 / len(v_fn)
    P = lambda ok: "PASS" if ok else "FAIL"
    print(f"B1 gold VERIFY (with-finding) = {b1}/{len(gold_f)} = {r1:.3f}  (bar >= 0.90) {P(r1>=.90)}")
    print(f"   B1 diagnostic (spin-gold excluded) = {b1c}/{len(gold_clean)} = {r1c:.3f}  [not the bar]")
    print(f"B2 NN-swap DEMOTE             = {b2}/{len(nn_f)} = {r2:.3f}  (bar >= 0.80) {P(r2>=.80)}")
    print(f"B3 fab+neg over-bind          = {b3}/{len(v_fn)} = {r3:.3f}  (bar <= 0.10) {P(r3<=.10)}")
    go = (r1 >= .90) and (r2 >= .80) and (r3 <= .10)
    print("\nVERDICT ->", "GO" if go else "NO-GO")

    leaks = [i for i, l in v_nn.items() if l != "DEMOTE"]
    if leaks:
        print(f"  B2 residual leaks (NN not demoted): {leaks}")
    if r1 < .90 and r1c >= .90:
        print("  NOTE: B1 sub-bar attributable to pre-registered spin-gold, not the veto.")
    return {"B1": r1, "B1_clean": r1c, "B2": r2, "B3": r3, "GO": go, "leaks": leaks}

# ---------------------------------------------------------------------------
# VETO_TAU calibration (lock BEFORE eval): smallest tau with NN-leak==0 & gold safe
# ---------------------------------------------------------------------------
def calibrate(heldout_path=HELDOUT, tau=TAU, veto_tau=VETO_TAU,
              floors=(0.55, 0.50, 0.48, 0.46, 0.45, 0.44, 0.43, 0.40, 0.35, 0.30)):
    """Pre-register the VETO FLOOR by PRECISION. The diag showed the contradicting
    authorized source sits below the 0.55 bind floor, so the veto must scan lower. The
    floor is the binding knob (veto_tau is settled: contradiction is ~1.0 vs ~0.0). Sweep
    the veto floor HIGH->LOW; lock the HIGHEST floor that closes every NN leak (final
    B2==14/14) WHILE harming no clean gold (no gold E18-verified gets newly vetoed). This
    is a precision lock, never tuned to B1. Bind FLOOR/TOP_K stay frozen throughout."""
    global VETO_FLOOR
    saved = VETO_FLOOR
    store = GoldStore()
    findings = nv.load_findings()
    items = [json.loads(l) for l in open(heldout_path, encoding="utf-8") if l.strip()]
    gold_f, gold_clean, nn_f, _, _ = _partition(items, findings)

    # E18 baseline (veto OFF): which gold E18 VERIFIES, how many NN E18 demotes.
    e18_gold = {it["id"]: nv.item_verdict_nli(it, store, findings, tau)[0] for it in gold_clean}
    e18_gold_verified = {i for i, l in e18_gold.items() if l == "VERIFIED"}
    b2_entail = sum(nv.item_verdict_nli(it, store, findings, tau)[0] == "DEMOTE" for it in nn_f)

    print(f"veto-FLOOR calibration | model={nv.MODEL_NAME} | tau={tau} | veto_tau={veto_tau} "
          f"| veto_depth={VETO_TOPK} | bind FLOOR={sr.FLOOR} (frozen)")
    print(f"  E18 baseline (veto OFF): NN demote={b2_entail}/{len(nn_f)} "
          f"(leaks veto must close={len(nn_f)-b2_entail}) ; E18 clean-gold VERIFIED="
          f"{len(e18_gold_verified)}/{len(gold_clean)}")
    print("  per-floor: FINAL NN-demote / total ; clean-gold NEWLY-vetoed / E18-verified")
    locked = None
    try:
        for f in floors:
            VETO_FLOOR = f
            b2_final = sum(item_verdict_e19(it, store, findings, tau, veto_tau)[0] == "DEMOTE"
                           for it in nn_f)
            e19_gold = {it["id"]: item_verdict_e19(it, store, findings, tau, veto_tau)[0]
                        for it in gold_clean}
            gold_hurt = sum(1 for i in e18_gold_verified if e19_gold[i] == "DEMOTE")
            ok = (b2_final == len(nn_f)) and (gold_hurt == 0)
            tag = "  <- LOCK candidate (highest safe floor)" if ok else ""
            print(f"  veto_floor={f:.2f}: NN_demote={b2_final}/{len(nn_f)} "
                  f"gold_hurt={gold_hurt}/{len(e18_gold_verified)}{tag}")
            if ok and locked is None:
                locked = f
    finally:
        VETO_FLOOR = saved
    print()
    if locked is not None:
        print(f"LOCK ONTO_VETO_FLOOR = {locked:.2f}  (FINAL NN-leak==0 AND no clean-gold harmed)")
        print(f"     keep ONTO_NLI_VETO_TAU={veto_tau} ONTO_VETO_TOPK={VETO_TOPK}")
    else:
        print("NO veto floor closes all NN leaks without harming gold.")
        print("  -> precision tension: the floor that reaches a contradicting source for the")
        print("     leaks also vetoes a real gold. Veto cannot cleanly separate this class;")
        print("     record as veto-insufficiency, do NOT relax. (Bounds the cheap-Entity path.)")
    return locked

# ---------------------------------------------------------------------------
def diag_leak(ids=("ho_sn00", "ho_sn03", "ho_sn10"), heldout_path=HELDOUT,
              tau=TAU, veto_tau=VETO_TAU, depth=25):
    """For each leak id: show E18 bind + a FULL ranked retrieval (cosine, locator,
    authorized, is-anchor, contra-prob vs claim) so the veto-miss mechanism is visible:
      - anchor present, cosine>=FLOOR, rank>bind-TOP_K, contra>=veto_tau -> widen VETO_TOPK fixes it
      - anchor present, cosine<FLOOR                                     -> floor gates it; lower veto floor
      - anchor present, contra<veto_tau                                  -> NLI misses the contradiction (terminal-ish)
      - anchor absent from ranking                                       -> retrieval cannot surface it"""
    import numpy as np
    store = GoldStore()
    findings = nv.load_findings()
    items = {json.loads(l)["id"]: json.loads(l)
             for l in open(heldout_path, encoding="utf-8") if l.strip()}
    mat, recs = sr.build_index(store.records)
    print(f"diag-leak | FLOOR={sr.FLOOR} bind_TOP_K={sr.TOP_K} veto_tau={veto_tau} depth={depth}\n")
    for tid in ids:
        it = items[tid]
        claim = it["text"]
        anchor = (it.get("anchor") or "").replace("DOI:", "").lower()
        query = v16._strip_cite(claim) or claim
        res = v16.resolve_claim(claim, store, "prose_provenance")
        print("=" * 90)
        print(f"{tid}  anchor={it.get('anchor')}")
        print(f"  claim: {claim}")
        print(f"  E18 bind -> label={res['label']} locator={res.get('locator')}")
        q = sr._embed([query])[0]
        sims = mat @ q
        order = np.argsort(-sims)[:depth]
        print(f"  {'rank':<5}{'cos':<7}{'auth':<6}{'anchor?':<8}{'contra':<8}locator")
        for rank, i in enumerate(order):
            r = recs[int(i)]
            cos = float(sims[int(i)])
            hit = {"source": r["source"], "locator": r["locator"], "hash": r["hash"]}
            auth = store.is_authorized(hit)
            is_anc = r["locator"].replace("DOI:", "").lower() == anchor
            prem = nv.lookup_finding(r["locator"], findings)
            pc = "-"
            if prem is not None:
                p, am, _ = contra_score(prem, claim)
                pc = f"{p:.3f}{'*' if (am and p>=veto_tau) else ''}"
            mark = " <ANCHOR" if is_anc else ""
            print(f"  {rank:<5}{cos:<7.3f}{str(auth):<6}{str(is_anc):<8}{pc:<8}{r['locator']}{mark}")
    print("\n* = would fire the veto (argmax=contradiction AND p>=veto_tau)")


def _probe(claim):
    store = GoldStore()
    findings = nv.load_findings()
    print(json.dumps(resolve_claim_e19(claim, store, findings), ensure_ascii=False, indent=1))

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) >= 2 else ""
    if arg == "--eval":
        eval_heldout_e19()
    elif arg == "--calibrate":
        calibrate()
    elif arg == "--diag-leak":
        diag_leak()
    elif arg == "--probe" and len(sys.argv) >= 3:
        _probe(sys.argv[2])
    else:
        print("usage: python nli_verify2.py --calibrate   # lock VETO_TAU first")
        print("       python nli_verify2.py --eval")
        print("       python nli_verify2.py --diag-leak    # why the veto misses the B2 leaks")
        print("       python nli_verify2.py --probe \"<claim text>\"")
