#!/usr/bin/env python3
# build_l5_truth.py
# Turn a PLAIN typed table into eval/_local/l5_coupling_truth.jsonl and check it.
# You only type ground-truth (DOIs + how each pair is coupled). The script writes the JSON + checks.
#
# INPUT FILE  : eval/_local/truth_input.txt   (plain text, you edit this)
# OUTPUT FILE : eval/_local/l5_coupling_truth.jsonl
#
# truth_input.txt format (lines starting with # are ignored):
#   CLAIM <claim_id> <free text of the claim>
#   SRC   <sid> <doi> <data_id|-> <method|->
#   PAIR  <sidA> <sidB> <independent|author|institution|data|citation>
#   (blank line or next CLAIM ends the block)
#
# data_id '-' = no DAS in the real paper (predicate fail-closes). method '-' = none (advisory anyway).

import json, sys, os, itertools
from collections import defaultdict

CLASSES = ["independent", "author", "institution", "data", "citation"]
IN  = "eval/_local/truth_input.txt"
OUT = "eval/_local/l5_coupling_truth.jsonl"

def parse(path):
    rows, cur = [], None
    for ln, raw in enumerate(open(path, encoding="utf-8"), 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        tok = s.split()
        kind = tok[0].upper()
        if kind == "CLAIM":
            if cur: rows.append(cur)
            cur = {"claim_id": tok[1], "claim": " ".join(tok[2:]), "sources": [], "coupling_truth": []}
        elif kind == "SRC":
            if cur is None: sys.exit(f"line {ln}: SRC before CLAIM")
            sid, doi = tok[1], tok[2]
            data_id = None if (len(tok) < 4 or tok[3] == "-") else tok[3]
            method  = None if (len(tok) < 5 or tok[4] == "-") else tok[4]
            cur["sources"].append({"sid": sid, "doi": doi, "data_id": data_id, "method_class": method})
        elif kind == "PAIR":
            if cur is None: sys.exit(f"line {ln}: PAIR before CLAIM")
            if tok[3] not in CLASSES: sys.exit(f"line {ln}: bad label '{tok[3]}'")
            cur["coupling_truth"].append({"a": tok[1], "b": tok[2], "label": tok[3]})
        else:
            sys.exit(f"line {ln}: unknown row '{kind}'")
    if cur: rows.append(cur)
    return rows

def check(rows):
    cls, problems = defaultdict(int), []
    for r in rows:
        sids = [s["sid"] for s in r["sources"]]
        if len(sids) < 2: problems.append(f"{r['claim_id']}: fewer than 2 sources")
        want = {frozenset(p) for p in itertools.combinations(sids, 2)}
        got  = {frozenset((t["a"], t["b"])) for t in r["coupling_truth"]}
        miss = want - got
        extra = got - want
        if miss:  problems.append(f"{r['claim_id']}: missing pair(s) {[tuple(m) for m in miss]}")
        if extra: problems.append(f"{r['claim_id']}: pair(s) for unknown sources {[tuple(e) for e in extra]}")
        for t in r["coupling_truth"]: cls[t["label"]] += 1
    missing_classes = [c for c in CLASSES if cls[c] == 0]
    return cls, missing_classes, problems

def main():
    if not os.path.exists(IN):
        sys.exit(f"NO INPUT: create {IN} first (see header of this script for the format).")
    rows = parse(IN)
    cls, missing, problems = check(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Built {OUT}: {len(rows)} claims.")
    print("Coupling-type counts:", {c: cls[c] for c in CLASSES})
    if missing: print("MISSING TYPES (must be >=1 each):", missing)
    if problems:
        print("PROBLEMS:")
        for p in problems: print("  -", p)
    ok = (not missing) and (not problems)
    print("RESULT:", "READY -- you can run the validation." if ok
          else "NOT READY -- fix the items above, re-run this.")
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
