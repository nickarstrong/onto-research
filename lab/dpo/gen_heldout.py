#!/usr/bin/env python3
# gen_heldout.py -- fresh §3 held-out claims (substrate-generated, disjoint from recut).
# 2 generations per topic -> volume to net >=10 CLEAN after Founder labels.
# Output: heldout_raw.jsonl {id, topic, claim}  -> Founder adds founder_label + dirty_class.
import json, subprocess, sys
MODEL="qwen2.5-coder:7b"
topics=[t.strip() for t in open("fresh_topics.txt",encoding="utf-8") if t.strip()]
def ollama(p):
    r=subprocess.run(["ollama","run",MODEL,p],capture_output=True,text=True,timeout=180)
    return r.stdout.strip()
out=[]
for k,t in enumerate(topics):
    for v in range(2):
        p=(f"Generate ONE specific, verifiable scientific claim about: {t}. "
           f"Include a concrete detail (date, name, or number). Output only the claim.")
        out.append({"id":f"held2_{k:02d}_{v}","topic":t,"claim":ollama(p)})
        print(f"[gen] {k:02d}_{v} {t[:40]}")
open("heldout_raw.jsonl","w",encoding="utf-8").write(
    "\n".join(json.dumps(r,ensure_ascii=False) for r in out)+"\n")
print(f"\nDONE {len(out)} claims -> heldout_raw.jsonl")
print("NEXT: add to each line  \"founder_label\":\"CLEAN\"|\"DIRTY\"  and for DIRTY  \"dirty_class\":\"specifics\"|\"other\"  -> return.")
