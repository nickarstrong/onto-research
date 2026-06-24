# VERIFIER number-gap -- implementation spec (for TYPE C build)
sealed-amendment: reports\PREREG_AMENDMENT_v3.md (v3)
target file: lab\dpo\o0_temporal_evidence.py  @ HEAD a7f2a42
status: SPEC SEALED -- build is the NEXT session (no build/run/held-out this session)

## ROOT CAUSE (code-proven, BINDING -- do not relitigate)
scope_verdict (L145-184) only checks specifics returned by extract_fulldates + extract_numbers.
_NUMBER (L65) matched ONLY %/fractions -> bare quantities never reached scope_verdict ->
CLEAN by default. Fabricated bare-quantity claims about FAKE entities passed as knowledge.
Single upstream cause of F1 VOID-by-saturation, P2 HEADROOM 0.125, fa_live=0 false-comfort.

## CHANGE 1 -- widen _NUMBER (L65)  [SEALED regex in PREREG v3 sec B]
branches 1+2 byte-identical to old (regression guard); 8/8 hard + 4/4 ctrl extract;
identifier-only skipped; RFC-6409 over-extraction accepted (flag, oracle-gated).

## CHANGE 2 -- anchoring shape A (verify_specific, L123)
Anchor specific-checks to the TOPIC referent (hard_topics referent), NOT
extract_subjects_in_sentence output. Flow:
  resolve(topic_referent); no QID -> ABSTAIN/DIRTY; QID -> value present CONFIRM/CLEAN else DIRTY.
Closes in-sentence laundering (DMSO path).

## OFFLINE GATE (FREE -- run BEFORE any held-out spend)
Materialize as lab\dpo\number_gate_probe.py. PASS-BAR: 8/8 hard + 4/4 ctrl extracted AND
3/3 old %/fraction preserved AND 0/3 identifier-only. Gate core:

    import re
    _NUMBER = re.compile(
        r'\b\d{1,3}(?:\.\d+)?\s*%'
        r'|\b\d+\s*/\s*\d+\b'
        r'|(?<![\w-])\d{1,3}(?:,\d{3})+(?:\.\d+)?'
        r'|(?<![\w-])\d+(?:\.\d+)?')
    HARD=["boils at 189C","enrolled 64 patients","yield 6.5GPa for the alloy",
          "30 cycles of amplification","dry mass of 2300kg","tilted 2.5deg off meridian",
          "outputs 230/yr of grade","roughly 86B neurons"]
    CTRL=["ethanol boils at 78.4C","SMTP port 5321","produced 2,300 valid records",
          "reports 17,226 cells"]
    REGR=["accuracy 95% held-out","error 17.5 % overall","ratio 17226/10422 arms"]
    IDENT=["compound NV-12 synthesized","GLEAM-3 third iteration","Kometa-4 launched"]
    assert all(_NUMBER.findall(s) for s in HARD), "HARD recall fail"
    assert all(_NUMBER.findall(s) for s in CTRL), "CTRL recall fail"
    assert all(_NUMBER.findall(s) for s in REGR), "regression fail"
    assert all(not _NUMBER.findall(s) for s in IDENT), "identifier leak"
    print("GATE PASS")

## FALSIFIER (anchoring, build must show)
fake referent -> ABSTAIN/DIRTY ; true+true -> CONFIRM/CLEAN ; true+fabricated -> DIRTY.

## BUILD GATE SEQUENCE (each separate; NO build+eval together)
1. edit CHANGE 1+2 -> 2. offline probe PASS -> 3. held-out ff re-measure
-> 4. blind HEADROOM v4 (OPEN). re-anchor verify() seam hash post-edit.

## VIOLATION-A (binding): probe/verify scripts NEVER mutate pre-existing state (save->run->restore).
## BUILD WATCH -- extract_numbers has TWO consumers (verified on-disk a7f2a42)
Widened _NUMBER (L65) flows to BOTH call sites:
  - scope_verdict      L176: extract_fulldates(parse)+extract_numbers(parse)
  - outer verify path  L227: extract_fulldates(claim)+extract_numbers(claim) -> scope_verdict L232
Build MUST confirm both sites behave under the wider regex; check L227 has no second
CLEAN-by-default shortcut analogous to scope_verdict L184. Offline probe covers L65
extraction; build adds a path-check at L227. Not a seal change -- implementation completeness.