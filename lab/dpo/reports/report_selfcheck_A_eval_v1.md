# report_selfcheck_A_eval_v1.md -- A-CHANNEL v0 honest >=20+20 eval (PASS vs frozen SPEC)

date   : 2026-06-15
plane  : RESEARCH / self-checkup loop v0 (G3 self-consistency)
home   : onto-research/reports (dateable priority + reproducibility)
spec   : SPEC_selfcheck_A.md (FROZEN; s2 bars BYTE-IDENTICAL to v0; this run touches NO predicate/SPEC byte)
impl   : verify_E16_A.py (md5 ea9d688b997aefdaebd06a78f3e49e50; UNCHANGED this run; organ verify_E16 import-only)
set    : eval/_local/labeled_A.jsonl (Founder-labeled, LOCAL ONLY; md5 f5427db15ff14b6b198648266ca42d75; 20 dirty + 20 clean)
super  : supersedes report_selfcheck_A_eval_v0.md (n=11+11, set md5 8d50ea81...); v0 RETAINED for dateable priority.

--------------------------------------------------------------------------------
## 0 RESULT
PASS vs frozen SPEC bars (s2, byte-identical):
  false_flag_rate = 0.000  (0/20 clean)   [HARD C1 bar <= 0.10]  PASS
  detect_rate     = 0.900  (18/20 dirty)  [TARGET R1 bar >= 0.60] PASS
  VOID guard      : >=1 dirty & >=1 clean present; per-check fires A1=5 A2=5 A3=5 A4=4 (each >=1). CLEAR.
  selftest        : 4/4 POS FLAGGED + 5/5 NEG CLEAN (harness != VOID).
REPRODUCED BYTE-IDENTICAL: sandbox (stubbed gold_retrieve) == box C:\Projects\onto-research\lab\dpo (2026-06-15).

--------------------------------------------------------------------------------
## 1 CI HONESTY (R1/R2, no relabel to green)
n = 20 dirty + 20 clean = the SPEC s5 honest floor (was 11+11 in v0).
  detect 18/20 = 0.900 ; Wilson 95% CI ~ [0.70, 0.97].
  false_flag 0/20 = 0.000 ; rule-of-three 95% upper ~ 0.15.
Point-PASS on both bars is real and tighter than v0 (v0 ff upper ~0.27, detect ~[0.52,0.95]).
HONEST GAP: false_flag 95% upper 0.15 STILL exceeds the 0.10 HARD bar. The bar is met on the point
  estimate, NOT yet CI-guaranteed. To CI-clear the HARD bar at 95% needs ~30 clean with 0 FP
  (rule of three: 3/30 = 0.10). Reported as-is; NOT relabeled.

--------------------------------------------------------------------------------
## 2 MISSES (R7, by-design, not a blind spot)
2/20 dirty MISSED = d_miss_1, d_miss_2 -- the pre-declared honest-miss items (human-dirty with no
  surface cue the deterministic regex can catch; the non-circular detect probe). Identical disposition
  to v0. On the 18 cue-bearing dirty: 18/18 FLAGGED. The 0.900 = honest detect, not a new gap.

--------------------------------------------------------------------------------
## 3 DELTA vs v0
  v0 (2026-06-12, n=11+11): false_flag 0.000, detect 0.818.
  v1 (2026-06-15, n=20+20): false_flag 0.000, detect 0.900.
Frozen bars byte-identical; only n, point-detect, and CI changed. patch_A2 (v0 s3) carried unchanged;
  no new predicate edit. v0 stays in tree for priority/provenance.

--------------------------------------------------------------------------------
## 4 CARRY (R3)
- ff CI-clear of the 0.10 HARD bar needs the clean class grown to ~30 (0 FP) -- the next honest increment.
- The strengthened attributed-clean negatives held: c_adv_a2_1 CLEAN (the A2 attribution-exemption
  shortcut-blocker stays intact for the G4+/DPO stage when A-flags become training signal).
- Coverage = 4 gating checks (A1-A4), not full R1-R18. detect is a v0 floor, not a ceiling claim.
