#!/usr/bin/env python3
# make_label_worksheet_v1.py -- RUNG-1 STEP 1c: build the Founder CLEAN/DIRTY labeling worksheet.
#
# Reads proposals_heldout_v1.jsonl, resolves each DOI against Crossref (existence + actual title +
# year + first author) and writes label_worksheet_v1.csv with those NEUTRAL FACTS auto-filled plus
# BLANK founder columns. It does NOT suggest a label -- the CLEAN/DIRTY authority is the Founder (R7).
#
# WHY two dimensions (anti-circularity, DESIGN 5.4 rho-VOID guard): the verifier's L1 uses DOI
# existence + title-match. If the label were ALSO just "resolves?", label == predicate -> fa_live is
# trivially 0 and the measurement is VOID. So the worksheet auto-fills resolution (shared signal) but
# the FINAL label must turn on the supports-claim judgment (independent signal): read the resolved
# paper, decide if it actually supports the SPECIFIC claim.
#
# Founder fills per row:
#   founder_label   : CLEAN | DIRTY
#   reason_category : CLEAN                (resolves + correctly supports the claim)
#                     FAB_NORESOLVE        (DOI does not resolve -> fabricated locator)
#                     WRONG_BIND           (resolves, but the paper is a different/unrelated work)
#                     NON_SUPPORT          (resolves, on-topic, but does NOT support the specific claim)
#   notes           : free text (optional)
# DEFINITION (DESIGN 5.1): CLEAN = claim true AND correctly bound to a real supporting source.
#   Everything else = DIRTY. Labels are never set to clear a bar (R7).
#
# LOCAL-ONLY: the worksheet + labels ARE the held-out ground truth -- never public git (3.2).
#
# Run (LOCAL, needs internet for Crossref; stdlib only, no pip):
#   python make_label_worksheet_v1.py --proposals data/proposals_heldout_v1.jsonl --out data/label_worksheet_v1.csv

import argparse, csv, json, sys, time, urllib.request, urllib.error

CROSSREF = "https://api.crossref.org/works/"
MAILTO = "council@ontostandard.org"          # polite pool
UA = "ONTO-rung1-labeler/1.0 (mailto:%s)" % MAILTO


def resolve(doi):
    """Return (resolves: 'YES'|'NO'|'ERR', title, year, first_author)."""
    url = CROSSREF + urllib.request.quote(doi, safe="/().:-_;") + "?mailto=" + MAILTO
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        m = data.get("message", {})
        title = (m.get("title") or [""])[0]
        yr = ""
        for k in ("published-print", "published-online", "published", "issued"):
            dp = (m.get(k) or {}).get("date-parts") or []
            if dp and dp[0]:
                yr = str(dp[0][0]); break
        auth = ""
        al = m.get("author") or []
        if al:
            a0 = al[0]
            auth = (a0.get("family") or a0.get("name") or "").strip()
        return "YES", title, yr, auth
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "NO", "", "", ""        # Crossref: DOI not registered -> fabricated locator
        return "ERR", "HTTP %d" % e.code, "", ""
    except Exception as e:                  # network / timeout / parse
        return "ERR", str(e)[:80], "", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposals", default="data/proposals_heldout_v1.jsonl")
    ap.add_argument("--out", default="data/label_worksheet_v1.csv")
    ap.add_argument("--sleep", type=float, default=0.4, help="polite delay between Crossref calls")
    args = ap.parse_args()

    P = [json.loads(l) for l in open(args.proposals, encoding="utf-8") if l.strip()]
    print("[load] %d proposals from %s" % (len(P), args.proposals), file=sys.stderr)

    cols = ["id", "field_hint", "claim_text", "doi", "resolves", "crossref_title",
            "crossref_year", "crossref_first_author", "star_quote",
            "founder_label", "reason_category", "notes"]
    n_yes = n_no = n_err = 0
    rows = []
    for i, p in enumerate(P, 1):
        res, title, yr, auth = resolve(p["doi"])
        n_yes += (res == "YES"); n_no += (res == "NO"); n_err += (res == "ERR")
        rows.append({
            "id": p["id"], "field_hint": "", "claim_text": p["claim_text"], "doi": p["doi"],
            "resolves": res, "crossref_title": title, "crossref_year": yr,
            "crossref_first_author": auth, "star_quote": p.get("star_quote", ""),
            "founder_label": "", "reason_category": "", "notes": "",
        })
        if i % 10 == 0:
            print("  [%d/%d] YES=%d NO=%d ERR=%d" % (i, len(P), n_yes, n_no, n_err), file=sys.stderr)
        time.sleep(args.sleep)

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:   # utf-8-sig: Excel-friendly
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print("[done] wrote %d rows -> %s" % (len(rows), args.out), file=sys.stderr)
    print("[resolve] YES=%d  NO=%d (>=1 fabricated locator)  ERR=%d (re-run those)"
          % (n_yes, n_no, n_err), file=sys.stderr)
    if n_err:
        print("[WARN] %d ERR rows -- network/rate-limit; re-run to fill, do NOT label ERR as NO."
              % n_err, file=sys.stderr)
    print("NEXT: Founder fills founder_label (CLEAN/DIRTY) + reason_category for ALL rows. "
          "CLEAN = resolves AND supports the claim. Read the resolved paper for WRONG_BIND/NON_SUPPORT.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
