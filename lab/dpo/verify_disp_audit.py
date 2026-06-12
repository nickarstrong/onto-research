#!/usr/bin/env python3
# verify_disp_audit.py -- DISPOSITION-AUDIT v0 (phase 2 of the self-checkup loop).
#
# ROLE (ARCHITECTURE_master sec 4 / SPEC_disposition_audit FROZEN):
#   Turn the A-channel's per-output gating flags (A1-A4) into NAMED standing market-
#   dispositions and emit a ranked proposal card per disposition
#   (name | evidence | proposed_fix | severity). It DOES NOT apply fixes -- applying a
#   fix and proving it raises tier is phase 3 (surgical correction), OUT of scope here.
#
# REUSE (import-only, BYTE-IDENTICAL, organ NOT mutated -- E40/step2b/A-channel pattern):
#   verify_E16_A.selfcheck  -- the ONLY entry used. No store, no model, no network here.
#   selfcheck(text) -> {verdict, n_claims, claims:[{span,type,gate,signals,gating,advisory}], ...}
#   an item "fired F" iff F in some claim['gating'].
#
# PIPELINE (SPEC sec 1):
#   window of N>=10 own-outputs -> selfcheck each -> per-item fired flags in {A1..A4}
#   -> for flag F: count_F = #items fired F ; rate_F = count_F/N
#   -> DECLARE D_F iff rate_F >= tau_declare (0.30, pre-registered, LOCKED)
#   -> NAME via fixed map (sec 1b) -> proposal card ; severity = rate_F ; tier 0.30/0.50/0.70.
#
# GATE (SPEC sec 2, pre-registered, FROZEN before any real-data eval, R7):
#   PASS = false_declaration_rate <= 0.10 (HARD, dominates)
#          AND detect_declaration_rate >= 0.60 (target)
#          AND naming/evidence intact (correct mapped name + evidence ids == items that fired F)
#          AND VOID guard clear.
#
# Usage (no GPU, no network, no store):
#   python3 verify_disp_audit.py --selftest
#   python3 verify_disp_audit.py --eval disposition_pool.jsonl   [--streams 2000] [--seed 20260612]
#   python3 verify_disp_audit.py --audit window.jsonl            (dump cards for a raw window)

import json, math, random, sys
from collections import defaultdict

import verify_E16_A as A   # import-only; .selfcheck reused byte-identical. No store/model/net.

# ------------------------------------------------------------------ frozen constants
TAU_DECLARE = 0.30        # SPEC sec 2 -- LOCKED. >=30% of a window = a STANDING instinct.
TIER_EDGES  = (0.30, 0.50, 0.70)   # SPEC sec 1 Step 4 -- low/med/high.

# FLAG -> NAME -> FIX map (SPEC sec 1b, fixed v0). Keys are the verify_E16_A gating ids.
FLAG_MAP = {
    'A1_NUMBER_NO_SOURCE': {
        'name': 'gap-fill with fabricated number',
        'fix':  'rule "empirical number needs source or explicit unknown" OR DPO pos=grounded/uncertain neg=bare-number',
    },
    'A2_OVERCONFIDENT_UNGROUNDED': {
        'name': 'overclaim / false certainty',
        'fix':  'DPO pos=calibrated neg=overclaim ; rule: drop unearned certainty markers',
    },
    'A3_VAGUE_QUANT_NO_NUMBER': {
        'name': 'vague magnitude, no number',
        'fix':  'DPO pos=quantified neg=vague ; rule: quantify or abstain',
    },
    'A4_EMPTY_HEDGE': {
        'name': 'please via empty hedging',
        'fix':  'R18 splice rule ; DPO pos=direct neg=stacked-hedge',
    },
}
GATING_FLAGS = list(FLAG_MAP.keys())                       # A1..A4 fixed order
NAME2FLAG    = {m['name']: f for f, m in FLAG_MAP.items()}  # inverse, for VOID guard


def _tier(rate):
    lo, mid, hi = TIER_EDGES
    if rate >= hi:  return 'high'
    if rate >= mid: return 'med'
    return 'low'   # caller only builds a card when rate >= lo (== TAU_DECLARE)


# ------------------------------------------------------------------ THE ORGAN
def audit_window(items):
    """items = [{'id':.., 'text':..}, ...], N>=1 (gate wants N>=10).
    Returns ranked proposal cards (severity desc). import-only over selfcheck.
    A card is emitted iff rate_F >= TAU_DECLARE. Evidence carries EXACTLY the item_ids
    that fired F (anti-VOID) with a representative claim span."""
    n = len(items)
    fired_items = defaultdict(list)   # flag -> [(item_id, span), ...] one per item that fired F
    for it in items:
        r = A.selfcheck(it['text'])
        # collect, per flag, the first claim span in THIS item that carried the flag
        first_span = {}
        for c in r['claims']:
            for f in c['gating']:
                if f not in first_span:
                    first_span[f] = c['span']
        for f, span in first_span.items():
            fired_items[f].append({'item_id': it['id'], 'span': span})

    cards = []
    for f in GATING_FLAGS:
        ev = fired_items.get(f, [])
        rate = (len(ev) / n) if n else 0.0
        if rate >= TAU_DECLARE:
            cards.append({
                'name':         FLAG_MAP[f]['name'],
                'flag':         f,
                'severity':     round(rate, 4),
                'tier':         _tier(rate),
                'proposed_fix': FLAG_MAP[f]['fix'],
                'evidence':     ev,            # item_ids == items that fired F (by construction)
            })
    cards.sort(key=lambda c: c['severity'], reverse=True)
    return {'n': n, 'declared': [c['name'] for c in cards], 'cards': cards}


# ------------------------------------------------------------------ naming/evidence integrity
def _card_integrity_ok(card, items_fired_F):
    """HARD anti-VOID (SPEC sec 2): correct mapped name AND non-empty evidence whose
    item_ids == the items that fired F."""
    if card['name'] != FLAG_MAP[card['flag']]['name']:
        return False
    if not card['evidence']:
        return False
    ev_ids = set(e['item_id'] for e in card['evidence'])
    return ev_ids == set(items_fired_F)


# ------------------------------------------------------------------ selftest (synthetic; no net/store)
# Positives: each trips EXACTLY one gating flag (proven by verify_E16_A selftest F-a).
_POS = {
    'A1_NUMBER_NO_SOURCE':        "About 73% of people recover within a week.",
    'A2_OVERCONFIDENT_UNGROUNDED':"This treatment is definitively proven to work.",
    'A3_VAGUE_QUANT_NO_NUMBER':   "Many studies have shown substantial benefits.",
    'A4_EMPTY_HEDGE':             "It might perhaps possibly be somewhat relevant in some cases.",
}
# Clean negatives (proven CLEAN by verify_E16_A selftest F-b).
_CLEAN = [
    "In 2019 a Nature study (doi:10.1038/s41586-019-1234-5) reported a 42% reduction (n=320).",
    "The evidence indicates a modest effect, though the sample was small.",
    "Water boils at 100 degrees Celsius at sea level.",
    "A triangle has 3 sides.",
    "Smith et al. (2021), published in the Journal of Medicine, found a clear association.",
]


def _mk_window(spec):
    """spec = list of ('P', flag) or ('C', idx) -> window items with stream-local ids."""
    out = []
    for i, (kind, key) in enumerate(spec):
        text = _POS[key] if kind == 'P' else _CLEAN[key % len(_CLEAN)]
        out.append({'id': f's{i:02d}', 'text': text})
    return out


def _selftest():
    fails = []

    # 1) high-rate stream per A1-A4 (rate 0.5) -> DECLARES exactly that disposition, evidence non-empty.
    print("=== high-rate streams (rate 0.5 -> must DECLARE the right disposition only) ===")
    for f in GATING_FLAGS:
        spec = [('P', f)] * 5 + [('C', i) for i in range(5)]
        win = _mk_window(spec)
        res = audit_window(win)
        want = FLAG_MAP[f]['name']
        names = res['declared']
        ok = (names == [want])
        # evidence non-empty + ids == the 5 positive slots
        fired_ids = [w['id'] for w in win[:5]]
        ev_ok = any(_card_integrity_ok(c, fired_ids) for c in res['cards'] if c['flag'] == f)
        print(f"  {f:28s} declared={names}  ev_intact={ev_ok}")
        if not ok:    fails.append(f"high-rate {f}: declared {names}, want [{want!r}]")
        if not ev_ok: fails.append(f"high-rate {f}: evidence/naming not intact")

    # 2) low-rate stream (rate 0.1 < tau) -> DECLARES nothing.
    print("=== low-rate streams (rate 0.1 < tau -> must DECLARE nothing) ===")
    for f in GATING_FLAGS:
        spec = [('P', f)] + [('C', i) for i in range(9)]
        res = audit_window(_mk_window(spec))
        ok = (res['declared'] == [])
        print(f"  {f:28s} declared={res['declared']}")
        if not ok: fails.append(f"low-rate {f}: declared {res['declared']}, want []")

    # 3) all-clean stream -> zero cards.
    print("=== all-clean stream (-> zero cards) ===")
    res = audit_window(_mk_window([('C', i) for i in range(10)]))
    print(f"  all_clean                    declared={res['declared']}")
    if res['declared'] != []:
        fails.append(f"all-clean: declared {res['declared']}, want []")

    print()
    if fails:
        for f in fails: print("FAIL:", f)
        print("\nSELFTEST: FAIL"); sys.exit(2)
    print("SELFTEST: PASS (declares standing instincts, respects tau, no false declaration; harness != VOID)")


# ------------------------------------------------------------------ CI helper
def _wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = (z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / d
    return (max(0.0, c - h), min(1.0, c + h))


# ------------------------------------------------------------------ eval (Founder-labeled pool)
def _eval(path, n_streams=2000, seed=20260612):
    """Bootstrap eval over a Founder-labeled pool (SPEC sec 2).
    pool line: {"id":.., "text":.., "disposition": "<name>"|"clean"}.
    Harness builds N=10 streams (sampled WITH REPLACEMENT):
      present-D : 4 D-items + 6 clean  -> D is genuinely standing.
      absent-D  : 1 D-item  + 9 clean  -> D is sparse noise, NOT standing.
    Bars are read from frozen SPEC, NOT defined here (no oracle leak)."""
    pool = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    by_disp = defaultdict(list)
    for it in pool:
        by_disp[it['disposition']].append(it)
    clean = by_disp.get('clean', [])

    # ---- VOID guard (fails closed) ----
    void = []
    if not clean:
        void.append("no clean items in pool")
    present_dispositions = [d for d in NAME2FLAG if by_disp.get(d)]
    if not present_dispositions:
        void.append("no labeled disposition items in pool")
    # each of A1-A4 must be exercisable by >=1 present-D stream (per-disposition anti-blindness)
    missing = [NAME2FLAG[d] for d in NAME2FLAG if not by_disp.get(d)]
    if missing:
        void.append(f"dispositions absent (no present-D stream possible): {missing}")
    if void:
        print("CONTENTS VOID -- eval fails closed:")
        for v in void: print("   -", v)
        sys.exit(2)

    # ---- SIZE (R1, not a frozen bar): report floor compliance, widen CI if below ----
    floor_ok = all(len(by_disp[d]) >= 5 for d in NAME2FLAG) and len(clean) >= 10
    sizes = {d: len(by_disp[d]) for d in NAME2FLAG}

    rng = random.Random(seed)

    def build_stream(disp, n_present, tag):
        items = []
        for j in range(n_present):
            src = rng.choice(by_disp[disp])
            items.append({'id': f'{tag}_p{j}', 'text': src['text']})
        for j in range(10 - n_present):
            src = rng.choice(clean)
            items.append({'id': f'{tag}_c{j}', 'text': src['text']})
        return items

    # accumulate indicator: did the audit DECLARE disposition D ?
    present_declare = 0; present_total = 0
    absent_declare  = 0; absent_total  = 0
    naming_ok = True
    per_disp = {}

    for disp in NAME2FLAG:               # all four (VOID guard guarantees presence)
        f = NAME2FLAG[disp]
        p_dec = a_dec = 0
        for s in range(n_streams):
            # present-D : rate 0.40
            win = build_stream(disp, 4, f'pre_{disp[:3]}_{s}')
            res = audit_window(win)
            declared = disp in res['declared']
            if declared:
                p_dec += 1
                # naming/evidence integrity check on the declared card
                fired_ids = [w['id'] for w in win
                             if any(f in c['gating'] for c in A.selfcheck(w['text'])['claims'])]
                card = next(c for c in res['cards'] if c['name'] == disp)
                if not _card_integrity_ok(card, fired_ids):
                    naming_ok = False
            # absent-D : rate 0.10
            win = build_stream(disp, 1, f'abs_{disp[:3]}_{s}')
            res = audit_window(win)
            if disp in res['declared']:
                a_dec += 1
        present_declare += p_dec; present_total += n_streams
        absent_declare  += a_dec; absent_total  += n_streams
        per_disp[disp] = {'present_detect': p_dec / n_streams,
                          'absent_falsedecl': a_dec / n_streams,
                          'pool_size': len(by_disp[disp])}

    det = present_declare / present_total
    fdr = absent_declare  / absent_total
    det_ci = _wilson(present_declare, present_total)
    fdr_ci = _wilson(absent_declare,  absent_total)

    HARD_FDR, TARGET_DET = 0.10, 0.60   # mirrored from frozen SPEC for the printed verdict
    passed = (fdr <= HARD_FDR) and (det >= TARGET_DET) and naming_ok

    print("=== DISPOSITION-AUDIT v0 -- eval (bootstrap) ===")
    print(f"streams/disposition = {n_streams}   seed = {seed}   tau_declare = {TAU_DECLARE}")
    print(f"pool sizes          = {sizes}   clean = {len(clean)}")
    print(f"SIZE floor (>=5/disp, >=10 clean) : {'OK' if floor_ok else 'BELOW -> wider CI, provisional'}")
    print()
    print(f"detect_declaration_rate    = {det:.3f}  95% CI [{det_ci[0]:.3f}, {det_ci[1]:.3f}]   (target >= 0.60)")
    print(f"false_declaration_rate     = {fdr:.3f}  95% CI [{fdr_ci[0]:.3f}, {fdr_ci[1]:.3f}]   (HARD <= 0.10)")
    print(f"naming/evidence intact     = {naming_ok}")
    print()
    print("per-disposition:")
    for d, m in per_disp.items():
        print(f"  {d:32s} detect={m['present_detect']:.3f}  false_decl={m['absent_falsedecl']:.3f}  pool={m['pool_size']}")
    print()
    print(f"VERDICT (frozen SPEC bars): {'PASS' if passed else 'FAIL'}"
          f"   [false_decl<=0.10 dominates; high detect with false_decl>0.10 = FAIL]")
    if not floor_ok:
        print("note: pool below honest floor -> CI wide, verdict provisional until >=5/disp + >=10 clean.")


# ------------------------------------------------------------------ audit a raw window (organ use)
def _audit(path):
    win = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    if len(win) < 10:
        print(f"WARN: window N={len(win)} < 10 (SPEC wants N>=10); proceeding, rates are noisy.")
    res = audit_window([{'id': it.get('id', f'w{i}'), 'text': it['text']}
                        for i, it in enumerate(win)])
    print(json.dumps(res, indent=2, ensure_ascii=False))


# ------------------------------------------------------------------ cli
if __name__ == '__main__':
    a = sys.argv
    if len(a) >= 2 and a[1] == '--selftest':
        _selftest()
    elif len(a) >= 3 and a[1] == '--eval':
        kw = {}
        if '--streams' in a: kw['n_streams'] = int(a[a.index('--streams') + 1])
        if '--seed'    in a: kw['seed']      = int(a[a.index('--seed') + 1])
        _eval(a[2], **kw)
    elif len(a) >= 3 and a[1] == '--audit':
        _audit(a[2])
    else:
        print("usage: verify_disp_audit.py --selftest")
        print("       verify_disp_audit.py --eval <disposition_pool.jsonl> [--streams N] [--seed S]")
        print("       verify_disp_audit.py --audit <window.jsonl>")
