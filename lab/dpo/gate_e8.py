#!/usr/bin/env python3
r"""
gate_e8.py - leak gate for P7_anchor pairs vs eval sets (E7 rule, verbatim).

RULES (PASS = 0 collisions):
  (1) exact-substring: no eval question appears inside a pair (either direction).
  (2) content-token overlap > 3: stopword/generic-measurement-word-filtered
      token intersection between a pair (instruction+output) and any eval
      question must be <= 3. Overlap >3 = collision.

Eval sets = heldout_v1.3.jsonl + bait_v2_n32.jsonl (questions only).
Any collision -> exit(1), print offending pair+eval id+shared tokens.
"""
import json, re, sys

STOP = set("""
a an the of to in on for and or with without is are was were be been being as at by from
this that these those it its their there here what how much many does do did has have had
will would can could should may might given since because now as per about into over under
between vs versus your you me i we they he she him her his them
typical typically modern current recent value figure number range rate exact precise per
study report data measure measured measurement most least more less than then so not no yes
give state provide tell single point each one two three under over high low good real world
""".split())

WORD = re.compile(r"[a-z0-9]+")


def toks(s):
    return {w for w in WORD.findall(s.lower()) if w not in STOP and len(w) > 2}


def load_q(path):
    out = []
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        out.append(json.loads(l))
    return out


def main():
    pairs = load_q("sft_p7_pairs_E8.jsonl")
    evals = load_q("heldout_v1.3.jsonl") + load_q("bait_v2_n32.jsonl")
    collisions = 0
    for p in pairs:
        ptxt = (p["instruction"] + " " + p["output"]).lower()
        pq = p["instruction"].lower()
        ptok = toks(p["instruction"] + " " + p["output"])
        for e in evals:
            eq = e["question"].lower()
            # (1) exact-substring both directions on the question text
            if eq in ptxt or pq in eq:
                print(f"COLLISION(substr): pair='{p['instruction'][:50]}' <-> {e['id']}")
                collisions += 1
                continue
            # (2) content-token overlap
            shared = ptok & toks(e["question"])
            if len(shared) > 3:
                print(f"COLLISION(overlap={len(shared)}): pair='{p['instruction'][:50]}' "
                      f"<-> {e['id']} shared={sorted(shared)}")
                collisions += 1
    print(f"\npairs={len(pairs)} eval_items={len(evals)} collisions={collisions}")
    if collisions:
        print("GATE: FAIL")
        sys.exit(1)
    print("GATE: PASS")


if __name__ == "__main__":
    main()
