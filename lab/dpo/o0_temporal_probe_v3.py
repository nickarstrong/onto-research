#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
o0_temporal_probe_v3.py  --  CONCEPT temporal channel V4 probe (live Wikidata/Wikipedia).

V4 vs V3 (REPORT_temporal_probe_v2.md sec 3/5): closes the D1 RESIDUAL (incidental-event-verb
co-location, incl. wiki section-header markup). D2 + D3 frozen (closed in V3), untouched.

  D1 RESIDUAL (18 false-CONFIRM on "develop" from "== Developments ==" header co-located with the
  incidental "2014 GPU upgrade" sentence). Two-part fix in confirm_in_text():
    (a) PREDICATE-CLASS anchor (not exact keyword): admissible co-location anchors = event verbs
        whose Wikidata predicate is in the CLAIM SENTENCE's licensed predicate set
        (event_predicates_for(sentence)). The article verb need not equal the claim verb; it must
        be the same EVENT TYPE. -- Strict exact-keyword (report sec5 literal) was FALSIFIED on
        frozen V3 trace: 16 confirmed on article "demonstrated/proposed" (claim verb "observed");
        09 confirmed on "observing/paper" (claim verbs "confirmed/generated/detected"). Exact-kw
        would regress BOTH -> P1 FAIL. Predicate-class keeps 16+09 (all P575/P585) and still kills
        18 (claim 2014 class = P585; "develop" = P571, off-class).
    (b) header strip + WORD-BOUNDARY: "== ... ==" markup removed before scanning; anchor stems
        matched at a left word boundary (\\bstem). Belt to (a): even if an off-class verb were
        re-added, the only "develop" near 2014 lived in the section header -> stripped.
  -> heldout_18 -> ABSTAIN (no claim-class verb co-located with 2014 post-strip).
  HARD REGRESSION GUARD: heldout_16 (1847) + heldout_09 (1887) MUST stay CONFIRM under (a)+(b).

  D2 (person-dominant resolve) and D3 (person-name refute block + event-predicate match): FROZEN.

  NEW TRAP (R15, still-open): TRAP_unconfirm -- a CLEAN claim whose CORRECT year is NOT confirmable
  (obscure same-label work, thin/absent enwiki) while a same-label WORK decoy carries a CONFIRMABLE
  DIFFERENT year. Forces ABSTAIN-not-CONFIRM, exercising refute-restraint without the CONFIRM
  short-circuit that made TRAP_norefute narrow. 1968 Soviet TV "Solaris" (correct, thin enwiki) vs
  the 1972/2002 same-title films (confirmable P577 != 1968).

SET: 5 frozen S4 B2-SUPPORTS (Founder labels v199) + 4 clean same-label TRAPS.
NO Ollama, NO embeddings, NO Crossref. Pure HTTP. Local. ~9 claims.

FROZEN BARS (pre-registered -- do NOT tune after results):
  P1 (CONFIRM, HARD regression guard): heldout_16 (1847) AND heldout_09 (1887) BOTH CONFIRM
                      under the tightened predicate-class anchor. heldout_14 stays N/A (1900 in abstract).
  P2 (REFUTE+ABSTAIN, HARD): heldout_03 REFUTE *anchored on the 1929 paper* (qid Q24563361);
                      heldout_18 ABSTAIN (D1 residual closed -> NOT CONFIRM).
  P3 (REFUTE-restraint, HARD, load-bearing): TRAP_python, TRAP_titanic, TRAP_norefute,
                      TRAP_unconfirm ALL not REFUTED. R15 sub-check: TRAP_unconfirm pass-mode --
                      ABSTAIN = load-bearing (R15 CLOSED) / CONFIRM = still narrow / REFUTE = D4 gap.
PASS = P1 AND P2 AND P3.
Falsifiers: F-D1 (18 CONFIRM); F-regress (16 or 09 ABSTAIN); F-D3 (03 anchor != Q24563361);
  F-D4 (TRAP_unconfirm REFUTED = work-title decoy refute, new gap).
"""

import json, re, sys, time, urllib.parse, urllib.request

UA = "ONTO-temporal-probe/1.1 (research; council@ontostandard.org)"
WINDOW = 200

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

STOP_CAPS = {
    "the", "a", "an", "this", "that", "these", "those", "in", "on", "at", "by", "for", "to",
    "however", "subsequent", "subsequently", "according", "as", "if", "when", "while", "one",
    "his", "her", "its", "their", "he", "she", "it", "they", "we", "i", "and", "but", "or",
    "abstract", "earth", "moon", "sun",
}
ORG_WORDS = {"hospital", "university", "college", "institute", "company", "journal",
             "laboratory", "observatory", "society", "department", "press"}
HUMAN_QID = "Q5"

def extract_years(text):
    return sorted(set(re.findall(r'\b(1[89]\d{2}|20\d{2})\b', text)))

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p for p in parts if p.strip()]

def sentence_of_year(claim, year):
    for s in split_sentences(claim):
        if re.search(r'\b' + re.escape(year) + r'\b', s):
            return s
    return claim

def event_predicates_for(sentence):
    low = sentence.lower()
    preds = []
    for kw, ps in EVENT_PREDICATES.items():
        if kw in low:
            for p in ps:
                if p not in preds:
                    preds.append(p)
    return preds

def subject_role(label, sentence):
    """work | person | thing.  (D3 gate keys on 'person'; D2 fallback keys on 'person'.)"""
    if ('"%s' % label) in sentence or ("'%s" % label) in sentence:  # opening quote (trailing punct tolerant)
        return "work"
    low = label.lower()
    if any(w in low for w in ORG_WORDS):
        return "thing"
    parts = label.split()
    if 2 <= len(parts) <= 3 and all(re.match(r'^[A-Z][a-z]+$', p) for p in parts):
        return "person"
    return "thing"

def extract_subjects_in_sentence(sentence, year):
    _clean = lambda s: s.strip().strip(' ,.;:"\'')
    ypos = sentence.find(year)
    if ypos < 0:
        ypos = 0
    cands = []

    def add(label, pos):
        label = _clean(label)
        if len(label) < 3:
            return
        if label.lower() in STOP_CAPS:
            return
        cands.append((label, abs(pos - ypos)))

    for m in re.finditer(r'"([^"]+)"', sentence):
        if len(_clean(m.group(1))) > 4:
            add(m.group(1), m.start())
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', sentence):
        add(m.group(1), m.start())
    for m in re.finditer(r'\b([A-Z][a-zA-Z]{2,})\b', sentence):
        tok = m.group(1)
        if tok.lower() in STOP_CAPS:
            continue
        if any(tok in lbl and lbl != tok for lbl, _ in cands):
            continue
        add(tok, m.start())

    best = {}
    for lbl, d in cands:
        k = lbl.lower()
        if k not in best or d < best[k][1]:
            best[k] = (lbl, d)
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
    u = ("https://www.wikidata.org/w/api.php?action=wbsearchentities"
         "&search=%s&language=en&format=json&limit=%d"
         % (urllib.parse.quote(label), limit))
    try:
        return [{"id": h["id"], "description": h.get("description", "")} for h in _get(u).get("search", [])]
    except Exception as e:
        return {"_err": str(e)}

def entity_data(qid):
    """{years_by_pred, enwiki_title, description, p31:[qid,...]}."""
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
    p31 = []
    for cl in ent.get("claims", {}).get("P31", []):
        try:
            p31.append(cl["mainsnak"]["datavalue"]["value"]["id"])
        except Exception:
            pass
    title = ent.get("sitelinks", {}).get("enwiki", {}).get("title", "")
    desc = ent.get("descriptions", {}).get("en", {}).get("value", "")
    return {"years_by_pred": years, "enwiki_title": title, "description": desc, "p31": p31}

def wiki_fulltext(title):
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

# ---------------------------- disambiguation (D2) ----------------------------
_TOK = lambda s: set(re.findall(r'[a-z]{3,}', (s or "").lower()))

def _is_human(qid):
    ed = entity_data(qid)
    time.sleep(0.2)
    if isinstance(ed, dict) and ed.get("_err"):
        return False
    return HUMAN_QID in ed.get("p31", [])

def resolve_subject(label, context_tokens, role):
    """Returns (qid, description, score, mode) or None (ambiguous -> ABSTAIN).
       D2: role=='person' + dominant human top-hit -> resolve even at overlap 0."""
    cands = wbsearch(label)
    if isinstance(cands, dict) or not cands:
        return None
    scored = []
    for c in cands:
        sc = len(_TOK(c["description"]) & context_tokens)
        scored.append((sc, c["id"], c["description"]))
    scored.sort(reverse=True)
    top = scored[0]
    if top[0] > 0 and (len(scored) == 1 or top[0] > scored[1][0]):
        return (top[1], top[2], top[0], "ctx")
    # D2 person-dominant fallback: top wbsearch hit, if human, for a person-name label
    if role == "person":
        tid = cands[0]["id"]
        if _is_human(tid):
            return (tid, cands[0].get("description", ""), 0, "person_dominant")
    if len(scored) == 1:
        return (scored[0][1], scored[0][2], scored[0][0], "lone")
    return None

# ---------------------------- verdict logic (V3) ----------------------------
_HDR = re.compile(r'={2,}[^=\n]*={2,}')           # "== Developments ==" section markup

def strip_wiki_markup(text):
    """Remove "== header ==" section markup so a header word can never be a co-location anchor."""
    return _HDR.sub(" ", text or "")

def confirm_in_text(text, year, claim_event_preds):
    """V4 D1-residual fix. CONFIRM iff the year is co-located (+-WINDOW) with an event verb whose
       Wikidata predicate is in the CLAIM SENTENCE's licensed set (claim_event_preds), matched at a
       LEFT word boundary, in HEADER-STRIPPED text. Predicate-class (not exact keyword) so 16/09 do
       not regress; off-class verbs (e.g. "develop"=P571 for a P585 claim) and header markup cannot
       anchor -> 18 ABSTAIN."""
    text = strip_wiki_markup(text)
    if not text or year not in text:
        return False, ""
    # admissible anchor stems = those whose predicate(s) intersect the claim sentence's predicates
    stems = [kw for kw, ps in EVENT_PREDICATES.items() if any(p in claim_event_preds for p in ps)]
    if not stems:
        return False, ""
    # word-boundary positions of any admissible stem (stems are prefixes: \b + stem)
    anchor_re = re.compile(r'\b(?:%s)' % "|".join(re.escape(s) for s in stems), re.IGNORECASE)
    anchor_pos = [m.start() for m in anchor_re.finditer(text)]
    if not anchor_pos:
        return False, ""
    for m in re.finditer(re.escape(year), text):
        lo, hi = m.start() - WINDOW, m.start() + WINDOW
        if any(lo <= ap <= hi for ap in anchor_pos):
            s, e = max(0, lo), min(len(text), hi)
            return True, text[s:e].replace("\n", " ")
    return False, ""

def verify_year(claim_year, sentence, context_tokens):
    log = {"claim_year": claim_year, "sentence_event_preds": event_predicates_for(sentence),
           "subjects": [], "tried": []}
    event_preds = event_predicates_for(sentence)
    subjects = extract_subjects_in_sentence(sentence, claim_year)
    roles = {s: subject_role(s, sentence) for s in subjects}
    log["subjects"] = subjects
    log["roles"] = roles

    confirmed = False
    refute_hit = None

    for s in subjects:
        role = roles[s]
        res = resolve_subject(s, context_tokens, role)
        if res is None:
            log["tried"].append({"label": s, "role": role, "resolve": "ABSTAIN_ambiguous_or_none"})
            continue
        qid, desc, score, mode = res
        ed = entity_data(qid)
        time.sleep(0.3)
        if isinstance(ed, dict) and ed.get("_err"):
            log["tried"].append({"label": s, "role": role, "qid": qid, "err": ed["_err"]})
            continue
        ybp = ed["years_by_pred"]
        title = ed["enwiki_title"]
        entry = {"label": s, "role": role, "qid": qid, "desc": desc, "ctx_score": score,
                 "resolve_mode": mode, "years_by_pred": ybp, "enwiki_title": title}

        flat = [y for ys in ybp.values() for y in ys]
        if claim_year in flat:
            entry["confirm"] = "WD_predicate"
            confirmed = True
            log["tried"].append(entry)
            continue
        text = wiki_fulltext(title)
        ok, snip = confirm_in_text(text, claim_year, event_preds)
        if ok:
            entry["confirm"] = "fulltext"
            entry["snippet"] = snip[:240]
            confirmed = True
            log["tried"].append(entry)
            continue
        # REFUTE: D3 -- person-name labels NEVER anchor a refute; G-d event-predicate match.
        if role != "person" and event_preds:
            for p in event_preds:
                for ky in ybp.get(p, []):
                    if ky != claim_year:
                        entry["refute"] = {"pred": p, "pred_name": PRED_NAME[p], "kb_year": ky}
                        refute_hit = refute_hit or (s, qid, p, ky)
        elif role == "person":
            entry["refute_blocked"] = "person_name_no_pubdate_D3"
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
    # NEW (R15): engages refute path. "Principia Mathematica" same-title collision with
    # Newton's 1687 work (different confirmable year). CLEAN -> must NOT refute.
    {"id": "TRAP_norefute", "label": "CLEAN",
     "claim": ("In 1910, philosophers Bertrand Russell and Alfred North Whitehead published "
               "the first volume of \"Principia Mathematica\", a foundational work in "
               "mathematical logic."),
     "abstract": ""},
    # NEW (R15, still-open falsifier): CLEAN claim, CORRECT year unconfirmable (obscure 1968 Soviet
    # TV "Solaris", thin/absent enwiki) vs same-title WORK decoys with confirmable DIFFERENT years
    # (1972 Tarkovsky film, 2002 Soderbergh film; both P577 != 1968). Forces ABSTAIN-not-CONFIRM ->
    # exercises refute-restraint against a confirmable-wrong-year WORK decoy (D3 only blocks PERSON
    # labels, so this is the untested case). Expected ABSTAIN; CONFIRM = still narrow; REFUTE = D4.
    {"id": "TRAP_unconfirm", "label": "CLEAN",
     "claim": ("In 1968, Soviet director Boris Nirenburg released a television adaptation of "
               "Stanislaw Lem's novel titled \"Solaris\", the first screen version of the work."),
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

    print("\n=== TEMPORAL CHANNEL V4 PROBE -- claim verdicts ===")
    print("%-15s %-6s %-18s %-12s" % ("id", "label", "years", "temporal"))
    for cid in [r["id"] for r in items]:
        x = results[cid]
        print("%-15s %-6s %-18s %-12s" % (cid, x["label"], ",".join(x["years"]), x["claim_verdict"]))

    g = results
    def cv(i): return g.get(i, {}).get("claim_verdict")

    # P1 -- HARD regression guard under tightened predicate-class anchor
    p1 = cv("heldout_16") == "CONFIRM" and cv("heldout_09") == "CONFIRM"
    # P2: 03 REFUTE anchored on the 1929 paper Q24563361 ; 18 ABSTAIN (D1 residual closed)
    h03 = g.get("heldout_03", {})
    anchor03 = h03.get("detail", {}).get("1925", {}).get("refute_anchor", {})
    anchor03_qid = anchor03.get("qid", "")
    p2_03 = cv("heldout_03") == "REFUTE" and anchor03_qid == "Q24563361"
    p2_18 = cv("heldout_18") == "ABSTAIN"
    p2 = p2_03 and p2_18
    # P3: no trap refuted (incl. the new R15 trap)
    traps = ("TRAP_python", "TRAP_titanic", "TRAP_norefute", "TRAP_unconfirm")
    p3 = all(cv(t) in ("CONFIRM", "ABSTAIN", "N/A_no_loadbearing_year") for t in traps)
    unconfirm_mode = cv("TRAP_unconfirm")  # ABSTAIN=R15 closed ; CONFIRM=narrow ; REFUTE=D4 gap

    print("\n=== PRE-REGISTERED BARS ===")
    print("P1 (HARD regress-guard) 16+09 CONFIRM   :", "PASS" if p1 else "FAIL",
          "(16=%s 09=%s)" % (cv("heldout_16"), cv("heldout_09")))
    print("P2 (HARD) 03 REFUTE@1929 / 18 ABSTAIN   :", "PASS" if p2 else "FAIL",
          "(03=%s anchor=%s 18=%s)" % (cv("heldout_03"), anchor03_qid or "-", cv("heldout_18")))
    print("P3 (HARD) traps NOT refuted             :", "PASS" if p3 else "FAIL",
          "(py=%s tit=%s noref=%s unconf=%s)" % (cv("TRAP_python"), cv("TRAP_titanic"),
                                                 cv("TRAP_norefute"), cv("TRAP_unconfirm")))
    print("R15 sub-check TRAP_unconfirm pass-mode  :", unconfirm_mode,
          "(ABSTAIN=R15 closed ; CONFIRM=still narrow ; REFUTE=D4 work-decoy gap)")
    overall = "PASS" if (p1 and p2 and p3) else "FAIL"

    print("\nFALSIFIERS:")
    print("  F-D1     (18 CONFIRM)               :", "TRIGGERED" if cv("heldout_18") == "CONFIRM" else "clear")
    print("  F-regress(16 or 09 ABSTAIN)         :",
          "TRIGGERED" if (cv("heldout_16") != "CONFIRM" or cv("heldout_09") != "CONFIRM") else "clear")
    print("  F-D3     (03 anchor != Q24563361)   :",
          "TRIGGERED" if (cv("heldout_03") == "REFUTE" and anchor03_qid != "Q24563361") else "clear")
    print("  F-D4     (TRAP_unconfirm REFUTED)   :", "TRIGGERED" if unconfirm_mode == "REFUTE" else "clear")
    print("\nOVERALL:", overall)

    json.dump(trace, open("o0_temporal_probe_v3_trace.json", "w"), indent=2)
    print("\ntrace -> o0_temporal_probe_v3_trace.json")

if __name__ == "__main__":
    main()
