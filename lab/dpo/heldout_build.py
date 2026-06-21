#!/usr/bin/env python3
# heldout_build.py -- split labeled held-out into blind claims + sealed labels, retrieve evidence.
# Input: heldout_labeled.jsonl {id, topic, claim, founder_label, dirty_class?}
# Out:   claims_blind_ev.jsonl {id, topic, claim, evidence}   (NO labels -> fresh-chat auditor)
#        sealed_labels.jsonl    {id, label, dirty_class}        (-> score-2b)
# stdlib only. Run on the box with internet.
import json, sys, urllib.parse, urllib.request, re, time

def read_jsonl(p): return [json.loads(l) for l in open(p,encoding="utf-8") if l.strip()]
def _inv(idx):
    if not idx: return ""
    pos={}
    for w,ls in idx.items():
        for l in ls: pos[l]=w
    return " ".join(pos[i] for i in sorted(pos))
def _get(u,t=20):
    r=urllib.request.Request(u,headers={"User-Agent":"onto-heldout/0 (mailto:onto@local)"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8"))
def retrieve(claim):
    q=urllib.parse.quote(claim[:300])
    try:
        d=_get(f"https://api.openalex.org/works?search={q}&per-page=1&mailto=onto@local")
        r=(d.get("results") or [])
        if r:
            t=r[0].get("display_name") or ""; ab=_inv(r[0].get("abstract_inverted_index"))
            if t or ab: return {"title":t,"abstract":ab,"via":"openalex"}
    except Exception: pass
    try:
        d=_get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=1")
        it=d.get("message",{}).get("items") or []
        if it:
            t=(it[0].get("title") or [""])[0]; ab=re.sub("<[^>]+>","",it[0].get("abstract","") or "")
            if t or ab: return {"title":t,"abstract":ab,"via":"crossref"}
    except Exception: pass
    return {"title":"","abstract":"","via":"none"}

rows=read_jsonl("heldout_labeled.jsonl")
nc=sum(1 for r in rows if str(r.get("founder_label")).upper()=="CLEAN")
if nc<10: sys.exit(f"ABORT: only {nc} CLEAN (<10).")
cf=open("claims_blind_ev.jsonl","w",encoding="utf-8")
lf=open("sealed_labels.jsonl","w",encoding="utf-8")
via={}
for r in rows:
    lab=str(r["founder_label"]).upper()
    if lab=="DIRTY" and r.get("dirty_class") not in ("specifics","other"):
        sys.exit(f"ABORT: {r['id']} DIRTY without dirty_class")
    ev=retrieve(r["claim"]); via[ev["via"]]=via.get(ev["via"],0)+1; time.sleep(0.3)
    cf.write(json.dumps({"id":r["id"],"topic":r.get("topic"),"claim":r["claim"],"evidence":ev},ensure_ascii=False)+"\n")
    lf.write(json.dumps({"id":r["id"],"label":lab,"dirty_class":r.get("dirty_class")},ensure_ascii=False)+"\n")
cf.close(); lf.close()
print(f"[done] {len(rows)} rows  CLEAN={nc}  via={via}")
print("claims_blind_ev.jsonl -> paste into a NEW chat for blind B0/B1' judging")
print("sealed_labels.jsonl   -> keep for score-2b")
