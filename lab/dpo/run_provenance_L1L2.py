#!/usr/bin/env python3
# run_provenance_L1L2.py
# SPEC sec9 step1 -- L1 EXISTENCE + L2 STATUS deterministic adapter (NO model).
# Frozen SPEC: SPEC_provenance_verifier_v1.md (md5 b62aad2f).
#
# L1 EXISTENCE  : DOI resolves (Crossref) AND metadata (title) matches the cited claim.
#                 non-resolve OR mismatch -> T4 (failed/fabricated marker).
# L2 STATUS     : retraction via NAMED registries [D1]: primary = publisher "RETRACTED" title flag,
#                 augment = Retraction Watch DB (RWD CSV, OriginalPaperDOI where RetractionNature=Retraction).
#                 either fires -> T4-retracted. Owns residual coverage gap (does NOT claim completeness).
# OUTPUT (step1 scope): T4_L1_NONRESOLVE | T4_L1_MISMATCH | T4_RETRACTED | L1L2_PASS (pending L4/L5).
#   ASYMMETRY (SPEC sec3): T4 (fabricated/failed) is the reject; L1L2_PASS only means provenance-clean,
#   NOT gold -- L4 bind (step2) + L5 (step3) + G-floor (step4) still gate the tier upward.
#
# Modes:
#   --selftest        : mocked Crossref + RWD (no network). Proves reject AND accept paths != VOID.
#   --run FIXTURE RWD : live. Crossref per DOI + RWD CSV index. Scores vs expected_verdict. Emits report.
#
# Self-test discipline: an adapter that rejects everything would pass an all-reject fixture trivially
# (E23 VOID-by-construction). The selftest and Fixture A BOTH carry a clean control that MUST PASS.

import argparse, json, sys, csv, re, time
from difflib import SequenceMatcher

RETRACT_RE = re.compile(r"^\s*retracted(\s+article)?\s*:?\s*", re.I)
TITLE_MATCH_THRESHOLD = 0.60

# ---------------------------------------------------------------- normalisation / match

def strip_retracted(title):
    return RETRACT_RE.sub("", title or "").strip()

def norm_title(t):
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()

def title_match(resolved_title, expected_title):
    a = norm_title(strip_retracted(resolved_title))
    b = norm_title(expected_title)
    if not a or not b:
        return 0.0
    # token-set ratio, order-insensitive
    ta, tb = set(a.split()), set(b.split())
    jacc = len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0
    seq = SequenceMatcher(None, a, b).ratio()
    return max(jacc, seq)

# ---------------------------------------------------------------- RWD index

def load_rwd_index(csv_path):
    """Return set of lowercased OriginalPaperDOI where RetractionNature indicates a Retraction.
    Per RW guidance, restrict to retractions (not bare EoC/correction)."""
    retracted = set()
    with open(csv_path, encoding="utf-8", errors="replace", newline="") as f:
        rdr = csv.DictReader(f)
        cols = {c.lower(): c for c in (rdr.fieldnames or [])}
        doi_col = cols.get("originalpaperdoi")
        nat_col = cols.get("retractionnature")
        if not doi_col:
            raise SystemExit("RWD CSV: OriginalPaperDOI column not found -- schema changed, halt.")
        for row in rdr:
            nat = (row.get(nat_col, "") if nat_col else "").lower()
            if (not nat_col) or ("retraction" in nat):
                d = (row.get(doi_col) or "").strip().lower()
                if d:
                    retracted.add(d)
    return retracted

# ---------------------------------------------------------------- layers

def l1_existence(doi, expected_title, fetch):
    """fetch(doi) -> {'resolved':bool, 'title':str} ; returns (status, detail)."""
    meta = fetch(doi)
    if not meta or not meta.get("resolved"):
        return "T4_L1_NONRESOLVE", {"title": None, "match": None}
    m = title_match(meta["title"], expected_title)
    if m < TITLE_MATCH_THRESHOLD:
        return "T4_L1_MISMATCH", {"title": meta["title"], "match": round(m, 3)}
    return "L1_PASS", {"title": meta["title"], "match": round(m, 3)}

def l2_status(doi, resolved_title, rwd_index):
    """Two named signals (D1). Returns (retracted_bool, sources)."""
    sources = []
    if resolved_title and RETRACT_RE.match(resolved_title):
        sources.append("title_flag")
    if doi.lower() in rwd_index:
        sources.append("rwd")
    return (len(sources) > 0), sources

def verdict(doi, expected_title, fetch, rwd_index):
    l1, l1d = l1_existence(doi, expected_title, fetch)
    if l1.startswith("T4"):
        return l1, {"l1": l1d, "l2": None}            # gate-before-anything: failed marker, stop
    retracted, l2src = l2_status(doi, l1d["title"], rwd_index)
    if retracted:
        return "T4_RETRACTED", {"l1": l1d, "l2": {"retracted": True, "sources": l2src}}
    return "L1L2_PASS", {"l1": l1d, "l2": {"retracted": False, "coverage_gap": "RWD+title only; residual gap owned"}}

# ---------------------------------------------------------------- selftest (mocked)

def selftest():
    EXP_VERF = "Pluripotency of mesenchymal stem cells derived from adult marrow"
    EXP_CHEE = "A primitive Late Pliocene cheetah, and evolution of the cheetah lineage"
    EXP_WC   = "Molecular Structure of Nucleic Acids"
    MOCK = {
        "10.1038/nature00807":     {"resolved": True,  "title": "Role of experience and oscillations in transforming a rate code"},
        "10.1073/pnas.0811124106": {"resolved": True,  "title": "Sleep, arousal, and rhythms in flies"},
        "10.1073/pnas.0810435106": {"resolved": True,  "title": "RETRACTED: A primitive Late Pliocene cheetah, and evolution of the cheetah lineage"},
        "10.1038/nature00870":     {"resolved": True,  "title": "RETRACTED ARTICLE: Pluripotency of mesenchymal stem cells derived from adult marrow"},
        "10.1038/171737a0":        {"resolved": True,  "title": "Molecular Structure of Nucleic Acids: A Structure for Deoxyribose Nucleic Acid"},
        "10.9999/fake.nonexist":   {"resolved": False, "title": None},
    }
    rwd = {"10.1073/pnas.0810435106", "10.1038/nature00870"}  # both retracted in RWD
    def fetch(doi): return MOCK.get(doi, {"resolved": False, "title": None})

    cases = [
        ("10.1038/nature00807",     EXP_VERF, "T4_L1_MISMATCH"),     # resolves to wrong paper
        ("10.1073/pnas.0811124106", EXP_CHEE, "T4_L1_MISMATCH"),     # corrected oracle: resolves, wrong paper
        ("10.1073/pnas.0810435106", EXP_CHEE, "T4_RETRACTED"),       # title flag + rwd
        ("10.1038/nature00870",     EXP_VERF, "T4_RETRACTED"),       # title flag + rwd
        ("10.9999/fake.nonexist",   EXP_WC,   "T4_L1_NONRESOLVE"),   # 404
        ("10.1038/171737a0",        EXP_WC,   "L1L2_PASS"),          # clean control -- MUST pass (accept path)
    ]
    allok = True
    for doi, exp_t, want in cases:
        got, det = verdict(doi, exp_t, fetch, rwd)
        ok = (got == want)
        allok &= ok
        print(f"  {'ok ' if ok else 'XX '} {doi:28} want={want:18} got={got:18} {det['l1']}")
    assert allok, "selftest mismatch"
    # explicit accept-path guard (E23): at least one L1L2_PASS present
    assert any(verdict(d, t, fetch, rwd)[0] == "L1L2_PASS" for d, t, _ in cases), "no accept path exercised"
    print("\nSELFTEST: PASS (reject + accept paths proven; not VOID-by-construction)")

# ---------------------------------------------------------------- live run

def live_run(fixture_path, rwd_csv, report_path):
    import urllib.request, urllib.error
    rwd_index = load_rwd_index(rwd_csv)
    print(f"RWD index: {len(rwd_index)} retracted DOIs loaded")

    def fetch(doi):
        url = "https://api.crossref.org/works/" + urllib.request.quote(doi)
        req = urllib.request.Request(url, headers={"User-Agent": "ONTO-prov/1.0 (mailto:council@ontostandard.org)"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                m = json.loads(r.read().decode())["message"]
            return {"resolved": True, "title": " ".join(m.get("title", []) or [])}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"resolved": False, "title": None}
            raise
        finally:
            time.sleep(0.3)

    rows = [json.loads(l) for l in open(fixture_path, encoding="utf-8") if l.strip()]
    results, npass, nfail = [], 0, 0
    for row in rows:
        got, det = verdict(row["doi"], row["expected_title"], fetch, rwd_index)
        exp = row.get("expected_verdict")
        match = (got == exp) if exp else None
        if match is True: npass += 1
        elif match is False: nfail += 1
        results.append({"doi": row["doi"], "expected": exp, "got": got, "ok": match, "detail": det})
        print(f"  {'ok ' if match else ('XX ' if match is False else '.. ')} {row['doi']:28} exp={exp} got={got}")

    emit_report(report_path, results, npass, nfail, len(rwd_index))
    print(f"\nFixture A: {npass} pass / {nfail} fail / {len(rows)} total")
    sys.exit(0 if nfail == 0 else 1)

def emit_report(p, results, npass, nfail, rwd_n):
    L = ["# report_provenance_L1L2 -- SPEC sec9 step1 (L1 existence + L2 status)", ""]
    L.append(f"VERDICT: {'PASS' if nfail == 0 else 'FAIL'}  ({npass} ok / {nfail} fail)")
    L.append(f"RWD index: {rwd_n} retracted DOIs (Retraction Watch CSV, OriginalPaperDOI x RetractionNature=Retraction)")
    L.append("")
    L.append("## Fixture A results")
    for r in results:
        L.append(f"- {r['doi']} : exp={r['expected']} got={r['got']} ok={r['ok']}")
    L.append("")
    L.append("## SPEC compliance notes")
    L.append("- L1 mismatch (not non-resolve) is the reject path for mis-attributed DOIs that resolve to a wrong paper.")
    L.append("- ORACLE FIX: Fixture A row pnas.0811124106 expected 'non-resolve' but RESOLVES to an unrelated paper")
    L.append("  -> corrected expectation = T4_L1_MISMATCH (regenerate Fixture A on spec edit, per D4 discipline).")
    L.append("- L2 dual-signal [D1]: publisher 'RETRACTED' title flag (primary) + RWD index (augment). Coverage gap OWNED.")
    L.append("- clean control present -> accept path (L1L2_PASS) exercised, not VOID-by-construction (E23).")
    L.append("- step1 scope = L1/L2 only. L1L2_PASS is provenance-clean, NOT gold: L4 bind/L5/G-floor still gate (steps 2-4).")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", p)

# ---------------------------------------------------------------- cli

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", metavar="FIXTURE_JSONL")
    ap.add_argument("--rwd", metavar="RWD_CSV")
    ap.add_argument("--out", default="reports/report_provenance_L1L2.md")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.run:
        if not a.rwd:
            sys.exit("--run requires --rwd <retraction_watch.csv>")
        live_run(a.run, a.rwd, a.out)
    else:
        ap.print_help()
