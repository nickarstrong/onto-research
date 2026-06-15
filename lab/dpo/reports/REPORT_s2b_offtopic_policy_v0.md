# REPORT_s2b_offtopic_policy_v0.md -- B2 off-topic->NOT policy : build + selftest + run

date   : 2026-06-16
plane  : RESEARCH / S2(b) -- implement-and-run against the frozen gate
gate   : GATE_s2b_offtopic_v0.md (pre-registered, frozen ; bars not relitigated by results, R7)
organ  : s2b_v0.py md5 75ba0a71a77de65692bc4a98db7b8a07 (predicate added in place, canonical name)
scope  : PUBLIC-SAFE -- counts and bar outcomes only. No DOIs, claim-texts, or abstracts.
         Control set + off-topic positives + selftest fixtures = LOCAL-ONLY, never public (privacy 3.2).

## 1 PREDICATE (gate sec 1)
Deterministic, no LLM, evaluated before the B2 model verdict. Returns NOT (leg=supports,
reason=off_topic) iff BOTH:
  (a) the claim's SUBJECT token-set has ZERO overlap with title+abstract ; AND
  (b) title+abstract carry their own non-thin subject (>= 8 subject tokens).
Subject tokens = content tokens minus a fixed, domain-agnostic English function-word set
(articles/conjunctions/prepositions/auxiliaries/pronouns). NO synonym/hypernym expansion and NO
domain-specific filler list -- a map keyed to the known positives would be tuning-to-pass (R7).
Otherwise the existing SUPPORTS / UNCLEAR mapping is UNCHANGED.

## 2 BARS (frozen ; HARD dominates)
  G1-G4 (=G6, no regression) : PASS, on the frozen falsifier with the real B2 model
                               (J2->NOT/binding ; J3 zero->SUPPORTS ; J1->SUPPORTS ; J4->UNCLEAR).
  G5 (HARD, no-castration, tol 0) : PASS. ZERO control-set correct-cites flipped to NOT.
                               n(CC)=18 (6 methods / 6 terse / 6 tangent). Held OFFLINE (fake getter,
                               md5-locked grounding) AND LIVE (Crossref/OpenAlex fetch).
PASS = G5 & G6. Both hold. The policy adds off_topic NOTs only on off-topic items ; it never moved
J1/J3/J4 and never flipped a correct cite.

## 3 RECALL (DIAGNOSTIC readout, NOT a bar)
Off-topic positives n=4 (same-venue+same-year wrong-bindings + one cross-domain mint).
  offline (md5-locked grounding) : 3/4 caught.
  live (Crossref/OpenAlex)       : 2/4 caught.
Delta is a source-availability effect, not a predicate regression: one positive's DOI returned an
empty abstract live -> deterministic no_abstract UNCLEAR (honest abstention, never a fabricated NOT).
One residual positive shares only generic cross-domain filler tokens with its (wrong) source; subject
overlap is non-zero at the token level -> stays UNCLEAR by design. Under-catch is honest UNCLEAR ;
over-catch would be castration. Precision-first held.

## 4 VERDICT
Off-topic->NOT is BUILDABLE+VALID at the abstract level under the frozen gate: it caps the residual
B1-blind off-topic wrong-bindings into NOT where a discriminating abstract is available, and abstains
honestly otherwise. Same-journal+same-year wrong-bindings without a usable live abstract, and
generic-filler near-overlaps, DEFER to full-text (SPEC sec 8) -- not tuned to fit. Results did not
move the bar.

## 5 REPRODUCIBILITY
  offline   : python s2b_v0.py --selftest --det-only      (G1+G4+B1-no-fire + G5, no model/network)
  full      : python s2b_v0.py --selftest --b2 local       (adds G2 + B2-content G3 via real model)
  live run  : python s2b_v0.py --run <cc+j5> --b2 local    (G5 + recall against live abstracts)
Fixtures (control set, off-topic positives, grounding, falsifier) are LOCAL-ONLY by privacy policy.
