#!/usr/bin/env python3
# E9 gate: collision/overlap of authored DPO prompts vs PRIVATE eval sets.
# Real collision = shared DISTINCTIVE n-gram (bigram/trigram of content tokens),
#   matched with word-boundary regex (base64-safe). 0 allowed = PASS.
# By-design vocab overlap = shared single common tokens -> sub-threshold report only.
import json, re, sys, hashlib
from pathlib import Path

PAIRS   = Path("data/onto_e9_dpo_pairs.jsonl")
HELDOUT = Path("eval/heldout_v1.3.jsonl")
BAIT    = Path("eval/bait_v2_n32.jsonl")

STOP = set("a an the of to in on at for and or with by is are was were be been "
           "what whats how much many give me the precise exact state provide your "
           "you do does did that this these those it its from as per just too also "
           "please tell paste add back up plus number per healthy adult adults".split())

def tokens(s):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP and len(t) > 2]

def ngrams(toks, n):
    return {" ".join(toks[i:i+n]) for i in range(len(toks)-n+1)}

def distinctive(s):
    t = tokens(s)
    return ngrams(t, 2) | ngrams(t, 3)

def wb(phrase, text):
    # word-boundary, base64-safe: no alnum immediately adjacent
    pat = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
    return re.search(pat, text.lower()) is not None

pairs = [json.loads(l) for l in open(PAIRS, encoding="utf-8")]
ref = []
for f in (HELDOUT, BAIT):
    if not f.is_file():
        print(f"ERROR: missing reference set {f}"); sys.exit(2)
    for l in open(f, encoding="utf-8"):
        if l.strip():
            d = json.loads(l); ref.append((d["id"], d["question"]))

ref_phrases = {}
for rid, q in ref:
    for ph in distinctive(q):
        ref_phrases.setdefault(ph, []).append(rid)
ref_tokens = {}
for rid, q in ref:
    for tk in set(tokens(q)):
        ref_tokens.setdefault(tk, set()).add(rid)

log = []
log.append("# E9 GATE REPORT")
log.append(f"pairs={len(pairs)}  ref_items={len(ref)} (heldout {sum(1 for _ in open(HELDOUT))} + bait {sum(1 for _ in open(BAIT))})")
log.append("")

# 1) exact prompt collision
exact = 0
ref_q_norm = {re.sub(r'\s+',' ',q.strip().lower()) for _,q in ref}
for p in pairs:
    if re.sub(r'\s+',' ',p["prompt"].strip().lower()) in ref_q_norm:
        log.append(f"EXACT-COLLISION {p['id']}"); exact += 1

# 2) distinctive n-gram collisions (HARD)
hard = 0
for p in pairs:
    hits = []
    for ph in distinctive(p["prompt"]):
        if ph in ref_phrases:
            # confirm with word-boundary match in at least one ref question text
            for rid, q in ref:
                if rid in ref_phrases[ph] and wb(ph, q):
                    hits.append((ph, rid)); break
    if hits:
        hard += len(hits)
        for ph, rid in hits:
            log.append(f"HARD-COLLISION {p['id']} <-> {rid}: '{ph}'")

# 3) sub-threshold single-token shared vocab (expected, report only)
log.append("")
log.append("## sub-threshold shared single tokens (expected vocab overlap, NOT a failure)")
subt = {}
for p in pairs:
    for tk in set(tokens(p["prompt"])):
        if tk in ref_tokens:
            subt.setdefault(tk, set()).update(ref_tokens[tk])
if subt:
    for tk in sorted(subt):
        log.append(f"  '{tk}' shared with {len(subt[tk])} ref item(s)")
else:
    log.append("  (none)")

md5 = hashlib.md5(open(PAIRS,"rb").read()).hexdigest()
log.append("")
log.append(f"## md5(onto_e9_dpo_pairs.jsonl) = {md5}")
verdict = "PASS" if (exact == 0 and hard == 0) else "FAIL"
log.append(f"## exact_collisions={exact}  hard_collisions={hard}")
log.append(f"## GATE VERDICT: {verdict}")

out = "\n".join(log)
print(out)
Path("eval/gate.log").write_text(out + "\n", encoding="utf-8")
sys.exit(0 if verdict == "PASS" else 1)
