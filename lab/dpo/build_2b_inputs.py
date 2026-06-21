#!/usr/bin/env python3
# build_2b_inputs.py -- assemble LEVERAGE PROBE 2b inputs.
# Merge 7 CLEAN (from recut_labeled.jsonl) + 33 DIRTY+dirty_class (from qwen file) by id,
# retrieve evidence per claim (OpenAlex -> Crossref fallback), split into:
#   - claims_blind.jsonl : {id, topic, claim, evidence}        (NO labels -> auditor)
#   - sealed_labels.jsonl: {id, founder_label, dirty_class}    (Founder -> scorer)
# Prints AGGREGATES only. Never dumps per-claim label+claim together (blinding).
# stdlib only (urllib). Run on Tommy's box (needs internet for retrieve).

import argparse, json, sys, urllib.parse, urllib.request, time, re

def read_jsonl(p):
    out=[]
    for ln in open(p, encoding="utf-8"):
        ln=ln.strip()
        if ln: out.append(json.loads(ln))
    return out

def _abstract_from_inverted(idx):
    if not idx: return ""
    pos={}
    for w,locs in idx.items():
        for l in locs: pos[l]=w
    return " ".join(pos[i] for i in sorted(pos))

def _get(url, timeout=20):
    req=urllib.request.Request(url, headers={"User-Agent":"onto-leverage-probe/0 (mailto:onto@local)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def retrieve(claim):
    q=urllib.parse.quote(claim[:300])
    # OpenAlex primary
    try:
        d=_get(f"https://api.openalex.org/works?search={q}&per-page=1&mailto=onto@local")
        res=d.get("results") or []
        if res:
            t=res[0].get("display_name") or ""
            ab=_abstract_from_inverted(res[0].get("abstract_inverted_index"))
            if t or ab: return {"title":t, "abstract":ab, "via":"openalex"}
    except Exception as e:
        pass
    # Crossref fallback
    try:
        d=_get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=1")
        items=d.get("message",{}).get("items") or []
        if items:
            t=(items[0].get("title") or [""])[0]
            ab=re.sub("<[^>]+>","",items[0].get("abstract","") or "")
            if t or ab: return {"title":t, "abstract":ab, "via":"crossref"}
    except Exception:
        pass
    return {"title":"", "abstract":"", "via":"none"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--recut", required=True, help="recut_labeled.jsonl (has the 7 CLEAN)")
    ap.add_argument("--dirty", required=True, help="qwen file: 33 DIRTY + dirty_class")
    ap.add_argument("--claims-out", default="claims_blind.jsonl")
    ap.add_argument("--labels-out", default="sealed_labels.jsonl")
    ap.add_argument("--no-retrieve", action="store_true", help="skip API (test merge/split only)")
    a=ap.parse_args()

    clean=[r for r in read_jsonl(a.recut) if str(r.get("founder_label")).upper()=="CLEAN"]
    dirty=read_jsonl(a.dirty)
    for r in dirty:
        if str(r.get("founder_label")).upper()!="DIRTY":
            sys.exit(f"ABORT: non-DIRTY row in dirty file: id {r.get('id')}")
        if r.get("dirty_class") not in ("specifics","other"):
            sys.exit(f"E15 ABORT: id {r.get('id')} dirty_class not specifics|other: {r.get('dirty_class')!r}")

    merged={}
    for r in clean+dirty:
        if r["id"] in merged: sys.exit(f"ABORT: duplicate id {r['id']}")
        merged[r["id"]]=r
    n=len(merged); nc=sum(1 for r in merged.values() if r["founder_label"].upper()=="CLEAN")
    nd=n-nc
    print(f"[merge] total={n}  CLEAN={nc}  DIRTY={nd}")
    if n!=40 or nc!=7 or nd!=33:
        sys.exit(f"ABORT: expected 40 (7C/33D), got {n} ({nc}C/{nd}D). Fix inputs.")

    cf=open(a.claims_out,"w",encoding="utf-8")
    lf=open(a.labels_out,"w",encoding="utf-8")
    via=dict(openalex=0,crossref=0,none=0)
    for i,(cid,r) in enumerate(sorted(merged.items())):
        ev={"title":"","abstract":"","via":"skipped"}
        if not a.no_retrieve:
            ev=retrieve(r["claim"]); via[ev["via"]]=via.get(ev["via"],0)+1
            time.sleep(0.3)
        cf.write(json.dumps({"id":cid,"topic":r.get("topic"),
                             "claim":r["claim"],"evidence":ev}, ensure_ascii=False)+"\n")
        lf.write(json.dumps({"id":cid,"founder_label":r["founder_label"].upper(),
                             "dirty_class":r.get("dirty_class")}, ensure_ascii=False)+"\n")
    cf.close(); lf.close()
    print(f"[retrieve] via={via}" if not a.no_retrieve else "[retrieve] SKIPPED (--no-retrieve)")
    print(f"[out] blind claims (NO labels) -> {a.claims_out}")
    print(f"[out] sealed labels (Founder)  -> {a.labels_out}")
    print("[next] send claims_blind.jsonl to auditor; keep sealed_labels.jsonl for score-2b.")

if __name__=="__main__":
    main()
