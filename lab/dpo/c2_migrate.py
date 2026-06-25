#!/usr/bin/env python3
# C-2 quarantine migration (faithful: tag-filter). Reuses frozen extractors for the audit field only.
# Writes NEW file; never overwrites source.
import json, hashlib
import o0_temporal_evidence as O
SRC="o0_verdicts.jsonl"; OUT="o0_verdicts_c2migrated.jsonl"; DELTA="c2_migration_delta.md"
rows=[json.loads(l) for l in open(SRC,encoding="utf-8") if l.strip()]
def specs(claim):
    p=O.clean_for_parse(claim); return O.extract_fulldates(p)+O.extract_numbers_nonyear(p)
out=[]; reclass=[]; no_spec=[]
for r in rows:
    if r.get("verdict")=="ABSORB" and r.get("targeted_weakness")=="fabricated-specifics":
        sp=specs(r.get("claim"))
        nr=dict(r); nr["verdict"]="ABSTAIN"
        nr["_c2_quarantine"]={"from":"ABSORB","class":"fabricated-specifics","specifics":sp}
        out.append(nr); reclass.append(r.get("id"))
        if not sp: no_spec.append(r.get("id"))
    else:
        out.append(r)
with open(OUT,"w",encoding="utf-8") as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
tally={}
for r in out: tally[r["verdict"]]=tally.get(r["verdict"],0)+1
rej_pre=[r.get("id") for r in rows if r.get("verdict")=="REJECT"]
rej_post=[r.get("id") for r in out if r.get("verdict")=="REJECT"]
# outside-class mutation check: every non-reclassified row must be byte-identical to source row
src_by_i={i:json.dumps(r,ensure_ascii=False) for i,r in enumerate(rows)}
mutated_outside=0
for i,r in enumerate(out):
    if r.get("id") in reclass: continue
    if json.dumps(r,ensure_ascii=False)!=src_by_i[i]: mutated_outside+=1
out_md5=hashlib.md5(open(OUT,"rb").read()).hexdigest()
M1=len(reclass)==86; M2=mutated_outside==0; M3=(rej_pre==rej_post and len(rej_post)==87)
M4=(tally=={"ABSORB":187,"ABSTAIN":86,"REJECT":87} and len(out)==360)
with open(DELTA,"w",encoding="utf-8") as f:
    f.write("# C-2 migration delta (faithful tag-filter)\n\n")
    f.write("source md5=9cfe3e51  output=%s md5=%s\n"%(OUT,out_md5))
    f.write("post tally: %s (total %d)\n\n"%(tally,len(out)))
    f.write("N_reclass=%d  mutated_outside=%d\n\n"%(len(reclass),mutated_outside))
    f.write("M1 N==86      : %s (%d)\n"%("PASS" if M1 else "FAIL",len(reclass)))
    f.write("M2 0 outside  : %s (%d)\n"%("PASS" if M2 else "FAIL",mutated_outside))
    f.write("M3 REJECT keep: %s\n"%("PASS" if M3 else "FAIL"))
    f.write("M4 tally      : %s\n\n"%("PASS" if M4 else "FAIL"))
    f.write("12 no-extractable-specific (entity-fork flag): %s\n"%no_spec)
print("N_reclass=%d mutated_outside=%d out_md5=%s"%(len(reclass),mutated_outside,out_md5))
print("tally=%s"%tally)
print("M1=%s M2=%s M3=%s M4=%s"%(M1,M2,M3,M4))
print("no_spec_count=%d"%len(no_spec))
