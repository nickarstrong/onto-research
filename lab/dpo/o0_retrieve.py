#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
o0_retrieve.py -- Step 6 retrieval adapter (PROPOSER-feed ONLY). [v280: +pool-hygiene quarantine]

Pulls CONFIRMED episodic memory for retrieval-conditioned GENERATE.
Reconciled against REAL disk (o0_verdicts.jsonl, v229):
  - CONFIRMED-only filter  = record['verdict'] == 'ABSORB'   (131/260 on disk)
  - topic match            = token-overlap on record['topic'] (string)
  - returned fact          = record['claim']  (+ best_abstract when present)

FIREWALL (CONCEPT_step6 sec 2): this module feeds the PROPOSER context only.
It is NEVER imported by any verify_* path. The verifier's proof-source stays the
EXTERNAL oracle. Keep this import out of verify code. (Asserted in step6_dryval.)

Retrieval method = keyword/token-overlap (CONCEPT sec 6 cheapest-honest for n<=8,
ROADMAP sec 0b). all-MiniLM embeddings are available but unnecessary at probe scale.
"""
import json, re
from pathlib import Path

ABSORB = "ABSORB"           # CONFIRMED label on disk (NOT "CONFIRM")
_WORD = re.compile(r"[a-z0-9]+")


def _toks(s):
    return set(_WORD.findall((s or "").lower()))


def load_confirmed(path):
    """All CONFIRMED (ABSORB) records. Returns list of dicts (claim/topic/best_abstract)."""
    out = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if r.get("verdict") != ABSORB:        # CONFIRMED-only filter (hard)
            continue
        # v280 POOL HYGIENE: quarantine both-channels-empty ABSORB rows from the PROPOSER feed.
        # No confirmed specific in EITHER gate channel (_materialised = non-year, _materialised_year
        # = year) => no-injection seed, must not condition GENERATE. ABSTAIN/REJECT already dropped
        # above. Missing flag => False (conservative quarantine; surfaces as fewer loaded -> verify).
        if not (r.get("_materialised", False) or r.get("_materialised_year", False)):
            continue
        out.append({
            "id": r.get("id"),
            "topic": r.get("topic", ""),
            "claim": r.get("claim", ""),
            "best_abstract": r.get("best_abstract", "") or "",
        })
    return out


def retrieve(goal_topic, confirmed, k=3):
    """Top-k CONFIRMED records by token-overlap on topic. Deterministic.

    Returns [] when nothing overlaps (honest empty -> proposer gets no episodic
    facts for that topic; that is correct, not an error)."""
    g = _toks(goal_topic)
    if not g:
        return []
    scored = []
    for r in confirmed:
        ov = len(g & _toks(r["topic"]))
        if ov > 0:
            scored.append((ov, r["id"], r))          # id = deterministic tiebreak
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [r for _, _, r in scored[:k]]


def snippet_audit(records):
    """FIX-OWED watch (pack v229 sec6): flag retrieved CONFIRMs whose snippet was
    dropped -> a NOVEL conditioned CONFIRM built on a dropped snippet is un-auditable."""
    dropped = [r["id"] for r in records if not r["best_abstract"].strip()]
    return {"n": len(records), "snippet_dropped": dropped}
