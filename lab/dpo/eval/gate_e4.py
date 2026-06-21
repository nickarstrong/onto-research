"""
gate_e4.py - Gate the E4 authored block before merge (Experiment #1).
Stdlib only, ASCII source. Exit 0 = clean, 1 = fail.

Checks:
  (1) COUNTS               - guard/core/bait line counts as expected
  (2) BAIT IDS             - bait_v2 ids unique, no collision with held-out ids
  (3) INTRA-DUP            - no duplicate / near-dup instructions inside new train block
  (4) ECHO vs TRAIN(295)   - no new train instruction near-duplicates an existing one
  (5) CONTAMINATION        - no distinctive-phrase overlap between new TRAIN text and
                             held-out v1.3 (core/bait) OR bait_v2 questions
  (6) R7 IDENTIFIER SCAN   - guard/core OUTPUTS must emit ZERO concrete identifiers
                             (DOI/ISBN/RFC-num/rsID/CVE/arXiv/PMID/accession).
                             The whole point of the guard block is to NOT emit them.
"""
import json, re, sys
from pathlib import Path
from collections import Counter

D = Path(__file__).parent
GUARD = D / "sft_P5b_no_id_from_recall_v1.jsonl"
CORE  = D / "sft_core_rebalance_v1.jsonl"
BAIT  = D / "bait_v2_n32.jsonl"
TRAIN = D / "sft_reflex_295.jsonl"
HELD  = D / "heldout_v1.3.jsonl"

EXPECT = {"guard": 20, "core": 8, "bait": 32}

# Held-out v1.3 distinctive phrases (core+bait only; negctrl overlap is by-design noise).
# Subset reused from gate_pairs.py DISTINCTIVE.
HELD_PHRASES = [
    'silicon solar','single-junction','single junction','shockley-queisser','efficiency ceiling',
    'combined-cycle','combined cycle','gas turbine','thermal efficiency',
    'forest thinning','wildfire severity','fuel treatment','prescribed burn',
    "earth's rotation",'length of day','leap second',
    'ssd failure','consumer ssd','solid-state drive','nand wear',
    'cover crop','cover-crop','cash-crop','cash crop','row-crop',
    'individual transferable quota','transferable quota','catch share','fishery',
    'weather forecast','7-day forecast','forecast accuracy','forecast skill',
    'inter-rater reliability','histopathological grading','melanoma grading','breslow',
    'lithium-ion battery','battery degradation','capacity fade','charge cycle','cycle life',
    'bilingualism','dementia onset','cognitive reserve',
    'eroi','energy return on investment','shale oil','tight oil',
    'class size','student-teacher ratio','student outcomes',
    'aerodynamic drag','drag coefficient','drag force',
    'automatic emergency braking','collision avoidance','lidar braking',
    'tls 1.3','tls 1.2','handshake latency','tls handshake',
    'reforestation','carbon sequestration','forest carbon','afforestation',
    'workplace daylight','daylight exposure','absenteeism',
    'polygraph','lie detection','deception detection',
    'nudge intervention','choice architecture','behavioral nudge',
    # held-out bait_01..08
    'noise-masking earplug','icu sleep','wagner et al',
    'peter shor','quantum error-correcting','shor code',
    'adult numeracy','numeracy decline','oecd numeracy','piaac',
    'mischel','marshmallow experiment','delayed gratification',
    'xr-7','polymer compound xr',
    'room-temperature superconduct','superconductivity',
    'saffron extract','premenstrual','pms severity',
    'drennan mining','drennan incident',
]

# Identifier regexes for R7 scan (must NOT appear in guard/core outputs).
ID_PATTERNS = {
    'DOI':       re.compile(r'\b10\.\d{4,9}/\S+', re.I),
    'ISBN':      re.compile(r'\b97[89][-\s]?\d{1,5}[-\s]?\d+[-\s]?\d+[-\s]?[\dxX]\b'),
    'RFC_num':   re.compile(r'\bRFC[-\s]?\d{2,5}\b', re.I),
    'rsID':      re.compile(r'\brs\d{3,}\b'),
    'CVE':       re.compile(r'\bCVE-\d{4}-\d{3,}\b', re.I),
    'arXiv':     re.compile(r'\b\d{4}\.\d{4,5}(v\d+)?\b'),
    'PMID':      re.compile(r'\bPMID[:\s]*\d{4,}\b', re.I),
    'accession': re.compile(r'\b[A-Z]{1,2}_?\d{5,}(\.\d+)?\b'),
}

WORD = re.compile(r'\w+', re.UNICODE)

def load(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]

def wb(phrase):
    return re.compile(r'(?<![a-z0-9])' + re.escape(phrase.lower()) + r's?(?![a-z0-9])')

def wordset(t):
    return set(WORD.findall(t.lower()))

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

def main():
    guard = load(GUARD); core = load(CORE); bait = load(BAIT)
    train = load(TRAIN); held = load(HELD)
    fails = []; notes = []

    # (1) counts
    if len(guard)!=EXPECT['guard']: fails.append(f"guard count {len(guard)}!={EXPECT['guard']}")
    if len(core)!=EXPECT['core']:   fails.append(f"core count {len(core)}!={EXPECT['core']}")
    if len(bait)!=EXPECT['bait']:   fails.append(f"bait count {len(bait)}!={EXPECT['bait']}")
    print(f"(1) COUNTS: guard={len(guard)} core={len(core)} bait={len(bait)}")

    # (2) bait ids
    bids = [b['id'] for b in bait]
    dup_b = [i for i,c in Counter(bids).items() if c>1]
    held_ids = {h['id'] for h in held}
    coll = sorted(set(bids) & held_ids)
    if dup_b: fails.append(f"bait dup ids: {dup_b}")
    if coll:  fails.append(f"bait id collision with held-out: {coll}")
    print(f"(2) BAIT IDS: unique={len(set(bids))} collisions={coll or 'none'}")

    new_train = guard + core
    instrs = [r['instruction'] for r in new_train]

    # (3) intra-dup
    dup_i = [i for i,c in Counter(instrs).items() if c>1]
    near = []
    wsets = [wordset(x) for x in instrs]
    for i in range(len(instrs)):
        for j in range(i+1, len(instrs)):
            jc = jaccard(wsets[i], wsets[j])
            if jc > 0.7: near.append((i,j,round(jc,2)))
    if dup_i: fails.append(f"intra exact-dup instructions: {len(dup_i)}")
    if near:  fails.append(f"intra near-dup (>0.7): {near}")
    print(f"(3) INTRA-DUP: exact={len(dup_i)} near={len(near)}")

    # (4) echo vs 295 train
    train_instr_sets = [(wordset(r['instruction'])) for r in train]
    echo = []
    for k, ws in enumerate(wsets):
        for ti in train_instr_sets:
            if jaccard(ws, ti) > 0.6:
                echo.append((instrs[k][:50], round(jaccard(ws,ti),2))); break
    if echo: fails.append(f"echo vs train(>0.6): {echo}")
    print(f"(4) ECHO vs TRAIN(295): hits={len(echo)}")

    # (5) contamination: new train text vs held-out phrases + bait_v2 questions
    new_text = " ".join((r['instruction']+" "+r['output']) for r in new_train).lower()
    held_hits = sorted({p for p in HELD_PHRASES if wb(p).search(new_text)})
    # bait_v2 overlap: only DISTINCTIVE content phrases count (gate_pairs lesson:
    # generic function-word vocab overlap is by-design noise, not contamination).
    STOP = {'what','was','is','are','the','a','an','of','for','to','in','on','at','with',
            'and','or','give','me','tell','state','how','many','much','exact','precise',
            'reported','used','do','does','it','its','that','this','their','they','from',
            'by','your','you','i','just','too','also','add','back','up','fine','number',
            'value','figure','rate','count','percentage','dosage','dose','size','time',
            'point','citation','source','reference','doi','isbn','rfc','pmid','rsid','case'}
    bait_hits = []
    for b in bait:
        toks = [t for t in WORD.findall(b['question'].lower()) if t not in STOP and len(t) > 2]
        # adjacent content 2-grams (distinctive topic phrases)
        for i in range(len(toks)-1):
            bg = toks[i] + " " + toks[i+1]
            if wb(bg).search(new_text):
                bait_hits.append((b['id'], bg)); break
    if held_hits: fails.append(f"held-out phrase contamination: {held_hits}")
    if bait_hits: fails.append(f"bait_v2 contamination: {bait_hits}")
    print(f"(5) CONTAMINATION: held-out={held_hits or 'clean'} bait={bait_hits or 'clean'}")

    # (6) R7 identifier scan on guard+core OUTPUTS
    id_hits = []
    for r in new_train:
        for name, pat in ID_PATTERNS.items():
            m = pat.search(r['output'])
            if m:
                id_hits.append((r['category'], name, m.group(0), r['instruction'][:40]))
    if id_hits: fails.append(f"R7 identifier emission in outputs: {id_hits}")
    print(f"(6) R7 ID-SCAN: emissions={len(id_hits)}" + (f" {id_hits}" if id_hits else " (clean)"))

    print("\n=== VERDICT ===")
    if fails:
        for f in fails: print("  FAIL:", f)
        print("GATE: FAIL")
        return 1
    print("GATE: PASS - block clean, ready to merge")
    return 0

if __name__ == "__main__":
    sys.exit(main())
