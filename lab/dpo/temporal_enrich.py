#!/usr/bin/env python3
"""Temporal channel enrichment for claim verification.
Queries Wikidata SPARQL + Wikipedia API to verify year tokens in claims.
Pure stdlib, no GPU, no pip. Run locally on Windows/Linux.

Usage:
  python temporal_enrich.py claims_blind_ev.jsonl claims_blind_ev_temporal.jsonl
"""

import json, re, sys, time, urllib.request, urllib.parse, ssl

# ── config ──────────────────────────────────────────────────────────
DELAY       = 8.0          # seconds between API bursts
UA          = "OntoTemporalChannel/1.0 (council@ontostandard.org)"
SNIPPET_WIN = 300          # chars around year mention to capture as snippet
CTX         = ssl.create_default_context()

def _get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] fetch failed: {url[:80]}… → {e}", file=sys.stderr)
        return None

# ── year extraction ─────────────────────────────────────────────────
def extract_years(text):
    """4-digit years plausible for scientific history (1500–2025)."""
    return sorted(set(y for y in re.findall(r'\b(\d{4})\b', text)
                      if 1500 <= int(y) <= 2025))

# ── wikidata ────────────────────────────────────────────────────────
def wd_search(query):
    """Search Wikidata entities, return top QID or None."""
    url = ("https://www.wikidata.org/w/api.php?action=wbsearchentities"
           f"&search={urllib.parse.quote(query)}&language=en&limit=3&format=json")
    raw = _get(url)
    if not raw: return None
    data = json.loads(raw)
    results = data.get("search", [])
    return results[0]["id"] if results else None

def wd_dates(qid):
    """Fetch all date-valued triples for an entity via SPARQL. Returns {year: [propLabel…]}."""
    sparql = f"""SELECT ?propLabel ?date WHERE {{
      wd:{qid} ?p ?stmt .
      ?stmt ?ps ?date .
      ?prop wikibase:claim ?p ; wikibase:statementProperty ?ps .
      FILTER(DATATYPE(?date) = xsd:dateTime)
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }} LIMIT 200"""
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": sparql})
    raw = _get(url)
    if not raw: return {}
    data = json.loads(raw)
    out = {}
    for b in data.get("results", {}).get("bindings", []):
        dt  = b.get("date", {}).get("value", "")
        lbl = b.get("propLabel", {}).get("value", "")
        m = re.match(r'(\d{4})', dt)
        if m:
            out.setdefault(m.group(1), []).append(lbl)
    return out

# ── wikipedia ───────────────────────────────────────────────────────
def wp_text(title):
    """Fetch plain-text extract of a Wikipedia article."""
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
    """Return context snippets around year mentions in Wikipedia text."""
    snippets = []
    for m in re.finditer(re.escape(year), text):
        start = max(0, m.start() - SNIPPET_WIN)
        end   = min(len(text), m.end() + SNIPPET_WIN)
        snippets.append(text[start:end].replace("\n", " ").strip())
    return snippets

# ── entity guessing ─────────────────────────────────────────────────
def guess_entities(topic, claim):
    """From topic + claim, guess 1-3 Wikipedia/Wikidata search terms."""
    entities = [topic]
    # try to extract a person name (heuristic: first capitalized multi-word near start)
    persons = re.findall(r'[A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+', claim[:200])
    for p in persons[:2]:
        if p not in topic:
            entities.append(p)
    return entities

# ── per-year verdict ────────────────────────────────────────────────
def verify_year(year, wd_year_map, wp_full_text):
    """Return (verdict, snippets) for a single year."""
    snippets = wp_snippets_for_year(wp_full_text, year)

    # CONFIRM: year found in Wikidata dates OR Wikipedia text with context
    in_wd = year in wd_year_map
    in_wp = len(snippets) > 0

    if in_wd or in_wp:
        src = []
        if in_wd: src.append(f"wikidata:{','.join(wd_year_map[year][:3])}")
        if in_wp: src.append(f"wikipedia:{len(snippets)} mentions")
        return "CONFIRM", snippets[:2], "; ".join(src)

    return "ABSTAIN", [], ""

# ── main pipeline ───────────────────────────────────────────────────
def enrich(claim_obj):
    years = extract_years(claim_obj["claim"])
    if not years:
        claim_obj["temporal"] = {"per_year": {}, "snippets": [], "note": "no years in claim"}
        return claim_obj

    topic = claim_obj.get("topic", "")
    entities = guess_entities(topic, claim_obj["claim"])

    # aggregate Wikidata dates + Wikipedia text across entities
    all_wd = {}
    all_wp = ""
    for ent in entities:
        qid = wd_search(ent)
        time.sleep(4.0)
        if qid:
            dates = wd_dates(qid)
            time.sleep(4.0)
            for y, props in dates.items():
                all_wd.setdefault(y, []).extend(props)

        wt = wp_text(ent)
        time.sleep(4.0)
        if wt:
            all_wp += "\n" + wt

    per_year = {}
    all_snippets = []
    for y in years:
        verdict, snips, src = verify_year(y, all_wd, all_wp)
        per_year[y] = verdict
        for s in snips:
            all_snippets.append(f"[{y}] {s}")
        if src:
            print(f"  {claim_obj['id']} year={y} → {verdict} ({src})", file=sys.stderr)
        else:
            print(f"  {claim_obj['id']} year={y} → {verdict}", file=sys.stderr)

    claim_obj["temporal"] = {"per_year": per_year, "snippets": all_snippets[:6]}
    return claim_obj

def main():
    if len(sys.argv) < 3:
        print("Usage: python temporal_enrich.py INPUT.jsonl OUTPUT.jsonl", file=sys.stderr)
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

    # summary
    confirms = sum(1 for r in results for v in r["temporal"]["per_year"].values() if v == "CONFIRM")
    abstains = sum(1 for r in results for v in r["temporal"]["per_year"].values() if v == "ABSTAIN")
    refutes  = sum(1 for r in results for v in r["temporal"]["per_year"].values() if v == "REFUTE")
    total_years = confirms + abstains + refutes
    print(f"\nDone. {len(results)} claims, {total_years} year-tokens: "
          f"{confirms} CONFIRM, {refutes} REFUTE, {abstains} ABSTAIN", file=sys.stderr)
    print(f"Output: {outp}", file=sys.stderr)

if __name__ == "__main__":
    main()
