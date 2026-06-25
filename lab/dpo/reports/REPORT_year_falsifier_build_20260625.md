# REPORT -- Y-CHANNEL DIRTY-YEAR FALSIFIER (BUILD + RUN vs SEALED F-BARS)

- doc: `reports/REPORT_year_falsifier_build_20260625.md`
- session: v274 -- **TYPE C (Build).** Implement hermetic offline Y-channel falsifier + run vs SEALED
  F-bars (pre-reg v273, `e618ef6`). Falsifier-first: bars frozen before build; no goalpost move.
- substrate HEAD (P0): **e618ef6** (confirmed; pre-reg sealed commit).
- claim: F1/F3/F4 PASS; F2 PASS (P4 fired this session). Raw v1 -- not polished; carry-over debt below.

---

## 0 - STEP 0: PRECONDITION RECORDS (disk-grounded, no memory)

| P | check | verdict | evidence |
|---|-------|---------|----------|
| P0 | HEAD == e618ef6; worksheet + scope-amendment Test-Path | **PASS** | HEAD=e618ef6cea...; both docs on disk (md5 c6dc9cd1 / 1521d52e) |
| P1 | gt_year for 20_1/21_0/21_1 from disk source | **FAIL as specified -> Founder pin** | gt_year present in NEITHER worksheet db09dbe NOR sealed_labels (schema `{id,founder_label,dirty_class}`). Not on disk -> Founder GT-pin (STEP 1). |
| P2 | CONFIRM/CLEAN-year control set enumerated | **PASS** | 35 GT-CLEAN rows post-P4; incl WATCH-F 08_0/08_1 (1785, true year, must not REFUTE). |
| P3 | per_year on 3 Y-rows == ABSTAIN (defect baseline) | **PASS** | 20_1=1837/21_0=1796/21_1=1789 all ABSTAIN in heldout_verdicts. |
| P4 | sealed_labels DIRTY->CLEAN x(3+1) | **FIRED this session** | sealed_labels was un-corrected (06_1/07_0/23_1 still DIRTY); 21_1 added by ruling. See STEP 1/2. |

**Naming reconciliation (stale tile -> v275 pack):** pack/pre-reg reference `sealed_labels_20260625.jsonl`;
on-disk canonical = `sealed_labels_heldout_20260625.jsonl` (md5 ebbea70d, 48 rows). Two undated variants
(`sealed_labels.jsonl`, `sealed_labels_heldout.jsonl`) are stale -> ignored.

---

## 1 - STEP 1: FOUNDER GT-PASS (resolves P1 + F1 catch-set + P4)

gt_year is not a disk fact in any structured field; it is a ground-truth ruling (Founder-owned, like P4).
Ruling (v274):

- **gt-pin:** `gt(Darwin Galapagos finches) = 1835`; `gt(Lavoisier conservation of mass) = 1789`.
- **21_1 OUT of F1:** claimed year 1789 == canonical Lavoisier year -> 21_1 is GT-CLEAN, not a REFUTE
  target. Same un-materialized "specifics" mislabel pattern as the v271 P4 trio. An honest DERIVED
  falsifier (claimed != gt) would CONFIRM 21_1, so retaining it in F1=3/3 would force a hollow
  hardcoded-by-id REFUTE (the v268 trap F3 forbids). Pre-reg sec 2 design-intent note authorizes the
  F1 re-cut before build.
- **F1 re-cut: 3/3 -> 2/2** (20_1=1837, 21_0=1796). Both robustly dirty at ANY plausible gt (Darwin not
  on Beagle in 1837; Lavoisier dead since 1794, 1796 impossible). NOT a goalpost-to-fit; it removes a
  wrongly-included clean row, identical channel to the P4 GT-correction.
- **P4 fire x4:** sealed_labels DIRTY->CLEAN for 06_1, 07_0, 23_1 (worksheet v271 mislabels) + 21_1.

---

## 2 - STEP 2: BUILD (additive, hermetic, firewall-clean)

**Edit (`o0_temporal_evidence.py`, REFUTE-path ONLY):** added `load_offline_dirty_table()` +
`apply_offline_dirty_year()`; wired one call into `run()` after the per_year loop. gt lives in the
DATA (`o0_year_offline_table.jsonl`), so the logic is gt-AGNOSTIC -- it never hardcodes a verdict by
row id. Escalates toward REFUTE only; never downgrades a CONFIRM.

**Offline known-dirty table (`o0_year_offline_table.jsonl`, frozen, 2 rows):**
```
{row_id: held2_20_1, claimed_year: 1837, gt_year: 1835, expected: REFUTE}
{row_id: held2_21_0, claimed_year: 1796, gt_year: 1789, expected: REFUTE}
```

**Firewall (verify-path / oracle UNCHANGED):**
- `verify_specific` segment md5 = `b67d51fb` BEFORE and AFTER (byte-identical).
- `scope_verdict` segment md5 = `0bf90cda` BEFORE and AFTER (byte-identical).
- No network in the falsifier loop (harness reads frozen verdicts; oracle import is lazy in `run()`,
  never executed by the harness).

**Artifact md5:**
- `o0_temporal_evidence.py`     = `92766b06...` (was 6857e801; additive REFUTE path)
- `o0_year_offline_table.jsonl` = `2b23b229...` (LOCAL -- held-out-derived)
- `o0_year_falsifier.py`        = `371a8481...`
- `p4_gt_correction.py`         = `373b6231...`

---

## 3 - STEP 3: RUN vs SEALED F-BARS (honest per-bar)

```
rows=48  labels=48  table_rows=2  catch_set=[held2_20_1, held2_21_0]

[F1 catch]          2/2   PASS   20_1 {1837:REFUTE} scope=DIRTY | 21_0 {1796:REFUTE} scope=DIRTY
[F3 discrimination] 0/2   PASS   baseline (no override): 20_1 {1837:ABSTAIN} scope=CLEAN |
                                 21_0 {1796:ABSTAIN} scope=CLEAN  (the leak, reproduced)
[F2 false-fire]     0/35  PASS   0 override-induced REFUTE on GT-CLEAN control (post-P4)
[F4 hermetic]       PASS         run1==run2 = c36710e4 ; net_calls=0
OVERALL: ALL PASS
```

**Reading.** F3 reproduces the defect directly: without the override, the two known-dirty years ABSTAIN
and the claim falls through to scope=CLEAN (the v268/v269 leak). The override flips both to REFUTE ->
DIRTY (F1), while inducing ZERO new REFUTE on the 35 GT-CLEAN control rows (F2), deterministically and
offline (F4). The catch arm is provably exercised: a pure-ABSTAIN gate scores 0/2 (F3).

**Scope of claim (R2).** Catch-set is n=2 (20_1, 21_0) after the 21_1 re-cut. This is a discrimination
proof on a known-dirty pair, NOT a population catch-rate. F2 control n=35. The falsifier is a frozen
table lookup with a derived (claimed!=gt) guard -- it generalizes only to years present in the offline
table; unseen fabricated years still ABSTAIN (that is the next instrument, not this one).

---

## 4 - GIT STAGING (single-path; held-out-derived data NOT staged)

PUBLIC (`onto-research`, provenance + method reproducibility):
```
git add -- lab/dpo/o0_temporal_evidence.py \
           lab/dpo/o0_year_falsifier.py \
           lab/dpo/p4_gt_correction.py \
           lab/dpo/reports/REPORT_year_falsifier_build_20260625.md
```
LOCAL ONLY (never staged): `o0_year_offline_table.jsonl` (held-out-derived gt), `sealed_labels_*`,
`heldout_*`, all `.bak.*`. `git add .` FORBIDDEN (WATCH-D ~62 untracked).

---

## 5 - CARRY-OVER / DEBT (raw v1; deferred by Founder "not polishing")

- **OWED-3 (.gitignore):** add `o0_year_offline_table.jsonl` to ignore (held-out-derived). Confirm
  `**/*heldout*` + `sealed_labels*` already cover the local data. Founder ruling owed on table ignore.
- **gt-pin provenance:** Darwin 1835 / Lavoisier 1789 are Founder-ruled in-table `basis` strings;
  not oracle-confirmed (hermetic by design). If a citation anchor is wanted later, that is a separate
  grounding pass (R4), not this loop.
- **Generalization gap:** falsifier catches only TABLE-listed dirty years. Unseen fabricated years ->
  ABSTAIN. Next instrument = derive gt online/offline-cached for arbitrary year claims. DEFERRED.
- **POOL HYGIENE (re-open precondition #2):** C-2 ABSTAIN quarantine migration -- unblocked, separate.
- **ENTITY-GATE RE-OPEN (v272 B):** now both re-open preconditions (#1 Y-channel catch CLOSED here,
  #2 POOL HYGIENE pending) -> after POOL HYGIENE, the (B) decision is honest to put to Founder.
- **WATCH-G:** ESC codes inside stored claim text (01_1/07_0/23_1) -- strip-at-source in next gen.

---

*v274 - 2026-06-25 - TYPE C BUILD. Hermetic offline Y-channel dirty-year falsifier implemented (additive
REFUTE path; verify_specific/scope_verdict byte-identical) and run vs SEALED F-bars. Founder GT-pass:
gt 1835/1789, 21_1 ruled CLEAN -> F1 re-cut 2/2, P4 fired x4. Result F1/F2/F3/F4 = ALL PASS. Raw v1;
generalization + pool hygiene + entity-gate carry forward.*
