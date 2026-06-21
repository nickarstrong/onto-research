#!/usr/bin/env python3
# l5_edge_source_probe.py -- READ-ONLY. Does NOT touch the frozen predicate.
# For each P4-relevant disposed pair, fetch Crossref `reference` + OpenCitations `references`
# (same fetch logic as the validator, imported) and report which index carries the edge.
# Confirms (before any predicate edit) whether v1.1 "P4 = Crossref-reference-only" gives G1 (suppress 3 DEFECT)
# and G2 (preserve the real cites). Also doubles as the network pre-check.
import urllib.request, json, time, sys
import run_L5_partI_validate as V   # import-only ; frozen predicate untouched

def getter(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ONTO-L5/1.0 (mailto:council@ontostandard.org)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

DOI = {
    "W": "10.1126/science.abb2507",        # S1 Wrapp 6VSB
    "L": "10.1016/j.cell.2020.02.058",     # S2 Walls 6VXX
    "Y": "10.1126/science.abb2762",        # S3 Yan 6M17
    "K": "10.1038/s41598-018-34171-7",     # S4 Kirchdoerfer 6CRZ
    "Wu":  "10.1038/s41586-020-2008-3",    # C014 S1
    "Zhou":"10.1038/s41586-020-2012-7",    # C014 S2
}
# P4-relevant pairs: (label, a, b, disposition, expect_P4_after_fix)
PAIRS = [
    ("C015 S1xS2 Wrapp/Walls",      "W","L", "DEFECT",   False),
    ("C015 S1xS3 Wrapp/Yan",        "W","Y", "DEFECT",   False),
    ("C014 S1xS2 Wu/Zhou",          "Wu","Zhou","DEFECT",False),
    ("C015 S3xS4 Yan/Kirchdoerfer", "Y","K", "EXEMPLAR", True),
    ("C015 S2xS4 Walls/Kirchdoerfer","L","K","citation", True),
]

cache = {}
cr_refs, oc_refs = {}, {}
print("fetching (Crossref + OpenCitations) ...")
for k, doi in DOI.items():
    try:
        cr = V.fetch_crossref(doi, cache, getter); time.sleep(0.3)
        oc = V.fetch_opencit_refs(doi, cache, getter); time.sleep(0.3)
    except Exception as e:
        print(f"  NET FAIL {k} {doi}: {e}"); sys.exit(2)
    cr_refs[k] = {r.lower() for r in cr["refs"]}
    oc_refs[k] = {r.lower() for r in oc}
    print(f"  {k:5} {doi:35}  crossref_refs={len(cr_refs[k]):4d}  oc_refs={len(oc_refs[k]):4d}")

def edge(a, b, refset):
    return (DOI[b].lower() in refset[a]) or (DOI[a].lower() in refset[b])

print()
print(f"{'pair':<32}{'disp':<10}{'cr_edge':<9}{'oc_edge':<9}{'v1.1(cr-only)':<14}{'verdict'}")
g1_ok = g2_ok = True
for label, a, b, disp, expect in PAIRS:
    ce = edge(a, b, cr_refs)
    oe = edge(a, b, oc_refs)
    after = ce  # v1.1 fires P4 on Crossref reference only
    ok = (after == expect)
    if disp == "DEFECT" and after:    g1_ok = False
    if expect and not after:          g2_ok = False
    tag = "OK" if ok else "MISMATCH"
    print(f"{label:<32}{disp:<10}{str(ce):<9}{str(oe):<9}{str(after):<14}{tag}")

print()
print(f"PREDICTED G1 (3 DEFECT -> P4 off after v1.1): {'PASS' if g1_ok else 'FAIL'}")
print(f"PREDICTED G2 (real cites -> P4 stays on)    : {'PASS' if g2_ok else 'FAIL'}")
print()
if g1_ok and g2_ok:
    print(">>> discriminator CONFIRMED: drop-OC P4 suppresses the 3 DEFECT and keeps the real cites. Safe to apply v1.1.")
else:
    print(">>> discriminator NOT clean. Read the cr_edge/oc_edge columns:")
    print("    - a DEFECT with cr_edge=True  -> Crossref itself carries a bad edge ; drop-OC is insufficient, strengthen.")
    print("    - a real cite with cr_edge=False -> Crossref lacks that ref (publisher non-deposit) ; drop-OC would castrate it.")
    print("    Do NOT edit the predicate until this is resolved (R7).")
