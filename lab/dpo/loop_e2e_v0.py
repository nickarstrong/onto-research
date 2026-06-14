#!/usr/bin/env python3
# loop_e2e_v0.py -- ONTO end-to-end loop, vertical slice v0 (SPEC_loop_e2e_v0.md)
#   PROPOSE -> EXTERNAL CHECK (gate) -> HUMAN RESIDUAL (worksheet) -> ABSORB (ledger)
#
# Station coverage (SPEC sec1/sec3):
#   S1 PROPOSE      : fixed proposals_v0.jsonl on disk (NOT live substrate ; v0.1).
#   S2 EXTERNAL CHK : THE GATE, well-done. per doi, independent of the proposer:
#                       (a) RESOLVE   -> Crossref works ; non-resolve = FABRICATION = HARD REJECT.
#                       (c) RETRACTED -> retraction signals ; retracted/withdrawn = HARD REJECT.
#                       (b) SUPPORTS? -> NOT automated, NOT self-answered -> routed to S3.
#   S3 HUMAN RESID  : worksheet ; an INDEPENDENT reader marks SUPPORTS / NOT / UNCLEAR.
#   S4 ABSORB       : only {resolve AND not-retracted AND human-SUPPORTS} is absorbed ; ledger + caught-log.
#
# Trust boundary (SPEC sec2): the proposer's star_quote is FORM only ; the gate re-resolves and the
#   (b) judge is a different actor. This script NEVER trusts star_quote as the verdict.
#
# Discipline: READ-ONLY on the substrate. Imports/touches NO predicate/SPEC/A-channel byte.
#   The Crossref getter is MIRRORED verbatim from run_L5_partI_validate.live_run (md5 b96bfb43) so the
#   resolve path is byte-faithful to the frozen L5 fetch pattern, without coupling to that module.
#   The gate reads ONLY {id, claim_text, doi, star_quote} ; it NEVER reads planted/expect (no oracle leak).
#   planted/expect are consumed ONLY by --finalize's falsifier check (SPEC sec4), never by the gate.

import argparse, json, sys, time
import urllib.request, urllib.error

CROSSREF      = "https://api.crossref.org/works/{doi}"            # resolve endpoint (== L5 CROSSREF)
CROSSREF_UPD  = "https://api.crossref.org/works?filter=updates:{doi}&rows=25"  # notices updating a doi
RETRACT_TYPES = {"retraction", "withdrawal", "removal"}
RETRACT_TITLE = ("RETRACT", "WITHDRAW", "REMOVED")               # publisher title prefixes

# ---------------------------------------------------------------- HTTP getter (mirrored, md5 b96bfb43)
def make_getter():
    def getter(url):
        req = urllib.request.Request(url, headers={"User-Agent": "ONTO-loop-v0/1.0 (mailto:council@ontostandard.org)"})
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    return getter

# ---------------------------------------------------------------- S2 the gate
class ResolveError(Exception):
    pass

def resolve(doi, getter):
    """S2(a). Return the Crossref `message` for a resolving doi ; raise ResolveError on non-resolve."""
    try:
        data = getter(CROSSREF.format(doi=doi))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ResolveError("crossref_404")
        raise ResolveError("crossref_http_%s" % e.code)
    except Exception as e:
        raise ResolveError("crossref_err_%s" % type(e).__name__)
    if not isinstance(data, dict) or data.get("status") != "ok":
        raise ResolveError("crossref_status_not_ok")
    msg = data.get("message")
    if not isinstance(msg, dict) or not msg:
        raise ResolveError("crossref_no_message")
    return msg

def is_retracted(doi, msg, getter):
    """S2(c). UNION of retraction signals -> (bool, signal_str).
    Signals: (1) title prefix RETRACTED/WITHDRAWN ; (2) update-to entry of retraction type ;
             (3) a Crossref `updates` query -> any notice that update-to's this doi as retraction
                 (or whose title says retraction). (3) is best-effort (supplement)."""
    d = (doi or "").lower()
    # (1) title prefix on the work itself
    for t in msg.get("title", []) or []:
        if (t or "").strip().upper().startswith(RETRACT_TITLE):
            return True, "title_prefix"
    # (2) update-to on the work (rare on the article, kept)
    for u in msg.get("update-to", []) or []:
        if (u.get("type", "") or "").lower() in RETRACT_TYPES and (u.get("DOI", "") or "").lower() == d:
            return True, "update_to_self"
    # (3) reverse lookup: notices that update THIS doi
    try:
        upd = getter(CROSSREF_UPD.format(doi=doi))
        items = (upd.get("message", {}) or {}).get("items", []) if isinstance(upd, dict) else []
        for it in items or []:
            for u in it.get("update-to", []) or []:
                if (u.get("DOI", "") or "").lower() == d and (u.get("type", "") or "").lower() in RETRACT_TYPES:
                    return True, "updates_query_retraction"
            for t in it.get("title", []) or []:
                if "retract" in (t or "").lower():
                    return True, "updates_query_title"
    except Exception:
        pass  # supplement only ; (1)+(2) already ran on the resolved work
    return False, ""

def gate(doi, getter):
    """S2. HARD veto. Returns dict {resolve, retracted, verdict, reason}.
    verdict in {HARD_REJECT (fabrication|retracted), ROUTE_S3 (resolved+clean -> human supports?)}."""
    try:
        msg = resolve(doi, getter)
    except ResolveError as e:
        return {"resolve": False, "retracted": None, "verdict": "HARD_REJECT", "reason": "no_resolve:%s" % e}
    retr, sig = is_retracted(doi, msg, getter)
    if retr:
        return {"resolve": True, "retracted": True, "verdict": "HARD_REJECT", "reason": "retracted:%s" % sig}
    return {"resolve": True, "retracted": False, "verdict": "ROUTE_S3", "reason": "needs_human_supports"}

# ---------------------------------------------------------------- run / worksheet / ledger
def load_proposals(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    for r in rows:
        assert "id" in r and "doi" in r and "claim_text" in r, "proposal missing id/doi/claim_text: %s" % r
    return rows

def run_gate(path, getter, sleep=0.3):
    """S2 over the whole proposal set. Returns (caught, routed) ; gate sees ONLY the doi."""
    rows = load_proposals(path)
    caught, routed = [], []
    for r in rows:
        g = gate(r["doi"], getter); time.sleep(sleep)
        rec = {"id": r["id"], "doi": r["doi"], "claim_text": r["claim_text"],
               "star_quote": r.get("star_quote", ""), "gate": g}
        if g["verdict"] == "HARD_REJECT":
            caught.append(rec)
        else:
            routed.append(rec)
    return caught, routed

def write_worksheet(routed, path):
    """S3 emit. One row per gate-passed proposal ; reviewer fills mark = SUPPORTS|NOT|UNCLEAR."""
    with open(path, "w", encoding="utf-8") as f:
        for r in routed:
            f.write(json.dumps({"id": r["id"], "doi": r["doi"], "claim_text": r["claim_text"],
                                "star_quote": r["star_quote"], "gate_reason": r["gate"]["reason"],
                                "mark": ""}, ensure_ascii=False) + "\n")

def finalize(worksheet_path, caught_path, proposals_path, ledger_path):
    """S4 ABSORB + ledger + locked-falsifier check (SPEC sec4). Falsifier reads planted/expect HERE only."""
    marks = [json.loads(l) for l in open(worksheet_path, encoding="utf-8") if l.strip()]
    caught = json.load(open(caught_path, encoding="utf-8"))
    planted = {r["id"]: r for r in load_proposals(proposals_path)}  # for the falsifier check ONLY

    absorbed, rejected_human = [], []
    for m in marks:
        mk = (m.get("mark", "") or "").strip().upper()
        if mk == "SUPPORTS":
            absorbed.append(m)
        elif mk in ("NOT", "UNCLEAR", ""):
            rejected_human.append({**m, "mark": mk or "UNMARKED"})
        else:
            rejected_human.append({**m, "mark": "BAD_MARK(%s)" % mk})

    # ---- locked falsifier (SPEC sec4) : per-item disposition vs expect
    def disposition(pid):
        if any(c["id"] == pid for c in caught):
            c = next(c for c in caught if c["id"] == pid)
            return "HARD_REJECT(%s)" % c["gate"]["reason"]
        if any(a["id"] == pid for a in absorbed):
            return "ABSORBED"
        if any(r["id"] == pid for r in rejected_human):
            r = next(r for r in rejected_human if r["id"] == pid)
            return "HUMAN_REJECT(%s)" % r["mark"]
        return "UNSEEN"

    checks = []
    ok_all = True
    for pid, p in planted.items():
        disp = disposition(pid)
        exp = p.get("expect", "")
        # expectation -> required disposition predicate
        if exp == "ACCEPT_after_S3_supports":
            good = (disp == "ABSORBED")
        elif exp == "HARD_REJECT_at_resolve":
            good = disp.startswith("HARD_REJECT(no_resolve")
        elif exp == "HARD_REJECT_at_retracted":
            good = disp.startswith("HARD_REJECT(retracted")
        elif exp == "S2_pass_then_S3_NOT_reject":
            good = disp.startswith("HUMAN_REJECT")
        else:
            good = False
        # salmonella + over-castration guards (SPEC sec4, absolute)
        if p.get("planted") in ("fabricated_non_resolving_doi", "retracted") and disp == "ABSORBED":
            good = False  # a fabricated/retracted item ABSORBED = v0 FAIL (do not ship)
        if p.get("planted") == "genuine" and disp.startswith("HARD_REJECT"):
            good = False  # genuine item hard-rejected pre-S3 = over-castration = v0 FAIL
        ok_all = ok_all and good
        checks.append({"id": pid, "planted": p.get("planted"), "expect": exp,
                       "disposition": disp, "ok": good})

    _write_ledger(ledger_path, caught, absorbed, rejected_human, checks, ok_all)
    return checks, ok_all

def _write_ledger(path, caught, absorbed, rejected_human, checks, ok_all):
    L = []
    L.append("# ledger_v0.md -- ONTO end-to-end loop, one full turn (SPEC_loop_e2e_v0.md sec5)")
    L.append("")
    L.append("generated : %s" % time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))
    L.append("stations  : PROPOSE -> EXTERNAL CHECK (gate) -> HUMAN RESIDUAL -> ABSORB")
    L.append("")
    L.append("## the turn (legible record)")
    cids = ", ".join(c["id"] for c in caught) or "(none)"
    aids = ", ".join(a["id"] for a in absorbed) or "(none)"
    rids = ", ".join(r["id"] for r in rejected_human) or "(none)"
    L.append("Star proposed %d items. Gate HARD-rejected: %s. Routed the rest to a human reader."
             % (len(caught) + len(absorbed) + len(rejected_human), cids))
    L.append("Human accepted (SUPPORTS): %s. Human rejected (NOT/UNCLEAR): %s." % (aids, rids))
    L.append("ABSORBED into accepted knowledge: %s." % aids)
    L.append("")
    L.append("## S2 caught-log (gate HARD reject, no human input)")
    if caught:
        for c in caught:
            L.append("- %s  doi=%s  -> %s" % (c["id"], c["doi"], c["gate"]["reason"]))
    else:
        L.append("- (none)")
    L.append("")
    L.append("## S3 human residual")
    for a in absorbed:
        L.append("- %s  doi=%s  -> SUPPORTS -> ABSORB" % (a["id"], a["doi"]))
    for r in rejected_human:
        L.append("- %s  doi=%s  -> %s -> REJECT" % (r["id"], r["doi"], r["mark"]))
    if not absorbed and not rejected_human:
        L.append("- (none routed)")
    L.append("")
    L.append("## S4 absorbed (accepted knowledge)")
    if absorbed:
        for a in absorbed:
            L.append("- %s : %s  [%s]" % (a["id"], a["claim_text"], a["doi"]))
    else:
        L.append("- (nothing absorbed)")
    L.append("")
    L.append("## falsifier check (SPEC sec4 ; locked before build)")
    L.append("%-4s %-32s %-28s %-26s %s" % ("id", "planted", "expect", "disposition", "ok"))
    for c in checks:
        L.append("%-4s %-32s %-28s %-26s %s" % (c["id"], c["planted"], c["expect"], c["disposition"],
                                                "PASS" if c["ok"] else "FAIL"))
    L.append("")
    L.append("v0 VERDICT : %s" % ("PASS" if ok_all else "FAIL"))
    L.append("  (PASS iff: F2+F3 HARD-rejected by the gate with NO human input ; F1 reachable+absorbable ;")
    L.append("   F4 reaches human and is rejected ; ZERO fabricated/retracted absorbed ; ZERO genuine pre-castrated.)")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---------------------------------------------------------------- selftest (well-done veto, offline)
def selftest():
    """Written-in validation of the veto with a FAKE getter -- no network, no Crossref.
    Proves: fabrication -> HARD REJECT(resolve) ; retracted -> HARD REJECT(retracted) ;
            genuine -> ROUTE_S3. The veto must pass this before it is trusted on the net."""
    GOOD = "10.0000/good"; FAB = "10.0000/fab"; RETR = "10.0000/retr"
    def fake_getter(url):
        if FAB in url:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        if url.startswith("https://api.crossref.org/works?filter=updates:"):
            # reverse-lookup endpoint: a retraction notice for RETR, nothing for GOOD
            if RETR in url:
                return {"status": "ok", "message": {"items": [
                    {"title": ["Retraction notice"], "update-to": [{"DOI": RETR, "type": "retraction"}]}]}}
            return {"status": "ok", "message": {"items": []}}
        if GOOD in url:
            return {"status": "ok", "message": {"title": ["A genuine resolving work"], "author": []}}
        if RETR in url:
            return {"status": "ok", "message": {"title": ["Some withdrawn-but-untitled work"], "author": []}}
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    g_good = gate(GOOD, fake_getter)
    g_fab  = gate(FAB,  fake_getter)
    g_retr = gate(RETR, fake_getter)
    fails = []
    if not (g_good["verdict"] == "ROUTE_S3" and g_good["resolve"] and not g_good["retracted"]):
        fails.append(("genuine->ROUTE_S3", g_good))
    if not (g_fab["verdict"] == "HARD_REJECT" and g_fab["resolve"] is False and g_fab["reason"].startswith("no_resolve")):
        fails.append(("fabrication->HARD_REJECT(resolve)", g_fab))
    if not (g_retr["verdict"] == "HARD_REJECT" and g_retr["retracted"] and g_retr["reason"].startswith("retracted")):
        fails.append(("retracted->HARD_REJECT(retracted)", g_retr))
    # title-prefix path (publisher-flagged retraction, no updates query needed)
    g_title = gate("10.0000/titleretr", lambda u: (_ for _ in ()).throw(urllib.error.HTTPError(u,404,"x",{},None))
                   if "updates:" in u else {"status":"ok","message":{"title":["RETRACTED: bad paper"]}})
    if not (g_title["verdict"] == "HARD_REJECT" and g_title["reason"] == "retracted:title_prefix"):
        fails.append(("title_prefix->HARD_REJECT", g_title))
    if fails:
        print("SELFTEST FAIL"); [print("  ", n, v) for n, v in fails]; sys.exit(1)
    print("SELFTEST PASS  (genuine->ROUTE_S3 ; fabrication->HARD_REJECT(resolve) ;")
    print("                retracted[updates]->HARD_REJECT ; retracted[title]->HARD_REJECT)")

# ---------------------------------------------------------------- net pre-check
def netcheck():
    """Before any run: prove Crossref resolve reaches AND a known-retracted doi trips the veto.
    Uses the planted F3 retracted doi as the live retraction-recall probe."""
    g = make_getter()
    probe_ok = "10.1038/171737a0"                      # F1 genuine, must RESOLVE + ROUTE_S3
    probe_retr = "10.1016/S0140-6736(97)11096-0"       # F3 retracted, must HARD_REJECT(retracted)
    r1 = gate(probe_ok, g); time.sleep(0.3)
    r2 = gate(probe_retr, g)
    print("netcheck resolve  %-26s -> %s" % (probe_ok, r1))
    print("netcheck retract  %-26s -> %s" % (probe_retr, r2))
    ok = (r1["verdict"] == "ROUTE_S3") and (r2["verdict"] == "HARD_REJECT" and r2["retracted"])
    print("NETCHECK", "PASS" if ok else "FAIL (retraction recall or resolve broken -- fix before --run)")
    sys.exit(0 if ok else 1)

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser(description="ONTO loop_e2e_v0 -- propose/check/residual/absorb")
    ap.add_argument("--selftest", action="store_true", help="offline veto validation (no net)")
    ap.add_argument("--netcheck", action="store_true", help="live resolve + retraction-recall probe")
    ap.add_argument("--run", metavar="PROPOSALS", help="S2 gate over proposals_v0.jsonl")
    ap.add_argument("--worksheet", metavar="OUT", help="S3 worksheet path to write (with --run) or read (with --finalize)")
    ap.add_argument("--caught", metavar="PATH", help="caught-log json path (write with --run, read with --finalize)")
    ap.add_argument("--finalize", action="store_true", help="S4: read marked worksheet -> ledger + falsifier")
    ap.add_argument("--proposals", metavar="PATH", help="proposals path (for --finalize falsifier check)")
    ap.add_argument("--ledger", metavar="OUT", default="ledger_v0.md", help="ledger output (with --finalize)")
    ap.add_argument("--dryplan", action="store_true", help="parse proposals + print plan, no net")
    a = ap.parse_args()

    if a.selftest: return selftest()
    if a.netcheck: return netcheck()

    if a.dryplan:
        rows = load_proposals(a.run or a.proposals)
        print("PLAN: %d proposals -> S2 gate -> S3 worksheet -> human -> S4 ledger" % len(rows))
        for r in rows: print("  %-4s %s" % (r["id"], r["doi"]))
        return

    if a.run and not a.finalize:
        caught, routed = run_gate(a.run, make_getter())
        ws = a.worksheet or "worksheet_v0.jsonl"
        cg = a.caught or "caught_log_v0.json"
        write_worksheet(routed, ws)
        json.dump(caught, open(cg, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("S2 gate done. caught(HARD reject)=%d routed(to human)=%d" % (len(caught), len(routed)))
        for c in caught: print("  CAUGHT %-4s %-30s %s" % (c["id"], c["doi"], c["gate"]["reason"]))
        for r in routed: print("  ROUTED %-4s %-30s %s" % (r["id"], r["doi"], r["gate"]["reason"]))
        print("\nworksheet -> %s   (mark each: SUPPORTS|NOT|UNCLEAR)" % ws)
        print("caught-log -> %s" % cg)
        return

    if a.finalize:
        if not (a.worksheet and a.caught and a.proposals):
            ap.error("--finalize needs --worksheet <marked> --caught <log> --proposals <proposals_v0.jsonl>")
        checks, ok = finalize(a.worksheet, a.caught, a.proposals, a.ledger)
        print("FINALIZE -> %s" % a.ledger)
        for c in checks:
            print("  %-4s %-26s -> %s  [%s]" % (c["id"], c["expect"], c["disposition"], "PASS" if c["ok"] else "FAIL"))
        print("v0 VERDICT:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)

    ap.print_help()

if __name__ == "__main__":
    main()
