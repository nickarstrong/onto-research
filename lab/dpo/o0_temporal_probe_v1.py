#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
o0_temporal_probe_v1.py  --  CONCEPT_temporal_channel_v2 sec3 pre-registered probe.

V2 vs v0 (REPORT_temporal_probe_v0.md): closes F3 (REFUTE misfire) + closes 09 (ABSTAIN).
Three guards, all entity-anchoring:
  G-a SAME-SENTENCE SCOPING : a year is checked ONLY against entities in ITS sentence
                              (kills the v0 cross-sentence 1983-book misfire on 18 + junk on 03).
  G-b SINGLE-WORD CAPTURE   : subject extraction now catches single-token entities
                              ("Cleverbot","Python","Titanic"), drops a stoplist of function words.
  G-c DISAMBIGUATION        : same-label candidates ranked by claim-context overlap; no confident
                              pick -> ABSTAIN (never castrate on ambiguity).
  G-d EVENT-TYPE PREDICATE  : REFUTE only on the date predicate matching the claim's event verb
                              ("published"->P577, "released"->P577/P571, "discovered"->P575/P585...).
                              An incidental predicate of a same-label work can NOT refute.
CONFIRM oracle (closes 09): FULL Wikipedia article plaintext (prop=extracts explaintext), year
  co-located with an event-anchor keyword (+-WINDOW chars), NOT REST summary. WD predicates secondary.

SET: 5 frozen S4 B2-SUPPORTS (Founder labels v199) + 2 NEW clean same-label TRAPS.
NO Ollama, NO embeddings, NO Crossref. Pure HTTP. Local. ~7 claims.

FROZEN BARS (pre-registered -- do NOT tune after results):
  P1 (CONFIRM, HARD) : heldout_16 (1847) AND heldout_09 (1887) BOTH CONFIRM via full text.
                       heldout_14 stays N/A (1900 covered in abstract).
  P2 (REFUTE anchored, HARD): heldout_03 REFUTE on resolved subject (paper P577=1929 != 1925);
                       heldout_18 REFUTE-on-resolved-subject OR ABSTAIN -- but NOT via the 1983 book.
  P3 (F3-FIX, HARD -- load-bearing falsifier): TRAP_python AND TRAP_titanic BOTH not REFUTED
                       (CONFIRM or ABSTAIN). Any REFUTE on a clean trap = F3 still live.
PASS = P1 AND P2 AND P3.  Falsifiers: F3' trap refuted; F2' 09 still ABSTAIN on full text;
  F4 subject-resolution wrong on a DIRTY -> real refute missed (REFUTE under-powered).
"""

import json, re, sys, time, urllib.parse, urllib.request

UA = "ONTO-temporal-probe/1.0 (research; council@ontostandard.org)"
WINDOW = 200  # chars: year<->event-anchor co-location window in full article text

# event verb (lowercased substring) -> date predicates it licenses for REFUTE/CONFIRM
EVENT_PREDICATES = {
    "publish": ["P577"], "paper": ["P577"], "wrote": ["P577"],
    "release": ["P577", "P571"],
    "found": ["P571"], "establish": ["P571"], "creat": ["P571"], "invent": ["P571"],
    "introduc": ["P571"], "develop": ["P571"], "inception": ["P571"],
    "discover": ["P575", "P585"], "observ": ["P575", "P585"], "demonstrat": ["P575", "P585"],
    "detect": ["P575", "P585"], "generat": ["P575", "P585"], "confirm": ["P575", "P585"],
    "propos": ["P575", "P585"], "formulat": ["P575", "P585"],
    "occur": ["P585"], "happen": ["P585"], "achiev": ["P585"], "pass": ["P585"], "took place": ["P585"],
}
PRED_NAME = {"P577": "publication date", "P571": "inception", "P575": "time of discovery",
             "P585": "point in time", "P580": "start time"}

# single-word capitalized tokens to DROP (function / sentence-frame words, never subjects)
STOP_CAPS = {
    "the", "a", "an", "this", "that", "these", "those", "in", "on", "at", "by", "for", "to",
    "however", "subsequent", "subsequently", "according", "as", "if", "when", "while", "one",
    "his", "her", "its", "their", "he", "she", "it", "they", "we", "i", "and", "but", "or",
    "abstract", "earth", "moon", "sun",  # generic, never the dated subject here
}

def extract_years(text):
    return sorted(set(re.findall(r'\b(1[89]\d{2}|20\d{2})\b', text)))

def split_sentences(text):
    # naive but adequate: split on . ! ? followed by space/cap; keep offsets implicitly by re-find
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p for p in parts if p.strip()]

def sentence_of_year(claim, year):
    for s in split_sentences(claim):
        if re.search(r'\b' + re.escape(year) + r'\b', s):
            return s
    return claim  # fallback: whole claim

def event_predicates_for(sentence):
    """Which date predicates does this sentence's event verb license? [] if none matched."""
    low = sentence.lower()
    preds = []
    for kw, ps in EVENT_PREDICATES.items():
        if kw in low:
            for p in ps:
                if p not in preds:
                    preds.append(p)
    return preds

def extract_subjects_in_sentence(sentence, year):
    """Candidate subject entities IN THE YEAR'S SENTENCE, ordered by char-distance to the year.
       Captures: quoted titles, multi-word Proper Names, AND single-word capitalized content tokens.
       Drops STOP_CAPS function words. (G-a + G-b)"""
    _clean = lambda s: s.strip().strip(' ,.;:"\'')
    ypos = sentence.find(year)
    if ypos < 0:
        ypos = 0
    cands = []  # (label, dist)

    def add(label, pos):
        label = _clean(label)
        if len(label) < 3:
            return
        if label.lower() in STOP_CAPS:
            return
        cands.append((label, abs(pos - ypos)))

    for m in re.finditer(r'"([^"]+)"', sentence):           # quoted work titles
        if len(_clean(m.group(1))) > 4:
            add(m.group(1), m.start())
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', sentence):  # First Last(+)
        add(m.group(1), m.start())
    for m in re.finditer(r'\b([A-Z][a-zA-Z]{2,})\b', sentence):              # single capitalized token
        tok = m.group(1)
        if tok.lower() in STOP_CAPS:
            continue
        # skip if already inside a captured multi-word name
        if any(tok in lbl and lbl != tok for lbl, _ in cands):
            continue
        add(tok, m.start())

    # de-dup preserve nearest
    best = {}
    for lbl, d in cands:
        k = lbl.lower()
        if k not in best or d < best[k][1]:
            best[k] = (lbl, d)
    # drop fragments that are substrings of a longer captured candidate (junk title pieces)
    labels = [lbl for lbl, _ in best.values()]
    kept = {k: v for k, v in best.items()
            if not any(v[0] != o and v[0].lower() in o.lower() for o in labels)}
    ordered = sorted(kept.values(), key=lambda t: t[1])
    return [lbl for lbl, _ in ordered][:6]

# ---------------------------- HTTP helpers ----------------------------
def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def wbsearch(label, limit=5):
    """[{id, description}] for same-label candidates."""
    u = ("https://www.wikidata.org/w/api.php?action=wbsearchentities"
         "&search=%s&language=en&format=json&limit=%d"
         % (urllib.parse.quote(label), limit))
    try:
        return [{"id": h["id"], "description": h.get("description", "")} for h in _get(u).get("search", [])]
    except Exception as e:
        return {"_err": str(e)}

def entity_data(qid):
    """{years_by_pred:{P:[y]}, enwiki_title, description}."""
    u = "https://www.wikidata.org/wiki/Special:EntityData/%s.json" % qid
    try:
        data = _get(u)
    except Exception as e:
        return {"_err": str(e)}
    ent = data.get("entities", {}).get(qid, {})
    years = {}
    for pid in PRED_NAME:
        for cl in ent.get("claims", {}).get(pid, []):
            try:
                t = cl["mainsnak"]["datavalue"]["value"]["time"]
                y = re.search(r'(\d{4})', t)
                if y:
                    years.setdefault(pid, []).append(y.group(1))
            except Exception:
                pass
    title = ent.get("sitelinks", {}).get("enwiki", {}).get("title", "")
    desc = ent.get("descriptions", {}).get("en", {}).get("value", "")
    return {"years_by_pred": years, "enwiki_title": title, "description": desc}

def wiki_fulltext(title):
    """FULL article plaintext (closes 09) -- prop=extracts explaintext, NOT REST summary."""
    if not title:
        return ""
    u = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1"
         "&redirects=1&format=json&titles=%s" % urllib.parse.quote(title.replace(" ", "_")))
    try:
        pages = _get(u).get("query", {}).get("pages", {})
        for _, p in pages.items():
            if "extract" in p:
                return p["extract"] or ""
    except Exception:
        return ""
    return ""

# ---------------------------- disambiguation (G-c) ----------------------------
_TOK = lambda s: set(re.findall(r'[a-z]{3,}', (s or "").lower()))

def resolve_subject(label, context_tokens):
    """Pick the same-label entity whose description best overlaps claim context.
       Returns (qid, description, score) or None (ambiguous/zero -> ABSTAIN)."""
    cands = wbsearch(label)
    if isinstance(cands, dict) or not cands:
        return None
    scored = []
    for c in cands:
        sc = len(_TOK(c["description"]) & context_tokens)
        scored.append((sc, c["id"], c["description"]))
    scored.sort(reverse=True)
    top = scored[0]
    # confident pick: positive overlap and strictly beats the runner-up, OR a lone candidate
    if top[0] > 0 and (len(scored) == 1 or top[0] > scored[1][0]):
        return (top[1], top[2], top[0])
    if len(scored) == 1:
        return (scored[0][1], scored[0][2], scored[0][0])  # lone candidate, low confidence
    return None  # ambiguous -> ABSTAIN

# ---------------------------- verdict logic (V2) ----------------------------
def confirm_in_text(text, year, event_kw_present, subject_title):
    """CONFIRM via full text: year co-located with an event-anchor keyword (or subject) +-WINDOW."""
    if not text or year not in text:
        return False, ""
    anchors = [kw for kw in EVENT_PREDICATES if kw in text.lower()]
    if subject_title:
        anchors.append(subject_title.lower())
    low = text.lower()
    for m in re.finditer(re.escape(year), text):
        lo, hi = max(0, m.start() - WINDOW), m.start() + WINDOW
        seg = low[lo:hi]
        if any(a in seg for a in anchors):
            return True, text[lo:hi].replace("\n", " ")
    return False, ""

def verify_year(claim_year, sentence, context_tokens):
    """Entity-anchored CONFIRM/REFUTE/ABSTAIN for one load-bearing year. Full audit log."""
    log = {"claim_year": claim_year, "sentence_event_preds": event_predicates_for(sentence),
           "subjects": [], "tried": []}
    event_preds = event_predicates_for(sentence)        # G-d
    subjects = extract_subjects_in_sentence(sentence, claim_year)  # G-a + G-b
    log["subjects"] = subjects

    confirmed = False
    refute_hit = None  # (subject, qid, pred, kb_year)

    for s in subjects:
        res = resolve_subject(s, context_tokens)        # G-c
        if res is None:
            log["tried"].append({"label": s, "resolve": "ABSTAIN_ambiguous_or_none"})
            continue
        qid, desc, score = res
        ed = entity_data(qid)
        time.sleep(0.3)
        if isinstance(ed, dict) and ed.get("_err"):
            log["tried"].append({"label": s, "qid": qid, "err": ed["_err"]})
            continue
        ybp = ed["years_by_pred"]
        title = ed["enwiki_title"]
        entry = {"label": s, "qid": qid, "desc": desc, "ctx_score": score,
                 "years_by_pred": ybp, "enwiki_title": title}

        # CONFIRM via WD: claim_year on ANY date predicate of the resolved subject
        flat = [y for ys in ybp.values() for y in ys]
        if claim_year in flat:
            entry["confirm"] = "WD_predicate"
            confirmed = True
            log["tried"].append(entry)
            continue
        # CONFIRM via FULL TEXT (closes 09)
        text = wiki_fulltext(title)
        ok, snip = confirm_in_text(text, claim_year, bool(event_preds), title)
        if ok:
            entry["confirm"] = "fulltext"
            entry["snippet"] = snip[:240]
            confirmed = True
            log["tried"].append(entry)
            continue
        # REFUTE candidate: ONLY on an event-type-matched predicate (G-d) carrying a confirmed
        # different year. No event match -> NEVER refute (precision).
        if event_preds:
            for p in event_preds:
                for ky in ybp.get(p, []):
                    if ky != claim_year:
                        entry["refute"] = {"pred": p, "pred_name": PRED_NAME[p], "kb_year": ky}
                        refute_hit = refute_hit or (s, qid, p, ky)
        log["tried"].append(entry)

    if confirmed:
        return "CONFIRM", log
    if refute_hit:
        log["refute_anchor"] = {"subject": refute_hit[0], "qid": refute_hit[1],
                                "pred": refute_hit[2], "kb_year": refute_hit[3]}
        return "REFUTE", log
    return "ABSTAIN", log

# ---------------------------- driver ----------------------------
TRAPS = [
    {"id": "TRAP_python", "label": "CLEAN",
     "claim": "Python is a high-level programming language first released in 1991.",
     "abstract": ""},
    {"id": "TRAP_titanic", "label": "CLEAN",
     "claim": "Titanic is a film directed by James Cameron, released in 1997.",
     "abstract": ""},
]

def load_frozen(enriched, labels):
    lab = {json.loads(l)["id"]: json.loads(l) for l in open(labels)}
    rows = {}
    for l in open(enriched):
        d = json.loads(l)
        if d["id"] in lab:
            rows[d["id"]] = {"id": d["id"], "claim": d["claim"],
                             "abstract": (d.get("best_abstract") or ""),
                             "label": lab[d["id"]]["label"]}
    return rows

def run_row(r):
    claim = r["claim"]
    abstract_low = r["abstract"].lower()
    ctx = _TOK(claim)
    years = extract_years(claim)
    per_year = {}
    for y in years:
        if y in abstract_low:
            per_year[y] = ("COVERED_IN_ABSTRACT", {})
            continue
        sent = sentence_of_year(claim, y)
        v, log = verify_year(y, sent, ctx)
        per_year[y] = (v, log)
    lb = {y: v for y, (v, _) in per_year.items() if v != "COVERED_IN_ABSTRACT"}
    if "REFUTE" in lb.values():
        cv = "REFUTE"
    elif lb and all(v == "CONFIRM" for v in lb.values()):
        cv = "CONFIRM"
    elif not lb:
        cv = "N/A_no_loadbearing_year"
    else:
        cv = "ABSTAIN"
    return {"id": r["id"], "label": r["label"], "years": years,
            "per_year": {y: per_year[y][0] for y in per_year},
            "claim_verdict": cv,
            "detail": {y: per_year[y][1] for y in per_year}}

def main():
    enriched = sys.argv[1] if len(sys.argv) > 1 else "o0_s4_enriched.jsonl"
    labels   = sys.argv[2] if len(sys.argv) > 2 else "o0_s4_founder_labels.jsonl"
    rows = load_frozen(enriched, labels)
    items = [rows[c] for c in sorted(rows)] + TRAPS

    results, trace = {}, []
    for r in items:
        res = run_row(r)
        results[res["id"]] = res
        trace.append(res)
        print("  done %-14s -> %s" % (res["id"], res["claim_verdict"]))

    print("\n=== TEMPORAL CHANNEL V2 PROBE -- claim verdicts ===")
    print("%-14s %-6s %-18s %-10s" % ("id", "label", "years", "temporal"))
    for cid in [r["id"] for r in items]:
        x = results[cid]
        print("%-14s %-6s %-18s %-10s" % (cid, x["label"], ",".join(x["years"]), x["claim_verdict"]))

    g = results
    def cv(i): return g.get(i, {}).get("claim_verdict")
    p1 = cv("heldout_16") == "CONFIRM" and cv("heldout_09") == "CONFIRM"
    p2 = (cv("heldout_03") == "REFUTE") and (cv("heldout_18") in ("REFUTE", "ABSTAIN"))
    # P2 extra guard: 18 must NOT have refuted via a non-subject 1983 book
    h18 = g.get("heldout_18", {})
    h18_clean = True
    if cv("heldout_18") == "REFUTE":
        ra = h18.get("detail", {}).get("2014", {}).get("refute_anchor", {})
        h18_clean = "cleverbot" in (ra.get("subject", "").lower()) or "goostman" in (ra.get("subject", "").lower())
    p3 = cv("TRAP_python") in ("CONFIRM", "ABSTAIN") and cv("TRAP_titanic") in ("CONFIRM", "ABSTAIN")

    print("\n=== PRE-REGISTERED BARS ===")
    print("P1 (HARD) 16+09 CONFIRM via full text :", "PASS" if p1 else "FAIL",
          "(16=%s 09=%s)" % (cv("heldout_16"), cv("heldout_09")))
    print("P2 (HARD) 03 REFUTE / 18 REFUTE|ABSTAIN:", "PASS" if (p2 and h18_clean) else "FAIL",
          "(03=%s 18=%s, 18-anchor-clean=%s)" % (cv("heldout_03"), cv("heldout_18"), h18_clean))
    print("P3 (HARD) F3-FIX: traps NOT refuted   :", "PASS" if p3 else "FAIL",
          "(python=%s titanic=%s)" % (cv("TRAP_python"), cv("TRAP_titanic")))
    overall = "PASS" if (p1 and p2 and h18_clean and p3) else "FAIL"
    print("\nFALSIFIERS:")
    print("  F3' (trap refuted)      :", "TRIGGERED" if not p3 else "clear")
    print("  F2' (09 abstain on text):", "TRIGGERED" if cv("heldout_09") not in ("CONFIRM",) else "clear")
    print("  F4  (18 anchor wrong)   :", "TRIGGERED" if (cv("heldout_18") == "REFUTE" and not h18_clean) else "clear")
    print("\nOVERALL:", overall)

    json.dump(trace, open("o0_temporal_probe_v1_trace.json", "w"), indent=2)
    print("\ntrace -> o0_temporal_probe_v1_trace.json")

if __name__ == "__main__":
    main()
