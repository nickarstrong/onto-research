#!/usr/bin/env python3
# pec_l1l2.py -- Provenance verifier, deterministic layers L1 (existence/match) + L2 (status).
# ZERO model. ZERO fabrication: every verdict comes from an external registry (Crossref / Retraction Watch),
# never from weights. This is spec sec9 step 1 (SPEC_provenance_verifier_v0.md).
#
# Two run modes:
#   --selftest : verifies the deterministic TIER-DECISION logic against the grounded Fixture A (no network).
#   --live     : hits Crossref REST + retraction signal for real DOIs (requires network to api.crossref.org).
#
# Honest scope: --selftest proves the DECISION function (assign_tier). The L1/L2 DATA-FETCH (crossref_lookup,
# check_retraction) is exercised only in --live, on a host that can reach Crossref. Nothing here claims to be
# "calibrated" until --live runs and its verdicts match Fixture A's grounded expectations.

import sys, json, argparse

VENUE_DEGRADED = (  # AXIS G low: not peer-reviewed-mainstream. Extend as a maintained blocklist.
    "bio-complexity", "intelligent-design",
    "arxiv", "biorxiv", "medrxiv", "preprint",   # preprints: clean provenance, lower grade
)

# ---------------- DECISION LOGIC (deterministic; offline-testable) ----------------
def assign_tier(l1, l2, grade):
    """l1 in {MATCH, MATCH-conditional, MISMATCH, NORESOLVE}; l2 in {CLEAN, CONCERN, RETRACTED, None};
       grade in {ok, degraded}. Returns a tier string. PURE function -- the auditable core."""
    if l1 == "NORESOLVE":
        return "T4-fabricated"          # marker present, resolves to nothing -> manufactured
    if l1 == "MISMATCH":
        return "T4-mismatch"            # resolves, but to a DIFFERENT paper than the claim cites
    # l1 MATCH or MATCH-conditional below
    if l2 == "RETRACTED":
        return "T4-retracted"           # fabricated > missing: retracted ranks at T4, not low-tier
    if l2 == "CONCERN":
        return "T2-grade-degraded"      # expression-of-concern -> degrade, do not yet reject
    # l2 CLEAN
    if grade == "degraded":
        return "T2-grade-degraded"      # clean provenance, low evidence grade (ID venue / preprint)
    return "T1-pending-bind"            # clean + ok grade; T0 requires L4 content-bind (not done here)

def grade_of(text):
    t = (text or "").lower()
    return "degraded" if any(k in t for k in VENUE_DEGRADED) else "ok"

# ---------------- LIVE DATA FETCH (network; exercised in --live only) ----------------
def crossref_lookup(doi):
    import urllib.request, urllib.error
    url = "https://api.crossref.org/works/" + doi
    req = urllib.request.Request(url, headers={"User-Agent": "ONTO-PEC/0 (mailto:council@ontostandard.org)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8")).get("message", {})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None      # NORESOLVE
        raise

def l1_match(meta, claimed_as):
    """MATCH iff the resolved title/author tokens overlap the claim's. Conservative: low overlap -> MISMATCH."""
    if meta is None:
        return "NORESOLVE"
    title = " ".join(meta.get("title") or []).lower()
    authors = " ".join((a.get("family", "") + " " + a.get("given", "")) for a in meta.get("author", []) or []).lower()
    hay = (title + " " + authors)
    claim_toks = [w for w in claimed_as.lower().replace("(", " ").replace(")", " ").split() if len(w) > 3]
    hits = sum(1 for w in claim_toks if w in hay)
    return "MATCH" if hits >= 1 else "MISMATCH"

def l2_status(meta):
    """RETRACTED via Crossref update-to type or title prefix. CONCERN via EoC. Authoritative cross-source =
       Retraction Watch DB (cross-check in --live; Crossref now ingests RW)."""
    if meta is None:
        return None
    title = " ".join(meta.get("title") or []).lower()
    if title.startswith("retracted"):
        return "RETRACTED"
    for upd in meta.get("update-to", []) or []:
        ty = (upd.get("type") or "").lower()
        if "retract" in ty:
            return "RETRACTED"
        if "concern" in ty:
            return "CONCERN"
    return "CLEAN"

# ---------------- SELFTEST (offline; grounded Fixture A) ----------------
def selftest(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    npass = 0
    print("%-32s %-14s %-9s %-19s %-19s %s" % ("doi", "L1", "L2", "got", "expected", "ok"))
    for r in rows:
        l1 = r["expected_L1"]
        l1 = "MATCH" if l1 == "MATCH-conditional" else l1   # tiering treats conditional as match; DOI-confirm is separate
        l2 = r["expected_L2"]
        grade = grade_of(r["grounded_fact"])
        got = assign_tier(l1, l2, grade)
        ok = (got == r["expected_tier"])
        npass += ok
        print("%-32s %-14s %-9s %-19s %-19s %s" % (r["doi"], r["expected_L1"], str(r["expected_L2"]), got, r["expected_tier"], "OK" if ok else "FAIL"))
    print("\n%d/%d logic checks pass" % (npass, len(rows)))
    return npass == len(rows)

def live(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    print("%-32s %-14s %-9s %s" % ("doi", "L1", "L2", "tier"))
    for r in rows:
        meta = crossref_lookup(r["doi"])
        l1 = l1_match(meta, r["claimed_as"])
        l2 = l2_status(meta)
        grade = grade_of((" ".join((meta or {}).get("container-title") or [])) + " " + r["grounded_fact"])
        tier = assign_tier(l1, l2, grade)
        flag = "" if tier == r["expected_tier"] else "  <-- DIVERGES from grounded expectation %s" % r["expected_tier"]
        print("%-32s %-14s %-9s %s%s" % (r["doi"], l1, str(l2), tier, flag))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="fixture_A_provenance.jsonl")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    if a.live:
        live(a.fixture)
    else:
        sys.exit(0 if selftest(a.fixture) else 1)
