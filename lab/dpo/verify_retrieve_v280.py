#!/usr/bin/env python3
# -*- coding: ascii -*-
# verify_retrieve_v280.py -- live check that the v280 POOL HYGIENE quarantine is wired into the
# PROPOSER feed (o0_retrieve.load_confirmed). Run from lab/dpo. Reproducibility artifact (git).
# PASS gate: ABSORB 187 -> load_confirmed 176, quarantine 11 (both-channels-empty), 0 leaked.
import json, sys
import o0_retrieve as R

POOL = "eval/o0/o0_verdicts.jsonl"   # swapped canonical (v280, md5 91f442a0)

loaded = R.load_confirmed(POOL)
rows = [json.loads(l) for l in open(POOL, encoding="utf-8") if l.strip()]
absorb = [r for r in rows if r["verdict"] == "ABSORB"]
expect = [r for r in absorb if r.get("_materialised") or r.get("_materialised_year")]
qids = {r["id"] for r in absorb if not (r.get("_materialised") or r.get("_materialised_year"))}
lids = {r["id"] for r in loaded}

P1 = len(loaded) == 176
P2 = lids == {r["id"] for r in expect}
P3 = lids.isdisjoint(qids)
P4 = len(qids) == 11

print("ABSORB=%d load_confirmed=%d expect=%d quarantine=%d" % (len(absorb), len(loaded), len(expect), len(qids)))
print("P1 load==176 : %s" % P1)
print("P2 set-match : %s" % P2)
print("P3 0 leaked  : %s" % P3)
print("P4 quar==11  : %s" % P4)
print("ALL=%s" % (P1 and P2 and P3 and P4))
sys.exit(0 if (P1 and P2 and P3 and P4) else 1)
