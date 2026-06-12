#!/usr/bin/env python3
# run_E16_e2e.py -- E16 END-TO-END (L1-L2-L4): one coherent pipe.
# For each item: turnstile_gate(item, bind) -> final verdict ; record vs item["expect"].
# bind = L4Bind(corpus_path) built ONCE (organ pulled lazily inside turnstile_gate on PASS-TO-L4).
# final verdict in {REJECT-L1, REJECT-L2, PASS-COMMON, DEMOTE, VERIFIED, CONTRADICTED}.
# Bad provenance dies at L1/L2 (organ NEVER runs) ; clean reaches L4 over live GOLD.
# NO turnstile / organ / SPEC edit. NEW code only.
#
# soft-collect (not hard-assert): collect every verdict + emit full report even on mismatch,
#   so gate-leak / false-veto are DIAGNOSABLE (a crash-assert would lose the report). exit !=0 on FAIL.
#
# usage: python run_E16_e2e.py <e2e_test.jsonl> <gold_corpus_live.json> <report_E16_e2e.md>

import json
import sys
import time

import provenance_turnstile as turn
import verify_E16_L4 as l4mod


def main(test_path, corpus_path, report_path):
    items = []
    with open(test_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    bind = l4mod.L4Bind(corpus_path)   # built ONCE ; reused per item

    rows = []
    leak = 0          # bad-provenance item whose organ was invoked (gate leak)
    false_veto = 0    # clean item that never reached the organ (turnstile false-veto)
    for it in items:
        t0 = time.time()
        verdict, rec = turn.turnstile_gate(it, bind)
        dt = time.time() - t0
        expect = it.get("expect", "?")
        ok = (verdict == expect)
        reached_l4 = ("l4" in rec)      # turnstile_gate sets rec["l4"] iff PASS-TO-L4
        bad_prov = expect in ("REJECT-L1", "REJECT-L2")
        clean = expect in ("VERIFIED", "CONTRADICTED")
        if bad_prov and reached_l4:
            leak += 1
        if clean and not reached_l4:
            false_veto += 1
        rows.append({
            "id": it["id"], "expect": expect, "verdict": verdict, "ok": ok,
            "reached_l4": reached_l4, "l1": rec.get("l1", ""), "l2": rec.get("l2", ""),
            "sec": round(dt, 2),
        })

    n_pass = sum(1 for r in rows if r["ok"])
    n_fail = len(rows) - n_pass

    # PASS criterion (pack v99 sec3):
    has_bad_rejected = any(
        r["expect"] in ("REJECT-L1", "REJECT-L2") and r["ok"] and not r["reached_l4"]
        for r in rows)
    has_clean_contra = any(r["expect"] == "CONTRADICTED" and r["verdict"] == "CONTRADICTED" for r in rows)
    has_clean_verif = any(r["expect"] == "VERIFIED" and r["verdict"] == "VERIFIED" for r in rows)
    clean_rows = [r for r in rows if r["expect"] in ("VERIFIED", "CONTRADICTED")]
    all_clean_reach = all(r["reached_l4"] for r in clean_rows)
    passed = (has_bad_rejected and has_clean_contra and has_clean_verif
              and all_clean_reach and leak == 0)

    L = []
    L.append("# report_E16_e2e -- END-TO-END L1-L2-L4 (one coherent pipe)\n\n")
    L.append("corpus    : %s\n" % corpus_path)
    L.append("turnstile : provenance_turnstile.turnstile_gate (FROZEN 4b04fe73)\n")
    L.append("organ     : verify_E16_L4.verify_item (FROZEN 544c9a7b, import-only)\n\n")
    L.append("| id | expect | verdict | ok | reached_L4 | L1 | L2 | sec |\n")
    L.append("|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
            r["id"], r["expect"], r["verdict"], "Y" if r["ok"] else "N",
            "Y" if r["reached_l4"] else "n/a(gated)", r["l1"], r["l2"], r["sec"]))
    L.append("\n")
    L.append("pass=%d fail=%d  gate_leak=%d  false_veto=%d\n" % (n_pass, n_fail, leak, false_veto))
    L.append("legs: bad_rejected_pre_model=%s  clean_contra->CONTRADICTED=%s  "
             "clean_agree->VERIFIED=%s  all_clean_reach_L4=%s\n" % (
                 has_bad_rejected, has_clean_contra, has_clean_verif, all_clean_reach))
    L.append("\nVERDICT: %s\n" % ("PASS" if passed else "FAIL"))
    if not passed:
        if leak:
            L.append("FAIL(gate): bad-provenance reached L4 -> diagnose TURNSTILE, not organ.\n")
        if all_clean_reach and not (has_clean_contra and has_clean_verif):
            L.append("FAIL(behaviour): clean item misverdicted at L4 -> ORGAN falsifier, "
                     "escalate (do NOT patch organ).\n")
        if false_veto:
            L.append("FAIL(false-veto): clean item gated before L4 -> diagnose TURNSTILE.\n")

    out = "".join(L)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(out)
    return 0 if passed else 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: run_E16_e2e.py <e2e_test.jsonl> <gold_corpus_live.json> <report_E16_e2e.md>")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
