# SEAL v279 -- GENERATOR AUDIT (ratified + executed)

Status: RATIFIED + EXECUTED (Founder "так и делай", 2026-06-25). Falsifier-first;
bars frozen before build, no goalpost move. Candidate-build only -- NO canonical swap
(Founder-gated, owed). Per-row enumeration LOCAL; this doc = counts + class-split only
(R15 leak-guard).

Substrate read (real bytes, md5-verified): controller.py, c2_migrate.py, canonical pool
755d81c3 (fab-spec slice 120/360).

---

## 0 -- PREMISE CORRECTION (R15, measured)

v278 framed "no-injection" from the worst 12-row hand-slice (11/12). Measured across ALL
120 fab-spec rows with the gate's own non-year channel (clean_for_parse + extract_fulldates
+ extract_numbers_nonyear -- the same symbols c2_migrate uses):

| class | count | % | meaning |
|---|---|---|---|
| REJECT (true catch)   | 34 | 28.3% | token materialised + oracle-refuted |
| ABSTAIN zero-specific | 12 | 10.0% | HARD no-injection (v271/GT-mislabel class) |
| ABSTAIN has-specific  | 74 | 61.7% | honest real-fact emit OR oracle-only -- NOT a defect |

The generator is NOT broken: the 74 are mostly the proposer emitting TRUE facts under a
disposition prompt; forcing injection = R7. The real defect is downstream consumption of
the verdict-blind SELECT *intent* stamp (targeted_weakness) as if it asserted a present
fabrication. Defect surface ~10%, an order smaller than the v278 framing.

## 1 -- (a) MATERIALISATION -- EXECUTED

Detector := len(extract_fulldates(clean_for_parse(claim)) + extract_numbers_nonyear(...)) > 0,
reusing the EXACT gate symbols (no second extractor -> no divergence). Per-row `_materialised`
written into a NEW candidate pool (o0_verdicts_v279cand.jsonl) beside source; source byte-
identical (md5 755d81c3 unchanged). Consumers (c2 quarantine, rate_f catch-attribution) gate
on `_materialised` going forward -> label becomes catch-honest.

Result on full pool (360 rows): _materialised true=315 / false=45.

## 2 -- (b) ARITY -- DEFERRED (void-as-measured)

'respectively'-enumeration arity is a real class but the floor is too thin to gate:
3 'respectively' rows pool-wide, 1 in fab-spec, and the seed defect (N-agents vs M-years,
3-vs-2) has a trailing comma-less 'A and B' list not cheaply regex-separable from a compound.
Building a gate tuned to n=1 = the v278 doctrine violation (no gate against ~empty floor).
DEFERRED to horizon; seed case recorded LOCAL for a future parser-grade build. Same
grounded-NO as the v278 entity-gate.

## 3 -- (c) WATCH-G -- EXECUTED (gen-path, new-gen only)

0 control-code rows in the current pool (measured full pool) -> no existing-pool strip needed.
Strip-at-source shipped: controller.py absorb sanitizes claim text (ESC/ANSI CSI + C0/C1)
before append, new generations only. Idempotent pure string op; verify firewall untouched.

## 4 -- FALSIFIER (sealed pre-build) -- OUTCOME

- F1 MATERIALISATION CATCH: 12 zero-specific rows -> _materialised:false. **PASS (12/12).**
- F2 NO FALSE-DROP: 34 REJECT rows -> _materialised:true. **PASS (34/34).**
- F3 CONSUMER HONESTY: only the `_materialised` key added; 0 outside-class mutation. **PASS (0).**
- F4 ARITY: **N/A -- deferred** (floor n=1, void-as-measured; no gate built).
- F5 HERMETIC: deterministic build, byte-identical re-run. **PASS.**
- Plane-falsifier: zero-specific count == c2_migration_delta no_spec (same extractor). **HOLDS.**

## 5 -- DISPOSITION

Candidate pool + delta = LOCAL ONLY (verdicts/delta never public git). Canonical swap NOT
executed -- Founder-gated, owed (pool-hygiene migration precondition). Reproducibility to git:
o0_v279_materialise.py + controller.py (WATCH-G patch) + this report.
