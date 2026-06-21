#!/usr/bin/env python3
# reharvest_run.py  -- re-generate the 11 lost claims with CLEAN capture.
# reads  : reharvest_task.json
# writes : claims_reharvested.jsonl  (same schema, only `claim` is fresh)
# capture: Ollama /api/generate, "stream": false, reads JSON `response`  (no TTY).
# stdlib only. local Ollama, no GPU cloud needed.
import json, urllib.request

MODEL = "qwen2.5-coder:7b"          # base proposer (no LoRA)
OLLAMA = "http://localhost:11434/api/generate"

# NOTE: keep this prompt identical to the original generate_claim (onto_e5_gen.py).
# If the original differs, swap the line below so the 11 stay on-distribution.
PROMPT = ("Write one factual textbook claim about: {topic}. "
          "State it in a single sentence and include the specific dates, names and numbers. "
          "Output only the claim sentence, nothing else.")

def gen(topic):
    body = json.dumps({"model": MODEL, "prompt": PROMPT.format(topic=topic),
                       "stream": False}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"].strip()

task = json.load(open("reharvest_task.json", encoding="utf-8"))
items = task["items"]
out = "claims_reharvested.jsonl"
with open(out, "w", encoding="utf-8") as f:
    for i, it in enumerate(items, 1):
        claim = gen(it["topic"])
        row = {"id": it["id"], "topic": it["topic"], "claim": claim,
               "evidence": it["evidence"]}
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"[{i}/{len(items)}] {it['id']}  OK  ({len(claim)} chars)")
print(f"\nwrote {len(items)} clean claims -> {out}")
