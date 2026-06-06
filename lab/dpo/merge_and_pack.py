#!/usr/bin/env python3
"""
merge_and_pack.py - merge base SFT (sft_reflex_323) with E7 G-pairs.

Schema-adaptive: detects the base file's pair schema from its first record and
emits G-pairs in the SAME schema. Aborts loudly if the schema cannot be mapped
(R10: no guessing; SKILL 10: state it, don't simulate).

Usage:
  python merge_and_pack.py --base <sft_reflex_323.jsonl> \
                           --added sft_g_pairs_E7.jsonl \
                           --out sft_reflex_392.jsonl
"""
import json, sys, hashlib, argparse

ALPACA_TEXT = "### Instruction:\n{q}\n\n### Response:\n{a}"

# G-pair role -> training category (P6 family, next after base P5b)
ROLE2CAT = {
    "G1_premise_guard":  "P6_premise_guard",
    "G2_disclaim_guard": "P6_disclaim_guard",
    "G3_anchor":         "P6_anchor",
}

def first_record(path):
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if l:
            return json.loads(l)
    raise SystemExit(f"ABORT: base file {path} is empty")

def detect(rec):
    k = set(rec.keys())
    if {"instruction", "output"} <= k:        return "instruction_output"
    if "messages" in k:                        return "messages"
    if {"prompt", "completion"} <= k:          return "prompt_completion"
    if {"prompt", "response"} <= k:            return "prompt_response"
    if k == {"text"} or k == {"text", "_meta"}: return "text_alpaca"
    raise SystemExit(f"ABORT: unrecognised base schema keys={sorted(k)} -- "
                     f"cannot map G-pairs safely. Inspect base file, do not guess.")

def to_schema(p, schema):
    q, a = p["instruction"], p["output"]
    cat = ROLE2CAT.get(p.get("_meta", {}).get("role"), "P6_guard")
    if schema == "instruction_output":  return {"instruction": q, "output": a, "category": cat}
    if schema == "messages":            return {"messages": [
                                            {"role": "user", "content": q},
                                            {"role": "assistant", "content": a}], "category": cat}
    if schema == "prompt_completion":   return {"prompt": q, "completion": a, "category": cat}
    if schema == "prompt_response":     return {"prompt": q, "response": a, "category": cat}
    if schema == "text_alpaca":         return {"text": ALPACA_TEXT.format(q=q, a=a), "category": cat}
    raise SystemExit("ABORT: unreachable")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--added", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    schema = detect(first_record(args.base))
    print(f"[merge] base schema detected : {schema}")

    base_lines = [l for l in open(args.base, encoding="utf-8") if l.strip()]
    added = [json.loads(l) for l in open(args.added, encoding="utf-8") if l.strip()]
    print(f"[merge] base records         : {len(base_lines)}")
    print(f"[merge] added G-pairs        : {len(added)}")

    with open(args.out, "w", encoding="utf-8") as f:
        for l in base_lines:
            f.write(l if l.endswith("\n") else l + "\n")
        for p in added:
            f.write(json.dumps(to_schema(p, schema), ensure_ascii=False) + "\n")

    total = len(base_lines) + len(added)
    md5 = hashlib.md5(open(args.out, "rb").read()).hexdigest()
    # validate line count
    n_written = sum(1 for l in open(args.out, encoding="utf-8") if l.strip())
    assert n_written == total, f"ABORT: line-count mismatch {n_written}!={total}"
    print(f"[merge] OUT                  : {args.out}")
    print(f"[merge] total records        : {total}  (validated)")
    print(f"[merge] md5({args.out}) : {md5}")

if __name__ == "__main__":
    main()
