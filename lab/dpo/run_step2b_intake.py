#!/usr/bin/env python3
# run_step2b_intake.py
# SPEC sec9 step2b -- LIVE intake: a NEW (claim, source-DOI) -> organ readout (n_con,n_ent,S_size)
#   -> frozen tier chain (tier_of_live -> final_tier). REUSES the frozen emit path; reimplements nothing.
#
# Frozen reuse (no copy):
#   L1/L2  provenance : run_provenance_L1L2.verdict(doi, expected_title, fetch, rwd_index)
#   organ  con/ent    : run_E37_probe.precompute_item + emit_E37_readout.representative
#                       (DeBERTa-v3-large-mnli ; ONTO_RETRIEVE_FLOOR=0.45 via run_E37 module setup ;
#                        con/ent over the bound subset S ; con_idx/ent_idx from id2label, never hardcoded)
#   tier   L4+ladder  : wire_provenance_L4.tier_of_live ; wire_tier.final_tier
#
# ARCHITECTURE (forced by the frozen organ, not a free choice):
#   The frozen L4 organ binds a claim against the GOLD store (store.records + manifest hash-gate), retrieving
#   representative S by cosine. It has NO path to bind against an arbitrary external DOI's text. Therefore:
#     - the source-DOI rides the PROVENANCE lane (L1/L2 -> resolve/retraction) ; axis P (SPEC sec1).
#     - L4 content-bind asks "does GOLD-consensus contradict this claim" over the retrieved authorized S ; axis G.
#   Binding the claim against the cited DOI's own text = a DIFFERENT organ (new substrate) -> out of step2b scope.
#
# GATE-BEFORE-MODEL (SPEC sec4): T4 provenance -> NLI is NEVER run (model cannot rescue a failed marker).
# CEILING (D3): l5_corroborated stays False in production -> T0 unreachable -> ceiling T1 (by design).
#
# Modes:
#   --selftest                          : mock organ ; exercises REAL L1/L2 + REAL tier chain. No torch, no GOLD.
#   --run --claim C --doi D --title T --rwd RWD.csv [--fixture F] [--grade G]
#                                       : live. GPU + GOLD fixture. PRE-RUN: anchor guard (emit_E37 fa 0.0333).
#
# Self-discipline: an all-reject wiring passes a reject-only selftest (E23 VOID-by-construction). The selftest
#   carries BOTH a T4 reject AND a T1 clean-bind accept-to-ceiling ; path collapse = FAIL.

import argparse, sys

# light tier chain only (no torch): wire_tier -> wire_provenance_L4 -> run_E39_probe, all pure-python.
from wire_tier import final_tier
from wire_provenance_L4 import tier_of_live

# frozen op-point for the bound-subset extractor is owned by emit_E37_readout.representative (reused at --run).

# --------------------------------------------------------------- heavy organ (lazy ; --run only)
_ORGAN = None  # (e37, representative, store, mat, recs, finding_by_source)

def _load_organ(fixture):
    """Lazy-load the frozen emit path + GOLD substrate. Imports torch/transformers via run_E37_probe FIRST,
    which sets ONTO_RETRIEVE_FLOOR=0.45 BEFORE semantic_retrieve import (env-wart ; default 0.55 = footgun)."""
    global _ORGAN
    if _ORGAN is None:
        import json
        import run_E37_probe as e37                    # FIRST -> FLOOR=0.45, torch, NLI, frozen substrate
        from emit_E37_readout import representative     # frozen (n_con,n_ent,S_size) extractor @ frozen op
        store = e37.gr.GoldStore(fixture)
        mat, recs = e37.sem.build_index(store.records)
        raw = json.load(open(fixture, encoding="utf-8"))
        fbs = {r["source"]: str(r.get("finding", "") or "").strip() for r in raw["records"]}
        _ORGAN = (e37, representative, store, mat, recs, fbs)
    return _ORGAN


def organ_readout(claim, fixture):
    """LIVE: (claim) -> (n_con, n_ent, S_size, pre_demoted_noauth) via the frozen organ over the GOLD store."""
    e37, representative, store, mat, recs, fbs = _load_organ(fixture)
    item = {"text": claim, "id": "live", "class": "live"}     # id/class feed only the throwaway diag
    res = e37.precompute_item(item, store, mat, recs, [], [], fbs, [])
    pre_demoted = (e37.item_label_at_C(res, float("inf"), 0.0, "any") == "DEMOTE")  # noauth channel
    rep = representative(res)
    n_con, n_ent, S_size = rep if rep else (0, 0, 0)
    return int(n_con), int(n_ent), int(S_size), bool(pre_demoted)


# --------------------------------------------------------------- live verdict
def verdict_live(claim, doi, expected_title, fetch, rwd_index, fixture, grade=None):
    """Full step2b: L1/L2 gate-before-model -> organ (only on survivors) -> tier chain."""
    import run_provenance_L1L2 as l12
    prov, prov_detail = l12.verdict(doi, expected_title, fetch, rwd_index)
    if prov.startswith("T4"):
        # GATE-BEFORE-MODEL: failed/fabricated/retracted marker -> NLI never runs.
        tier = final_tier(prov, 0, 0, 0, grade, l5_corroborated=False, has_marker=True)
        return {"doi": doi, "prov": prov, "nli_run": False,
                "n_con": None, "n_ent": None, "S_size": None,
                "l4": "T4", "tier": tier, "prov_detail": prov_detail}
    # L1L2_PASS -> run the organ
    n_con, n_ent, S_size, _pre = organ_readout(claim, fixture)
    l4 = tier_of_live(prov, n_con, n_ent, S_size)
    tier = final_tier(prov, n_con, n_ent, S_size, grade, l5_corroborated=False, has_marker=True)
    return {"doi": doi, "prov": prov, "nli_run": True,
            "n_con": n_con, "n_ent": n_ent, "S_size": S_size,
            "l4": l4, "tier": tier, "prov_detail": prov_detail}


# --------------------------------------------------------------- selftest (no torch, no GOLD)
def selftest():
    """REAL L1/L2 + REAL tier chain ; organ mocked. Proves the WIRING contract, not the organ
    (organ fidelity = the GPU anchor guard, fa 0.0333). Both reject (T4) and accept-to-ceiling (T1) present."""
    EXP = "A primitive Late Pliocene cheetah and evolution of the cheetah lineage"
    MOCK = {
        "10.1073/pnas.0810435106":  {"resolved": True,  "title": "RETRACTED: A primitive Late Pliocene cheetah and evolution of the cheetah lineage"},
        "10.9999/fake":             {"resolved": False, "title": None},
        "10.1073/pnas.0810435106c": {"resolved": True,  "title": "A primitive Late Pliocene cheetah and evolution of the cheetah lineage"},
    }
    rwd = {"10.1073/pnas.0810435106"}
    def fetch(doi): return MOCK.get(doi, {"resolved": False, "title": None})

    organ_cases = {}                                   # claim -> (n_con,n_ent,S_size,pre)
    def mock_organ(claim, fixture):                    # noqa: ARG001
        return organ_cases[claim]
    globals()["organ_readout"] = mock_organ            # verdict_live resolves organ_readout at call time

    # (label, claim, doi, title, grade, organ(nc,ne,S,pre), want_nli, want_l4, want_tier)
    cases = [
        ("retracted -> T4 no NLI",        "c_retr",  "10.1073/pnas.0810435106",  EXP, "rct",
         (0, 0, 0, False), False, "T4",                   "T4"),
        ("nonresolve -> T4 no NLI",       "c_fake",  "10.9999/fake",             EXP, "rct",
         (0, 0, 0, False), False, "T4",                   "T4"),
        ("clean+bind-holds -> T1 ceiling","c_hold",  "10.1073/pnas.0810435106c", EXP, "observational",
         (0, 3, 4, False), True,  "T0_ELIGIBLE",          "T1"),   # D=-0.75 holds ; L5 absent -> ceiling
        ("clean+contradicted -> T1",      "c_con",   "10.1073/pnas.0810435106c", EXP, "rct",
         (4, 0, 4, False), True,  "T1_BIND_CONTRADICTED",  "T1"),  # D=1.0
        ("clean+empty S -> T1 unchecked", "c_empty", "10.1073/pnas.0810435106c", EXP, "rct",
         (0, 0, 0, True),  True,  "T1_BIND_UNCHECKED",     "T1"),
    ]
    allok = True
    for lbl, claim, doi, title, grade, organ, want_nli, want_l4, want_tier in cases:
        organ_cases[claim] = organ
        r = verdict_live(claim, doi, title, fetch, rwd, "MOCK_FIXTURE", grade)
        ok = (r["nli_run"] == want_nli) and (r["l4"] == want_l4) and (r["tier"] == want_tier)
        allok &= ok
        print(f"  {'ok ' if ok else 'XX '} {lbl:33} prov={r['prov']:14} nli={int(r['nli_run'])} "
              f"l4={r['l4']:22} tier={r['tier']:3} want={want_tier}")
    assert allok, "step2b wiring mismatch"
    tiers = {verdict_live(c[1], c[2], c[3], fetch, rwd, "MOCK", c[4])["tier"] for c in cases}
    assert "T4" in tiers and "T1" in tiers, "path collapse (E23 VOID-by-construction)"
    print("\nSELFTEST: PASS (gate-before-model + tier chain sound ; T4 reject + T1 ceiling both reached)")
    print("NOTE: organ fidelity (fa 0.0333) is validated ONLY by the GPU anchor guard, not here.")


# --------------------------------------------------------------- cli
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true", help="live intake (GPU + GOLD fixture). Run anchor guard FIRST.")
    ap.add_argument("--claim")
    ap.add_argument("--doi")
    ap.add_argument("--title", help="expected title for L1 metadata match")
    ap.add_argument("--grade", default=None, help="AXIS-G grade (rct/observational/preprint/id_venue/...)")
    ap.add_argument("--rwd", help="Retraction Watch CSV")
    ap.add_argument("--fixture", default="eval/_local/gold_fixture_E25b.json")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.run:
        if not (a.claim and a.doi and a.title and a.rwd):
            sys.exit("--run requires --claim --doi --title --rwd")
        import urllib.request, urllib.error, json, time
        import run_provenance_L1L2 as l12
        rwd_index = l12.load_rwd_index(a.rwd)
        def fetch(doi):
            url = "https://api.crossref.org/works/" + urllib.request.quote(doi)
            req = urllib.request.Request(url, headers={"User-Agent": "ONTO-step2b/1.0 (mailto:council@ontostandard.org)"})
            try:
                with urllib.request.urlopen(req, timeout=30) as rsp:
                    m = json.loads(rsp.read().decode())["message"]
                return {"resolved": True, "title": " ".join(m.get("title", []) or [])}
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return {"resolved": False, "title": None}
                raise
            finally:
                time.sleep(0.3)
        r = verdict_live(a.claim, a.doi, a.title, fetch, rwd_index, a.fixture, a.grade)
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        ap.print_help()
