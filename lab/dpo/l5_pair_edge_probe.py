#!/usr/bin/env python3
# l5_pair_edge_probe.py -- READ-ONLY generalized per-pair edge emitter (gg instrument).
#
# WHY: the two old probes (l5_edge_source_probe / l5_edge_direction_probe) are HARDCODED to the
# (ee) cryo-EM DOIs, P4-only, no CLI -> they cover 0 of the 7 (ff) false-couples. This emitter
# adjudicates BOTH legs (P1 author + P4 derivation) for ANY (claim,pair) read from the frozen
# truth-set, then prints a per-pair disposition that hands a fix-spec target to a LATER session.
#
# DISCIPLINE (R7):
#   - import-only. The COUPLING VERDICT of each leg comes from the FROZEN predicate functions
#     (V.fetch_crossref / V.fetch_opencit_refs / V._norm_name) -- byte-identical to what the scorer saw.
#   - raw Crossref message is fetched ONLY for DISPLAY enrichment (raw author name, ORCID,
#     affiliation, issued-date). It NEVER feeds a verdict. The URL-memoizing getter reuses the same
#     HTTP response V already pulled, so no extra crossref hit per DOI.
#   - NO predicate edit. NO gate edit. NO truth edit. NO relabel-to-pass. NO write of any truth content.
#   - startup md5-guard asserts the on-disk predicate is the frozen v1.1 (b96bfb43...). Mismatch = STOP.
#
# MODES:
#   --dryplan            : resolve (claim,pair)->DOIs from truth, print the plan. NO network. (TYPE C verify)
#   --netcheck           : fetch one Crossref + one OpenCitations record. reachable? exit 0/2. (run step 1)
#   --run                : live. fetch + adjudicate both legs for each pair. emit disposition table.
#   --pairs "C:SaxSb,..."  : claim-qualified pair list. default = the 7 (ff) false-couples (Wu/Zhou SKIP).
#   --truth PATH         : truth jsonl (default eval/_local/l5_coupling_truth.jsonl).
#   --out PATH           : optional LOCAL-ONLY md disposition doc. default = stdout only. (never git)

import argparse, json, sys, time, hashlib, os
import run_L5_partI_validate as V   # import-only ; frozen predicate untouched

FROZEN_PREDICATE_MD5 = "b96bfb434d1df3d50b4395a011eb355a"
UA = "ONTO-L5/1.0 (mailto:council@ontostandard.org)"
SLEEP = 0.3

# the 7 (ff) false-couples ; Wu/Zhou (C014 S1xS2) = accepted residual -> NOT here (SKIP)
DEFAULT_PAIRS = ["C002:S1xS2", "C003:S2xS3",
                 "C004:S1xS3", "C004:S1xS4", "C004:S2xS3", "C004:S2xS4", "C004:S3xS4"]


# ---------------------------------------------------------------- predicate-frozen guard
def guard_frozen():
    p = os.path.abspath(V.__file__)
    if p.endswith(".pyc"):
        p = p[:-1]  # .pyc -> .py
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    if h != FROZEN_PREDICATE_MD5:
        print(f"STOP: predicate md5 {h} != frozen {FROZEN_PREDICATE_MD5} ({p})", file=sys.stderr)
        sys.exit(3)
    return h


# ---------------------------------------------------------------- url-memoizing getter
class Getter:
    """One real HTTP GET per unique URL (sleep only on a real miss). Shared by V.* and raw fetch
    so the verdict legs and the display enrichment ride the SAME crossref response."""
    def __init__(self):
        self._http = {}
        self.hits = 0
    def __call__(self, url):
        if url in self._http:
            return self._http[url]
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read().decode())
        self._http[url] = data
        self.hits += 1
        time.sleep(SLEEP)
        return data


# ---------------------------------------------------------------- raw crossref (DISPLAY ONLY)
def raw_message(doi, getter):
    """Raw Crossref message for display fields ONLY (names/ORCID/affil/issued). Never a verdict."""
    try:
        return getter(V.CROSSREF.format(doi=doi)).get("message", {})
    except Exception:
        return {}

def issued_str(msg):
    for k in ("published-online", "published-print", "issued", "created"):
        dp = (msg.get(k, {}) or {}).get("date-parts", [[None]])[0]
        if dp and dp[0]:
            return "-".join(str(x) for x in dp)
    return "?"

def authors_for_token(msg, token):
    """Raw author entries whose V._norm_name(given+family) == token. Display enrichment."""
    out = []
    for a in msg.get("author", []) or []:
        fam, giv = a.get("family", ""), a.get("given", "")
        if V._norm_name(giv + fam) == token:
            out.append({
                "name": (f"{giv} {fam}").strip(),
                "orcid": a.get("ORCID"),
                "affils": [af.get("name", "") for af in (a.get("affiliation", []) or []) if af.get("name")],
            })
    return out


# ---------------------------------------------------------------- leg adjudicators
def p1_emit(da, db, vcache, getter):
    """P1 author leg. VERDICT from frozen V.fetch_crossref intersection ; call from raw enrichment."""
    ma = V.fetch_crossref(da, vcache, getter)
    mb = V.fetch_crossref(db, vcache, getter)
    inter = sorted(ma["authors"] & mb["authors"])          # frozen, normalized tokens
    fired = bool(inter)
    rm_a, rm_b = raw_message(da, getter), raw_message(db, getter)
    tokens = []
    overall = "no_author_overlap"
    for tok in inter:
        sa, sb = authors_for_token(rm_a, tok), authors_for_token(rm_b, tok)
        orc_a = {x["orcid"] for x in sa if x["orcid"]}
        orc_b = {x["orcid"] for x in sb if x["orcid"]}
        aff_a = {V._norm_affil(f) for x in sa for f in x["affils"]}
        aff_b = {V._norm_affil(f) for x in sb for f in x["affils"]}
        if orc_a and orc_b and (orc_a & orc_b):
            call = "genuine_same_person(ORCID match)"
        elif orc_a and orc_b and not (orc_a & orc_b):
            call = "collision(ORCID mismatch)"
        elif aff_a & aff_b:
            call = "genuine_by_affil(no ORCID confirm)"
        else:
            call = "ambiguous_common_name(no ORCID, no affil overlap)"
        tokens.append({"token": tok, "a": sa, "b": sb, "call": call})
    if tokens:
        calls = [t["call"].split("(")[0] for t in tokens]
        overall = ("collision" if any(c == "collision" for c in calls)
                   else "genuine_same_person" if any(c == "genuine_same_person" for c in calls)
                   else "genuine_by_affil" if any(c == "genuine_by_affil" for c in calls)
                   else "ambiguous_common_name")
    return {"leg": "P1", "fired": fired, "tokens": tokens, "call": overall}

def p4_emit(da, db, vcache, getter):
    """P4 derivation leg. VERDICT from frozen V.fetch_crossref refs + V.fetch_opencit_refs ;
    source (cr vs oc-only) + chronological direction from the same frozen data + raw issued-date."""
    cr_a = {r.lower() for r in V.fetch_crossref(da, vcache, getter)["refs"]}
    cr_b = {r.lower() for r in V.fetch_crossref(db, vcache, getter)["refs"]}
    oc_a = {r.lower() for r in V.fetch_opencit_refs(da, vcache, getter)}
    oc_b = {r.lower() for r in V.fetch_opencit_refs(db, vcache, getter)}
    la, lb = da.lower(), db.lower()
    a2b_cr, b2a_cr = lb in cr_a, la in cr_b
    a2b_oc, b2a_oc = lb in oc_a, la in oc_b
    cr_edge = a2b_cr or b2a_cr
    oc_edge = a2b_oc or b2a_oc
    fired = cr_edge or oc_edge                              # frozen P4 = refs_all (cr UNION oc)
    oc_only = oc_edge and not cr_edge
    dt_a = issued_str(raw_message(da, getter))
    dt_b = issued_str(raw_message(db, getter))
    def sound(citing_dt, cited_dt):
        try:
            ci = tuple(int(x) for x in citing_dt.split("-"))
            ce = tuple(int(x) for x in cited_dt.split("-"))
            return ci >= ce
        except Exception:
            return None
    dirs = []
    if a2b_cr or a2b_oc:
        s = sound(dt_a, dt_b)
        dirs.append({"citing": da, "cited": db, "src": "cr" if a2b_cr else "oc-only",
                     "chron": "REAL" if s else "IMPOSSIBLE" if s is False else "date?"})
    if b2a_cr or b2a_oc:
        s = sound(dt_b, dt_a)
        dirs.append({"citing": db, "cited": da, "src": "cr" if b2a_cr else "oc-only",
                     "chron": "REAL" if s else "IMPOSSIBLE" if s is False else "date?"})
    # disposition call
    if not fired:
        call = "no_edge"
    elif any(d["src"] == "cr" and d["chron"] == "REAL" for d in dirs):
        call = "COUPLED-relabel(real cr cite, later->earlier)"
    elif oc_only and any(d["chron"] == "IMPOSSIBLE" for d in dirs):
        call = "INDEPENDENT-defect(oc-only courtesy, impossible direction)"
    elif oc_only and any(d["chron"] == "REAL" for d in dirs):
        call = "AMBIGUOUS(oc-only real cite; drop-OC would castrate -> G2 risk)"
    elif cr_edge and any(d["chron"] == "IMPOSSIBLE" for d in dirs):
        call = "DEFECT-cr(Crossref carries bad edge; drop-OC insufficient)"
    else:
        call = "REVIEW(date-unresolved)"
    return {"leg": "P4", "fired": fired, "cr_edge": cr_edge, "oc_edge": oc_edge,
            "oc_only": oc_only, "issued": {da: dt_a, db: dt_b}, "dirs": dirs, "call": call}


# ---------------------------------------------------------------- truth resolution
def load_truth(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    by_claim = {}
    for r in rows:
        sid2doi = {s["sid"]: s["doi"] for s in r["sources"]}
        labels = {frozenset((t["a"], t["b"])): t["label"] for t in r["coupling_truth"]}
        by_claim[r["claim_id"]] = {"sid2doi": sid2doi, "labels": labels}
    return by_claim

def resolve(pairs, by_claim):
    out = []
    for p in pairs:
        claim, pr = p.split(":")
        a, b = pr.split("x")
        c = by_claim.get(claim)
        if not c or a not in c["sid2doi"] or b not in c["sid2doi"]:
            print(f"STOP: cannot resolve {p} in truth-set", file=sys.stderr); sys.exit(4)
        out.append({"key": p, "claim": claim, "pair": pr, "a": a, "b": b,
                    "doi_a": c["sid2doi"][a], "doi_b": c["sid2doi"][b],
                    "declared": c["labels"].get(frozenset((a, b)), "?")})
    return out


# ---------------------------------------------------------------- modes
def do_dryplan(plan):
    print("DRYPLAN (no network) -- (claim,pair) -> DOIs ; declared truth label")
    for x in plan:
        print(f"  {x['key']:<12} {x['doi_a']:<34} x {x['doi_b']:<34}  declared={x['declared']}")
    print(f"\n{len(plan)} pairs resolved. predicate frozen OK. ready for --netcheck then --run.")

def do_netcheck(getter):
    cr_probe = "10.1126/science.abb2507"   # known-resolvable
    try:
        m = getter(V.CROSSREF.format(doi=cr_probe)).get("message", {})
        ok_cr = bool(m.get("DOI"))
    except Exception as e:
        print(f"CROSSREF UNREACHABLE: {e}", file=sys.stderr); sys.exit(2)
    try:
        oc = V.fetch_opencit_refs(cr_probe, {}, getter)
        ok_oc = isinstance(oc, set)
    except Exception as e:
        print(f"OPENCITATIONS UNREACHABLE: {e}", file=sys.stderr); sys.exit(2)
    print(f"NETCHECK: crossref={'OK' if ok_cr else 'FAIL'}  opencitations={'OK' if ok_oc else 'FAIL'}  "
          f"(oc_refs on probe={len(oc)})")
    sys.exit(0 if (ok_cr and ok_oc) else 2)

def do_run(plan, getter, out_path):
    vcache = {}
    recs = []
    for x in plan:
        p1 = p1_emit(x["doi_a"], x["doi_b"], vcache, getter)
        p4 = p4_emit(x["doi_a"], x["doi_b"], vcache, getter)
        recs.append({**x, "p1": p1, "p4": p4})
        print(f"\n== {x['key']}  [{x['doi_a']} x {x['doi_b']}]  declared={x['declared']}")
        print(f"   P1 fired={p1['fired']}  call={p1['call']}")
        for t in p1["tokens"]:
            print(f"      token '{t['token']}': call={t['call']}")
            print(f"        A: {[ (s['name'], s['orcid']) for s in t['a'] ]}")
            print(f"        B: {[ (s['name'], s['orcid']) for s in t['b'] ]}")
        print(f"   P4 fired={p4['fired']}  cr_edge={p4['cr_edge']}  oc_edge={p4['oc_edge']}  "
              f"oc_only={p4['oc_only']}  call={p4['call']}")
        for d in p4["dirs"]:
            print(f"      {d['citing']} -> {d['cited']}  src={d['src']}  chron={d['chron']}")

    # disposition table
    print("\n## PER-PAIR DISPOSITION (read-only ; predicate not gated by this)")
    print(f"{'pair':<12} {'declared':<12} {'P1':<6} {'P1 call':<34} {'P4':<6} {'P4 call'}")
    for r in recs:
        print(f"{r['key']:<12} {r['declared']:<12} "
              f"{str(r['p1']['fired']):<6} {r['p1']['call']:<34} "
              f"{str(r['p4']['fired']):<6} {r['p4']['call']}")

    if out_path:
        write_md(out_path, recs, getter)
        print(f"\nwrote LOCAL-ONLY disposition: {out_path}  (NEVER git -- truth-derived)")

def write_md(path, recs, getter):
    L = ["# l5_gg_disposition -- per-pair edge adjudication (READ-ONLY ; LOCAL ONLY ; NOT git)",
         "",
         f"predicate frozen md5 {FROZEN_PREDICATE_MD5} ; real crossref+oc GETs this run = {getter.hits}",
         "",
         "| pair | declared | P1 fired | P1 call | P4 fired | cr | oc | P4 call |",
         "|---|---|---|---|---|---|---|---|"]
    for r in recs:
        p1, p4 = r["p1"], r["p4"]
        L.append(f"| {r['key']} | {r['declared']} | {p1['fired']} | {p1['call']} "
                 f"| {p4['fired']} | {p4['cr_edge']} | {p4['oc_edge']} | {p4['call']} |")
    L += ["", "## evidence detail"]
    for r in recs:
        L.append(f"### {r['key']}  ({r['doi_a']} x {r['doi_b']})  declared={r['declared']}")
        for t in r["p1"]["tokens"]:
            L.append(f"- P1 token `{t['token']}` -> {t['call']}")
            L.append(f"  - A: {[(s['name'], s['orcid'], s['affils']) for s in t['a']]}")
            L.append(f"  - B: {[(s['name'], s['orcid'], s['affils']) for s in t['b']]}")
        for d in r["p4"]["dirs"]:
            L.append(f"- P4 {d['citing']} -> {d['cited']} : src={d['src']} chron={d['chron']}")
        L.append(f"- P4 issued: {r['p4']['issued']}")
        L.append("")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dryplan", action="store_true")
    ap.add_argument("--netcheck", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--pairs", default=",".join(DEFAULT_PAIRS))
    ap.add_argument("--truth", default="eval/_local/l5_coupling_truth.jsonl")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    guard_frozen()
    pairs = [p.strip() for p in a.pairs.split(",") if p.strip()]

    if a.netcheck:
        do_netcheck(Getter()); sys.exit(0)

    by_claim = load_truth(a.truth)
    plan = resolve(pairs, by_claim)

    if a.dryplan:
        do_dryplan(plan)
    elif a.run:
        do_run(plan, Getter(), a.out)
    else:
        ap.print_help()
