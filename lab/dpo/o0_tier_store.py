"""
o0_tier_store.py — Phase 7: Tier Store
=======================================
Persistence layer for knowledge tiering.

Responsibilities:
  - Track tier assignments for every routed record.
  - Tombstone mechanism (discard + TTL expiry) — reversible, auditable.
  - TTL countdown for temporary records.
  - GOLD-queue log (propose-only, Founder-gated).
  - Curated view: filtered JSONL for proposer (o0_retrieve reads this).

INVARIANT:
  - No hard-delete. Every removal = tombstone (reversible).
  - count(removed) == count(tombstones)  (T3 gate).
  - GOLD-queue: 0 autonomous writes (T4 gate).
  - Curated view = permanent + active-temporary only.

Home: C:\\Projects\\onto-research\\lab\\dpo\\o0_tier_store.py
"""

from __future__ import annotations
import json
import copy
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from o0_tier_router import (
    TIER_GOLD_QUEUE, TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD, LIVE_TIERS,
)

# ── defaults ───────────────────────────────────────────────────────
DEFAULT_TTL_CYCLES = 5          # temporary records expire after N cycles w/o retrieval
STORE_FILE         = "o0_tier_state.json"
CURATED_FILE       = "o0_verdicts_curated.jsonl"
GOLD_QUEUE_FILE    = "o0_gold_queue.jsonl"
TOMBSTONE_LOG      = "o0_tombstones.jsonl"


# ── tier state ─────────────────────────────────────────────────────

class TierStore:
    """In-memory tier state with JSON persistence.

    Schema (o0_tier_state.json):
    {
      "version": 1,
      "ttl_cycles": 5,
      "cycle_counter": 0,
      "records": {
        "<provoke_id>": {
          "tier": "permanent|temporary|discard",
          "routed_at": "ISO",
          "value_features": {...},
          "tombstone": false,
          "tombstone_at": null,
          "tombstone_reason": null,
          "last_retrieved_cycle": null,
          "ttl_remaining": null
        }
      }
    }
    """

    def __init__(self, store_path: str | Path = STORE_FILE, ttl_cycles: int = DEFAULT_TTL_CYCLES):
        self.path = Path(store_path)
        self.ttl_cycles = ttl_cycles
        self._state: dict[str, Any] = self._load()

    # ── persistence ────────────────────────────────────────────────

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {
            "version": 1,
            "ttl_cycles": self.ttl_cycles,
            "cycle_counter": 0,
            "records": {},
        }

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ── core ops ───────────────────────────────────────────────────

    def assign(
        self,
        provoke_id: str,
        tier: str,
        value_features: dict,
        *,
        record_snapshot: dict | None = None,
    ) -> None:
        """Assign a record to a tier.  Overwrites previous assignment (re-route)."""
        now = datetime.now(timezone.utc).isoformat()
        entry: dict[str, Any] = {
            "tier": tier,
            "routed_at": now,
            "value_features": value_features,
            "tombstone": False,
            "tombstone_at": None,
            "tombstone_reason": None,
            "last_retrieved_cycle": None,
            "ttl_remaining": self.ttl_cycles if tier == TIER_TEMPORARY else None,
        }
        if record_snapshot:
            entry["snapshot"] = record_snapshot  # for curated view rebuild
        self._state["records"][provoke_id] = entry

    def tombstone(self, provoke_id: str, reason: str) -> bool:
        """Mark a record as tombstoned. Returns True if newly tombstoned."""
        rec = self._state["records"].get(provoke_id)
        if not rec or rec["tombstone"]:
            return False
        rec["tombstone"] = True
        rec["tombstone_at"] = datetime.now(timezone.utc).isoformat()
        rec["tombstone_reason"] = reason
        return True

    def promote(self, provoke_id: str, new_tier: str) -> bool:
        """Re-promote a tombstoned record (reversibility proof for T3).

        Returns True if promoted successfully.
        """
        rec = self._state["records"].get(provoke_id)
        if not rec:
            return False
        rec["tombstone"] = False
        rec["tombstone_at"] = None
        rec["tombstone_reason"] = None
        rec["tier"] = new_tier
        rec["routed_at"] = datetime.now(timezone.utc).isoformat()
        if new_tier == TIER_TEMPORARY:
            rec["ttl_remaining"] = self.ttl_cycles
        else:
            rec["ttl_remaining"] = None
        return True

    def mark_retrieved(self, provoke_id: str, cycle: int) -> None:
        """Mark a temporary record as retrieved this cycle (resets TTL)."""
        rec = self._state["records"].get(provoke_id)
        if rec and rec["tier"] == TIER_TEMPORARY and not rec["tombstone"]:
            rec["last_retrieved_cycle"] = cycle
            rec["ttl_remaining"] = self.ttl_cycles

    def tick_cycle(self) -> list[str]:
        """Advance cycle counter.  Expire temporary records with TTL=0.

        Returns list of provoke_ids that were tombstoned this tick.
        """
        self._state["cycle_counter"] += 1
        expired = []
        for pid, rec in self._state["records"].items():
            if (
                rec["tier"] == TIER_TEMPORARY
                and not rec["tombstone"]
                and rec["ttl_remaining"] is not None
            ):
                rec["ttl_remaining"] -= 1
                if rec["ttl_remaining"] <= 0:
                    self.tombstone(pid, "ttl_expiry")
                    expired.append(pid)
        return expired

    # ── queries ────────────────────────────────────────────────────

    @property
    def cycle(self) -> int:
        return self._state["cycle_counter"]

    def active_records(self, tier: str | None = None) -> dict[str, dict]:
        """Return non-tombstoned records, optionally filtered by tier."""
        out = {}
        for pid, rec in self._state["records"].items():
            if rec["tombstone"]:
                continue
            if tier and rec["tier"] != tier:
                continue
            out[pid] = rec
        return out

    def tombstoned_records(self) -> dict[str, dict]:
        return {
            pid: rec
            for pid, rec in self._state["records"].items()
            if rec["tombstone"]
        }

    def all_records(self) -> dict[str, dict]:
        return dict(self._state["records"])

    # ── audit counters (for gate tests) ────────────────────────────

    def count_by_tier(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for rec in self._state["records"].values():
            key = rec["tier"] + ("/tomb" if rec["tombstone"] else "")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def count_tombstones(self) -> int:
        return sum(1 for r in self._state["records"].values() if r["tombstone"])

    def count_removals(self) -> int:
        """Removals = discard assignments + TTL expirations (both are tombstones)."""
        return self.count_tombstones()

    def gold_queue_count(self) -> int:
        """Autonomous GOLD writes.  Must be 0 in v1 (T4)."""
        return sum(
            1 for r in self._state["records"].values()
            if r["tier"] == TIER_GOLD_QUEUE and not r["tombstone"]
        )

    # ── curated view ───────────────────────────────────────────────

    def write_curated_view(
        self,
        source_verdicts_path: str | Path,
        output_path: str | Path = CURATED_FILE,
    ) -> int:
        """Write a curated JSONL containing only active permanent + temporary records.

        Reads full records from source_verdicts_path (o0_verdicts.jsonl),
        filters to records present in active tier store.
        Returns count of curated records written.

        This file is what o0_retrieve.py reads in the curated arm.
        """
        source = Path(source_verdicts_path)
        all_verdicts = {
            _extract_id(json.loads(line)): json.loads(line)
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

        active = self.active_records()
        curated = []
        for pid in active:
            if pid in all_verdicts:
                curated.append(all_verdicts[pid])

        out = Path(output_path)
        out.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in curated) + "\n",
            encoding="utf-8",
        )
        return len(curated)

    # ── tombstone log (append-only audit trail) ────────────────────

    def append_tombstone_log(
        self,
        provoke_id: str,
        reason: str,
        log_path: str | Path = TOMBSTONE_LOG,
    ) -> None:
        entry = {
            "provoke_id": provoke_id,
            "reason": reason,
            "cycle": self.cycle,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ── GOLD-queue (propose-only) ──────────────────────────────────

    def propose_gold(
        self,
        provoke_id: str,
        rationale: str,
        log_path: str | Path = GOLD_QUEUE_FILE,
    ) -> None:
        """Log a GOLD proposal.  Does NOT write to GOLD.  Founder reviews queue.

        This is NOT an autonomous write — it is a propose-only entry.
        T4 gate checks gold_queue_count() on the tier store, not this log.
        """
        entry = {
            "provoke_id": provoke_id,
            "rationale": rationale,
            "proposed_at": datetime.now(timezone.utc).isoformat(),
            "cycle": self.cycle,
            "status": "proposed",  # Founder sets "accepted" / "rejected"
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── helpers ────────────────────────────────────────────────────────

def _extract_id(record: dict) -> str:
    """Extract the canonical record ID."""
    return record.get("id", "")
