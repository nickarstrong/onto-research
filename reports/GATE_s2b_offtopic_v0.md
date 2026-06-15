# GATE_s2b_offtopic_v0.md -- pre-registered gate for the B2 off-topic->NOT policy (DRAFT -> FREEZE on accept)

date   : 2026-06-15
plane  : RESEARCH / S2(b) -- B2 decision-policy gate. THIS DOC = eval design only. NO predicate byte (R7).
home   : onto-research/reports (dateable priority + reproducibility ; generic-safe, ZERO dois/claim-texts/abstracts)
status : DRAFT for Founder review -> FREEZE on accept (md5-locked BEFORE any policy byte, same as SPEC_s2b_v0 §6)
binds  : SPEC_s2b_v0.md (md5 80bdf2a9, frozen). This gate ADDS to its bars ; relitigates none of G1-G4.

## 0 WHAT THIS GATES (one paragraph, zero-context reader)
The keystone loop is SAFE (0/30 absorbed). The residual 11 UNCLEAR split 8 honest-thin / 3 B1-blind / 0 B2-soft.
The 3 B1-blind (Higgs / Statins / mRNA) are SAME-JOURNAL + SAME-YEAR wrong-bindings: the cited DOI resolves to a
real paper whose author/year/venue MATCH the citation tokens (so B1 passes) but whose subject is a DIFFERENT topic.
Today B2 reads that off-topic abstract, finds no support, and honestly returns UNCLEAR. A proposed B2 policy would
return NOT instead ("abstract clearly off-topic to the claim -> NOT"). That policy can FALSE-FIRE: a CORRECT citation
whose abstract is terse, methods-only, or tangential also yields "no explicit support found", and a brittle
topic-match would flip it to NOT and begin fabricating-by-omission. This doc freezes the no-false-fire bar that any
such policy must clear FIRST. The policy itself is a SEPARATE later session ; this is eval, not fix (R7).

## 1 THE DECISION RULE (falsifiable, R6) -- the discriminator is SUBJECT-OVERLAP, not RESULT-COVERAGE
Today B2 collapses two distinct relations into one UNCLEAR:
  (i)  ON-TOPIC-INSUFFICIENT : abstract is about the claim's subject but does not state the claimed result
                               (methods-only / terse / tangential). The cite may be CORRECT. -> must stay UNCLEAR.
  (ii) OFF-TOPIC             : abstract is about a DIFFERENT subject entirely (wrong DOI). -> the new NOT.

The policy MAY return NOT (leg=supports, reason=off_topic) only when OFF-TOPIC holds. OFF-TOPIC is defined on
SUBJECT, never on result-coverage:

  OFF-TOPIC(claim, fetched) := TRUE iff BOTH hold --
    (a) the claim's PRIMARY subject token-set (its defining entity / measured quantity / named mechanism, and
        their synonyms/hypernyms) has ZERO overlap with title+abstract ; AND
    (b) title+abstract have an identifiable PRIMARY subject of their own that is a DIFFERENT topic
        (not merely thin/empty -- emptiness is the no_abstract / UNCLEAR short-circuit, already handled).
  Otherwise OFF-TOPIC := FALSE -> the existing SUPPORTS / UNCLEAR mapping is UNCHANGED.

Why this discriminates the false-fire cases:
  - methods-only correct cite : abstract describes method M used IN the paper ; claim is a result the paper reports.
    The studied system/phenomenon (the subject) is SHARED -> (a) fails -> NOT off-topic -> UNCLEAR. Protected.
  - tangential correct cite    : same subject, claim is a secondary finding -> (a) fails -> UNCLEAR. Protected.
  - off-topic wrong DOI        : subject entirely different -> (a) and (b) hold -> NOT. Caught.

APPROACH-LEVEL FALSIFIER (R6): if no subject-overlap predicate can separate the 3 B1-blind off-topic cases from
the methods-only/tangential CORRECT cites without false-firing -- i.e. a methods-only correct cite is
subject-indistinguishable from an off-topic wrong cite at the abstract level -- then off-topic->NOT is NOT safely
gateable on the abstract and DEFERS to full-text (SPEC §8 deferred). The run REJECTS the policy ; it does not tune it.

## 2 THE CLEAN-CONTROL SET (blocking finding -- must be BUILT, R7/R2/C5)
FINDING (verified on the frozen falsifier, md5 8307d97d): the 4 J1 items are all STRONG bound+backed -- each
abstract explicitly states the claimed result. NONE is methods-only / terse / tangential. Off-topic->NOT therefore
CANNOT false-fire on J1 ; a bar set against J1 alone is beautiful-empty (C5) and proves nothing about the actual
castration risk.

REQUIREMENT (pre-registered ; precondition of the policy run, NOT optional):
  CC = a purpose-built clean-control set of CORRECT citations (right-bound, non-retracted, resolving) chosen to
  EXERCISE the false-fire surface. Composition MUST include, in declared minimum counts:
    - CC-methods  : correct cite, abstract is methods-only (result not in abstract).      n >= 6
    - CC-terse    : correct cite, abstract present but minimal/one-line.                   n >= 6
    - CC-tangent  : correct cite, abstract on the claim's subject but claim = 2nd finding. n >= 6
  TOTAL n(CC) >= 18. Every item's DOI grounded LIVE before entry (anti-fab 3.9). LOCAL-ONLY, bait-class
  (holds real dois/claim-texts) -- never public git. Every CC item is, by construction, NOT a genuine NOT:
  the cite is correct, so the only correct verdicts on CC are SUPPORTS or UNCLEAR -- never NOT.

  OFF-TOPIC POSITIVES (recall side, diagnostic): a J5 class of >= 4 same-journal+same-year off-topic wrong-bindings
  (the Higgs/Statins/mRNA pattern), expect NOT (leg=supports, reason=off_topic). LOCAL-ONLY.

## 3 BARS (pre-registered, frozen ; HARD dominates, C1)
  G5 (HARD, no-castration) : ZERO CC items return NOT. A correct citation flipped to NOT is castration ; this is
                             the precision-first spine and mirrors the existing G3 (J1->NOT = 0). tol 0.
  G6 (consistency)         : G1-G4 of SPEC_s2b_v0 still hold under the policy (no regression on the frozen
                             falsifier). The policy may only ADD off_topic NOTs on OFF-TOPIC items, never move J1/J3/J4.
  PASS (policy is BUILDABLE+VALID) = G5 & G6. Recall on J5 (off-topic caught) is a DIAGNOSTIC READOUT, NOT a bar
  (SPEC §9 frame: precision-first ; under-catching off-topic is honest UNCLEAR, over-catching is castration).

NOTE on the <= 0.10 precedent (SEC1 step 3): a non-zero false-NOT allowance would RELAX the existing G3 (tol 0)
discipline. Recommended bar is tol 0 (G5), consistent with G3 -- a curated CC set with no genuine NOTs makes tol 0
the correct, non-brittle target. If Founder rules <= 0.10, that is a documented relaxation, ruled before the run.

## 4 WHAT THIS DOC DOES NOT DO
  - No predicate byte. s2b_v0.py is UNCHANGED this session (R7 ; eval+fix never share).
  - No CC items written here (this doc is public-safe). CC + J5 construction is the FIRST step of the next plane.
  - No tuning loop. The run either clears G5 & G6 or REJECTS the policy (defers to full-text). Results never
    relitigate the bar (R7).

## 5 NEXT PLANE (handed in close pack ; do NOT start here)
  PLANE: implement-and-run the off-topic->NOT policy against this frozen gate.
  STEP 1 of that plane: build CC (n>=18, the 3 sub-classes) + J5 (n>=4), dois grounded LIVE, md5-lock -- BEFORE
         any policy byte. STEP 2: implement the §1 OFF-TOPIC predicate in b2_supports. STEP 3: --selftest must
         re-prove G1-G4 AND prove G5 (0/CC -> NOT) offline. STEP 4: run, report G5/G6 PASS + J5 recall readout.
  trigger : "LABA, S2B OFFTOPIC POLICY"

freeze: on Founder accept, md5-lock this doc and the §3 bars before the next plane's first byte.
