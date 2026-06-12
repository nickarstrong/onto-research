#!/usr/bin/env python3
# provenance_turnstile.py -- E16 L1/L2 PROVENANCE TURNSTILE (v97 BUILD)
#
# Implements the DETERMINISTIC L1/L2 contract of SPEC_provenance_verifier_v1
# (md5 b62aad2f8ccf1a45d2634f74b432dd0a, FROZEN; sec2 L1/L2, sec3 tiers, sec4 boundaries).
# ZERO model. External registry owns the verdict (Crossref); ONTO only asks (SPEC sec2/sec4).
#
# CONTRACT (SPEC sec2):
#   L1 EXISTENCE : DOI resolves via Crossref AND (optional) metadata matches the cited claim.
#                  non-resolve / mismatch -> T4 (failed/fabricated marker).
#   L2 STATUS    : retraction / expression-of-concern, queried Crossmark (+ RWD coverage note).
#                  retracted / EoC -> T4-retracted.
#   clean L1+L2  -> passes the turnstile (PASS-TO-L4); the L4 organ runs ONLY on survivors.
#
# VERDICTS (pack v97 schema {id,expect,doi}):
#   REJECT-L1   : L1 fails (non-resolve OR metadata mismatch).        [SPEC T4: L1 fail]
#   REJECT-L2   : L1 pass, L2 retracted / EoC.                        [SPEC T4-retracted]
#   PASS-TO-L4  : L1 pass + L2 clean -> survivor, model may run.      [SPEC T1+, AXIS P clean]
#
# GATE-BEFORE-MODEL (SPEC sec4): a REJECT-L1/L2 verdict NEVER calls the L4 organ. The
#   frozen verify_E16_L4.verify_item is invoked ONLY on PASS-TO-L4 (see turnstile_gate).
#   The organ (md5 544c9a7b...) is import-only, NEVER edited.
#
# L1 metadata-MATCH is implemented but DORMANT for v97: the pack test schema carries no
#   cited_title. If an item carries item["cited_title"] it is checked (token-Jaccard >= MATCH_TAU);
#   otherwise L1 = resolve-only. Exercising mismatch (Fixture A nature00807) is NEXT+1 (needs title).
#
# RWD COVERAGE (SPEC sec2-L2, D1): L2 owns a stated coverage ceiling. This build queries
#   Crossref/Crossmark retraction signals (relation is-retracted-by, update-to type, RETRACTED
#   title prefix, RW-sourced update labels). A standalone RWD endpoint was NOT pre-confirmed this
#   session -> RWD is reported as 'crossref-integrated only' and the residual coverage gap is
#   surfaced per item, not hidden. If a SPEC-oracle retracted DOI returns clean, the SPEC L2
#   coverage falsifier has fired -> that is a real finding to surface, not a test bug.

import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

CROSSREF = "https://api.crossref.org/works/"
MAILTO = "council@ontostandard.org"            # Crossref polite pool
UA = "ONTO-provenance-turnstile/1.0 (mailto:%s)" % MAILTO
MATCH_TAU = 0.5                                # L1 metadata-match token-Jaccard floor (dormant v97)
RETRACT_TYPES = {
    "retraction", "removal", "withdrawal", "partial_retraction",
    "expression_of_concern", "expression-of-concern",
}


# -- Crossref lookup (the only network call; deterministic, no model) --------------------
def crossref_lookup(doi, timeout=20):
    """GET /works/{doi}. Returns (status, message|None). status: 200 ok, 404 non-resolve,
    or 'ERR:<reason>' on transport failure (caller treats as non-resolve + logs)."""
    url = CROSSREF + urllib.parse.quote(doi) + "?mailto=" + MAILTO
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
            return r.status, payload.get("message")
    except urllib.error.HTTPError as e:
        return e.code, None                    # 404 = non-resolve (fabricated marker)
    except Exception as e:                     # noqa: BLE001 -- transport, treated as non-resolve
        return "ERR:%s" % type(e).__name__, None


# -- L1 EXISTENCE ------------------------------------------------------------------------
def _norm_tokens(s):
    return set(w for w in "".join(c.lower() if c.isalnum() else " " for c in s).split() if len(w) > 2)


def l1_existence(item, msg, status):
    """Returns (ok, detail). ok=False -> REJECT-L1 (non-resolve OR metadata mismatch)."""
    if status != 200 or msg is None:
        return False, "non-resolve(status=%s)" % status
    cited_title = (item.get("cited_title") or "").strip()
    if not cited_title:
        return True, "resolve-only(no cited_title; match dormant)"
    got = " ".join(msg.get("title") or [])
    a, b = _norm_tokens(cited_title), _norm_tokens(got)
    if not a or not b:
        return True, "resolve(metadata-title empty; match skipped)"
    jac = len(a & b) / float(len(a | b))
    if jac >= MATCH_TAU:
        return True, "resolve+match(jaccard=%.2f)" % jac
    return False, "metadata-mismatch(jaccard=%.2f < %.2f)" % (jac, MATCH_TAU)


# -- L2 STATUS ---------------------------------------------------------------------------
def l2_status(msg):
    """Returns (clean, detail). clean=False -> REJECT-L2. Scans Crossmark/RW signals."""
    sigs = []
    # title prefix: publishers prepend RETRACTED/Retraction of...
    title = " ".join(msg.get("title") or []).strip().lower()
    if title.startswith("retracted") or title.startswith("retraction of") \
            or "[retracted]" in title:
        sigs.append("title-prefix")
    # Crossref relation: is-retracted-by
    rel = msg.get("relation") or {}
    if "is-retracted-by" in rel:
        sigs.append("relation:is-retracted-by")
    # update-to / updated-by entries carrying a retraction type
    for key in ("update-to", "updated-by"):
        for u in (msg.get(key) or []):
            t = str(u.get("type", "")).lower().replace(" ", "_")
            if t in RETRACT_TYPES:
                sigs.append("%s:%s" % (key, t))
    if sigs:
        return False, "retracted[" + ",".join(sorted(set(sigs))) + "]"
    return True, "clean(crossmark; RWD=crossref-integrated only -- coverage gap owned)"


# -- TURNSTILE (one item) ----------------------------------------------------------------
def turnstile(item, timeout=20):
    """Returns record {id, doi, verdict, l1, l2, status}. verdict in
    {REJECT-L1, REJECT-L2, PASS-TO-L4}."""
    doi = item["doi"]
    status, msg = crossref_lookup(doi, timeout=timeout)
    ok1, d1 = l1_existence(item, msg, status)
    if not ok1:
        return {"id": item["id"], "doi": doi, "verdict": "REJECT-L1",
                "l1": d1, "l2": "n/a(gated)", "status": status}
    clean2, d2 = l2_status(msg)
    if not clean2:
        return {"id": item["id"], "doi": doi, "verdict": "REJECT-L2",
                "l1": d1, "l2": d2, "status": status}
    return {"id": item["id"], "doi": doi, "verdict": "PASS-TO-L4",
            "l1": d1, "l2": d2, "status": status}


# -- PRE-STAGE WIRING (gate-before-model; organ import-only, NEVER edited) ----------------
def turnstile_gate(item, bind, timeout=20):
    """L1/L2 turnstile AHEAD of the frozen L4 organ. The model runs ONLY on PASS-TO-L4.
    REJECT-L1/L2 -> verify_item is NOT called (SPEC sec4 gate-before-model).
    NOTE: the L4 call needs GPU+GOLD (DeBERTa + live corpus) -> exercised in the end-to-end
    NEXT+1 pass, NOT in the no-GPU L1/L2 run. Here for the wiring contract only."""
    rec = turnstile(item, timeout=timeout)
    if rec["verdict"] != "PASS-TO-L4":
        return rec["verdict"], rec               # organ untouched
    import verify_E16_L4 as l4                    # lazy: pulls torch only when a survivor exists
    label, organ_rec = l4.verify_item(item, bind)
    rec["l4"] = label
    rec["l4_record"] = organ_rec
    return label, rec


# -- SELF-TEST DRIVER: assert verdict == expect, emit report -----------------------------
def run(test_path, report_path, sleep=0.3):
    items = [json.loads(l) for l in open(test_path, encoding="utf-8") if l.strip()]
    rows, npass = [], 0
    for it in items:
        rec = turnstile(it)
        exp = it["expect"]
        ok = (rec["verdict"] == exp)
        npass += int(ok)
        rec["expect"] = exp
        rec["pass"] = ok
        rows.append(rec)
        print("[%s] %-28s expect=%-11s got=%-11s %s"
              % ("PASS" if ok else "FAIL", rec["id"], exp, rec["verdict"],
                 "" if ok else "<<< MISMATCH"))
        time.sleep(sleep)                          # Crossref courtesy
    verdict = "PASS" if npass == len(rows) else "FAIL"
    _emit_report(report_path, rows, npass, verdict)
    print("\n[turnstile] %d/%d items -> %s  (report: %s)"
          % (npass, len(rows), verdict, report_path))
    return verdict


def _emit_report(path, rows, npass, verdict):
    L = []
    L.append("# report_E16_turnstile -- L1/L2 PROVENANCE TURNSTILE (v97)\n")
    L.append("SPEC : SPEC_provenance_verifier_v1 (b62aad2f...) sec2 L1/L2, sec3 tiers, sec4 gate.\n")
    L.append("organ: verify_E16_L4.py (544c9a7b...) UNTOUCHED -- turnstile is a PRE-STAGE in front.\n")
    L.append("L1=resolve(+match dormant) ; L2=crossmark retraction(+RWD coverage gap owned).\n\n")
    L.append("| id | doi | L1 | L2 | expect | verdict | pass |\n")
    L.append("|----|-----|----|----|--------|---------|------|\n")
    for r in rows:
        L.append("| %s | %s | %s | %s | %s | %s | %s |\n"
                 % (r["id"], r["doi"], r["l1"], r["l2"], r["expect"],
                    r["verdict"], "Y" if r["pass"] else "N"))
    L.append("\nRESULT: %d/%d -> %s\n" % (npass, len(rows), verdict))
    L.append("\nPASS criterion (pack v97 sec3): clean-source -> PASS-TO-L4 AND unresolvable -> "
             "REJECT-L1 AND retracted -> REJECT-L2.\n")
    L.append("FAIL = clean source rejected (false provenance veto) OR bad source passed (gate "
             "leak) -> diagnose turnstile, do NOT patch the frozen L4 organ.\n")
    open(path, "w", encoding="utf-8").write("".join(L))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: provenance_turnstile.py <prov_test.jsonl> [report_E16_turnstile.md]")
        sys.exit(2)
    tp = sys.argv[1]
    rp = sys.argv[2] if len(sys.argv) > 2 else "report_E16_turnstile.md"
    v = run(tp, rp)
    sys.exit(0 if v == "PASS" else 1)
