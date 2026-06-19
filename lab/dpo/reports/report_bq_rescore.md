# report_provenance_L1L2 -- SPEC sec9 step1 (L1 existence + L2 status)

VERDICT: PASS  (2 ok / 0 fail)
RWD index: 59011 retracted DOIs (Retraction Watch CSV, OriginalPaperDOI x RetractionNature=Retraction)

## Fixture A results
- 10.1038/s41586-019-1666-5 : exp=L1L2_PASS got=L1L2_PASS ok=True
- 10.1038/s41586-019-1666-5 : exp=T4_L1_MISMATCH got=T4_L1_MISMATCH ok=True

## SPEC compliance notes
- L1 mismatch (not non-resolve) is the reject path for mis-attributed DOIs that resolve to a wrong paper.
- ORACLE FIX: Fixture A row pnas.0811124106 expected 'non-resolve' but RESOLVES to an unrelated paper
  -> corrected expectation = T4_L1_MISMATCH (regenerate Fixture A on spec edit, per D4 discipline).
- L2 dual-signal [D1]: publisher 'RETRACTED' title flag (primary) + RWD index (augment). Coverage gap OWNED.
- clean control present -> accept path (L1L2_PASS) exercised, not VOID-by-construction (E23).
- step1 scope = L1/L2 only. L1L2_PASS is provenance-clean, NOT gold: L4 bind/L5/G-floor still gate (steps 2-4).
