#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
o0_temporal_probe_v0.py  --  CONCEPT_temporal_channel_v1 sec7 pre-registered probe.

Question (falsifiable): can an OUT-OF-BAND date oracle REFUTE a wrong year and
CONFIRM correct historical event-years that academic abstracts cannot carry?

Set      : the 5 frozen S4 B2-SUPPORTS (Founder labels banked v199).
Oracle   : Wikidata structured date predicates (REFUTE-strong) +
           Wikipedia REST summary text co-occurrence (CONFIRM-strong for event-years).
           Both OUT-OF-BAND vs Crossref/OpenAlex abstracts.
Verdict  : CONFIRM / REFUTE / ABSTAIN per load-bearing year.
NO Ollama, NO embeddings, NO Crossref. Pure HTTP. Local. <=5 claims.

FROZEN BARS (do not tune after seeing results -- pre-registered):
  P1 HARD : heldout_03 -> REFUTE        (claim 1925 vs truth 1929)
  P2      : heldout_09 -> CONFIRM (1887) AND heldout_16 -> CONFIRM (1847)
  P3      : log ABSTAIN rate; ABSTAIN on 09/16 even with fallback = coverage gap.
  DEMO    : heldout_18 year 2014 may CONFIRM (real Goostman year) -> proves temporal
            is NOT sufficient alone; name-binding (Cleverbot, banked v207) owns 18.
PASS = P1 AND P2.  FAIL = NOT P1 (any wrong-year leak).  PARTIAL = P1 + one of 09/16.
"""

import json, re, sys, time, urllib.parse, urllib.request

UA = "ONTO-temporal-probe/0.1 (research; council@ontostandard.org)"
DATE_PREDICATES = {
    "P577": "publication date", "P571": "inception", "P575": "time of discovery",
    "P585": "point in time", "P580": "start time",
}
ARTICLE_LED = ("the ", "a ", "an ")

# ---- reuse from o0_specifics_filter.py (year extraction is identical, kept inline
#      so the probe is standalone; tail-debt 9: subject extraction cleaned below) ----
def extract_years(text):
    return sorted(set(re.findall(r'\b(1[89]\d{2}|20\d{2})\b', text)))

def extract_subjects(text):
    """Clean entity candidates for KB linking (tail-debt 9 applied):
       quoted titles first, then 2+-word capitalized names, drop article-led junk."""
    _clean = lambda s: s.strip().strip(' ,.;:"\'')
    cands = []
    for q in re.findall(r'"([^"]+)"', text):           # quoted work titles
        q = _clean(q)
        if len(q) > 4: cands.append(q)
    for m in re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text):  # First Last(+)
        m = _clean(m)
        if m.lower().startswith(ARTICLE_LED):  continue
        cands.append(m)
    # de-dup preserve order
    seen, out = set(), []
    for c in cands:
        if c.lower() not in seen:
            seen.add(c.lower()); out.append(c)
    return out[:6]

# ---------------------------- HTTP helpers ----------------------------
def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def wikidata_qids(label, limit=2):
    u = ("https://www.wikidata.org/w/api.php?action=wbsearchentities"
         "&search=%s&language=en&format=json&limit=%d"
         % (urllib.parse.quote(label), limit))
    try:
        return [h["id"] for h in _get(u).get("search", [])]
    except Exception as e:
        return {"_err": str(e)}

def wikidata_years(qid):
    """Return {predicate: [years]} for date predicates on this entity."""
    u = "https://www.wikidata.org/wiki/Special:EntityData/%s.json" % qid
    try:
        data = _get(u)
    except Exception as e:
        return {"_err": str(e)}
    out = {}
    ent = data.get("entities", {}).get(qid, {})
    for pid in DATE_PREDICATES:
        for cl in ent.get("claims", {}).get(pid, []):
            try:
                t = cl["mainsnak"]["datavalue"]["value"]["time"]   # +1929-00-00T...
                y = re.search(r'(\d{4})', t)
                if y: out.setdefault(pid, []).append(y.group(1))
            except Exception:
                pass
    return out

def wikipedia_summary(title):
    u = ("https://en.wikipedia.org/api/rest_v1/page/summary/%s"
         % urllib.parse.quote(title.replace(" ", "_")))
    try:
        d = _get(u)
        return (d.get("extract") or "")
    except Exception as e:
        return ""

# ---------------------------- verdict logic ----------------------------
def verify_year(claim_year, subjects):
    """CONFIRM/REFUTE/ABSTAIN claim_year against out-of-band oracles.
       Logs every QID/predicate/kb_year/wiki hit for interpretability."""
    log = {"claim_year": claim_year, "subjects": subjects, "wd": [], "wiki": []}
    refute_years, confirm = set(), False

    for s in subjects:
        qids = wikidata_qids(s)
        if isinstance(qids, dict):  # error
            log["wd"].append({"label": s, "err": qids.get("_err")}); continue
        for qid in qids:
            yrs = wikidata_years(qid)
            log["wd"].append({"label": s, "qid": qid, "years": yrs})
            if isinstance(yrs, dict):
                flat = [y for k, v in yrs.items() if k != "_err" for y in v]
                if claim_year in flat:
                    confirm = True
                # structured years that are NOT the claim year, for the same entity,
                # are refutation candidates (a dated work/event with a different year)
                for y in flat:
                    if y != claim_year:
                        refute_years.add(y)
        time.sleep(0.3)  # politeness

    # Wikipedia text fallback: entity page that co-locates the claim year
    for s in subjects:
        ex = wikipedia_summary(s)
        hit = claim_year in ex
        other = sorted(set(re.findall(r'\b(1[89]\d{2}|20\d{2})\b', ex)) - {claim_year})
        log["wiki"].append({"label": s, "year_in_summary": hit, "other_years": other[:6]})
        if hit:
            confirm = True

    if confirm:
        return "CONFIRM", log
    # REFUTE only when a structured oracle gave a DIFFERENT year and none confirmed
    if refute_years:
        log["refute_years"] = sorted(refute_years)
        return "REFUTE", log
    return "ABSTAIN", log

# ---------------------------- driver ----------------------------
def load_set(enriched, labels):
    lab = {json.loads(l)["id"]: json.loads(l) for l in open(labels)}
    rows = {}
    for l in open(enriched):
        d = json.loads(l)
        if d["id"] in lab:
            rows[d["id"]] = {"claim": d["claim"],
                             "abstract": (d.get("best_abstract") or ""),
                             "label": lab[d["id"]]["label"]}
    return rows

def main():
    enriched = sys.argv[1] if len(sys.argv) > 1 else "o0_s4_enriched.jsonl"
    labels   = sys.argv[2] if len(sys.argv) > 2 else "o0_s4_founder_labels.jsonl"
    rows = load_set(enriched, labels)

    results, trace = {}, []
    for cid in sorted(rows):
        r = rows[cid]
        years = extract_years(r["claim"])
        subjects = extract_subjects(r["claim"])
        abstract_low = r["abstract"].lower()
        per_year = {}
        for y in years:
            covered = y in abstract_low          # already in abstract -> not load-bearing
            if covered:
                per_year[y] = ("COVERED_IN_ABSTRACT", {})
                continue
            v, log = verify_year(y, subjects)
            per_year[y] = (v, log)
        # claim-level temporal verdict: REFUTE if any load-bearing year REFUTES;
        # else CONFIRM if all load-bearing years CONFIRM/covered; else ABSTAIN.
        lb = {y: v for y, (v, _) in per_year.items() if v != "COVERED_IN_ABSTRACT"}
        if "REFUTE" in lb.values():        claim_verdict = "REFUTE"
        elif lb and all(v == "CONFIRM" for v in lb.values()): claim_verdict = "CONFIRM"
        elif not lb:                       claim_verdict = "N/A_no_loadbearing_year"
        else:                              claim_verdict = "ABSTAIN"
        results[cid] = {"label": r["label"], "years": years,
                        "subjects": subjects, "per_year": {y: per_year[y][0] for y in per_year},
                        "claim_verdict": claim_verdict}
        trace.append({"id": cid, **results[cid],
                      "detail": {y: per_year[y][1] for y in per_year}})

    # ----- report -----
    print("\n=== TEMPORAL CHANNEL PROBE -- claim verdicts ===")
    print("%-12s %-6s %-22s %-10s" % ("id", "label", "years", "temporal"))
    for cid in sorted(results):
        x = results[cid]
        print("%-12s %-6s %-22s %-10s" % (cid, x["label"], ",".join(x["years"]), x["claim_verdict"]))

    g = results
    p1 = g.get("heldout_03", {}).get("claim_verdict") == "REFUTE"
    p2 = (g.get("heldout_09", {}).get("claim_verdict") == "CONFIRM" and
          g.get("heldout_16", {}).get("claim_verdict") == "CONFIRM")
    print("\n=== PRE-REGISTERED BARS ===")
    print("P1 (HARD) heldout_03 REFUTE :", "PASS" if p1 else "FAIL",
          "(got %s)" % g.get("heldout_03", {}).get("claim_verdict"))
    print("P2 heldout_09+16 CONFIRM    :", "PASS" if p2 else "FAIL",
          "(09=%s 16=%s)" % (g.get("heldout_09", {}).get("claim_verdict"),
                             g.get("heldout_16", {}).get("claim_verdict")))
    print("DEMO heldout_18 (year 2014) :", g.get("heldout_18", {}).get("claim_verdict"),
          "-- name-binding owns 18, not temporal")
    overall = "PASS" if (p1 and p2) else ("FAIL" if not p1 else "PARTIAL")
    print("\nOVERALL:", overall)

    json.dump(trace, open("o0_temporal_probe_trace.json", "w"), indent=2)
    print("\ntrace -> o0_temporal_probe_trace.json")

if __name__ == "__main__":
    main()
