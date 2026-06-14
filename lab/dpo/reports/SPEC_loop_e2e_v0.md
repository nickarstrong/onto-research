# SPEC_loop_e2e_v0.md -- ONTO end-to-end loop, vertical slice v0 (FROZEN on accept)

date   : 2026-06-15
plane  : RESEARCH / North-Star loop (NOT A-channel self-checkup ; NOT L5 predicate)
home   : onto-research/reports (dateable priority + reproducibility)
status : DRAFT for Founder review -> FREEZE on accept (bars + falsifier md5-locked before build)
doneness: v0 = medium-rare. Crude end-to-end turn that RUNS. Everything iterated from contact EXCEPT the
          discipline veto, which ships well-done or it does not ship.

## 0 PURPOSE (why this exists, what it is NOT)
The product is the LOOP, not its instruments. Every predicate/gate/eval built so far is scaffolding for
this one turn:

    PROPOSE  ->  EXTERNAL CHECK  ->  HUMAN RESIDUAL  ->  ABSORB

The star PROPOSES (claim + source). An external, algorithmic conscience CHECKS. Whatever the algorithm
cannot settle goes to a HUMAN. Only what passes is ABSORBED. The conscience is OUTSIDE the substrate and
is PERMANENT -- the substrate is never trusted to be its own judge (E8: fabrications pass surface form).
This spec stands up the THINNEST version of that turn that actually runs, so reality -- not more polish --
tells us which instrument to build next.

NOT this spec: L5 independence precision (parked, over_prune 0.50, SEC 3 of pack). NOT the A-channel
self-checkup eval (closed (ii)). Those are organs ; this is the body they hang on.

## 1 THE FOUR STATIONS (v0 doneness per station)
S1 PROPOSE (medium-rare ; v0 = fixed set, live substrate next).
   A proposal = { claim_text, doi, (optional) star_quote }. The star MAY read the DOI to formulate the
   quote (capability -- good). Its self-attestation "I read it, it supports me" is NOT trusted (the read
   improves the proposal ; it is not the verdict). v0 proposer = a SMALL FIXED proposal set on disk
   (proposals_v0.jsonl), deliberately seeded with planted defects (see S4). Wiring the live frozen
   substrate as proposer = v0.1, AFTER the machine is shown to turn.

S2 EXTERNAL CHECK = THE GATE (well-done ; the only fully-cooked station).
   Per proposed doi, independent of the star:
     (a) RESOLVE      : Crossref works lookup. doi does not resolve -> FABRICATION -> HARD REJECT.
     (c) RETRACTED    : retraction lookup. retracted/withdrawn -> HARD REJECT.
     (b) SUPPORTS?    : does the resolved source actually back claim_text? This is JUDGMENT, not regex.
                        v0 does NOT automate it and does NOT let the star self-answer it -> routed to S3.
   Veto rule (HARD, no medium-rare): any (a)-fail or (c)-fail = REJECT, logged as a caught fabrication.
   (a)+(c) reuse the live-resolve pattern already in run_L5_partI_validate.fetch_crossref (Crossref works
   endpoint, per-doi, on-demand -- O(citations), never O(corpus)). Retraction lookup = a new lightweight
   call (Crossref `update-to` / RetractionWatch), TO BE WIRED in v0.

S3 HUMAN RESIDUAL (real for v0).
   Everything the algorithm cannot settle -- i.e. (b) supports? -- is handed to an independent reader
   (Founder, or a separate non-proposing instance), never back to the proposing star. v0 = a worksheet
   the reviewer marks SUPPORTS / NOT / UNCLEAR. Cheap checks auto ; the hard judgment is human, by design,
   and NOT faked as automated.

S4 ABSORB (real for v0).
   Only proposals that clear ALL of { resolve, not-retracted, supports } are ABSORBED (recorded as accepted
   knowledge). Anything rejected is logged as caught. ABSORB v0 = append to an accepted-ledger ; no
   substrate write-back yet (the star self-trains nothing -- it proposes, we dispose).

## 2 TRUST BOUNDARY (the one line that must not blur)
star read  = upstream, improves the PROPOSAL.        (trusted for FORM, never for TRUTH)
gate read  = downstream, renders the VERDICT.        (the only authority on accept/reject)
Same source text, different power. v0 enforces this by construction: the gate re-resolves and the (b)
judge is a different actor than the proposer.

## 3 v0 SCOPE CONTRACT (anti-zadrot ; what is deliberately crude)
REAL in v0      : S2(a) resolve, S2(c) retracted, S3 human worksheet, S4 ledger, S4 caught-log.
STUBBED/FIXED   : S1 proposer = fixed proposals_v0.jsonl (not the live substrate).
EXPLICIT DEFER  : automated (b) support-judgment ; live-substrate proposer ; multi-step agency ; any
                  L5/A-channel precision work. Do NOT gold-plate these in v0.
WELL-DONE only  : the veto (S2 HARD reject on fabricate/retract). No medium-rare here -- a half-working
                  fabrication veto is worse than none (false confidence ; the substrate learns to slip).

## 4 FALSIFIER (what would prove v0 does NOT work -- locked before build)
proposals_v0.jsonl carries >=4 planted items:
  F1 genuine     : real doi, real support           -> expect ACCEPT (after S3 SUPPORTS).
  F2 fabricated  : invented non-resolving doi        -> expect HARD REJECT at S2(a).
  F3 retracted   : a known retracted doi              -> expect HARD REJECT at S2(c).
  F4 wrong-claim : real doi, claim it does NOT back   -> expect S2 pass (a/c), S3 marks NOT -> REJECT.
v0 PASSES iff: F2 and F3 are HARD-rejected by the gate WITHOUT human input ; F1 reaches S3 and can be
accepted ; F4 reaches S3 and is rejected there. ANY fabricated/retracted item that ABSORBS = v0 FAIL
(salmonella ; do not ship). Any genuine item the gate hard-rejects pre-S3 = over-castration = v0 FAIL.

## 5 THE ONE ARTIFACT (the institute deliverable)
ledger_v0.md : one legible record of a full turn --
  "star proposed { F1..F4 } ; gate hard-rejected F2 (no-resolve) + F3 (retracted) ; routed F1,F4 to human ;
   human accepted F1, rejected F4 ; ABSORBED: F1."
That record -- a caught fabrication + a clean accept, end to end -- is the peer-reviewable proof of the bet.
Not an F1-score. This is what a regulator/reviewer reads.

## 6 NON-GOALS for v0
No live substrate proposer. No automated support-judge. No retraction DB build-out (one lookup is enough).
No L5/A-channel touching. No autonomy/self-training. Resist every urge to cook these now -- the loop must
turn first.

## 7 BUILD ORDER (one step/msg next session ; TYPE C build then TYPE B run, may split)
  1. write proposals_v0.jsonl (F1-F4 planted ; LOCAL-ONLY, holds real dois).
  2. build loop_e2e_v0.py : S2 gate (resolve + retracted, reuse fetch_crossref pattern) -> S3 worksheet
     emit -> S4 ledger/caught-log. READ-ONLY on the substrate ; no predicate/SPEC byte.
  3. net pre-check -> run on proposals_v0 -> gate auto-verdicts F2/F3, worksheet for F1/F4.
  4. human marks the worksheet (S3) -> finalize ABSORB (S4) -> ledger_v0.md.
  5. check against S4 falsifier ; commit loop_e2e_v0.py + ledger_v0.md (generic-safe) to onto-research ;
     proposals_v0.jsonl LOCAL-ONLY (holds the planted set -> never public, same as bait).

trigger : "LABA, LOOP E2E v0"  (non-colliding ; supersedes the ambiguous "LOOP v0").
