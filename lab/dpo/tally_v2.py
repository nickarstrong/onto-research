#!/usr/bin/env python3
# tally_v2.py -- ORGAN TALLY for phase-3 step1 (per-flag rates, not just declared).
# import-only over the FROZEN A-channel (verify_E16_A.selfcheck); organ NOT mutated.
# Mirrors verify_disp_audit.audit_window flag-extraction byte-for-byte, but prints
# per-flag count/rate + per-genre A1 + the pre-stated R6 verdict (A1 >= 0.30).
#
# Usage (no GPU/net/store; run where the organs live):
#   python tally_v2.py .\eval\ordinary_window_v2_clean.jsonl

import json, sys
from collections import defaultdict

import verify_E16_A as A   # frozen; .selfcheck reused byte-identical

TAU = 0.30
FLAGS = ['A1_NUMBER_NO_SOURCE', 'A2_OVERCONFIDENT_UNGROUNDED',
         'A3_VAGUE_QUANT_NO_NUMBER', 'A4_EMPTY_HEDGE']
SHORT = {FLAGS[0]: 'A1', FLAGS[1]: 'A2', FLAGS[2]: 'A3', FLAGS[3]: 'A4'}


def fired_flags(text):
    r = A.selfcheck(text)
    fired = set()
    for c in r['claims']:
        for f in c['gating']:
            fired.add(f)
    return fired


def main():
    path = sys.argv[1]
    win = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    n = len(win)

    count = defaultdict(int)
    items_with_any = 0
    fired_ids = defaultdict(list)
    genre_a1 = defaultdict(lambda: [0, 0])   # family -> [a1_fired, total]

    for it in win:
        fam = it.get('family', '?')
        genre_a1[fam][1] += 1
        ff = fired_flags(it['text'])
        if ff:
            items_with_any += 1
        for f in ff:
            count[f] += 1
            fired_ids[f].append(it['id'])
        if FLAGS[0] in ff:
            genre_a1[fam][0] += 1

    floor = -(-int(TAU * 100) * n // 100)   # ceil(TAU*n) integer
    # robust ceil:
    import math
    floor = math.ceil(TAU * n)

    print(f"N = {n}   tau_declare = {TAU}   A1 floor = {floor}/{n}")
    print("-" * 60)
    for f in FLAGS:
        c = count[f]
        rate = c / n if n else 0.0
        mark = "  <-- DECLARE" if rate >= TAU else ""
        print(f"  {SHORT[f]} {f:30s} {c:2d}/{n}  rate={rate:.3f}{mark}")
    print("-" * 60)
    print(f"  items tripping >=1 flag: {items_with_any}/{n} ({items_with_any/n:.3f})")
    print()
    print("A1 by genre:")
    for fam, (a, t) in sorted(genre_a1.items()):
        print(f"  {fam:24s} {a}/{t}  ({a/t:.3f})")
    print()
    for f in FLAGS:
        if fired_ids[f]:
            print(f"  {SHORT[f]} fired on: {', '.join(fired_ids[f])}")
    print()
    a1_rate = count[FLAGS[0]] / n if n else 0.0
    verdict = "PASS" if a1_rate >= TAU else "FAIL"
    print(f"R6 TARGET A1 >= {TAU}:  A1 = {a1_rate:.3f}  ->  {verdict}")


if __name__ == '__main__':
    main()
