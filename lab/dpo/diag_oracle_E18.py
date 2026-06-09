#!/usr/bin/env python3
"""diag_oracle_E18.py - NLI CEILING diagnostic (NOT a bar, R7).

v2: oracle premise = OWN-anchor finding (retrieval bypassed) AND tests two hypothesis
forms to isolate a measurement confound the v1 oracle exposed:
  WRAPPED  = held-out text verbatim ("A paper argued that <proposition>")
  STRIPPED = proposition only (provenance frame removed)
Rationale: the bind stage already establishes "a source exists"; the NLI stage should
test the CLAIM PROPOSITION against the source finding, not re-litigate provenance. NLI
does not entail "a paper argued X" from a bare statement of X -> wrapped under-fires on
faithful paraphrase. Stripping is an instrument correction (analogous to held-out v1->v2),
NOT tuning: pass bar stays B1>=0.90 / B2>=0.80, and B2 is re-checked under STRIPPED to
confirm spoofs still demote (a false proposition still contradicts the finding).

Run with `python`. CPU. Env: KMP_DUPLICATE_LIB_OK=TRUE ; ONTO_NLI_MODEL (optional).
"""
import json, re
import nli_verify as nv

HELD = nv.HELDOUT
TAU = 0.50

def main():
    findings = nv.load_findings()
    items = [json.loads(l) for l in open(HELD, encoding="utf-8") if l.strip()]
    gold = [it for it in items if it["id"].startswith("ho_g")]
    nn   = [it for it in items if it["id"].startswith("ho_sn")]

    print(f"oracle NLI ceiling v3 | model={nv.MODEL_NAME} | tau={TAU} | premise=OWN-anchor finding")
    print("gate = max(P(finding,claim), P(finding,proposition))  [same gate as nli_verify --eval]\n")

    def run(group):
        out = []
        for it in group:
            prem = nv.lookup_finding(it.get("anchor"), findings)
            if prem is None:
                continue
            p, am, form = nv.support_score(prem, it["text"])
            out.append((it["id"], p, (am and p >= TAU), form, it.get("anchor")))
        return out

    g = run(gold); n = run(nn)
    b1 = sum(r[2] for r in g); b2 = sum(not r[2] for r in n)
    print(f"B1_oracle gold VERIFY  = {b1}/{len(g)} = {b1/len(g):.3f}  (target >= 0.90)")
    print(f"B2_oracle NN   DEMOTE  = {b2}/{len(n)} = {b2/len(n):.3f}  (target >= 0.80)\n")

    print("[gold]  id / P / verdict / form")
    for i, p, v, f, a in g:
        print(f"  {i:<9} {p:.3f}  {'VERIFY' if v else 'DEMOTE'}  {f}")
    print("\n[NN]    id / P / verdict")
    for i, p, v, f, a in n:
        print(f"  {i:<9} {p:.3f}  {'VERIFY(LEAK)' if v else 'DEMOTE'}")

    resid = [(i, p, a) for i, p, v, f, a in g if not v]
    print("\n[residual gold failing under ORACLE = premise-specificity or held-out defect, NOT NLI]")
    for i, p, a in resid:
        print(f"  {i}  P={p:.3f}  anchor={a}")
    if not resid:
        print("  none.")

if __name__ == "__main__":
    main()
