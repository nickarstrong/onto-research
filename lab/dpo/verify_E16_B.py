#!/usr/bin/env python3
# verify_E16_B.py -- B-CHANNEL band-A phase-1 eval harness (the grounded leg of self-checkup v0).
#
# DOCTRINE (ARCHITECTURE_master sec2/sec4 ; SPEC_selfcheck_A sec0 split):
#   A. SELF-CONSISTENCY  -- verify_E16_A.py (no source/corpus/net).
#   B. IS-IT-GROUNDED    -- THIS leg: verify_E16.resolve_claim (L1-L3) against the GOLD store.
# Phase-1 band-A gate (canon sec4) is BOTH channels: false_flag <= 0.10 AND detect >= 0.60 on a
# >=20+20 Founder-labeled held-out set. The A-channel --eval already exists (verify_E16_A._eval);
# the B-channel had no equivalent dirty/clean band-A harness on disk -- this builds it, mirroring
# A's --eval byte-for-byte in shape so the two channels are read against the SAME frozen bars.
#
# REUSE (import-only, organ NOT mutated -- E40/step2b/A-channel pattern):
#   verify_E16.segment / is_qa_scaffold / classify / _norm / resolve_claim
# The base verifier stays where it is; this harness only READS its per-claim resolve verdicts.
#
# ITEM VERDICT (mirrors verify_E16._eval_heldout per-item label collapse):
#   segment -> skip QA-scaffold -> dedup -> classify ; for each checkable claim call
#   resolve_claim(claim, store, claim_type) -> label in {VERIFIED, UNVERIFIABLE, PASS-COMMON}.
#   item = FLAGGED iff any claim resolved UNVERIFIABLE (== DEMOTE) ; else CLEAN
#          (no checkable claim, or all VERIFIED / PASS-COMMON).
#   This is the grounded analogue of the A-channel verdict: a provenance assertion with no
#   authorized GOLD source is the violation the B-channel exists to catch (C1 precision-first --
#   common-knowledge PASS-COMMON and genuinely grounded VERIFIED must pass untouched).
#
# LABELED SET (Founder-judged ground truth, R7 -- NEVER synthetic):
#   jsonl, one obj/line: {"id":.., "text":.., "label":"dirty"|"clean"}
#     dirty = Founder judges this output asserts provenance with NO real authorized GOLD source
#             (fabricated or true-but-uncovered) -> the verifier SHOULD demote (FLAG).
#     clean = grounded against the real GOLD store (-> VERIFIED) OR pure common-knowledge with no
#             provenance assertion (-> PASS-COMMON) -> the verifier should PASS.
#   NOTE for the author: a "clean/grounded" item only resolves VERIFIED if its claim actually hits
#   the REAL GOLD store and is hash-authorized; a grounded-looking claim NOT in GOLD will (correctly)
#   demote and count as a false_flag. Lean the clean class on common-knowledge + items truly in GOLD.
#
# FALSIFIERS exercised by --selftest (F-a/F-b, mirror SPEC_selfcheck_A sec3):
#   F-a : a deliberately ungrounded provenance assertion must DEMOTE (else detector blind = VOID).
#   F-b : a common-knowledge / genuinely grounded claim must stay CLEAN (else over-prune / castration).
#
# Usage (--selftest needs NO store/net ; --eval needs the real GOLD store on the box):
#   python3 verify_E16_B.py --selftest
#   python3 verify_E16_B.py --check some_output.txt          (uses real GOLD store)
#   python3 verify_E16_B.py --eval labeled_B.jsonl           (Founder set ; bars in canon/SPEC, frozen)

import json, sys

import verify_E16 as v   # import-only; segment/is_qa_scaffold/classify/_norm/resolve_claim reused


# ---------------------------------------------------------------- item-level pass
def bcheck(text, store):
    """Segment own output -> per-claim grounded resolve -> item verdict.
    Returns {verdict, n_claims, claims:[resolve_claim dicts]}.
    verdict = FLAGGED iff any claim resolved UNVERIFIABLE (== DEMOTE) ; else CLEAN."""
    claims, seen = [], set()
    for s in v.segment(text):
        if v.is_qa_scaffold(s):
            continue
        n = v._norm(s)
        if n in seen:
            continue
        seen.add(n)
        ctype, ok = v.classify(s)
        if ok:
            r = v.resolve_claim(s, store, ctype)
            r['span'] = s[:140]
            claims.append(r)
    labs = [c['label'] for c in claims]
    verdict = 'FLAGGED' if ('UNVERIFIABLE' in labs) else 'CLEAN'
    return {'verdict': verdict, 'n_claims': len(claims), 'claims': claims}


# ---------------------------------------------------------------- selftest (no store/net)
class _FakeStore:
    """Minimal duck-typed GoldStore for selftest only: one authorized passage.
    Mirrors GoldStore.retrieve(claim)->[hit] and is_authorized(hit)->bool.
    The real --eval uses gold_retrieve.GoldStore() (the genuine GOLD slice)."""
    _AUTH = {'source': 'GOLD: spaced repetition improves long-term retention (controlled study).',
             'locator': 'GOLD:sr-001', 'hash': 'authorized', 'authorized': True}

    def retrieve(self, claim):
        return [self._AUTH] if 'spaced repetition' in claim.lower() else []

    def is_authorized(self, hit):
        return bool(hit.get('authorized'))


def _selftest():
    store = _FakeStore()
    POS = {  # ungrounded provenance assertion -> MUST DEMOTE (F-a anti-VOID)
        'BP1_prose_no_src':  "Researchers found that this compound cured the disease in most patients.",
        'BP2_locator_no_hit':"According to a 2021 clinical trial (n=400), the drug cut mortality by 42%.",
    }
    NEG = {  # MUST stay CLEAN (F-b anti-over-prune)
        'BN1_grounded':      "Spaced repetition improves long-term retention, as a controlled study showed.",
        'BN2_common_const':  "Water boils at 100 degrees Celsius at sea level.",
        'BN3_abstain':       "There is no credible source for that specific figure.",
    }
    fails = []
    print("=== POSITIVES (must FLAG / DEMOTE) ===")
    for k, t in POS.items():
        r = bcheck(t, store)
        labs = [c['label'] for c in r['claims']]
        print(f"  {k:18s} verdict={r['verdict']:8s} labels={labs}")
        if r['verdict'] != 'FLAGGED':
            fails.append(f"F-a VOID: {k} did not demote")
    print("=== NEGATIVES (must be CLEAN) ===")
    for k, t in NEG.items():
        r = bcheck(t, store)
        labs = [c['label'] for c in r['claims']]
        print(f"  {k:18s} verdict={r['verdict']:8s} labels={labs}")
        if r['verdict'] != 'CLEAN':
            fails.append(f"F-b OVER-PRUNE: {k} wrongly flagged {labs}")
    print()
    if fails:
        for f in fails:
            print("FAIL:", f)
        print("\nSELFTEST: FAIL")
        sys.exit(2)
    print("SELFTEST: PASS (B-channel demotes ungrounded provenance, passes grounded/common; harness != VOID)")


# ---------------------------------------------------------------- check one file (real store)
def _check(path):
    import gold_retrieve as gr
    text = open(path, encoding='utf-8').read()
    r = bcheck(text, gr.GoldStore())
    print(json.dumps(r, indent=2, ensure_ascii=False))
    print("VERDICT:", r['verdict'])


# ---------------------------------------------------------------- eval (Founder-labeled set, real store)
def _eval(path):
    """Item-level detect-rate + false-flag-rate over a Founder-labeled set, mirroring
    verify_E16_A._eval. Each line: {"id":..,"text":..,"label":"dirty"|"clean"}.
    Bars are PRE-REGISTERED (ARCHITECTURE_master sec4 / SPEC; frozen before real data, R7):
    false_flag_rate <= 0.10 (HARD, C1) AND detect_rate >= 0.60 (TARGET, R1). This harness
    computes the rates only; PASS/FAIL is read from the frozen bars, not defined here (no oracle leak)."""
    import gold_retrieve as gr
    store = gr.GoldStore()
    items = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    dirty = [it for it in items if it['label'] == 'dirty']
    clean = [it for it in items if it['label'] == 'clean']
    if not dirty or not clean:
        print("CONTENTS VOID -- need >=1 dirty and >=1 clean item")
        sys.exit(2)
    det = sum(bcheck(it['text'], store)['verdict'] == 'FLAGGED' for it in dirty) / len(dirty)
    ff  = sum(bcheck(it['text'], store)['verdict'] == 'FLAGGED' for it in clean) / len(clean)
    print(f"detect_rate     = {det:.3f}  ({len(dirty)} dirty)")
    print(f"false_flag_rate = {ff:.3f}  ({len(clean)} clean)   [C1 HARD bar -- see canon/SPEC]")
    print("note: PASS/FAIL read from frozen canon sec4 bars (ff<=0.10 AND detect>=0.60), not from this script.")


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--selftest':
        _selftest()
    elif len(sys.argv) >= 3 and sys.argv[1] == '--check':
        _check(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == '--eval':
        _eval(sys.argv[2])
    else:
        print("usage: verify_E16_B.py --selftest")
        print("       verify_E16_B.py --check <output.txt>      (real GOLD store)")
        print("       verify_E16_B.py --eval <labeled_B.jsonl>  (Founder set ; bars frozen in canon/SPEC)")
