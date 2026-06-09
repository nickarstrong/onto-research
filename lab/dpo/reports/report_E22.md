# report_E22 -- model-scale NLI support-gate, SAME E20-B gate (frozen, no-train probe)

- lever          : facebook/bart-large-mnli -- P(entailment), premise=source / hypothesis=claim (claim-SUPPORT, not topicality)
- vs E21         : E21 used ms-marco relevance (topicality) -> FAIL_NO_MOVEMENT. E22 single new var vs NLI line = SCALE.
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 493b8ada955edd89c0f169609a121887 (E18) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## decorrelation guard (falsifiability)
- spearman(support,cosine) rho = 0.126 over 139 authorized pairs (VOID if >= 0.95)

## baseline sanity (no support-gate, T=-inf) -- model-independent, must reproduce E20-B
- B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (E20-B 0.467) reproduced=True

## threshold rule (frozen: highest T with B2>=0.90; peek only recall)
- chosen T = 0.0006890006479807198 | B2 at op-point = 0.9

## gate (frozen E20-B: false-accept <= 0.10 == B1 >= 0.90)
- B1 spoof-demotion = 0.6666666666666666
- false-accept      = 0.33333333333333337
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.13366666666666666

## VERDICT : FAIL_PARTIAL_MOVEMENT

decision (probe-first fork, Tommy-authorized): PASS -> model-scale entailment SEPARATES support from topicality where small-NLI (E18/E19) could not -> substrate-floor WAS the bottleneck -> PRE_REGISTER model-scale gate-2 regime (real GPU + model-scale data) | FAIL_NO_MOVEMENT / FAIL_PARTIAL_MOVEMENT -> even a model-scale entailment representation cannot separate at iso-recall -> reject-organ failure is ARCHITECTURAL, not scale -> NORTH STAR reframe (ACCEPT/REJECT as separate organs; non-retrieval reject primitive) | FAIL_RECALL_UNUSABLE -> support-gate destroys gold recall | VOID_* -> rebuild before any conclusion.
