#!/usr/bin/env python3
"""gold_retrieve.py - GOLD retrieval for the tier-spoof harness (E15/E16).

STUB fixture loader (not the real GOLD Core). Loads a small hard-coded GOLD slice
from a LOCAL, gitignored fixture and exposes:

    GOLD_retrieve(claim) -> [hit, ...]            # candidate hits, may be empty
    is_authorized(hit, manifest_files) -> bool    # sec-2 predicate component

A hit record is {source, locator, hash}. hash is computed at load by sha256 over
the source string (genuine, tamper-evident). manifest_files (the Genesis-Hash
analog) is the AUTHORIZATION set: a hit counts only if hash(hit.source) in it.

Retrieval is SEMANTIC (E16, semantic_retrieve.py) - embedding cosine over
claim_key+source, conservative similarity floor (a false hit HIDES a fabrication).
Authorization is NOT decided by retrieval; the manifest hash-gate below is the
only authorization predicate and is unchanged from E15.
"""
import hashlib
import json
import os
import re

import semantic_retrieve as _sem  # E16 semantic backend

# Fixture lives LOCAL-ONLY (eval/_local). Path resolved relative to this file's
# expected on-disk home: lab/dpo/  with fixture at lab/dpo/eval/_local/ .
_DEFAULT_FIXTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "eval", "_local", "gold_fixture.json"
)


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _normalize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class GoldStore:
    def __init__(self, fixture_path: str = None):
        path = fixture_path or _DEFAULT_FIXTURE
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"GOLD fixture missing at {path}. It is LOCAL-ONLY (eval/_local, "
                f"gitignored); pull it locally - it is never carried in git or a pack."
            )
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.manifest_files = set(data["manifest_files"])
        self.records = []
        for r in data["records"]:
            self.records.append({
                "claim_key": r["claim_key"],
                "source": r["source"],
                "locator": r.get("locator", ""),
                "hash": _sha256(r["source"]),          # genuine, computed at load
                "key_tokens": _normalize(r["claim_key"]),
            })

    def retrieve(self, claim: str):
        """Return candidate hits by SEMANTIC cosine against claim_key+source. May be empty.

        E16: token-overlap stub replaced by embedding retrieval (semantic_retrieve.py).
        The similarity floor is conservative (precision over recall) because a false
        hit would HIDE a fabrication, not cause one. Retrieval returns candidates only;
        authorization is decided solely by is_authorized() (manifest hash-gate, unchanged).
        Floor/top_k locked by instrument-sanity (semantic_retrieve.FLOOR/TOP_K).
        """
        return _sem.retrieve(claim, self.records)

    def is_authorized(self, hit: dict) -> bool:
        """sec-2 predicate: hash in manifest.files AND locator != ''."""
        return hit.get("hash") in self.manifest_files and bool(hit.get("locator"))


# module-level convenience (lazy singleton)
_store = None


def _get_store():
    global _store
    if _store is None:
        _store = GoldStore()
    return _store


def GOLD_retrieve(claim: str):
    return _get_store().retrieve(claim)


def is_authorized(hit: dict, manifest_files=None) -> bool:
    store = _get_store()
    if manifest_files is None:
        return store.is_authorized(hit)
    return hit.get("hash") in set(manifest_files) and bool(hit.get("locator"))


if __name__ == "__main__":
    s = GoldStore()
    print("manifest_files (authorized hashes):", len(s.manifest_files))
    for probe in [
        "spaced repetition improves long-term retention",   # authorized hit
        "vitamin C megadose prevents common cold",           # retrievable, hash-fail
        "the Great Wall is visible from the Moon",           # known miss
    ]:
        hits = s.retrieve(probe)
        auth = [s.is_authorized(h) for h in hits]
        print(f"  {probe!r:55s} hits={len(hits)} authorized={auth}")
