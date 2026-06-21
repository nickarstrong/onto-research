#!/usr/bin/env python3
# o0_temporal_evidence.py -- ORGAN EVIDENCE WIRE (ROADMAP step 3).
# Wires the FROZEN V6 temporal CONFIRM channel (o0_temporal_probe_v5.py) into the
# self-model organ's specifics check, as an out-of-band evidence layer.
#
# WHY: the §3 organ card rule "specific not in retrieved evidence -> DIRTY" SATURATES
# to reject-all on the held-out's empty crossref abstracts (36/48 empty) -> ff=1.000.
# The temporal channel CONFIRMS a true date from Wikidata/Wikipedia even when the
# abstract is empty, so a CLEAN claim's true date no longer reads as "unsupported".
#
# WHAT THIS DOES: for each blind claim, for each load-bearing year (a year in the claim
# NOT already covered by the abstract), call the frozen verify_year() and record
# CONFIRM | REFUTE | ABSTAIN. Emits an augmented evidence file the auditor reads at B1''.
#
# FROZEN REUSE (no drift): imports verify_year / extract_years / sentence_of_year /
# event_predicates_for / _TOK from o0_temporal_probe_v5 UNCHANGED. This script adds NO
# verdict logic -- it only drives the frozen channel over the 48 and packages the result.
#
# E15: authors NO labels. Pure derivation over blind claims + public oracles.
# COMPUTE: live HTTP to Wikidata/Wikipedia, pure stdlib, NO GPU -> LOCAL (network-bound,
#          ~0.3s sleep per resolve; 48 claims ~ a few minutes).
#
# Usage:  python o0_temporal_evidence.py [claims_blind_ev.jsonl] [claims_blind_ev_temporal.jsonl]

import json, re, sys

# NOTE: o0_temporal_probe_v5 (frozen V6) is imported LAZILY inside run() only.
# The deterministic scope functions below (extract_*, scope_verdict) need no probe and
# no network, so the offline self-test can import this module without the frozen probe present.

# --- transient claim cleanup for PARSING ONLY (the original claim is preserved in output) ---
# The held-out claims carry Ollama terminal-capture junk: ANSI control sequences
# (ESC[K, ESC[13D) and stray control chars. Years/numbers survive, but sentence
# splitting can choke on embedded control chars. We strip them for extraction only;
# the judge sees the ORIGINAL claim (so it stays byte-aligned to the sealed labels).
_ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
_CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')

def clean_for_parse(claim):
    s = _ANSI.sub(" ", claim or "")
    s = _CTRL.sub(" ", s)
    s = s.replace("\n", " ")
    return re.sub(r'\s+', " ", s).strip()

# --- sec 4 cheap fold: widen year visibility (was T.extract_years = 1[89]\d{2}|20\d{2}) -----------
# CE 1000-2099 (so Newton 1687 / Coulomb 1785 become temporal-VISIBLE). Word-boundary + 4-digit
# guards against bare 1-3 digit numbers that are NOT years. BCE requires an explicit BC/BCE marker
# (sec 4 guard) and is routed to ABSTAIN -- the frozen verify_year takes a 4-digit CE arg only, so
# a BCE token must NOT be fed to it; it is made visible but not confirmable through the frozen channel.
_YEAR_CE  = re.compile(r'\b(1\d{3}|20\d{2})\b')
_YEAR_BCE = re.compile(r'\b(\d{1,4})\s*(?:BCE|BC|B\.C\.)\b', re.I)

def extract_years_ext(text):
    ce  = list(dict.fromkeys(_YEAR_CE.findall(text)))            # ordered-unique 4-digit CE
    bce = list(dict.fromkeys("-" + y for y in _YEAR_BCE.findall(text)))  # tagged, visibility-only
    return ce, bce

# --- typed non-year specifics (spec 2.1) ----------------------------------------------------------
_MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December")
_FULLDATE = re.compile(r'(?:%s)\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}(?:st|nd|rd|th)?\s+(?:%s)'
                       % (_MONTHS, _MONTHS), re.I)
# NUMBER = percentages and fractions only (the v219 fa_live class: "56.3%", "8/14"). Kept narrow on
# purpose -- gating every integer in prose would inject false specifics; names/places are the
# SEPARATE out-of-band ff plane (v218), intentionally not gated on the safety axis here.
_NUMBER = re.compile(r'\b\d{1,3}(?:\.\d+)?\s*%|\b\d+\s*/\s*\d+\b')

def extract_fulldates(text):
    return [m.group(0).strip() for m in _FULLDATE.finditer(text)]

def extract_numbers(text):
    return [m.group(0).strip() for m in _NUMBER.finditer(text)]

def _norm(s):
    return re.sub(r'\s+', " ", (s or "")).strip().lower()

def _specific_supported(spec, pool_low):
    # literal normalized presence in (abstract  UNION  confirming snippet). Precision-first:
    # literal-only -- a softer fuzzy match risks FALSE support, which is the unsafe direction.
    return _norm(spec) in pool_low

def scope_verdict(rec):
    """Deterministic claim verdict under the locked scope rule (REPORT_organ_subclaim_scope_v1
       sec 2.1-2.3), SAFETY axis = YEAR / FULL_DATE / NUMBER.

       - A year CONFIRM licenses ONLY the year token (and the subject the resolution matched =
         "resolved out-of-band", spec 2.2). It NEVER sets a claim-level support flag.
       - REFUTE on the year -> claim DIRTY (hard).
       - Each FULL_DATE / NUMBER specific must appear in the abstract OR the temporal confirming
         snippet; absent -> UNVERIFIED -> claim DIRTY (precision-first).
       - NAME / PLACE gating = the separate ff / out-of-band plane (v218); NOT gated here, because
         gating the subject name against an empty abstract would regress year-only CLEANs
         (falsifier sec 5 secondary guard).

       Returns (verdict, reasons). verdict in {"CLEAN","DIRTY"}.
    """
    parse    = clean_for_parse(rec.get("claim"))
    temporal = rec.get("temporal", {})
    per_year = temporal.get("per_year", {})
    snip     = " ".join((s.get("snippet") or "")
                        for s in temporal.get("snippets", {}).values())
    abstract = (rec.get("evidence", {}) or {}).get("abstract") or ""
    pool_low = _norm(abstract + " " + snip)

    if "REFUTE" in per_year.values():
        bad = [y for y, v in per_year.items() if v == "REFUTE"]
        return "DIRTY", ["year_refuted:" + ",".join(bad)]

    reasons = []
    for spec in extract_fulldates(parse) + extract_numbers(parse):
        if not _specific_supported(spec, pool_low):
            reasons.append("unverified_non_year_specific:%r" % spec)
    if reasons:
        return "DIRTY", reasons
    return "CLEAN", ["year+subject supported; no unverified date/number specific"]

def collapse(per_year):
    """Same claim-level collapse as the frozen probe's run_row tail (REFUTE > ABSTAIN;
       all-CONFIRM -> CONFIRM; no load-bearing year -> N/A)."""
    lb = {y: v for y, v in per_year.items() if v != "COVERED_IN_ABSTRACT"}
    if "REFUTE" in lb.values():
        return "REFUTE"
    if lb and all(v == "CONFIRM" for v in lb.values()):
        return "CONFIRM"
    if not lb:
        return "N/A_no_loadbearing_year"
    return "ABSTAIN"

def run(in_path, out_path):
    import o0_temporal_probe_v5 as T   # frozen V6 probe (lazy: only the live wire needs it)
    rows = [json.loads(l) for l in open(in_path, encoding="utf-8") if l.strip()]
    n_clean = n_dirty = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows:
            claim_orig = r["claim"]
            claim = clean_for_parse(claim_orig)
            abstract_low = (r.get("evidence", {}).get("abstract") or "").lower()
            ctx = T._TOK(claim)
            years_ce, years_bce = extract_years_ext(claim)   # sec 4 widened range
            per_year, snippets = {}, {}
            for y in years_ce:
                if y in abstract_low:
                    per_year[y] = "COVERED_IN_ABSTRACT"
                    continue
                sent = T.sentence_of_year(claim, y)
                v, log = T.verify_year(y, sent, ctx)
                per_year[y] = v
                # carry the confirming snippet (if any) so the auditor can see the basis
                for t in log.get("tried", []):
                    if isinstance(t, dict) and t.get("confirm"):
                        snippets[y] = {"qid": t.get("qid"), "via": t.get("confirm"),
                                       "snippet": t.get("snippet", "")}
                        break
            for yb in years_bce:
                # visible but not confirmable through the frozen CE-only channel (sec 4 guard)
                per_year[yb] = "ABSTAIN_BCE_unverifiable"
            cv = collapse(per_year)            # YEAR-LEVEL diagnostic ONLY -- NOT a claim support flag
            out = dict(r)
            sv, sr = scope_verdict({**r, "temporal": {"per_year": per_year, "snippets": snippets}})
            n_clean += sv == "CLEAN"; n_dirty += sv == "DIRTY"
            out["temporal"] = {
                "per_year": per_year,
                "snippets": snippets,
                "year_collapse": cv,                 # diagnostic: year sub-claim state, not claim support
                "scope": {"verdict": sv, "reasons": sr},   # claim-level safety verdict (2.3)
            }
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            print("  %-14s years=%-18s year=%-9s scope=%s" %
                  (r["id"], ",".join(years_ce) or "-", cv, sv))
    print("\n[temporal] %d claims -> %s" % (len(rows), out_path))
    print("[temporal] SCOPE claim_verdict: CLEAN=%d DIRTY=%d" % (n_clean, n_dirty))
    print("[temporal] a year CONFIRM supports the YEAR sub-claim only; non-year date/number "
          "specifics are gated independently (precision-first).")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "claims_blind_ev.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "claims_blind_ev_temporal.jsonl"
    run(src, dst)
