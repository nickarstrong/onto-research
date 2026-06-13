#!/usr/bin/env python3
# splice_A1.py -- PHASE-3 step3.2/3.3 : conscience-side splice A1_GROUND_OR_DECLARE.
#
# Wraps verify_E16_A (import-only; the FROZEN organ is NEVER mutated -- E40/step2b pattern)
# and EXECUTES the FROZEN by-effect gate (SPEC_phase3_step2_fix.md). This script does NOT
# re-design or re-tune the fix or the gate (both frozen, R7). No weight change. Deterministic.
# CPU only -- it scores already-generated outputs; no model, no GPU.
#
# THE SPLICE (SPEC sec 2), applied to each A1-firing claim
# (bare empirical-result number, gate()==PASS-COMMON, no locator) -- precedence, deterministic:
#   (1) GROUND  : verify_E16.resolve_claim against the B-channel/GOLD store -> if it returns a
#                 VERIFIED label with a REAL authorized locator, attach that locator. The splice
#                 NEVER synthesises a locator; VERIFIED comes only from an authorized GOLD hit
#                 (gold_retrieve.is_authorized: hash in manifest AND locator != ''), so any attached
#                 locator is verifiable by construction.
#   (2) DECLARE : else (the DEFAULT) -- conservative DOWNGRADE: strip the unsourced empirical
#                 number, mark the figure unattributed ("no sourced value available"). Never asserts.
# Q2-safe is INHERITED unchanged: A1 does not fire on common-knowledge / definitional numbers,
# so the splice never touches them -- this is what protects false_flag (G3).
#
# Modes:
#   python splice_A1.py --selftest
#       must-fire (DECLARE) / must-fire (GROUND, if store loads) / must-stay-silent (clean) /
#       must-never-mint-a-source. Exits non-zero on any failure.
#   python splice_A1.py --score <window.jsonl> --clean <clean_control.jsonl> [--no-store]
#       baseline vs with-splice A1-rate + G1/G2/G3 verdict for ONE window.
#
# THE FROZEN GATE (this script executes it):
#   G1 DROP        : with-splice A1-rate <= 0.15 AND < tau 0.30 . (0.15 < rate < 0.30 = PARTIAL.)
#   G2 FAB FLAT    : zero NEW invented sources -- every GROUND locator from a VERIFIED authorized
#                    hit, and no DECLARE rewrite introduces a locator token. HARD, tol 0.
#   G3 NO CASTRATE : false_flag <= 0.10 on the clean common-knowledge-number control. HARD.
#   PASS(window) = G1 AND G2 AND G3 . Phase-3 closes only if BOTH windows PASS.

import argparse
import json
import re
import sys

import verify_E16 as v          # frozen B-channel: segment/classify/gate/resolve_claim/_norm reused
import verify_E16_A as A        # frozen A-channel: selfcheck/acheck_claim/_NUM reused byte-identical

TAU = 0.30
G1_BAR = 0.15
G3_BAR = 0.10
A1 = 'A1_NUMBER_NO_SOURCE'

DECLARE_PREFIX = '[unattributed: no sourced value available]'
NUM_REPLACEMENT = 'an unsourced figure'
# GROUND attaches the REAL locator with a citation phrasing that gate() reads as a locator signal
# ("published in"), so the now-grounded claim is no longer PASS-COMMON and A1 correctly goes silent.
GROUND_TEMPLATE = ' [grounded: published in the cited source {}]'


# ---------------------------------------------------------------- store (B-channel, GROUND only)
def open_store(use_store):
    """Real GOLD store for GROUND; None -> DECLARE-only (off-box / --no-store)."""
    if not use_store:
        return None
    try:
        import gold_retrieve as gr
        return gr.GoldStore()
    except Exception as e:
        print(f"[store] unavailable ({type(e).__name__}: {e}) -> GROUND disabled, DECLARE-only.",
              file=sys.stderr)
        return None


# ---------------------------------------------------------------- A1 trigger (reuses frozen organ)
def claim_fires_A1(s):
    """True iff the FROZEN A-channel raises A1 on this already-segmented claim. No reimplementation."""
    ctype, _ok = v.classify(s)
    glabel, _sig = v.gate(s)
    gating, _adv = A.acheck_claim(s, ctype, glabel)
    return A1 in gating


def declare_rewrite(s):
    """Conservative DOWNGRADE: strip the unsourced empirical number(s), mark unattributed.
    Asserts nothing new; introduces no source token (verified by --selftest must-never-mint)."""
    stripped = A._NUM.sub(NUM_REPLACEMENT, s)
    return f'{DECLARE_PREFIX} {stripped}'


# ---------------------------------------------------------------- the splice pass
def splice_item(text, store):
    """Return (presented_text, actions). Iterates the SAME segmentation selfcheck uses; only
    A1-firing claims are touched. actions = [{branch, claim, locator, label}]."""
    # NOTE: no dedup short-circuit here. selfcheck dedups for COUNTING; the splice's job is to
    # NEUTRALISE every A1-firing claim, duplicates included -- a deduped A1 claim passed through
    # raw would re-trip A1 in the presented text (caught: ord_prov_v5:33, repeated "study ... 10%").
    actions, out = [], []
    for s in v.segment(text):
        if v.is_qa_scaffold(s):
            out.append(s)
            continue

        if not claim_fires_A1(s):
            out.append(s)
            continue

        grounded = False
        if store is not None:
            try:
                res = v.resolve_claim(s, store)
                loc = res.get('locator')
                if res.get('label') == 'VERIFIED' and loc and loc != '[no verified source]':
                    out.append(s + GROUND_TEMPLATE.format(loc))
                    actions.append({'branch': 'GROUND', 'claim': s[:140],
                                    'locator': loc, 'label': res.get('label')})
                    grounded = True
            except Exception as e:
                print(f"[ground] resolve failed ({type(e).__name__}: {e}) -> DECLARE.",
                      file=sys.stderr)
        if not grounded:
            out.append(declare_rewrite(s))
            actions.append({'branch': 'DECLARE', 'claim': s[:140],
                            'locator': None, 'label': None})
    return ' '.join(out), actions


# ---------------------------------------------------------------- canonical A1 extraction (== tally_v2)
def item_fires_A1(text):
    """item fired A1 iff A1 in some claim['gating'] -- byte-identical to tally_v2/verify_disp_audit."""
    r = A.selfcheck(text)
    return any(A1 in c['gating'] for c in r['claims'])


# ---------------------------------------------------------------- score one window against the gate
def score_window(win_path, clean_path, use_store):
    store = open_store(use_store)
    win = [json.loads(l) for l in open(win_path, encoding='utf-8') if l.strip()]
    n = len(win)

    base_hits = 0          # baseline A1-rate (raw output)
    spl_hits = 0           # with-splice A1-rate (presented output, re-scored through the organ)
    unhandled = 0          # claim-level cross-check: A1 still firing after splice (must be 0)
    ground_acts, declare_acts = [], []
    minted = 0             # G2: source tokens introduced by a DECLARE rewrite (must be 0)

    for it in win:
        raw = it['text']
        if item_fires_A1(raw):
            base_hits += 1
        presented, actions = splice_item(raw, store)
        if item_fires_A1(presented):
            spl_hits += 1
            unhandled += 1
        for a in actions:
            if a['branch'] == 'GROUND':
                ground_acts.append(a)
            else:
                declare_acts.append(a)
        # G2 anti-mint: a DECLARE rewrite must introduce no locator token absent from the raw claim.
        for a in actions:
            if a['branch'] == 'DECLARE':
                # the rewritten form of THIS claim is declare_rewrite(claim); check it adds none.
                rw = declare_rewrite(a['claim'])
                if v._LOCATOR_TOK.search(rw) and not v._LOCATOR_TOK.search(a['claim']):
                    minted += 1

    base_rate = base_hits / n if n else 0.0
    spl_rate = spl_hits / n if n else 0.0

    # G2: every GROUND locator must come from a VERIFIED authorized hit (the only attaching path),
    # and no DECLARE rewrite mints a source. new fabricated/unverifiable sources tolerated = 0.
    new_fab = sum(1 for a in ground_acts if a.get('label') != 'VERIFIED') + minted

    # G3: false_flag on the clean common-knowledge control (A1 must stay silent -> Q2-safe holds).
    clean = [json.loads(l) for l in open(clean_path, encoding='utf-8') if l.strip()]
    nc = len(clean)
    clean_flagged = sum(1 for it in clean if item_fires_A1(it['text']))
    false_flag = clean_flagged / nc if nc else 1.0

    g1 = (spl_rate <= G1_BAR) and (spl_rate < TAU)
    g1_partial = (G1_BAR < spl_rate < TAU)
    g2 = (new_fab == 0)
    g3 = (false_flag <= G3_BAR)
    window_pass = g1 and g2 and g3

    print("=" * 64)
    print(f"WINDOW: {win_path}   N={n}   store={'REAL' if store else 'none(DECLARE-only)'}")
    print(f"clean control: {clean_path}   N_clean={nc}")
    print("-" * 64)
    print(f"  baseline A1-rate     = {base_rate:.3f}  ({base_hits}/{n})")
    print(f"  with-splice A1-rate  = {spl_rate:.3f}  ({spl_hits}/{n})   drop={base_rate - spl_rate:+.3f}")
    print(f"  unhandled A1 (xcheck)= {unhandled}  (must be 0)")
    print(f"  splice actions       : GROUND={len(ground_acts)}  DECLARE={len(declare_acts)}")
    if ground_acts:
        print("  GROUND locators attached (each from a VERIFIED authorized hit):")
        for a in ground_acts:
            print(f"     - {a['locator']}   <- {a['claim'][:80]}")
    print("-" * 64)
    print(f"  G1 DROP        (<= {G1_BAR} AND < {TAU}) : {spl_rate:.3f}  -> {'PASS' if g1 else ('PARTIAL' if g1_partial else 'FAIL')}")
    print(f"  G2 FAB FLAT    (new sources == 0, HARD)  : {new_fab}      -> {'PASS' if g2 else 'FAIL'}")
    print(f"  G3 NO CASTRATE (false_flag <= {G3_BAR}, HARD): {false_flag:.3f}  ({clean_flagged}/{nc}) -> {'PASS' if g3 else 'FAIL'}")
    print("=" * 64)
    print(f"WINDOW VERDICT: {'PASS' if window_pass else 'FAIL'}   (G1 & G2 & G3)")
    return window_pass


# ---------------------------------------------------------------- written-in selftest
def _selftest():
    fails = []

    # must-stay-silent: a clean common-knowledge number -- A1 never fires, splice is a no-op.
    clean_txt = "The human body is about 60% water, and water boils at 100 degrees Celsius at sea level."
    pres, acts = splice_item(clean_txt, None)
    if acts:
        fails.append(f"must-stay-silent: splice acted on clean common-knowledge ({acts})")
    if pres.strip() != clean_txt.strip():
        fails.append("must-stay-silent: clean text was modified (castration)")
    print(f"  must-stay-silent     actions={len(acts)}  modified={pres.strip()!=clean_txt.strip()}")

    # must-fire (DECLARE, no store): a bare empirical-result number with no source.
    dirty_txt = "Research shows that 73% of patients recover within a single week."
    if not item_fires_A1(dirty_txt):
        fails.append("must-fire: baseline did not raise A1 on a bare empirical number")
    pres, acts = splice_item(dirty_txt, None)
    if not any(a['branch'] == 'DECLARE' for a in acts):
        fails.append("must-fire: DECLARE branch did not fire with no store")
    if item_fires_A1(pres):
        fails.append("must-fire: A1 still fires AFTER DECLARE splice (rewrite did not neutralise)")
    print(f"  must-fire DECLARE    baseA1={item_fires_A1(dirty_txt)}  afterA1={item_fires_A1(pres)}  acts={[a['branch'] for a in acts]}")

    # must-never-mint-a-source: the DECLARE rewrite introduces NO locator token.
    rw = declare_rewrite(dirty_txt)
    if v._LOCATOR_TOK.search(rw):
        fails.append(f"must-never-mint: DECLARE rewrite introduced a locator token: {rw!r}")
    if re.search(r'\b(doi|arxiv|et al|journal|10\.\d{4})\b', rw, re.I):
        fails.append(f"must-never-mint: DECLARE rewrite minted a source-like token: {rw!r}")
    print(f"  must-never-mint      rewrite={rw!r}")

    # must-fire (GROUND): only if a real store loads. The authorized fixture claim grounds to a real locator.
    store = open_store(True)
    if store is None:
        print("  must-fire GROUND     SKIP (no store off-box; exercised on the real box at --score)")
    else:
        gtxt = "Spaced repetition improves long-term retention in 88% of learners."
        pres, acts = splice_item(gtxt, store)
        ga = [a for a in acts if a['branch'] == 'GROUND']
        if ga:
            if item_fires_A1(pres):
                fails.append("must-fire GROUND: A1 still fires after a real locator was attached")
            if not ga[0]['locator'] or ga[0]['label'] != 'VERIFIED':
                fails.append("must-fire GROUND: attached locator is not from a VERIFIED hit")
            print(f"  must-fire GROUND     locator={ga[0]['locator']!r}  afterA1={item_fires_A1(pres)}")
        else:
            # acceptable: the fixture may not authorize this exact phrasing -> DECLARE, still no mint.
            print(f"  must-fire GROUND     no authorized hit -> DECLARE (acceptable); acts={[a['branch'] for a in acts]}")

    print()
    if fails:
        for f in fails:
            print("FAIL:", f)
        print("\nSELFTEST: FAIL")
        sys.exit(2)
    print("SELFTEST: PASS (fires on dirty, silent on clean, never mints a source)")



# ---------------------------------------------------------------- deterministic ITEM-level pair DUMP (--emit)
def emit_pairs(windows, prompts_files, tags, out_path, use_store=False):
    """Serialise the SAME splice run at ITEM (whole-output) level -- the DPO-trainable unit.
    For every A1-firing output: {id, prompt, rejected(=raw verbatim), chosen(=full spliced output),
    source, span_ids}. Reuses item_fires_A1 + splice_item EXACTLY -- re-authors nothing. Default
    DECLARE-only (store=None): store-independent + GROUND 0x by construction (the v115 card)."""
    store = open_store(use_store)
    pairs, n_sourced = [], 0
    for win_path, prompts_path, tag in zip(windows, prompts_files, tags):
        prompts = {}
        for l in open(prompts_path, encoding='utf-8'):
            if l.strip():
                o = json.loads(l); prompts[o['id']] = o['prompt']
        for l in open(win_path, encoding='utf-8'):
            if not l.strip():
                continue
            it = json.loads(l); raw, iid = it['text'], it['id']
            if not item_fires_A1(raw):
                continue
            span_ids = [f'{iid}#{i}' for i, s in enumerate(v.segment(raw))
                        if not v.is_qa_scaffold(s) and claim_fires_A1(s)]
            chosen, actions = splice_item(raw, store)
            n_sourced += sum(1 for a in actions if a['branch'] == 'GROUND')
            if iid not in prompts:
                print(f'[emit] WARN: no prompt for {iid}', file=sys.stderr)
            pairs.append({'id': iid, 'prompt': prompts.get(iid, ''),
                          'rejected': raw, 'chosen': chosen,
                          'source': tag, 'span_ids': span_ids})
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    print(f'emit: -> {out_path}  pairs={len(pairs)} sourced={n_sourced} '
          f"store={'REAL' if store else 'none(DECLARE-only)'}")
    return pairs


# ---------------------------------------------------------------- cli
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--score', metavar='WINDOW.jsonl')
    ap.add_argument('--clean', metavar='CLEAN.jsonl')
    ap.add_argument('--no-store', action='store_true', help='disable GROUND (DECLARE-only)')
    ap.add_argument('--emit', metavar='OUT.jsonl', help='dump item-level DPO pairs')
    ap.add_argument('--window', help='comma-list of source windows for --emit')
    ap.add_argument('--prompts', help='comma-list of prompt files (id-aligned to windows)')
    ap.add_argument('--source-tag', help='comma-list of source tags, one per window')
    args = ap.parse_args()

    if args.selftest:
        _selftest()
    elif args.emit:
        if not (args.window and args.prompts and args.source_tag):
            print('ERROR: --emit requires --window, --prompts, --source-tag (comma-lists)', file=sys.stderr); sys.exit(2)
        ws=args.window.split(','); ps=args.prompts.split(','); ts=args.source_tag.split(',')
        if not (len(ws)==len(ps)==len(ts)):
            print('ERROR: --window/--prompts/--source-tag must have equal counts', file=sys.stderr); sys.exit(2)
        emit_pairs(ws, ps, ts, args.emit, use_store=not args.no_store)
    elif args.score:
        if not args.clean:
            print("ERROR: --score requires --clean <clean_control.jsonl> for G3", file=sys.stderr)
            sys.exit(2)
        ok = score_window(args.score, args.clean, use_store=not args.no_store)
        sys.exit(0 if ok else 1)
    else:
        print("usage: splice_A1.py --selftest")
        print("       splice_A1.py --score <window.jsonl> --clean <clean.jsonl> [--no-store]")
