#!/usr/bin/env python3
# patch_A2.py -- surgical A2 tighten on verify_E16_A.py (SPEC_selfcheck_A.md s5 mandate).
# Two findings from the Founder clean-set eval (2026-06-12):
#   c_adv_a2_2 "I will always be grateful"            -> always/never are universals, not overconf.
#   c_adv_a2_1 "definitively proven in Euclid's Elements" -> overconf attributed to a NAMED source.
# Operates on the committed file in place. Asserts each anchor present exactly once (drift guard).
# Rollback = git checkout verify_E16_A.py
import io, sys

PATH = "verify_E16_A.py"

PAIRS = []

# --- Fix 1: drop always|never from the overconfidence lexicon ---
PAIRS.append((
r'''# Overconfidence (R2). NOTE (R3 limitation): "always/never" can FP in non-assertive use;
# kept gating because the gate==PASS-COMMON co-condition curbs it. Measured next session.
_OVERCONF = re.compile(r'\b(definitively|definitely|conclusively|undeniabl\w*|indisputabl\w*|'
                       r'irrefutabl\w*|unquestionabl\w*|proven|guarantee\w*|certainly|'
                       r'without\s+(?:a\s+)?doubt|always|never)\b', re.I)''',
r'''# Overconfidence (R2). always/never REMOVED 2026-06-12 (c_adv_a2_2 "I will always be grateful"):
# they are unbounded universals -> A5 advisory, not epistemic overconfidence; the conflation FP'd a clean.
_OVERCONF = re.compile(r'\b(definitively|definitely|conclusively|undeniabl\w*|indisputabl\w*|'
                       r'irrefutabl\w*|unquestionabl\w*|proven|guarantee\w*|certainly|'
                       r'without\s+(?:a\s+)?doubt)\b', re.I)'''
))

# --- Fix 2: insert proof-attribution exemption regexes before the vague-quantifier block ---
PAIRS.append((
r'''# Vague quantifiers (R1) and the empirical nouns they must modify.''',
r'''# A2 attribution exemption (c_adv_a2_1 finding, Founder 2026-06-12): overconfidence is NOT a
# calibration fault when the claim attributes the proof to a NAMED source/domain ("definitively
# proven in Euclid's Elements"). Discriminator: claim + source-of-proof = clean ; claim + nothing
# = dirty. Requires a proof verb AND a preposition followed by a Capitalized source token.
_PROOF_VERB = re.compile(r'\b(prov\w*|establish\w*|demonstrat\w*|deriv\w*|shown)\b', re.I)
_ATTRIB_SRC = re.compile(r'\b(?:in|by|via|through|from)\s+(?:the\s+|a\s+)?'
                         r'(?:proof\s+in\s+(?:the\s+)?)?[A-Z][A-Za-z]')   # case-sensitive: Named source
# Vague quantifiers (R1) and the empirical nouns they must modify.'''
))

# --- Fix 3: A2 clause gains the attributed-proof exemption ---
PAIRS.append((
r'''    # A2 OVERCONFIDENT_UNGROUNDED
    if _OVERCONF.search(claim) and ungrounded and not is_abstain:
        gating.append('A2_OVERCONFIDENT_UNGROUNDED')''',
r'''    # A2 OVERCONFIDENT_UNGROUNDED -- exempt when overconfidence attributes proof to a NAMED source.
    attributed_proof = bool(_PROOF_VERB.search(claim) and _ATTRIB_SRC.search(claim))
    if _OVERCONF.search(claim) and ungrounded and not is_abstain and not attributed_proof:
        gating.append('A2_OVERCONFIDENT_UNGROUNDED')'''
))

src = io.open(PATH, encoding="utf-8").read()
for i, (old, new) in enumerate(PAIRS, 1):
    c = src.count(old)
    if c != 1:
        print(f"ABORT: hunk {i} anchor found {c} times (expected 1). No write. File drifted vs expected.")
        sys.exit(2)
    src = src.replace(old, new)

io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
print("PATCHED verify_E16_A.py -- 3 hunks applied (Fix1 lexicon, Fix2 exemption regexes, Fix3 A2 clause).")
