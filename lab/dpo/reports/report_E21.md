# report_E21 -- cross-encoder binder-escalation, SAME E20-B gate (frozen)

- lever          : cross-encoder/ms-marco-MiniLM-L-6-v2 (NLI-free), pre-authorize rerank-filter on retrieved candidates
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 493b8ada955edd89c0f169609a121887 (E18) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37 (v3)
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## decorrelation guard (falsifiability)
- spearman(rerank,cosine) rho = 0.528 over 139 authorized pairs (VOID if >= 0.95)

## baseline sanity (no rerank, T=-inf) -- must reproduce E20-B
- B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (E20-B 0.467) reproduced=True

## threshold rule (frozen: highest T with B2>=0.90; peek only recall)
- chosen T = -9.872098922729492 | B2 at op-point = 0.9

## gate (frozen E20-B: false-accept <= 0.10 == B1 >= 0.90)
- B1 spoof-demotion = 0.5333333333333333
- false-accept      = 0.4666666666666667
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.00033333333333335213

## VERDICT : FAIL_NO_MOVEMENT

decision (PRE_REGISTER_E21 sec6): PASS->reranker becomes gate-2 selector, design RFT loop |
FAIL_NO_MOVEMENT->R6 confirmed, bindability insufficient, TERMINAL cheap-Entity, escalate substrate |
FAIL_PARTIAL_MOVEMENT->lever right, substrate-bound, escalate substrate |
FAIL_RECALL_UNUSABLE->reranker destroys recall | VOID_*->rebuild before any conclusion.
