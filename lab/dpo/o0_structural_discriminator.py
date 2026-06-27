# -*- coding: utf-8 -*-
# Layer-1 hermetic structural discriminator (oracle-free).
# SEPARATE module. The frozen verifier o0_temporal_evidence.py (md5 92766b06) is NOT edited;
# its extract_years_ext is reused as the SINGLE year source (C-1 single-ownership mirror).
#
# Scope (Layer-1 = hermetic: self-consistency only, no external truth):
#   internal_inconsistency : two in-claim years + an asserted "N years" span -> recompute
#                            |Y2 - Y1|; asserted != computed -> DIRTY (claim contradicts ITSELF,
#                            no oracle needed).
#   numeric_false_precision: bare non-year quantity, no offline oracle -> HONEST-ABSTAIN.
#   anachronism            : single year, truth needs an oracle -> HONEST-ABSTAIN (defer Layer-2/B3).
#
# Keystone (gengap v287): enemy is FALSE-DIRTY, never ABSTAIN. DIRTY fires ONLY on an arithmetic
# self-contradiction stated in the claim's own tokens. A fabricated DIRTY would be R7 on the
# verifier itself. ABSTAIN is the honest floor.
#
# R3 LIMITATION (documented, not silently swallowed): the intinc rule assumes the two years and
# the "N years" span form a subtraction relation. A claim carrying two UNRELATED years plus an
# unrelated "N years" count could false-DIRTY. Out-of-scope for this cut (verified 0 false-DIRTY
# on the 15-row PREREG set, B0-B2). A relation-anchor gate is deferred, not built here.

import re, importlib.util

_SPAN = re.compile(r'(\d{1,3})\s+years?\b', re.I)


def load_frozen(path="o0_temporal_evidence.py"):
    """Load the frozen verifier module to borrow its pure year extractor (single year source)."""
    spec = importlib.util.spec_from_file_location("o0te_frozen", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def discriminate(claim, frozen):
    """Return (verdict, meta). verdict in {DIRTY, CLEAN, ABSTAIN}. Pure / offline / hermetic."""
    ce, _bce = frozen.extract_years_ext(claim)        # C-1 mirror: frozen owns "what is a year"
    years = [int(y) for y in ce]                       # ordered-unique, text order
    spans = [int(s) for s in _SPAN.findall(claim)]

    if len(years) == 2 and spans:
        computed = abs(years[1] - years[0])
        asserted = spans[0]
        if asserted != computed:
            return "DIRTY", {"layer": 1, "rule": "internal_inconsistency",
                             "years": years, "asserted": asserted, "computed": computed}
        return "CLEAN", {"layer": 1, "rule": "internal_inconsistency_consistent",
                         "years": years, "asserted": asserted, "computed": computed}

    return "ABSTAIN", {"layer": 1, "rule": "out_of_hermetic_scope",
                       "n_years": len(years), "n_spans": len(spans)}
