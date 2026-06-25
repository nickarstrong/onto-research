# PRE-REG -- Y-CHANNEL DIRTY-YEAR FALSIFIER (hermetic / offline)

- doc: `reports/PREREG_year_channel_falsifier_20260625.md`
- session: v273 -- CONCEPT / PRE-REG (falsifier-first). Read-only design. No build, no oracle, no gen, no code-edit.
- substrate HEAD (precondition P0): **4d0cbc9** (confirm at build STEP 0; disk-wins 3.10).
- per_year status: **FROZEN this session.** This doc designs the falsifier; it does not run or implement it.
- re-open linkage: this is **re-open precondition #1** for the v272-(B) DEFERRED entity/relation gate
  (un-defer only AFTER this catch-rate closes AND POOL HYGIENE migration done; founder owns re-open).
- claim this session: **none.** No measurement, no pass/fail. F-bars are SEALED here; evaluation is a separate TYPE C session.

---

## 0 · DEFECT UNDER FALSIFICATION (committed-pack grounded)

Held-out (v267 fresh set, 48, `held2_00_0..23_1`, LOCAL) carries 3 **KNOWN-dirty-year** rows where
`per_year` currently returns **ABSTAIN** instead of **REFUTE** -- the leak this falsifier must catch:

| row  | dirty claimed year | current per_year (expected) | required per_year |
|------|--------------------|-----------------------------|-------------------|
| 20_1 | 1837               | ABSTAIN  (defect)           | **REFUTE**        |
| 21_0 | 1796               | ABSTAIN  (defect)           | **REFUTE**        |
| 21_1 | 1789               | ABSTAIN  (defect)           | **REFUTE**        |

Source of dirty tokens: committed pack v273 (sec 0 / sec 6, carried from worksheet `db09dbe`).
Diagnosis grounding (v269, BINDING): leak is **not** a number-extractor regression -- `E=0` structurally,
`per_specific={}` by design; leak = `per_year` **never REFUTE** -> scope falls through CLEAN. Instrument
question is the **YEAR channel + SCOPE**, not the number extractor.

---

## 1 · FALSIFIER DESIGN -- HERMETIC / OFFLINE

**Principle.** No live Wikidata / network in the falsifier loop. Hermetic = repeatable = byte-identical.
The falsifier's substrate is an **offline known-dirty-year table** (frozen on disk), NOT an oracle call.
`verify_specific` (oracle, md5 `c6eafcdb`, UNCHANGED) is **out of scope** for this loop.

**Required behaviour of `per_year` under the falsifier:**
- input row's claimed year present in the offline KNOWN-DIRTY table AND != ground-truth year  -> **REFUTE**
- claimed year == ground-truth year                                                            -> **CONFIRM** (per existing rule)
- claimed year absent / unresolvable offline                                                   -> **ABSTAIN** (per existing rule)

**Discrimination requirement (v268 lesson, BINDING).** v268 PASS was NON-DISCRIMINATIVE: a pure-ABSTAIN
gate scores identically when catch arms are never exercised. Therefore this falsifier MUST exercise the
catch arm -- a pure-ABSTAIN baseline MUST FAIL F1. Stated as bar F3 below.

### 1.1 Offline KNOWN-dirty-year table (substrate schema)

Frozen JSONL/table, hermetic. One row per known-dirty case. Schema:

```
{ "row_id": <held2 id>, "claimed_year": <int>, "gt_year": <int>, "expected": "REFUTE" }
```

| row_id | claimed_year | gt_year                    | expected |
|--------|--------------|----------------------------|----------|
| 20_1   | 1837         | <P1: from worksheet db09dbe> | REFUTE   |
| 21_0   | 1796         | <P1: from worksheet db09dbe> | REFUTE   |
| 21_1   | 1789         | <P1: from worksheet db09dbe> | REFUTE   |

**`gt_year` cells are NOT filled here (R7 / no-fab / disk-wins).** They are a build-time disk read --
see precondition **P1**. The claimed (dirty) years are committed-pack fact; the ground-truth correct
years live in worksheet `db09dbe` on disk and must be read there, not recalled.

### 1.2 Control rows (for F2 false-fire + F3 discrimination)

The false-fire / discrimination arms draw on CLEAN/CONFIRM-year rows from the same held-out:
- **WATCH-F candidate:** `held2_08_*` (Coulomb, claimed 1785) -- fresh set scope=CLEAN, year=ABSTAIN
  (defect did not fire). Correct-year control: a true year must NOT REFUTE. Exact membership of the
  control set is a P2 disk read (enumerate CONFIRM/CLEAN-year rows from held-out at build STEP 0).

---

## 2 · SEALED F-BARS (falsifiable, fixed before any build)

| bar | statement | pass condition |
|-----|-----------|----------------|
| **F1** | catch | **3/3** KNOWN-dirty years (20_1, 21_0, 21_1) -> **REFUTE** (not ABSTAIN). |
| **F2** | false-fire | **0** false-REFUTE on CONFIRM/CLEAN-year control rows (mirrors v268 0/31 discipline). |
| **F3** | discrimination | a **pure-ABSTAIN baseline FAILS F1** (catch arm provably exercised; non-discriminative gate is rejected). |
| **F4** | hermetic | falsifier reproduces **byte-identical** offline across 2 runs; **0** network calls in the loop. |

These four bars are **SEALED**. No goalpost move at build time (no post-hoc rationalization). A bar that
fails is reported as a fail; denominators are not adjusted to fit.

**Design-intent note (R2).** F1 targets and dirty tokens are committed-pack fact and are sealed. The
*current-ABSTAIN baseline* (the defect each row exhibits today) is asserted by the pack as "expected" and
is **confirmed, not assumed**, at build STEP 0 (precondition P0/P3). If any of the 3 rows is NOT ABSTAIN
on disk, the defect set changes and F1 re-opens before build.

---

## 3 · BINDING PRECONDITIONS (must hold before the BUILD/measure session)

| id | precondition | type | default if unmet |
|----|--------------|------|------------------|
| **P0** | HEAD == 4d0cbc9; Test-Path worksheet + scope-amendment doc | disk-confirm | STOP -- conveyor drifted |
| **P1** | `gt_year` for 20_1 / 21_0 / 21_1 read from worksheet `db09dbe` (not memory) | disk-read | table incomplete -> no build |
| **P2** | CONFIRM/CLEAN-year control set enumerated from held-out (incl. WATCH-F 08_*) | disk-read | F2/F3 arms undefined -> no build |
| **P3** | current `per_year` verdict on the 3 Y-rows dumped == ABSTAIN (defect baseline confirmed) | disk-read | F1 re-opens |
| **P4 -- GT-CORRECTION (BINDING, owed)** | `sealed_labels` carries DIRTY->CLEAN x3 (06_1, 07_0, 23_1) | label-pass | **denominator wrong -> measurement invalid** |

**P4 detail (GT-CORRECTION).** v271 (BINDING): leak-set is 8, not 11 -- 06_1/07_0/23_1 are CLEAN
(raw==claim; GT mislabel; `dirty_class="specifics"` with no materialized token = gen/labeling defect).
The Y-channel labeled set MUST carry these 3 corrected to CLEAN before measurement, else the false-fire
denominator (F2) and the leak-set are wrong. **Default = OWED** (fires at next gen/label pass; couples to
the Y-channel set). Founder may pre-fire this cycle; if not pre-fired, it stays owed and is recorded here
as the gating precondition for a valid measurement.

---

## 4 · OUT OF SCOPE (this falsifier)

- `verify_specific` oracle path (md5 `c6eafcdb`, UNCHANGED) -- no network in the loop.
- Number extractor / `per_specific` (E=0 by design; v269 BINDING -- not the instrument here).
- The 5 S-rows declared OUT-OF-CLASS by v272 scope-amendment (title/name/venue/attribution) -- number
  gate is non-year numeric only; entity/relation gate is DEFERRED (v272 B).
- WATCH-G ESC-code corruption in stored claim text (held2_01_1/07_0/23_1) -- strip-at-source is a gen fix,
  not in the falsifier loop; flagged as a tokenization risk that touches P2 control-row hygiene.

---

## 5 · BUILD HANDOFF (separate TYPE C session -- NOT this session)

Next TYPE C: implement the offline falsifier against the on-disk substrate, run vs these SEALED F-bars
after P0-P3 (and P4 ruling) hold. Build + eval never share a session. per_year stays frozen until that
build session opens.

---

*v273 -- 2026-06-25 -- CONCEPT/PRE-REG. Falsifier-first: hermetic offline Y-channel dirty-year falsifier.
F1-F4 sealed. Dirty tokens committed-pack fact; gt_year / control-set / current-verdict = disk-read
preconditions P1/P2/P3 (R7 no-fab). GT-CORRECTION = P4 (BINDING, owed). Re-open precondition #1 for v272-(B).
No build / oracle / gen / eval / code-edit this session.*
