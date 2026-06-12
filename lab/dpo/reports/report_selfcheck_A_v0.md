# report_selfcheck_A_v0.md -- A-channel self-consistency checker, BUILD readout

date    : 2026-06-12
plane   : RESEARCH / self-checkup loop v0 (G3)
pair    : verify_E16_A.py  +  SPEC_selfcheck_A.md (FROZEN bars)
session : pivot from verifier-v1 step3 routing -> rev2 reorder (L5 is parallel, not a v0 blocker)

## WHAT WAS BUILT
verify_E16_A.py -- the A-channel (self-consistency) checker. Runs the discipline on the system's
OWN output with NO source, NO model, NO network. First cognitive organ of the self-checkup loop.
Reuse is IMPORT-ONLY over frozen verify_E16 (segment/classify/gate/_norm/PROVEN/ABSTAIN) -- the
organ is not mutated (E40/step2b pattern). New logic = 4 gating + 2 advisory deterministic A-checks.

## WHY THIS, NOT L5 (rev2 R15 self-correction)
STRATEGY rev2 split the discipline: A self-consistency needs no DOI/corpus and was UNBUILT ; B
grounding already exists (L4 fa 0.0333). L5/step3 only broadens B -- it is a PARALLEL track, not a
prerequisite. The high-value move is assembling v0, starting with the cheapest unbuilt piece (A).
L5 truth-set authoring continues offline in parallel (not blocked by this).

## SELFTEST RESULT (synthetic fixture ; --selftest)
POSITIVES 4/4 FLAGGED (one gating check each, no cross-fire):
  A1 number-no-source | A2 overconfident-ungrounded | A3 vague-quant-no-number | A4 empty-hedge
NEGATIVES 5/5 CLEAN: grounded-number(doi+date+org), calibrated-hedge, common-constant(100C),
  common-fact(triangle 3 sides), clean-attribution(Smith et al. 2021, Journal).
Reproduced BYTE-IDENTICAL on real verify_E16 (box) == sandbox (stubbed store). VERDICT: PASS.
=> F-a (detector not blind) and F-b (clean output not corrupted) closed on the synthetic set.

## BARS (pre-registered, frozen in SPEC_selfcheck_A.md BEFORE real data)
HARD  false_flag_rate <= 0.10 (C1 precision-first, the trust bar).
TARGET detect_rate >= 0.60 (above the rev2 ">50%" bootstrap floor).
VOID guard: >=1 dirty & >=1 clean ; each gating check A1-A4 exercised by >=1 dirty.

## DEFERRED (next session, gated)
Real eval needs a Founder-labeled set eval/_local/labeled_A.jsonl ({id,text,label}) -- the Founder
judges dirty/clean (R7: not fabricated). dirty must collectively exercise A1-A4 ; clean must include
the N-class shapes (grounded number, calibrated hedge, common-knowledge, clean attribution).
Then: python verify_E16_A.py --eval eval/_local/labeled_A.jsonl  -> rates vs frozen SPEC bars.

## NOT IN v0 SCOPE (named)
G1 self-input wrap, G2 controller (initiative trigger), G4 patch-gen (F-c/F-d). v0 = the A-detector only.
The per-claim flag record is the audit seed those stages consume.
