#!/usr/bin/env python3
"""
o0_denominator_recut_score.py  --  SPEC_denominator_recut_v1 scorer.

E15-SAFE: pure aggregator. Authors NO claims, NO CLEAN/DIRTY labels, runs NO pipeline.
Reads Founder-labeled re-cut set + one frozen temporal-channel run, emits M1/M2/lift/fa_live
plus acceptance A1-A4. Deterministic: same inputs -> same numbers.

Inputs
------
--recut    recut_labeled.jsonl   Founder-authored. One claim per line:
             {"id": str,
              "claim": str,
              "abstract": str,            # B2 abstract used by the pipeline (may be "")
              "founder_label": "CLEAN"|"DIRTY",
              "absorbed_off": bool,       # absorbed by pipeline with temporal channel OFF
              "absorbed_on":  bool,       # absorbed by pipeline with temporal channel ON
              "temporal_verdict": "CONFIRM"|"REFUTE"|"ABSTAIN"|"NA"}  # this run, frozen
--live-date-band  "lo,hi"        optional. Observed date-bearing fraction band from S2.
                                 Omitted -> A4 reported, never blocks.

Structural fields (date_bearing, year_in_abstract) are DERIVED here, not labeled.
"""
import argparse, json, math, re, sys

YEAR = re.compile(r"\b(1[5-9]\d{2}|20\d{2})\b")  # 1500-2099, load-bearing year token


def years(text):
    return set(YEAR.findall(text or ""))


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit("INVALID: %s line %d not JSON: %s" % (path, ln, e))
    return rows


def derive(r):
    cy = years(r.get("claim", ""))
    ay = years(r.get("abstract", ""))
    r["_date_bearing"] = len(cy) > 0
    # year is "covered" only if a claim year also appears in the abstract
    r["_year_in_abstract"] = len(cy & ay) > 0
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recut", required=True)
    ap.add_argument("--live-date-band", default=None)
    a = ap.parse_args()

    rows = [derive(r) for r in load(a.recut)]
    n = len(rows)
    if n == 0:
        sys.exit("INVALID: empty re-cut set")

    clean = [r for r in rows if r.get("founder_label") == "CLEAN"]
    dirty = [r for r in rows if r.get("founder_label") == "DIRTY"]
    other = [r for r in rows if r.get("founder_label") not in ("CLEAN", "DIRTY")]
    if other:
        sys.exit("INVALID: %d rows with non-CLEAN/DIRTY founder_label (E15: labels required)"
                 % len(other))

    # M1 pipeline G3 (CLEAN absorbed / N) channel on/off
    m1_on  = sum(1 for r in clean if r.get("absorbed_on"))  / n
    m1_off = sum(1 for r in clean if r.get("absorbed_off")) / n
    lift = m1_on - m1_off

    # M2 channel recovery: CONFIRMed / CLEAN date-bearing, year-not-in-abstract
    recov_pool = [r for r in clean if r["_date_bearing"] and not r["_year_in_abstract"]]
    recovered = [r for r in recov_pool if r.get("temporal_verdict") == "CONFIRM"]
    m2 = (len(recovered) / len(recov_pool)) if recov_pool else None

    # fa_live: fabricated (DIRTY) absorbed (channel ON) / DIRTY count
    dirty_n = len(dirty)
    fa_live = (sum(1 for r in dirty if r.get("absorbed_on")) / dirty_n) if dirty_n else None

    # acceptance
    clean_absorbable = sum(1 for r in clean
                           if r.get("absorbed_on") or r.get("absorbed_off")
                           or (r["_date_bearing"] and not r["_year_in_abstract"]))
    dirty_year = sum(1 for r in dirty if r["_date_bearing"])
    db_frac = sum(1 for r in rows if r["_date_bearing"]) / n

    A1 = n >= 40
    A2 = clean_absorbable >= math.ceil(0.20 * n) + 2
    A3 = dirty_year >= 4
    if a.live_date_band:
        lo, hi = (float(x) for x in a.live_date_band.split(","))
        A4 = "PASS" if lo <= db_frac <= hi else "FLAG(out-of-band)"
    else:
        A4 = "FLAG(no-band-provided)"

    promote = (m1_on >= 0.20) and (lift > 0) and (fa_live is not None and fa_live <= 0.10)

    out = {
        "N": n, "clean": len(clean), "dirty": dirty_n,
        "date_bearing_fraction": round(db_frac, 3),
        "M1_on": round(m1_on, 3), "M1_off": round(m1_off, 3), "lift": round(lift, 3),
        "M2_channel_recovery": (round(m2, 3) if m2 is not None else "N/A(empty pool)"),
        "M2_pool": len(recov_pool),
        "fa_live": (round(fa_live, 3) if fa_live is not None else "N/A(no DIRTY)"),
        "acceptance": {
            "A1_N>=40": A1,
            "A2_absorbable>=ceil(.2N)+2": "%s (have %d, need %d)" %
                (A2, clean_absorbable, math.ceil(0.20 * n) + 2),
            "A3_dirty_with_year>=4": "%s (have %d)" % (A3, dirty_year),
            "A4_date_band": A4,
        },
        "valid_for_scoring": bool(A1 and A2 and A3),
        "promotion_rule": "M1_on>=0.20 AND lift>0 AND fa_live<=0.10",
        "PROMOTE_to_gating": bool(promote),
    }
    print(json.dumps(out, indent=2))
    if not out["valid_for_scoring"]:
        sys.stderr.write("WARN: cut INVALID (A1-A3) -- numbers advisory only, re-cut required\n")


if __name__ == "__main__":
    main()
