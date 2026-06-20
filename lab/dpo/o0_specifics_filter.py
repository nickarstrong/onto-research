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
