# PRE_REGISTER E20 - branch decision + criterion (pre-run, R6)

Pre-registered BEFORE any execution. Governs E20. No post-hoc bar editing.
Provenance: E19 NO-GO (report_E19.md) + keystone sec 4 (bindability primitive, NLI secondary).

## DECISION: BRANCH B (bindability-only gate-2 measurement). Branch A conditional, deferred.

Rationale (destination governs, keystone sec 0/4):
- The verifier exists to enable SELF-LEARNING via rejection-sampling RFT (NORTH STAR property 2).
- Rejection sampling is PRECISION-bound, not recall-bound: a fabrication that passes contaminates
  weights (cardinal R7 / E15 failure); a clean sample discarded only costs yield, and
  self-generated yield is cheap. Therefore accept-PRECISION is the governing axis; recall is yield.
- E19 already wall-tested the contradiction-veto axis: the leak is a retrieval/bind-precision wall
  (E17), not an NLI weakness (NLI contradiction is oracle-perfect, B2_oracle=1.0). Branch A's NLI
  swap does not touch that wall; its binder lever is the same wall E17 hit.
- => Branch A spends model-scale compute on a recall bar (B1>=0.90) the destination does not
  require. Branch B measures the destination-true quantity cheaply on frozen artifacts and GATES
  whether Branch A is even necessary.

## MEASUREMENT (E20-B, TYPE C - run, no new design)
Substrate: bindability-only acceptance, NLI layer OFF.
  Frozen reused byte-identical: verify_E16.py, gold_retrieve.py, semantic_retrieve.py.
  Held-out: heldout_E17.jsonl v3, md5 7e9fe030646d5671952e7a9fe9437e37 (LOCAL-only).
  Fixture:  gold_fixture_E18.json, md5 493b8ada955edd89c0f169609a121887 (LOCAL-only).
Decision rule under test: bind to a real locator -> ACCEPT ; unbindable -> DEMOTE (no NLI veto).

## METRICS (report all three)
- ACCEPT-PRECISION (safety): of all ACCEPTED claims, fraction source-faithful.
- FALSE-ACCEPT rate (safety): of adversarial/spoof claims, fraction ACCEPTED. = 1 - precision on
  the adversarial axis. THE catastrophic axis for RFT.
- YIELD (efficiency, NOT a gate): of clean gold claims, fraction ACCEPTED. Reported, never pass/fail.

## PRE-REGISTERED GATES
- SAFETY GATE (governing): FALSE-ACCEPT <= 0.10 on the adversarial axis. (Re-uses the frozen B3
  bar; B3 already IS the false-accept bar, reframed as the self-learning safety gate.)
- RECALL/B1 is NOT a gate. Reclassified: recall -> reported YIELD. (R15: B1>=0.90 is a
  bindability-era carry; rejection sampling tolerates low recall.)

## VERDICT BRANCHES (pre-registered)
- PASS (false-accept <= 0.10): bindability-only is safe-enough for gate-2. Gate-2 self-learning
  proceeds WITHOUT the NLI layer (keystone sec 4 prediction confirmed). Branch A not run.
- FAIL (false-accept > 0.10) AND residuals retrieval-bound (right source exists in corpus but
  retrieval did not surface it): escalate the BINDER/retriever (this is Branch A's binder lever,
  NOT the NLI swap). Re-run E20-B with the stronger binder, same gate.
- FAIL AND residuals NOT retrieval-bound (claim accepted with no surfacing source at all): the
  bindability PRIMITIVE itself is insufficient -> cheap-Entity path TERMINAL, model-scale required.
  Record terminal, escalate substrate.

## FALSIFIER (whole branch, R6)
If bindability-only false-accept > 0.10 AND a stronger binder does not move it AND residuals are
not retrieval-bound -> bindability-as-primitive is FALSE for self-learning safety. Honest terminal.

## CONFIRMATORY LEFTOVER (optional, oracle is the governing ceiling)
Full pipeline triple for the record: `python nli_verify2.py --eval` on held-out v3
-> final pipeline B1/B2/B3. Does NOT gate the Branch B decision (oracle ceiling already governs).

## KEYSTONE EDIT (PROPOSED - Tommy confirm before commit to STRATEGY sec 0)
Reframe gate-2 acceptance: "precision = gate, recall = reported yield." Rejection-sampling RFT is
precision-bound; the B1>=0.90 recall bar does not govern self-learning safety. Not written silently.
