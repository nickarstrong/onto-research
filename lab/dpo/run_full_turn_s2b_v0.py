#!/usr/bin/env python3
# run_full_turn_s2b_v0.py -- automated full turn for ONTO loop_e2e.
# PROPOSE -> gate VETO -> s2b JUDGE (replaces the S3 human worksheet) -> ABSORB + falsifier.
# This IS "the automated supports-judge dropped into the whole loop": s2b verdict -> worksheet mark.
import os, json
os.environ.setdefault("S2B_NO_4BIT", "1")   # 8GB GPU: skip broken bnb 4bit -> fp16 offload load
import loop_e2e_v0 as loop
import s2b_v0 as s2b

PROPOSALS = "eval/_local/proposals_v0.jsonl"
WS        = "eval/_local/worksheet_v0_auto.jsonl"
CAUGHT    = "eval/_local/caught_log_v0_auto.json"
LEDGER    = "eval/_local/ledger_s2b_v0_full.md"   # LOCAL (carries DOIs); public-safe derived separately
MODEL     = "Qwen/Qwen2.5-7B-Instruct"

def main():
    caught, routed = loop.run_gate(PROPOSALS, loop.make_getter())   # S2 HARD veto
    b2_fn = s2b.select_b2("local", MODEL)                            # S3 judge (automated, replaces human)
    marked = []
    for r in routed:
        rec = s2b.judge({"id": r["id"], "doi": r["doi"],
                         "claim_text": r["claim_text"], "star_quote": r["star_quote"]},
                        s2b.fetch_crossref, MODEL, b2_fn)
        marked.append({"id": r["id"], "doi": r["doi"], "claim_text": r["claim_text"],
                       "star_quote": r["star_quote"], "gate_reason": r["gate"]["reason"],
                       "mark": rec["verdict"], "leg": rec["leg"], "reason": rec["reason"],
                       "abstract_present": rec["fetched"]["abstract_present"]})
    with open(WS, "w", encoding="utf-8") as f:
        for m in marked:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    json.dump(caught, open(CAUGHT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    checks, ok = loop.finalize(WS, CAUGHT, PROPOSALS, LEDGER)        # S4 ABSORB + F1-F4 falsifier

    print("=== AUTOMATED FULL TURN (gate veto + s2b judge) ===")
    print("caught(gate HARD)=%d  routed(s2b judge)=%d" % (len(caught), len(marked)))
    for c in caught:
        print("  CAUGHT %-4s %s" % (c["id"], c["gate"]["reason"]))
    for m in marked:
        print("  JUDGE  %-4s -> %-8s leg=%-8s abstract=%s  %s"
              % (m["id"], m["mark"], m["leg"], m["abstract_present"], m["reason"]))
    print("--- F1-F4 falsifier (automated S3) ---")
    for c in checks:
        print("  %-4s %-26s -> %-26s [%s]"
              % (c["id"], c["expect"], c["disposition"], "PASS" if c["ok"] else "FAIL"))
    print("F1-F4 VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
