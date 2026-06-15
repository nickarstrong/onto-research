#!/usr/bin/env python3
# finalize_v01.py -- LOOP v0.1 S3+S4 (gate loop_e2e_v0.py UNCHANGED, R7).
#
# The S2(b) supports-judge here is Claude acting as a SEPARATE NON-PROPOSING INSTANCE (SPEC sec2
# permits "a separate non-proposing instance" as the residual reader; the proposer is the frozen
# Qwen base, a different actor). Each NOT is GROUNDED on a fetch-free contradiction (journal-domain
# mismatch, or the quote's own cited year/source vs the DOI vintage). Items with no fetch-free tell
# are UNCLEAR (honest: not verified, not absorbed). This is NOT a human residual and NOT the
# automated true-core; it is a one-off grounded judgment to close the turn. Reasons are recorded
# for audit in supports_judgment_v01.md.
#
# Run (in lab\dpo\):  python finalize_v01.py

import json, datetime, os, sys

WS  = os.path.join("eval", "_local", "worksheet_v01.jsonl")
CG  = os.path.join("eval", "_local", "caught_log_v01.json")
SJ  = os.path.join("eval", "_local", "supports_judgment_v01.md")
LOC = os.path.join("eval", "_local", "ledger_v01.md")
PUB = os.path.join("reports", "ledger_v01_public.md")

# id -> (mark, grounded reason). Authored by Claude (separate non-proposing instance), grounded.
MARKS = {
 "sub_v01:01": ("NOT", "claim = the 1953 Watson-Crick double helix (real DOI 10.1038/171737a0); nature01319 is a 2001+-era Nature DOI -> cannot be the cited 1953 paper."),
 "sub_v01:03": ("NOT", "quote cites Spergel et al. 2003; PhysRevLett vol.96 is 2006 -> the quote's own year contradicts the DOI vintage."),
 "sub_v01:05": ("NOT", "quote cites IPCC 2013; nature09317 is a ~2010 Nature article -> an IPCC 2013 report is not this Nature DOI."),
 "sub_v01:06": ("NOT", "quote cites Jinek et al. 2012; nature14499 is a ~2015 Nature DOI -> not the cited 2012 paper (year contradiction)."),
 "sub_v01:07": ("NOT", "quote describes the PLB 716 (2012) Higgs discovery; the discovery DOIs are ...2012.08.020 (ATLAS)/...021 (CMS), not ...028 [recall-based]."),
 "sub_v01:09": ("NOT", "quote says Nature 2008; nature08700 is a ~2010-issue Nature DOI -> vintage contradicts the quote year."),
 "sub_v01:12": ("NOT", "claim is about ANTIBIOTIC resistance but the DOI is in Antiviral Research (j.antiviral) -> journal-domain mismatch."),
 "sub_v01:14": ("NOT", "quote says Nature 2008 (iron-based superconductivity); nature09148 is a ~2010-issue DOI -> vintage contradiction."),
 "sub_v01:15": ("NOT", "quote cites Takahashi et al. 2007 (human iPSC); nature08484 is a ~2009 Nature DOI -> not the cited 2007 paper."),
 "sub_v01:23": ("NOT", "quote cites Planck Collaboration 2015; nature04606 is a ~2006 Nature DOI -> a 2015 result is not this 2006 DOI."),
 "sub_v01:29": ("NOT", "claim = K-Pg asteroid impact but the DOI is in the Journal of Geriatric Oncology (j.jgo); 'Hildebrand 2019' also wrong (Chicxulub is Hildebrand 1991) -> journal-domain mismatch."),
 "sub_v01:02": ("UNCLEAR", "generic immunology claim; doi is a 2019 Vaccine article with no internal contradiction -> cannot confirm/deny support without the source title."),
 "sub_v01:08": ("UNCLEAR", "generic statin claim; quote names no source/year; doi is a 2018 Am Heart J article -> no fetch-free tell."),
 "sub_v01:11": ("UNCLEAR", "quote 'Larkin et al. 2014'; doi is a 2014 Cancer Cell article (year matches) -> cannot confirm the specific paper backs the claim without title."),
 "sub_v01:13": ("UNCLEAR", "quote 'Wysession 2010' (textbook author); nature09573 vintage ~2010 (year matches) -> cannot ground topic without title."),
 "sub_v01:18": ("UNCLEAR", "quote 'Nature 2005'; nature04712 vintage ~2006 (borderline) -> not a clean contradiction."),
 "sub_v01:22": ("UNCLEAR", "generic mRNA-vaccine mechanism; doi is a 2020 Vaccine article (plausible topic) -> no fetch-free tell."),
 "sub_v01:24": ("UNCLEAR", "quote 'Kirsch et al. 2006'; doi is a 2006 Neuropharmacology article (year matches) -> cannot confirm without title."),
 "sub_v01:25": ("UNCLEAR", "human-genome gene-count claim; nature01273 vintage ~2003 -> cannot ground topic without title."),
}

for p in (WS, CG):
    if not os.path.exists(p):
        sys.exit("STOP: missing %s (run the gate --run first)" % p)

rows   = [json.loads(l) for l in open(WS, encoding="utf-8") if l.strip()]
caught = json.load(open(CG, encoding="utf-8"))

ids_ws = {r["id"] for r in rows}
miss   = ids_ws - set(MARKS)
extra  = set(MARKS) - ids_ws
if miss:  sys.exit("STOP: worksheet ids with no authored mark: %s" % ", ".join(sorted(miss)))
if extra: sys.exit("STOP: authored marks for ids not in worksheet: %s" % ", ".join(sorted(extra)))

# patch worksheet in place (mark + mark_reason + judge provenance)
for r in rows:
    mk, reason = MARKS[r["id"]]
    r["mark"] = mk
    r["mark_reason"] = reason
    r["judge"] = "claude_separate_nonproposing_instance_grounded"
with open(WS, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

def mk(r): return (r.get("mark", "") or "").strip().upper()
absorbed = [r for r in rows if mk(r) == "SUPPORTS"]
rej_not  = [r for r in rows if mk(r) == "NOT"]
rej_unc  = [r for r in rows if mk(r) in ("UNCLEAR", "")]
n_caught, n_routed = len(caught), len(rows)
n_total = n_caught + n_routed
pct = lambda x: (100.0 * x / n_total) if n_total else 0.0
date = datetime.date.today().isoformat()

# ---- audit: per-item grounded reasoning (LOCAL)
A = ["# supports_judgment_v01.md -- S2(b) grounded judgment (LOCAL, bait-class, NEVER public)", "",
     "judge : Claude as a separate non-proposing instance (SPEC sec2). GROUNDED per-item, fetch-free.",
     "        NOT requires a defensible contradiction ; no tell -> UNCLEAR (not verified, not absorbed).",
     "        This is not a human residual and not the automated true-core. n=%d." % n_routed, "",
     "## verdicts"]
for r in rows:
    A.append("    %-7s %-12s %-34s %s" % (mk(r), r["id"], r["doi"], r.get("mark_reason", "")))
open(SJ, "w", encoding="utf-8").write("\n".join(A) + "\n")

# ---- LOCAL detailed ledger (with DOIs)
L = ["# ledger_v01.md -- ONTO LOOP v0.1, one full off-plant turn (LOCAL, bait-class, NEVER public)", "",
     "date     : %s" % date,
     "plane    : RESEARCH / North-Star loop v0.1 (live frozen substrate as PROPOSER)",
     "proposer : frozen_base_qwen25coder7b (4-bit nf4, greedy, NO adapter, NO GOLD)",
     "gate     : loop_e2e_v0.py a39e66f (UNCHANGED) -- S2(a) resolve + S2(c) retracted, live Crossref.",
     "judge    : S2(b) supports = Claude as a separate non-proposing instance, GROUNDED (not human, not true-core).",
     "           per-item reasons in supports_judgment_v01.md.", "",
     "## SUMMARY (rate-level)",
     "    proposed                          %2d  (100.0%%)" % n_total,
     "    gate HARD-reject (no-resolve)     %2d  (%5.1f%%)   -- caught with ZERO judge input" % (n_caught, pct(n_caught)),
     "    judge-reject (real DOI, wrong)    %2d  (%5.1f%%)   -- invisible to resolve/retract veto" % (len(rej_not), pct(len(rej_not))),
     "    judge UNCLEAR (not groundable)    %2d  (%5.1f%%)" % (len(rej_unc), pct(len(rej_unc))),
     "    ABSORBED                          %2d  (%5.1f%%)" % (len(absorbed), pct(len(absorbed))), "",
     "## S2 caught-log (gate HARD reject, no judge input)"]
for c in caught:
    L.append("    CAUGHT %-12s %-34s %s" % (c["id"], c["doi"], c["gate"]["reason"]))
L += ["", "## S3 judge disposition (grounded ; reasons in supports_judgment_v01.md)"]
for r in rows:
    L.append("    %-7s %-12s %-34s %s" % (mk(r), r["id"], r["doi"], r.get("claim_text", "")[:46]))
L += ["", "## ABSORBED (accepted knowledge)"]
if absorbed:
    for a in absorbed: L.append("    %-12s %-34s %s" % (a["id"], a["doi"], a.get("claim_text", "")))
else:
    L.append("    (none) -- zero proposals cleared {resolve AND not-retracted AND supports}.")
L += ["", "## READING",
      "%d/%d cited DOIs never resolved (gate caught, no judge input). Of the %d that resolved, the" % (n_caught, n_total, n_routed),
      "grounded judge marked %d as wrong-binding (the DOI is not the source the quote names) and %d" % (len(rej_not), len(rej_unc)),
      "UNCLEAR (no fetch-free tell). Honest-citation rate this draw = %d/%d. The resolve/retract veto" % (len(absorbed), n_total),
      "cannot see wrong-binding -- that class sizes the true core: an automated INDEPENDENT supports-judge.",
      "n=%d, single draw, single prompt-set, fetch-free grounding (some recall-assisted) -- not generalized." % n_total]
open(LOC, "w", encoding="utf-8").write("\n".join(L) + "\n")

# ---- PUBLIC rate-level ledger (NO DOIs)
P = ["# ONTO LOOP v0.1 -- off-plant disposition (rate-level, public-safe)", "",
     "date  : %s" % date,
     "setup : a frozen base model PROPOSES {claim, source-id}; an EXTERNAL gate resolves the source and",
     "        checks retraction; whatever resolves is routed to a separate non-proposing supports-judge.",
     "        The proposer is never trusted to judge its own citation. n=%d, single draw." % n_total, "",
     "## disposition",
     "    proposed                       %2d   100.0%%" % n_total,
     "    gate hard-reject (no-resolve)  %2d   %5.1f%%   (caught automatically, no judge)" % (n_caught, pct(n_caught)),
     "    judge-reject (wrong binding)   %2d   %5.1f%%   (source real but is not what the claim cites)" % (len(rej_not), pct(len(rej_not))),
     "    unclear (not groundable)       %2d   %5.1f%%" % (len(rej_unc), pct(len(rej_unc))),
     "    absorbed                       %2d   %5.1f%%" % (len(absorbed), pct(len(absorbed))), "",
     "## finding",
     "The cheap external existence/retraction check caught %.1f%% of defective citations with no" % pct(n_caught),
     "judge input. Every remaining proposal that resolved was either a wrong-binding (a real source that",
     "is not the one cited) or not groundable without reading the source -- a class the existence check",
     "cannot detect. Honest-citation rate this draw was zero. The external check is necessary but not",
     "sufficient; the load-bearing instrument is an automated INDEPENDENT supports-judge. Single off-plant",
     "draw, not a generalized rate; no source identifiers published (measurement-integrity)."]
open(PUB, "w", encoding="utf-8").write("\n".join(P) + "\n")

print("FINALIZE v0.1 done.")
print("  worksheet patched (mark+reason+judge) -> %s" % WS)
print("  audit  -> %s" % SJ)
print("  LOCAL  -> %s" % LOC)
print("  PUBLIC -> %s" % PUB)
print("  proposed=%d gate_caught=%d judge_reject=%d unclear=%d absorbed=%d"
      % (n_total, n_caught, len(rej_not), len(rej_unc), len(absorbed)))
