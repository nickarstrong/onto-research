# report_selfcheck_A_eval_v0.md -- A-CHANNEL v0 real eval + A2 re-freeze (PASS vs frozen SPEC)

date   : 2026-06-12
plane  : RESEARCH / self-checkup loop v0 (G3 self-consistency)
home   : onto-research/reports (dateable priority + reproducibility)
spec   : SPEC_selfcheck_A.md (FROZEN; re-frozen this date, s2 bars byte-identical -- A2 tighten in s5)
impl   : verify_E16_A.py (A2 tightened via patch_A2.py ; organ verify_E16 import-only, untouched)
set    : eval/_local/labeled_A.jsonl (Founder-labeled, LOCAL ONLY; md5 8d50ea81b30f8c08d2a1135a304dca1e)

--------------------------------------------------------------------------------
## 0 RESULT
PASS vs frozen SPEC bars:
  false_flag_rate = 0.000  (0/11 clean)   [HARD C1 bar <= 0.10]  PASS
  detect_rate     = 0.818  (9/11 dirty)   [TARGET R1 bar >= 0.60] PASS
  VOID guard      : >=1 dirty & >=1 clean present; all 4 gating checks A1-A4 exercised. CLEAR.
CI caveat (R1/R2): n=11+11 is small. false_flag 95% upper ~0.27 (rule of three);
  detect 95% ~[0.52,0.95] (Wilson). Point-PASS is real; honest gate needs the >=20+20 set.

--------------------------------------------------------------------------------
## 1 SET COMPOSITION (11 dirty + 11 clean)
dirty exercises every gating check: A1 x2 (d_a1_1/2), A2 x2 (d_a2_1/2), A3 x2 (d_a3_1/2),
  A4 x2 (d_a4_1/2), A1+A2 combo (d_combo_1), + 2 honest-miss (d_miss_1/2, human-dirty the
  regex is expected to miss -- non-circular detect probe).
clean spans grounded-number, calibrated-hedge, common-knowledge, clean-attribution, + 4 adversarial
  traps (c_adv_a1_1, c_adv_a3_1, c_adv_a2_1/2 -- the two A2 traps probe SPEC s5's named weakness).

--------------------------------------------------------------------------------
## 2 PER-ITEM DIAGNOSTIC (pre-fix run, the FP trace)
  9/9 non-miss dirty .... FLAGGED correctly (A1/A2/A3/A4/combo all fire on the right check)
  d_miss_1, d_miss_2 .... CLEAN (MISS) -- honest, by design (no surface cue for the regex)
  9/9 non-trap clean ..... CLEAN correctly
  c_adv_a2_1 ............. FALSEFLAG [A2]  "definitively proven in Euclid's Elements"
  c_adv_a2_2 ............. FALSEFLAG [A2]  "I will always be grateful"
=> both false-flags 100% attributable to A2 (not baseline drift). detect 0.818, false_flag 0.182 (FAIL).

--------------------------------------------------------------------------------
## 3 FIX (patch_A2.py ; Founder verdict + discriminator)
Founder ruled both texts CLEAN. Discriminator (2026-06-12): "claim + source-of-proof" = clean
  vs "claim + nothing" = dirty.
  Fix 1  always/never REMOVED from _OVERCONF -- they are unbounded universals (A5 advisory),
         not epistemic overconfidence. The A2<->A5 conflation was the c_adv_a2_2 FP.
  Fix 2  attribution exemption -- _PROOF_VERB (prov/establish/demonstrat/deriv/shown) AND
         _ATTRIB_SRC (in|by|via|through|from + optional articles/"proof in" + Capitalized Named
         source, case-sensitive) => overconfidence does NOT gate. Clears c_adv_a2_1.
Pre-delivery validation (isolated A2 logic, 9 cases): both clean + 2 strengthened adversarials
  ("conclusively proven in Euclid's Elements", "established by the proof in Book I of Euclid's
  Elements") do NOT fire; P2 selftest + d_a2_1/2 + d_combo_1 still fire. PASS.

--------------------------------------------------------------------------------
## 4 POST-FIX (re-run)
  selftest : 4/4 positives FLAGGED, 5/5 negatives CLEAN -- unchanged (no regression).
  eval     : detect 0.818 (unchanged) ; false_flag 0.000 (both FP cleared).
  git diff verify_E16_A.py : exactly 3 hunks (lexicon comment+line, exemption regexes, A2 clause);
             organ verify_E16 untouched.

--------------------------------------------------------------------------------
## 5 ACCEPTED COST + CARRY
- Recall cost: bare "X always cures" no longer gates A2 (now A5 advisory only). Accepted under
  C1 precision-first; detect has headroom (0.818 vs 0.60 bar).
- Dataset-leakage note (Founder, forward-looking): a learner could pick up surface "definitively->dirty".
  The deterministic checker has no such risk. When A-flags later become training signal (G4+/DPO),
  the attributed-clean cases (c_adv_a2_1, + the 2 strengthened variants) are the exact negatives
  that block the shortcut. Logged for that stage; add the strengthened variants to the >=20+20 set.
- Next gate: Founder-authored >=20 dirty + >=20 clean -> tighter CI on the same frozen bars.
