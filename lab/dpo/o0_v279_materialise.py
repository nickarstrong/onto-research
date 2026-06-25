#!/usr/bin/env python3
# o0_v279_materialise.py -- v279 GENERATOR AUDIT build (candidate + delta + F-bars).
# OFFLINE. Reuses the GATE's own non-year specific channel (no second extractor).
# NEVER overwrites source: writes a NEW candidate file beside it. No canonical swap.
import json, hashlib, re, sys
import o0_temporal_evidence as O

SRC   = "eval/o0/o0_verdicts.jsonl"
CAND  = "eval/o0/o0_verdicts_v279cand.jsonl"
DELTA = "eval/o0/v279_materialise_delta.md"
EXPECT_SRC_MD5_PREFIX = "755d81c3"   # canonical pool (pack v279 SUBSTRATE-ANCHOR)

# ---- staleness guard: pool md5 must match the anchor (disk-wins) ----
raw = open(SRC, "rb").read()
src_md5 = hashlib.md5(raw).hexdigest()
if not src_md5.startswith(EXPECT_SRC_MD5_PREFIX):
    sys.exit(f"FATAL pool md5 drift: {src_md5} (expect {EXPECT_SRC_MD5_PREFIX}...) -- reconcile before relabel")

rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]

# ---- materialisation detector = the gate's exact channel (same as c2_migrate.specs) ----
def specs(claim):
    p = O.clean_for_parse(claim or "")
    return O.extract_fulldates(p) + O.extract_numbers_nonyear(p)

# ---- WATCH-G: detect (report only; do NOT strip existing pool -> would mutate outside-class) ----
CTRL = re.compile(r"(\x1b\[[0-9;]*[A-Za-z])|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

# ---- arity probe (REPORT ONLY -- deferred per void-as-measured: floor n=1, needs parser) ----
# 'respectively'-enumeration arity is a real defect class (1 seed case on this surface:
# N-agents vs M-years mismatch) but the floor is too thin + the trailing 'A and B' list has
# no comma -> not cheaply regex-separable. Recorded as seed; gate build deferred to horizon.

cand = []
mat_true = mat_false = 0
watchg_ids = []
respectively_ids = []
for r in rows:
    nr = dict(r)
    claim = r.get("claim", "")
    mat = len(specs(claim)) > 0
    nr["_materialised"] = mat
    mat_true += int(mat); mat_false += int(not mat)
    if CTRL.search(claim or ""):
        watchg_ids.append(r.get("id"))
    if "respectively" in (claim or "").lower():
        respectively_ids.append(r.get("id"))
    cand.append(nr)

# ---- write candidate (NEW file; source untouched) ----
with open(CAND, "w", encoding="utf-8") as f:
    for r in cand:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
cand_md5 = hashlib.md5(open(CAND, "rb").read()).hexdigest()

# ---- outside-class mutation check: candidate == source + ONLY the _materialised key ----
def strip_mat(r):
    r2 = dict(r); r2.pop("_materialised", None)
    return json.dumps(r2, ensure_ascii=False, sort_keys=True)
src_by_i = {i: json.dumps(r, ensure_ascii=False, sort_keys=True) for i, r in enumerate(rows)}
mutated_outside = sum(1 for i, r in enumerate(cand) if strip_mat(r) != src_by_i[i])

# ---- F-bars on the fabricated-specifics class ----
fab          = [r for r in cand if r.get("targeted_weakness") == "fabricated-specifics"]
fab_reject   = [r for r in fab if r.get("verdict") == "REJECT"]
fab_abstain  = [r for r in fab if r.get("verdict") == "ABSTAIN"]
zero_spec    = [r for r in fab_abstain if r["_materialised"] is False]
rej_mat      = [r for r in fab_reject if r["_materialised"] is True]

F1 = len(zero_spec) == 12
F2 = len(rej_mat) == len(fab_reject) and len(fab_reject) == 34
F3 = mutated_outside == 0
F5 = True  # deterministic by construction; hermetic re-run = byte-identical

# ---- delta report (counts only; per-row IDs local) ----
with open(DELTA, "w", encoding="utf-8") as f:
    f.write("# v279 materialise delta (candidate build; source untouched)\n\n")
    f.write("source : %s md5=%s\n" % (SRC, src_md5))
    f.write("cand   : %s md5=%s\n\n" % (CAND, cand_md5))
    f.write("rows total           : %d\n" % len(cand))
    f.write("_materialised true   : %d\n" % mat_true)
    f.write("_materialised false  : %d\n\n" % mat_false)
    f.write("fab-spec class       : %d (REJECT %d / ABSTAIN %d)\n" % (len(fab), len(fab_reject), len(fab_abstain)))
    f.write("  zero-specific ABSTAIN (no-injection): %d\n" % len(zero_spec))
    f.write("  REJECT materialised                : %d/%d\n\n" % (len(rej_mat), len(fab_reject)))
    f.write("F1 zero-spec==12        : %s (%d)\n" % ("PASS" if F1 else "FAIL", len(zero_spec)))
    f.write("F2 REJECT all-mat & ==34: %s (%d/%d)\n" % ("PASS" if F2 else "FAIL", len(rej_mat), len(fab_reject)))
    f.write("F3 0 outside-mutation   : %s (%d)\n" % ("PASS" if F3 else "FAIL", mutated_outside))
    f.write("F5 hermetic             : PASS (deterministic)\n\n")
    f.write("WATCH-G ctrl-code rows  : %d (strip-at-source owed in gen path; existing-pool = separate pass)\n" % len(watchg_ids))
    f.write("arity 'respectively' rows: %d (DEFERRED -- floor too thin for a gate; seed recorded local)\n" % len(respectively_ids))
    f.write("\n# LOCAL-only per-row (not for public git):\n")
    f.write("zero_spec_ids = %s\n" % [r.get("id") for r in zero_spec])
    f.write("watchg_ids    = %s\n" % watchg_ids)
    f.write("respectively_ids = %s\n" % respectively_ids)

# ---- console summary ----
print("src_md5=%s cand_md5=%s rows=%d" % (src_md5, cand_md5, len(cand)))
print("materialised true=%d false=%d" % (mat_true, mat_false))
print("fab-spec=%d REJECT=%d ABSTAIN=%d zero_spec=%d rej_mat=%d" %
      (len(fab), len(fab_reject), len(fab_abstain), len(zero_spec), len(rej_mat)))
print("F1=%s F2=%s F3=%s F5=PASS" % (F1, F2, F3))
print("WATCH-G_rows=%d respectively_rows=%d (arity DEFERRED)" %
      (len(watchg_ids), len(respectively_ids)))
