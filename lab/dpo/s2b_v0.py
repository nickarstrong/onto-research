#!/usr/bin/env python3
# s2b_v0.py -- ONTO automated supports-judge, S2(b) v0. Built against FROZEN SPEC_s2b_v0.md (md5 80bdf2a9).
# PUBLIC-SAFE: contains NO dois, claim-texts, or abstracts. Bait-class data is read from LOCAL files only.
#
# Contract (SPEC): INPUT {claim_text, doi, (opt) star_quote} -> fetch Crossref -> B1 binding (deterministic,
# grounded ; runs first) -> B2 supports (SEPARATE non-proposing grounded model instance ; survivors only)
# -> verdict in {SUPPORTS, NOT, UNCLEAR} + leg + reason-code + fetched snapshot. READ-ONLY. O(citations).
# Getter is MIRRORED from the documented fetch_crossref behavior (run_L5_partI_validate not imported).
#
# BARS (SPEC §7, frozen): G1 zero J2->SUPPORTS (HARD) ; G2 zero J3->SUPPORTS (HARD) ;
#                         G3 zero J1->NOT (HARD, no-castration) ; G4 J4->UNCLEAR (honesty).
#
# Modes:
#   --selftest            fake getter (LOCAL ground json) + B2 ; asserts G1-G4 vs planted expect. No Crossref.
#   --selftest --det-only stub B2 ; asserts only the DETERMINISTIC guarantees (G1 via B1 ; G4 via empty-abstract
#                         short-circuit ; B1 does NOT fire on correct-cite J1/J3/J4). No model, no network.
#   --netcheck            one live Crossref fetch of a fixed control doi ; prints metadata. Proves getter.
#   --run INPUT.jsonl     live fetch per item -> B1 -> B2 -> write OUTPUT.jsonl + summary.
#
# expect labels feed ONLY the falsifier check, NEVER the judge (no oracle leak).

import sys, os, json, re, time, argparse, hashlib, urllib.request, urllib.error, urllib.parse

LOCKED_FALSIFIER_MD5 = "8307d97d541f06780763137edbbd4d9c"   # frozen before this file's first predicate byte
MAILTO  = "council@ontostandard.org"
B2_MODEL_DEFAULT = "claude-sonnet-4-6"
CONTROL_DOI = "10.7554/eLife.00065"   # known abstract-present record, for --netcheck only

# ---------- util ----------
def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def strip_jats(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()

def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).strip()

def tokens(s):
    return set(t for t in norm(s).split() if len(t) > 2)

def strip_accents(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c))

# ---------- Step A : retrieval (MIRRORED getter) ----------
def _reconstruct_inverted_index(inv):
    # OpenAlex stores abstracts as {word: [positions...]} ; rebuild linear text.
    if not inv:
        return ""
    pairs = []
    for word, idxs in inv.items():
        for i in idxs:
            pairs.append((i, word))
    pairs.sort(key=lambda p: p[0])
    return " ".join(w for _, w in pairs)

def fetch_openalex_abstract(doi, mailto=MAILTO, timeout=25):
    # Abstract-only fallback from a VERIFIED third-party source (not model self-report).
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/.") + "?mailto=" + mailto
    req = urllib.request.Request(url, headers={"User-Agent": "onto-s2b/0.0 (mailto:%s)" % mailto})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.load(r)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError):
        return ""
    return _reconstruct_inverted_index(body.get("abstract_inverted_index"))

def fetch_crossref(doi, mailto=MAILTO, timeout=25):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/.") + "?mailto=" + mailto
    req = urllib.request.Request(url, headers={"User-Agent": "onto-s2b/0.0 (mailto:%s)" % mailto})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.load(r)
    m = body["message"]
    issued = m.get("issued", {}).get("date-parts", [[None]])
    year = issued[0][0] if issued and issued[0] else None
    authors = [a.get("family", "") for a in (m.get("author") or []) if a.get("family")]
    cont = m.get("container-title") or [""]
    abstract = strip_jats(m.get("abstract", ""))
    if not abstract:
        # Crossref empty -> OpenAlex abstract fallback. Crossref STAYS primary for
        # title/venue/year/authors/retraction ; OpenAlex supplies abstract ONLY.
        abstract = strip_jats(fetch_openalex_abstract(doi, mailto=mailto, timeout=timeout))
    return {
        "doi": doi,
        "title": (m.get("title") or [""])[0],
        "venue": cont[0] if cont else "",
        "year": year,
        "author_surnames": authors,
        "abstract": abstract,
    }

# ---------- B1 : binding (deterministic, grounded) ----------
CITE_RE = re.compile(
    r"([A-Z][A-Za-z\u00C0-\u024F'\-]+)"            # first cited surname
    r"(?:\s+et al\.?| and [A-Z][A-Za-z\u00C0-\u024F'\-]+)?"
    r"\s*\((\d{4}),\s*([^)]+)\)"                    # (YEAR, Venue)
)

def parse_citation(claim_text, star_quote=None):
    src = claim_text if claim_text else ""
    m = CITE_RE.search(src)
    if not m and star_quote:
        m = CITE_RE.search(star_quote)
    if not m:
        return None
    return {"surname": m.group(1), "year": int(m.group(2)), "venue": m.group(3).strip()}

# B1 fallback: prose citations ("Jinek et al. 2012") carry no (YYYY, Venue).
# The 4-digit YEAR is the one reliable binding signal -- no author/initials/venue
# matching here (L5 P1: false-fires on common names). Fire only on an UNAMBIGUOUS
# single year ; multiple distinct years in a source -> abstain (never fire on ambiguity).
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")

def parse_year_only(claim_text, star_quote=None):
    for src in (star_quote, claim_text):     # star_quote first, else claim_text (SPEC priority)
        if not src:
            continue
        yrs = sorted(set(int(y) for y in YEAR_RE.findall(src)))
        if len(yrs) == 1:
            return yrs[0]
        if yrs:                              # >1 distinct year here -> ambiguous, abstain
            return None
    return None

def venue_compatible(cited, container):
    c, k = norm(cited), norm(container)
    if not c or not k:
        return True                       # absence is not a contradiction (SPEC: never fire on absence)
    if c in k or k in c:
        return True
    # acronym either direction (PNAS <-> Proceedings of the National Academy of Sciences)
    def acro(s): return "".join(w[0] for w in s.split() if len(w) > 2)
    if c.replace(" ", "") == acro(k) or k.replace(" ", "") == acro(c):
        return True
    a, b = tokens(cited), tokens(container)
    if a and b:
        jacc = len(a & b) / len(a | b)
        if jacc >= 0.34:
            return True
    return False                          # genuinely disjoint named venues -> contradiction

def b1_binding(claim_text, star_quote, meta):
    cit = parse_citation(claim_text, star_quote)
    if not cit:
        cy = parse_year_only(claim_text, star_quote)     # prose-cite fallback: year-only signal
        fy = meta.get("year")
        if cy is not None and fy is not None and abs(cy - fy) > 1:
            return "NOT", "wrong_binding_year", {"cited_year": cy, "fetched_year": fy}
        return None, "binding_inapplicable", {}     # no parseable named source -> route to B2
    fetched_auth = {strip_accents(a).lower() for a in meta.get("author_surnames", [])}
    cited_auth = strip_accents(cit["surname"]).lower()
    author_miss = bool(fetched_auth) and cited_auth not in fetched_auth
    fy = meta.get("year")
    year_miss = (fy is not None) and (abs(cit["year"] - fy) > 1)
    venue_miss = not venue_compatible(cit["venue"], meta.get("venue", ""))
    signals = {"author_miss": author_miss, "year_miss": year_miss, "venue_miss": venue_miss,
               "cited": cit}
    if author_miss or year_miss or venue_miss:
        return "NOT", "wrong_binding", signals       # HARD miss -> cited source != fetched DOI's source
    return None, "binding_ok", signals               # bound -> route to B2

# ---------- B2 : supports (grounded, separate non-proposing model instance) ----------
B2_SYS = (
    "You are a grounded scientific-claims verifier. You did NOT write the claim and are not its author. "
    "Read ONLY the provided source title and abstract. Decide whether that source SUPPORTS the claim, "
    "using ONLY information present in the title/abstract -- never outside knowledge. "
    "If the abstract is missing or too thin to adjudicate the claim, answer UNCLEAR. "
    "Reply with exactly one token: SUPPORTS, NOT, or UNCLEAR."
)

def b2_call_api(claim_text, title, abstract, model):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set (B2 needs the grounded model instance)")
    payload = {
        "model": model, "max_tokens": 8, "system": B2_SYS,
        "messages": [{"role": "user", "content":
            "CLAIM:\n%s\n\nSOURCE TITLE:\n%s\n\nSOURCE ABSTRACT:\n%s\n\nVerdict (one token):"
            % (claim_text, title or "(none)", abstract or "(none)")}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return text.strip().upper()

_LOCAL = {}   # cache: model_id -> (tokenizer, model)

def b2_local_factory(model_id):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    if model_id not in _LOCAL:
        tok = AutoTokenizer.from_pretrained(model_id)
        kw = {"torch_dtype": "auto", "device_map": "auto", "low_cpu_mem_usage": True}
        if not os.environ.get("S2B_NO_4BIT"):     # opt-out: skip bnb (broken DLL on new CUDA) -> fp16 offload
            try:
                from transformers import BitsAndBytesConfig
                kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16, bnb_4bit_quant_type="nf4")
            except Exception:
                pass
        mdl = AutoModelForCausalLM.from_pretrained(model_id, **kw)
        _LOCAL[model_id] = (tok, mdl)
    tok, mdl = _LOCAL[model_id]

    def call(claim_text, title, abstract, model):
        msgs = [{"role": "system", "content": B2_SYS},
                {"role": "user", "content":
                    "CLAIM:\n%s\n\nSOURCE TITLE:\n%s\n\nSOURCE ABSTRACT:\n%s\n\nVerdict (one token):"
                    % (claim_text, title or "(none)", abstract or "(none)")}]
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                      return_tensors="pt", return_dict=True)
        enc = {k: v.to(mdl.device) for k, v in enc.items()}
        out = mdl.generate(**enc, max_new_tokens=6, do_sample=False,
                           pad_token_id=tok.eos_token_id)
        gen = out[0][enc["input_ids"].shape[1]:]
        return tok.decode(gen, skip_special_tokens=True).strip().upper()
    return call

def select_b2(backend, model_id):
    if backend == "api":
        return b2_call_api
    if backend == "local":
        return b2_local_factory(model_id)
    raise ValueError("unknown b2 backend: %s" % backend)

# ---------- B2 off-topic predicate (GATE_s2b_offtopic_v0 sec 1 ; deterministic, no LLM) ----------
# OFF-TOPIC(claim, fetched) := TRUE iff BOTH
#   (a) the claim's subject token-set has ZERO overlap with title+abstract ; AND
#   (b) title+abstract carry their own non-thin subject (>= OFFTOPIC_ABS_MIN_TOKENS content tokens).
# NO synonym/hypernym expansion (none in-repo ; a hardcoded map keyed to the known J5 would be
# tuning-to-pass, R7). Raw token-set overlap is the CONSERVATIVE proxy: it can only FALSE-FIRE
# more, never less, so G5 (0/CC -> NOT) is the honest approach-falsifier. Precision-first:
# under-catch (off-topic missed) -> honest UNCLEAR ; over-catch (correct cite -> NOT) -> castration.
OFFTOPIC_ABS_MIN_TOKENS = 8

# Fixed, DOMAIN-AGNOSTIC English function-word set (articles/conjunctions/prepositions/auxiliaries/
# pronouns). NOT derived from any J5 term -- never extend with content words (that is tuning, R7).
# Gate sec 1 keys (a) on the claim's PRIMARY SUBJECT tokens ("defining entity / measured quantity /
# named mechanism") -- function words are never subject ; counting them as overlap under-implements sec 1.
STOPWORDS = frozenset((
    "the and but for with from that this these those they them their there here whom whose which what "
    "when where how than then also into via within during after before over under above below between "
    "among such been being are was were has have had not can will may might must should would could "
    "its his her our your you its it is be of to in on at by as or an a no nor so yet do does did done "
    "using used based both each more most some any all only other another about against both because "
    "while whether either neither per via due across along around upon onto off out up down very much"
).split())

def subj_tokens(s):
    return tokens(s) - STOPWORDS                      # gate sec 1: subject tokens, function words removed

def off_topic(claim_text, meta):
    ctoks = subj_tokens(claim_text)
    if not ctoks:
        return False                                  # no claim subject to test -> not off-topic
    abs_toks = subj_tokens(meta.get("abstract", ""))
    surface = abs_toks | subj_tokens(meta.get("title", ""))
    if ctoks & surface:
        return False                                  # (a) fails: shared subject token -> on-topic surface
    if len(abs_toks) < OFFTOPIC_ABS_MIN_TOKENS:
        return False                                  # (b) fails: thin abstract, no own subject -> protect CC-terse
    return True                                       # (a) & (b) hold -> off-topic

def b2_supports(claim_text, meta, model, b2_fn):
    abstract = (meta.get("abstract") or "").strip()
    if not abstract:
        return "UNCLEAR", "no_abstract", None         # deterministic honesty short-circuit (G4)
    if off_topic(claim_text, meta):
        return "NOT", "off_topic", None               # GATE sec 1 ; deterministic, before model verdict
    raw = b2_fn(claim_text, meta.get("title", ""), abstract, model)
    if "SUPPORTS" in raw:
        return "SUPPORTS", "b2_supports", raw
    if "UNCLEAR" in raw:
        return "UNCLEAR", "b2_unclear", raw
    if "NOT" in raw:
        return "NOT", "b2_not", raw
    return "UNCLEAR", "b2_unparseable", raw

# ---------- judge one item ----------
def judge(item, getter, model, b2_fn):
    doi = item["doi"]
    meta = getter(doi)
    rec = {"doi": doi, "claim_text": item.get("claim_text", ""),
           "fetched": {"title": meta.get("title", ""), "venue": meta.get("venue", ""),
                       "year": meta.get("year"), "authors": meta.get("author_surnames", []),
                       "abstract_present": bool((meta.get("abstract") or "").strip()),
                       "abstract_len": len((meta.get("abstract") or "").strip())}}
    if "id" in item:
        rec["id"] = item["id"]
    v, reason, sig = b1_binding(item.get("claim_text", ""), item.get("star_quote"), meta)
    if v == "NOT":
        rec.update({"verdict": "NOT", "leg": "binding", "reason": reason})
        return rec
    v2, reason2, raw = b2_supports(item.get("claim_text", ""), meta, model, b2_fn)
    rec.update({"verdict": v2, "leg": "supports", "reason": reason2})
    return rec

# ---------- falsifier loading + ground fake getter ----------
def load_falsifier(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

def make_fake_getter(ground_path):
    g = {r["doi"]: r for r in json.load(open(ground_path, encoding="utf-8"))}
    def getter(doi):
        r = g.get(doi)
        if not r or not r.get("resolves"):
            raise RuntimeError("fake getter: doi not in local ground: %s" % doi)
        return {"doi": doi, "title": r.get("title", ""), "venue": r.get("venue", ""),
                "year": r.get("year"), "author_surnames": r.get("author_surnames", []),
                "abstract": r.get("abstract", "")}
    return getter

# ---------- bars ----------
def check_bars(items, records):
    by_id = {r.get("id"): r for r in records}
    fails = []
    for it in items:
        r = by_id.get(it["id"]); v = r["verdict"]; c = it["class"]
        if c == "J2" and v == "SUPPORTS": fails.append(("G1", it["id"], "J2 returned SUPPORTS"))
        if c == "J3" and v == "SUPPORTS": fails.append(("G2", it["id"], "J3 returned SUPPORTS"))
        if c == "J1" and v == "NOT":      fails.append(("G3", it["id"], "J1 returned NOT"))
        if c == "J4" and v != "UNCLEAR":  fails.append(("G4", it["id"], "J4 returned %s" % v))
    return fails

# ---------- G5 : off-topic no-castration bar (GATE sec 3 ; deterministic, no model/network) ----------
# G5 (HARD, tol 0): ZERO CC correct-cites may yield off_topic -> NOT (castration).
# J5 recall = DIAGNOSTIC readout, never a bar. Tests ONLY the predicate the policy ADDED
# (off_topic), via fake getter -- no model verdict, no live fetch (R7: results never move the bar).
def run_g5(cc_path, j5_path, ground_path):
    getter = make_fake_getter(ground_path)
    cc = load_falsifier(cc_path)
    j5 = load_falsifier(j5_path)
    g5_fails, b1_on_cc, cc_rows = [], [], []
    for it in cc:
        meta = getter(it["doi"])
        ct = it.get("claim_text", "")
        v1, r1, _ = b1_binding(ct, it.get("star_quote"), meta)
        if v1 == "NOT":
            b1_on_cc.append((it["id"], r1))            # CC bound-wrong = labeling/B1 flag, not the policy
        ot = off_topic(ct, meta)
        if ot:
            g5_fails.append(it["id"])                  # correct cite -> off_topic NOT = castration
        cc_rows.append((it["id"], it.get("class", ""), "OFF_TOPIC->NOT" if ot else "ok"))
    j5_caught, j5_rows = [], []
    for it in j5:
        meta = getter(it["doi"])
        ot = off_topic(it.get("claim_text", ""), meta)
        if ot:
            j5_caught.append(it["id"])
        j5_rows.append((it["id"], it.get("class", ""), "caught(NOT)" if ot else "missed(UNCLEAR)"))
    return {"g5_fails": g5_fails, "b1_on_cc": b1_on_cc, "cc_rows": cc_rows,
            "j5_caught": j5_caught, "j5_rows": j5_rows, "n_cc": len(cc), "n_j5": len(j5)}

def _emit_g5(args):
    # Runs the G5 block if the CC/J5/ground fixtures are present. Returns process exit code:
    # 0 = G5 PASS or fixtures absent (G6-only run) ; 1 = G5 FAIL (any CC -> off_topic).
    import os.path as _p
    if not (_p.exists(args.cc) and _p.exists(args.j5) and _p.exists(args.cc_ground)):
        print("G5 SKIPPED: CC/J5/ground fixtures not present (G1-G4=G6 only). "
              "supply --cc/--j5/--cc-ground (LOCAL-ONLY) to prove G5.")
        return 0
    r = run_g5(args.cc, args.j5, args.cc_ground)
    for cid, cls, status in r["cc_rows"]:
        print("  CC %-7s %-11s %s" % (cid, cls, status))
    if r["b1_on_cc"]:
        print("  WARN B1 fired NOT on CC (labeling/B1, not the policy):", r["b1_on_cc"])
    print("  J5 recall (DIAGNOSTIC, not a bar): %d/%d caught -> %s"
          % (len(r["j5_caught"]), r["n_j5"], r["j5_caught"]))
    for jid, cls, status in r["j5_rows"]:
        print("  J5 %-7s %-4s %s" % (jid, cls, status))
    if r["g5_fails"]:
        print("G5 FAIL (HARD, tol 0): %d/%d CC correct-cites flipped to off_topic->NOT = castration: %s"
              % (len(r["g5_fails"]), r["n_cc"], r["g5_fails"]))
        print("POLICY REJECTED at abstract level (defer full-text, SPEC sec 8). Predicate NOT tuned to pass (R7).")
        return 1
    print("G5 PASS (HARD, tol 0): 0/%d CC -> NOT. No castration. Off-topic policy is BUILDABLE+VALID at abstract level."
          % r["n_cc"])
    return 0

# ---------- modes ----------
def mode_selftest(args):
    fpath = args.falsifier
    if md5_file(fpath) != LOCKED_FALSIFIER_MD5:
        print("STARTUP GUARD FAIL: falsifier md5 != locked %s" % LOCKED_FALSIFIER_MD5); return 2
    print("startup md5-guard OK (falsifier == %s)" % LOCKED_FALSIFIER_MD5)
    items = load_falsifier(fpath)
    getter = make_fake_getter(args.ground)
    if args.det_only:
        b2_fn = lambda *a, **k: (_ for _ in ()).throw(AssertionError("B2 called in --det-only"))
    else:
        b2_fn = select_b2(args.b2, args.model)
    recs = []
    for it in items:
        if args.det_only:
            # exercise B1 + empty-abstract short-circuit only ; if it would reach the model, record ROUTE
            meta = getter(it["doi"])
            v, reason, sig = b1_binding(it.get("claim_text", ""), it.get("star_quote"), meta)
            if v == "NOT":
                recs.append({"id": it["id"], "verdict": "NOT", "leg": "binding", "reason": reason})
            elif not (meta.get("abstract") or "").strip():
                recs.append({"id": it["id"], "verdict": "UNCLEAR", "leg": "supports", "reason": "no_abstract"})
            else:
                recs.append({"id": it["id"], "verdict": "ROUTE_B2", "leg": "supports", "reason": "needs_model"})
        else:
            recs.append(judge(it, getter, args.model, b2_fn))
    for it in items:
        r = next(x for x in recs if x["id"] == it["id"])
        print("  %-4s %-3s expect=%-8s got=%-9s leg=%-8s %s"
              % (it["id"], it["class"], it["expect"], r["verdict"], r["leg"], r["reason"]))
    if args.det_only:
        # deterministic bars only: G1 (all J2 -> NOT/binding) ; G4 (all J4 -> UNCLEAR/no_abstract) ;
        # B1 no-fire on correct-cite J1/J3 (must ROUTE_B2, never NOT)
        fails = []
        for it, r in ((it, next(x for x in recs if x["id"] == it["id"])) for it in items):
            if it["class"] == "J2" and not (r["verdict"] == "NOT" and r["leg"] == "binding"):
                fails.append(("G1", it["id"], r["verdict"]))
            if it["class"] == "J4" and not (r["verdict"] == "UNCLEAR"):
                fails.append(("G4", it["id"], r["verdict"]))
            if it["class"] in ("J1", "J3") and r["verdict"] == "NOT":
                fails.append(("G3/no-castration(binding)", it["id"], r["verdict"]))
        if fails:
            print("DET-ONLY FAIL:", fails); return 1
        print("DET-ONLY PASS: G1 (J2->NOT/binding) + G4 (J4->UNCLEAR) + B1 never fires on correct-cite J1/J3.")
        print("  (G2 and the B2-content side of G3 require the real B2 model -> run plain --selftest.)")
        return _emit_g5(args)
    fails = check_bars(items, recs)
    if fails:
        print("BARS FAIL:", fails); return 1
    print("BARS PASS: G1 & G2 & G3 hold, G4 held. v0 judge is BUILDABLE+VALID.")
    return _emit_g5(args)

def mode_netcheck(args):
    meta = fetch_crossref(CONTROL_DOI)
    ok = bool(meta["title"]) and bool(meta["author_surnames"])
    print("netcheck %s -> title=%r venue=%r year=%s authors=%d abstract_len=%d"
          % (CONTROL_DOI, meta["title"][:60], meta["venue"], meta["year"],
             len(meta["author_surnames"]), len(meta["abstract"])))
    print("NETCHECK", "PASS" if ok else "FAIL")
    return 0 if ok else 1

def mode_run(args):
    items = load_falsifier(args.run)
    b2_fn = select_b2(args.b2, args.model)
    out = []
    for it in items:
        try:
            out.append(judge(it, fetch_crossref, args.model, b2_fn))
        except Exception as e:
            out.append({"doi": it.get("doi"), "verdict": "ERROR", "leg": "getter", "reason": str(e)})
        time.sleep(1.0)
    outpath = args.out or (args.run.rsplit(".", 1)[0] + "_s2b_out.jsonl")
    with open(outpath, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    c = Counter(r["verdict"] for r in out)
    print("ran %d items -> %s" % (len(out), dict(c)))
    print("wrote", outpath)
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--det-only", action="store_true")
    ap.add_argument("--netcheck", action="store_true")
    ap.add_argument("--run")
    ap.add_argument("--out")
    ap.add_argument("--b2", choices=["api", "local"], default="local")
    ap.add_argument("--falsifier", default="eval/_local/s2b_falsifier_v0.jsonl")
    ap.add_argument("--ground", default="eval/_local/ground_candidates.json")
    ap.add_argument("--cc", default="eval/_local/cc_v0.jsonl")
    ap.add_argument("--j5", default="eval/_local/j5_v0.jsonl")
    ap.add_argument("--cc-ground", dest="cc_ground", default="eval/_local/cc_j5_ground_v0.json")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()
    if args.model is None:
        args.model = "Qwen/Qwen2.5-7B-Instruct" if args.b2 == "local" else B2_MODEL_DEFAULT
    if args.selftest:  sys.exit(mode_selftest(args))
    if args.netcheck:  sys.exit(mode_netcheck(args))
    if args.run:       sys.exit(mode_run(args))
    ap.print_help(); sys.exit(0)

if __name__ == "__main__":
    main()
