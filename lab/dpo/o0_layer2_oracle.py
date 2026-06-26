#!/usr/bin/env python3
# o0_layer2_oracle.py -- LAYER-2 EVENT-ANCHOR ORACLE (v294 BUILD-2, raw v2).
# Supersedes v292 (REJECTED, B0 fail: 4 false-DIRTY on garbage/wrong-event subjects).
# Sealed spec: reports/LAYER2_REDESIGN_v293.md (G1/G2/G3 + B-bars). LOCAL until commit gate.
#
# ROLE: gated single-authority REFUTE for an (entity, event) year-anachronism, above the frozen
# Layer-1 discriminator. ENEMY = false-DIRTY (B0 ABSOLUTE = 0 false-DIRTY on GT-CLEAN). ABSTAIN is
# honest; layers SHRINK it, never zero it. Precision-first (ONTO: safety > capability).
#
# REFUTE licensed ONLY when ALL THREE hold (else ABSTAIN). This is the v293 sealed redesign:
#   G1 subject-is-content : resolved subject is a claim CONTENT entity, NOT a leading temporal
#                           phrase / bare month / date-only token. (kills 04_1 / 16_0 / 18_0)
#   G2 event-type match   : the authority year is a PUBLICATION-class date of the WORK (WD P577),
#                           NOT the discovery/inception/observation date of a phenomenon/sibling
#                           (P571/P575/P585/P580). Resolved entity must expose P577 and not be human.
#                           (kills 14_1 = Brown discovery P575=1827; 20_0 = unrelated entity)
#   G3 co-location        : the authority article must co-locate the claim SUBJECT and an event
#                           REFERENT noun (paper|publication|equation|experiment|study|article|book|
#                           title) and the authority year in ONE sentence -- the SAME discipline the
#                           CONFIRM branch already enforces (confirm_in_text). v292's refute did bare
#                           predicate-match (too weak); G3 closes that asymmetry.
#   granularity guard     : |claimed-auth| <= 2y on a publication/conception class -> ABSTAIN.
#                           Defense-in-depth, UNEXERCISED on held-out (no ~1y row); retained.
#
# CONFIRM stays BROAD (any admissible pred year-match) so true-year rows still CONFIRM (B3-WATCHF).
# Only the REFUTE branch is narrowed to G1+G2+G3.
#
# FROZEN REUSE (no drift): all resolution / WD-fetch / extraction primitives imported UNCHANGED from
# o0_temporal_probe_v5 (md5 b231da36) and o0_temporal_evidence (md5 92766b06). This module adds ONLY
# the gated REFUTE decision; it never re-implements resolution (the V2-V6 castration source).
#
# INPUT: ESC-stripped held-out (heldout_clean_20260625.jsonl from o0_esc_strip.py). WATCH-G precond.
# NETWORK: live HTTP to Wikidata via the frozen probe. Stub probe._get -> hermetic (all ABSTAIN).
# COMPUTE: network-bound, pure stdlib, NO GPU -> LOCAL.
#
# Usage:
#   python o0_layer2_oracle.py heldout_clean_20260625.jsonl o0_layer2_verdicts.jsonl   # live
#   python o0_layer2_oracle.py --selftest                                              # offline logic

import json, re, sys, time

from o0_temporal_evidence import (
    clean_for_parse, extract_years_ext, extract_numbers_nonyear,
)

CONFIRM, REFUTE, ABSTAIN = "CONFIRM", "REFUTE", "ABSTAIN"

# G2: the ONLY predicate that licenses a REFUTE = publication date of the work.
PUBLICATION_PRED = "P577"
HUMAN_QID = "Q5"

# G1: leading temporal phrase / bare date subjects are NOT content entities.
_MONTHS = {"january", "february", "march", "april", "may", "june", "july",
           "august", "september", "october", "november", "december"}
_DATE_ONLY = re.compile(r'^[\d\s,./\-]+$')

# G3: event referent nouns (the "what" the publication-class authority is about).
_EVENT_REFERENT = re.compile(
    r'\b(paper|publication|published|publishes|publishing|equation|experiment|study|studies|'
    r'article|book|treatise|monograph|title|journal|edition|volume|proceedings|memoir)\b', re.I)

# granularity guard (defense-in-depth)
_GRAN_YEARS = 2


# --- v296 Option A: un-quoted title reconstruction (sealed GENGAP_titlebind_v295 sec 3) ----------
# Deterministic, offline, ADDITIVE. The frozen V6 probe regex [A-Z][a-z]+(\s+[A-Z][a-z]+)+ cannot
# bridge a lowercase connector, so un-quoted titles like "On the Origin of Species" fragment at
# "the"/"of". This helper emits the full connector-bridged run as an EXTRA candidate (it never
# removes the probe's fragments). Pure all-capital runs already bind in the probe and are skipped
# (no double-emit). No network, no randomness -> hermetic.
TITLE_CONNECTORS = {"of", "the", "a", "an", "and", "for", "to", "in", "on",
                    "by", "concerning", "with", "between", "upon", "from"}
_CAP_WORD = re.compile(r"^[A-Z][a-z']+$")
_TITLE_TOK = re.compile(r"[A-Za-z']+")


def reconstruct_titles(sentence):
    """Emit verbatim connector-bridged capitalized title runs as extra candidate strings.
    A title-run (sec 3) is a MAXIMAL token sequence that begins AND ends on a capitalized word
    [A-Z][a-z']+, whose interior tokens are each a capitalized word OR a TITLE_CONNECTORS token,
    that contains >=1 LOWERCASE connector bridging two capitalized words (pure all-capital runs
    already bind in the probe -> skipped to avoid dup), with >=2 capitalized words and <=12 tokens."""
    toks = _TITLE_TOK.findall(sentence or "")
    is_cap = lambda t: bool(_CAP_WORD.match(t))
    is_conn = lambda t: t.lower() in TITLE_CONNECTORS
    out, i, n = [], 0, len(toks)
    while i < n:
        if not is_cap(toks[i]):
            i += 1
            continue
        j = i
        last_cap = i
        while j + 1 < n and (is_cap(toks[j + 1]) or is_conn(toks[j + 1])):
            j += 1
            if is_cap(toks[j]):
                last_cap = j
        run = toks[i:last_cap + 1]              # trim trailing connectors: end on a capitalized word
        i = j + 1                                # maximal, non-overlapping advance
        if sum(1 for t in run if is_cap(t)) < 2:                 # rule 2: >=2 capitalized words
            continue
        if len(run) > 12:                                        # rule 3: runaway-sentence guard
            continue
        if not any(is_conn(t) and not is_cap(t) for t in run):   # rule 1: real lowercase connector
            continue                                             #         (pure all-cap -> skip dup)
        out.append(" ".join(run))                                # rule 4: verbatim run
    return out


def _is_temporal_opener(label):
    """G1: True iff label is a leading temporal phrase / bare month / date-only token."""
    low = (label or "").strip().lower()
    if not low:
        return True
    if low in _MONTHS:
        return True
    toks = low.split()
    if toks and toks[0] in ("on", "in") and len(toks) >= 2 and toks[1] in _MONTHS:
        return True
    if _DATE_ONLY.match(low):
        return True
    return False


def _refute_colocated(article_text, subject_label, auth_year, T):
    """G3 (spec-literal): co-location on the REFUTE branch. The authority value (auth_year) is already
       established from WD P577; G3 confirms the ARTICLE is about the same (subject, event) by requiring
       ONE sentence that co-locates (a) a subject token AND (b) an event-referent noun -- the same
       discipline confirm_in_text enforces. The authoritative year must also appear somewhere in the
       (header-stripped) article. Returns (ok, snippet)."""
    text = T.strip_wiki_markup(article_text or "")
    if not text or auth_year not in text:
        return False, ""
    subj_toks = T._TOK(subject_label)
    if not subj_toks:
        return False, ""
    for s in T.split_sentences(text):
        if _EVENT_REFERENT.search(s) and (subj_toks & T._TOK(s)):
            return True, s.strip().replace("\n", " ")[:240]
    return False, ""


def _oracle_year_one(year, sent, ctx, topic, T, cache, art_cache):
    """Per-year single-authority verdict for ONE load-bearing year (G1+G2+G3 on REFUTE)."""
    preds = T.event_predicates_for(sent)
    if not preds:
        return ABSTAIN, {"reason": "no_event_predicate"}

    # G1: subject candidates, with temporal-opener / date-only dropped.
    subjects = [s for s in T.extract_subjects_in_sentence(sent, year)
                if not _is_temporal_opener(s)]
    # v296 Option A (sealed GENGAP_titlebind_v295 sec 3): ADDITIVE un-quoted-title reconstruction.
    # Merge connector-bridged title runs as EXTRA candidates; existing fragments are retained
    # (evolution-only / R-noregress). Dedup by lowercase. B0 stays held by the unchanged G2 P577
    # gate -- a candidate that does not resolve to a real P577 work cannot false-DIRTY.
    _seen = {s.lower() for s in subjects}
    for _t in reconstruct_titles(sent):
        if _t.lower() not in _seen:
            subjects.append(_t)
            _seen.add(_t.lower())
    if topic and topic not in subjects and not _is_temporal_opener(topic):
        subjects.append(topic)
    if not subjects:
        return ABSTAIN, {"reason": "g1_no_content_subject"}

    refute_cand = None
    for label in subjects:
        role = T.subject_role(label, sent)
        res = T.resolve_subject(label, ctx, role); time.sleep(0.2)
        if not res:
            continue
        qid, _desc, score, mode = res
        if qid not in cache:
            cache[qid] = T.entity_data(qid); time.sleep(0.2)
        ed = cache[qid]
        if not isinstance(ed, dict) or ed.get("_err"):
            continue
        ybp = ed.get("years_by_pred", {}) or {}

        # CONFIRM channel: BROAD (any admissible claim-class pred). A match anywhere = CONFIRM.
        auth_all = sorted({y for p in preds for y in ybp.get(p, [])})
        if year in auth_all:
            return CONFIRM, {"qid": qid, "subject": label, "pred_years": auth_all, "mode": mode}

        # REFUTE channel: G2 publication-class-of-work ONLY.
        if refute_cand is not None:
            continue
        if PUBLICATION_PRED not in preds:
            continue                                  # claim is not a publication-class event
        if HUMAN_QID in (ed.get("p31") or []):
            continue                                  # a person is not the published work
        pub = sorted(set(ybp.get(PUBLICATION_PRED, [])))
        if not pub:
            continue                                  # entity silent on publication -> not a work / non-confirm
        if len(pub) != 1:
            continue                                  # ambiguous publication authority -> ABSTAIN
        auth_year = pub[0]
        if year == auth_year:
            return CONFIRM, {"qid": qid, "subject": label, "pred_years": pub, "mode": mode}
        # positive DIFFERENT publication year. precision gate (ctx-confident resolve only).
        if not (mode == "ctx" and score > 0):
            continue
        # granularity guard (defense-in-depth): near-equal publication years -> ABSTAIN.
        try:
            if abs(int(year) - int(auth_year)) <= _GRAN_YEARS:
                continue
        except ValueError:
            pass
        # G3 co-location on the authority article.
        title = ed.get("enwiki_title") or ""
        if qid not in art_cache:
            art_cache[qid] = T.wiki_fulltext(title) if title else ""; time.sleep(0.2)
        ok, snip = _refute_colocated(art_cache[qid], label, auth_year, T)
        if not ok:
            continue                                  # G3 unsatisfied -> ABSTAIN
        refute_cand = {"qid": qid, "subject": label, "auth_year": auth_year,
                       "claimed": year, "mode": mode, "pred": PUBLICATION_PRED, "snippet": snip}
    if refute_cand:
        return REFUTE, refute_cand
    return ABSTAIN, {"reason": "g2g3_unsatisfied_or_silent"}


def oracle_year(claim, topic, T, cache, art_cache):
    parse = clean_for_parse(claim)
    ctx = T._TOK(parse)
    ce, _bce = extract_years_ext(parse)
    per_year = {}
    for y in ce:
        sent = T.sentence_of_year(parse, y)
        v, d = _oracle_year_one(y, sent, ctx, topic, T, cache, art_cache)
        per_year[y] = {"verdict": v, **d}
    verds = {pv["verdict"] for pv in per_year.values()}
    coll = REFUTE if REFUTE in verds else (CONFIRM if CONFIRM in verds else ABSTAIN)
    return coll, per_year


# NUMERIC CHANNEL (raw v2: SAFE NO-OP, declared -- unchanged from v292). No WD quantity mapper yet;
# a half-built one risks B0 false-DIRTY. ABSTAIN-always: structure present, zero false-DIRTY risk.
def oracle_numeric(claim, topic, T, cache):
    specifics = extract_numbers_nonyear(clean_for_parse(claim))
    return ABSTAIN, {n: {"verdict": ABSTAIN, "reason": "raw-v2 no-op (OWED: WD quantity property)"}
                     for n in specifics}


def oracle_record(rec, T, cache=None, art_cache=None):
    cache = cache if cache is not None else {}
    art_cache = art_cache if art_cache is not None else {}
    claim = rec.get("claim", "")
    topic = rec.get("topic") or ""
    yv, per_year = oracle_year(claim, topic, T, cache, art_cache)
    nv, per_num = oracle_numeric(claim, topic, T, cache)
    verds = {yv, nv}
    verdict = REFUTE if REFUTE in verds else (CONFIRM if CONFIRM in verds else ABSTAIN)
    return verdict, {"year": {"collapse": yv, "per_year": per_year},
                     "numeric": {"collapse": nv, "per_specific": per_num}}


def run(in_path, out_path):
    import o0_temporal_probe_v5 as T
    rows = [json.loads(l) for l in open(in_path, encoding="utf-8") if l.strip()]
    cache, art_cache = {}, {}
    n = {CONFIRM: 0, REFUTE: 0, ABSTAIN: 0}
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows:
            v, detail = oracle_record(r, T, cache, art_cache)
            n[v] += 1
            out = {"id": r.get("id"), "topic": r.get("topic"),
                   "layer2": {"verdict": v, **detail}}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            print("  %-14s layer2=%-8s year=%-8s" % (r.get("id"), v, detail["year"]["collapse"]))
    print("\n[layer2] %d rows -> %s" % (len(rows), out_path))
    print("[layer2] CONFIRM=%d REFUTE=%d ABSTAIN=%d  (REFUTE = G1+G2+G3 publication anachronism only)"
          % (n[CONFIRM], n[REFUTE], n[ABSTAIN]))


# ----------------------------------------------------------------------------------------------
# OFFLINE SELF-TEST (no network): asserts the G1/G2/G3 decision gate on a STUBBED probe.
# ----------------------------------------------------------------------------------------------
def selftest():
    import types, re as _re

    def make_T(resolve, ed, article="", subjects=("Subj",)):
        T = types.SimpleNamespace()
        T._TOK = lambda s: set(_re.findall(r'[a-z]{3,}', (s or "").lower()))
        T.sentence_of_year = lambda c, y: c
        T.split_sentences = lambda t: _re.split(r'(?<=[.!?])\s+', t or "")
        T.strip_wiki_markup = lambda t: t or ""
        T.event_predicates_for = lambda s: (
            ["P577"] if _re.search(r'publish', s, _re.I) else
            (["P575", "P585"] if _re.search(r'discover|observ', s, _re.I) else []))
        T.subject_role = lambda l, s: "thing"
        T.extract_subjects_in_sentence = lambda s, y: list(subjects)
        T.resolve_subject = lambda l, c, r: resolve
        T.entity_data = lambda q: ed
        T.wiki_fulltext = lambda title: article
        return T

    def verdict(claim, resolve, ed, article="", subjects=("Subj",), topic=""):
        T = make_T(resolve, ed, article, subjects)
        return oracle_record({"claim": claim, "topic": topic}, T, {}, {})[0]

    Q  = ("Q1", "law", 2, "ctx")          # ctx-confident
    QL = ("Q1", "law", 0, "lone")         # weak resolution
    # a work article that co-locates Subj + "paper" + 1785 (G3 satisfiable)
    ART_OK = "Subj is a paper. It was a paper published in 1785 by the author."
    # an article WITHOUT an event referent noun co-located (G3 fails)
    ART_NOREF = "Subj appeared in 1785 somewhere in the record without the referent."

    P31_WORK   = {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]}
    P31_PHENOM = {"years_by_pred": {"P575": ["1827"]}, "enwiki_title": "Subj", "p31": ["Q179630"]}
    P31_HUMAN  = {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q5"]}

    cases = [
      # name, claim, resolve, entity_data, article, subjects, expect
      ("confirm_same",    "X was published in 1785.", Q, P31_WORK, ART_OK, ("Subj",), CONFIRM),
      ("refute_g1g2g3",   "X was published in 1799.", Q,
                          {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK.replace("1785", "1785"), ("Subj",), REFUTE),
      ("g1_kills_month",  "Subj was published in 1799.", Q,
                          {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK, ("February",), ABSTAIN),  # only subject is a month -> G1 -> ABSTAIN
      ("g2_kills_phenom", "X was published in 1905.", Q, P31_PHENOM, ART_OK, ("Subj",), ABSTAIN),
      ("g2_kills_human",  "X was published in 1799.", Q, P31_HUMAN, ART_OK, ("Subj",), ABSTAIN),
      ("g2_nopub_claim",  "X was discovered in 1799.", Q,
                          {"years_by_pred": {"P575": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK, ("Subj",), ABSTAIN),  # claim not publication-class -> no REFUTE
      ("g3_kills_noref",  "X was published in 1799.", Q,
                          {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_NOREF, ("Subj",), ABSTAIN),  # G3 co-location fails -> ABSTAIN
      ("gran_guard",      "X was published in 1786.", Q,
                          {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK, ("Subj",), ABSTAIN),     # |1786-1785|=1 <=2 -> ABSTAIN
      ("abstain_weakres", "X was published in 1799.", QL,
                          {"years_by_pred": {"P577": ["1785"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK, ("Subj",), ABSTAIN),
      ("abstain_ambig",   "X was published in 1799.", Q,
                          {"years_by_pred": {"P577": ["1785", "1801"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK, ("Subj",), ABSTAIN),
      ("abstain_neterr",  "X was published in 1799.", Q, {"_err": "stub"}, ART_OK, ("Subj",), ABSTAIN),
      ("abstain_unres",   "X was published in 1799.", None, {}, ART_OK, ("Subj",), ABSTAIN),
      ("confirm_wins",    "X published in 1785 and 1900.", Q,
                          {"years_by_pred": {"P577": ["1785", "1900"]}, "enwiki_title": "Subj", "p31": ["Q13442814"]},
                          ART_OK, ("Subj",), CONFIRM),
    ]
    ok = True
    for name, claim, res, ed, art, subj, exp in cases:
        got = verdict(claim, res, ed, art, subj)
        flag = "PASS" if got == exp else "FAIL"
        if got != exp:
            ok = False
        print("  %-16s expect=%-8s got=%-8s  %s" % (name, exp, got, flag))

    # v296: reconstruct_titles unit assertions (offline, deterministic). emit == reconstructed runs.
    print("  -- reconstruct_titles --")
    title_cases = [
        ("origin_unquoted",  "On the Origin of Species was published in 1872.",
                             ["On the Origin of Species"]),
        ("dialogue_unquoted","Dialogue Concerning the Two Chief World Systems appeared in 1610.",
                             ["Dialogue Concerning the Two Chief World Systems"]),
        ("treatise_drops_A", "A Treatise of Human Nature shaped ethics.",
                             ["Treatise of Human Nature"]),
        ("principia_allcap", "Philosophiae Naturalis Principia Mathematica was issued in 1750.",
                             []),                                    # pure all-cap -> probe binds, skip
        ("no_title_plain",   "The paper was published in 1799.", []),
        ("single_cap",       "Newton studied motion.", []),
    ]
    for name, sent, exp in title_cases:
        got = reconstruct_titles(sent)
        flag = "PASS" if got == exp else "FAIL"
        if got != exp:
            ok = False
        print("  %-16s exp=%s got=%s  %s" % (name, exp, got, flag))

    print("\n[selftest] %s" % ("ALL PASS" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    src = sys.argv[1] if len(sys.argv) > 1 else "heldout_clean_20260625.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "o0_layer2_verdicts.jsonl"
    run(src, dst)
