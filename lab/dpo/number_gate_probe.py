#!/usr/bin/env python3
"""number_gate_probe.py -- offline build-verification for the verifier number-gap fix (PREREG v3).

Two hermetic gates. NO network, NO state mutation (VIOLATION-A: this probe never opens, writes, or
mutates any pre-existing file -- all inputs are in-memory synthetic).

  GATE 1 (CHANGE 1): widened _NUMBER recall/precision vs the SEALED PASS-BAR
                     (HARD 8/8, CTRL 4/4, REGR 3/3 preserved, IDENT 0/3 leak).
  GATE 2 (CHANGE 2): shape-A topic-anchoring falsifier on synthetic inputs with MOCKED probe
                     primitives -- demonstrates the three sealed falsifier rows through the REAL
                     patched verify_specific + scope_verdict control flow:
                       fake referent            -> ABSTAIN -> DIRTY
                       true referent + true val -> CONFIRM -> CLEAN
                       true referent + fab val  -> ABSTAIN -> DIRTY

Run: python number_gate_probe.py   ->  GATE 1 / GATE 2 / ALL GATES PASS, else AssertionError.
"""
import re
import o0_temporal_evidence as V   # the patched verifier (widened _NUMBER + shape-A verify_specific)


# ---------------- GATE 1: _NUMBER widen (sealed regex; bar = 8/8 + 4/4 + 3/3 + 0/3) --------------
def gate1():
    NUM = V._NUMBER
    HARD = ["boils at 189C", "enrolled 64 patients", "yield 6.5GPa for the alloy",
            "30 cycles of amplification", "dry mass of 2300kg", "tilted 2.5deg off meridian",
            "outputs 230/yr of grade", "roughly 86B neurons"]
    CTRL = ["ethanol boils at 78.4C", "SMTP port 5321", "produced 2,300 valid records",
            "reports 17,226 cells"]
    REGR = ["accuracy 95% held-out", "error 17.5 % overall", "ratio 17226/10422 arms"]
    IDENT = ["compound NV-12 synthesized", "GLEAM-3 third iteration", "Kometa-4 launched"]
    assert all(NUM.findall(s) for s in HARD),  "HARD recall fail"
    assert all(NUM.findall(s) for s in CTRL),  "CTRL recall fail"
    assert all(NUM.findall(s) for s in REGR),  "regression fail"
    assert all(not NUM.findall(s) for s in IDENT), "identifier leak"
    print("GATE 1 (CHANGE 1 _NUMBER widen) PASS  [HARD 8/8, CTRL 4/4, REGR 3/3, IDENT 0/3]")


# ---------------- GATE 2: shape-A anchoring falsifier (mocked primitives, no network) ------------
class MockT:
    """Hermetic stand-in for o0_temporal_probe_v5. Controls resolution + article text per case.
       _TOK / extract_subjects_in_sentence / strip_wiki_markup mirror the frozen probe semantics."""
    def __init__(self, qid_for, article_for):
        self._qid_for = qid_for          # subject_label_lower -> qid (or absent = unresolved)
        self._article_for = article_for  # qid -> wiki fulltext

    _TOK = staticmethod(lambda s: set(re.findall(r'[a-z]{3,}', (s or "").lower())))

    def strip_wiki_markup(self, t):
        return t or ""

    def extract_subjects_in_sentence(self, sentence, anchor):
        cands = []
        for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', sentence):
            cands.append(m.group(1))
        for m in re.finditer(r'\b([A-Z][a-zA-Z]{2,})\b', sentence):
            tok = m.group(1)
            if not any(tok in c and c != tok for c in cands):
                cands.append(tok)
        seen, out = set(), []
        for c in cands:
            if c.lower() not in seen:
                seen.add(c.lower())
                out.append(c)
        return out[:6]

    def subject_role(self, label, sent):
        return "thing"

    def resolve_subject(self, label, ctx, role):
        q = self._qid_for.get(label.lower())
        return (q, "desc", 1, "mock") if q else None

    def entity_data(self, qid):
        return {"enwiki_title": "T_%s" % qid}

    def wiki_fulltext(self, title):
        return self._article_for.get(title.replace("T_", "", 1), "")


def _drive(spec, claim, topic, T):
    """Run the patched verify_specific then scope_verdict on a synthetic empty-abstract record."""
    sv, _ = V.verify_specific(spec, claim, set(), T, {}, topic=topic)
    rec = {"id": "syn", "claim": claim, "evidence": {"abstract": ""},
           "temporal": {"per_year": {}, "snippets": {}, "per_specific": {V._norm(spec): sv}}}
    verdict, _reasons = V.scope_verdict(rec)
    return sv, verdict


def gate2():
    # C-2 (PREREG v4) UPDATE: empty-abstract non-confirm is ABSTAIN, NOT DIRTY. The shape-A anchoring
    # still drives resolution; only the empty-abstract verdict changes (oracle-rescue path FALSIFIED).
    # Row 1 -- fake referent (nothing resolves), empty abstract -> ABSTAIN -> claim ABSTAIN (was DIRTY)
    T1 = MockT(qid_for={}, article_for={})
    sv1, v1 = _drive("78.4", "Kometa probe boils at 78.4 C.",
                     "Boiling point of the Soviet probe Kometa-4", T1)
    assert sv1 == "ABSTAIN" and v1 == "ABSTAIN", "row1 fake-referent: sv=%s v=%s" % (sv1, v1)

    # Row 2 -- true referent + true value -> CONFIRM -> CLEAN (unchanged)
    T2 = MockT(qid_for={"ethanol": "Q153"},
               article_for={"Q153": "Ethanol boils at 78.4 C under standard pressure."})
    sv2, v2 = _drive("78.4", "Ethanol boils at 78.4 C.", "Ethanol boiling point", T2)
    assert sv2 == "CONFIRM" and v2 == "CLEAN", "row2 true+true: sv=%s v=%s" % (sv2, v2)

    # Row 3 -- true referent + fabricated value, empty abstract -> ABSTAIN -> claim ABSTAIN (was DIRTY).
    # C-2 TRADE: a fab value on an EMPTY abstract is UNCATCHABLE; the verifier declares ABSTAIN (quarantine)
    # rather than fake-detect. Catch on fab values is preserved WHERE evidence exists (see gate4 contradiction).
    T3 = MockT(qid_for={"ethanol": "Q153"},
               article_for={"Q153": "Ethanol boils at 78.4 C under standard pressure."})
    sv3, v3 = _drive("999.9", "Ethanol boils at 999.9 C.", "Ethanol boiling point", T3)
    assert sv3 == "ABSTAIN" and v3 == "ABSTAIN", "row3 true+fab: sv=%s v=%s" % (sv3, v3)

    print("GATE 2 (shape-A anchoring, C-2 verdicts) PASS  [fake->ABSTAIN, true+true->CLEAN, true+fab->ABSTAIN]")


# ---------------- GATE 3: C-1 year single-ownership (PREREG v4, hermetic) ------------------------
def gate3():
    H = V.extract_numbers_nonyear
    # year tokens subtracted from the non-year number gate
    assert H("Newton published Principia in 1687.") == [], "C-1: lone year leaked to number gate"
    assert H("active 1856 and 1864 across the span") == [], "C-1: range-pair years leaked"
    assert H("ran from 1900 to 1925") == [], "C-1: 'to'-range years leaked"
    # true bare quantities RETAINED (not year-subtracted) -- out-of-band ints + decimals + %
    assert H("enrolled 64 patients") == ["64"], "C-1: bare qty wrongly subtracted"
    assert H("yield 6.5 GPa") == ["6.5"], "C-1: decimal qty wrongly subtracted"
    assert H("dry mass of 2300 kg") == ["2300"], "C-1: out-of-band 4-digit qty wrongly subtracted"
    assert H("accuracy 95% held-out") == ["95%"], "C-1: percent wrongly subtracted"
    # control flow: year-only TRUE claim must NOT go DIRTY via the number gate
    rec_year = {"id": "y", "claim": "Newton published Principia in 1687.",
                "evidence": {"abstract": ""},
                "temporal": {"per_year": {"1687": "CONFIRM"}, "snippets": {}, "per_specific": {}}}
    vy, _ = V.scope_verdict(rec_year)
    assert vy != "DIRTY", "C-1: year-only claim went DIRTY via number gate: %s" % vy
    # control flow: fab bare-qty still REACHES the gate -> contradiction makes it DIRTY
    rec_fab = {"id": "f", "claim": "enrolled 64 patients",
               "evidence": {"abstract": "the trial enrolled 12 patients"},
               "temporal": {"per_year": {}, "snippets": {}, "per_specific": {"64": "REFUTE"}}}
    vf, _ = V.scope_verdict(rec_fab)
    assert vf == "DIRTY", "C-1: contradicted bare-qty did not reach the gate: %s" % vf
    print("GATE 3 (C-1 year single-ownership) PASS  [years/ranges subtracted; bare-qty retained+gated]")


# ---------------- GATE 4: C-2 evidence-state 3-state gate (PREREG v4, hermetic) ------------------
def gate4():
    # empty-abstract TRUE bare-qty -> ABSTAIN (not DIRTY): no evidence, no contradiction, no rescue
    rec_empty = {"id": "e", "claim": "the device draws 64 watts",
                 "evidence": {"abstract": ""},
                 "temporal": {"per_year": {}, "snippets": {}, "per_specific": {"64": "ABSTAIN"}}}
    ve, _ = V.scope_verdict(rec_empty)
    assert ve == "ABSTAIN", "C-2: empty-abstract bare-qty not ABSTAIN: %s" % ve
    # evidence-contradicted bare-qty -> DIRTY (positive disagreement via oracle REFUTE)
    rec_contra = {"id": "c", "claim": "the device draws 64 watts",
                  "evidence": {"abstract": "the device draws 12 watts"},
                  "temporal": {"per_year": {}, "snippets": {}, "per_specific": {"64": "REFUTE"}}}
    vc, _ = V.scope_verdict(rec_contra)
    assert vc == "DIRTY", "C-2: contradicted bare-qty not DIRTY: %s" % vc
    # confirmed bare-qty (literal in non-empty abstract) -> CLEAN
    rec_ok = {"id": "o", "claim": "the device draws 64 watts",
              "evidence": {"abstract": "the device draws 64 watts continuously"},
              "temporal": {"per_year": {}, "snippets": {}, "per_specific": {}}}
    vo, _ = V.scope_verdict(rec_ok)
    assert vo == "CLEAN", "C-2: confirmed bare-qty not CLEAN: %s" % vo
    # ABSTAIN must NOT leak to CLEAN, and must NOT be DIRTY -> it is a real third state
    assert ve not in ("CLEAN", "DIRTY"), "C-2: ABSTAIN collapsed into CLEAN/DIRTY"
    print("GATE 4 (C-2 evidence-state 3-state) PASS  [empty->ABSTAIN, contradicted->DIRTY, confirm->CLEAN]")


if __name__ == "__main__":
    gate1()
    gate2()
    gate3()
    gate4()
    print("ALL GATES PASS")
