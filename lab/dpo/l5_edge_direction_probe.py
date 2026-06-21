#!/usr/bin/env python3
# l5_edge_direction_probe.py -- READ-ONLY. Resolve the DIRECTION of every P4 edge against the
# authoritative Crossref deposited `reference` list (+ OpenCitations), and date-check each.
# Adjudicates: real (later cites earlier) citation  vs  impossible-direction Crossref artifact.
import urllib.request, json, time, sys
import run_L5_partI_validate as V   # import-only ; frozen predicate untouched

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ONTO-L5/1.0 (mailto:council@ontostandard.org)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

DOI = {
    "Wrapp":"10.1126/science.abb2507", "Walls":"10.1016/j.cell.2020.02.058",
    "Yan":"10.1126/science.abb2762",   "Kirch":"10.1038/s41598-018-34171-7",
    "Wu":"10.1038/s41586-020-2008-3",  "Zhou":"10.1038/s41586-020-2012-7",
}
PAIRS = [  # (claim-pair, A, B, current truth label after relabel)
    ("C015 S1xS2 Wrapp/Walls",  "Wrapp","Walls", "independent (DEFECT?)"),
    ("C015 S1xS3 Wrapp/Yan",    "Wrapp","Yan",   "independent (DEFECT?)"),
    ("C014 S1xS2 Wu/Zhou",      "Wu","Zhou",     "independent (DEFECT?)"),
    ("C015 S3xS4 Yan/Kirch",    "Yan","Kirch",   "citation (relabeled)"),
    ("C015 S2xS4 Walls/Kirch",  "Walls","Kirch", "citation"),
]

def issued(doi):
    try:
        m = get(("https://api.crossref.org/works/{}").format(doi)).get("message", {})
        for k in ("published-online","published-print","issued","created"):
            dp = m.get(k, {}).get("date-parts", [[None]])[0]
            if dp and dp[0]: return "-".join(str(x) for x in dp)
    except Exception: pass
    return "?"

cache = {}; cr={}; oc={}; dt={}
print("fetching ...")
for k, doi in DOI.items():
    try:
        c = V.fetch_crossref(doi, cache, get); time.sleep(0.3)
        o = V.fetch_opencit_refs(doi, cache, get); time.sleep(0.3)
        dt[k] = issued(doi); time.sleep(0.3)
    except Exception as e:
        print(f"NET FAIL {k}: {e}"); sys.exit(2)
    cr[k] = {x.lower() for x in c["refs"]}; oc[k] = {x.lower() for x in o}
    print(f"  {k:7} {doi:34} issued={dt[k]:12} cr_refs={len(cr[k])} oc_refs={len(oc[k])}")

print()
for label, a, b, lbl in PAIRS:
    a2b_cr = DOI[b].lower() in cr[a];  b2a_cr = DOI[a].lower() in cr[b]
    a2b_oc = DOI[b].lower() in oc[a];  b2a_oc = DOI[a].lower() in oc[b]
    print(f"== {label}   [truth: {lbl}]")
    print(f"   {a}({dt[a]}) cites {b}({dt[b]}) ?  crossref={a2b_cr}  oc={a2b_oc}")
    print(f"   {b}({dt[b]}) cites {a}({dt[a]}) ?  crossref={b2a_cr}  oc={b2a_oc}")
    # adjudicate by chronology: the citing paper must be NOT-earlier than the cited
    def sound(citing, cited):
        try:
            ci = tuple(int(x) for x in dt[citing].split("-"))
            ce = tuple(int(x) for x in dt[cited].split("-"))
            return ci >= ce
        except Exception:
            return None
    verdicts = []
    if a2b_cr or a2b_oc:
        s = sound(a, b); verdicts.append(f"{a}->{b} {'REAL-cite (later cites earlier)' if s else 'IMPOSSIBLE-direction (artifact)' if s is False else 'date-? '}")
    if b2a_cr or b2a_oc:
        s = sound(b, a); verdicts.append(f"{b}->{a} {'REAL-cite (later cites earlier)' if s else 'IMPOSSIBLE-direction (artifact)' if s is False else 'date-? '}")
    if not verdicts: verdicts = ["no edge either index"]
    print("   ADJUDICATION:", " | ".join(verdicts))
    print()
print("READ-ONLY. No predicate edit. Use ADJUDICATION to correct the disposition (relabel real cites -> citation ;")
print("keep only impossible-direction edges as the genuine P4 artifact to fix).")
