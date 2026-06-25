#!/usr/bin/env python3
# p4_gt_correction.py -- v274 P4 GT-CORRECTION (Founder-ruled, sanctioned, NOT a silent mutation).
# DIRTY->CLEAN x4 in sealed_labels: 06_1, 07_0, 23_1 (worksheet v271 mislabels) + 21_1 (v274 ruling:
# claimed 1789 = canonical Lavoisier year; same un-materialized "specifics" mislabel pattern).
# Writes a dated backup BEFORE edit and prints a line-level diff. VIOLATION-A safe: backup -> edit
# -> diff (original preserved). dirty_class set to null on corrected rows.

import json, sys, shutil, datetime, os

PATH = sys.argv[1] if len(sys.argv) > 1 else "sealed_labels_heldout_20260625.jsonl"
CORRECT = {"held2_06_1", "held2_07_0", "held2_23_1", "held2_21_1"}

stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
bak = PATH + ".bak." + stamp
shutil.copyfile(PATH, bak)
print("[P4] backup ->", bak)

rows = [json.loads(l) for l in open(PATH, encoding="utf-8") if l.strip()]
diff = []
for r in rows:
    if r["id"] in CORRECT:
        before = (r.get("founder_label"), r.get("dirty_class"))
        r["founder_label"] = "CLEAN"
        r["dirty_class"] = None
        after = (r["founder_label"], r["dirty_class"])
        diff.append((r["id"], before, after))

with open(PATH, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("[P4] corrected %d rows (expected 4):" % len(diff))
for rid, b, a in diff:
    print("   %-14s %s -> %s" % (rid, b, a))
assert len(diff) == 4, "P4 expected exactly 4 corrections, got %d" % len(diff)
print("[P4] OK")
