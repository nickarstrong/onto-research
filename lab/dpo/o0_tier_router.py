"""
o0_tier_router.py — Phase 7: Knowledge Tiering Router
======================================================
Post-verdict consumer. Reads verdict + value-features, routes to tier store.

INVARIANT (firewall):
  - NEVER writes back into the verify path.
  - NEVER calls verify().
  - Tier-store feeds the PROPOSER only (o0_retrieve reads curated view).

VALUE PREDICATE (STRATEGY sec 3):
  REJECT (DIRTY)        -> permanent   ALWAYS  (caught fabricate = evidence)
  weakness_relevant     -> permanent           (feeds SELECT via self_model) [STUB v1]
  novel, !relevant      -> temporary           (TTL -> tombstone on expiry)
  !novel, !relevant     -> discard             (tombstone, reversible)

GOLD-queue: exists structurally; 0 autonomous writes in v1 (T4 = GOLD-freeze).

Verdict is NOT a value-feature (axis orthogonality). The crossover rule
(REJECT -> keep) is hardcoded, not scored — it IS the proof of orthogonality.

Home: C:\\Projects\\onto-research\\lab\\dpo\\o0_tier_router.py
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

# ── tiers ──────────────────────────────────────────────────────────
TIER_GOLD_QUEUE = "gold-queue"   # propose-only, Founder-gated, frozen v1
TIER_PERMANENT  = "permanent"    # confirmed + relevant (lives in curated view)
TIER_TEMPORARY  = "temporary"    # TTL-based; tombstone on expiry
TIER_DISCARD    = "discard"      # tombstone, reversible

LIVE_TIERS = (TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD)  # T5 checks these


# ── value features ─────────────────────────────────────────────────

def compute_value_features(
    record: dict[str, Any],
    self_model: dict[str, Any],
    existing_absorb: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute value-features for a verdict record.

    Features: novelty (bool), weakness_relevance (bool), evidential_use (bool).
    Verdict enters ONLY via evidential_use (crossover rule) — axis orthogonality.

    Args:
        record: single verdict record from o0_verdicts.jsonl
        self_model: parsed self_model.json (weakness cards)
        existing_absorb: list of all ABSORB records already in memory
    Returns:
        dict with novelty, weakness_relevance, evidential_use, matched_weakness
    """
    novelty = _is_novel(record, existing_absorb)
    weak_rel, matched_w = _is_weakness_relevant(record, self_model)
    evidential = record.get("verdict") == "REJECT"

    return {
        "novelty": novelty,
        "weakness_relevance": weak_rel,
        "evidential_use": evidential,
        "matched_weakness": matched_w,  # for audit; None if !relevant
    }


def _is_novel(record: dict, existing: list[dict]) -> bool:
    """A record is novel if no existing ABSORB has the same topic.

    v1 heuristic: exact normalised topic match.
    Claim text is too long for exact comparison; topic is the right grain.
    Refinement (substring / embedding) deferred to rung C.
    """
    rt = _normalise(record.get("topic", ""))
    for ex in existing:
        if _normalise(ex.get("topic", "")) == rt:
            return False
    return True


def _is_weakness_relevant(
    record: dict, self_model: dict
) -> tuple[bool, str | None]:
    """Check if a record is relevant to any weakness card.

    rung C delta-3: the controller stamps the SELECTed disposition onto every
    written record (record['targeted_weakness']) via the sanctioned sealed-write
    path (option (a) of the former v1 stub). A record is weakness-relevant iff
    that stamp names a known weakness card.

    VERDICT-BLIND: reads only targeted_weakness + self_model names, never the
    verdict. Orthogonality preserved (the stamp comes from SELECT, which runs
    BEFORE verify). Records that predate the stamp (sealed 220) carry no field
    -> (False, None) -> routing on the sealed substrate is unchanged (no
    regression). No content classifier, no GOLD.
    """
    tw = record.get("targeted_weakness")
    if not tw:
        return False, None
    known = {w.get("name") for w in self_model.get("weaknesses", [])}
    if tw in known:
        return True, tw
    return False, None


def _normalise(text: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    return " ".join(text.lower().split())


# ── routing ────────────────────────────────────────────────────────

def route(record: dict[str, Any], vf: dict[str, Any]) -> str:
    """Route a verdict record to a tier using the value predicate.

    Args:
        record: verdict record (used for crossover rule only)
        vf: value-features dict from compute_value_features()
    Returns:
        tier string (one of TIER_* constants)
    """
    # Crossover rule: REJECT always kept (evidential use).
    # This is the axis-orthogonality proof: DIRTY -> keep.
    if vf["evidential_use"]:
        return TIER_PERMANENT

    # Weakness-relevant -> permanent (feeds SELECT via self_model).
    if vf["weakness_relevance"]:
        return TIER_PERMANENT

    # Novel but not relevant -> temporary (TTL).
    if vf["novelty"]:
        return TIER_TEMPORARY

    # Not novel, not relevant -> discard.
    return TIER_DISCARD

    # GOLD-queue: no autonomous routing in v1 (T4 = 0 writes).
    # Founder-manual promotion only.


# ── batch routing (for dry-val / gate tests) ───────────────────────

def route_batch(
    records: list[dict],
    self_model: dict,
    *,
    exclude_id: str | None = None,
) -> list[dict]:
    """Route a batch of verdict records.  Returns enriched records with tier + vf.

    For each record, existing_absorb = all OTHER records in the batch with
    verdict==ABSORB (leave-one-out: the record itself is excluded from its own
    novelty check, and optionally exclude_id skips a specific record).
    """
    absorb_pool = [r for r in records if r.get("verdict") == "ABSORB"]
    results = []
    for rec in records:
        # leave-one-out: exclude self from novelty pool
        pool = [r for r in absorb_pool if r is not rec]
        if exclude_id and rec.get("id") == exclude_id:
            continue
        vf = compute_value_features(rec, self_model, pool)
        tier = route(rec, vf)
        results.append({
            **rec,
            "_tier": tier,
            "_value_features": vf,
        })
    return results


# ── CLI (diagnostic) ───────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Phase 7 tier router (diagnostic)")
    ap.add_argument("--verdicts", default="eval/o0/o0_verdicts.jsonl")
    ap.add_argument("--self-model", default="self_model.json")
    args = ap.parse_args()

    verdicts = [json.loads(l) for l in Path(args.verdicts).read_text(encoding="utf-8").splitlines() if l.strip()]
    sm = json.loads(Path(args.self_model).read_text(encoding="utf-8"))

    routed = route_batch(verdicts, sm)
    counts = {}
    for r in routed:
        t = r["_tier"]
        counts[t] = counts.get(t, 0) + 1
    print(f"Routed {len(routed)} records:")
    for t in (TIER_PERMANENT, TIER_TEMPORARY, TIER_DISCARD, TIER_GOLD_QUEUE):
        print(f"  {t}: {counts.get(t, 0)}")
