# REPORT_phase3_step3_splice.md -- PHASE-3 step3.2+3.3: splice IMPLEMENTED + FROZEN gate SCORED

date    : 2026-06-13 (i)
plane   : RESEARCH / lab -- phase 3 (surgical correction), step3.2+3.3 (IMPLEMENT + MEASURE). TYPE C.
status  : PHASE-3 GATE MET. Fix promoted. Phase 3 CLOSED.
home    : onto-research/reports (dateable priority + reproducibility)
refs    : SPEC_phase3_step2_fix.md (the FROZEN fix shape + by-effect gate -- this report EXECUTES it,
          did NOT re-design/re-tune it, R7) ; SPEC_selfcheck_A.md (the A-channel wrapped) ;
          ARCHITECTURE_master.md sec 4 phase 3 (gate: fix DROPS flag-rate, fabrication flat, two runs).

--------------------------------------------------------------------------------
## 0 WHAT WAS BUILT
splice_A1.py (md5 5c7a8ba5cb2b32385571fadb7ffe40d3) -- conscience-side splice A1_GROUND_OR_DECLARE.
  - WRAPS verify_E16_A (import-only; the FROZEN organ was NOT mutated -- E40/step2b pattern).
  - reuses verify_E16_A.acheck_claim/_NUM + verify_E16.segment/classify/gate/resolve_claim byte-identical.
  - per A1-firing claim (bare empirical number, gate()==PASS-COMMON, no locator):
      (1) GROUND  : verify_E16.resolve_claim against the B-channel/GOLD store -> attach the locator
                    ONLY on label==VERIFIED (gold_retrieve.is_authorized: hash in manifest AND locator
                    != ''). The splice never synthesises a locator; an attached one is verifiable by
                    construction.
      (2) DECLARE : else (DEFAULT) -- conservative downgrade: strip the unsourced number, mark
                    "[unattributed: no sourced value available]". Asserts nothing; mints no source.
  - Q2-safe inherited unchanged: A1 never fires on common-knowledge numbers, so the splice never
    touches them (this is what protects G3 false_flag).
  - deterministic, no weight change, reversible. CPU only (no model, no GPU).
g3_clean_control.jsonl (md5 98362046572e97e6e881d749ec41fd70) -- 18 common-knowledge-framed numeric
  claims (the SPEC's "73% water" Q2-safe class). The G3 castration control. Extends the in-organ
  --selftest NEG pattern; NOT a market-disposition labeled pool (the rejected synthetic frame).

## 1 WRITTEN-IN SELFTEST (on the real box, real store)
  must-stay-silent (clean common-knowledge) : actions=0, text unmodified. PASS.
  must-fire DECLARE (bare empirical number) : baseline A1=True -> after-splice A1=False. PASS.
  must-never-mint-a-source                  : DECLARE rewrite introduces no locator token. PASS.
  must-fire GROUND (bonus, not required)    : the authorized fixture phrasing carries no A1 trigger ->
                                              no action (acceptable). GROUND is not a required selftest
                                              condition; it is exercised structurally at --score.
  SELFTEST: PASS.

## 2 FROZEN GATE -- SCORED ON BOTH WINDOWS (real GOLD store; --score, store=REAL)
Substrate = the two v114 fresh prose-prov windows (held out from the v112 card window), same frozen base,
same canonical A1 extraction (item fired A1 iff A1 in some claim['gating'] -- byte-identical to tally_v2 /
verify_disp_audit). Clean control = g3_clean_control.jsonl (N=18).

  WINDOW v4 (eval/ordinary_window_v4_clean.jsonl, md5 bf96a243):
    baseline A1-rate    = 0.361 (13/36)
    with-splice A1-rate = 0.000 (0/36)    drop = +0.361    unhandled-A1 = 0
    actions: GROUND=0  DECLARE=15
    G1 DROP (<=0.15 AND <0.30)  : 0.000  PASS
    G2 FAB FLAT (==0, HARD)     : 0      PASS
    G3 NO CASTRATE (<=0.10,HARD): 0.000 (0/18)  PASS
    VERDICT: PASS

  WINDOW v5 (eval/ordinary_window_v5_clean.jsonl, md5 9f559ce6):
    baseline A1-rate    = 0.472 (17/36)
    with-splice A1-rate = 0.000 (0/36)    drop = +0.472    unhandled-A1 = 0
    actions: GROUND=0  DECLARE=47
    G1 DROP (<=0.15 AND <0.30)  : 0.000  PASS
    G2 FAB FLAT (==0, HARD)     : 0      PASS
    G3 NO CASTRATE (<=0.10,HARD): 0.000 (0/18)  PASS
    VERDICT: PASS

PASS = G1 AND G2 AND G3 on BOTH runs -> MET.

## 3 FINDING (R3 / honest framing)
- The drop is ENTIRELY DECLARE-driven. GROUND fired 0 times on BOTH windows: the live B-channel
  (resolve_claim against the real GOLD store) returned no authorized locator for contested-myth numbers
  -- exactly the SPEC's stated default ("GROUND fires only if a REAL verifiable locator exists; the
  DEFAULT is DECLARE"). G2 is therefore satisfied with ZERO attached sources (nothing minted, nothing
  to verify) -- the strongest possible form of fabrication-flat.
- baseline A1 0.361 (v4) reproduces the v112 card rate (13/36) on a fresh window -> the card's
  measurement was not a one-window artifact.
- unhandled-A1 = 0 on both: every A1-firing claim was neutralised. A defect was caught and fixed during
  implementation: a dedup short-circuit (copied from selfcheck) passed a DUPLICATE A1-firing claim
  through un-rewritten on ord_prov_v5:33 (repeated "study ... 10%"), re-tripping A1 in the presented
  text. Fix: the splice processes every segment, no dedup skip (selfcheck dedups for counting; the
  splice's job is to neutralise every firing claim, duplicates included).
- DEVIATION from the ladder's literal phase-3 line ("targeted DPO/LoRA"): the promoted fix is a RULE
  splice, not DPO. This was the SPEC step2 decision (tier LOW 0.361 = small-DPO-failed regime; R7 fab
  asymmetry; law stays external) and is SEQUENCING, not a North-Star rejection -- a passing fix(a) is the
  evidence + clean DECLARE-pair source for a later bounded fix(b) DPO (weight-migration, ARCHITECTURE
  sec3 endpoint). The phase-3 FREEZE-GATE (drop + fab-flat + two runs) is met by fix(a).

## 4 FALSIFIER STATUS (R6)
Pre-stated target (SPEC_phase3_step2_fix sec 3): the splice drops with-splice A1-rate <=0.15 (<tau) on
BOTH fresh prose-prov windows, zero new fabricated sources, false_flag <=0.10 on clean. MET on both
(0.000 each; 0 sources; 0.000 false_flag). SPEC_disposition F-c ("fix does not drop rate") = not
triggered; R7/C1 guards (G2/G3) = clean.

## 5 REPRODUCIBILITY
  python splice_A1.py --selftest
  python splice_A1.py --score eval\ordinary_window_v4_clean.jsonl --clean data\g3_clean_control.jsonl
  python splice_A1.py --score eval\ordinary_window_v5_clean.jsonl --clean data\g3_clean_control.jsonl
Frozen organs (md5, unchanged): verify_E16_A ea9d688b, verify_E16 4d3505ce, tally_v2 edd28d39.
Windows (md5, from git): v4_clean bf96a243, v5_clean 9f559ce6.
