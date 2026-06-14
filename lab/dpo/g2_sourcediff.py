import json, re, sys
def load(p):
    d = {}
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l: continue
        o = json.loads(l); d[o["id"]] = o.get("text","")
    return d
PATS = [
    (r"10\.\d{4,}/\S+","DOI"),
    (r"arXiv:\s*\d{4}\.\d{4,5}","arXiv"),
    (r"\b\d{4}\.\d{4,5}\b","arxiv_bare"),
    (r"https?://\S+","URL"),
    (r"\bdoi\b","doi_word"),
    (r"\bet al\.?","etal"),
    (r"\(\s*\d{4}\s*\)","year_paren"),
    (r"\bpp?\.\s*\d+","page_loc"),
    (r"\bvol\.\s*\d+","vol_loc"),
    (r"\bISBN\b","isbn"),
]
def srcs(t):
    out = set()
    for pat, tag in PATS:
        for m in re.findall(pat, t, flags=re.IGNORECASE):
            out.add(tag + "::" + str(m))
    return out
base, dpo = sys.argv[1], sys.argv[2]
B, D = load(base), load(dpo)
netnew = []
for i in sorted(D):
    new = srcs(D.get(i,"")) - srcs(B.get(i,""))
    if new: netnew.append((i, sorted(new)))
print("pair:", base, "->", dpo)
print("ids with NET-NEW source tokens (DPO not in base):", len(netnew))
for i, ns in netnew: print("  ", i, ns)
print("G2 raw:", "CLEAN (0 net-new -> no mint)" if not netnew else "NET-NEW -> must resolve via GOLD")
