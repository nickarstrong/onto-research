#!/usr/bin/env python3
"""Temporal channel enrichment v2.
- Year verification via Wikipedia (Wikidata SPARQL skipped — WDQS outage)
- Wikipedia extract injected as evidence.abstract when original is empty
Pure stdlib. Run locally.

Usage:
  python temporal_enrich_v2.py claims_blind_ev.jsonl claims_enriched.jsonl
"""

import json, re, sys, time, urllib.request, urllib.parse, ssl

DELAY       = 1.5
UA          = "OntoTemporalChannel/2.0 (council@ontostandard.org)"
SNIPPET_WIN = 300
WP_MAX_CHARS= 8000   # max Wikipedia text to inject as evidence
CTX         = ssl.create_default_context()

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] {url[:80]}… → {e}", file=sys.stderr)
        return None

def extract_years(text):
    return sorted(set(y for y in re.findall(r'\b(\d{4})\b', text) if 1500 <= int(y) <= 2025))

def wp_text(title):
    url = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
           f"&explaintext=true&redirects=1&titles={urllib.parse.quote(title)}"
           "&format=json")
    raw = _get(url)
    if not raw: return ""
    data = json.loads(raw)
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1": return ""
        return page.get("extract", "")
    return ""

def wp_snippets_for_year(text, year):
    snippets = []
    for m in re.finditer(re.escape(year), text):
        start = max(0, m.start() - SNIPPET_WIN)
        end   = min(len(text), m.end() + SNIPPET_WIN)
        snippets.append(text[start:end].replace("\n", " ").strip())
    return snippets

def guess_entities(topic, claim):
    entities = [topic]
    persons = re.findall(r'[A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+', claim[:200])
    for p in persons[:2]:
        if p not in topic:
            entities.append(p)
    return entities

def enrich(claim_obj):
    years = extract_years(claim_obj["claim"])
    topic = claim_obj.get("topic", "")
    entities = guess_entities(topic, claim_obj["claim"])

    # Fetch Wikipedia text for all entities
    all_wp = ""
    wp_sources = []
    for ent in entities:
        wt = wp_text(ent)
        time.sleep(0.8)
        if wt:
            all_wp += "\n" + wt
            wp_sources.append(ent)

    # Year verification (Wikipedia only — WDQS down)
    per_year = {}
    all_snippets = []
    for y in years:
        snips = wp_snippets_for_year(all_wp, y)
        if snips:
            per_year[y] = "CONFIRM"
            for s in snips[:2]:
                all_snippets.append(f"[{y}] {s}")
            print(f"  {claim_obj['id']} year={y} → CONFIRM (wikipedia:{len(snips)} mentions)", file=sys.stderr)
        else:
            per_year[y] = "ABSTAIN"
            print(f"  {claim_obj['id']} year={y} → ABSTAIN", file=sys.stderr)

    claim_obj["temporal"] = {"per_year": per_year, "snippets": all_snippets[:6]}

    # INJECT: if original abstract is empty, fill with Wikipedia extract
    orig_abstract = claim_obj.get("evidence", {}).get("abstract", "").strip()
    if not orig_abstract and all_wp.strip():
        claim_obj["evidence"]["abstract"] = all_wp.strip()[:WP_MAX_CHARS]
        claim_obj["evidence"]["abstract_source"] = "wikipedia:" + "+".join(wp_sources)
        print(f"  {claim_obj['id']} abstract INJECTED ({len(claim_obj['evidence']['abstract'])} chars from {wp_sources})", file=sys.stderr)

    return claim_obj

def main():
    if len(sys.argv) < 3:
        print("Usage: python temporal_enrich_v2.py INPUT.jsonl OUTPUT.jsonl", file=sys.stderr)
        sys.exit(1)

    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, encoding="utf-8") as f:
        claims = [json.loads(l) for l in f if l.strip()]

    print(f"Enriching {len(claims)} claims…", file=sys.stderr)
    results = []
    for i, c in enumerate(claims):
        print(f"[{i+1}/{len(claims)}] {c['id']} — {c.get('topic','')}", file=sys.stderr)
        enriched = enrich(c)
        results.append(enriched)
        time.sleep(DELAY)

    with open(outp, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    confirms = sum(1 for r in results for v in r["temporal"]["per_year"].values() if v == "CONFIRM")
    abstains = sum(1 for r in results for v in r["temporal"]["per_year"].values() if v == "ABSTAIN")
    injected = sum(1 for r in results if r.get("evidence",{}).get("abstract_source","").startswith("wikipedia"))
    orig     = sum(1 for r in results if not r.get("evidence",{}).get("abstract_source",""))
    print(f"\nDone. {len(results)} claims, {confirms} CONFIRM / {abstains} ABSTAIN", file=sys.stderr)
    print(f"Abstracts: {injected} injected from Wikipedia, {orig} kept original", file=sys.stderr)
    print(f"Output: {outp}", file=sys.stderr)

if __name__ == "__main__":
    main()
