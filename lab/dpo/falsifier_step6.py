#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
falsifier_step6.py -- pre-registered A/B falsifier (CONCEPT_step6 sec 4).

Two arms, SAME fixed weakness W (fabricated-specifics), shared substrate / Crown /
oracle / topic-seed sequence. ONLY difference = proposer context (blind vs conditioned).
K=8/arm (<=10, LOCAL probe, protocol sec 3.7).

REUSES the controller's injected verify adapter (external oracle) UNCHANGED -- the
harness never re-implements or modifies the proof path. Verify sees only {"topic","claim"}.

Metrics per arm:
  rate_f  = caught fabrications / K            (DIRTY verdicts ; what the PROPOSER proposes)
  fa_live = DIRTY that reached knowledge / K   (must be 0.000 BOTH arms ; what ABSORBS)
GUARD1 novelty = fraction of conditioned candidates NOT near-dup of retrieved set.
GUARD2 inertness = read from controller run state (>=2 cards, >=2 distinct selected,
  cooldown fired >=1x). Supplied by caller from the live controller; harness adjudicates.

Verdict logic (pre-registered, exact):
  fa_live!=0 (either arm)              -> FAIL
  drop>=BAR and novelty>=NOV and G2 ok -> PASS
  drop>=BAR and novelty<NOV            -> COSMETIC
  drop< BAR                            -> NULL
"""
import re

BAR = 0.25        # rate_f(blind) - rate_f(cond) >= 0.25  (>= 2/8)
NOV = 0.75        # >= 6/8 novel
_WORD = re.compile(r"[a-z0-9]+")


def _toks(s):
    return set(_WORD.findall((s or "").lower()))


def _near_dup(claim, retrieved_set, jaccard=0.6):
    c = _toks(claim)
    if not c:
        return False
    for r in retrieved_set:
        rt = _toks(r)
        if not rt:
            continue
        j = len(c & rt) / len(c | rt)
        if j >= jaccard:
            return True
    return False


def run_arm(generate, verify, k, retrieved_by_topic=None):
    """Generate K, verify each (external oracle), tally. retrieved_by_topic maps
    topic->[claim,...] of what was fed (for novelty); None for blind arm."""
    claims = generate(k)
    n_dirty = 0
    leaked = 0
    novel = 0
    rows = []
    for c in claims:
        # FIREWALL assert: verify input carries no retrieval/GOLD handle.
        assert set(c.keys()) == {"topic", "claim"}, f"FIREWALL: leak in verify input {set(c.keys())}"
        v, reasons = verify(c)
        dirty = (v == "DIRTY")
        n_dirty += int(dirty)
        # fa_live: a DIRTY claim must never be absorbed as knowledge.
        if dirty and reasons.get("_absorbed_knowledge"):
            leaked += 1
        if retrieved_by_topic is not None:
            fed = retrieved_by_topic.get(c["topic"], [])
            if not _near_dup(c["claim"], fed):
                novel += 1
        rows.append({"topic": c["topic"], "verdict": v, "dirty": dirty})
    n = len(claims)
    return {
        "k": n,
        "rate_f": (n_dirty / n) if n else 1.0,
        "fa_live": (leaked / n) if n else 0.0,
        "novelty": (novel / n) if (retrieved_by_topic is not None and n) else None,
        "rows": rows,
    }


def adjudicate(blind, cond, guard2_ok):
    drop = blind["rate_f"] - cond["rate_f"]
    fa_breach = (blind["fa_live"] != 0.0) or (cond["fa_live"] != 0.0)
    novelty = cond["novelty"]
    if fa_breach:
        verdict = "FAIL"
    elif drop < BAR:
        verdict = "NULL"
    elif novelty is not None and novelty < NOV:
        verdict = "COSMETIC"
    elif not guard2_ok:
        verdict = "NULL_INERT"   # primary met but loop did not rotate -> honest NO
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "rate_f_blind": round(blind["rate_f"], 3),
        "rate_f_cond": round(cond["rate_f"], 3),
        "drop": round(drop, 3),
        "bar": BAR,
        "fa_live_blind": blind["fa_live"],
        "fa_live_cond": cond["fa_live"],
        "novelty_cond": novelty,
        "novelty_bar": NOV,
        "guard2_rotation_ok": guard2_ok,
    }
