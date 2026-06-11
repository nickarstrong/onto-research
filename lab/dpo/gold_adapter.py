#!/usr/bin/env python3
# gold_adapter.py -- E16 LIVE-BIND: deterministic GOLD literature module -> GoldStore corpus.
#
# DISCIPLINE (pack v95 sec0/sec1/sec3 ; PACK_SPEC ; SPEC_verifier_v1):
#   - Deterministic, NO model. One pass over literature/extractions/*.json (+ .bib for cite
#     enrichment). Emits the EXACT record shape GoldStore (gold_retrieve.py) consumes:
#         {"manifest_files": [sha256(source), ...],
#          "records": [{"claim_key", "source", "locator", "finding"}, ...]}
#   - This is the OPERATIONAL bind-corpus config. It is NOT a re-derivation of the frozen
#     E25b fixture (SPEC sec3): different path, different content, same record shape. The E25b
#     fixture + its 0.0333 anchor stay the separate drift sentinel; this never touches them.
#   - Heterogeneous source schema across 34 files is handled by an EXPLICIT prioritized
#     field-map (below). Records that cannot yield a non-empty (source, locator, finding) are
#     EXCLUDED WITH A LOGGED REASON -- never fabricated, never silently dropped (R7, E23 VOID).
#
# RECORD CONTRACT (read off GoldStore + verify_E16_L4, byte-verified vs committed organ):
#   GoldStore wants per record: claim_key (REQUIRED), source (REQUIRED), locator (default "",
#     but is_authorized demands != ""). hash = sha256(source) computed at load.
#   verify_E16_L4.L4Bind reads record["finding"] (NLI premise) keyed by record["source"];
#     => source MUST be unique per finding (else finding_by_source collapses).
#   semantic_retrieve.build_index embeds f'{claim_key} {source}'.
#
# FIELD-MAP (frozen this session):
#   finding  = leaf text T (a quote/claim/finding/admission/statement, >= MIN_WORDS words)
#   locator  = f"{extraction_id}::{json_path}"  (+ " | " + explicit location sibling if present)
#              -- the structural GOLD address: real, deterministic, tamper-evident, non-empty.
#   source   = f"{paper_cite} #{json_path}"     -- unique per finding (path-suffixed)
#   claim_key= T                                 -- finding text as retrieval key (max retrieval
#              fidelity: retrieve(claim) embeds claim_key+source, NLI compares claim vs finding)
#   paper_cite = first available of: source.id -> source.doi -> source.reference/
#                primary_reference -> RU top-level author+year -> source-as-string ->
#                extraction_id ; enriched with author(s)+year+title when present.
#
# USAGE:
#   python3 gold_adapter.py --lit <literature_dir> --out <corpus.json> [--gate]
#     <literature_dir> must contain extractions/*.json (BIBLIOGRAPHY.bib optional, cite enrich).
#   --gate runs the G2 structural gate and exits non-zero on any violation.

import argparse
import glob
import hashlib
import json
import os
import re
import sys

MIN_WORDS = 4  # scaffolding filter: a finding leaf must carry >= 4 words

# keys whose string value at any depth is a finding (premise) leaf
FINDING_KEY = re.compile(
    r"^(quote|quote_ru|quote_en|quote_paraphrase|quote_source|finding|actual_finding|"
    r"initial_finding|admission|claim|prigogine_claim|statement|statement_ru|conclusion|"
    r"main_claim|supporting_claim|key_point|key_insight|key_finding|key_quote|key_quote_ru|"
    r"insight|response|tour_critique|onto_critique|critical_insight|takeaway)$",
    re.I,
)
# keys naming a location/locator sibling
LOC_KEY = re.compile(r"^(location|locator|page|section|where|cite|reference)$", re.I)


def _sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _cite(d):
    """Deterministic paper citation string from a heterogeneous extraction dict."""
    src = d.get("source")
    eid = str(d.get("extraction_id", "UNKNOWN"))
    parts = []
    if isinstance(src, dict) and src:
        a = src.get("author") or src.get("authors")
        if a:
            parts.append(str(a))
        if src.get("year"):
            parts.append(str(src["year"]))
        if src.get("title"):
            parts.append(str(src["title"]))
        ref = src.get("reference") or src.get("primary_reference")
        if ref:
            parts.append(str(ref))
        tag = src.get("id") or (("doi:" + str(src["doi"])) if src.get("doi") else None)
        if tag:
            parts.append("[" + str(tag) + "]")
    elif isinstance(src, str) and src.strip():
        parts.append(src.strip())
        if d.get("author"):
            parts.append(str(d["author"]))
        if d.get("year"):
            parts.append(str(d["year"]))
    else:  # source MISSING -- RU top-level or extraction_id fallback
        if d.get("author"):
            parts.append(str(d["author"]))
        if d.get("year"):
            parts.append(str(d["year"]))
        ts = d.get("target_source")
        if isinstance(ts, dict) and ts.get("title"):
            parts.append("re:" + str(ts["title"]))
        elif isinstance(ts, str):
            parts.append("re:" + ts)
    cite = " ".join(p for p in parts if p).strip()
    return cite if cite else eid


def _walk(node, path, loc_inherited, out):
    """Collect (json_path, finding_text, locator) for every finding leaf."""
    if isinstance(node, dict):
        loc = loc_inherited
        for k, v in node.items():
            if isinstance(v, str) and LOC_KEY.match(k) and v.strip():
                loc = v.strip()
        for k, v in node.items():
            jp = path + "." + k if path else k
            if isinstance(v, str):
                if FINDING_KEY.match(k) and len(v.split()) >= MIN_WORDS:
                    out.append((jp, v.strip(), loc))
            else:
                _walk(v, jp, loc, out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, path + "[%d]" % i, loc_inherited, out)


def adapt(lit_dir):
    ex_dir = os.path.join(lit_dir, "extractions")
    files = sorted(glob.glob(os.path.join(ex_dir, "*.json")))
    records, manifest, excl, per_file = [], [], [], {}
    seen_src = set()
    for f in files:
        base = os.path.basename(f)
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            excl.append((base, "json_parse_error:%s" % e))
            continue
        eid = str(d.get("extraction_id", os.path.splitext(base)[0]))
        cite = _cite(d)
        leaves = []
        _walk(d, "", "", leaves)
        n = 0
        for jp, text, loc in leaves:
            source = "%s #%s" % (cite, jp)
            if source in seen_src:  # path is unique already; guard anyway
                continue
            seen_src.add(source)
            locator = "%s::%s" % (eid, jp) + ((" | " + loc) if loc else "")
            records.append({
                "claim_key": text,
                "source": source,
                "locator": locator,
                "finding": text,
            })
            manifest.append(_sha256(source))
            n += 1
        per_file[base] = n
        if n == 0:
            excl.append((base, "no_finding_leaf >= %d words" % MIN_WORDS))
    corpus = {"manifest_files": manifest, "records": records}
    return corpus, per_file, excl


def gate(corpus):
    """G2 structural gate (CONTENTS, not md5). Returns (ok, violations)."""
    v = []
    recs = corpus.get("records", [])
    mani = set(corpus.get("manifest_files", []))
    if len(recs) == 0:
        v.append("records == 0 (VOID-by-construction)")
    for i, r in enumerate(recs):
        if not str(r.get("source", "")).strip():
            v.append("rec[%d] empty source" % i)
        if not str(r.get("locator", "")).strip():
            v.append("rec[%d] empty locator" % i)
        if not str(r.get("finding", "")).strip():
            v.append("rec[%d] empty finding" % i)
        if not str(r.get("claim_key", "")).strip():
            v.append("rec[%d] missing claim_key" % i)
        h = _sha256(r["source"])
        if h not in mani:
            v.append("rec[%d] sha256(source) NOT in manifest_files" % i)
    # manifest must be exactly the per-record source hashes (no orphan/extra)
    rec_hashes = [_sha256(r["source"]) for r in recs]
    if sorted(mani) != sorted(set(rec_hashes)):
        v.append("manifest_files != set(sha256(source)) -- orphan/extra hash")
    return (len(v) == 0), v[:20]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lit", required=True, help="literature dir (contains extractions/)")
    ap.add_argument("--out", required=True, help="output corpus json path")
    ap.add_argument("--gate", action="store_true", help="run G2 gate, nonzero exit on fail")
    a = ap.parse_args()
    corpus, per_file, excl = adapt(a.lit)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(corpus, fh, ensure_ascii=False, indent=1)
    print("[adapt] files=%d  records=%d  manifest=%d  out=%s"
          % (len(per_file), len(corpus["records"]), len(corpus["manifest_files"]), a.out))
    print("[adapt] per-file finding counts:")
    for k in sorted(per_file):
        print("   %-44s %d" % (k, per_file[k]))
    if excl:
        print("[adapt] EXCLUSIONS (logged, not fabricated):")
        for b, why in excl:
            print("   %-44s %s" % (b, why))
    if a.gate:
        ok, viol = gate(corpus)
        print("[G2] %s" % ("GREEN" if ok else "RED"))
        for x in viol:
            print("   VIOL %s" % x)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
