#!/usr/bin/env python3
# verify_E16_A.py -- A-CHANNEL self-consistency checker (G3 of the self-checkup loop v0).
#
# DOCTRINE (STRATEGY_selfcheckup_loop_v0 rev2 sec1): discipline splits in two.
#   A. SELF-CONSISTENCY  -- needs NO source/corpus/DOI. Runs structurally on the system's
#                           OWN output. Cheapest, fastest, most relevant to self-development.
#   B. IS-IT-GROUNDED    -- verify_E16.resolve_claim (L1-L3) + verify_E16_L4 (L4). Substrate-bound.
# This module is the A-channel. It NEVER needs the GOLD store, a model, or the network.
#
# REUSE (import-only, BYTE-IDENTICAL, organ NOT mutated -- E40/step2b pattern):
#   verify_E16.segment / is_qa_scaffold / classify / gate / _norm / PROVEN / ABSTAIN
# The B-channel stays where it is; A adds detectors that read the SAME segmented claims.
#
# C1 PRECISION-FIRST (rev2 sec5): a FLAG must be trustworthy. Detectors fire only on a clear
#   violation; clean output must pass untouched (the fa-0.0333 asymmetry, held in A-space).
#   Q2 common-knowledge is respected: a bare number in a definitional/common claim is NOT a
#   provenance violation -- A1 fires only on an EMPIRICAL-result number with no source signal.
#
# GATING checks (change the item verdict):
#   A1 NUMBER_NO_SOURCE      (R4/R17) : empirical-result number, gate()==PASS-COMMON (no source signal).
#   A2 OVERCONFIDENT_UNGROUNDED (R2)  : overconfidence lexicon on an ungrounded claim.
#   A3 VAGUE_QUANT_NO_NUMBER (R1)     : vague quantifier + empirical noun, no number present.
#   A4 EMPTY_HEDGE           (R18)    : stacked hedges in a short, low-content span.
# ADVISORY checks (reported, NEVER gate -- mirror L5 I.3 method leg; deterministically FP-prone):
#   A5 UNFALSIFIABLE_UNIVERSAL (R6)   : unbounded universal assertion ("all/every/none ... ever").
#   A6 INTERNAL_CONTRADICTION  (R17)  : same normalized subject asserted and negated across claims.
#
# FALSIFIERS exercised by --selftest (rev2 sec7):
#   F-a : every deliberately-bad positive must trip a GATING flag (else detector is blind in-loop = VOID).
#   F-b : every clean negative must trip ZERO gating flags (else over-prune / castration).
# F-c (patch raises tier) and F-d audit-vs-verdict belong to G4 (patch-gen) -- out of A-channel scope.
#
# Usage (no GPU, no network, no store):
#   python3 verify_E16_A.py --selftest
#   python3 verify_E16_A.py --check some_output.txt
#   python3 verify_E16_A.py --eval labeled_A.jsonl     (Founder-labeled set; bars pre-registered, see SPEC)

import json, re, sys
from collections import defaultdict

import verify_E16 as v   # import-only; segment/classify/gate/_norm/PROVEN/ABSTAIN reused byte-identical

# ---------------------------------------------------------------- A-channel lexicons
# Numbers that look like measured results (percent, n=, plain magnitudes).
_NUM = re.compile(r'(?:\bn\s*=\s*\d+|\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\b)')
# An EMPIRICAL-result cue: PROVEN attribution OR "<num>% of <human/sample noun>".
_EMP_PCT = re.compile(r'\d+(?:\.\d+)?\s?%\s+of\s+(?:people|patients|participants|adults|children|'
                      r'cases|respondents|users|women|men|individuals|subjects|the population)\b', re.I)
# Overconfidence (R2). always/never REMOVED 2026-06-12 (c_adv_a2_2 "I will always be grateful"):
# they are unbounded universals -> A5 advisory, not epistemic overconfidence; the conflation FP'd a clean.
_OVERCONF = re.compile(r'\b(definitively|definitely|conclusively|undeniabl\w*|indisputabl\w*|'
                       r'irrefutabl\w*|unquestionabl\w*|proven|guarantee\w*|certainly|'
                       r'without\s+(?:a\s+)?doubt)\b', re.I)
# A2 attribution exemption (c_adv_a2_1 finding, Founder 2026-06-12): overconfidence is NOT a
# calibration fault when the claim attributes the proof to a NAMED source/domain ("definitively
# proven in Euclid's Elements"). Discriminator: claim + source-of-proof = clean ; claim + nothing
# = dirty. Requires a proof verb AND a preposition followed by a Capitalized source token.
_PROOF_VERB = re.compile(r'\b(prov\w*|establish\w*|demonstrat\w*|deriv\w*|shown)\b', re.I)
_ATTRIB_SRC = re.compile(r'\b(?:in|by|via|through|from)\s+(?:the\s+|a\s+)?'
                         r'(?:proof\s+in\s+(?:the\s+)?)?[A-Z][A-Za-z]')   # case-sensitive: Named source
# Vague quantifiers (R1) and the empirical nouns they must modify.
_VAGUE = re.compile(r'\b(many|most|numerous|several|substantial(?:ly)?|significant(?:ly)?|'
                    r'countless|various|multiple|majority|a\s+lot\s+of|lots\s+of|plenty\s+of)\b', re.I)
_EMP_NOUN = re.compile(r'\b(studies|study|papers?|research(?:ers)?|experiments?|trials?|surveys?|'
                       r'scientists?|people|participants|patients|cases|results|findings|data|'
                       r'sources|examples|effects?|benefits?|improvements?)\b', re.I)
# Hedges (R18). Empty-hedge = >=2 distinct hedges in a short, low-content span.
_HEDGE = re.compile(r'\b(might|may|perhaps|possibly|arguably|potentially|presumably|conceivably|'
                    r'seem(?:s|ed)?|appears?\s+to|could\s+be|to\s+some\s+extent|in\s+some\s+cases|'
                    r'it\s+is\s+possible|sort\s+of|kind\s+of|more\s+or\s+less|somewhat)\b', re.I)
# Advisory: unbounded universal (R6) and negation tokens (R6/R17).
_UNIVERSAL = re.compile(r'\b(all|every|none|no\s+\w+\s+ever|always|never|everyone|nobody|'
                        r'in\s+every\s+case|without\s+exception)\b', re.I)
_NEG = re.compile(r"\b(not|no|never|cannot|can't|don't|doesn't|isn't|aren't|without)\b", re.I)
# Negated-certainty (A2 disclaimer exemption, 2026-06-13): a certainty marker UNDER negation
# within its own clause ("can't/no guarantee", "not proven", "never certain") is calibrated
# honesty, the OPPOSITE of overconfidence. Deliberately excludes "without" (means "lacking",
# not a negator of the certainty). Found by the disposition-organ written-in clean condition
# tripping A2 on "I can't guarantee this will work...". Precision-first (C1).
_NEG_CERT = re.compile(r"\b(not|no|never|cannot|can't|won't|don't|doesn't|isn't|aren't|wasn't)\b", re.I)
_STOP = set('the a an of to in on at by for and or but is are was were be been being this that '
            'these those it its with as from into than then so such will would can could may might'.split())


def _content_words(s):
    toks = re.findall(r"[A-Za-z']+", s.lower())
    return [t for t in toks if t not in _STOP]


def _subject_key(s):
    """Crude normalized subject: first 1-3 content words before the main verb. Advisory only."""
    cw = _content_words(s)
    return ' '.join(cw[:3]) if cw else ''


def _neg_before(claim, m):
    """True if the certainty marker at match m sits under negation within its own clause
    (clause = text back to the previous ; , or .). 'I can't guarantee', 'no doubt'->no,
    but ';'/',' boundaries stop an unrelated earlier negator from leaking in."""
    seg = claim[:m.start()]
    cut = max(seg.rfind(';'), seg.rfind(','), seg.rfind('.'))
    clause = seg[cut + 1:] if cut >= 0 else seg
    return bool(_NEG_CERT.search(clause))


# ---------------------------------------------------------------- per-claim A-checks
def acheck_claim(claim, claim_type, gate_label):
    """Return (gating_flags, advisory_flags) for one already-segmented claim.
    Deterministic. No store, no model, no network."""
    gating, advisory = [], []
    has_num = bool(_NUM.search(claim))
    is_abstain = (claim_type == 'abstain') or bool(v.ABSTAIN.search(claim))
    ungrounded = (gate_label == 'PASS-COMMON')   # no locator/date/org signal from gate()

    # A1 NUMBER_NO_SOURCE -- empirical-result number with no source signal (Q2-safe).
    empirical_number = has_num and (bool(v.PROVEN.search(claim)) or bool(_EMP_PCT.search(claim)))
    if empirical_number and ungrounded and not is_abstain:
        gating.append('A1_NUMBER_NO_SOURCE')

    # A2 OVERCONFIDENT_UNGROUNDED -- exempt when (a) proof is attributed to a NAMED source, or
    # (b) every certainty marker present is under negation (calibrated honesty, not overclaim).
    attributed_proof = bool(_PROOF_VERB.search(claim) and _ATTRIB_SRC.search(claim))
    overconf_live = any(not _neg_before(claim, m) for m in _OVERCONF.finditer(claim))
    if overconf_live and ungrounded and not is_abstain and not attributed_proof:
        gating.append('A2_OVERCONFIDENT_UNGROUNDED')

    # A3 VAGUE_QUANT_NO_NUMBER
    if (not has_num) and _VAGUE.search(claim) and _EMP_NOUN.search(claim) and not is_abstain:
        gating.append('A3_VAGUE_QUANT_NO_NUMBER')

    # A4 EMPTY_HEDGE -- stacked hedges, short low-content span
    hedges = set(m.group(0).lower() for m in _HEDGE.finditer(claim))
    if len(hedges) >= 2 and len(_content_words(claim)) <= 16:
        gating.append('A4_EMPTY_HEDGE')

    # A5 UNFALSIFIABLE_UNIVERSAL (advisory)
    if _UNIVERSAL.search(claim) and not has_num and not is_abstain:
        advisory.append('A5_UNFALSIFIABLE_UNIVERSAL')

    return gating, advisory


# ---------------------------------------------------------------- item-level pass
def selfcheck(text):
    """Segment own output -> per-claim A-checks -> item verdict.
    Returns {verdict, n_claims, claims:[{span,type,gate,signals,gating,advisory}], a6}.
    verdict = FLAGGED iff any gating flag fired; else CLEAN. Advisory never changes verdict."""
    claims, seen = [], set()
    subj_polarity = defaultdict(set)   # for A6 cross-claim contradiction (advisory)
    for s in v.segment(text):
        if v.is_qa_scaffold(s):
            continue
        n = v._norm(s)
        if n in seen:
            continue
        seen.add(n)
        ctype, _ok = v.classify(s)
        glabel, sig = v.gate(s)
        gating, advisory = acheck_claim(s, ctype, glabel)
        subj_polarity[_subject_key(s)].add(bool(_NEG.search(s)))
        claims.append({'span': s[:140], 'type': ctype, 'gate': glabel, 'signals': sig,
                       'gating': gating, 'advisory': advisory})

    # A6 INTERNAL_CONTRADICTION (advisory): same subject seen both asserted and negated.
    a6 = sorted(k for k, pol in subj_polarity.items() if k and len(pol) > 1)
    any_gating = any(c['gating'] for c in claims)
    return {'verdict': 'FLAGGED' if any_gating else 'CLEAN',
            'n_claims': len(claims), 'claims': claims,
            'a6_contradiction_subjects': a6}


# ---------------------------------------------------------------- selftest (no network/store)
def _selftest():
    POS = {  # each MUST trip >= 1 gating flag (F-a anti-VOID)
        'P1_num_no_source':  "About 73% of people recover within a week.",
        'P2_overconfident':  "This treatment is definitively proven to always work.",
        'P3_vague_quant':    "Many studies have shown substantial benefits.",
        'P4_empty_hedge':    "It might perhaps possibly be somewhat relevant in some cases.",
    }
    NEG = {  # each MUST trip ZERO gating flags (F-b anti-over-prune)
        'N1_grounded_num':   "In 2019 a Nature study (doi:10.1038/s41586-019-1234-5) reported a 42% reduction (n=320).",
        'N2_calibrated':     "The evidence indicates a modest effect, though the sample was small.",
        'N3_common_const':   "Water boils at 100 degrees Celsius at sea level.",
        'N4_common_fact':    "A triangle has 3 sides.",
        'N5_clean_attrib':   "Smith et al. (2021), published in the Journal of Medicine, found a clear association.",
    }
    fails = []
    print("=== POSITIVES (must FLAG) ===")
    for k, t in POS.items():
        r = selfcheck(t)
        fired = [f for c in r['claims'] for f in c['gating']]
        ok = r['verdict'] == 'FLAGGED'
        print(f"  {k:18s} verdict={r['verdict']:8s} fired={fired}")
        if not ok: fails.append(f"F-a VOID: {k} did not flag")
    print("=== NEGATIVES (must be CLEAN) ===")
    for k, t in NEG.items():
        r = selfcheck(t)
        fired = [f for c in r['claims'] for f in c['gating']]
        ok = r['verdict'] == 'CLEAN'
        print(f"  {k:18s} verdict={r['verdict']:8s} fired={fired}")
        if not ok: fails.append(f"F-b OVER-PRUNE: {k} wrongly flagged {fired}")
    print()
    if fails:
        for f in fails: print("FAIL:", f)
        print("\nSELFTEST: FAIL"); sys.exit(2)
    print("SELFTEST: PASS (detector not blind, clean output not corrupted; harness != VOID)")


# ---------------------------------------------------------------- check one file
def _check(path):
    text = open(path, encoding='utf-8').read()
    r = selfcheck(text)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    print("VERDICT:", r['verdict'])


# ---------------------------------------------------------------- eval (Founder-labeled set)
def _eval(path):
    """Item-level detect-rate + false-flag-rate over a Founder-labeled set.
    Each line: {"id":..,"text":..,"label":"dirty"|"clean"}. dirty = should FLAG, clean = should pass.
    Bars are PRE-REGISTERED in SPEC_selfcheck_A.md (frozen before this is run on real data, R7).
    This harness computes the rates; it does NOT define the verdict bars here (no oracle leak)."""
    items = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    dirty = [it for it in items if it['label'] == 'dirty']
    clean = [it for it in items if it['label'] == 'clean']
    if not dirty or not clean:
        print("CONTENTS VOID -- need >=1 dirty and >=1 clean item"); sys.exit(2)
    det = sum(selfcheck(it['text'])['verdict'] == 'FLAGGED' for it in dirty) / len(dirty)
    ff  = sum(selfcheck(it['text'])['verdict'] == 'FLAGGED' for it in clean) / len(clean)
    print(f"detect_rate     = {det:.3f}  ({len(dirty)} dirty)")
    print(f"false_flag_rate = {ff:.3f}  ({len(clean)} clean)   [C1 HARD bar -- see SPEC]")
    print("note: PASS/FAIL read from frozen SPEC_selfcheck_A.md bars, not from this script.")


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--selftest':
        _selftest()
    elif len(sys.argv) >= 3 and sys.argv[1] == '--check':
        _check(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == '--eval':
        _eval(sys.argv[2])
    else:
        print("usage: verify_E16_A.py --selftest")
        print("       verify_E16_A.py --check <output.txt>")
        print("       verify_E16_A.py --eval <labeled_A.jsonl>")
