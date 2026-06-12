# SPEC_selfcheck_A.md -- A-CHANNEL self-consistency checker, PRE-REGISTERED bars (FROZEN)

date   : 2026-06-12
plane  : RESEARCH / self-checkup loop v0 (G3 self-consistency)
home   : onto-research/reports (dateable priority)
status : FROZEN (re-frozen 2026-06-12 after A2 tighten; s2 bars BYTE-IDENTICAL, only s5 records the executed fix). Results never relitigate bars (R7).
implements : verify_E16_A.py  (A-channel ; import-only over frozen verify_E16 ; no store/model/network)
refs   : STRATEGY_selfcheckup_loop_v0.md rev2 (sec1 discipline-split, sec5 bootstrap C1/C2, sec7 falsifiers)

--------------------------------------------------------------------------------
## 0 WHAT THIS GATES
The A-channel runs the discipline on the system's OWN output with NO source/corpus/DOI.
It is the cheapest, first cognitive organ of the self-checkup loop (rev2: build A before broadening B/L5).
B-channel (grounded) is verify_E16 (L1-L3) + verify_E16_L4 (L4) and is NOT in this SPEC.

--------------------------------------------------------------------------------
## 1 CHECK ROSTER (frozen v0)
GATING (changes the item verdict ; fire only on a clear violation, C1 precision-first):
  A1 NUMBER_NO_SOURCE        (R4/R17) : empirical-result number (PROVEN cue OR "<n>% of <sample>"),
                                        gate()==PASS-COMMON (no locator/date/org). Q2-safe: a bare
                                        number in a definitional/common claim does NOT fire.
  A2 OVERCONFIDENT_UNGROUNDED (R2)    : overconfidence lexicon on an ungrounded (PASS-COMMON) claim.
  A3 VAGUE_QUANT_NO_NUMBER    (R1)    : vague quantifier + empirical noun, no number present.
  A4 EMPTY_HEDGE              (R18)   : >=2 distinct hedges in a short (<=16 content-word) span.
ADVISORY (reported, NEVER gates -- mirror L5 I.3 method leg ; deterministically FP-prone):
  A5 UNFALSIFIABLE_UNIVERSAL  (R6)    : unbounded universal assertion, no number.
  A6 INTERNAL_CONTRADICTION   (R17)   : same normalized subject asserted and negated across claims.

item verdict = FLAGGED iff >=1 gating flag fired ; else CLEAN. Advisory never changes the verdict.

--------------------------------------------------------------------------------
## 2 PRE-REGISTERED BARS (for --eval over a Founder-labeled set)
Labeled set = jsonl, one obj/line: {"id":.., "text":.., "label":"dirty"|"clean"}.
  dirty = the Founder judges this output to carry a real self-consistency violation (should FLAG).
  clean = grounded / calibrated / common-knowledge / properly-attributed (should PASS).

BARS:
  (HARD) false_flag_rate (clean wrongly FLAGGED) <= 0.10    -- C1 precision-first. The trust bar.
  (TARGET, R1) detect_rate (dirty correctly FLAGGED) >= 0.60 -- above the rev2 sec5 ">50%" floor.
                                                               Wide CI on small sets ; report the CI.
VOID GUARD (--eval fails closed if violated):
  - >= 1 dirty AND >= 1 clean present (no clean verdict over an empty class).
  - each gating check A1-A4 exercised by >= 1 dirty item (per-check anti-blindness, L5 "every class >=1").
SIZE (R1, not a frozen bar): floor to run = >=5 dirty + >=5 clean + all 4 gating checks covered.
  honest = >= 20 dirty, >= 20 clean. Smaller -> wider CI, state it.

PASS = (false_flag_rate <= 0.10) AND (detect_rate >= 0.60) AND VOID guard clear.
The C1 HARD bar dominates: a high detect_rate with false_flag_rate > 0.10 is FAIL (castration risk).

--------------------------------------------------------------------------------
## 3 FALSIFIERS (v0 is theatre, not cognition, if:)
  F-a : a deliberately-bad output trips NO gating flag        -> detector blind in-loop (VOID).
  F-b : a clean output trips a gating flag                    -> over-prune / castration (breaks C1).
  F-c : (G4 scope) a patch does not raise tier/calibration    -> patch is hallucination. NOT in v0.
  F-d : (G4 scope) audit trail != actual verdicts             -> self-model asserted. NOT in v0.
v0 closes F-a + F-b. The per-claim flag record (verify_E16_A.selfcheck -> claims[]) is the audit seed for G4.

--------------------------------------------------------------------------------
## 4 SELFTEST EVIDENCE (synthetic, no network/store ; proves harness != VOID before real data)
verify_E16_A.py --selftest : 4/4 positives FLAGGED (one per gating check, no cross-fire) ;
  5/5 negatives CLEAN (grounded number, calibrated hedge, common constant, common fact, clean attribution).
Reproduced BYTE-IDENTICAL: sandbox (stubbed store) == real verify_E16 on box (2026-06-12). PASS.

--------------------------------------------------------------------------------
## 5 KNOWN LIMITATIONS (R3)
- A2 always/never FP CONFIRMED + FIXED 2026-06-12 (Founder clean-set eval, 11+11). Both false-flags
  traced to A2: c_adv_a2_2 "I will always be grateful" ; c_adv_a2_1 "definitively proven in Euclid's
  Elements". Fix (patch_A2.py, re-frozen here): (1) always/never REMOVED from _OVERCONF -- unbounded
  universals belong to A5 advisory, not epistemic overconfidence; (2) attribution exemption -- overconf
  with proof-verb + preposition + Capitalized Named source (claim+source-of-proof) does NOT gate.
  Post-fix: false_flag 0.182 -> 0.000 ; detect 0.818 unchanged (no dirty held on always/never alone);
  selftest 4/4 + 5/5 unchanged. Accepted recall cost: bare "X always cures" no longer gates A2 (-> A5).
  CI caveat: n=11+11 -> false_flag 95% upper ~0.27, detect 95% ~[0.52,0.95]; honest gate needs >=20+20.
- A5/A6 advisory by design: deterministic falsifiability/contradiction detection is FP-prone -> never gated in v0.
- Coverage is 4 gating checks, not the full R1-R18. detect_rate is a v0 floor, not a ceiling claim.
