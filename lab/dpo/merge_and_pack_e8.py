#!/usr/bin/env python3
r"""
merge_and_pack_e8.py - merge local base SFT (sft_reflex_392) with P7_anchor pairs.

Schema-adaptive: detects base file's pair schema from its first record and emits
P7 pairs in the SAME schema. Aborts loudly if schema cannot be mapped (R10: no
guessing). Asserts final line count == EXPECT or aborts.

Usage:
  python merge_and_pack_e8.py --base sft_reflex_392.jsonl \
                              --added sft_p7_pairs_E8.jsonl \
                              --out  sft_reflex_418.jsonl --expect 418
"""
import json, sys, hashlib, argparse

ALPACA = "### Instruction:\n{q}\n\n### Response:\n{a}"


def first_record(path):
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if l:
            return json.loads(l)
    sys.exit(f"ABORT: base file {path} is empty")


def detect(rec):
    k = set(rec.keys())
    if {"instruction", "output"} <= k:        return "instruction_output"
    if "messages" in k:                        return "messages"
    if {"prompt", "completion"} <= k:          return "prompt_completion"
    if {"prompt", "response"} <= k:            return "prompt_response"
    if k <= {"text", "_meta", "category"} and "text" in k: return "text_alpaca"
    sys.exit(f"ABORT: unrecognised base schema keys={sorted(k)} -- inspect base, do not guess.")


def emit(schema, q, a, cat):
    if schema == "instruction_output":
        return {"instruction": q, "output": a, "category": cat}
    if schema == "messages":
        return {"messages": [{"role": "user", "content": q},
                             {"role": "assistant", "content": a}], "category": cat}
    if schema == "prompt_completion":
        return {"prompt": q, "completion": a, "category": cat}
    if schema == "prompt_response":
        return {"prompt": q, "response": a, "category": cat}
    if schema == "text_alpaca":
        return {"text": ALPACA.format(q=q, a=a), "category": cat}
    sys.exit("ABORT: emit schema mismatch")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--added", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", type=int, required=True)
    args = ap.parse_args()

    schema = detect(first_record(args.base))
    print(f"base schema = {schema}")

    base_lines = [l for l in open(args.base, encoding="utf-8") if l.strip()]
    added = [json.loads(l) for l in open(args.added, encoding="utf-8") if l.strip()]

    with open(args.out, "w", encoding="utf-8") as f:
        for l in base_lines:
            f.write(l if l.endswith("\n") else l + "\n")
        for p in added:
            rec = emit(schema, p["instruction"], p["output"], p.get("category", "P7_anchor"))
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    total = sum(1 for l in open(args.out, encoding="utf-8") if l.strip())
    if total != args.expect:
        sys.exit(f"ABORT: line count {total} != expected {args.expect} "
                 f"(base={len(base_lines)} added={len(added)})")
    h = hashlib.md5(open(args.out, "rb").read()).hexdigest()
    print(f"OK: {len(base_lines)} base + {len(added)} P7 = {total} -> {args.out}")
    print(f"md5={h}")


if __name__ == "__main__":
    main()
