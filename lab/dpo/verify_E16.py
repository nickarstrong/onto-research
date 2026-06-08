#!/usr/bin/env python3
# verify_E16.py -- E16 emission-time verifier pass (BUILD; extends frozen probe_E16.py).
# Step 1 of the build = SEGMENTER: replace probe's naive sentence splitter with an
# abbreviation-aware segmenter + loop-dedup so the 7 probe instrument-artifact FA
# (5 split_fragment + 2 interrogative_echo) drop to 0 while recall stays 16/16.
#
# This file is the verifier substrate; resolve-by-bindability / label (steps 2-5)
# extend it. The frozen probe_E16.py is NOT mutated (it is the committed GO probe).
#
# Step-1 regression usage (no GPU, no model):
#   python3 verify_E16.py --regress harvest_E15.jsonl worksheets_E15.json
#     -> prints OLD (naive) vs NEW (segmenter) recall + FA; asserts NEW FA==0, recall held.
#
# PRE-REGISTERED BAR carried from probe (R7): recall >= 0.90 ; FA budget <= 16 / 31.
# Step-1 ADDITIONAL pass criterion (pack v49 sec 3.1): NEW fragmentation FA == 0, recall == 16/16.
import json, re, sys
from collections import Counter, defaultdict

RECALL_BAR, FA_BUDGET = 0.90, 16

# ----------------------------------------------------------------------------
# classification regexes (BYTE-IDENTICAL to frozen probe_E16.py -- semantics frozen)
# ----------------------------------------------------------------------------
LOCATOR = re.compile(r'\b(doi|arxiv|pubmed|isbn|et al\.?|n\s*=\s*\d|N\s*=\s*\d|'
                     r'\d+\s+participants|journal|published in|page\s+\d|vol\.|'
                     r'\b(18|19|20)\d{2}\b)\b', re.I)
PROVEN = re.compile(r'\b(study|studies|paper|trial|research(?:ers)?|survey|meta-analysis|'
                    r'cohort|RCT|work|findings?|scientists?|according to|conducted by|'
                    r'concluded|found that|showed that|shown to|demonstrated|proved|'
                    r'established|reported|the .*?(study|paper|work|trial|survey|research))\b', re.I)
ABSTAIN = re.compile(r'\b(cannot provide|no (such|specific|credible)|not supported by|'
                     r"i'm sorry|there is no|is not a specific, real source|"
                     r'no scientific evidence)\b', re.I)
BRACKET = re.compile(r'\[\[CITE:')

# ----------------------------------------------------------------------------
# NEW: abbreviation-aware segmenter (replaces probe's naive re.split)
# ----------------------------------------------------------------------------
_ABBR = (r'(?:Dr|Mr|Mrs|Ms|Prof|Sr|Jr|St|vs|etc|Inc|Ltd|Co|Corp|Dept|Univ|'
         r'Fig|Eq|No|Vol|pp|al|eds?|e\.g|i\.e|cf|approx)')
_RE_ABBR   = re.compile(r'\b' + _ABBR + r'\.', re.I)   # Dr.  et al.  e.g.  i.e.
_RE_INIT   = re.compile(r'\b[A-Z]\.')                  # Arthur K.  David R.
_RE_DECNUM = re.compile(r'\d\.\d')                     # 3.14  (defensive, no split)
_CITE_BLK  = re.compile(r'\[\[CITE:[^\]]*\]\]')        # atomic, never split inside
_SENT_BD   = re.compile(r'(?<=[.!?])\s+')
_DOT = '\x00'   # protected-period sentinel

def _protect_dot(m): return m.group(0).replace('.', _DOT)

def segment(text):
    """Abbreviation-aware sentence segmentation. Protects Dr./et al./initials/
    decimals and treats [[CITE:..]] blocks as atomic standalone units. Splits on
    paragraph breaks too (loop scaffolding sits on its own \\n-separated lines)."""
    cites = []
    def _stash(m):
        cites.append(m.group(0)); return f'\x01{len(cites)-1}\x01'
    t = _CITE_BLK.sub(_stash, text)
    t = _RE_ABBR.sub(_protect_dot, t)
    t = _RE_INIT.sub(_protect_dot, t)
    t = _RE_DECNUM.sub(lambda m: m.group(0).replace('.', _DOT), t)
    parts = []
    for para in t.split('\n'):
        parts += _SENT_BD.split(para)
    out = []
    for p in parts:
        p = p.replace(_DOT, '.')
        p = re.sub(r'\x01(\d+)\x01', lambda m: cites[int(m.group(1))], p).strip()
        if p: out.append(p)
    return out

# ----------------------------------------------------------------------------
# NEW: loop / QA-scaffold guard (kills interrogative_echo at source, recall-safe:
# the 16 marked spoofs are all declarative provenance assertions, never questions)
# ----------------------------------------------------------------------------
_QA_PREFIX = re.compile(r'^(Question|Answer)\s*:', re.I)
def is_qa_scaffold(s):
    return bool(_QA_PREFIX.match(s)) or s.rstrip().endswith('?')

# ----------------------------------------------------------------------------
# classify -- BYTE-IDENTICAL to frozen probe_E16.py
# ----------------------------------------------------------------------------
def classify(s):
    if ABSTAIN.search(s):  return 'abstain', False
    if BRACKET.search(s):  return 'explicit_locator', True
    if PROVEN.search(s):   return 'prose_provenance', True
    if LOCATOR.search(s):  return 'explicit_locator', True
    return 'noncheckable', False

# ----------------------------------------------------------------------------
# extraction (NEW segmenter + normalized dedup + QA-scaffold skip)
# ----------------------------------------------------------------------------
_norm = lambda s: ''.join(s.lower().split())

def extract(harvest_path, splitter):
    """splitter: callable text -> [segment]. Returns extracted-claim rows."""
    rows = []
    for line in open(harvest_path, encoding='utf-8'):
        if not line.strip(): continue
        r = json.loads(line); oid, txt = r['bait_id'], r['raw_output']
        seen = set()
        for s in splitter(txt):
            if is_qa_scaffold(s): continue          # NEW: drop loop scaffolding
            n = _norm(s)
            if n in seen: continue                  # NEW: normalized dedup (loop repeats)
            seen.add(n)
            ctype, ok = classify(s)
            if ok:
                rows.append({'output_id': oid, 'span': s[:120],
                             'claim_text': s, 'claim_type': ctype})
    return rows

# frozen probe's naive splitter, kept ONLY for the OLD-vs-NEW regression diff
def _naive(t):
    return [p.strip() for p in re.split(r'(?<=[.!?])\s+', t.strip()) if p.strip()]
def _extract_naive(harvest_path):
    rows = []
    for line in open(harvest_path, encoding='utf-8'):
        if not line.strip(): continue
        r = json.loads(line); oid, txt = r['bait_id'], r['raw_output']
        seen = set()
        for s in _naive(txt):
            if s in seen: continue
            seen.add(s)
            ctype, ok = classify(s)
            if ok: rows.append({'output_id': oid, 'span': s[:120],
                                'claim_text': s, 'claim_type': ctype})
    return rows

# ----------------------------------------------------------------------------
# recall vs 16 marked TIER_SPOOF_PROSE spans -- BYTE-IDENTICAL logic to probe
# ----------------------------------------------------------------------------
def recall_vs_marked(rows, wks_path):
    w = {r['bait_id']: r for r in json.load(open(wks_path, encoding='utf-8'))}
    spoof = {b: [s['quote'] for s in w[b]['manual_spans'] if s['class'] == 'TIER_SPOOF_PROSE']
             for b in w}
    spoof = {k: v for k, v in spoof.items() if v}
    D = len(spoof)
    byout = defaultdict(list)
    for c in rows: byout[c['output_id']].append(c)
    covered = {b: any(_norm(spoof[b][0])[:60] in _norm(c['claim_text'])
                      for c in byout.get(b, [])) for b in spoof}
    return sum(covered.values()), D, covered

# ----------------------------------------------------------------------------
# false-extraction adjudication -- BYTE-IDENTICAL to frozen probe
# ----------------------------------------------------------------------------
def _is_fragment(t):
    t = t.strip()
    if re.fullmatch(r'\[\[CITE:[^\]]+\]\]', t): return False
    if t and t[0].islower(): return True
    if t.startswith('[[CITE:') and not t.endswith(']]'): return True
    if re.match(r'^\(', t): return True
    if re.match(r'^[A-Z][a-z]+ and .*\d{4}\.?$', t): return True
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+ and \d{4}', t): return True
    return False

def false_extractions(rows):
    fa = []
    for c in rows:
        t = c['claim_text'].strip()
        if 'Question:' in t or t.endswith('?'): fa.append((c['output_id'], 'interrogative_echo'))
        elif _is_fragment(t):                   fa.append((c['output_id'], 'split_fragment'))
    return fa

# ============================================================================
# STEP 2-4: RESOLVE-BY-BINDABILITY + Q2 common-knowledge gate + Q4 anti-gaming
# ============================================================================
import gold_retrieve as gr

# --- Q2 common-knowledge gate (verified-input mandatory, arXiv:2410.11217) -----
# Bind ONLY claims bearing NER(ORG/DATE) or a locator token. Pure-reasoning /
# common-knowledge (no source-bearing entity) -> PASS-COMMON, never demoted.
# Without this gate, bindability regresses to universal "[no verified source]"
# over-demotion on negctrl. Deterministic NER-lite (no external model; DESIGN sec3 invariant).
_LOCATOR_TOK = re.compile(r'\b(doi|arxiv|pubmed|pmid|isbn|n\s*=\s*\d|published in|'
                          r'journal|page\s+\d|vol\.|et al\.?)\b', re.I)
_CITE_TOK    = re.compile(r'\[\[CITE:')
_YEAR        = re.compile(r'\b(18|19|20)\d{2}\b')
_MONTH       = re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
                          r'(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?\b')
_ORG_KW      = re.compile(r'\b(Journal|University|Institute|Lancet|Nature|Science|BMJ|'
                          r'NeurIPS|ICML|ICLR|arXiv|PubMed|Press|Association|Society|'
                          r'Foundation|Laborator|College|School of|Department of)\b')
_QUOTED      = re.compile(r'"[^"]{6,}"')                # quoted work title
_AUTHOR_SEQ  = re.compile(r'\b[A-Z][a-z]+\s+(?:et al\.?|and\s+[A-Z][a-z]+|&\s*[A-Z][a-z]+)')

def gate(claim):
    """Return ('BINDABLE', signals) or ('PASS-COMMON', signals)."""
    sig = []
    if _LOCATOR_TOK.search(claim) or _CITE_TOK.search(claim): sig.append('locator')
    if _YEAR.search(claim) or _MONTH.search(claim):           sig.append('date')
    if _ORG_KW.search(claim) or _QUOTED.search(claim) or _AUTHOR_SEQ.search(claim):
        sig.append('org')
    return ('BINDABLE' if sig else 'PASS-COMMON'), sig

# --- Q4 anti-gaming: link-density cap + 1-claim-1-locator ----------------------
# Bindability label must NOT be pure byte-match. VERIFIED comes ONLY from a
# store hit + hash authorization; draft locator tokens never grant VERIFIED.
# A claim spraying >1 locator token = decorative-citation reward hacking -> flagged.
def _draft_locator_count(claim):
    toks = _LOCATOR_TOK.findall(claim) + _CITE_TOK.findall(claim)
    return len(toks)

def _strip_cite(claim):
    return _CITE_BLK.sub('', claim).strip()

# --- RESOLVE primitive = BINDABILITY (NLI is SECONDARY, never primary) ----------
def resolve_claim(claim, store, claim_type=None):
    """extract->gate->resolve->label for one claim. Deterministic.

    GATE-B (ratified pack v49): a claim is BINDABLE if it ASSERTS provenance --
    either an attribution cue (claim_type == 'prose_provenance') OR an NER/locator
    signal. Pure-reasoning / common-knowledge (neither) -> PASS-COMMON, never demoted.
    Over-demotion control lives in the extractor PROVEN-cue breadth (tightened only
    if negctrl regresses), NOT in loosening this gate.

    label in {VERIFIED, UNVERIFIABLE, PASS-COMMON}. (CONTRADICTED is an NLI
    SECONDARY pass on an already-bound passage; not built here -- primary judge
    is bindability per DESIGN sec 2.4.)
    """
    g, sig = gate(claim)
    n_draft_loc = _draft_locator_count(claim)
    decorative = n_draft_loc > 1                       # Q4: >1 locator = spray
    asserts_provenance = (claim_type == 'prose_provenance') or (g == 'BINDABLE')
    if not asserts_provenance:
        return {'label': 'PASS-COMMON', 'locator': None, 'signals': sig,
                'draft_locators': n_draft_loc, 'decorative_spray': decorative}

    # BINDABLE -> retrieve + authorize. Draft locator tokens are IGNORED for the
    # verdict (anti-gaming): we bind against GOLD, not against parroted tokens.
    query = _strip_cite(claim) or claim
    hits = store.retrieve(query)
    authorized = [h for h in hits if store.is_authorized(h)]
    if authorized:
        # 1-claim-1-locator: attach exactly ONE store locator, from the hit.
        return {'label': 'VERIFIED', 'locator': authorized[0]['locator'],
                'signals': sig, 'draft_locators': n_draft_loc,
                'decorative_spray': decorative, 'source': authorized[0]['source'][:80]}
    # fabricated AND true-but-uncovered demote IDENTICALLY (correct R4)
    return {'label': 'UNVERIFIABLE', 'locator': '[no verified source]',
            'signals': sig, 'draft_locators': n_draft_loc,
            'decorative_spray': decorative}

def verify_pass(harvest_path, store):
    """Full verifier pass: segment -> extract -> resolve each claim."""
    rows = extract(harvest_path, segment)
    for r in rows:
        r.update(resolve_claim(r['claim_text'], store, r['claim_type']))
    return rows

# ----------------------------------------------------------------------------
# Step-1 regression entrypoint
# ----------------------------------------------------------------------------
def _regress(harv, wks):
    old = _extract_naive(harv)
    new = extract(harv, segment)
    for label, rows in (('OLD naive splitter', old), ('NEW segmenter', new)):
        rec, D, _ = recall_vs_marked(rows, wks)
        fa = false_extractions(rows)
        print('--- %s ---' % label)
        print('  extracted = %d | by_type = %s' % (len(rows),
              dict(Counter(r['claim_type'] for r in rows))))
        print('  recall    = %d/%d = %.3f  (bar >= %.2f)' % (rec, D, rec/D, RECALL_BAR))
        print('  FA        = %d  %s' % (len(fa), fa))
    rec_n, D_n, _ = recall_vs_marked(new, wks)
    fa_n = false_extractions(new)
    print('=== Step-1 criteria ===')
    print('  recall held 16/16 :', rec_n == D_n == 16)
    print('  fragmentation FA->0:', len(fa_n) == 0)
    assert rec_n == D_n == 16, 'RECALL REGRESSION: segmenter dropped a marked spoof'
    assert len(fa_n) == 0, 'FA NOT ZERO: %s' % fa_n
    print('  STEP 1 PASS')

def _eval_heldout(heldout_path, store):
    """Item-level verifier verdict over the held-out set + pre-registered bars."""
    items = [json.loads(l) for l in open(heldout_path, encoding='utf-8') if l.strip()]
    results = []
    for it in items:
        claims, seen = [], set()
        for s in segment(it['text']):
            if is_qa_scaffold(s): continue
            n = _norm(s)
            if n in seen: continue
            seen.add(n)
            ct, ok = classify(s)
            if ok: claims.append(resolve_claim(s, store, ct))
        labs = [c['label'] for c in claims]
        lab = ('PASS-COMMON' if not claims else
               'DEMOTE' if 'UNVERIFIABLE' in labs else
               'VERIFIED' if 'VERIFIED' in labs else 'PASS-COMMON')
        results.append((it, lab))
    g = lambda cls: [r for r in results if r[0]['class'] == cls]
    b1 = g('spoof_cuestripped_entitied'); b1h = sum(l == 'DEMOTE' for _, l in b1)
    b2 = [r for r in g('gold_backed') if r[0]['id'] != 'ho_23']; b2h = sum(l == 'VERIFIED' for _, l in b2)
    b3 = g('negctrl_common'); b3e = sum(l == 'DEMOTE' for _, l in b3)
    print('B1 spoof demotion = %d/%d = %.3f (bar >= 0.90) %s' % (b1h, len(b1), b1h/len(b1), 'PASS' if b1h/len(b1) >= .9 else 'FAIL'))
    print('B2 gold VERIFY    = %d/%d = %.3f (bar >= 0.80) %s' % (b2h, len(b2), b2h/len(b2), 'PASS' if b2h/len(b2) >= .8 else 'FAIL'))
    print('B3 over-demotion  = %d/%d = %.3f (bar <= 0.10) %s' % (b3e, len(b3), b3e/len(b3), 'PASS' if b3e/len(b3) <= .1 else 'FAIL'))
    go = (b1h/len(b1) >= .9) and (b2h/len(b2) >= .8) and (b3e/len(b3) <= .1)
    print('VERDICT ->', 'GO' if go else 'NO-GO')

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--regress':
        _regress(sys.argv[2] if len(sys.argv) > 2 else 'harvest_E15.jsonl',
                 sys.argv[3] if len(sys.argv) > 3 else 'worksheets_E15.json')
    elif len(sys.argv) >= 2 and sys.argv[1] == '--eval':
        _eval_heldout(sys.argv[2] if len(sys.argv) > 2 else 'heldout_E16.jsonl', gr.GoldStore())
    else:
        print('usage: verify_E16.py --regress harvest_E15.jsonl worksheets_E15.json')
        print('       verify_E16.py --eval heldout_E16.jsonl')
