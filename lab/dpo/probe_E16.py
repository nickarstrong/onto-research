#!/usr/bin/env python3
# probe_E16.py -- E16 no-GPU GO/NO-GO probe (extraction-recall on E15 prose spoofs).
# Self-contained + reproducible. Rule-layer extractor (VeriScore-style decontextualization,
# TARGET = [subject+claim+locator] triples on PROSE) + recall vs the 16 manually-marked
# TIER_SPOOF_PROSE spans + deterministic false-extraction adjudication + pre-registered verdict.
# Verifier-class judgment (Opus, in-session) was applied on top; this script is the substrate.
#
# Inputs  (_local, gitignored): harvest_E15.jsonl, worksheets_E15.json
# Output  (_local, gitignored): extracted_claims_E16.jsonl
# Usage: python3 probe_E16.py harvest_E15.jsonl worksheets_E15.json extracted_claims_E16.jsonl
#
# PRE-REGISTERED BAR (R7, locked before run): recall >= 0.90 ; FA budget <= 16 across 31.
import json, re, sys
from collections import Counter, defaultdict

HARV = sys.argv[1] if len(sys.argv) > 1 else 'harvest_E15.jsonl'
WKS  = sys.argv[2] if len(sys.argv) > 2 else 'worksheets_E15.json'
OUT  = sys.argv[3] if len(sys.argv) > 3 else 'extracted_claims_E16.jsonl'
RECALL_BAR, FA_BUDGET = 0.90, 16

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

def sentences(t):
    return [p.strip() for p in re.split(r'(?<=[.!?])\s+', t.strip()) if p.strip()]

def classify(s):
    if ABSTAIN.search(s):                 return 'abstain', False
    if BRACKET.search(s):                 return 'explicit_locator', True
    if PROVEN.search(s):                  return 'prose_provenance', True
    if LOCATOR.search(s):                 return 'explicit_locator', True
    return 'noncheckable', False

# --- extract ---
rows = []
for line in open(HARV):
    if not line.strip(): continue
    r = json.loads(line); oid, txt = r['bait_id'], r['raw_output']
    seen = set()
    for s in sentences(txt):
        if s in seen: continue
        seen.add(s)
        ctype, ok = classify(s)
        if ok: rows.append({'output_id': oid, 'span': s[:120],
                            'claim_text': s, 'claim_type': ctype})
with open(OUT, 'w') as f:
    for row in rows: f.write(json.dumps(row, ensure_ascii=False) + '\n')

# --- recall vs 16 marked spans ---
w = {r['bait_id']: r for r in json.load(open(WKS))}
spoof = {b: [s['quote'] for s in w[b]['manual_spans'] if s['class'] == 'TIER_SPOOF_PROSE']
         for b in w}
spoof = {k: v for k, v in spoof.items() if v}
D = len(spoof)
byout = defaultdict(list)
for c in rows: byout[c['output_id']].append(c)
norm = lambda s: ''.join(s.lower().split())
covered = {b: any(norm(spoof[b][0])[:60] in norm(c['claim_text']) for c in byout.get(b, []))
           for b in spoof}
recall = sum(covered.values())

# --- false-extraction adjudication (deterministic) ---
def is_fragment(t):
    t = t.strip()
    if re.fullmatch(r'\[\[CITE:[^\]]+\]\]', t): return False     # valid standalone locator
    if t[0].islower(): return True
    if t.startswith('[[CITE:') and not t.endswith(']]'): return True
    if re.match(r'^\(', t): return True
    if re.match(r'^[A-Z][a-z]+ and .*\d{4}\.?$', t): return True
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+ and \d{4}', t): return True
    return False
fa = []
for c in rows:
    t = c['claim_text'].strip()
    if 'Question:' in t or t.endswith('?'): fa.append((c['output_id'], 'interrogative_echo'))
    elif is_fragment(t):                    fa.append((c['output_id'], 'split_fragment'))

go = (recall / D >= RECALL_BAR) and (len(fa) <= FA_BUDGET)
print('extracted claims =', len(rows), '| by_type =', dict(Counter(r['claim_type'] for r in rows)))
print('recall = %d/%d = %.3f  (bar >= %.2f)' % (recall, D, recall / D, RECALL_BAR))
print('FA     = %d            (budget <= %d)  %s' % (len(fa), FA_BUDGET, fa))
print('VERDICT ->', 'GO' if go else 'NO-GO')
