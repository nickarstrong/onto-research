#!/usr/bin/env python3
"""
o0_contact.py — organism-0 contact signals

Writes operator-facing events to contact_queue.jsonl (append-only).
Triggers (from CONCEPT_organism0_v1.md §5):
  PLATEAU        — 10 consecutive REJECT verdicts
  GEN_FAIL       — Ollama generation failure
  GATE_FAIL_LEARN — post-learning validation failed (rollback executed)

Channel = file signal, not handshake. Daemon continues on PLATEAU/GEN_FAIL,
STOPS on GATE_FAIL_LEARN (safety brake).
"""

import json
from datetime import datetime, timezone

CONTACT_PATH = "contact_queue.jsonl"

VALID_TRIGGERS = ("PLATEAU", "GEN_FAIL", "GATE_FAIL_LEARN")


def emit(trigger, cycle, detail, path=CONTACT_PATH):
    """Append one contact event to the queue file."""
    if trigger not in VALID_TRIGGERS:
        raise ValueError(f"Unknown trigger '{trigger}', must be one of {VALID_TRIGGERS}")

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trigger": trigger,
        "cycle": cycle,
        "detail": detail,
        "action_needed": "STOP" if trigger == "GATE_FAIL_LEARN" else "review",
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"  [CONTACT] {trigger} @ cycle {cycle}: {detail}")
    return event
