#!/usr/bin/env python3
"""nli_verify.py - E18 claim-support layer ABOVE the frozen E16 bind.

WRAPS (never mutates) verify_E16.resolve_claim. A claim that E16 binds to an
AUTHORIZED hit is VERIFIED only if the bound source's FINDING entails the claim:

    VERIFY  iff  E16 label == VERIFIED
                 AND argmax NLI(premise=hit.finding, hypothesis=claim) == ENTAILMENT
                 AND P(entail) >= tau
    else DEMOTE  (label downgraded to UNVERIFIABLE).

This is NLI-as-SECONDARY on an already-bound passage (keystone sec 4), the precise
gap E17 exposed: a faithful gold finding and an on-topic over-claim are equidistant
from the source embedding (bindability cannot split them); only claim-support can.

Premise = `finding` from the enriched fixture (gold_fixture_E18.json). Anchors with
no grounded finding (R4 no-source) are SKIPPED by NLI (excluded from the bars),
never silently passed as VERIFIED.

FROZEN: verify_E16 / gold_retrieve / semantic_retrieve are imported byte-identical.
NLI model loaded via transformers DIRECTLY (torch-first; faulthandler already enabled
by importing semantic_retrieve) to avoid the sentence_transformers->datasets->pyarrow
SEH on the Windows box - the same proven import discipline as semantic_retrieve.

Env (load-bearing): KMP_DUPLICATE_LIB_OK=TRUE ; ONTO_NLI_TAU (decision threshold,
locked by sanity_E18 BEFORE eval) ; ONTO_NLI_MODEL (override, default below).
Run with `python` (Windows: not python3). CPU.

Usage:
  python nli_verify.py --eval            # E18 bars over frozen heldout_E17.jsonl
  python nli_verify.py --probe "<claim>" # single-claim trace (bind + entailment)
"""
import json, os, re, sys

import semantic_retrieve as sr            # enables faulthandler; torch-first path
from gold_retrieve import GoldStore
import verify_E16 as v16

# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE_E18 = os.path.join(_HERE, "eval", "_local", "gold_fixture_E18.json")
HELDOUT     = os.path.join(_HERE, "eval", "_local", "heldout_E17.jsonl")
TAU         = float(os.environ.get("ONTO_NLI_TAU", "0.50"))   # locked by sanity_E18
MODEL_NAME  = os.environ.get("ONTO_NLI_MODEL", "cross-encoder/nli-deberta-v3-small")
# fallback if the deberta-v3 (sentencepiece) tokenizer chokes on the box:
#   $env:ONTO_NLI_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"   (BERT wordpiece, no sentencepiece)

# held-out gold whose FROZEN claim is framed beyond its source (pre-registered
# known limitation, R15) - reported as a B1 diagnostic, never tuned away.
SPIN_GOLD_ANCHORS = {
    "10.1038/s41586-023-06288-x",   # held-out "no new genes" vs source = fitness recovery
    "10.1073/pnas.2321592121",      # held-out "~91% / never self-replication" (91% not in finding)
}

# ---------------------------------------------------------------------------
# findings (premise) loader
# ---------------------------------------------------------------------------
def load_findings(path=FIXTURE_E18):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"E18 fixture missing at {path}. It is LOCAL-ONLY (eval/_local, gitignored)."
        )
    data = json.load(open(path, encoding="utf-8"))
    by_loc, by_doi = {}, {}
    for r in data["records"]:
        f = r.get("finding")
        if not f:
            continue
        loc = r.get("locator", "")
        by_loc[loc] = (f, r.get("finding_provenance", "?"))
        by_doi[loc.replace("DOI:", "").lower()] = (f, r.get("finding_provenance", "?"))
    return by_loc, by_doi

def lookup_finding(locator, findings):
    by_loc, by_doi = findings
    if locator in by_loc:
        return by_loc[locator][0]
    return (by_doi.get((locator or "").replace("DOI:", "").lower()) or (None,))[0]

# ---------------------------------------------------------------------------
# NLI cross-encoder (transformers directly; torch-first; SEH-safe)
# ---------------------------------------------------------------------------
_nli = None   # (tok, model, entail_idx)

def get_nli():
    global _nli
    if _nli is None:
        import torch  # noqa: F401  (torch first, as in the proven semantic_retrieve path)
        try:
            import pyarrow  # noqa: F401  (recoverable SEH under faulthandler; then reused)
        except Exception:
            pass
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model.eval()
        id2label = {int(k): str(val) for k, val in model.config.id2label.items()}
        entail_idx = next((i for i, lab in id2label.items() if "entail" in lab.lower()), None)
        if entail_idx is None:
            sys.exit(f"NLI model {MODEL_NAME} has no 'entailment' label: {id2label}")
        _nli = (tok, model, entail_idx)
    return _nli

def nli_entail_prob(premise, hypothesis):
    """P(entailment) and argmax-is-entail for (premise, hypothesis)."""
    import torch
    tok, model, eidx = get_nli()
    enc = tok(premise, hypothesis, return_tensors="pt",
              truncation=True, max_length=256)
    with torch.no_grad():
        logits = model(**enc).logits[0]
    probs = torch.nn.functional.softmax(logits, dim=-1)
    p_entail = float(probs[eidx])
    is_argmax_entail = int(torch.argmax(probs)) == eidx
    return p_entail, is_argmax_entail

# --- proposition extraction (instrument fix, validated by diag_oracle_E18) ----------
# The bind stage already establishes "a source exists"; the NLI stage must test the
# claim PROPOSITION against the finding, not re-litigate the provenance wrapper.
# NLI does not entail "a paper argued X" from a bare statement of X -> wrapped form
# under-fires on faithful paraphrase (diag: B1_oracle 0.41 wrapped -> 0.74 stripped).
# Two cuts: (1) "<subject> <verb> that/how <prop>" -> strip through that/how;
#           (2) "<subject NP> <content-verb> <obj>" (no that) -> strip SUBJECT, keep verb
#               (else "challenged X"/"introduced Y" collapse to a verbless fragment).
# The GATE takes max(P(finding,claim), P(finding,proposition)) so an over-strip never
# lowers a score, and spoofs (both forms ~0, contradiction) never leak.
_PROV_VERB = (r"(reported|found|showed|shown|demonstrated|proved|proven|established|"
              r"concluded|argued|characteri[sz]ed|defined|distinguished|attributed|"
              r"suggested|estimated|calculated|described|posed|provided|set out|"
              r"determined|introduced|challenged|formali[sz]ed)")
_SUBJ_NOUN = (r"(study|studies|paper|papers|trial|research|researchers|survey|"
              r"meta-analysis|analysis|work|team|scientists?|academies study|model|"
              r"review|calculation|report|result|experiment|theory)")
_FRAME_THAT = re.compile(r"^\s*(according to[^,]*,\s*)?(a|an|the)\s+[^.,]*?\b"
                         + _PROV_VERB + r"\b\s+(that|how)\s+", re.I)
_FRAME_SUBJ = re.compile(r"^\s*(according to[^,]*,\s*)?(a|an|the)\s+([\w-]+\s+){0,4}?\b"
                         + _SUBJ_NOUN + r"\b\s+", re.I)

def proposition(claim):
    m = _FRAME_THAT.match(claim)
    rest = claim[m.end():] if (m and m.end() < len(claim)) else None
    if rest is None:
        m2 = _FRAME_SUBJ.match(claim)
        rest = claim[m2.end():] if (m2 and m2.end() < len(claim)) else None
    if rest:
        rest = rest.strip()
        return (rest[0].upper() + rest[1:]) if rest else claim
    return claim

def support_score(premise, claim):
    """Gate score: max entail over the claim and its proposition. Returns (p, argmaxE, form)."""
    pw, aw = nli_entail_prob(premise, claim)
    prop = proposition(claim)
    if prop == claim:
        return pw, aw, "wrapped"
    ps, as_ = nli_entail_prob(premise, prop)
    return (ps, as_, "stripped") if ps >= pw else (pw, aw, "wrapped")

# ---------------------------------------------------------------------------
# the wrap: E16 resolve_claim + entailment gate
# ---------------------------------------------------------------------------
def resolve_claim_nli(claim, store, findings, tau=TAU, claim_type=None):
    res = v16.resolve_claim(claim, store, claim_type)
    res["nli"] = None
    if res["label"] != "VERIFIED":
        return res                                  # no-bind / pass-common untouched
    premise = lookup_finding(res.get("locator"), findings)
    if premise is None:
        res["nli"] = "SKIP-no-finding"              # nulled anchor: excluded from bars
        return res
    p_entail, argmax_entail, form = support_score(premise, claim)
    res["nli"] = {"p_entail": round(p_entail, 4), "argmax_entail": argmax_entail,
                  "form": form, "tau": tau, "premise": premise[:70]}
    if not (argmax_entail and p_entail >= tau):
        res["label"] = "UNVERIFIABLE"
        res["locator"] = "[no verified source: claim not entailed by bound finding]"
    return res

def _item_claims(text):
    """Frozen E16 extraction path for one held-out item."""
    out, seen = [], set()
    for s in v16.segment(text):
        if v16.is_qa_scaffold(s):
            continue
        n = v16._norm(s)
        if n in seen:
            continue
        seen.add(n)
        ct, ok = v16.classify(s)
        if ok:
            out.append((s, ct))
    return out

def item_verdict_nli(item, store, findings, tau=TAU):
    claims = [resolve_claim_nli(s, store, findings, tau, ct) for s, ct in _item_claims(item["text"])]
    labs = [c["label"] for c in claims]
    skipped = any(c.get("nli") == "SKIP-no-finding" for c in claims)
    label = ("PASS-COMMON" if not claims else
             "DEMOTE" if "UNVERIFIABLE" in labs else
             "VERIFIED" if "VERIFIED" in labs else "PASS-COMMON")
    return label, claims, skipped

# ---------------------------------------------------------------------------
# E18 eval over the frozen held-out
# ---------------------------------------------------------------------------
def eval_heldout_nli(heldout_path=HELDOUT, tau=TAU):
    store = GoldStore()
    findings = load_findings()
    items = [json.loads(l) for l in open(heldout_path, encoding="utf-8") if l.strip()]

    by_loc, _ = findings
    has_finding = lambda it: lookup_finding(it.get("anchor"), findings) is not None

    gold = [it for it in items if it["id"].startswith("ho_g")]
    nn   = [it for it in items if it["id"].startswith("ho_sn")]
    fab  = [it for it in items if it["id"].startswith("ho_sf")]
    neg  = [it for it in items if it["id"].startswith("ho_n")]

    gold_f = [it for it in gold if has_finding(it)]            # B1 set (27)
    nn_f   = [it for it in nn   if has_finding(it)]            # B2 set (14)
    gold_clean = [it for it in gold_f if (it.get("anchor","").replace("DOI:","").lower()
                  not in {a.lower() for a in SPIN_GOLD_ANCHORS})]   # B1 diagnostic

    print(f"E18 NLI gate | model={MODEL_NAME} | tau={tau}")
    print(f"  adjudicated: gold_with_finding={len(gold_f)}/{len(gold)} "
          f"nn_with_finding={len(nn_f)}/{len(nn)} | nulled excluded")
    print(f"  fab={len(fab)} negctrl={len(neg)} (bind-stage control; NLI never reached)\n")

    def verdict(it):
        return item_verdict_nli(it, store, findings, tau)[0]

    v_gold   = {it["id"]: verdict(it) for it in gold_f}
    v_clean  = {it["id"]: v_gold[it["id"]] for it in gold_clean}
    v_nn     = {it["id"]: verdict(it) for it in nn_f}
    v_fabneg = {it["id"]: verdict(it) for it in (fab + neg)}

    b1  = sum(l == "VERIFIED" for l in v_gold.values())
    b1c = sum(l == "VERIFIED" for l in v_clean.values())
    b2  = sum(l == "DEMOTE"   for l in v_nn.values())
    b3  = sum(l == "VERIFIED" for l in v_fabneg.values())

    r1, r1c = b1/len(gold_f), (b1c/len(gold_clean) if gold_clean else float("nan"))
    r2  = b2/len(nn_f)
    r3  = b3/len(v_fabneg)
    P = lambda ok: "PASS" if ok else "FAIL"
    print(f"B1 gold VERIFY (with-finding) = {b1}/{len(gold_f)} = {r1:.3f}  (bar >= 0.90) {P(r1>=.90)}")
    print(f"   B1 diagnostic (spin-gold excluded) = {b1c}/{len(gold_clean)} = {r1c:.3f}  [not the bar]")
    print(f"B2 NN-swap DEMOTE             = {b2}/{len(nn_f)} = {r2:.3f}  (bar >= 0.80) {P(r2>=.80)}")
    print(f"B3 fab+neg over-bind          = {b3}/{len(v_fabneg)} = {r3:.3f}  (bar <= 0.10) {P(r3<=.10)}")
    go = (r1 >= .90) and (r2 >= .80) and (r3 <= .10)
    print("\nVERDICT ->", "GO" if go else "NO-GO")

    spin_fail = [i for i in v_gold if v_gold[i] != "VERIFIED"
                 and i not in v_clean]
    if r1 < .90 and r1c >= .90:
        print("  NOTE: B1 sub-bar is attributable to pre-registered spin-gold "
              "(held-out v3 issue), NOT NLI failure. Clean-gold B1 clears.")
    return {"B1": r1, "B1_clean": r1c, "B2": r2, "B3": r3, "GO": go}

# ---------------------------------------------------------------------------
def _probe(claim):
    store = GoldStore()
    findings = load_findings()
    r = resolve_claim_nli(claim, store, findings)
    print(json.dumps(r, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--eval":
        eval_heldout_nli()
    elif len(sys.argv) >= 2 and sys.argv[1] == "--probe":
        _probe(sys.argv[2])
    else:
        print("usage: python nli_verify.py --eval")
        print("       python nli_verify.py --probe \"<claim text>\"")
