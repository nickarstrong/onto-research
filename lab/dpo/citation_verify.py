"""
citation_verify.py -- Q2 citation-existence verifier (Step-6 apparatus, G1).

Sits BESIDE temporal-verify in the verify path. Temporal-verify catches
ungroundable numbers/years; it is blind to a fabricated *identifier* (a DOI that
is syntactically valid but does not exist). This module closes that gap.

FIREWALL INVARIANT (R11 / pack sec 3.2):
    The existence oracle is an EXTERNAL REGISTRY ONLY (Crossref / doi.org).
    GOLD and episodic memory MUST NEVER be passed as the oracle. verify() and
    the knowledge store share no fields -- circular self-confirmation is an
    architectural prohibition, not a guideline.

THREE-STATE, false-DIRTY-free by construction:
    oracle says EXISTS      -> CLEAN       (registry confirms the DOI resolves)
    oracle says ABSENT      -> DIRTY       (registry definitively has no such DOI)
    oracle says UNRESOLVED  -> UNVERIFIED  (oracle unreachable/ambiguous; NOT a flag)
    malformed identifier    -> UNVERIFIED  (not a resolution result; never DIRTY)

DIRTY is emitted ONLY on a positive "absent" answer from the registry. A
network/timeout/5xx failure can never produce DIRTY. This keeps the
false-positive rate at zero by design (G1 constraint: resolution-failure ->
UNVERIFIED, not a false flag).
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Protocol

# Verdict vocabulary -- must match the verify path (gate step6_apparatus_v1).
CLEAN = "CLEAN"
DIRTY = "DIRTY"
UNVERIFIED = "UNVERIFIED"

# Syntactic DOI shape (ISO 26324 / Crossref handle): 10.<registrant>/<suffix>.
_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


class Existence(Enum):
    EXISTS = "EXISTS"          # registry positively confirms resolution
    ABSENT = "ABSENT"          # registry positively confirms non-existence (e.g. 404)
    UNRESOLVED = "UNRESOLVED"  # could not be determined (network/timeout/5xx/ambiguous)


class RegistryOracle(Protocol):
    """External-registry existence check. The ONLY permitted oracle kind."""
    def exists(self, doi: str) -> Existence: ...


def is_well_formed(doi: str) -> bool:
    return bool(_DOI_RE.match(doi.strip())) if isinstance(doi, str) else False


def verify_citation(doi: str, oracle: RegistryOracle) -> str:
    """
    Map a DOI + external-registry answer to a verify-path verdict.
    Returns one of CLEAN | DIRTY | UNVERIFIED. Pure function of (doi, oracle);
    no GOLD/episodic state is read here.
    """
    if not is_well_formed(doi):
        # A malformed identifier is not a registry "absent" result. Do NOT flag.
        return UNVERIFIED

    answer = oracle.exists(doi.strip())
    if answer is Existence.EXISTS:
        return CLEAN
    if answer is Existence.ABSENT:
        return DIRTY
    return UNVERIFIED  # Existence.UNRESOLVED


# --------------------------------------------------------------------------- #
# Oracles                                                                      #
# --------------------------------------------------------------------------- #

class FrozenOracle:
    """
    Offline-deterministic oracle for the G1 unit test (frozen allowlist).
    real -> EXISTS, fake -> ABSENT, everything else -> UNRESOLVED.
    Encodes the "cannot tell" default so unknown-but-possibly-real DOIs are
    never falsely flagged DIRTY -- the property G1 must protect.
    """
    def __init__(self, real: set[str], fake: set[str]) -> None:
        overlap = real & fake
        if overlap:
            raise ValueError(f"allowlist/denylist overlap: {overlap}")
        self._real = set(real)
        self._fake = set(fake)

    def exists(self, doi: str) -> Existence:
        if doi in self._real:
            return Existence.EXISTS
        if doi in self._fake:
            return Existence.ABSENT
        return Existence.UNRESOLVED


class CrossrefOracle:
    """
    Production oracle (NOT used in the G1 deterministic test). External registry.
    GET https://api.crossref.org/works/{doi}
        200 -> EXISTS | 404 -> ABSENT | anything else / network error -> UNRESOLVED.
    Kept import-light so the G1 unit test runs with zero network and zero deps.
    """
    BASE = "https://api.crossref.org/works/"

    def __init__(self, timeout: float = 5.0, mailto: str | None = None) -> None:
        self.timeout = timeout
        self.mailto = mailto

    def exists(self, doi: str) -> Existence:
        import urllib.error
        import urllib.request
        url = self.BASE + urllib.request.quote(doi, safe="")
        if self.mailto:
            url += f"?mailto={self.mailto}"
        try:
            req = urllib.request.Request(url, method="GET",
                                         headers={"User-Agent": "onto-citation-verify/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return Existence.EXISTS if resp.status == 200 else Existence.UNRESOLVED
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return Existence.ABSENT
            return Existence.UNRESOLVED
        except Exception:
            return Existence.UNRESOLVED
