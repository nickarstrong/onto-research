import json
from hard_topics import HARD_TOPICS
HARD = set(HARD_TOPICS)

rows = [json.loads(l) for l in open("hl_baseline_v3.jsonl", encoding="utf-8") if l.strip()]
print("rows:", len(rows))

rfs = [r["rate_f"] for r in rows if "rate_f" in r]
print("rate_f per row:", rfs)
print("blind rate_f (mean):", round(sum(rfs)/len(rfs), 4) if rfs else "N/A")

flat = []
for r in rows:
    t = r.get("topics", [])
    flat += t if isinstance(t, list) else [t]
uniq = set(flat)
print("topics emitted (unique):", len(uniq))
print("subset of HARD_TOPICS(24)?:", uniq.issubset(HARD), "|", len(uniq & HARD), "in-hard /", len(uniq - HARD), "stray")
stray = sorted(uniq - HARD)[:8]
print("stray sample:", stray)
print("pool_size range:", min((r.get("pool_size",0) for r in rows), default=0), "->", max((r.get("pool_size",0) for r in rows), default=0))
print("fa_live nonzero rows:", sum(1 for r in rows if r.get("fa_live",0)))
