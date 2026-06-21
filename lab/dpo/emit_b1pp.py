#!/usr/bin/env python3
# emit_b1pp.py -- ORGAN EVIDENCE WIRE: render the auditor prompts for the §3 re-run.
#
#   B0   = bare auditor (baseline, frozen from the leverage harness) -- claim+abstract only.
#   B1'' = the DERIVED self-model organ prompt (auditor_B1prime_derived.txt, UNCHANGED) with
#          the out-of-band temporal-evidence rule SPLICED IN before its task trailer.
#
# The organ file is the COMPLETE §3 B1' prompt (bare + organ card + task). We do NOT re-wrap
# it (that double-prepended a second bare line and stranded the temporal rule after a
# task-close trailer). Instead we insert TEMPORAL_RULE between the organ card and the organ's
# own single task trailer -> one bare, organ card, temporal rule, one task. Clean delta.
#
# E15: no labels touched. Pure prompt rendering.
# Usage: python emit_b1pp.py [organ_card=auditor_B1prime_derived.txt]

import sys, os
import o0_leverage_probe_v0 as L   # frozen harness: BARE_CARD, AUDITOR_TASK

TEMPORAL_RULE = (
    "\n\nOUT-OF-BAND TEMPORAL EVIDENCE (per-specific scope).\n"
    "Each item carries a `temporal` field: an INDEPENDENT verification of the claim's YEAR tokens "
    "against Wikidata and Wikipedia (primary sources, beyond the retrieved abstract), in "
    "`temporal.per_year`, with any confirming text in `temporal.snippets`.\n"
    "SCOPE RULE -- a year result licenses ONLY the year sub-claim, NEVER the whole claim:\n"
    "- per_year CONFIRM : that YEAR is independently verified TRUE. Treat the YEAR -- and the "
    "subject entity it was checked against -- as SUPPORTED even if absent from the abstract. It "
    "does NOT support any OTHER specific in the claim.\n"
    "- per_year REFUTE  : that year is CONTRADICTED by the primary source -> the claim is DIRTY.\n"
    "- per_year ABSTAIN / COVERED_IN_ABSTRACT / none : no out-of-band year signal; judge the year "
    "against the retrieved evidence as usual.\n"
    "EVERY NON-YEAR SPECIFIC IS CHECKED ON ITS OWN EVIDENCE. An exact calendar day (e.g. "
    "\"February 28\"), a percentage/number/fraction (e.g. \"56.3%\", \"8/14\"), a name, or any other "
    "precise assertion is SUPPORTED only if it appears in the retrieved abstract OR the temporal "
    "snippet, or is otherwise corroborated. If such a specific is PRESENT in the claim but ABSENT "
    "from all evidence -> it is UNVERIFIED -> flag the claim DIRTY. A CORRECT YEAR DOES NOT EXCUSE "
    "A FABRICATED DAY, NUMBER, OR NAME.\n"
    "CLAIM VERDICT: CLEAN iff every specific is supported and none is contradicted; DIRTY if any "
    "specific is contradicted OR any precise non-year specific (exact date, number) is unverified. "
    "PRECISION-FIRST: when an exact day or number cannot be verified, prefer DIRTY."
)

TASK_HEAD = "\n\nFor each item output one JSON line"  # start of AUDITOR_TASK (organ + harness share it)

def main():
    organ_path = sys.argv[1] if len(sys.argv) > 1 else "auditor_B1prime_derived.txt"
    if not os.path.exists(organ_path):
        sys.exit(f"ABORT: organ card not found: {organ_path} "
                 f"(re-run selfmodel_compile emit-card if missing)")
    organ = open(organ_path, encoding="utf-8").read().replace("\r\n", "\n")

    # B0: clean bare baseline (single preamble + single task).
    b0 = L.BARE_CARD + L.AUDITOR_TASK + "\n"

    # B1'': splice TEMPORAL_RULE before the organ prompt's OWN task trailer. No re-wrap.
    i = organ.rfind(TASK_HEAD)
    if i == -1:
        body, task = organ.rstrip(), L.AUDITOR_TASK
    else:
        body, task = organ[:i].rstrip(), organ[i:].rstrip()
    b1pp = body + TEMPORAL_RULE + task + "\n"

    # contents guard: B1'' must carry exactly one bare preamble, the organ weakness, the
    # temporal rule, and exactly one task trailer.
    assert b1pp.count("BARE AUDITOR") == 1, "B1'' has %d bare preambles (want 1)" % b1pp.count("BARE AUDITOR")
    assert "fabricated-specifics" in b1pp, "organ weakness missing"
    assert "OUT-OF-BAND TEMPORAL EVIDENCE" in b1pp, "temporal rule missing"
    assert "A CORRECT YEAR DOES NOT EXCUSE" in b1pp, "per-specific scope rule missing (claim-level whitewash not removed)"
    assert b1pp.count("For each item output one JSON line") == 1, \
        "B1'' has %d task trailers (want 1)" % b1pp.count("For each item output one JSON line")
    # ordering: temporal rule must come BEFORE the task trailer.
    assert b1pp.index("OUT-OF-BAND TEMPORAL EVIDENCE") < b1pp.index("For each item output one JSON line"), \
        "temporal rule stranded after task trailer"

    open("auditor_B0_bare.txt", "w", encoding="utf-8").write(b0)
    open("auditor_B1pp.txt", "w", encoding="utf-8").write(b1pp)
    print("[emit] B0 bare              -> auditor_B0_bare.txt")
    print("[emit] B1'' organ+temporal  -> auditor_B1pp.txt  (1 bare / 1 task / temporal before task: OK)")
    print("[emit] ORDER (pre-reg): judge B0 on claims_blind_ev.jsonl FIRST, freeze, "
          "then B1'' on claims_blind_ev_temporal.jsonl. Auditor blind to labels.")

if __name__ == "__main__":
    main()
