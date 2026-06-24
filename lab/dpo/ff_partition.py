import json, collections
def load(p):
    d={}
    for l in open(p,encoding="utf-8"):
        l=l.strip()
        if not l: continue
        o=json.loads(l); d[o["id"]]=o
    return d
V=load("heldout_verdicts_20260625.jsonl")
L=load("sealed_labels_heldout_20260625.jsonl")
vi,li=set(V),set(L)
print("verdicts:",len(vi)," labels:",len(li))
print("only_in_verdicts:",sorted(vi-li))
print("only_in_labels:",sorted(li-vi))
assert vi==li,"ID MISMATCH"
conf=collections.defaultdict(list)
for i in sorted(vi):
    fl=L[i]["founder_label"]; sv=V[i]["temporal"]["scope"]["verdict"]
    conf[(fl,sv)].append(i)
print("\n=== CONFUSION founder_label x scope.verdict ===")
for fl in ["CLEAN","DIRTY"]:
    for sv in ["CLEAN","DIRTY","ABSTAIN"]:
        ids=conf.get((fl,sv),[]); print("%-5s x %-8s = %2d  %s"%(fl,sv,len(ids),ids))
print("\n=== PER-CLAIM STRUCT ===")
for i in sorted(vi):
    t=V[i]["temporal"]; sc=t["scope"]
    print("%-11s GT=%-5s dc=%-9s | sv=%-8s | yc=%-26s | snip=%-5s | pspec=%-22s | pyear=%-18s | r=%s"%(
        i, L[i]["founder_label"], str(L[i]["dirty_class"]), sc["verdict"], str(t.get("year_collapse")),
        bool(t.get("snippets")), str(t.get("per_specific",{})), str(t.get("per_year",{})), sc.get("reasons")))
