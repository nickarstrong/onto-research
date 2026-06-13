#!/usr/bin/env python3
# trim_window.py -- deterministic echo-loop trim for frozen-base windows (v114 method, verbatim).
#
# The frozen base (non-instruct Qwen2.5-Coder-7B) does not emit EOS and echo-loops the
# "### Instruction" / "### Response" wrapper. This cuts each output at the FIRST reoccurrence
# of either marker (greedy => the first block is identical to a stop-sequence run). Reads the
# raw window {id, text, family}, writes the clean window with the SAME schema. Deterministic;
# no model, no GPU. LF newlines so md5 is cross-platform stable.
#
# Run:
#   python trim_window.py --in ordinary_window_v6.jsonl --out ordinary_window_v6_clean.jsonl
#   python trim_window.py --in ordinary_window_v7.jsonl --out ordinary_window_v7_clean.jsonl

import argparse
import json

MARKERS = ["### Instruction", "### Response"]


def trim(t):
    idx = [t.find(m) for m in MARKERS if t.find(m) != -1]
    return (t[:min(idx)] if idx else t).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="raw window jsonl {id,text,family}")
    ap.add_argument("--out", required=True, help="clean window jsonl (same schema)")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    n_trim, empties = 0, 0
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            raw = r["text"]
            t = trim(raw)
            if t != raw.strip():
                n_trim += 1
            if not t:
                empties += 1
            f.write(json.dumps({"id": r["id"], "text": t, "family": r.get("family")},
                               ensure_ascii=False) + "\n")
    print(f"trim: {args.inp} -> {args.out}  n={len(rows)} trimmed={n_trim} empties={empties}")


if __name__ == "__main__":
    main()
