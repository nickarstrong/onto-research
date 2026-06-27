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
# v322 OWED-R3RELATION: relation-anchor gate NOW BUILT below (additive, MONOTONE: ABSTAIN-only),
# behind 4 pre-registered bars (B0-strict35 / B-recall 5/5 / B-relation ord_prov_v4:11 / B-hermetic).

import re, importlib.util

_SPAN = re.compile(r'(\d{1,3})\s+years?\b', re.I)

# v322 relation-anchor (hermetic, in-claim structure only; NO oracle, NO network). Binds
# {year_a, year_b, span_value} iff all three co-occur in ONE sentence-window AND a closed
# duration-cue connective is present in that window. Closed cue set derived from the live
# internal-contradiction channel; extend the cue set (not the eligibility) if a real binding
# pattern is missed (v321 design sec 3). ABSTAIN is the honest floor (R7), never a fabricated DIRTY.
_SENT_SPLIT = re.compile(r'[.\n;]')
_DURATION_CUES = ("age of", "lived", "stood", "apart", "lasting", "after")


def _relation_anchor(claim, years, spans):
    """True iff EXACTLY ONE single-sentence window co-binds both years + the span value with a
    closed-cue duration connective. Zero or >=2 binding windows -> False (-> ABSTAIN upstream)."""
    if len(years) != 2 or not spans:
        return False
    ya_re = re.compile(r'\b' + str(years[0]) + r'\b')
    yb_re = re.compile(r'\b' + str(years[1]) + r'\b')
    span_re = re.compile(r'\b' + str(spans[0]) + r'\s+years?\b', re.I)
    n_bind = 0
    for seg in _SENT_SPLIT.split(claim):
        if ya_re.search(seg) and yb_re.search(seg) and span_re.search(seg):
            seg_l = seg.lower()
            if any(cue in seg_l for cue in _DURATION_CUES):
                n_bind += 1
    return n_bind == 1


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
        # v322 OWED-R3RELATION relation-anchor precondition (additive, MONOTONE: ABSTAIN-only,
        # never a new DIRTY). The subtraction check below is UNCHANGED; it only runs when the
        # two years and the span value co-bind ONE asserted duration relation (single-sentence
        # window + closed duration-cue set). Not bound -> ABSTAIN (ord_prov_v4:11 failure mode).
        if not _relation_anchor(claim, years, spans):
            return "ABSTAIN", {"layer": 1, "rule": "relation_anchor_unbound",
                               "n_years": len(years), "n_spans": len(spans)}
        computed = abs(years[1] - years[0])
        asserted = spans[0]
        if asserted != computed:
            return "DIRTY", {"layer": 1, "rule": "internal_inconsistency",
                             "years": years, "asserted": asserted, "computed": computed}
        return "CLEAN", {"layer": 1, "rule": "internal_inconsistency_consistent",
                         "years": years, "asserted": asserted, "computed": computed}

    return "ABSTAIN", {"layer": 1, "rule": "out_of_hermetic_scope",
                       "n_years": len(years), "n_spans": len(spans)}
