#!/usr/bin/env python3
"""o0_specifics_filter.py -- Post-B2 specifics-coverage filter.

After B2 says SUPPORTS, checks whether key specifics (years, proper nouns)
from the claim actually appear in the abstract. Absent specifics = UNVERIFIED
= downgrade SUPPORTS -> UNCLEAR.

Usage (test on S4 data):
  python o0_specifics_filter.py --enriched eval/o0/o0_s4_enriched.jsonl --verdicts eval/o0/o0_s4_b2_verdicts.jsonl

Standalone function for pipeline integration:
  from o0_specifics_filter import specifics_check
  result = specifics_check(claim_text, abstract_text)
  # result["pass"] = True/False, result["unverified"] = list of absent specifics
"""

import json, re, sys, argparse


# --- Core filter ---

def extract_years(text):
    """Extract 4-digit years (1800-2099) from text."""
    return list(set(re.findall(r'\b(1[89]\d{2}|20\d{2})\b', text)))


def extract_proper_nouns(text):
    """Extract likely proper nouns (names of people, places, things).
    Heuristic: capitalized words not at sentence start, excluding common words."""
    # Split into sentences, skip first word of each
    stopwords = {
        'The', 'This', 'These', 'That', 'Those', 'In', 'As', 'According',
        'However', 'Furthermore', 'Moreover', 'Although', 'Because', 'Since',
        'While', 'When', 'Where', 'Which', 'What', 'How', 'Its', 'Their',
        'His', 'Her', 'Our', 'If', 'But', 'And', 'Or', 'Not', 'For',
        'With', 'From', 'About', 'After', 'Before', 'During', 'Between',
        'Through', 'Into', 'Over', 'Under', 'Each', 'Every', 'Both',
        'Such', 'Other', 'Another', 'Some', 'Any', 'All', 'Most', 'Many',
        'Much', 'Several', 'Few', 'No', 'One', 'Two', 'Three',
        'A', 'An', 'Of', 'To', 'By', 'On', 'At', 'It', 'Is', 'Was',
        'Are', 'Were', 'Be', 'Been', 'Being', 'Has', 'Had', 'Have',
        'Do', 'Does', 'Did', 'Will', 'Would', 'Could', 'Should', 'May',
        'Might', 'Can', 'Shall', 'Must', 'Also', 'Just', 'Even', 'Still',
        'Only', 'Very', 'So', 'Too', 'Then', 'Now', 'Here', 'There',
        'Thus', 'Hence', 'Therefore', 'Subsequently', 'Approximately',
        'Notably', 'Specifically', 'Particularly', 'Generally',
    }

    # Find capitalized words/phrases (2+ chars, not all-caps abbreviations)
    # Pattern: capitalized word possibly followed by more capitalized words
    candidates = re.findall(r'\b([A-Z][a-z]{1,}(?:\s+[A-Z][a-z]{1,})*)\b', text)

    proper = []
    for c in candidates:
        # Skip if it's a single stopword
        if c in stopwords:
            continue
        # Skip generic science terms that happen to be capitalized at sentence start
        words = c.split()
        # Keep multi-word proper nouns (likely real names)
        if len(words) >= 2:
            proper.append(c)
        # Single word: keep if it's not a common word
        elif c not in stopwords and len(c) > 2:
            proper.append(c)

    return list(set(proper))


def extract_specific_numbers(text):
    """Extract numbers that are part of specific claims (with units or context).
    Focus on numbers that identify a specific measurement/value."""
    patterns = []
    # Numbers with units: "500 km/s", "299,792 km/s", "6.626", "33/36", "30%"
    for m in re.finditer(r'(\d+(?:[.,]\d+)?)\s*(%|km/?s|km|mph|Hz|GHz|MHz|eV|keV|MeV|GeV|'
                         r'J[·\s]*s|degrees?|°[CFK]?|per\s+megaparsec|Mpc|'
                         r'meters?|years?|days?|hours?)', text):
        patterns.append(m.group(1))  # just the number part
    # Fractions: "33 out of 36", "33/36"
    for m in re.finditer(r'(\d+)\s+out\s+of\s+(\d+)', text):
        patterns.append(m.group(1))
        patterns.append(m.group(2))
    for m in re.finditer(r'(\d+)/(\d+)', text):
        patterns.append(m.group(1))
        patterns.append(m.group(2))
    return list(set(patterns))


def specifics_check(claim_text, abstract_text):
    """Check if abstract covers the key specifics in the claim.

    Returns dict with:
      pass: bool (all specifics found)
      specifics: list of {type, value, found}
      unverified: list of absent specifics
    """
    if not abstract_text:
        return {"pass": False, "specifics": [], "unverified": [],
                "reason": "no_abstract"}

    abstract_lower = abstract_text.lower()

    specifics = []

    # Years
    for y in extract_years(claim_text):
        found = y in abstract_text
        specifics.append({"type": "year", "value": y, "found": found})

    # Proper nouns
    for pn in extract_proper_nouns(claim_text):
        # Check case-insensitive; also check surname-only for multi-word names
        found = pn.lower() in abstract_lower
        if not found and ' ' in pn:
            # Try last name only (e.g., "Edwin Hubble" -> "Hubble")
            surname = pn.split()[-1]
            if len(surname) > 2:
                found = surname.lower() in abstract_lower
        specifics.append({"type": "proper_noun", "value": pn, "found": found})

    # Specific numbers (optional, more aggressive)
    for num in extract_specific_numbers(claim_text):
        found = num in abstract_text
        specifics.append({"type": "number", "value": num, "found": found})

    unverified = [s for s in specifics if not s["found"]]

    return {
        "pass": len(unverified) == 0,
        "total": len(specifics),
        "verified": len(specifics) - len(unverified),
        "unverified_count": len(unverified),
        "specifics": specifics,
        "unverified": unverified,
    }


# --- v2: targeted-retrieval conjunction rescue (BUILD, binds REPORT_S4 sec5) ---
#
# v1 (specifics_check) FAILs whenever a load-bearing specific is absent from the
# single topic-level best_abstract. That conflates "absent from THIS abstract"
# with "unverified" -> over-rejects CLEAN claims (S4 G3 yield 0.05).
#
# v2 keeps v1 as the first pass. On v1 FAIL it does ONE targeted-retrieval rescue:
#   query = "{verified anchors} {in-scope unverified specifics}"  (conjunction)
#   -> fetch alt abstracts (Crossref + OpenAlex)
#   -> CONFIRM only if a SINGLE alt abstract contains ALL in-scope unverified
#      specifics AND >=1 verified anchor (subject binding).
#
# The AND-in-ONE-abstract rule is the safety hinge: it confirms the binding the
# claim asserts, not each token independently. Binding-fabrications (heldout_18
# "Cleverbot passed in 2014" = real event was Goostman; heldout_03 "1925" vs the
# 1929 redshift-distance discovery) are never co-bound in any source -> stay FAIL.
# Real bindings (Hertz+Maxwell+1887, Semmelweis+1847+Vienna) co-occur -> rescued.
#
# In-scope = years + proper nouns (minus leading-article sentence-fragment junk,
# REPORT_S4 sec5 lever1). Bare numbers are incidental: dropped (non-blocking).

_ARTICLE_LED = ("the ", "a ", "an ", "this ", "that ", "these ", "those ")


# --- v2 retrieve-side fix (pack v207): subject-only query + relaxed match ---
# v206 DEFECT = conjunction query stuffed anchors+specifics into one API query ->
# pool collapsed (n_alt 1-2) -> rescue starved. Fix: query on SUBJECT only
# (anchors + unverified proper-noun names + topic keywords); years/numbers are
# verified in the CHECK by co-occurrence, never put in the query. Token match in
# the check relaxed: year exact; proper noun by last significant token.

_TOPIC_STOP = set(w.lower() for w in [
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'and', 'or', 'but',
    'nor', 'for', 'of', 'to', 'in', 'on', 'at', 'by', 'with', 'from', 'as',
    'is', 'was', 'are', 'were', 'be', 'been', 'being', 'has', 'had', 'have',
    'its', 'it', 'their', 'his', 'her', 'which', 'who', 'when', 'where', 'what',
    'how', 'than', 'then', 'also', 'such', 'into', 'over', 'under', 'about',
    'between', 'through', 'during', 'first', 'known', 'discovered', 'proposed',
    'showed', 'found', 'demonstrated', 'described', 'called', 'used', 'using',
    'based', 'study', 'research', 'paper', 'results', 'result', 'effect',
    'theory', 'model', 'approximately', 'around', 'while', 'because', 'since',
    'they', 'were', 'made', 'work', 'works', 'show', 'shown', 'between',
])


def _last_token(value):
    """Last significant (len>=3) whitespace token of a value, lowercased.
    'Heinrich Hertz' -> 'hertz'; 'Vienna' -> 'vienna'."""
    toks = [t for t in re.split(r'\s+', (value or "").strip()) if len(t) >= 3]
    return (toks[-1] if toks else (value or "").strip()).lower()


def _spec_in_abstract(spec, abstract_low):
    """Relaxed presence test for ONE in-scope specific (lever 3).
    year       -> exact substring (no relaxation; the disputed value itself).
    proper noun-> full phrase OR last significant token (surname/place word)."""
    v = (spec.get("value") or "").lower().strip()
    if not v:
        return False
    if spec.get("type") == "year":
        return v in abstract_low
    if v in abstract_low:
        return True
    return _last_token(v) in abstract_low


def _anchor_in_abstract(anchor_low, abstract_low):
    """Anchor (verified subject term) present by phrase or last token."""
    if anchor_low in abstract_low:
        return True
    return _last_token(anchor_low) in abstract_low


def _topic_keywords(claim_text, exclude, max_kw=4):
    """Salient content keywords from the claim for the subject query.
    Drops stopwords, the in-scope specific tokens (so years / disputed names do
    not sneak back into the query), and short words. Order-preserving, capped."""
    excl = set()
    for v in exclude:
        for t in re.split(r'\s+', str(v).lower()):
            if t:
                excl.add(t)
    out = []
    for tok in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", claim_text):
        tl = tok.lower()
        if tl in _TOPIC_STOP or tl in excl or tl in out:
            continue
        out.append(tl)
        if len(out) >= max_kw:
            break
    return out


def _is_loadbearing(spec):
    """In-scope for rescue: years and real named-entity proper nouns.
    Drops bare numbers (incidental) and leading-article sentence-fragment junk
    ('The Doppler', 'The Maxwell') per REPORT_S4_specifics_gate.md sec5 lever1.
    """
    t = spec.get("type")
    v = (spec.get("value") or "").strip()
    if t == "year":
        return True
    if t == "proper_noun":
        if v.lower().startswith(_ARTICLE_LED):
            return False
        return len(v) >= 3
    # type == "number" (bare statistic) -> incidental
    return False


def specifics_check_v2(claim_text, abstract_text, retrieve_fn,
                       top_k=10, log=None):
    """Targeted-retrieval rescue around specifics_check (v1).

    claim_text     : the proposed claim
    abstract_text  : best_abstract from primary retrieval (frozen for S4)
    retrieve_fn    : callable(query_str, top_k) -> list[dict] with key "abstract"
                     (e.g. a Crossref+OpenAlex dual-query fetcher). If None,
                     behaves exactly like v1 (no rescue).
    log            : optional list; appended with a trace dict.

    Returns the v1 result dict, plus:
      rescued     : bool
      method      : "v1_pass" | "incidental_only" | "rescued" | "no_rescue"
      rescue_doi  : DOI of the confirming abstract (if rescued)
      inscope     : list of in-scope unverified specific values
    """
    base = specifics_check(claim_text, abstract_text)

    if base["pass"]:
        base.update({"rescued": False, "method": "v1_pass",
                     "rescue_doi": None, "inscope": []})
        return base

    inscope = [u for u in base["unverified"] if _is_loadbearing(u)]
    inscope_vals = [u["value"] for u in inscope]
    base["inscope"] = inscope_vals

    # Only incidental (bare-number / junk) specifics were missing -> not a
    # fabrication signal. Pass (v1's number-strictness was the false-reject).
    if not inscope:
        base["pass"] = True
        base.update({"rescued": True, "method": "incidental_only",
                     "rescue_doi": None})
        return base

    if retrieve_fn is None:
        base.update({"rescued": False, "method": "no_rescue_no_retriever",
                     "rescue_doi": None})
        return base

    anchors = [s["value"] for s in base["specifics"] if s["found"]]
    anchors = [a for a in anchors if not a.lower().startswith(_ARTICLE_LED)]

    # in-scope split: proper-noun names identify the SUBJECT (-> into the query);
    # years are what we VERIFY by co-occurrence (NEVER into the query -- that is
    # the v206 over-constraint that collapsed the pool). bare numbers already out.
    inscope_pn = [u["value"] for u in inscope if u["type"] == "proper_noun"]

    # SUBJECT-only query: verified anchors + unverified proper-noun names + topic
    # keywords from the claim. NO years/numbers. e.g. "Maxwell Hertz
    # electromagnetic waves"; "Semmelweis childbed fever Vienna".
    q_terms = []
    for a in anchors[:2] + inscope_pn:
        if a and a not in q_terms:
            q_terms.append(a)
    seen_low = {t.lower() for t in q_terms}
    for kw in _topic_keywords(claim_text, exclude=inscope_vals + anchors):
        if kw not in seen_low:
            q_terms.append(kw)
            seen_low.add(kw)
    query = " ".join(q_terms)

    try:
        alt = retrieve_fn(query, top_k) or []
    except Exception as e:
        base.update({"rescued": False, "method": "retrieve_error:%s" % type(e).__name__,
                     "rescue_doi": None})
        return base

    anchors_low = [a.lower() for a in anchors]

    confirm_doi = None
    for p in alt:
        ab = (p.get("abstract") or "").lower()
        if not ab:
            continue
        # ALL in-scope specifics co-occur in THIS one abstract (relaxed match:
        # year exact; proper noun by full phrase OR last significant token) ...
        if not all(_spec_in_abstract(u, ab) for u in inscope):
            continue
        # ... AND it is bound to the claim subject (>=1 verified anchor present,
        # anchor also matched by last token). Binding semantics UNCHANGED.
        if anchors_low and not any(_anchor_in_abstract(a, ab) for a in anchors_low):
            continue
        confirm_doi = p.get("doi", "?")
        break

    if log is not None:
        log.append({"query": query, "n_alt": len(alt),
                    "inscope": inscope_vals, "anchors": anchors[:2],
                    "confirmed": confirm_doi is not None, "doi": confirm_doi})

    if confirm_doi is not None:
        base["pass"] = True
        base.update({"rescued": True, "method": "rescued", "rescue_doi": confirm_doi})
    else:
        base.update({"rescued": False, "method": "no_rescue", "rescue_doi": None})
    return base


# --- Test harness for S4 data ---

def load_s4_absorb(enriched_path, verdicts_path):
    """Load S4 claims that got B2=SUPPORTS (ABSORB)."""
    # Load enriched records
    enriched = {}
    with open(enriched_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            enriched[rec.get("id", "")] = rec

    # Load verdicts, find SUPPORTS
    absorb_ids = []
    with open(verdicts_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("verdict") == "SUPPORTS" or rec.get("b2_verdict") == "SUPPORTS":
                absorb_ids.append(rec.get("id", ""))

    # Join
    results = []
    for aid in absorb_ids:
        if aid in enriched:
            results.append(enriched[aid])

    return results


def main():
    ap = argparse.ArgumentParser(description="Specifics-coverage filter test")
    ap.add_argument("--enriched", required=True,
                    help="Path to o0_s4_enriched.jsonl")
    ap.add_argument("--verdicts", required=True,
                    help="Path to o0_s4_b2_verdicts.jsonl")
    args = ap.parse_args()

    absorb = load_s4_absorb(args.enriched, args.verdicts)
    print(f"Loaded {len(absorb)} ABSORB claims from S4\n")

    if not absorb:
        print("No ABSORB claims found. Check file paths and field names.")
        # Try to show what fields exist
        with open(args.verdicts, encoding="utf-8") as f:
            sample = json.loads(f.readline())
            print(f"  Verdict fields: {list(sample.keys())}")
        with open(args.enriched, encoding="utf-8") as f:
            sample = json.loads(f.readline())
            print(f"  Enriched fields: {list(sample.keys())}")
        sys.exit(1)

    for rec in sorted(absorb, key=lambda r: r.get("id", "")):
        rid = rec.get("id", "?")
        claim = rec.get("claim") or rec.get("text") or rec.get("completion", "")
        abstract = rec.get("abstract") or rec.get("best_abstract", "")

        print(f"{'=' * 70}")
        print(f"[{rid}] {claim[:100]}...")
        print(f"  Abstract: {abstract[:100]}..." if abstract else "  Abstract: NONE")

        result = specifics_check(claim, abstract)

        print(f"\n  Specifics found: {result['total']}")
        for s in result["specifics"]:
            mark = "✓" if s["found"] else "✗ UNVERIFIED"
            print(f"    [{s['type']:12s}] {s['value']:30s} {mark}")

        if result["unverified"]:
            print(f"\n  >> FILTER: FAIL ({result['unverified_count']} unverified)")
            print(f"  >> ACTION: downgrade SUPPORTS -> UNCLEAR (unverified_specifics)")
            for u in result["unverified"]:
                print(f"     - {u['type']}: {u['value']}")
        else:
            print(f"\n  >> FILTER: PASS (all {result['total']} specifics verified)")

        print()

    # Summary
    print(f"{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    n_pass = sum(1 for rec in absorb
                 for r in [specifics_check(
                     rec.get("claim") or rec.get("text") or rec.get("completion", ""),
                     rec.get("abstract") or rec.get("best_abstract", ""))]
                 if r["pass"])
    n_fail = len(absorb) - n_pass
    print(f"  ABSORB claims tested: {len(absorb)}")
    print(f"  Filter PASS (specifics verified): {n_pass}")
    print(f"  Filter FAIL (unverified specifics): {n_fail}")
    print(f"\n  Expected: 3 PASS (CLEAN), 2 FAIL (DIRTY)")


if __name__ == "__main__":
    main()
