#!/usr/bin/env python3
"""Fetch abstracts for rung1 dry-run results and enrich the JSONL."""
import json, sys, time, re
import urllib.request, urllib.error, urllib.parse

MAILTO = "council@ontostandard.org"
HEADERS = {"User-Agent": "ONTO-rung1/1.0 (mailto:%s)" % MAILTO}

def clean_jats(s):
    return re.sub(r"<[^>]+>", "", s).strip() if s else ""

def reconstruct_oa(inv):
    if not inv: return ""
    w = {}
    for word, pos in inv.items():
        for p in pos: w[p] = word
    return " ".join(w[i] for i in sorted(w))

def fetch_abstract(doi):
    """Crossref first, OpenAlex fallback."""
    # Crossref
    try:
        url = "https://api.crossref.org/works/%s?mailto=%s" % (
            urllib.parse.quote(doi, safe="/."), MAILTO)
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            m = json.loads(r.read().decode())["message"]
        title = (m.get("title") or [""])[0]
        abstract = clean_jats(m.get("abstract", ""))
        if abstract:
            return title, abstract
    except Exception:
        pass
    # OpenAlex
    try:
        url = "https://api.openalex.org/works/doi:%s?mailto=%s" % (
            urllib.parse.quote(doi, safe="/."), MAILTO)
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = json.loads(r.read().decode())
        title = body.get("display_name") or body.get("title") or ""
        abstract = reconstruct_oa(body.get("abstract_inverted_index"))
        return title, abstract
    except Exception:
        pass
    return "", ""

def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "eval/rung1_wiring_v0_dryrun.jsonl"
    out = inp.replace(".jsonl", "_enriched.jsonl")
    rows = [json.loads(l) for l in open(inp, encoding="utf-8") if l.strip()]
    for i, r in enumerate(rows):
        doi = (r.get("retrieval") or {}).get("best_doi")
        gate = (r.get("gate") or {}).get("passed", False)
        if not doi or not gate:
            r["best_abstract"] = ""
            r["best_title_full"] = ""
            print("[%d/%d] %s SKIP (no DOI or gate reject)" % (i+1, len(rows), r["id"]))
            continue
        title, abstract = fetch_abstract(doi)
        r["best_abstract"] = abstract
        r["best_title_full"] = title
        print("[%d/%d] %s DOI=%s abstract=%d chars" % (
            i+1, len(rows), r["id"], doi, len(abstract)))
        time.sleep(0.4)
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("\nEnriched: %s (%d rows)" % (out, len(rows)))

if __name__ == "__main__":
    main()
