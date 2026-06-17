# P1 RESOLUTION-YIELD - CLOSURE (falsifier fired)
home: onto-research/lab/dpo/reports/ (DURABLE git, not pack-only -- prev pack-only copy vanished on rebuild, 3.8)
spec: SPEC_yield_v0 c90f8a40 | closed this session | resolver: s2b_v0.py wd (blob 35eefda1)

## Decision
P1 CLOSED by contract falsifier (GATE sec 6). Judge-iteration (STEP 3-4) NOT pursued.
Reason: on fresh disjoint S-dev, wd resolver already at honest ceiling; headroom ~2 items
at G7/G8 risk = negative ROI. Compute -> E9 DPO (capability growth).

## Baseline of record (telemetry, S-dev VALID)
S-dev = 24 (10 thin / 10 wrong / 4 no-OA), all bars PASS:
  G7 no-poison PASS | G8 no-castration PASS | G9 honesty PASS  -> VERDICT VALID
YIELD (contract sec-1, resolvable 20): thin 8/10 SUPPORTS + wrong 7/10 NOT = 15/20 = 0.75
  S-bar (contaminated, pre-g8fix) 14/20=0.70 ; S-dev (fresh) 15/20=0.75 -> GENERALIZES, no overfit gap
Residual 5/20: 2 thin inconclusive (only real headroom) + 3 wrong honest-UNCLEAR (I2 ceiling, not a gap)

## Caveat (discipline)
Headline number is telemetry (S-dev = read/tuned set), NOT the contract's single-shot held-out.
Falsifier conclusion stands on S-dev VALID; for a DATED PUBLISHABLE number the held-out run is still owed.

## Deferred - buildable on demand
S-held (24) NOT built (thin-correct 0/10; no-OA+wrong on disk use the broken recipe).
Conveyor proven + scripted -> rebuild in one session if the standard needs the dated cite.
  recipe: thin-correct = older-arXiv body, abstract-thin ; wrong = registered older-arXiv + mismatch ;
          no-OA = paywalled classic w/o Crossref abstract (Hartigan-Wong/Kalman/Metropolis/Alder-Wainwright pattern)
  blocklist for disjointness = S-bar(24) UNION S-dev(24) dois (in S_dev.jsonl + ft_cc_v0.jsonl)
  tool: build_yield_candidates.py (arXiv API + OpenAlex OA-status)
  SINGLE-SHOT DISCIPLINE (critical): S-held runs the resolver EXACTLY ONCE = that run IS the number.
    Validate construction BEFORE the run, WITHOUT the resolver: no-OA via Crossref no-abstract check ;
    wrong via arXiv-DOI-resolves check (reject 2606.* 404) ; disjoint + schema. Then one --run + --score.
    NEVER iterate "run -> see leak -> fix" on S-held -- that burns the held-out exactly like S-dev was burned.
  DUE-TRIGGER (build iff this fires, else idle): the first surface/outreach artifact that must CITE verifier
    yield -- article on the verifier / dissertation revision / standard submission. Until then S-held stays
    deferred. "buildable-on-demand" != "someday"; without this trigger the owed number quietly evaporates.

## Tail debt
- I3 getter robustness: on HTTP 404 (unregistered/dead DOI) getter returns ERROR; must fail-closed UNCLEAR.
  Fix ~3 lines: wrap getter fetch, on HTTPError/exception -> verdict UNCLEAR (not ERROR). Not P1 surface.
- arXiv DataCite DOIs (10.48550) are inconsistently in Crossref; very recent (2606.*) 404. Use registered older arXiv for any future FT-CC build.

## Local artifacts (eval/_local/, LOCAL-ONLY never git)
  S_dev.jsonl              md5 9e5fe9be0df59415edf804c279ed8962   (VALID, locked)
  S_dev_ground.json        md5 3424cd47b465bec29d795040225d4fad
  S_dev_s2b_out.jsonl      (wd output, VALID run)
  S_dev_STEP2_RESULT.md    (baseline record)
  S_held_partial.*         (14 items, BROKEN recipe - rebuild or discard)
