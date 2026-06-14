# ledger_v0.md -- ONTO end-to-end loop, one full turn (SPEC_loop_e2e_v0.md sec5)

date    : 2026-06-15
plane   : RESEARCH / North-Star loop, vertical slice v0
artifact: the institute deliverable -- a caught fabrication + a clean accept, end to end.
note    : the planted proposal set (real + fabricated DOIs) is LOCAL-ONLY (bait-class). This public
          ledger records the TURN and its verdict generically, without the planted payload.

## the loop
    PROPOSE  ->  EXTERNAL CHECK (gate)  ->  HUMAN RESIDUAL  ->  ABSORB

The star proposes { claim, source-DOI }. An external, algorithmic conscience checks each DOI,
independent of the proposer. Whatever the algorithm cannot settle goes to an independent human.
Only what clears { resolves AND not-retracted AND human-judged-SUPPORTS } is absorbed.

## the turn (one run, 4 planted items: 1 genuine / 1 fabricated-DOI / 1 retracted / 1 wrong-claim)
- S2 EXTERNAL CHECK (gate, no human input):
    - the fabricated-DOI item   -> DOI does not resolve on Crossref  -> HARD REJECT (caught fabrication).
    - the retracted item        -> resolves, flagged retracted       -> HARD REJECT (caught retraction).
    - the genuine item          -> resolves, not retracted           -> routed to human (supports?).
    - the wrong-claim item      -> resolves, not retracted           -> routed to human (supports?).
- S3 HUMAN RESIDUAL (independent reader, NOT the proposing star):
    - genuine item     -> reader marks SUPPORTS.
    - wrong-claim item -> reader marks NOT (source does not back the claim).
- S4 ABSORB:
    - ABSORBED: the genuine item only.
    - REJECTED: the fabricated-DOI + retracted (by gate), the wrong-claim (by human).

## falsifier (locked before build, SPEC sec4) -- result
    genuine        expect ACCEPT-after-supports     -> ABSORBED                 PASS
    fabricated     expect HARD-REJECT-at-resolve     -> HARD REJECT (no-resolve) PASS
    retracted      expect HARD-REJECT-at-retracted   -> HARD REJECT (retracted)  PASS
    wrong-claim    expect S2-pass-then-human-reject  -> HUMAN REJECT (NOT)        PASS

    absolute guards: zero fabricated/retracted items absorbed ; zero genuine items pre-castrated.

v0 VERDICT : PASS

## what this proves (and what it deliberately does not)
PROVES: the thinnest end-to-end turn RUNS on real Crossref -- the external veto catches a non-resolving
DOI and a retracted DOI with no human input, a genuine claim survives to absorption, and a real-DOI /
wrong-claim is stopped by the human reader. The conscience is OUTSIDE the substrate and the (supports?)
judge is a different actor than the proposer (trust boundary held by construction).

DOES NOT (deferred, by design): automated support-judgment (human in v0) ; live-substrate proposer
(fixed set in v0) ; multi-step agency ; L5 / A-channel precision. The loop turns first ; reality now
says which instrument to build next.

## reproduce
    python loop_e2e_v0.py --selftest      # offline veto validation
    python loop_e2e_v0.py --netcheck      # live resolve + retraction-recall probe
    python loop_e2e_v0.py --run <proposals> --worksheet <ws> --caught <log>
    # human marks <ws> : SUPPORTS | NOT | UNCLEAR
    python loop_e2e_v0.py --finalize --worksheet <ws> --caught <log> --proposals <proposals> --ledger <out>
