# report_E20B - bindability-only gate-2 safety (NLI OFF) : NO-GO

date         : 2026-06-10
pre-register : PRE_REGISTER_E20.md (Branch B; no post-hoc bar edit)
substrate    : verify_E16.py (frozen, byte-identical) + gold_retrieve.py + semantic_retrieve.py
nli          : OFF (verify_E16 _eval_heldout path; nli_verify2 not used)
heldout      : eval/_local/heldout_E17.jsonl  md5 7e9fe030646d5671952e7a9fe9437e37 (v3 frozen)
fixture      : eval/_local/gold_fixture_E18.json md5 493b8ada955edd89c0f169609a121887
               (INJECTED via run_E20B.py; NOT the drifted default gold_fixture.json 732abc05)
env (locked) : ONTO_RETRIEVE_FLOOR=0.45 (E16-locked); TOPK=5; KMP_DUPLICATE_LIB_OK=TRUE
crosswalk    : safety-gate = B1>=0.90 (false-accept<=0.10); B2 = reported yield; B3 = over-refusal

## metrics (held-out v3, 75 items; spoof=30, gold=30, negctrl=15)
B1 spoof-demotion = 16/30 = 0.533   -> false-accept = 0.467
B2 gold-VERIFY    = 28/30 = 0.933   (reported yield)
B3 over-demotion  =  0/15 = 0.000   (reported over-refusal)

## verdict : FAIL (NO-GO)
Safety gate false-accept <= 0.10 MISSED at 0.467 (~4.7x bar).
Non-degenerate: B2=0.933 confirms retrieval alive -> FAIL is a real false-accept,
not a dead-retrieval artifact.

## residual diagnosis (14 false-accepts)
breakdown {VERIFIED:14, DEMOTE:16}. All 14 leaks VERIFIED, nclaims=1, zero PASS-COMMON.
Each false-accept = a cue-stripped+entitied spoof binding to a REAL authorized source
above floor 0.45. Residuals are retrieval-bound BY MECHANISM (a source surfaced for each).

## branch (pre-registered): retrieval-bound -> escalate BINDER, re-run E20-B same gate = E21.

## R6 hypothesis for E21 (falsifiable)
Leak = topical-bind != claim-support: spoof is paraphrastically near a real on-topic
authorized source; a stronger retriever surfaces the SAME source, predicted NOT to move
false-accept (E17/E19 bind-precision wall).
Falsifier: stronger binder drops false-accept <= 0.10 -> hypothesis wrong.
Otherwise + still source-surfacing -> primitive insufficient -> terminal, model-scale, reopen NORTH STAR.

## reproducibility
run_E20B.py (lab/dpo root) reproduces this exactly with the locked env above.
