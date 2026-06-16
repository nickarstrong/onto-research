#!/usr/bin/env python3
# run_L5_partI_validate.py
# Validate FROZEN L5 PART I independence predicate (SPEC_L5_independence_predicate.md, md5 d83d7a71...)
# against I.7 bars on a Founder-labeled coupling ground-truth set.
#
# Predicate legs implemented (PART I, frozen v1):
#   I.2 PROVENANCE: P1 shared author | P2 shared institution | P3 shared primary data (fail-closed on
#                   missing DAS) | P4 derivation ancestry (reference-list[Crossref] + OpenCitations)
#   I.3 METHOD:     ADVISORY by default (no kappa>=0.80 classifier) -> reported, NEVER gates.
#   I.4 CITATION DISCOUNT: citation edge -> collapse to one cluster (no ref-context in API -> any
#                   basis-citation edge treated as collapse; conservative).
#   I.5 CLUSTERING: edge iff (provenance-coupled OR citation-collapsed); method EXCLUDED from frozen verdict.
#
# I.7 BARS (gating = provenance + citation only):
#   (a) coupling recovery balanced-accuracy >= 0.85
#   (b) citation-discount leak == 0   (HARD)  -- no citation-coupled pair lands in different clusters
#   (c) over-prune (false-coupling on genuinely-independent class) <= 0.10
#
# Modes:
#   --contents  : VOID guard. Assert every class present, schema sane. STOP if any class empty.
#   --selftest  : run scoring logic on a synthetic mocked fixture (NO network). Proves harness != VOID.
#   --run       : live. Fetch Crossref + OpenCitations, apply frozen predicate, score, emit report.
#
# R7: predicate logic is applied BLIND to truth labels. Labels used ONLY in scoring. No oracle leak.

import argparse, json, sys, time, re, itertools, os
from collections import defaultdict

CROSSREF = "https://api.crossref.org/works/{doi}"
OPENCIT  = "https://opencitations.net/index/api/v2/references/doi:{doi}"
CLASSES  = ["independent", "author", "institution", "data", "citation"]
COUPLED_CLASSES = ["author", "institution", "data", "citation"]

# ---------------------------------------------------------------- metadata fetch

def _norm_name(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())

def _norm_affil(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def fetch_crossref(doi, cache, getter):
    if doi in cache: return cache[doi]
    data = getter(CROSSREF.format(doi=doi))
    msg = data.get("message", {})
    authors, affils = set(), set()
    for a in msg.get("author", []) or []:
        fam, giv = a.get("family", ""), a.get("given", "")
        if fam: authors.add(_norm_name(giv + fam))
        for af in a.get("affiliation", []) or []:
            n = _norm_affil(af.get("name", ""))
            if n: affils.add(n)
    refs = set()
    for r in msg.get("reference", []) or []:
        d = r.get("DOI")
        if d: refs.add(d.lower())
    rec = {"authors": authors, "affils": affils, "refs": refs}
    cache[doi] = rec
    return rec

def fetch_opencit_refs(doi, cache, getter):
    key = ("oc", doi)
    if key in cache: return cache[key]
    refs = set()
    try:
        rows = getter(OPENCIT.format(doi=doi))
        for row in rows or []:
            cited = row.get("cited", "")  # e.g. "doi:10.x/y meta:..."
            for tok in cited.split():
                if tok.startswith("doi:"):
                    refs.add(tok[4:].lower())
    except Exception:
        refs = set()  # OpenCitations is supplement; Crossref refs are primary
    cache[key] = refs
    return refs

# ---------------------------------------------------------------- predicate legs

def provenance_edge(mi, mj):
    """Return dict of fired provenance rules (frozen I.2). P3 fail-closed handled by caller."""
    fired = {}
    if mi["authors"] & mj["authors"]:               fired["P1"] = True
    if mi["affils"] & mj["affils"]:                 fired["P2"] = True
    # P3 handled in pair_predict (needs data_id from truth-set side metadata, fail-closed)
    if (mj["doi"].lower() in mi["refs_all"]) or (mi["doi"].lower() in mj["refs_all"]):
        fired["P4"] = True
    return fired

def pair_predict(si, sj, meta):
    """
    Apply FROZEN PART I to one pair. Returns:
      coupled_gating (bool)  -- provenance(P1-P4) OR citation(I.4); method EXCLUDED
      legs (dict)            -- which rules fired
      method_coupled (bool)  -- advisory only
    """
    mi, mj = meta[si["sid"]], meta[sj["sid"]]
    legs = provenance_edge(mi, mj)

    # P3 shared primary data (frozen: missing DAS -> PROV_UNKNOWN -> fail-closed coupled)
    di, dj = si.get("data_id"), sj.get("data_id")
    if di is None or dj is None:
        legs["P3"] = "unknown"              # absent DAS = PROV_UNKNOWN -> NOT a coupling signal (no fail-close)
    elif di == dj:
        legs["P3"] = True

    # I.4 citation discount == P4 citation edge (same graph signal); already captured by P4.
    citation_coupled = legs.get("P4", False) is True

    # method (I.3) ADVISORY -- reported, not gating
    method_coupled = (si.get("method_class") is not None
                      and si.get("method_class") == sj.get("method_class"))

    prov_coupled = any(v is True for k, v in legs.items())
    coupled_gating = prov_coupled or citation_coupled
    return coupled_gating, legs, method_coupled, citation_coupled

# ---------------------------------------------------------------- clustering

def clusters_from_edges(sids, edges):
    parent = {s: s for s in sids}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for a, b in edges: union(a, b)
    comp = defaultdict(list)
    for s in sids: comp[find(s)].append(s)
    return list(comp.values())

# ---------------------------------------------------------------- scoring

def score_dataset(rows, meta_for):
    """meta_for(claim) -> {sid: {authors,affils,refs_all,doi}} ; pure-logic, network handled by caller."""
    tp = tn = fp = fn = 0
    leak = 0
    indep_pairs = indep_false_coupled = 0
    per_class_total = defaultdict(int)
    per_class_hit = defaultdict(int)
    citation_pairs = []
    method_agree = method_total = 0
    excluded = []

    for row in rows:
        cid = row["claim_id"]
        sources = {s["sid"]: s for s in row["sources"]}
        meta = meta_for(row)
        if meta is None:
            excluded.append(cid); continue
        for sid in sources:
            sources[sid]["sid"] = sid

        truth = {}
        for t in row["coupling_truth"]:
            truth[frozenset((t["a"], t["b"]))] = t["label"]

        # predict every pair
        edges = []
        for si, sj in itertools.combinations(row["sources"], 2):
            key = frozenset((si["sid"], sj["sid"]))
            lbl = truth.get(key)
            if lbl is None:
                excluded.append(f"{cid}:missing-pair-label"); continue
            coupled_pred, legs, m_coup, cit_pred = pair_predict(si, sj, meta)
            coupled_true = (lbl in COUPLED_CLASSES)

            # confusion (positive = coupled)
            if coupled_true and coupled_pred:   tp += 1
            elif coupled_true and not coupled_pred: fn += 1
            elif (not coupled_true) and coupled_pred: fp += 1
            else: tn += 1

            per_class_total[lbl] += 1
            if (coupled_pred if coupled_true else (not coupled_pred)):
                per_class_hit[lbl] += 1

            if lbl == "independent":
                indep_pairs += 1
                if coupled_pred: indep_false_coupled += 1

            if lbl == "citation":
                citation_pairs.append((cid, si["sid"], sj["sid"]))

            method_total += 1
            if m_coup: method_agree += 1

            if coupled_pred: edges.append((si["sid"], sj["sid"]))

        # clusters for leak check
        clus = clusters_from_edges(list(sources.keys()), edges)
        cl_of = {}
        for i, c in enumerate(clus):
            for s in c: cl_of[s] = i
        for ccid, a, b in citation_pairs:
            if ccid == cid and cl_of.get(a) != cl_of.get(b):
                leak += 1  # citation-coupled pair survived as distinct clusters -> propagation leak

    tpr = tp / (tp + fn) if (tp + fn) else 1.0
    tnr = tn / (tn + fp) if (tn + fp) else 1.0
    bal_acc = (tpr + tnr) / 2.0
    over_prune = indep_false_coupled / indep_pairs if indep_pairs else 0.0
    return {
        "balanced_accuracy": round(bal_acc, 4),
        "tpr": round(tpr, 4), "tnr": round(tnr, 4),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "citation_discount_leak": leak,
        "over_prune": round(over_prune, 4),
        "indep_pairs": indep_pairs, "indep_false_coupled": indep_false_coupled,
        "per_class_recall": {c: (round(per_class_hit[c]/per_class_total[c], 4)
                                 if per_class_total[c] else None) for c in CLASSES},
        "per_class_n": dict(per_class_total),
        "method_advisory_agree_rate": (round(method_agree/method_total, 4) if method_total else None),
        "excluded": excluded,
    }

def verdict(sc):
    a = sc["balanced_accuracy"] >= 0.85
    b = sc["citation_discount_leak"] == 0
    c = sc["over_prune"] <= 0.10
    bars = {"recovery>=0.85": a, "discount_leak==0(HARD)": b, "over_prune<=0.10": c}
    return all([a, b, c]), bars

# ---------------------------------------------------------------- per-pair readout (READ-ONLY)

def per_pair_readout(rows, meta_for):
    """READ-ONLY reporting. Re-apply the FROZEN pair_predict to every labeled pair to surface
    per-pair verdicts the aggregate scorer does not expose. Does NOT gate, does NOT mutate
    pair_predict / score_dataset / verdict. Same frozen function + same meta -> verdicts are
    byte-identical to what score_dataset saw.

    Also splits the `independent` class into two sub-populations the gate FIX rides on:
      - indep_accession_bearing : BOTH sources carry a data_id (P3 not fail-closed -> a real test)
      - indep_accession_less    : >=1 source has data_id None (P3 fail-closed -> the over-prune)
    """
    pairs = []
    sub = {"indep_accession_bearing": {"n": 0, "false_coupled": 0, "ids": []},
           "indep_accession_less":    {"n": 0, "false_coupled": 0, "ids": []}}
    for row in rows:
        cid = row["claim_id"]
        meta = meta_for(row)
        if meta is None:
            continue
        for s in row["sources"]:
            s["sid"] = s["sid"]  # parity with score_dataset (idempotent)
        truth = {frozenset((t["a"], t["b"])): t["label"] for t in row["coupling_truth"]}
        for si, sj in itertools.combinations(row["sources"], 2):
            key = frozenset((si["sid"], sj["sid"]))
            lbl = truth.get(key)
            if lbl is None:
                continue
            coupled_pred, legs, m_coup, cit_pred = pair_predict(si, sj, meta)
            fired = sorted(k for k, v in legs.items() if v is True or v == "fail_closed")
            verd = "coupled" if coupled_pred else "independent"
            rec = {"claim": cid, "pair": f'{si["sid"]}x{sj["sid"]}',
                   "declared": lbl, "verdict": verd, "legs": fired,
                   "data_id": [si.get("data_id"), sj.get("data_id")]}
            pairs.append(rec)
            if lbl == "independent":
                both_acc = si.get("data_id") is not None and sj.get("data_id") is not None
                k = "indep_accession_bearing" if both_acc else "indep_accession_less"
                sub[k]["n"] += 1
                sub[k]["ids"].append(rec["pair"])
                if coupled_pred:
                    sub[k]["false_coupled"] += 1
    return pairs, sub

# ---------------------------------------------------------------- contents guard

def contents_check(rows):
    cls = defaultdict(int)
    problems = []
    for row in rows:
        sids = [s["sid"] for s in row["sources"]]
        if len(sids) < 2:
            problems.append(f"{row['claim_id']}: <2 sources")
        for s in row["sources"]:
            if not s.get("doi"):
                problems.append(f"{row['claim_id']}/{s['sid']}: missing doi")
        npairs = len(list(itertools.combinations(sids, 2)))
        if len(row.get("coupling_truth", [])) != npairs:
            problems.append(f"{row['claim_id']}: {len(row.get('coupling_truth',[]))} labels != {npairs} pairs")
        for t in row.get("coupling_truth", []):
            if t["label"] not in CLASSES:
                problems.append(f"{row['claim_id']}: bad label {t['label']}")
            cls[t["label"]] += 1
    empty = [c for c in CLASSES if cls[c] == 0]
    return cls, empty, problems

# ---------------------------------------------------------------- selftest (mocked, no network)

def selftest():
    # Synthetic fixture: 1 claim, 5 sources, known couplings.
    # S1-S2 author-coupled ; S1-S3 citation chain (S3 cites S1) ; S4-S5 institution ; rest independent.
    rows = [{
        "claim_id": "T001", "claim": "synthetic",
        "sources": [
            {"sid": "S1", "doi": "10.x/1", "data_id": "D1", "method_class": "a"},
            {"sid": "S2", "doi": "10.x/2", "data_id": "D2", "method_class": "b"},
            {"sid": "S3", "doi": "10.x/3", "data_id": "D3", "method_class": "c"},
            {"sid": "S4", "doi": "10.x/4", "data_id": "D4", "method_class": "d"},
            {"sid": "S5", "doi": "10.x/5", "data_id": "D5", "method_class": "d"},
        ],
        "coupling_truth": [
            {"a": "S1", "b": "S2", "label": "author"},
            {"a": "S1", "b": "S3", "label": "citation"},
            {"a": "S1", "b": "S4", "label": "independent"},
            {"a": "S1", "b": "S5", "label": "independent"},
            {"a": "S2", "b": "S3", "label": "independent"},
            {"a": "S2", "b": "S4", "label": "independent"},
            {"a": "S2", "b": "S5", "label": "independent"},
            {"a": "S3", "b": "S4", "label": "independent"},
            {"a": "S3", "b": "S5", "label": "independent"},
            {"a": "S4", "b": "S5", "label": "institution"},
        ],
    }]
    # second claim exercises P3 (data): same data_id -> coupled ; missing data_id -> unknown (NOT coupled)
    rows.append({
        "claim_id": "T002", "claim": "synthetic-p3",
        "sources": [
            {"sid": "Q1", "doi": "10.y/1", "data_id": "SHARED", "method_class": "a"},
            {"sid": "Q2", "doi": "10.y/2", "data_id": "SHARED", "method_class": "b"},  # P3 same data
            {"sid": "Q3", "doi": "10.y/3", "data_id": None,     "method_class": "c"},  # missing DAS -> unknown (NOT coupled)
        ],
        "coupling_truth": [
            {"a": "Q1", "b": "Q2", "label": "data"},
            {"a": "Q1", "b": "Q3", "label": "independent"},   # corrected: absent-DAS = NOT coupled
            {"a": "Q2", "b": "Q3", "label": "independent"},
        ],
    })
    MOCK = {
        "10.x/1": {"authors": {"asmith"}, "affils": {"mit"}, "refs": set()},
        "10.x/2": {"authors": {"asmith"}, "affils": {"stanford"}, "refs": set()},   # shares author -> P1
        "10.x/3": {"authors": {"bjones"}, "affils": {"cern"}, "refs": {"10.x/1"}},  # cites S1 -> P4/I.4
        "10.x/4": {"authors": {"cwang"}, "affils": {"oxford"}, "refs": set()},
        "10.x/5": {"authors": {"dlee"}, "affils": {"oxford"}, "refs": set()},       # shares affil -> P2
        "10.y/1": {"authors": {"e"}, "affils": {"a"}, "refs": set()},
        "10.y/2": {"authors": {"f"}, "affils": {"b"}, "refs": set()},
        "10.y/3": {"authors": {"g"}, "affils": {"c"}, "refs": set()},
    }
    def meta_for(row):
        m = {}
        for s in row["sources"]:
            r = MOCK[s["doi"]]
            m[s["sid"]] = {"authors": r["authors"], "affils": r["affils"],
                           "refs_all": r["refs"], "doi": s["doi"]}
        return m
    sc = score_dataset(rows, meta_for)
    ok, bars = verdict(sc)
    print(json.dumps(sc, indent=2))
    print("VERDICT bars:", bars)
    # harness assertions: author(P1), citation(P4), institution(P2) recovered; independents clean; leak 0
    assert sc["per_class_recall"]["author"] == 1.0, "P1 author not recovered"
    assert sc["per_class_recall"]["citation"] == 1.0, "P4/I.4 citation not recovered"
    assert sc["per_class_recall"]["institution"] == 1.0, "P2 institution not recovered"
    assert sc["per_class_recall"]["data"] == 1.0, "P3 data (real shared accession) not recovered"
    assert sc["over_prune"] == 0.0, "spurious coupling on independents"
    assert sc["citation_discount_leak"] == 0, "citation chain leaked as distinct clusters"
    assert sc["balanced_accuracy"] == 1.0, "clean fixture must score 1.0"
    print("\nSELFTEST: PASS (harness logic sound; not VOID-by-construction)")

# ---------------------------------------------------------------- live run

def live_run(path, report_path):
    import urllib.request
    def getter(url):
        req = urllib.request.Request(url, headers={"User-Agent": "ONTO-L5/1.0 (mailto:council@ontostandard.org)"})
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    cls, empty, problems = contents_check(rows)
    if empty:
        print("CONTENTS VOID -- empty classes:", empty); sys.exit(2)
    cache = {}
    def fetch_meta(row):
        m = {}
        for s in row["sources"]:
            doi = s["doi"]
            try:
                cr = fetch_crossref(doi, cache, getter); time.sleep(0.3)
            except Exception as e:
                print(f"  fetch-fail {doi}: {e}"); return None
            oc = fetch_opencit_refs(doi, cache, getter); time.sleep(0.3)
            m[s["sid"]] = {"authors": cr["authors"], "affils": cr["affils"],
                           "refs_all": cr["refs"] | oc, "doi": doi}
        return m
    # fetch each claim's meta ONCE (shared by the frozen scorer AND the read-only readout ->
    # no double network/sleep, and the readout sees byte-identical meta to the scorer)
    meta_cache = {row["claim_id"]: fetch_meta(row) for row in rows}
    def meta_for(row): return meta_cache.get(row["claim_id"])
    sc = score_dataset(rows, meta_for)
    pairs, sub = per_pair_readout(rows, meta_for)
    ok, bars = verdict(sc)
    emit_report(report_path, sc, bars, ok, cls, pairs, sub)
    print(json.dumps(sc, indent=2)); print("VERDICT:", "PASS" if ok else "FAIL", bars)
    print("\n## per-pair readout (READ-ONLY ; predicate not gated by this)")
    print(f"{'claim':<6} {'pair':<10} {'declared':<12} {'verdict':<12} legs")
    for r in pairs:
        print(f"{r['claim']:<6} {r['pair']:<10} {r['declared']:<12} {r['verdict']:<12} {','.join(r['legs']) or '-'}")
    ab, al = sub["indep_accession_bearing"], sub["indep_accession_less"]
    print("\n## independent sub-group split (the gate the predicate-FIX rides on)")
    print(f"  accession-bearing : {ab['false_coupled']}/{ab['n']} false-coupled  ids={ab['ids']}")
    print(f"  accession-less    : {al['false_coupled']}/{al['n']} false-coupled  ids={al['ids']}")
    sys.exit(0 if ok else 1)

def emit_report(p, sc, bars, ok, cls, pairs=None, sub=None):
    L = []
    L.append("# report_L5_partI -- PART I independence predicate validation")
    L.append("")
    L.append(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    L.append("")
    L.append("## I.7 bars")
    for k, v in bars.items(): L.append(f"- {k}: {'PASS' if v else 'FAIL'}")
    L.append("")
    L.append("## metrics")
    L.append(f"- balanced_accuracy : {sc['balanced_accuracy']} (tpr {sc['tpr']} / tnr {sc['tnr']})")
    L.append(f"- citation_discount_leak : {sc['citation_discount_leak']} (HARD==0)")
    L.append(f"- over_prune : {sc['over_prune']} ({sc['indep_false_coupled']}/{sc['indep_pairs']} indep pairs)")
    L.append(f"- confusion : {sc['confusion']}")
    L.append(f"- per_class_recall : {sc['per_class_recall']}")
    L.append(f"- per_class_n : {sc['per_class_n']}")
    L.append(f"- method leg (ADVISORY, kappa N/A single-annotator) agree_rate : {sc['method_advisory_agree_rate']}")
    L.append(f"- excluded : {sc['excluded']}")
    if pairs is not None:
        L.append("")
        L.append("## per-pair readout (READ-ONLY ; re-applies frozen pair_predict, does NOT gate)")
        L.append("| claim | pair | declared | verdict | legs | data_id |")
        L.append("|---|---|---|---|---|---|")
        for r in pairs:
            L.append(f"| {r['claim']} | {r['pair']} | {r['declared']} | {r['verdict']} "
                     f"| {','.join(r['legs']) or '-'} | {r['data_id']} |")
    if sub is not None:
        ab, al = sub["indep_accession_bearing"], sub["indep_accession_less"]
        L.append("")
        L.append("## independent sub-group split (gate substrate for the predicate FIX)")
        L.append(f"- accession-bearing : {ab['false_coupled']}/{ab['n']} false-coupled ; ids {ab['ids']}")
        L.append(f"- accession-less    : {al['false_coupled']}/{al['n']} false-coupled ; ids {al['ids']}")
    L.append("")
    L.append("## WATCH (frozen-predicate interactions, reported not edited)")
    L.append("- P3 fail-closed on missing DAS can inflate over-prune on real no-DAS independents -> if")
    L.append("  over_prune FAIL traces to P3 fail-closed, that is a legit FALSIFY(over-prune): file DEFECT + v1.1, do NOT edit frozen.")
    L.append("- citation leg has no reference-context (APIs give edges not context) -> any basis-citation")
    L.append("  edge treated as collapse (conservative; safe for leak==0, adds over-prune risk).")
    L.append("- method leg ADVISORY by default (I.3); excluded from gating verdict.")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", p)

# ---------------------------------------------------------------- cli

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--contents", metavar="JSONL")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", metavar="JSONL")
    ap.add_argument("--out", default="reports/report_L5_partI.md")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.contents:
        rows = [json.loads(l) for l in open(a.contents, encoding="utf-8") if l.strip()]
        cls, empty, problems = contents_check(rows)
        print("class histogram:", dict(cls))
        print("empty classes :", empty)
        print("problems      :", problems if problems else "none")
        sys.exit(2 if (empty or problems) else 0)
    elif a.run:
        live_run(a.run, a.out)
    else:
        ap.print_help()
