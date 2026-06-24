#!/usr/bin/env python3
# gen_heldout.py -- fresh held-out claims (substrate-generated, disjoint from the SPENT set).
# 2 generations per topic. Output: NEW dated jsonl. NEVER overwrites pre-existing state (VIOLATION-A).
# Usage: python gen_heldout.py [OUT_PATH] [TOPIC_LIMIT]
#   OUT_PATH     default heldout_raw_<YYYYMMDD>.jsonl ; ABORTS if the path already exists.
#   TOPIC_LIMIT  default = all topics ; pass e.g. 1 for a smoke / timing probe.
# Founder then adds  founder_label + dirty_class  per line.
import json, subprocess, sys, os, datetime
MODEL = "qwen2.5-coder:7b"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"heldout_raw_{datetime.date.today():%Y%m%d}.jsonl"
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else None
if os.path.exists(OUT):
    sys.exit(f"ABORT (VIOLATION-A): {OUT} exists -- refusing to overwrite pre-existing state. Pass a new path.")
topics = [t.strip() for t in open("fresh_topics.txt", encoding="utf-8") if t.strip()]
if LIMIT is not None:
    topics = topics[:LIMIT]
def ollama(p):
    r = subprocess.run(["ollama", "run", MODEL, p], capture_output=True, text=True, timeout=180)
    return r.stdout.strip()
out = []
t0 = datetime.datetime.now()
for k, t in enumerate(topics):
    for v in range(2):
        p = (f"Generate ONE specific, verifiable scientific claim about: {t}. "
             f"Include a concrete detail (date, name, or number). Output only the claim.")
        out.append({"id": f"held2_{k:02d}_{v}", "topic": t, "claim": ollama(p)})
        print(f"[gen] {k:02d}_{v} {t[:40]}")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n")
dt = (datetime.datetime.now() - t0).total_seconds()
print(f"\nDONE {len(out)} claims -> {OUT}  ({dt:.1f}s total, {dt/max(1,len(out)):.1f}s/gen)")
print("NEXT: add to each line  \"founder_label\":\"CLEAN\"|\"DIRTY\"  and for DIRTY  \"dirty_class\":\"specifics\"|\"other\"  -> return.")
