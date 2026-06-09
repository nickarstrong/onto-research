# report_E24 -- NLI support-gate over CONTENT premise (raw-fixture side-map), SAME E20-B gate (frozen)

- lever          : facebook/bart-large-mnli -- P(entailment), premise=source.FINDING (fallback source) / hypothesis=claim
- vs E22/E23     : same model+gate; premise content injected via raw-fixture side-map (GoldStore frozen). premises_from_finding=51/139
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 493b8ada955edd89c0f169609a121887 (E18) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## decorrelation guard (falsifiability)
- spearman(support,cosine) rho = 0.202 over 139 authorized pairs (VOID if >= 0.95)

## baseline sanity (no support-gate, T=-inf) -- model-independent, must reproduce E20-B
- B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (E20-B 0.467) reproduced=True

## threshold rule (frozen: highest T with B2>=0.90; peek only recall)
- chosen T = 0.001319460105150938 | B2 at op-point = 0.9

## gate (frozen E20-B: false-accept <= 0.10 == B1 >= 0.90)
- B1 spoof-demotion = 0.8
- false-accept      = 0.19999999999999996
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.26700000000000007

## VERDICT : FAIL_PARTIAL_MOVEMENT

decision (probe-first fork, Tommy-authorized): PASS -> the E16-E21 wall was PREMISE-IMPOVERISHMENT (entailment judged against citation strings, not content); fix = content-binding (GOLD as bind-corpus, pack sec4) -- NOT scale, NOT architecture | FAIL_PARTIAL_MOVEMENT / FAIL_NO_MOVEMENT -> even content-premise model-scale entailment cannot separate the cue-stripped+entitied spoofs at iso-recall -> reject-organ failure is ARCHITECTURAL -> NORTH STAR reframe (ACCEPT/REJECT as separate organs; non-retrieval reject primitive) | FAIL_RECALL_UNUSABLE -> gate destroys gold recall | VOID_* -> rebuild before any conclusion.
