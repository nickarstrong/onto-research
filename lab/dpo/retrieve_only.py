#!/usr/bin/env python3
# retrieve_only.py -- add evidence to the BLIND claims (heldout_raw.jsonl, no labels on disk).
# Out: claims_blind_ev.jsonl {id, topic, claim, evidence}. stdlib only; needs internet.
import json, urllib.parse, urllib.request, re, time
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
rows=[json.loads(l) for l in open("heldout_raw.jsonl",encoding="utf-8") if l.strip()]
via={}
with open("claims_blind_ev.jsonl","w",encoding="utf-8") as f:
    for r in rows:
        ev=retrieve(r["claim"]); via[ev["via"]]=via.get(ev["via"],0)+1; time.sleep(0.3)
        f.write(json.dumps({"id":r["id"],"topic":r.get("topic"),"claim":r["claim"],"evidence":ev},ensure_ascii=False)+"\n")
print(f"[done] {len(rows)} claims  via={via} -> claims_blind_ev.jsonl")
