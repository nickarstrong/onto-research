#!/usr/bin/env python3
# o0_layer2_driver_v308.py -- COMPOSED DRIVER for wired numprop build.
# Routes: year leg -> frozen oracle (read-only import), numprop leg -> o0_layer2_numprop module.
# ZERO edit to frozen anchors (oracle 0e59ae0f, probe b231da36, verifier 92766b06).
# The frozen oracle's `oracle_numeric` ABSTAIN no-op is BYPASSED: this driver calls the year leg
# functions from the frozen oracle, then calls the new numprop module, and composes the result.
# Combination: REFUTE > CONFIRM > ABSTAIN (either leg can REFUTE).
# Usage:
#   python o0_layer2_driver_v308.py <input.jsonl> <output.jsonl>
import json, os, re, sys, time

# --- frozen imports (read-only; these modules are NOT edited) ---
import o0_temporal_probe_v5 as T
import o0_layer2_oracle as oracle
import o0_layer2_numprop as numprop

REFUTE, CONFIRM, ABSTAIN = "REFUTE", "CONFIRM", "ABSTAIN"


def _combine(yr, nm):
    """Combine year-leg and numeric-leg collapses into overall verdict."""
    if REFUTE in (yr, nm):
        return REFUTE
    if CONFIRM in (yr, nm):
        return CONFIRM
    return ABSTAIN


_CAP_SUBJ = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b")


def extract_subjects(claim):
    """Extract subject labels from claim text for the numprop resolver.
    Combines frozen probe's extract_subjects_in_sentence + oracle's reconstruct_titles +
    a regex fallback for capitalized entity names."""
    subjects = []
    seen = set()

    def _add(s):
        sl = s.lower()
        if sl not in seen:
            subjects.append(s)
            seen.add(sl)

    # primary: frozen probe's extractor (defensive: year=None may not be supported)
    try:
        for sent in T.split_sentences(claim or ""):
            for s in T.extract_subjects_in_sentence(sent, None):
                _add(s)
    except Exception:
        pass

    # secondary: connector-bridged title runs (v296 Option A)
    try:
        for t in oracle.reconstruct_titles(claim or ""):
            _add(t)
    except Exception:
        pass

    # fallback: regex capitalized entity names (if above produced nothing)
    if not subjects:
        for m in _CAP_SUBJ.findall(claim or ""):
            if m not in ("The", "According", "In", "Its", "This", "That", "However"):
                _add(m)

    return subjects


def process_record(rec, cache, art_cache):
    """Process one record: frozen year-leg (direct call) + wired numprop-leg."""
    claim = rec.get("claim", "")
    topic = rec.get("topic", "")

    # 1. year leg: call frozen oracle_year directly (returns tuple: verdict, detail_dict)
    try:
        yr_result = oracle.oracle_year(claim, topic, T, cache, art_cache)
        if isinstance(yr_result, tuple):
            yr_collapse = yr_result[0] if isinstance(yr_result[0], str) else ABSTAIN
            yr_detail = yr_result[1] if len(yr_result) > 1 and isinstance(yr_result[1], dict) else {}
        else:
            yr_collapse = ABSTAIN
            yr_detail = {}
    except Exception:
        yr_collapse = ABSTAIN
        yr_detail = {}
    year_part = {"collapse": yr_collapse, "per_year": yr_detail.get("per_year", yr_detail)}

    # 2. numprop leg: call new module
    subjects = extract_subjects(claim)
    nv, nd = numprop.numprop_verdict(claim, topic, subjects)
    numeric_part = {"collapse": nv, "per_specific": nd}

    # 3. combine
    overall = _combine(yr_collapse, nv)

    return {
        "verdict": overall,
        "year": year_part,
        "numeric": numeric_part,
    }


def run(in_path, out_path):
    """Main entry: read records, process each, write output."""
    numprop.load_domain_map()
    numprop.load_cache()
    cache = {}       # year-leg entity cache (frozen oracle's)
    art_cache = {}   # year-leg article cache (frozen oracle's)

    records = [json.loads(l) for l in open(in_path, encoding="utf-8") if l.strip()]
    results = []
    for rec in records:
        r = process_record(rec, cache, art_cache)
        out = {"id": rec["id"], "layer2": r}
        results.append(out)
        tag = r["verdict"]
        yr = r["year"].get("collapse", "?")
        nm = r["numeric"].get("collapse", "?")
        print("  %-18s layer2=%-7s year=%-7s numprop=%-7s" % (rec["id"], tag, yr, nm))

    numprop.save_cache()

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for x in results:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    nc = sum(1 for x in results if x["layer2"]["verdict"] == CONFIRM)
    nr = sum(1 for x in results if x["layer2"]["verdict"] == REFUTE)
    na = sum(1 for x in results if x["layer2"]["verdict"] == ABSTAIN)
    print("[driver_v308] %d rows -> %s" % (len(results), out_path))
    print("[driver_v308] CONFIRM=%d REFUTE=%d ABSTAIN=%d" % (nc, nr, na))


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "heldout_numprop_liveform_v308.jsonl"
    out = sys.argv[2] if len(sys.argv) > 2 else "numprop_wired_v308_verdicts.jsonl"
    run(inp, out)
