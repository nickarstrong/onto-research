# SPEC: DENOMINATOR RE-CUT v1

Plane: organism-0 Phase 4, temporal-channel promotion gate.
Status: SPEC (Founder executes the cut). Supersedes nothing; defines the honest G3 denominator.
Trigger: "LABA, DENOMINATOR RECUT".

---

## 0  PURPOSE

CONFIRM (same-sentence sound, D1'' closed) + REFUTE (D3+D4 restrained) are bar-clean on the
probe set (REPORT_temporal_probe_v5, OVERALL PASS). The blocking question for PROMOTION
(gating vs advisory) is a REAL G3 yield denominator. The S4 held-out set (N=20) cannot serve
as that denominator. This spec defines the replacement and the deterministic scoring that
decides promotion.

---

## 1  FROZEN DIAGNOSIS (banked, R15 — NOT recomputed this session)

S4 held-out, N=20, Founder-labeled at v199:
- absorb-ceiling with sound CONFIRM = 3/20 = **0.150 < 0.20** (banked, report v5 sec 7).
- 3 CLEAN-and-supported (absorbable): heldout_09 (1887), heldout_14 (1900), heldout_16 (1847).
  - 14: year in abstract -> specifics-gate pass (baseline absorb, no temporal).
  - 09, 16: year NOT in abstract -> recovered by temporal CONFIRM (2/2).
- 2 DIRTY-supported, correctly NOT absorbed: heldout_03 (1925 wrong-date), heldout_18 (Cleverbot).
- 15 non-absorbable: 2 gate-reject (404) + 4 B2-NOT + 9 B2-UNCLEAR (retrieval/support failures,
  not temporal-addressable).

Conclusion: 17/20 of the denominator can never absorb (should-reject or un-retrievable). The
0.20 bar requires >=4/20; the set tops out at 3/20 independent of channel quality. The
denominator is structurally dead for measuring this channel.

---

## 2  ROOT CAUSE

G3 (yield >= 0.20) is a PIPELINE gate: "does the loop absorb enough to learn." Its denominator
must be claims that COULD legitimately absorb. The S4-20 denominator instead counts
should-reject (DIRTY) and cannot-retrieve claims, so the achievable yield is bounded by the
CLEAN-and-retrievable fraction, not by channel recovery. Yield here measures set composition,
not the lever under test.

---

## 3  TWO-METRIC SPLIT (engineer decision — do NOT redefine G3 per-component)

Re-cutting the denominator to "date-bearing only" would game the pipeline gate (move the bar to
pass). Rejected. Instead: one honest pipeline number + one honest component number.

- **M1  PIPELINE G3** (definition unchanged; new denominator only)
  `M1 = CLEAN_absorbed / N_recut`, bar **>= 0.20**. This is the promotion gate.
  Computed channel-ON and channel-OFF; `lift = M1_on - M1_off`.

- **M2  CHANNEL RECOVERY** (component, advisory — never a pipeline gate)
  `M2 = temporal_recovered / CLEAN_date_bearing_year_not_in_abstract`.
  Frozen S4 reference: 2/2 = 1.000 (09, 16). Reports whether the channel works where it applies;
  says nothing about whether it is load-bearing for the pipeline.

- **fa_live** (HARD invariant, unchanged): `fabricated_absorbed / DIRTY_in_recut <= 0.10`.

---

## 4  RE-CUT REQUIREMENTS (Founder-owned — E15 boundary)

The cut and the CLEAN/DIRTY labels are authored by the Founder. Claude authors NEITHER claims
NOR labels. Mechanical structural fields (date-bearing, year-in-abstract) are derived by the
scorer, not labeled.

Requirements:
1. **Source distribution = live organism-0 cycles** (same generator/topic distribution as S2).
   NO artificial enrichment of date-bearing claims. Enrichment contaminates G3 (would measure a
   hand-picked population, not the loop). Representativeness is the validity condition.
2. **Size N_recut >= 40.** At N=40 a single claim moves M1 by <= 0.025, giving the 0.20 bar
   resolution. N=20 gave 0.05 granularity (one claim = 1/4 of the bar).
3. **Founder labels:** CLEAN / DIRTY per claim. The only labeling act in this plane.
4. **DIRTY date-controls present** (non-empty recall set, E15): at least a handful of DIRTY
   claims carrying a wrong/fabricated year, so fa_live is measurable (not vacuous).
5. **Held-out hygiene (3.2):** local/private only. NEVER to public git (future pretrains eat it).

---

## 5  ACCEPTANCE CRITERIA (cut is VALID before scoring)

The scorer aborts with INVALID if any fails (no scoring on a bad set):
- A1  N_recut >= 40.
- A2  CLEAN_absorbable_in_principle >= ceil(0.20 * N_recut) + margin>=2, i.e. the set is
      capable of clearing 0.20 if the channel works (else the cut repeats the S4 defect).
- A3  DIRTY_with_year >= 4 (fa_live measurable on a non-empty recall set).
- A4  date_bearing_fraction within the live-cycle band [report from S2; not hand-set] — guards
      against accidental enrichment. If the live band is unknown, Founder records the observed
      fraction; scorer only flags, does not block, on A4.

---

## 6  WHAT CLAUDE COMPUTES ON RETURN (deterministic, one run, no re-label)

Input: `recut_labeled.jsonl` (Founder) + temporal verdicts from one frozen channel run.
Scorer (`o0_denominator_recut_score.py`) emits, deterministically:
- M1_on, M1_off, lift
- M2
- fa_live
- acceptance A1-A4 PASS/FAIL/FLAG

No generation, no labeling, no re-run inside the scorer. Pure aggregation (E15-safe).

---

## 7  PROMOTION DECISION RULE

CONFIRM/REFUTE promote from ADVISORY to **GATING** iff ALL hold on the valid RE-CUT:
- `M1_on >= 0.20`  (pipeline gate cleared with channel)
- `lift > 0`       (channel is the reason, not the set)
- `fa_live <= 0.10` (no fabrication absorbed — HARD)

Else: channel STAYS ADVISORY. Correct outcome if the live distribution simply lacks enough
date-bearing claims for the channel to be load-bearing — it helps where it applies (M2 high)
without carrying the pipeline gate. Not a failure of the channel; a fact about the workload.

---

## 8  STOP BOUNDARY (this session)

This plane produces SPEC + scorer ONLY. No new claims, no labels, no pipeline re-run, no model
eval. The killing number (S4 ceiling 0.150 < 0.20) is banked, not recomputed. Founder executes
the cut next; scoring is a separate, single-number session on the returned labeled set.

---
*SPEC_denominator_recut_v1 - 2026-06-21 - honest G3 denominator + two-metric split (M1 pipeline /
M2 component) + promotion rule. S4-20 denominator declared structurally dead (ceiling 0.150).
Cut + labels Founder-owned (E15). Scorer = pure aggregator. Promotion gate: M1_on>=0.20 AND
lift>0 AND fa_live<=0.10.*
