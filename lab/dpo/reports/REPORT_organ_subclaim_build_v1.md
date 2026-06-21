# REPORT - Organ Subclaim Build (TYPE C) -- scope the year-CONFIRM, close fa_live, offline falsifier PASS

date    : 2026-06-21
pack    : v221 (from v220)
plane   : ROADMAP S3 -- BUILD the scope rule locked in v220 (REPORT_organ_subclaim_scope_v1)
type    : TYPE C. Build + OFFLINE self-test only. NOT the S3 eval (E15-blocked: label binding + soft-LLM).
binds   : REPORT_organ_subclaim_scope_v1.md (the locked spec) ; REPORT_organ_evidence_wire_v1.md
          (the v219 fa_live=3 FAIL this closes) ; REPORT_temporal_probe_v5.md (FROZEN V6, untouched).

## 0  ONE LINE
Scope rule built into the wire + the organ prompt. Offline falsifier PASS: the 3 v219 fa_live cases
read DIRTY, the 5 genuinely year-only CLEANs do NOT regress. fa_live mechanism CLOSED (no fabricated
non-year date/number can ride a positive year anywhere in the 48). ff UNCHANGED (separate plane, by
design). S3 eval still owed (E15).

## 1  WHAT WAS BUILT (2 patches + 1 self-test)

### o0_temporal_evidence.py
- Frozen-probe import made LAZY (moved into run()): the deterministic scope functions import with no
  probe and no network, so the offline self-test runs standalone. verify_year / sentence_of_year /
  _TOK still imported UNCHANGED inside run() (V6 frozen, no drift).
- `extract_years_ext` (sec 4 cheap fold): CE range widened 1[89]xx|20xx -> `1\d{3}|20\d{2}` (1000-2099),
  word-boundary + 4-digit guard. BCE requires an explicit BC/BCE marker and is routed to
  ABSTAIN_BCE_unverifiable (the frozen CE-only verify_year is never fed a BCE arg). Newton 1687 /
  Coulomb 1785 now temporal-VISIBLE; BCE visible-but-not-confirmable. Marginal ff help, not the ff fix.
- `scope_verdict(rec)` (spec 2.1-2.3, SAFETY axis = YEAR / FULL_DATE / NUMBER):
  - REFUTE on the year -> claim DIRTY (hard).
  - each FULL_DATE (month+day) and NUMBER (percentage/fraction) specific must be literally present in
    (abstract UNION confirming snippet); absent -> UNVERIFIED -> claim DIRTY (precision-first, literal
    match only -- a fuzzy match would risk FALSE support, the unsafe direction).
  - a year CONFIRM licenses the YEAR token + the subject the resolution matched ("resolved
    out-of-band", spec 2.2); it NEVER sets a claim-level support flag.
- run() now emits `temporal.scope = {verdict, reasons}` as the claim-level safety verdict, and demotes
  the old `collapse()` claim_verdict to `temporal.year_collapse` -- a YEAR-LEVEL diagnostic only, no
  longer a claim support signal (contract 2.4: "do not emit a claim-level support signal from a year
  CONFIRM").

### emit_b1pp.py  (the load-bearing prompt change for the soft S3 judge)
- TEMPORAL_RULE rewritten from claim-level whitewash -> per-specific scope. The removed line was
  "Do NOT flag the claim DIRTY on account of that date" + "supported ... unsupported by BOTH the
  abstract AND the temporal oracle" (collapsed onto the year). The new rule states: a year CONFIRM
  supports ONLY the year sub-claim + its subject; every non-year specific (exact day, number, name)
  is judged on its own evidence; an unverified precise non-year specific -> DIRTY; **"A CORRECT YEAR
  DOES NOT EXCUSE A FABRICATED DAY, NUMBER, OR NAME."** Contents guard updated to assert this phrase
  (catches a silent revert to the whitewash rule).

### o0_subclaim_selftest.py  (offline, no network, NOT the S3 eval)
Runs scope_verdict over the frozen claims_blind_ev_temporal.jsonl and checks the pre-registered
falsifier (scope spec sec 5).

## 2  FALSIFIER RESULT (offline, deterministic)

PRIMARY -- the 3 v219 fa_live cases MUST read DIRTY:
| id | year | fabricated specific | evidence-present? | scope |
|----|------|---------------------|-------------------|-------|
| held2_04_0 | 1953 CONFIRM | "February 28" (real 25 Apr) | no (snippet: "In 1953...") | DIRTY PASS |
| held2_11_0 | 1952 CONFIRM | "November 21" | no (snippet: "In 1952...") | DIRTY PASS |
| held2_13_1 | 1824 COVERED | "56.3%" / "8/14" | no (abstract lacks both) | DIRTY PASS |

SECONDARY -- genuinely year-only CONFIRM-rescued CLEANs MUST NOT regress:
held2_05_1, held2_11_1, held2_14_0, held2_14_1, held2_19_0 -> all CLEAN (no FULL_DATE/NUMBER beyond
the year; subject rides the CONFIRM resolution). 5/5 no regression.

FLAGGED (reported, not asserted) -- held2_06_1 "June 30, 1905" (photoelectric paper, real ~9 Jun):
scope reads DIRTY on an unverifiable extra exact day. NOT a year-only claim, so outside the secondary
guard; this is the scope rule CATCHING an extra fabricated-looking day, not a regression. Whether
06_1's sealed label is CLEAN or DIRTY is E15-owed; either way it is the same class as the intended
catches (exact-day-absent-from-evidence), not separable by the year rule.

SELF-TEST: PASS.

## 3  FULL-48 SAFETY READOUT (instrument, not a score)
Scope over the 48: CLEAN=37 / DIRTY=11 (SAFETY axis: FULL_DATE/NUMBER gated, NAME/PLACE not).
Every claim carrying a POSITIVE year (CONFIRM/COVERED) AND a non-year date/number specific reads
DIRTY: 04_0, 06_1, 11_0, 13_1 -- NO year-rides-a-fabrication leak. fa_live mechanism CLOSED across
the set, not just the 3 cases.

## 4  HONEST DECOUPLING (R2/R3) -- what this does NOT do
- The CLEAN=37 above is the SAFETY-axis verdict, NOT the S3 ff. The soft S3 prompt additionally
  instructs the judge to gate NAMES against evidence; on the 36/48 empty abstracts that pulls many
  multi-specific CLEANs back to DIRTY -> ff stays ~0.800 (the acknowledged saturation plane, spec
  sec 3). Scope fixes fa_live, NOT ff. Do not read 37/11 as "ff fixed."
- The ff fix is a SEPARATE plane: an out-of-band non-year evidence channel (exact-date oracle from
  Wikipedia full date; number/name from article body), banked v218. Not this session.

## 5  FALSIFIER FOR THE OWED S3 RE-RUN (carry-forward)
When the soft-LLM S3 score-2b runs on the binding-confirmed 48: fa_live MUST be 0 (the 3 cases above
read DIRTY). If any of 04_0/11_0/13_1 absorbs under the soft judge -> the prompt rule is too weak and
needs tightening toward the deterministic scope. catch_specifics must stay >= 0.833.

## 6  WHAT THIS SESSION DID / DID NOT
DID   : patch o0_temporal_evidence.py + emit_b1pp.py per scope spec sec 2.4 + 4 ; add
        o0_subclaim_selftest.py ; offline falsifier PASS ; full-48 safety readout (no leak).
NOT   : (a) S3 EVAL -- E15-blocked: owes the 11-claim label<->claim binding confirm + the
        pre-registered soft-LLM blind run (B0 then B1'') for the official ff/lift. Never build+eval
        in one session.
        (b) the ff out-of-band non-year-evidence channel (separate plane, v218).

## 7  NEXT
After E15 (label binding + soft-LLM official blind run): re-run S3 score-2b on the binding-confirmed
clean 48 with the patched B1'' prompt. Gate unchanged: detect-lift >= 0.20 AND ff <= 0.10 AND
fa_live = 0. fa_live is now mechanically protected; ff remains gated on the out-of-band non-year
channel (next build after S3 reads). Trigger: "LABA, ORGAN SUBCLAIM S3" (soft-LLM run) or
"LABA, NON-YEAR EVIDENCE" (the ff plane).

---
*REPORT_organ_subclaim_build_v1 - 2026-06-21 - TYPE C build. Scope rule wired: year-CONFIRM licenses
the year sub-claim only; FULL_DATE/NUMBER gated independently (unverified -> DIRTY); year_collapse
demoted to diagnostic; prompt rewritten ("a correct year does not excuse a fabricated day/number");
extract_years widened pre-1800 + BCE-visible. Offline falsifier PASS (3/3 fa_live DIRTY, 5/5 year-only
CLEAN, 06_1 caught). Full-48: no year-rides-a-fabrication leak. fa_live mechanism CLOSED; ff UNCHANGED
(separate out-of-band plane). S3 soft-LLM eval + 11-claim label binding owed (E15).*
