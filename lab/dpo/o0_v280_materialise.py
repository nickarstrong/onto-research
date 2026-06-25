#!/usr/bin/env python3
# o0_v280_materialise.py -- v280 POOL HYGIENE build (candidate + delta + F-bars).
# OFFLINE. Rebuilds from CANONICAL (755d81c3); additive-only: +_materialised +_materialised_year.
# Both flags from the GATE's OWN frozen channels (no second extractor):
#   _materialised      = len(extract_fulldates + extract_numbers_nonyear) > 0   (non-year channel; == v279)
#   _materialised_year = len(extract_years_ext CE or BCE) > 0                    (year channel; NEW)
# Retrieval-quarantine predicate (proposer feed): drop ABSORB iff NOT _materialised AND NOT _materialised_year.
# NEVER overwrites source: writes a NEW candidate beside it. No canonical swap (Founder-gated).
import json, hashlib, sys
from pathlib import Path
import o0_temporal_evidence as O

SRC    = "eval/o0/o0_verdicts.jsonl"
V279   = "eval/o0/o0_verdicts_v279cand.jsonl"   # optional regression cross-check
CAND   = "eval/o0/o0_verdicts_v280cand.jsonl"
DELTA  = "eval/o0/v280_materialise_delta.md"
EXPECT_SRC_MD5_PREFIX = "755d81c3"              # canonical pool (pack v280 SUBSTRATE-ANCHOR)

# ---- staleness guard: pool md5 must match the anchor (disk-wins) ----
raw = open(SRC, "rb").read()
src_md5 = hashlib.md5(raw).hexdigest()
if not src_md5.startswith(EXPECT_SRC_MD5_PREFIX):
    sys.exit("FATAL pool md5 drift: %s (expect %s...) -- reconcile before relabel" % (src_md5, EXPECT_SRC_MD5_PREFIX))

rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]

# ---- detectors = the gate's exact frozen channels (no second extractor) ----
def mat_nonyear(claim):
    p = O.clean_for_parse(claim or "")
    return len(O.extract_fulldates(p) + O.extract_numbers_nonyear(p)) > 0

def mat_year(claim):
    p = O.clean_for_parse(claim or "")
    ce, bce = O.extract_years_ext(p)
    return (len(ce) > 0) or (len(bce) > 0)

cand = []
mt = mf = yt = yf = 0
for r in rows:
    nr = dict(r)
    claim = r.get("claim", "")
    m = mat_nonyear(claim)
    y = mat_year(claim)
    nr["_materialised"] = m
    nr["_materialised_year"] = y
    mt += int(m); mf += int(not m)
    yt += int(y); yf += int(not y)
    cand.append(nr)

with open(CAND, "w", encoding="utf-8", newline="\n") as f:   # LF pin: match canonical EOL, cross-platform hermetic
    for r in cand:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
cand_md5 = hashlib.md5(open(CAND, "rb").read()).hexdigest()

# ---- FA: additive-only -- candidate == source + EXACTLY {_materialised,_materialised_year} ----
def strip_new(r):
    r2 = dict(r); r2.pop("_materialised", None); r2.pop("_materialised_year", None)
    return json.dumps(r2, ensure_ascii=False, sort_keys=True)
src_by_i = {i: json.dumps(r, ensure_ascii=False, sort_keys=True) for i, r in enumerate(rows)}
mutated_outside = sum(1 for i, r in enumerate(cand) if strip_new(r) != src_by_i[i])
FA = mutated_outside == 0

# ---- FB: gate-stability regression -- recomputed _materialised == v279cand._materialised ----
FB = None; fb_mismatch = -1
if Path(V279).exists():
    v279 = {json.loads(l)["id"]: json.loads(l) for l in open(V279, encoding="utf-8") if l.strip()}
    fb_mismatch = sum(1 for r in cand
                      if r["id"] in v279 and v279[r["id"]].get("_materialised") != r["_materialised"])
    FB = (fb_mismatch == 0)

# ---- FC: retrieval quarantine on the ABSORB feed (load_confirmed = verdict==ABSORB) ----
absorb       = [r for r in cand if r["verdict"] == "ABSORB"]
keep         = [r for r in absorb if r["_materialised"] or r["_materialised_year"]]
quarantine   = [r for r in absorb if not r["_materialised"] and not r["_materialised_year"]]
# year-bearing-but-nonyear-empty rows that MUST survive (the v279 over-broad-key victims):
saved_by_year = [r for r in absorb if (not r["_materialised"]) and r["_materialised_year"]]
FC1 = len(keep) + len(quarantine) == len(absorb)                 # partition
FC2 = all(r["_materialised"] or r["_materialised_year"] for r in keep)  # no kept row is both-empty
FC3 = len(saved_by_year) == 22                                   # the measured legit-seed save (seal target)

# ---- verdict tally untouched (additive build) ----
from collections import Counter
tally = dict(Counter(r["verdict"] for r in cand))
FD = (tally == {"ABSORB": 187, "REJECT": 87, "ABSTAIN": 86} and len(cand) == 360)

with open(DELTA, "w", encoding="utf-8") as f:
    f.write("# v280 materialise delta (candidate build; source untouched)\n\n")
    f.write("source : %s md5=%s\n" % (SRC, src_md5))
    f.write("cand   : %s md5=%s\n\n" % (CAND, cand_md5))
    f.write("rows total            : %d\n" % len(cand))
    f.write("_materialised      t/f: %d / %d\n" % (mt, mf))
    f.write("_materialised_year t/f: %d / %d\n\n" % (yt, yf))
    f.write("RETRIEVAL FEED (verdict==ABSORB = %d):\n" % len(absorb))
    f.write("  keep (mat OR mat_year)     : %d\n" % len(keep))
    f.write("  quarantine (both empty)    : %d\n" % len(quarantine))
    f.write("  saved-by-year (mat=F,yr=T) : %d  <- v279 over-broad-key would have wrongly dropped these\n\n" % len(saved_by_year))
    f.write("FA additive-only (0 outside)  : %s (%d)\n" % ("PASS" if FA else "FAIL", mutated_outside))
    f.write("FB _materialised == v279cand  : %s (mismatch=%d)\n" % ("PASS" if FB else ("SKIP" if FB is None else "FAIL"), fb_mismatch))
    f.write("FC1 ABSORB partition          : %s\n" % ("PASS" if FC1 else "FAIL"))
    f.write("FC2 no both-empty kept        : %s\n" % ("PASS" if FC2 else "FAIL"))
    f.write("FC3 saved-by-year==22         : %s (%d)\n" % ("PASS" if FC3 else "FAIL", len(saved_by_year)))
    f.write("FD verdict tally untouched    : %s %s\n\n" % ("PASS" if FD else "FAIL", tally))
    f.write("# LOCAL-only per-row (not for public git):\n")
    f.write("quarantine_ids = %s\n" % [r["id"] for r in quarantine])

print("src_md5=%s cand_md5=%s rows=%d" % (src_md5, cand_md5, len(cand)))
print("_materialised t/f=%d/%d  _materialised_year t/f=%d/%d" % (mt, mf, yt, yf))
print("ABSORB=%d keep=%d quarantine=%d saved_by_year=%d" % (len(absorb), len(keep), len(quarantine), len(saved_by_year)))
print("FA=%s FB=%s FC1=%s FC2=%s FC3=%s FD=%s" % (FA, FB, FC1, FC2, FC3, FD))
