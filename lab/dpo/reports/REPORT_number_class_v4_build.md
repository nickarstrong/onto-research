# REPORT -- NUMBER-CLASS v4 BUILD (TYPE C) -- C-1 + C-2

- type: TYPE C BUILD. Implements SEALED PREREG_AMENDMENT_v4 (md5 7a42d312). No re-design, no held-out, no eval.
- substrate: HEAD `abc4c42`; verify_specific seam `c6eafcdb` @ L128 (confirmed pre-edit).
- exit: OFFLINE GATE GREEN (number_gate_probe.py, hermetic). ALL GATES PASS.
- date: 2026-06-24.

## C-1 -- year single-ownership (implemented literally)
- NEW `_year_claimed_tokens(text)` (pure) + `extract_numbers_nonyear(text)` (pure). ONE shared helper.
- Subtracts: `extract_years_ext` output (per_year keys) + `extract_fulldates` numeric components
  + both integers of `NNNN (and|to|through|-) NNNN` range bigram.
- BOTH gate feeders switched to the helper: `scope_verdict` loop + `run()` per_specific loop.
- `_NUMBER` regex + `extract_numbers` body BYTE-IDENTICAL (firewall: raw extractor untouched).

## C-2 -- evidence-state 3-state gate (implemented)
- `_specific_status`: returns SUPPORTED | REFUTED | **ABSTAIN** (was UNVERIFIED->DIRTY).
- `scope_verdict`: returns CLEAN | DIRTY | **ABSTAIN**. DIRTY only on contradiction (oracle REFUTE);
  CLEAN on CONFIRM/literal; ABSTAIN on non-confirm without contradiction (quarantine).
- `run()`: ABSTAIN counted separately (`n_abstain`, quarantine), not folded into CLEAN/DIRTY.

## OFFLINE GATE (number_gate_probe.py)
- GATE 1 (_NUMBER widen, sealed regex): PASS [HARD 8/8, CTRL 4/4, REGR 3/3, IDENT 0/3].
- GATE 2 (shape-A anchoring, C-2 verdicts): PASS [fake->ABSTAIN, true+true->CLEAN, true+fab->ABSTAIN].
  CHANGED from v3: empty-abstract non-confirm now ABSTAIN, not DIRTY (oracle-rescue FALSIFIED; C-2 TRADE).
- GATE 3 (C-1): PASS [years/ranges subtracted; bare-qty 64/6.5/2300/95% retained; year-only !DIRTY; contradicted->DIRTY].
- GATE 4 (C-2): PASS [empty->ABSTAIN, contradicted->DIRTY, confirm->CLEAN; ABSTAIN != CLEAN/DIRTY].

## SEAM STATUS (re-anchor)
- `verify_specific` BYTE-IDENTICAL -> seam `c6eafcdb` UNCHANGED. C-2 verdict logic landed in the GATE
  (`_specific_status` + `scope_verdict`), NOT the oracle. Pack note "seam WILL re-hash" does not apply to
  verify_specific. Changed verdict nodes (8-hex md5, for Founder seam-freeze tool):
  - `_specific_status`  f0c16852 (CHANGED, C-2)
  - `scope_verdict`     e84d64af (CHANGED, C-1+C-2)
  - `extract_numbers_nonyear` 64642bad (NEW) ; `_year_claimed_tokens` 30bf6806 (NEW)
  RULING NEEDED: does the frozen seam cover the oracle only (then nothing to re-freeze) or the verdict
  path (then re-anchor against scope_verdict e84d64af)?

## FLAGGED RESIDUAL (R3, sealed-spec tension -- Founder ruling)
- `extract_years_ext` is band-only (1000-2099, NO temporal-context gate). The sealed "subtract per_year
  matches" mechanism therefore subtracts in-band TRUE 4-digit quantities ("1500 mg", "1850 kg") and any
  `NNNN and NNNN` quantity pair ("2300 and 2400 kg") -> false-NEGATIVE = the exact class PREREG REJECTED(i)
  meant to protect. The TRADE's "context-free 4-digit still leaks to the number gate" holds ONLY with a
  context gate the year channel does not have on disk. Implemented literally (no context gate = no re-open);
  flagged for ruling: (a) accept (in-band true 4-digit quantities are rare) or (b) add temporal-context gate
  to extract_years_ext (re-opens C-1, new design).

## NOT DONE (out of scope this session)
- POOL HYGIENE migration (~15 absorbed-CLEAN bare-qty -> ABSTAIN quarantine): BUILD/TYPE-C, separate.
- Fresh held-out + ff re-measure (TYPE B, new set; old SPENT). HEADROOM v4 stays DEFERRED.
- WATCH-F year-oracle false-refute (year channel defect, not number class).

---
*v4 build -- 2026-06-24 -- C-1 helper + C-2 3-state ABSTAIN. Offline gate GREEN = build exit. No eval/held-out.*
