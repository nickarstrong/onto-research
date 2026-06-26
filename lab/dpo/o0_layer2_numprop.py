#!/usr/bin/env python3
# o0_layer2_numprop.py -- v308 WIRED numprop verdict module (ADDITIVE, evolution-only).
# Composes Option B resolver (v305: P31 type-class + P279* closure K=8 + sitelink Delta=2x)
# with v303 property-floor read (fetch QID numeric prop, compare to claim value).
# P->domain map (p_domain_map_v308.json) derives expected_class from the claim's property.
# CIRCULARITY PROHIBITION (HARD): expected_class derived from P's DOMAIN (property-identity),
# NEVER P's VALUE. Subject resolved by entity-TYPE, not the target numeric value.
# FROZEN SEAMS UNTOUCHED: imports o0_temporal_probe_v5 for _get/wbsearch only (read-only).
# oracle 0e59ae0f, probe b231da36, verifier 92766b06 -- ZERO edit.
# ABSTAIN-PRESERVING: every branch not leading to a confident BIND+property-check -> ABSTAIN.
import json, os, re, sys, time
import o0_temporal_probe_v5 as T

# --- configuration (v304/v305/v306 floor) ---
K_DEPTH = 8          # P279* closure bound
DELTA = 2.0          # sitelink salience dominance margin
MAX_CANDS = 15       # wbsearch candidates inspected

CACHE_PATH = "numprop_wired_cache_v308.json"
MAP_PATH = os.path.join(os.path.dirname(__file__) or ".", "p_domain_map_v308.json")

# unit QID -> physical dimension (v303 lineage + extensions)
UNIT_DIM = {
    "Q11573": "length", "Q828224": "length",
    "Q11570": "mass", "Q25343": "area",
    "Q712226": "area", "Q35852": "area",
    "Q7727": "time", "Q11574": "time", "Q25235": "time",
    "1": "count",
}

_cache = {}
_domain_map = {}


def load_domain_map():
    global _domain_map
    with open(MAP_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    _domain_map = {k: v for k, v in raw.items() if k.startswith("P")}


def load_cache():
    global _cache
    _cache = json.load(open(CACHE_PATH, encoding="utf-8")) if os.path.exists(CACHE_PATH) else {}


def save_cache():
    with open(CACHE_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(_cache, f, ensure_ascii=False, sort_keys=True, indent=0)


# --- WD fetch (cached, hermetic) ---

def _cget(url):
    if url in _cache:
        return _cache[url]
    v = T._get(url)
    time.sleep(0.2)
    _cache[url] = v
    return v


def _csearch(subj):
    key = "search::" + subj
    if key in _cache:
        return _cache[key]
    v = T.wbsearch(subj)
    time.sleep(0.2)
    _cache[key] = v
    return v


def entity_json(qid):
    return _cget("https://www.wikidata.org/wiki/Special:EntityData/%s.json" % qid)


def _ent(data, qid):
    return data.get("entities", {}).get(qid, {}) if data else {}


def label_en(data, qid):
    return _ent(data, qid).get("labels", {}).get("en", {}).get("value", "")


def _claim_ids(data, qid, pid):
    out = []
    for cl in _ent(data, qid).get("claims", {}).get(pid, []):
        try:
            out.append(cl["mainsnak"]["datavalue"]["value"]["id"])
        except Exception:
            continue
    return out


def sitelink_count(data, qid):
    return len(_ent(data, qid).get("sitelinks", {}) or {})


# --- Option B resolver (v305 floor, composed read-only) ---

def reaches_class(start_qid, target_qid):
    """BFS up P279 from start_qid; True iff target_qid in closure, depth <= K_DEPTH."""
    if start_qid == target_qid:
        return True
    seen = {start_qid}
    frontier = [start_qid]
    for _ in range(K_DEPTH):
        nxt = []
        for q in frontier:
            d = entity_json(q)
            if d is None:
                continue
            for p in _claim_ids(d, q, "P279"):
                if p == target_qid:
                    return True
                if p not in seen:
                    seen.add(p)
                    nxt.append(p)
        if not nxt:
            break
        frontier = nxt
    return False


def type_consistent(cand_data, cand_qid, expected_class):
    for k in _claim_ids(cand_data, cand_qid, "P31"):
        if reaches_class(k, expected_class):
            return True
    return False


def resolve_optionB(subject_label, expected_class):
    """Option B disambiguator. Returns (qid, label_en) or (None, reason)."""
    cands = _csearch(subject_label)
    if not cands or isinstance(cands, dict):
        return None, "empty_candidate_set"
    qids = [c["id"] for c in cands][:MAX_CANDS]
    typed = []
    for qid in qids:
        d = entity_json(qid)
        if d is None:
            continue
        lbl = label_en(d, qid)
        sl = sitelink_count(d, qid)
        if type_consistent(d, qid, expected_class):
            typed.append((qid, sl, lbl))
    if len(typed) == 0:
        return None, "no_type_consistent"
    if len(typed) == 1:
        return typed[0][0], typed[0][2]
    typed.sort(key=lambda t: (t[1], t[0]), reverse=True)
    q1, sl1, l1 = typed[0]
    q2, sl2, l2 = typed[1]
    if sl1 >= DELTA * sl2:
        return q1, l1
    return None, "co_equal(%d,%d)" % (sl1, sl2)


# --- property-floor read (v303 lineage) ---

def _unit_qid(unit):
    if not unit or unit == "1":
        return "1"
    return unit.rstrip("/").split("/")[-1]


def read_wd_prop(data, qid, pid, expected_dim):
    """Read quantity value of pid from QID. Prefers preferred-rank claim (WD convention:
    most current/authoritative value has rank=preferred). Returns (amount_str, unit_qid, dim_ok)."""
    claims = _ent(data, qid).get("claims", {})
    entries = claims.get(pid, [])
    if not entries:
        return None, None, False
    # sort: preferred > normal > deprecated
    RANK_ORDER = {"preferred": 0, "normal": 1, "deprecated": 2}
    ranked = sorted(entries, key=lambda cl: RANK_ORDER.get(cl.get("rank", "normal"), 1))
    for cl in ranked:
        try:
            dv = cl["mainsnak"]["datavalue"]["value"]
            if not isinstance(dv, dict) or "amount" not in dv:
                continue
            uq = _unit_qid(dv.get("unit", "1"))
            dim = UNIT_DIM.get(uq)
            return dv["amount"], uq, (dim == expected_dim)
        except Exception:
            continue
    return None, None, False


# --- property extraction from claim text ---

_NUM_RE = re.compile(r"[\d,]+(?:\.\d+)?")


def extract_numbers(text):
    """Extract all numeric values from text as floats."""
    out = []
    for m in _NUM_RE.findall(text or ""):
        try:
            out.append(float(m.replace(",", "")))
        except ValueError:
            continue
    return out


def identify_property(claim_text):
    """Match claim text against P->domain map keywords. Returns (pid, map_entry) or (None, None)."""
    low = (claim_text or "").lower()
    for pid, entry in _domain_map.items():
        for kw in entry.get("keywords", []):
            if kw in low:
                return pid, entry
    return None, None


# --- numprop verdict (per-record) ---

def numprop_verdict(claim, topic, subjects, cache=None):
    """Main entry point for a single numprop record.
    Returns (verdict, detail_dict) where verdict in {REFUTE, CONFIRM, ABSTAIN}."""
    REFUTE, CONFIRM, ABSTAIN = "REFUTE", "CONFIRM", "ABSTAIN"
    detail = {"pid": None, "domain": None, "bind_qid": None, "bind_label": None,
              "wd_amount": None, "claim_numbers": [], "reason": ""}

    # 1. identify which numeric property the claim is about
    pid, pentry = identify_property(claim)
    if pid is None:
        detail["reason"] = "no_mapped_property"
        return ABSTAIN, detail
    detail["pid"] = pid
    detail["domain"] = pentry["domain_qid"]
    expected_dim = pentry.get("unit_dim", "")

    # 2. resolve subject via Option B with this property's domain
    # try each subject label (from the caller's extraction)
    bind_qid = None
    bind_label = ""
    for subj in subjects:
        qid, lbl = resolve_optionB(subj, pentry["domain_qid"])
        if qid is not None:
            bind_qid = qid
            bind_label = lbl
            break
    if bind_qid is None:
        detail["reason"] = "resolve_abstain"
        return ABSTAIN, detail
    detail["bind_qid"] = bind_qid
    detail["bind_label"] = bind_label

    # 3. read WD property value
    data = entity_json(bind_qid)
    if data is None:
        detail["reason"] = "entity_fetch_fail"
        return ABSTAIN, detail
    wd_amount_str, unit_qid, dim_ok = read_wd_prop(data, bind_qid, pid, expected_dim)
    if wd_amount_str is None:
        detail["reason"] = "no_%s_on_%s" % (pid, bind_qid)
        return ABSTAIN, detail
    if not dim_ok:
        detail["reason"] = "unit_dim_mismatch(%s)" % unit_qid
        return ABSTAIN, detail

    # parse WD amount
    try:
        wd_val = float(wd_amount_str.lstrip("+"))
    except (ValueError, AttributeError):
        detail["reason"] = "wd_amount_parse_fail"
        return ABSTAIN, detail
    detail["wd_amount"] = wd_val

    # 4. extract claim's numeric values and compare
    claim_nums = extract_numbers(claim)
    # filter out year-like values (1400-2100) to avoid confusion with the year leg
    claim_nums = [n for n in claim_nums if not (1400 <= n <= 2100 and n == int(n))]
    detail["claim_numbers"] = claim_nums

    if not claim_nums:
        detail["reason"] = "no_claim_numbers"
        return ABSTAIN, detail

    # comparison: does any claim number match WD value?
    # tolerance: for count/integer properties (atomic number, population) use exact or <=1% relative
    # for measurements (height, area, mass) use <=5% relative
    tol = 0.01 if expected_dim == "count" else 0.05
    matched = False
    contradicted = False
    for cn in claim_nums:
        if wd_val == 0 and cn == 0:
            matched = True
            continue
        if wd_val != 0:
            rel = abs(cn - wd_val) / abs(wd_val)
            if rel <= tol:
                matched = True
            elif abs(wd_val) > 0 and cn > 0 and rel > 0.10:
                # claim states a number in similar magnitude range -> likely about this property
                # check if it's plausibly the SAME quantity but wrong
                ratio_log = abs(cn / wd_val) if wd_val != 0 else 999
                if 0.01 < ratio_log < 100:  # same order of magnitude -> this IS about this property
                    contradicted = True

    if matched:
        detail["reason"] = "value_match"
        return CONFIRM, detail
    if contradicted:
        detail["reason"] = "value_mismatch"
        return REFUTE, detail

    detail["reason"] = "no_conclusive_match"
    return ABSTAIN, detail
