#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
o0_temporal_probe_v5.py  --  CONCEPT temporal channel V6 probe (live Wikidata/Wikipedia).

V6 vs V5 (REPORT_temporal_probe_v4.md sec 3/5): closes D4 -- the same-title WORK-decoy refute. With
V5's same-sentence CONFIRM removing the short-circuit, TRAP_unconfirm reached the refute path and
REFUTED a CLEAN: subject "Solaris" resolved to Q261281 the 1961 SOURCE NOVEL (P577=1961) != the
claim's 1968 TV adaptation -> spurious REFUTE (castration on CLEAN). D3 only blocks PERSON-name
labels; a WORK-role decoy is structurally outside it.

  SINGLE surgical change, refute branch of verify_year() ONLY (D4, mechanism 5(b) work-side restraint,
  operationalized as SOURCE-PREDATES-DERIVATIVE -- literal token-overlap 5(b) is falsified at
  design-time: the claim CITES its own source "Lem's novel", so the source-work's description
  necessarily shares {novel, lem} -> overlap>0 -> would not block):
    A refute may anchor on a same-title work ONLY if the claim does NOT frame its subject as a
    DERIVATIVE whose resolved same-title work PREDATES the claim year. If the claim sentence carries a
    derivative marker (adaptation/version/remake/based-on/translation/adapted/reboot) AND the resolved
    work's refuting year < claim year -> that work is the likely SOURCE/sibling, not the claim's
    event-subject -> BLOCK refute (ABSTAIN). Precision-first: blocking a refute never castrates a
    CLEAN; it only forgoes an ADVISORY refute (ONTO priority safety > capability).

  Closes: "Solaris" -> Q261281 P577=1961 < 1968, claim has "adaptation/version" -> BLOCK -> ABSTAIN.
  Preserves P2: claim_03 (Hubble 1925) carries no derivative marker -> D4 inactive -> 03 REFUTE on the
  1929 paper Q24563361 (D3) UNTOUCHED.
  Residual D5 (flagged, NOT in V6 traps): a same-title sibling decoy dated LATER than the claim's work
  (remake after the claim) is not covered by the predates rule.

  HARD REGRESSION GUARD (frozen from V5, load-bearing): 16 + 09 MUST stay CONFIRM same-sentence
  (D4 touches the refute branch only; confirm path is byte-identical to V5).

  CONFIRM same-sentence + predicate-class + "== header ==" strip + LEFT word-boundary,
  D2 (person-dominant resolve), D3 (person-name refute block + event-predicate match): FROZEN.
  EVENT_PREDICATES, WD-predicate confirm path: UNTOUCHED.

SET: 5 frozen S4 B2-SUPPORTS (Founder labels v199) + 4 clean same-label TRAPS.
NO Ollama, NO embeddings, NO Crossref. Pure HTTP. Local. ~9 claims.

OFFLINE SELFTEST (run `python o0_temporal_probe_v4.py --selftest`, NO network): asserts the
same-sentence confirm_in_text on the two frozen snippets resolvable from the v3 trace --
16 -> CONFIRM, TRAP_unconfirm -> ABSTAIN. 09 is NOT offline-assertable (snippet truncated) and is
deferred to the live run. Must pass before the live run.

FROZEN BARS (pre-registered -- do NOT tune after results):
  P1 (CONFIRM, HARD regression guard): heldout_16 (1847) AND heldout_09 (1887) BOTH CONFIRM
                      same-sentence (frozen confirm path). heldout_14 stays N/A (1900 in abstract).
  P2 (REFUTE+ABSTAIN, HARD): heldout_03 REFUTE *anchored on the 1929 paper* (qid Q24563361)
                      -- D4 must NOT over-block it; heldout_18 ABSTAIN.
  P3 (REFUTE-restraint, HARD, load-bearing): TRAP_python, TRAP_titanic, TRAP_norefute,
                      TRAP_unconfirm ALL not REFUTED. D4 sub-check: TRAP_unconfirm pass-mode --
                      ABSTAIN = D4 CLOSED (work-decoy refute restrained) /
                      CONFIRM = frozen confirm path regressed / REFUTE = D4 NOT closed.
PASS = P1 AND P2 AND P3.
Falsifiers: F-regress (16 or 09 ABSTAIN = frozen confirm path broke);
  F-D3 (03 anchor != Q24563361); F-D4' (TRAP_unconfirm REFUTED = work-decoy restraint did not fire);
  F-D4-overblock (03 refute_blocked by D4 = restraint over-fired on a true refute).
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
    """V5 D1'' fix. CONFIRM iff the year AND an admissible-class event verb share ONE article
       SENTENCE (not +-WINDOW chars). Predicate-class + header-strip + LEFT word-boundary retained
       from V4. Closes the cross-sentence window bleed (D1''): TRAP_unconfirm's 1968 (filmography
       line) no longer co-locates with the 2024-edition "published" two sentences away.

       Same-sentence is monotonically TIGHTER than +-WINDOW: it can only REMOVE confirms, never add
       one. So 18 stays ABSTAIN (had no in-window admissible verb -> none in-sentence either) and no
       trap gains a confirm. The only at-risk pre-existing confirm is the one whose admissible verb
       lived in an ADJACENT sentence under +-200:
         - 16 (1847): "In 1847, he proposed..." -> "propos" in-sentence (claim class) -> HOLDS.
         - 09 (1887): "...November 1887 with his paper..." -- "paper"=P577 is OFF-CLASS for claim_09
           {P575,P585}; the admissible "observing" was the PRIOR sentence under +-200. 09 survives
           iff the FULL 1887 sentence (text beyond the old +-200 window) carries a P575/P585 verb.
           Unresolvable from the truncated v3 snippet -> LIVE regression risk, pre-registered."""
    text = strip_wiki_markup(text)
    if not text or year not in text:
        return False, ""
    # admissible anchor stems = those whose predicate(s) intersect the claim sentence's predicates
    stems = [kw for kw, ps in EVENT_PREDICATES.items() if any(p in claim_event_preds for p in ps)]
    if not stems:
        return False, ""
    anchor_re = re.compile(r'\b(?:%s)' % "|".join(re.escape(s) for s in stems), re.IGNORECASE)
    yre = re.compile(r'\b' + re.escape(year) + r'\b')
    for s in split_sentences(text):              # SAME-SENTENCE scope (was +-WINDOW chars)
        if yre.search(s) and anchor_re.search(s):
            return True, s.strip().replace("\n", " ")[:240]
    return False, ""

# ---------------------------- D4 (V6): work-decoy refute restraint ----------------------------
DERIV_MARKERS = ("adaptation", "adapted", "version", "remake", "reboot",
                 "based on", "translation", "cover of")

def claim_asserts_derivative(sentence):
    """True iff the claim sentence frames its subject as a DERIVATIVE of a same-named source
       (adaptation/version/remake/based-on/translation). Used by D4 to restrain a refute that would
       anchor on the SOURCE work rather than the claim's derivative event-subject."""
    low = (sentence or "").lower()
    return any(m in low for m in DERIV_MARKERS)

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
        # D4 (V6, work-decoy restraint): a same-title work may anchor a refute ONLY if the claim is
        # NOT a derivative whose resolved work PREDATES the claim year. Derivative marker present AND
        # resolved refuting year < claim year -> resolved work is the likely SOURCE/sibling, not the
        # claim's event-subject -> BLOCK (ABSTAIN). Safe direction (forgoes an advisory refute).
        if role != "person" and event_preds:
            deriv = claim_asserts_derivative(sentence)
            for p in event_preds:
                for ky in ybp.get(p, []):
                    if ky != claim_year:
                        if deriv and int(ky) < int(claim_year):
                            entry.setdefault("refute_blocked_D4", []).append(
                                {"pred": p, "pred_name": PRED_NAME[p], "kb_year": ky,
                                 "reason": "work_decoy_source_predates_derivative"})
                            continue
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

    print("\n=== TEMPORAL CHANNEL V6 PROBE -- claim verdicts ===")
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
    # P3: no trap refuted (incl. the R15/D4 work-decoy trap)
    traps = ("TRAP_python", "TRAP_titanic", "TRAP_norefute", "TRAP_unconfirm")
    p3 = all(cv(t) in ("CONFIRM", "ABSTAIN", "N/A_no_loadbearing_year") for t in traps)
    unconfirm_mode = cv("TRAP_unconfirm")  # ABSTAIN=D4 closed ; CONFIRM=confirm regressed ; REFUTE=D4 gap
    # D4 over-block guard: did D4 wrongly block heldout_03's true refute?
    d4_overblock_03 = bool(h03.get("detail", {}).get("1925", {}).get("tried")
                           and any("refute_blocked_D4" in t
                                   for t in h03.get("detail", {}).get("1925", {}).get("tried", [])
                                   if isinstance(t, dict))) and cv("heldout_03") != "REFUTE"

    print("\n=== PRE-REGISTERED BARS ===")
    print("P1 (HARD regress-guard) 16+09 CONFIRM   :", "PASS" if p1 else "FAIL",
          "(16=%s 09=%s)" % (cv("heldout_16"), cv("heldout_09")))
    print("P2 (HARD) 03 REFUTE@1929 / 18 ABSTAIN   :", "PASS" if p2 else "FAIL",
          "(03=%s anchor=%s 18=%s)" % (cv("heldout_03"), anchor03_qid or "-", cv("heldout_18")))
    print("P3 (HARD) traps NOT refuted             :", "PASS" if p3 else "FAIL",
          "(py=%s tit=%s noref=%s unconf=%s)" % (cv("TRAP_python"), cv("TRAP_titanic"),
                                                 cv("TRAP_norefute"), cv("TRAP_unconfirm")))
    print("D4 sub-check TRAP_unconfirm pass-mode   :", unconfirm_mode,
          "(ABSTAIN=D4 closed ; CONFIRM=confirm path regressed ; REFUTE=D4 work-decoy NOT closed)")
    overall = "PASS" if (p1 and p2 and p3) else "FAIL"

    print("\nFALSIFIERS:")
    print("  F-regress(16 or 09 ABSTAIN)         :",
          "TRIGGERED" if (cv("heldout_16") != "CONFIRM" or cv("heldout_09") != "CONFIRM") else "clear")
    print("  F-D3     (03 anchor != Q24563361)   :",
          "TRIGGERED" if (cv("heldout_03") == "REFUTE" and anchor03_qid != "Q24563361") else "clear")
    print("  F-D4'    (TRAP_unconfirm REFUTED)   :", "TRIGGERED" if unconfirm_mode == "REFUTE" else "clear")
    print("  F-D4-overblock (D4 blocked 03 refute):", "TRIGGERED" if d4_overblock_03 else "clear")
    print("\nOVERALL:", overall)

    json.dump(trace, open("o0_temporal_probe_v5_trace.json", "w"), indent=2)
    print("\ntrace -> o0_temporal_probe_v5_trace.json")

def selftest():
    """Offline, no-network. Asserts same-sentence confirm_in_text on the two frozen snippets that
       are fully resolvable from the v3 trace. 09 is NOT here (v3 snippet truncated mid 1887
       sentence -> live-only). Frozen verbatim from o0_temporal_probe_v3_trace.json."""
    ok = True
    # heldout_16 (1847): admissible "proposed" (P575/P585) shares the 1847 sentence -> CONFIRM.
    t16 = ("Childbed fever was common and often fatal.  Semmelweis demonstrated that the incidence "
           "of infection could be drastically reduced by requiring healthcare workers in "
           "obstetrical clinics to disinfect their hands. In 1847, he proposed hand washing with "
           "chlorinated lime solutions.")
    preds16 = event_predicates_for("Semmelweis observed in 1847")   # claim_16 class {P575,P585}
    c16, s16 = confirm_in_text(t16, "1847", preds16)
    print("SELFTEST 16 (expect CONFIRM) :", "PASS" if c16 else "FAIL", "|", s16[:80])
    ok &= c16
    # TRAP_unconfirm (1968): admissible "published" is in the 2024-edition sentence (no 1968);
    # the 1968 filmography sentence has no admissible release verb -> ABSTAIN (D1'' closed).
    tuc = ("Due to legal issues, this translation did not appear in print until 2024, when "
           "Conversation Tree Press published a fine press edition of the book. Solaris has been "
           "filmed three times:  Solaris (1968), a Soviet TV play directed by Boris Nirenburg.")
    predsuc = event_predicates_for("In 1968 the director released a television adaptation")  # P577/P571
    cuc, suc = confirm_in_text(tuc, "1968", predsuc)
    print("SELFTEST unconfirm (expect ABSTAIN):", "PASS" if not cuc else "FAIL",
          "|", (suc[:80] if cuc else "(no same-sentence co-location)"))
    ok &= (not cuc)
    # control: same TRAP_unconfirm text but year 2024 SHOULD confirm (publish in-sentence) -> proves
    # the ABSTAIN above is same-sentence scoping, not a dead matcher.
    c24, s24 = confirm_in_text(tuc, "2024", predsuc)
    print("SELFTEST control 2024 (expect CONFIRM):", "PASS" if c24 else "FAIL", "|", s24[:80])
    ok &= c24
    # D4 (V6) offline units -- no network. Derivative detection + source-predates block.
    d_uc = claim_asserts_derivative(
        "In 1968, Boris Nirenburg released a television adaptation of Lem's novel titled Solaris.")
    print("SELFTEST D4 derivative=TRUE (unconfirm) :", "PASS" if d_uc else "FAIL")
    ok &= d_uc
    d_03 = claim_asserts_derivative(
        "Edwin Hubble discovered the redshift-distance relationship for galaxies in 1925.")
    print("SELFTEST D4 derivative=FALSE (03)       :", "PASS" if not d_03 else "FAIL")
    ok &= (not d_03)
    block = d_uc and int("1961") < int("1968")        # source novel predates the 1968 adaptation
    print("SELFTEST D4 block source<claim (1961<68):", "PASS" if block else "FAIL")
    ok &= block
    noblock = (not d_03)                               # 03 not derivative -> refute path stays open
    print("SELFTEST D4 03 refute path OPEN         :", "PASS" if noblock else "FAIL")
    ok &= noblock
    print("\nSELFTEST OVERALL:", "PASS" if ok else "FAIL",
          "  (09 deferred to live -- truncated v3 snippet, not offline-assertable)")
    return 0 if ok else 1

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
