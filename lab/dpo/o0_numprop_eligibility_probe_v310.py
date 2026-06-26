#!/usr/bin/env python3
# o0_numprop_eligibility_probe_v310.py -- v311 plane, read-only eligibility floor-probe.
# AUTHORITY: sealed note reports/NUMPROP_coverage_v310.md section 3. NO design change here.
# PURPOSE: measure the ONE unmeasured number that gates PATH A vs PATH B --
#          the numprop-ELIGIBILITY floor of the held-out rows.
#
# eligibility(row) := row asserts a numeric MAGNITUDE about a BOUND entity, AND that magnitude
#                     class corresponds to >=1 EXISTING WD numeric property (quantity datatype),
#                     INDEPENDENT of whether p_domain_map_v308 currently maps it.
#
# Eligibility is DISTINCT from and UPSTREAM of:
#   - resolution floor  (v301, RED 0.000)  -> live WD bind. NOT done here.
#   - property floor     (v303, PASS 1.000) -> QID has the numeric P. NOT done here.
# Substituting either for eligibility = fabrication (R7). This probe measures eligibility ONLY.
#
# HERMETIC + READ-ONLY:
#   - NO network, NO GPU, NO WD fetch, NO cache, NO clock-dependence -> byte-identical cold runs.
#   - touches NO frozen substrate; imports nothing from the oracle/numprop/probe stack.
#   - number-detection + year-filter are a BYTE-EXACT mirror of o0_layer2_numprop (frozen seam
#     reproduced, not edited) so eligibility uses the same numeric surface the verdict uses.
#   - bound-entity is operationalized STRUCTURALLY (named-entity subject candidate, mirroring the
#     driver's _CAP_SUBJ fallback) -- NOT live WD resolution (that is v301, a different floor).
#
# R7 / R4 (no invented IDs): the ELIGIBLE basis is ONLY the dimension classes BYTE-PROVEN to have
#   a WD quantity property by the audited v308 map. Each proven class cites its confirming P-id
#   (read from p_domain_map_v308.json bytes, md5 335a59cb). No new/unverified P-id is asserted.
#   A magnitude in a class NOT proven here -> BARE-QUANTITY-NO-PROP, with the detected dimension
#   logged so any suppressed-but-real class is auditable (Void-as-measured).
#
# OUTPUT: counts {ELIGIBLE, BARE-QUANTITY-NO-PROP, NOT-NUMERIC} to stdout (= the floor) +
#   per-row-id label table to a KEEP-LOCAL jsonl (IDs + labels + reason ONLY; NO held-out content).
#
# Usage:
#   python o0_numprop_eligibility_probe_v310.py [heldout.jsonl] [labels_out.jsonl]
import json, re, sys

# ----------------------------------------------------------------------------
# (A) number-detection -- BYTE-EXACT mirror of o0_layer2_numprop (926d10a8)
# ----------------------------------------------------------------------------
_NUM_RE = re.compile(r"[\d,]+(?:\.\d+)?")


def extract_numbers(text):
    """Mirror of numprop.extract_numbers: all numeric values from text as floats."""
    out = []
    for m in _NUM_RE.findall(text or ""):
        try:
            out.append(float(m.replace(",", "")))
        except ValueError:
            continue
    return out


def magnitude_numbers(text):
    """numprop's year-filter (verdict step 4) applied: drop year-like integers 1400..2100."""
    nums = extract_numbers(text)
    return [n for n in nums if not (1400 <= n <= 2100 and n == int(n))]


# ----------------------------------------------------------------------------
# (B) bound-entity proxy -- mirror of driver _CAP_SUBJ (de7998ba) fallback.
#     Structural only: a capitalized proper-noun run = a bindable subject candidate.
#     This is NOT resolution (no WD). Stopword heads match the driver's own filter.
# ----------------------------------------------------------------------------
_CAP_SUBJ = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b")
_STOP_HEADS = ("The", "According", "In", "Its", "This", "That", "However")


def has_entity_subject(text):
    for m in _CAP_SUBJ.findall(text or ""):
        if m not in _STOP_HEADS:
            return True
    return False


# ----------------------------------------------------------------------------
# (C) dimension cues.
#     PROVEN classes: each is byte-confirmed to have >=1 WD quantity property by the audited
#     v308 map (md5 335a59cb). Confirming P-id cited per class. ELIGIBLE basis = these only.
#     UNPROVEN classes: detected + LOGGED but NOT claimed to have a WD property here -> BARE.
#     Cue keywords seeded from the v308 map's own keyword surface, lightly generalized to
#     standard magnitude tokens. Lowercased substring match (same as numprop.identify_property).
# ----------------------------------------------------------------------------
# class -> (confirming P-id from v308 map bytes, [cue substrings])
PROVEN_DIM = {
    "length": ("P2044/P2048", [
        "elevation", "altitude", "above sea level", "meters above",
        "height", "tall", "meters tall", "feet tall",
        "meters long", "metres long", "km long", "kilometers long", "kilometres long",
        "long", "wide", "deep", "diameter", "radius", "wingspan",
    ]),
    "area": ("P2046", [
        "area", "surface area", "square kilometers", "square kilometres",
        "square miles", "sq km", "sq mi", "hectares", "acres",
    ]),
    "time": ("P2047", [
        "duration", "runtime", "running time", "minutes long", "hours long",
        "lasts", "seconds long",
    ]),
    "mass": ("P2067", [
        "mass", "weighs", "weight", "kilograms", "body mass",
        "tonnes", "tons", "grams", "pounds",
    ]),
    "count": ("P1082/P1086", [
        "population", "inhabitants", "residents", "people live",
        "atomic number", "proton number", "atomic mass number",
        "employees", "students", "members", "seats", "votes",
    ]),
}

# detected but NOT proven to have a WD quantity property in THIS probe -> routed to BARE,
# logged so a suppressed-but-real class is visible for a grounded follow-up (web_search) if it
# ever shows up in the held-out. (None are claimed eligible -- no fabrication.)
UNPROVEN_DIM = {
    "temperature": ["celsius", "fahrenheit", "kelvin", "degrees", "boiling point", "melting point"],
    "money": ["dollars", "euros", "revenue", "profit", "gdp", "budget", "usd"],
    "speed": ["km/h", "mph", "kilometers per hour", "miles per hour", "knots"],
    "energy_power": ["joules", "watts", "kilowatts", "megawatts", "calories"],
    "frequency": ["hertz", "hz", "rpm", "per second"],
}


def detect_dimension(text):
    """Return (kind, dim, marker). kind in {PROVEN, UNPROVEN, NONE}. First match wins;
    PROVEN checked before UNPROVEN. Deterministic dict order (py3.7+ insertion order)."""
    low = (text or "").lower()
    for dim, (pid, cues) in PROVEN_DIM.items():
        for kw in cues:
            if kw in low:
                return "PROVEN", dim, pid
    for dim, cues in UNPROVEN_DIM.items():
        for kw in cues:
            if kw in low:
                return "UNPROVEN", dim, None
    return "NONE", None, None


# ----------------------------------------------------------------------------
# (D) per-row classifier -> exactly one of ELIGIBLE | BARE-QUANTITY-NO-PROP | NOT-NUMERIC
# ----------------------------------------------------------------------------
ELIGIBLE = "ELIGIBLE"
BARE = "BARE-QUANTITY-NO-PROP"
NOT_NUM = "NOT-NUMERIC"


def classify(claim):
    nums = magnitude_numbers(claim)
    if not nums:
        return NOT_NUM, "no_magnitude_number"

    kind, dim, pid = detect_dimension(claim)
    if kind == "NONE":
        return BARE, "no_dim_cue"
    if kind == "UNPROVEN":
        return BARE, "dim_unproven=%s" % dim
    # PROVEN dimension: requires a bound-entity subject to be a numeric-property assertion
    if not has_entity_subject(claim):
        return BARE, "no_entity_subject(dim=%s)" % dim
    return ELIGIBLE, "dim=%s via=%s" % (dim, pid)


# ----------------------------------------------------------------------------
# (E) run
# ----------------------------------------------------------------------------
def run(in_path, out_path):
    rows = []
    with open(in_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    labels = []
    counts = {ELIGIBLE: 0, BARE: 0, NOT_NUM: 0}
    for rec in rows:
        rid = rec.get("id", "<no-id>")
        label, reason = classify(rec.get("claim", ""))
        counts[label] += 1
        labels.append({"id": rid, "label": label, "reason": reason})

    # KEEP-LOCAL label table: IDs + labels + reason ONLY. NO held-out claim text. LF-pinned.
    labels.sort(key=lambda r: r["id"])
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for r in labels:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    floor = counts[ELIGIBLE]
    total = len(rows)
    print("[eligibility_probe_v310] rows=%d" % total)
    print("[eligibility_probe_v310] ELIGIBLE=%d  BARE-QUANTITY-NO-PROP=%d  NOT-NUMERIC=%d"
          % (counts[ELIGIBLE], counts[BARE], counts[NOT_NUM]))
    print("[eligibility_probe_v310] FLOOR (ELIGIBLE) = %d of %d" % (floor, total))
    bar = ">=3 -> PATH A" if floor >= 3 else "<3 -> PATH B"
    print("[eligibility_probe_v310] B-ELIGIBILITY: floor %s" % bar)
    print("[eligibility_probe_v310] labels -> %s (KEEP-LOCAL)" % out_path)


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "heldout_numprop_liveform_v308.jsonl"
    out = sys.argv[2] if len(sys.argv) > 2 else "numprop_eligibility_v310_labels.jsonl"
    run(inp, out)
