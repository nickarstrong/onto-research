#!/usr/bin/env python3
# build_fixture_E17.py  ::  E17 full-GOLD bind-fixture builder
# Reproduces the E16 derivation at full scale. No fabricated citations.
#
# Derivation (locked against E16 gold_fixture.json, char-exact):
#   source    = citation + ". " + title + "."          (curated/MASTER rule)
#               OR  "{authors} ({year}). {title}."      (structured-module rule)
#   locator   = "DOI:" + doi
#   claim_key = lowercased key_claim, stopwords/symbol/range tokens dropped,
#               standalone integers kept, first 3 content tokens
#   authorized predicate (verifier side, unchanged): sha256(source.utf8) in manifest_files AND locator != ""
#
# Freeze rule: every DOI present in E16 -> source+locator copied VERBATIM (sha256 stable).
#   Only a degenerate/empty E16 claim_key is repaired (embedding side only; does not touch sha256).
#
# Usage: python build_fixture_E17.py <GOLD_ROOT> <E16_FIXTURE.json> <OUT.json>

import json, re, glob, os, sys, hashlib, unicodedata

GOLD = sys.argv[1] if len(sys.argv) > 1 else "ONTO-GOLD"
E16  = sys.argv[2] if len(sys.argv) > 2 else "gold_fixture.json"
OUT  = sys.argv[3] if len(sys.argv) > 3 else "gold_fixture_full.json"

DOI_RE = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')
STOP = {"of","the","a","an","for","to","in","on","and","or","is","are","be","with",
        "from","by","at","as","that","this","not","no","requires","require","still",
        "after","vs","via","using","per","than","minimal","more","less",
        # RU stopwords (GOLD carries Russian sources)
        "и","в","во","на","к","о","об","по","для","от","из","с","со","три","к","понятия","определению"}

def sh(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def norm_doi(d): return d.strip().rstrip('.').lower() if isinstance(d, str) else None

def fix_mojibake(s):
    if not isinstance(s, str): return s
    try: s = s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError): pass
    return unicodedata.normalize("NFC", s)

def claim_key(text):
    """Deterministic reduction: lowercase, drop stopwords/symbol/range tokens,
    keep standalone integers, first 3 content tokens. Unicode-aware (Latin+Cyrillic)."""
    if not text: return ""
    t = fix_mojibake(text).lower()
    raw = re.split(r'[^0-9a-z\u0400-\u04ff]+', t)
    out = []
    for tok in raw:
        if not tok or tok in STOP: continue
        if tok.isdigit(): out.append(tok)                   # keep standalone integers
        elif len(tok) >= 2: out.append(tok)                 # alpha content word (Latin/Cyrillic)
        if len(out) == 3: break
    return " ".join(out)

# ---- curated sources (MASTER_SOURCES) : citation + title + key_claim + doi ----
curated = {}  # norm_doi -> {source, claim_key}
ms = json.load(open(os.path.join(GOLD, "MASTER_SOURCES.json"), encoding="utf-8"))
for k, v in ms.items():
    if k.startswith("tier_") and isinstance(v, dict):
        for r in v.get("sources", {}).values():
            d = norm_doi(r.get("doi"))
            if not (d and r.get("citation") and r.get("title")): continue
            src = f"{fix_mojibake(r['citation'])}. {fix_mojibake(r['title'])}."
            ck  = claim_key(r.get("key_claim") or r["title"])
            curated[d] = {"source": src, "claim_key": ck}

# ---- structured module sources : authors + title + year + doi ----
def walk_sources(o):
    if isinstance(o, dict):
        d = norm_doi(o.get("doi"))
        if d and (o.get("title") or o.get("citation")):
            yield d, o
        for vv in o.values(): yield from walk_sources(vv)
    elif isinstance(o, list):
        for vv in o: yield from walk_sources(vv)

structured = {}  # norm_doi -> {source, claim_key}
prose_only = set()
for j in glob.glob(os.path.join(GOLD, "**", "*.json"), recursive=True):
    try: obj = json.load(open(j, encoding="utf-8", errors="replace"))
    except Exception: continue
    sd = set()
    for d, o in walk_sources(obj):
        sd.add(d)
        if d in curated or d in structured: continue
        title = fix_mojibake(o.get("title") or "")
        if o.get("citation"):
            src = f"{fix_mojibake(o['citation'])}. {title}." if title else fix_mojibake(o["citation"])
        elif o.get("authors") and title:
            au = o["authors"]; au = au if isinstance(au, list) else [au]
            au = ", ".join(fix_mojibake(x) for x in au)
            yr = o.get("year", "")
            src = f"{au} ({yr}). {title}." if yr else f"{au}. {title}."
        elif title:
            src = title if title.endswith(".") else title + "."
        else:
            continue
        structured[d] = {"source": src, "claim_key": claim_key(o.get("key_claim") or title)}
    # prose-only DOIs (no structured citation) -> cannot synthesize, log + skip
    txt = open(j, encoding="utf-8", errors="replace").read()
    for m in DOI_RE.findall(txt):
        d = norm_doi(m)
        if d and d not in sd and d not in curated and d not in structured:
            prose_only.add(d)

# ---- E16 freeze: carry authorized records verbatim, repair only degenerate claim_key ----
fx16 = json.load(open(E16, encoding="utf-8"))
mf16 = set(fx16["manifest_files"])
DEGEN = {"", "blue", "origins", "nasa"}
e16_by_doi = {}
records, manifest, decoys = [], set(), []
carried = repaired = 0
for r in fx16["records"]:
    authed = sh(r["source"]) in mf16 and r.get("locator")
    if not authed:
        decoys.append(dict(r)); continue          # E16 decoy carried as-is
    ck = r["claim_key"]
    if ck.strip().lower() in DEGEN:
        ck = claim_key(r["source"].split(".")[-2] if "." in r["source"] else r["source"])
        repaired += 1
    rec = {"claim_key": ck, "source": r["source"], "locator": r["locator"]}
    records.append(rec); manifest.add(sh(r["source"])); carried += 1
    d = (r["locator"].split("DOI:")[-1].strip().lower()) if "DOI:" in r["locator"] else None
    if d: e16_by_doi[norm_doi(d)] = True

# ---- append NEW authorized records (curated + structured, not already in E16) ----
new = 0
seen_src = {r["source"] for r in records}
for d, rec in {**curated, **structured}.items():
    if d in e16_by_doi: continue
    if not rec["source"] or not d: continue
    if rec["source"] in seen_src: continue          # dedup: same paper under variant DOI
    ck = rec["claim_key"]
    if not ck.strip():                              # degenerate -> fall back to source title tail
        tail = rec["source"].rstrip(".").split(". ")[-1]
        ck = claim_key(tail)
    r = {"claim_key": ck, "source": rec["source"], "locator": "DOI:" + d}
    records.append(r); manifest.add(sh(r["source"])); seen_src.add(rec["source"]); new += 1

fixture = {
    "_meta": {
        "purpose": "Full-GOLD retrieval bind-corpus for E17 scale check (supersedes E16 61-record slice).",
        "provenance": "onto-gold-clean :: E16 authorized carried verbatim (source+locator frozen) + "
                      "MASTER_SOURCES.json + all module sources[] (structured authors/title/year/doi); "
                      "dedup by DOI; prose-only DOIs without structured citation skipped (no synthesis).",
        "hash_alg": "sha256 over source string (utf-8)",
        "derivation": "source=citation+'. '+title+'.' (curated) | '{authors} ({year}). {title}.' (module); "
                      "claim_key=first-3 content tokens of key_claim|title; E16 claim_keys verbatim "
                      "except degenerate/empty repaired (embedding only, sha256 unaffected).",
        "authorized_count": len(records),
        "decoy_count": len(decoys),
        "e16_carried": carried, "e16_claimkey_repaired": repaired, "new_records": new,
        "prose_only_skipped": sorted(prose_only),
        "note": "manifest_files = authorization set (sha256(source)). Decoys absent from manifest (hash-fail).",
    },
    "manifest_files": sorted(manifest),
    "records": records + decoys,
}
json.dump(fixture, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"WROTE {OUT}")
print(f"  authorized={len(records)} (E16 carried={carried}, repaired_ck={repaired}, new={new})")
print(f"  decoys={len(decoys)} | manifest_files={len(manifest)} | prose-only skipped={len(prose_only)}")
