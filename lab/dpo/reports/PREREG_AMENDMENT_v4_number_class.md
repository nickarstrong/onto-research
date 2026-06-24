# PRE-REG AMENDMENT v4 -- NUMBER-CLASS SCOPE (C-1 + C-2)

- status: **SEALED at write time.** Do NOT move falsifiers next session.
- type: CONCEPT (design only). NO build, NO eval, NO held-out spend in the writing session.
- substrate (disk-wins, confirmed): HEAD `ad84df5` ; `verify_specific` seam `c6eafcdb` @ L128 ;
  `_NUMBER` @ L65 (4-branch; branch 4 `(?<![\w-])\d+(?:\.\d+)?`) ; gate feeders L176 + L227.
- amends: the NUMBER-CLASS knob only. Knobs a/c of PREREG_AMENDMENT_v3 (5ee4402f) stay SEALED, NOT reopened.
- driving evidence: REPORT_ff_resaturation_v264 (held-out SPENT 48->48): ff_all=0.800, ff_bq=1.000,
  fab recall 18/18 NON-DISCRIMINATIVE, DIRTY precision 0.429, live CONFIRM 2/48. §5 oracle-rescue FALSIFIED.
- date: 2026-06-24.

---

## A. PROBLEM (one line)
The v263 `_NUMBER` widening fixed bare-quantity CLEAN-by-default but over-shot into 4-digit years, and the
non-year gate marks DIRTY on oracle non-confirm even when there is NO evidence to refute against -- so TRUE
quantities and TRUE years mass-fire DIRTY (14/24 FF year-only, 9/9 FF bare-qty). The pendulum, not a leak.

---

## C-1 KNOB -- YEAR TOKENS MUST NOT ENTER THE NON-YEAR NUMBER GATE

**DECISION (default, engineer-owned):** single-ownership. A token claimed by the YEAR channel
(`extract_fulldates` components + `per_year` matches) is SUBTRACTED from `extract_numbers` output
*before* the non-year gate, via ONE shared pure helper feeding BOTH consumers (L176 + L227). Plus an
explicit year-range-pair guard: in a `NNNN (and|to|-) NNNN` bigram both integers are claimed as years
(the v264 dominant FF was the range `1856 and 1864`; a lone per_year match can miss the 2nd integer).

**TRADE (one line, R3):** coverage-bound to year-channel recall -- a 4-digit year in NO temporal context
(no prep / no range / outside plausible band) still leaks to the number gate. Accepted: that residual is
the C-2 class (a bare quantity that happens to be 4 digits), correctly handled by C-2, not by C-1.

**REJECTED (1 line each):**
- (i) regex year-range exclusion in branch 4 -> drops TRUE 4-digit quantities ("1500 mg") -> new false-NEGATIVE class. No.
- (iii) filter at the gate consumer -> two insertion sites (L176+L227) -> seam-divergence risk. Subsume into the shared helper instead.

**FALSIFIER (C-1) -- two tiers:**
- OFFLINE (number_gate_probe.py, hermetic, build session): a year-only TRUE claim and a `NNNN and NNNN`
  range TRUE claim must NOT reach `unverified_non_year_specific` / must NOT go DIRTY via the number gate;
  a fab bare-qty must still reach it.
- FRESH-HELD-OUT (post-build TYPE B, new set): the 14 year-only GT-CLEAN false-fires clear (year-only true
  claims stop going DIRTY through the number gate) AND fab catch on GT-DIRTY *year* items holds via the
  YEAR channel (not the number gate). OLD-set baseline to beat: 14/24 FF were year-only.

---

## C-2 KNOB -- NUMBER-CLASS SCOPE WITHOUT ORACLE RESCUE

**DECISION (default):** evidence-state-gated verdict. The number gate emits THREE states, not two:
- **DIRTY** only on CONTRADICTION -- the quantity appears in available evidence with a different value,
  OR an oracle REFUTE. (DIRTY requires positive disagreement, never mere non-confirmation.)
- **CLEAN** on CONFIRM -- quantity matches present evidence / oracle CONFIRM.
- **ABSTAIN** on NON-CONFIRM over EMPTY/absent evidence -- no abstract, no oracle CONFIRM, no contradiction
  => the gate has NO basis to adjudicate => it must NOT assert DIRTY. (Absence of evidence != fabrication.)

This kills the oracle-rescue dependency (the FALSIFIED §5 path): a TRUE bare quantity on an empty abstract
passes by ABSTAINing, not by waiting for a CONFIRM the dead oracle (2/48) will never send.

**TRADE (one line, R2/R7 honesty):** a fabricated bare quantity on an EMPTY abstract also ABSTAINs --
it is UNCATCHABLE without evidence, and the verifier must declare that rather than pretend to detect it.
fab catch on the empty-abstract sub-class drops by design; this is calibration, not regression. ABSTAIN
claims are QUARANTINED (never absorbed CLEAN, never counted fab-DIRTY) -- they are not "passed".

**FALSIFIER (C-2) -- FRESH-HELD-OUT, partitioned by abstract-emptiness:**
- EMPTY-abstract partition: GT-CLEAN bare-qty -> ABSTAIN (not DIRTY); the 9/9 current false-fires move to 0.
  GT-DIRTY bare-qty here -> ABSTAIN too (declared uncatchable; NOT scored as a miss-regression).
- NON-EMPTY-abstract partition: GT-DIRTY bare-qty with a contradicting value present -> DIRTY (fab catch
  preserved WHERE evidence exists; OLD baseline 11/11 caught-but-non-selective). GT-CLEAN matching -> CLEAN.
- PASS = empty-abstract true-bare-qty FF -> 0 via ABSTAIN, WITHOUT losing DIRTY on evidence-contradicted bare-qty.
  FAIL = ABSTAIN leaks contradicted quantities to CLEAN, OR empty-abstract true bare-qty still DIRTY.

---

## D. CONSEQUENCE -- ABSTAIN IS A REAL THIRD STATE
ABSTAIN != CLEAN and != DIRTY. The pool/conditioning path MUST add a quarantine bucket: ABSTAIN claims are
neither training-positive nor fab-rejected. This closes §6 POOL HYGIENE the right way -- the ~15 unverified
bare-qty currently ABSORBED CLEAN in the v3 run were mis-classed; under C-2 they are ABSTAIN -> quarantine.
(Pool-state migration is BUILD/TYPE-C work, flagged here, not done now.)

## E. DECISION RULE (sealed, do NOT move)
No "fix" is valid without a FRESH-held-out re-measure plan -- the old set is SPENT + TERMINAL. Each knob
above names (1) an offline hermetic falsifier provable in the BUILD session and (2) a fresh-held-out
falsifier provable only AFTER `gen_heldout.py` + Founder labels. Build is the SEPARATE next TYPE C session.

## F. OUT OF SCOPE (do not conflate)
- WATCH-F: year oracle FALSE-REFUTE on true year 1785 (held2_08_1). Defect in the YEAR channel, not the
  number class. Queued behind this; C-1 routes years TO that channel but does not fix its oracle.
- HEADROOM v4: stays DEFERRED until the verifier passes a fresh-held-out re-measure under C-1+C-2.
- Knobs a/c (v3): not reopened.

## G. BUILD HANDOFF (next+1 TYPE C, not this session)
Implement C-1 helper + C-2 three-state gate against on-disk `o0_temporal_evidence.py` @ ad84df5. Extend
`number_gate_probe.py` with the C-1 offline regressions (year-only + range-pair TRUE -> not DIRTY; fab
bare-qty -> DIRTY) and a C-2 empty-vs-nonempty ABSTAIN regression. Offline gate GREEN is the BUILD exit;
held-out re-measure is a later TYPE B on a FRESH set. Re-anchor + freeze the new `verify_specific` seam
(C-2 changes verdict logic at L128 -> seam hash WILL change; that is expected, freeze the new one).

---
*v4 - 2026-06-24 - NUMBER-CLASS CONCEPT. C-1 year single-ownership (subtract year-channel tokens + range-pair
guard, shared helper). C-2 evidence-state-gated 3-state verdict (ABSTAIN-on-empty, DIRTY only on contradiction)
killing the FALSIFIED oracle-rescue path. Both falsifiers fresh-held-out (old set SPENT). Build = separate TYPE C.*
