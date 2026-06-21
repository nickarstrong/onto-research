#!/usr/bin/env python3
"""Temporal channel enrichment v3.
Fixes from v2:
 1. Entity search: fallback to person names + law/concept name separately
 2. Relevance check: if abstract has <=1 claim keyword, inject Wikipedia over it
 3. Per-entity char budget (4000 each) instead of concat+truncate

Pure stdlib. Run locally.
Usage: python temporal_enrich_v3.py claims_blind_ev.jsonl claims_enriched_v3.jsonl
"""

import json, re, sys, time, urllib.request, urllib.parse, ssl

DELAY        = 1.5
INTER_CALL   = 0.8
UA           = "OntoTemporalChannel/3.0 (council@ontostandard.org)"
SNIPPET_WIN  = 300
PER_ENTITY   = 4000   # chars per entity (fix #3)
MAX_ENTITIES = 3
CTX          = ssl.create_default_context()

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

# ── Wikipedia ───────────────────────────────────────────────────────
def wp_search(query):
    """Search Wikipedia for best article title."""
    url = ("https://en.wikipedia.org/w/api.php?action=opensearch"
           f"&search={urllib.parse.quote(query)}&limit=3&format=json")
    raw = _get(url)
    if not raw: return None
    data = json.loads(raw)
    titles = data[1] if len(data) > 1 else []
    return titles[0] if titles else None

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
    snippets = []
    for m in re.finditer(re.escape(year), text):
        start = max(0, m.start() - SNIPPET_WIN)
        end   = min(len(text), m.end() + SNIPPET_WIN)
        snippets.append(text[start:end].replace("\n", " ").strip())
    return snippets

# ── Entity guessing (fix #1) ────────────────────────────────────────
def guess_entities(topic, claim):
    """Broader entity search: topic, person names, concept name."""
    entities = []
    # 1. Topic as-is
    entities.append(topic)
    # 2. Person names from claim (first 300 chars)
    persons = re.findall(r'([A-Z][a-z]+ (?:[A-Z]\. )?(?:de )?[A-Z][a-z]+)', claim[:300])
    for p in persons:
        if p not in entities and p.lower() not in topic.lower():
            entities.append(p)
    # 3. If topic has possessive/descriptive, extract core noun
    #    e.g. "Mendel pea inheritance experiments" -> "Gregor Mendel" (via person)
    #    "Archimedes principle of buoyancy" -> "Archimedes"
    core = re.match(r"^([A-Z][a-z]+(?:'s)?)", topic)
    if core:
        name = core.group(1).rstrip("'s")
        if name not in entities:
            entities.append(name)
    return entities[:MAX_ENTITIES]

def fetch_entity_texts(entities):
    """Fetch Wikipedia text for entities, with search fallback. Returns [(name, text)]."""
    results = []
    for ent in entities:
        # Try direct fetch first
        text = wp_text(ent)
        time.sleep(INTER_CALL)
        if not text or len(text) < 200:
            # Fallback: search Wikipedia
            title = wp_search(ent)
            time.sleep(INTER_CALL)
            if title:
                text = wp_text(title)
                time.sleep(INTER_CALL)
                if text and len(text) >= 200:
                    results.append((title, text))
                    continue
        if text and len(text) >= 200:
            results.append((ent, text))
    return results

# ── Relevance check (fix #2) ────────────────────────────────────────
def is_relevant(abstract, claim, threshold=2):
    """Check if abstract is relevant to claim (>=threshold content words overlap)."""
    if not abstract.strip():
        return False
    # Extract content words from claim (4+ chars, lowercase)
    claim_words = set(w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', claim))
    ab_lower = abstract.lower()
    hits = sum(1 for w in claim_words if w in ab_lower)
    return hits >= threshold

# ── Main enrichment ─────────────────────────────────────────────────
def enrich(claim_obj):
    years = extract_years(claim_obj["claim"])
    topic = claim_obj.get("topic", "")
    claim_text = claim_obj["claim"]
    entities = guess_entities(topic, claim_text)

    # Fetch Wikipedia per entity (fix #3: per-entity budget)
    entity_texts = fetch_entity_texts(entities)
    
    # Build combined text (full, for year search)
    all_wp_full = "\n".join(t for _, t in entity_texts)
    
    # Build evidence text (per-entity budget)
    wp_evidence = "\n\n".join(t[:PER_ENTITY] for _, t in entity_texts)
    wp_sources = [name for name, _ in entity_texts]

    # Year verification
    per_year = {}
    all_snippets = []
    for y in years:
        snips = wp_snippets_for_year(all_wp_full, y)
        if snips:
            per_year[y] = "CONFIRM"
            for s in snips[:2]:
                all_snippets.append(f"[{y}] {s}")
            print(f"  {claim_obj['id']} year={y} → CONFIRM (wikipedia:{len(snips)} mentions)", file=sys.stderr)
        else:
            per_year[y] = "ABSTAIN"
            print(f"  {claim_obj['id']} year={y} → ABSTAIN", file=sys.stderr)

    claim_obj["temporal"] = {"per_year": per_year, "snippets": all_snippets[:6]}

    # Evidence injection (fix #2: relevance check)
    orig_abstract = claim_obj.get("evidence", {}).get("abstract", "").strip()
    should_inject = False
    if not orig_abstract:
        should_inject = True
        reason = "empty"
    elif not is_relevant(orig_abstract, claim_text):
        should_inject = True
        reason = "irrelevant"
    
    if should_inject and wp_evidence.strip():
        claim_obj["evidence"]["abstract"] = wp_evidence.strip()
        claim_obj["evidence"]["abstract_source"] = f"wikipedia:{'+'.join(wp_sources)}"
        print(f"  {claim_obj['id']} abstract INJECTED ({len(wp_evidence)} chars, {reason}, from {wp_sources})", file=sys.stderr)
    elif not should_inject:
        print(f"  {claim_obj['id']} abstract KEPT (original relevant, {len(orig_abstract)} chars)", file=sys.stderr)

    return claim_obj

def main():
    if len(sys.argv) < 3:
        print("Usage: python temporal_enrich_v3.py INPUT.jsonl OUTPUT.jsonl", file=sys.stderr)
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
    injected = sum(1 for r in results if "wikipedia" in r.get("evidence",{}).get("abstract_source",""))
    print(f"\nDone. {len(results)} claims, {confirms} CONFIRM / {abstains} ABSTAIN", file=sys.stderr)
    print(f"Abstracts: {injected} injected, {len(results)-injected} kept original", file=sys.stderr)

if __name__ == "__main__":
    main()
