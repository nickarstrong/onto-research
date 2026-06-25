# report_provenance_L1L2 -- SPEC sec9 step1 (L1 existence + L2 status)

VERDICT: FAIL  (0 ok / 30 fail)
RWD index: 59011 retracted DOIs (Retraction Watch CSV, OriginalPaperDOI x RetractionNature=Retraction)

## Fixture A results
- 10.1073/pnas.25.3.497 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/j.vaccine.2019.01.056 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1038/nature04258 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/S0006-8993(00)80167-6 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1029/2006JD007582 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.tig.2015.01.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.physletb.2012.08.021 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.atherosclerosis.2014.03.010 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.tree.2014.06.012 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.48550/arXiv.1706.03762 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/j.ccr.2017.03.012 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/B978-0-12-811443-6.00002-6 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/B978-0-12-385863-3.00001-6 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1126/science.235.4798.381 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1038/nature10186 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1093/infdis/jif088 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1021/acs.jcim.8b00523 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/j.physrep.2005.10.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.ecolind.2018.01.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.biosystems.2014.03.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.matt.2010.01.001 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/j.vaccine.2020.08.056 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.physrep.2014.07.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.jpsychires.2018.01.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1038/nature04892 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.ajp.2018.01.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/B978-0-12-385051-6.50005-8 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/j.plaphy.2008.03.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False
- 10.1016/j.jgs.2007.05.001 : exp=L1L2_PASS got=T4_L1_NONRESOLVE ok=False
- 10.1016/j.diabres.2018.01.001 : exp=L1L2_PASS got=T4_L1_MISMATCH ok=False

## SPEC compliance notes
- L1 mismatch (not non-resolve) is the reject path for mis-attributed DOIs that resolve to a wrong paper.
- ORACLE FIX: Fixture A row pnas.0811124106 expected 'non-resolve' but RESOLVES to an unrelated paper
  -> corrected expectation = T4_L1_MISMATCH (regenerate Fixture A on spec edit, per D4 discipline).
- L2 dual-signal [D1]: publisher 'RETRACTED' title flag (primary) + RWD index (augment). Coverage gap OWNED.
- clean control present -> accept path (L1L2_PASS) exercised, not VOID-by-construction (E23).
- step1 scope = L1/L2 only. L1L2_PASS is provenance-clean, NOT gold: L4 bind/L5/G-floor still gate (steps 2-4).
