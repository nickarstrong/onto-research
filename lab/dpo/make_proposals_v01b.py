#!/usr/bin/env python3
# make_proposals_v01b.py -- SELF-REFINEMENT seed (pack v185 STEP 1): elicit clean self-supply.
#
# Frozen base as PROPOSER under 2 honest elicitation variants (V1 abstention-permitted,
# V2 confident-binds), each emitting an asserted TITLE so the intake's expected_title is the
# model's OWN title claim -- the (b)-rescore fix banked in v185 STEP 2a (the FROZEN intake admits
# a correct binding when expected_title = real title; rung-1's reject was a claim-as-title artifact).
#
# Base load + wrapper + decode are IMPORTED byte-exact from run_ordinary_window (md5 d1f569c4) via the
# make_proposals_v01 helpers (DOI_RE / _trim_echo / _clean_doi / _after_key) -> the substrate and the
# DOI parse cannot drift from the lab's frozen path (R9). v01 is NOT edited (locked f7ed6d31); this is
# a sibling for the titled/abstaining elicitation. proposals are LOCAL-ONLY (bait-class: raw DOIs may
# be fabricated) -- NEVER public git (pack 3.2).
#
# Outcome per prompt: ABSTAIN | NO_DOI | NO_TITLE | PROPOSED. PROPOSED rows (claim,title,doi,quote)
# carry expected_verdict=L1L2_PASS so the STEP-2 intake report tallies pass=ABSORBED / fail=rejected.
#
# Run (LOCAL GPU, light job per protocol 3.7):
#   python make_proposals_v01b.py --prompts data/proposer_prompts_v01b.jsonl \
#       --out proposals_v01b.jsonl --raw-out raw_v01b.jsonl
# Dry-run (CPU, no model -- baked mock, parser+emit+tally shape only):
#   python make_proposals_v01b.py --prompts data/proposer_prompts_v01b.jsonl --dry-run --out /tmp/p.jsonl

import argparse, json, re, sys
from collections import Counter

import make_proposals_v01 as P01     # _trim_echo, _clean_doi, _after_key, DOI_RE (byte-exact reuse)
import run_ordinary_window as W      # build_model, build_bad_words_ids, generate, load_prompts

ABSTAIN_RE = re.compile(r'\[\s*no verified source\s*\]', re.I)


def classify(raw):
    """raw generation -> (outcome, row|None). outcome in ABSTAIN/NO_DOI/NO_TITLE/PROPOSED."""
    block = P01._trim_echo(raw)
    has_doi = P01.DOI_RE.search(block)
    if ABSTAIN_RE.search(block) and not has_doi:
        return "ABSTAIN", None
    if not has_doi:
        return "NO_DOI", None
    doi = P01._clean_doi(has_doi.group(0))
    if not doi:
        return "NO_DOI", None
    claim = P01._after_key(block, "CLAIM")
    if not claim:
        pre = block[:has_doi.start()].strip()
        pre = re.sub(r'(?im)^\s*(DOI|TITLE|QUOTE|SOURCE)\s*:.*$', '', pre).strip()
        pre = re.sub(r'(?im)^\s*CLAIM\s*:\s*', '', pre).strip()
        claim = pre.split("\n")[0].strip() if pre else ""
    title = P01._after_key(block, "TITLE")
    quote = P01._after_key(block, "QUOTE")
    if not claim:
        return "NO_TITLE", None     # no checkable claim
    if not title:
        return "NO_TITLE", None     # no asserted title -> no binding to check (the seed's whole point)
    return "PROPOSED", {"claim_text": claim[:400], "expected_title": title[:300],
                        "doi": doi, "star_quote": quote[:400]}


# baked mocks exercising both branches (dry-run shape only, NOT base behavior)
MOCK = {
    "V1": "CLAIM: DNA is a double helix held by base pairing.\nTITLE: Molecular Structure of Nucleic Acids\n"
          "DOI: 10.1038/171737a0\nQUOTE: a structure for deoxyribose nucleic acid.",
    "V2": "[no verified source]",
}


def main():
    ap = argparse.ArgumentParser(description="self-refinement seed: titled proposals under elicitation variants")
    ap.add_argument("--prompts", required=True, help="proposer_prompts_v01b.jsonl (id/variant/field/prompt)")
    ap.add_argument("--out", default="proposals_v01b.jsonl", help="LOCAL-ONLY PROPOSED rows (bait-class)")
    ap.add_argument("--raw-out", default="raw_v01b.jsonl", help="raw generations dump (LOCAL-ONLY)")
    ap.add_argument("--dry-run", action="store_true", help="CPU mock: no model, parser+emit+tally only")
    args = ap.parse_args()

    prompts = W.load_prompts(args.prompts)
    print("[load] %d prompts from %s" % (len(prompts), args.prompts), file=sys.stderr)
    assert len(prompts) >= 20, "STOP: need N>=20 prompts, got %d" % len(prompts)

    if args.dry_run:
        gen_fn = lambda q, v: MOCK.get(v, MOCK["V1"])
    else:
        tok, model = W.build_model(adapter=None)        # frozen base, no adapter, no GOLD
        bad = W.build_bad_words_ids(tok)
        gen_fn = lambda q, v: W.generate(tok, model, q, bad)

    tally = {}
    proposals, raw_rows = [], []
    for i, row in enumerate(prompts):
        v = row.get("variant", "V?")
        raw = gen_fn(row["prompt"], v)
        raw_rows.append({"id": row["id"], "variant": v, "raw": raw})
        outcome, rec = classify(raw)
        tally.setdefault(v, Counter())[outcome] += 1
        if outcome == "PROPOSED":
            rec.update({"id": row["id"], "variant": v, "field": row.get("field"),
                        "source": "frozen_base_qwen25coder7b", "expected_verdict": "L1L2_PASS"})
            proposals.append(rec)
        if (i + 1) % 10 == 0:
            print("  [%d/%d]" % (i + 1, len(prompts)), file=sys.stderr)

    with open(args.out, "w", encoding="utf-8") as f:
        for p in proposals:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(args.raw_out, "w", encoding="utf-8") as f:
        for r in raw_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\n=== STEP 1 ELICIT TALLY (per variant) ===", file=sys.stderr)
    for v in sorted(tally):
        c = tally[v]
        n = sum(c.values())
        print("  %s n=%d : PROPOSED=%d ABSTAIN=%d NO_DOI=%d NO_TITLE=%d"
              % (v, n, c["PROPOSED"], c["ABSTAIN"], c["NO_DOI"], c["NO_TITLE"]), file=sys.stderr)
    print("[done] %d PROPOSED rows -> %s (LOCAL-ONLY, bait-class) ; raw -> %s"
          % (len(proposals), args.out, args.raw_out), file=sys.stderr)
    print("NEXT: STEP 2 intake -> python run_provenance_L1L2.py --run %s --rwd <rwd.csv> ; pass=ABSORBED"
          % args.out, file=sys.stderr)


if __name__ == "__main__":
    main()
