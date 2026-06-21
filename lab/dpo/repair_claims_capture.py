#!/usr/bin/env python3
# repair_claims_capture.py
# Lossless triage for claim-fields corrupted by raw-TTY harvest capture.
# - replays ANSI CSI (nD cursor-back, K erase-to-EOL) to reconstruct clean text
# - flags mojibake rows (bytes destroyed) as UNRECOVERABLE -> re-harvest only those
# Authors NO claim content and NO labels (R7/E15 safe). stdlib only, no GPU.
import json, re, sys, os

ANSI = re.compile(r'\x1b\[')
MOJI = re.compile(r'[\u0400-\u04FF\uFF00-\uFFEF\u3000-\u303F]')

def replay(s):
    out=[]; col=0; i=0
    while i < len(s):
        if s[i]=='\x1b' and i+1<len(s) and s[i+1]=='[':
            j=i+2; num=''
            while j<len(s) and s[j].isdigit(): num+=s[j]; j+=1
            cmd=s[j] if j<len(s) else ''
            n=int(num) if num else 1
            if cmd=='D': col=max(0,col-n)
            elif cmd=='K': out=out[:col]
            i=j+1; continue
        ch=s[i]
        if ch=='\n': i+=1; continue
        if col<len(out): out[col]=ch
        else: out.append(ch)
        col+=1; i+=1
    return ''.join(out)

def status(c):
    if MOJI.search(c): return "UNRECOVERABLE"
    if ANSI.search(c): return "REPAIRED"
    return "CLEAN"

def process(path):
    rows=[json.loads(l) for l in open(path,encoding='utf-8') if l.strip()]
    bad=[]
    out_path=path.replace(".jsonl",".repaired.jsonl")
    with open(out_path,"w",encoding='utf-8') as f:
        for r in rows:
            st=status(r["claim"])
            if st=="REPAIRED": r["claim"]=replay(r["claim"])
            elif st=="UNRECOVERABLE": bad.append(r["id"])
            r["_repair"]=st
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    n={"CLEAN":0,"REPAIRED":0,"UNRECOVERABLE":0}
    for r in rows: n[r["_repair"]]+=1   # count snapshot status, not post-mutation
    print(f"{os.path.basename(path)}: {len(rows)} rows -> {os.path.basename(out_path)}")
    print(f"  CLEAN {n['CLEAN']}  REPAIRED {n['REPAIRED']}  UNRECOVERABLE {n['UNRECOVERABLE']}")
    return bad

if __name__=="__main__":
    files=sys.argv[1:] or ["claims_blind_ev.jsonl","claims_blind_ev_temporal.jsonl"]
    allbad=set()
    for p in files: allbad |= set(process(p))
    with open("reharvest_ids.txt","w") as f:
        for i in sorted(allbad): f.write(i+"\n")
    print(f"\nRE-HARVEST {len(allbad)} ids -> reharvest_ids.txt")
