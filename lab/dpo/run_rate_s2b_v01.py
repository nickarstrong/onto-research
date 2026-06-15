#!/usr/bin/env python3
# run_rate_s2b_v01.py -- ONTO S2B RATE driver (TYPE B measurement).
# Feeds the LIVE FROZEN SUBSTRATE's own raw proposals (proposals_v01.jsonl, n=30, NO expect)
# through the SAME frozen automated pipeline -- gate VETO (resolve + retracted, HARD) then the
# s2b JUDGE (B1 binding -> B2 supports) -- with an AUTOMATED disposition (no human, no `expect`):
#     HARD_REJECT (gate veto) / NOT (judge wrong-binding) / UNCLEAR=HELD (safe, not absorbed) /
#     SUPPORTS=ABSORBED.
# Emits a rate report (counts per bucket + honest-citation rate = ABSORBED / n). DIAGNOSTIC:
# there is NO PASS/FAIL bar (SPEC sec9) -- read the rate honestly, never relabel to flatter a number (R7).
#
# FROZEN organs are IMPORT-ONLY (loop_e2e_v0.py + s2b_v0.py md5 e8f84bb0). Nothing mirrored.
# run_full_turn_s2b_v0.py / loop_e2e_v0.finalize() are NOT used (finalize forces FAIL on no-expect input).
# READ-ONLY on all inputs ; writes only NEW files. proposals_v01 + per-item judgments stay LOCAL-ONLY.
#
# Modes:
#   --selftest         offline ; 4 synthetic records routed through dispose() proving the 4 buckets. No net/model.
#   --run              live ; gate -> judge -> dispose -> write LOCAL per-item jsonl + PUBLIC rate report.

import sys, os, json, argparse, datetime

PROPOSALS = "eval/_local/proposals_v01.jsonl"           # LOCAL-ONLY (bait-class), read off disk
JUDGMENTS = "eval/_local/rate_judgments_v01.jsonl"      # LOCAL-ONLY output (carries dois/claims)
REPORT    = "reports/report_s2b_rate_v01.md"            # PUBLIC-SAFE output (NO dois/claims)
MODEL     = "Qwen/Qwen2.5-7B-Instruct"

# (ll) Claude-fetch-free baseline on the SAME n=30 draw, for the agreement readout (public, from the ledger):
LL_BASELINE = {"HARD_REJECT": 11, "NOT": 11, "UNCLEAR_HELD": 8, "ABSORBED": 0}

BUCKETS = ["HARD_REJECT", "NOT", "UNCLEAR_HELD", "ABSORBED", "ERROR"]


def dispose(caught, judged):
    """Pure routing of gate-caught + judge-verdicts into the 4 (+ERROR) buckets. No net, no model."""
    out = {b: [] for b in BUCKETS}
    for c in caught:
        out["HARD_REJECT"].append(c)
    for r in judged:
        v = r.get("verdict")
        if v == "NOT":
            out["NOT"].append(r)
        elif v == "UNCLEAR":
            out["UNCLEAR_HELD"].append(r)
        elif v == "SUPPORTS":
            out["ABSORBED"].append(r)
        else:                                  # ERROR / unexpected -> never absorbed (safe, honest)
            out["ERROR"].append(r)
    return out


def hard_reject_breakdown(caught):
    """Sub-count HARD_REJECT by gate reason prefix (no_resolve vs retracted). Public-safe (counts only)."""
    sub = {}
    for c in caught:
        reason = (c.get("gate", {}) or {}).get("reason", "") or "unknown"
        key = reason.split(":", 1)[0]
        sub[key] = sub.get(key, 0) + 1
    return sub


def write_report(path, n, counts, sub, rate):
    rows = [
        ("HARD_REJECT (gate veto)",        counts["HARD_REJECT"], LL_BASELINE["HARD_REJECT"]),
        ("NOT (judge wrong-binding)",      counts["NOT"],          LL_BASELINE["NOT"]),
        ("UNCLEAR = HELD (safe)",          counts["UNCLEAR_HELD"], LL_BASELINE["UNCLEAR_HELD"]),
        ("SUPPORTS = ABSORBED",            counts["ABSORBED"],     LL_BASELINE["ABSORBED"]),
    ]
    lines = []
    lines.append("# S2B RATE v01 -- first automated rate of the live substrate (DIAGNOSTIC)\n")
    lines.append("Date: %s. n = %d raw {claim, doi, star_quote} proposals from the frozen 7B substrate,\n"
                 % (datetime.date.today().isoformat(), n))
    lines.append("run end to end through the FROZEN automated pipeline: gate veto (resolve + retracted, HARD)\n")
    lines.append("-> s2b supports-judge (B1 binding deterministic -> B2 supports, separate non-proposing model).\n")
    lines.append("No human, no `expect`. NO PASS/FAIL bar (SPEC sec9): this sizes a rate, it does not gate.\n\n")
    lines.append("## Disposition (automated)\n\n")
    lines.append("| bucket | this run (automated) | (ll) Claude-fetch-free |\n")
    lines.append("|---|---|---|\n")
    for label, mine, base in rows:
        lines.append("| %s | %d | %d |\n" % (label, mine, base))
    if counts["ERROR"]:
        lines.append("| ERROR (getter, never absorbed) | %d | 0 |\n" % counts["ERROR"])
    lines.append("\n")
    if sub:
        lines.append("HARD_REJECT breakdown: " +
                     ", ".join("%s %d" % (k, v) for k, v in sorted(sub.items())) + ".\n\n")
    lines.append("## Honest-citation rate\n\n")
    lines.append("ABSORBED / n = %d / %d = %.3f.\n\n" % (counts["ABSORBED"], n, rate))
    lines.append("## Reading (R7, honest)\n\n")
    lines.append("DIAGNOSTIC measurement, not a freeze-gate -- no number is relabeled to look better. The (ll)\n")
    lines.append("baseline column was marked by a separate non-proposing Claude instance fetch-free (recall-\n")
    lines.append("assisted, an honest gap) ; THIS run is the SAME gate + an automated retrieval-grounded judge.\n")
    lines.append("Agreement sizes the automated judge's reliability ; disagreement is informative, not a fail.\n")
    lines.append("The judge holds the safety property by construction: UNCLEAR routes to HELD (never absorbed),\n")
    lines.append("so a thin/absent abstract or an unseparable binding fails safe rather than minting a citation.\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(lines))


def mode_selftest():
    # Offline proof that dispose() routes the 4 buckets correctly. No net, no model, no frozen-organ import.
    caught = [{"id": "s1", "gate": {"reason": "no_resolve:crossref_404"}}]
    judged = [
        {"id": "s2", "verdict": "NOT",      "leg": "binding",  "reason": "wrong_binding_year"},
        {"id": "s3", "verdict": "UNCLEAR",  "leg": "supports", "reason": "no_abstract"},
        {"id": "s4", "verdict": "SUPPORTS", "leg": "supports", "reason": "b2_supports"},
    ]
    out = dispose(caught, judged)
    counts = {b: len(out[b]) for b in BUCKETS}
    expect = {"HARD_REJECT": 1, "NOT": 1, "UNCLEAR_HELD": 1, "ABSORBED": 1, "ERROR": 0}
    fails = [(b, counts[b], expect[b]) for b in BUCKETS if counts[b] != expect[b]]
    # an unexpected verdict must fail safe into ERROR, never ABSORBED
    err = dispose([], [{"id": "s5", "verdict": "WAT"}])
    if err["ABSORBED"] or len(err["ERROR"]) != 1:
        fails.append(("ERROR-failsafe", len(err["ERROR"]), 1))
    n = len(caught) + len(judged)
    rate = counts["ABSORBED"] / n
    for b in BUCKETS:
        print("  %-13s %d (expect %d)" % (b, counts[b], expect[b]))
    print("  rate ABSORBED/n = %d/%d = %.3f (expect 0.250)" % (counts["ABSORBED"], n, rate))
    if fails or abs(rate - 0.25) > 1e-9:
        print("SELFTEST FAIL:", fails or "rate"); return 1
    print("SELFTEST PASS: 4 buckets route correctly ; unexpected verdict fails safe to ERROR (never ABSORBED).")
    return 0


def mode_run():
    os.environ.setdefault("S2B_NO_4BIT", "1")   # CPU path: skip broken bnb 4bit -> fp16 offload
    import loop_e2e_v0 as loop
    import s2b_v0 as s2b

    caught, routed = loop.run_gate(PROPOSALS, loop.make_getter())   # S2 HARD veto (frozen)
    b2_fn = s2b.select_b2("local", MODEL)                            # S2B judge model (frozen)
    judged = []
    for r in routed:
        item = {"id": r["id"], "doi": r["doi"],
                "claim_text": r.get("claim_text", ""), "star_quote": r.get("star_quote")}
        try:
            rec = s2b.judge(item, s2b.fetch_crossref, MODEL, b2_fn)
        except Exception as e:
            rec = {"id": r["id"], "doi": r["doi"], "claim_text": r.get("claim_text", ""),
                   "verdict": "ERROR", "leg": "getter", "reason": str(e),
                   "fetched": {"abstract_present": False}}
        judged.append(rec)

    out = dispose(caught, judged)
    counts = {b: len(out[b]) for b in BUCKETS}
    n = len(caught) + len(judged)
    rate = counts["ABSORBED"] / n if n else 0.0
    sub = hard_reject_breakdown(caught)

    # LOCAL-ONLY per-item judgments (carry doi/claim) -- gate-caught + judged
    with open(JUDGMENTS, "w", encoding="utf-8") as f:
        for c in caught:
            f.write(json.dumps({"id": c.get("id"), "doi": c.get("doi"),
                                "bucket": "HARD_REJECT",
                                "gate_reason": (c.get("gate", {}) or {}).get("reason")},
                               ensure_ascii=False) + "\n")
        for r in judged:
            v = r.get("verdict")
            bucket = {"NOT": "NOT", "UNCLEAR": "UNCLEAR_HELD",
                      "SUPPORTS": "ABSORBED"}.get(v, "ERROR")
            f.write(json.dumps({"id": r.get("id"), "doi": r.get("doi"),
                                "claim_text": r.get("claim_text", ""),
                                "bucket": bucket, "verdict": v, "leg": r.get("leg"),
                                "reason": r.get("reason"),
                                "abstract_present": (r.get("fetched", {}) or {}).get("abstract_present")},
                               ensure_ascii=False) + "\n")

    write_report(REPORT, n, counts, sub, rate)

    print("=== S2B RATE v01 (automated, n=%d) ===" % n)
    print("  caught(gate HARD) = %d  routed(judge) = %d" % (len(caught), len(judged)))
    for b in ["HARD_REJECT", "NOT", "UNCLEAR_HELD", "ABSORBED", "ERROR"]:
        if b == "ERROR" and not counts[b]:
            continue
        print("  %-13s %d" % (b, counts[b]))
    if sub:
        print("  HARD_REJECT:", ", ".join("%s=%d" % kv for kv in sorted(sub.items())))
    print("  honest-citation rate ABSORBED/n = %d/%d = %.3f" % (counts["ABSORBED"], n, rate))
    print("  wrote", JUDGMENTS, "(LOCAL) and", REPORT, "(public)")
    if len(caught) + len(judged) != n or sum(counts.values()) != n:
        print("INTEGRITY FAIL: buckets do not sum to n"); return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(mode_selftest())
    if args.run:
        sys.exit(mode_run())
    ap.print_help(); sys.exit(0)


if __name__ == "__main__":
    main()
