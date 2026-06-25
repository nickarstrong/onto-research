#!/usr/bin/env python3
# C-2 quarantine migration v281 (CONSUMER-GATING).
# Selector migrated: verdict-blind intent stamp (targeted_weakness) -> honest catch flags
#   (_materialised / _materialised_year). Quarantine = ABSORB AND both channels empty.
# Faithful: reuses frozen extractors ONLY as a live cross-check of the stored flags.
# Writes NEW file; never overwrites source. Canonical SWAP is Founder-gated, NOT here.
import json, hashlib, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import o0_temporal_evidence as O
SRC=os.path.join(HERE,"eval","o0","o0_verdicts.jsonl")
OUT=os.path.join(HERE,"eval","o0","o0_verdicts_c2migrated.jsonl")
DELTA=os.path.join(HERE,"c2_migration_delta.md")
rows=[json.loads(l) for l in open(SRC,encoding="utf-8") if l.strip()]
def specs(claim):
    p=O.clean_for_parse(claim); return O.extract_fulldates(p)+O.extract_numbers_nonyear(p)
def both_empty(r):
    return (not r.get("_materialised")) and (not r.get("_materialised_year"))
out=[]; reclass=[]; flag_extractor_disagree=[]
for r in rows:
    if r.get("verdict")=="ABSORB" and both_empty(r):
        sp=specs(r.get("claim"))                       # live non-year channel re-extract
        if sp: flag_extractor_disagree.append(r.get("id"))   # _materialised==False but specs found -> gate drift
        nr=dict(r); nr["verdict"]="ABSTAIN"
        nr["_c2_quarantine"]={"from":"ABSORB","reason":"both-channels-empty",
                              "_materialised":bool(r.get("_materialised")),
                              "_materialised_year":bool(r.get("_materialised_year"))}
        out.append(nr); reclass.append(r.get("id"))
    else:
        out.append(r)
with open(OUT,"w",encoding="utf-8",newline="\n") as f:    # LF-pin (pool-class write)
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
tally={}
for r in out: tally[r["verdict"]]=tally.get(r["verdict"],0)+1
rej_pre=[r.get("id") for r in rows if r.get("verdict")=="REJECT"]
rej_post=[r.get("id") for r in out if r.get("verdict")=="REJECT"]
# outside-class mutation check: every non-reclassified row byte-identical to source row
src_by_i={i:json.dumps(r,ensure_ascii=False) for i,r in enumerate(rows)}
mutated_outside=0
for i,r in enumerate(out):
    if r.get("id") in reclass: continue
    if json.dumps(r,ensure_ascii=False)!=src_by_i[i]: mutated_outside+=1
out_md5=hashlib.md5(open(OUT,"rb").read()).hexdigest()
F1=len(reclass)==11
F3=mutated_outside==0
F4=(rej_pre==rej_post and len(rej_post)==87)
F5=(tally=={"ABSORB":176,"ABSTAIN":97,"REJECT":87} and len(out)==360)
F7=(len(flag_extractor_disagree)==0)
with open(DELTA,"w",encoding="utf-8",newline="\n") as f:
    f.write("# C-2 migration delta v281 (consumer-gating: flag-driven quarantine)\n\n")
    f.write("source md5=91f442a0  output=%s md5=%s\n"%(OUT,out_md5))
    f.write("selector: ABSORB AND NOT _materialised AND NOT _materialised_year\n")
    f.write("post tally: %s (total %d)\n\n"%(tally,len(out)))
    f.write("N_reclass=%d  mutated_outside=%d  flag/extractor_disagree=%d\n\n"
            %(len(reclass),mutated_outside,len(flag_extractor_disagree)))
    f.write("F1 N==11          : %s (%d)\n"%("PASS" if F1 else "FAIL",len(reclass)))
    f.write("F3 0 outside-mut  : %s (%d)\n"%("PASS" if F3 else "FAIL",mutated_outside))
    f.write("F4 REJECT keep 87 : %s\n"%("PASS" if F4 else "FAIL"))
    f.write("F5 tally 176/97/87: %s\n"%("PASS" if F5 else "FAIL"))
    f.write("F7 flag==extractor: %s\n\n"%("PASS" if F7 else "FAIL"))
    f.write("reclassed ids (the 11 both-channels-empty):\n%s\n"%reclass)
print("N_reclass=%d mutated_outside=%d out_md5=%s"%(len(reclass),mutated_outside,out_md5))
print("tally=%s"%tally)
print("F1=%s F3=%s F4=%s F5=%s F7=%s"%(F1,F3,F4,F5,F7))
print("reclass_ids=%s"%reclass)
