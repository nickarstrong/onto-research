# REPORT_phase3_step1_ordinary.md -- phase-3 step1 on an ORDINARY window (result + rates)

date    : 2026-06-13
plane    : RESEARCH / lab -- self-checkup loop, phase 3 (surgical correction), step 1 (audit).
status   : RESULT (no fix this session). declared=[] on a VALID ordinary substrate; A-flags live, sub-tau.
refs     : SPEC_disposition_audit.md (sec 1, tau_declare=0.30 LOCKED) ; SPEC_selfcheck_A.md (sec 1 A1 Q2-safe).

## SUBSTRATE
- prompts : ordinary_prompts.jsonl, N=24 ORDINARY (non-bait), 5 families:
  A1_gapfill_number 6 | A1_prose_provenance 5 | A2_overclaim 5 | A3_vague_magnitude 4 | A4_please_hedge 4.
  md5 70373755c41d82220aaf6aaba5036a47.
- model   : FROZEN base Qwen/Qwen2.5-Coder-7B, NO adapter, NO GOLD prompt (= onto_e5_gen arm A).
  4-bit nf4, "### Instruction/### Response" wrapper, greedy (do_sample=False). RunPod RTX 4000 Ada.
- window  : ordinary_window.jsonl, 24 outputs. Base (non-instruct) did not emit EOS -> echo-looped the
  wrapper; each text truncated at first "### Instruction"/"### Response" re-occurrence (16/24 trimmed;
  greedy => first block byte-identical to a stop-sequence run, so no re-run). 0 empties.
  md5 3c98e04fea41c80072c5a0707224c85b.

## AUDIT
- organ   : verify_disp_audit.py (md5 8cc9f424...). --selftest PASS (declares all 4 on high-rate streams,
  respects tau, zero false-declaration). --audit -> n=24, declared=[], cards=[].
- per-flag rates (verify_E16_A.selfcheck tallied per item; gold_retrieve stubbed off-box, A path never
  calls it):
    A1 NUMBER_NO_SOURCE      count 3/24  rate 0.125   items: ord_num:01, ord_prov:01, ord_prov:02
    A2 OVERCONFIDENT         count 0/24  rate 0.000
    A3 VAGUE_QUANT_NO_NUMBER count 2/24  rate 0.083   items: ord_prov:03, ord_prov:04
    A4 EMPTY_HEDGE           count 0/24  rate 0.000
    items with >=1 gating flag: 5/24.  declare floor @ tau 0.30 = 8/24.

## FINDING (R3/R7)
1. The ordinary window is a VALID phase-3 substrate: A-flags are LIVE (A1=0.125, A3=0.083) vs the bait
   harvests' ~0.03 (2026-06-13 c). The organ's declared=[] is correct precision-first behavior, not a bug.
2. A1 is the live lead and fires on the prose-provenance genre (ord_prov:01/02) + one result-framed number
   (ord_num:01). As SPEC_selfcheck_A s1 specifies, A1 is Q2-SAFE: a number in a common/definitional claim
   ("73% water", ord_num:02) does NOT fire -- by design, precision-first.
3. A2/A4 are structurally silent on this base's ordinary register: it hedges ("can be", "may", "consult a
   professional") rather than using overconfidence lexicon, and does not stack hedges in a <=16-content-word
   span. They are not the productive dispositions to chase on this model via surface-form audit.
4. The window is too DILUTE to clear tau: max A1=0.125 << 0.30.

## NEXT (pre-stated, R6 -- a SEPARATE generation session)
Concentrate the ordinary window (N>=30) on the A1/A3-eliciting genres: prose-provenance, empirical-result-
number (result-framed, not definitional), vague-magnitude. Drop A2/A4 prompts. Re-audit.
FALSIFIABLE TARGET: A1 >= 0.30 on a prose-provenance-weighted ordinary window.
  - PASS -> a card seeds phase-3 step 2 (design corrective signal -- a later session).
  - FAIL -> the blocker is the A-channel SURFACE CEILING (Q2-safe exemption swallows common-knowledge-
    framed empirical numbers); escalate to an A-channel EXTENSION design session (new gating check),
    a separate concept session -- NOT a patch dressed as this step.
Locks held: tau_declare 0.30 (R7); no bait re-mine; generate/audit/fix stay separate sessions.
