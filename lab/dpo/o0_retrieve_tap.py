#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
o0_retrieve_tap.py -- v282 prereg TAP around o0_retrieve.retrieve (PROPOSER-feed audit).

Purpose: the generator (generate_step6) firewall emits ONLY {topic, claim}; retrieved
ids never enter the proposal stream (generate_step6 L76/L89). So the prereg bar
"0 retrieval over the 97 quarantined ids" is UNFALSIFIABLE from proposals alone.

This tap wraps retrieve_fn and writes every returned record id to a LOCAL audit jsonl
(one line per (topic, returned_ids)). It does NOT alter the records handed to the
generator -> firewall intact (audit file is a side-channel, never merged into `out`).

Usage in the runner (proposer side only -- NEVER import on verify path):
    import o0_retrieve as R
    from o0_retrieve_tap import tapped_retrieve
    confirmed = R.load_confirmed(verdicts_path)          # ABSORB-only, pool-hygiene filtered
    retrieve_fn = tapped_retrieve(R.retrieve, "eval/o0/v282_retrieve_audit.jsonl")
    # pass retrieve_fn into generate_step6.generate(..., retrieve_fn=retrieve_fn, ...)
"""
import json
from pathlib import Path


def tapped_retrieve(inner_retrieve, audit_path):
    """Return a retrieve_fn(goal_topic, confirmed, k) that logs returned ids.

    inner_retrieve = o0_retrieve.retrieve (unchanged behaviour).
    audit_path     = LOCAL jsonl; each call appends {"topic", "ids"} (ids may be []).
    """
    p = Path(audit_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    def _retrieve(goal_topic, confirmed, k=3):
        recs = inner_retrieve(goal_topic, confirmed, k=k)
        ids = [r.get("id") for r in recs]
        with p.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"topic": goal_topic, "ids": ids}) + "\n")
        return recs                      # records UNCHANGED -> firewall intact

    return _retrieve
