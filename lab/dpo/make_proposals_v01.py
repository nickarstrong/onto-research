#!/usr/bin/env python3
# make_proposals_v01.py -- LOOP v0.1 S1: live frozen substrate as the PROPOSER.
#
# Prompts the FROZEN base (Qwen2.5-Coder-7B, 4-bit nf4, greedy, NO adapter, NO GOLD) for a
# {claim + supporting DOI}, parses the generation into the gate's proposal schema, and writes
# proposals_v01.jsonl -- the input loop_e2e_v0.py --run (a39e66f, UNCHANGED) reads.
#
# The base load + wrapper + decode are IMPORTED byte-exact from run_ordinary_window.py (md5
# d1f569c4): build_model / format_example / build_bad_words_ids / generate. NOT re-typed -> the
# substrate cannot drift from the lab's established frozen-base path (R9, the step3/step4a lesson).
# This script adds ONLY: a deterministic parser (generation -> claim/doi/quote) + the emit.
#
# The phenomenon under test (load-bearing assumption, R2): the base WILL emit parseable claim+DOI
# rows, and SOME of those DOIs WILL be non-resolving / wrong -- that is exactly what v0.1 measures
# (the substrate's OWN off-plant fabrication/retraction rate, fed to the same v0 veto).
#
# proposals_v01.jsonl is LOCAL-ONLY (bait-class: it carries the substrate's raw, possibly fabricated
# DOIs). NEVER public git, same handling as proposals_v0.jsonl / bait-sets (pack 3.2).
#
# Run (pod, GPU mandatory):
#   python make_proposals_v01.py --prompts proposer_prompts_v01.jsonl --out proposals_v01.jsonl
# Dry-run (CPU, no model -- validates parser + emit shape on a baked mock, NOT base behavior):
#   python make_proposals_v01.py --prompts proposer_prompts_v01.jsonl --dry-run --out /tmp/p.jsonl

import argparse, json, re, sys
from pathlib import Path

# byte-exact frozen-base path (do NOT re-implement; import so format cannot drift, R9)
import run_ordinary_window as W   # build_model, format_example, build_bad_words_ids, generate, load_prompts

# a DOI: 10.<registrant>/<suffix>. The suffix MAY contain balanced parens (Elsevier PII DOIs,
# e.g. 10.1016/S0006-8993(00)89707-7) -> include () in the class, terminate on whitespace/quote/angle.
DOI_RE = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')
# echo-loop guard: the non-instruct base re-emits the wrapper; isolate the FIRST response block
ECHO_MARKS = ("### Instruction", "### Response")
TRAIL = ".,;:"                  # sentence punctuation to strip off a parsed DOI (NOT parens)


def _trim_echo(text):
    """Cut at the first reoccurrence of the wrapper (base echo-loops; keep only the 1st block)."""
    cut = len(text)
    for m in ECHO_MARKS:
        i = text.find(m)
        if i != -1:
            cut = min(cut, i)
    return text[:cut].strip()


def _clean_doi(d):
    d = d.strip()
    # strip trailing sentence punctuation (keep DOI-internal chars incl. balanced parens)
    while d and d[-1] in TRAIL:
        d = d[:-1]
    # strip a trailing ')' ONLY if unbalanced (a wrapper paren, not an Elsevier PII paren)
    while d.endswith(")") and d.count(")") > d.count("("):
        d = d[:-1].rstrip(TRAIL)
    return d


def _after_key(block, key):
    """Return the text after a 'KEY:' label up to end-of-line, else ''. Case-insensitive key."""
    m = re.search(r'(?im)^\s*' + re.escape(key) + r'\s*:\s*(.+?)\s*$', block)
    return m.group(1).strip() if m else ""


def parse_proposal(raw):
    """generation text -> (claim_text, doi, star_quote) or None if no DOI emitted.
    Format-tolerant: prefers CLAIM:/DOI:/QUOTE: labels, falls back to first-DOI + surrounding text.
    The proposer that emits no DOI made no citation -> not a proposal (dropped, counted)."""
    block = _trim_echo(raw)
    m = DOI_RE.search(block)
    if not m:
        return None
    doi = _clean_doi(m.group(0))
    if not doi:
        return None

    claim = _after_key(block, "CLAIM")
    if not claim:
        # fallback: the text before the DOI line, first non-empty sentence, label-stripped
        pre = block[:m.start()].strip()
        pre = re.sub(r'(?im)^\s*(DOI|QUOTE|SOURCE)\s*:.*$', '', pre).strip()
        # drop a leading "CLAIM:" if present without a captured value
        pre = re.sub(r'(?im)^\s*CLAIM\s*:\s*', '', pre).strip()
        claim = pre.split("\n")[0].strip() if pre else ""
    claim = claim[:400].strip()

    quote = _after_key(block, "QUOTE")
    quote = quote[:400].strip()

    if not claim:
        return None  # a bare DOI with no claim is not a checkable proposal
    return claim, doi, quote


def main():
    ap = argparse.ArgumentParser(description="LOOP v0.1 S1: frozen substrate -> {claim,doi} proposals")
    ap.add_argument("--prompts", required=False, help="proposer_prompts_v01.jsonl (id/field/prompt)")
    ap.add_argument("--out", default="proposals_v01.jsonl", help="LOCAL-ONLY proposals (bait-class)")
    ap.add_argument("--raw-out", default=None, help="optional: dump raw generations for audit (LOCAL-ONLY)")
    ap.add_argument("--dry-run", action="store_true", help="CPU: baked mock generations, parser+emit only")
    ap.add_argument("--reparse", default=None, metavar="RAW",
                    help="CPU: re-derive proposals from a frozen raw dump ({id,raw}) -- no model, "
                         "deterministic. Use after a parser fix to avoid re-generation.")
    args = ap.parse_args()

    # --reparse: deterministic re-parse of the frozen substrate output (no GPU, no model load)
    if args.reparse:
        raw_rows = [json.loads(l) for l in open(args.reparse, encoding="utf-8") if l.strip()]
        print("[reparse] %d raw rows from %s (no model)" % (len(raw_rows), args.reparse), file=sys.stderr)
        proposals, dropped = [], []
        for r in raw_rows:
            parsed = parse_proposal(r["raw"])
            if parsed is None:
                dropped.append(r["id"]); continue
            claim, doi, quote = parsed
            proposals.append({"id": r["id"], "claim_text": claim, "doi": doi, "star_quote": quote,
                              "source": "frozen_base_qwen25coder7b", "planted": "substrate_v01"})
        with open(args.out, "w", encoding="utf-8") as f:
            for p in proposals:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        print("[done] reparse kept %d dropped %d -> %s" % (len(proposals), len(dropped), args.out),
              file=sys.stderr)
        if dropped:
            print("[dropped] " + ", ".join(dropped), file=sys.stderr)
        if len(proposals) < 20:
            print("[WARN] < 20 proposals kept (need N>=20 before the gate).", file=sys.stderr)
        return


    if not args.prompts:
        ap.error("--prompts is required unless --reparse is given")
    prompts = W.load_prompts(args.prompts)
    print("[load] %d proposer prompts from %s" % (len(prompts), args.prompts), file=sys.stderr)
    assert len(prompts) >= 20, "STOP: need N>=20 proposer prompts, got %d" % len(prompts)

    if args.dry_run:
        # baked mock outputs exercising the parser branches: labeled, unlabeled-fallback, no-doi.
        MOCK = [
            "CLAIM: DNA is a double helix held by base pairing.\nDOI: 10.1038/171737a0\nQUOTE: It has not escaped our notice that the specific pairing we have postulated suggests a copying mechanism.",
            "The Higgs boson was observed near 125 GeV at the LHC.\n10.1016/j.physletb.2012.08.020\nas reported by the ATLAS collaboration.",
            "CLAIM: Vaccines train memory B cells.\nDOI: 10.0000/this-one-does-not-resolve.\nQUOTE: memory persists for years.",
            "I am not certain of a specific source for this claim about plate tectonics.",
            "### Instruction:\nSomething\n### Response:\nCLAIM: leaked second block must be ignored.\nDOI: 10.9999/should-not-appear",
        ]
        gen_fn = lambda q, i: MOCK[i % len(MOCK)]
    else:
        tok, model = W.build_model(adapter=None)          # frozen base, no adapter, no GOLD
        bad = W.build_bad_words_ids(tok)
        gen_fn = lambda q, i: W.generate(tok, model, q, bad)

    proposals, dropped, raw_rows = [], [], []
    for i, row in enumerate(prompts):
        raw = gen_fn(row["prompt"], i)
        raw_rows.append({"id": row["id"], "raw": raw})
        parsed = parse_proposal(raw)
        if parsed is None:
            dropped.append(row["id"])
            continue
        claim, doi, quote = parsed
        proposals.append({
            "id": row["id"],
            "claim_text": claim,
            "doi": doi,
            "star_quote": quote,
            "source": "frozen_base_qwen25coder7b",   # provenance; gate ignores it
            "planted": "substrate_v01",              # NOT a planted falsifier -> v0.1 disposition table
        })
        if (i + 1) % 6 == 0:
            print("  [%d/%d] kept=%d dropped=%d" % (i + 1, len(prompts), len(proposals), len(dropped)),
                  file=sys.stderr)

    with open(args.out, "w", encoding="utf-8") as f:
        for p in proposals:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    if args.raw_out:
        with open(args.raw_out, "w", encoding="utf-8") as f:
            for r in raw_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("[done] kept %d proposals (with parseable claim+DOI), dropped %d (no DOI/no claim) -> %s"
          % (len(proposals), len(dropped), args.out), file=sys.stderr)
    if dropped:
        print("[dropped] " + ", ".join(dropped), file=sys.stderr)
    if len(proposals) < 20:
        print("[WARN] < 20 proposals kept. Add proposer prompts and re-run before the gate (need N>=20).",
              file=sys.stderr)
    print("=== PROPOSALS DONE === LOCAL-ONLY (bait-class). Next: SEPARATE TYPE B gate-run session.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
