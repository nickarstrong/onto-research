# WATCH-F DIAGNOSIS + SEALED FIX-RULE (B3 precondition)

- plane: v291, TYPE-B (diagnosis only; no oracle/verifier edit this session)
- substrate anchor: HEAD 887fa04; frozen verifier o0_temporal_evidence.py (md5 92766b06)
  wiring the frozen V6 probe o0_temporal_probe_v5.py (md5 b231da36)
- status: **WATCH-F closed-by-construction on current substrate.** Sealed bar below binds the
  future Layer-2 oracle BUILD.
- R15: this report carries mechanism only. WATCH-F-class claim text, topic, year value, and the
  mis-bound evidence title stay LOCAL (measurement-sensitive). Rows referenced by id only.

---

## 1 - STEP 1: REPRODUCE (hermetic, offline)

Harness `o0_watchf_repro.py` (LOCAL, not committed) drove the FROZEN wired oracle
(`o0_temporal_evidence.run`, lazily importing the frozen V6 probe) over the two WATCH-F-class rows
(`held2_08_0`, `held2_08_1`), rows read verbatim from disk. Network egress in the probe was
stubbed at `_get` (every wbsearch / entity_data / wiki_fulltext routes through it).

Result (hermetic, 10 network calls attempted -> all stubbed None):

| row | per_year | collapse | scope |
|-----|----------|----------|-------|
| held2_08_0 | {year: ABSTAIN} | ABSTAIN | CLEAN |
| held2_08_1 | {year: ABSTAIN} | ABSTAIN | CLEAN |

**STEP1 = FAIL-to-reproduce.** No REFUTE on the true year offline. Per the plane's Fail branch:
WATCH-F is not offline-reproducible on the frozen substrate -> re-characterize, do not invent a
defect. (Disk-wins: the live hermetic run is authoritative over any dated verdict file.)

## 2 - STEP 2: ROOT CAUSE (the precise failing branch)

The false-REFUTE was real but **historical and network-bound**, present only in stale lifecycle
artifacts (`claims_blind_ev_temporal.jsonl`, `claims_blind_ev_temporal_v264.jsonl`) and only for
one of the two rows -- the row whose bundled evidence was mis-bound to an unrelated paper, so the
local abstract carried no confirmation of the true year.

Failing branch = **REFUTE-on-non-confirmation**, not any of the three candidate causes:
- NOT entity-resolution miss (subject did resolve).
- NOT wrong single-authority value (no contradicting authoritative year was returned).
- NOT rounding/format.

Mechanism: the old free-text year channel (`verify_year`, probe_v5 tail return "REFUTE") treated
*absence of local confirmation* as grounds to go to the network and emit REFUTE, rather than
ABSTAIN. A true value was actively contradicted because the confirming text was not present in the
(mis-bound) local evidence. This is the "castration direction" (a true claim pushed to DIRTY).

**Why it is closed now (V6 wiring, o0_temporal_evidence.py):** the evidence layer is CONFIRM /
ABSTAIN only for the live channel; the sole REFUTE source is `apply_offline_dirty_year`, a derived
override that fires only when a claimed year is listed in the offline table AND differs from that
table's ground-truth year (`claimed != gt`, gt-agnostic, never hardcoded by id). A TRUE year is by
definition never a known-dirty table entry, so REFUTE on a true year is structurally unreachable.
The hermetic run confirms: 10 network calls stubbed, verdict ABSTAIN -> no surviving REFUTE path.

## 3 - STEP 3: SEALED FIX-RULE (B3 bar for the future Layer-2 oracle)

The risk is regression: the NEXT+1 Layer-2 BUILD re-introduces a single-authority oracle emitting
REFUTE on anachronism + numeric. If that oracle's REFUTE fires on non-confirmation (as the old
free-text path did), WATCH-F regresses. The bar:

> **B3-WATCHF (sealed).** REFUTE is licensed ONLY when the authoritative source returns a
> POSITIVE, DIFFERENT value for the SAME resolved (entity, event) as the claim -- i.e. a real
> contradiction. Every non-contradiction outcome -- subject unresolved, event-predicate mismatch,
> source silent, evidence lacks the value -- MUST collapse to ABSTAIN, NEVER REFUTE.
> A claimed value equal to the authoritative value -> CONFIRM.

**Exact trigger condition (falsifiable bar).** For any row where the claimed year equals the
authoritative year for the resolved (entity, event) -- a TRUE-year row -- Layer-2 MUST emit CONFIRM
or ABSTAIN. Emitting REFUTE on such a row = bar violation.

**Falsifier (sealed, to run at Layer-2 B-stage).** Feed the WATCH-F-class rows (`held2_08_*`,
true-year) through the Layer-2 oracle, hermetic and live. PASS = verdict in {CONFIRM, ABSTAIN} for
both. FAIL (bar broken) = any REFUTE. Generalize: assert `claimed == gt => verdict != REFUTE` over
every GT-CLEAN true-year row in held-out.

## 4 - CARRY

- WATCH-F: re-characterized as a network-path historical defect, **closed-by-construction** under
  V6 offline-table-only REFUTE. No fix code owed; the bar above governs Layer-2.
- B3-WATCHF is now a precondition on the Layer-2 oracle BUILD (NEXT+1).
