# report_E25 -- content-premise separation readout (no new data), SAME E20-B gate (frozen)

- lever          : facebook/bart-large-mnli -- P(entailment), premise=source.FINDING (fallback source) / hypothesis=claim
- vs E22/E23     : same model+gate; premise content injected via raw-fixture side-map (GoldStore frozen). premises_from_finding=109/139
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E18) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## decorrelation guard (falsifiability)
- spearman(support,cosine) rho = 0.241 over 139 authorized pairs (VOID if >= 0.95)

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

## E25 diagnostics -- entailment score by (item-class, premise-kind)
- gold_backed                  premise=finding : n=74 mean=0.1876 p10=0.0002 p50=0.0079 p90=0.8239
- gold_backed                  premise=source  : n=14 mean=0.0094 p10=0.0007 p50=0.0020 p90=0.0154
- spoof_cuestripped_entitied   premise=finding : n=35 mean=0.0033 p10=0.0000 p50=0.0002 p90=0.0018
- spoof_cuestripped_entitied   premise=source  : n=16 mean=0.0016 p10=0.0000 p50=0.0002 p90=0.0014

## content-premise separation (chosen_T=0.00132, ~0 (pinned))
- gold-content  : n=74 mean=0.1876 p10=0.0002 p50=0.0079 p90=0.8239 | >=T: 54/74
- spoof-content : n=35 mean=0.0033 p10=0.0000 p50=0.0002 p90=0.0018 | >=T: 5/35
- gold-vs-spoof content p50 separation = 0.0077 (gold 0.0079 - spoof 0.0002)

## CORPUS GO-GATE (pre-registered, PRE_REGISTER_E25.md)
- sep > 0 with gold-content p50 clearly above spoof-content p50 -> full-content bind-corpus JUSTIFIED -> build E26 (author content + run same gate).
- gold-content p50 ALSO pinned ~0 (gain was spoof-rejection only) -> corpus alone insufficient -> PIVOT passage-NLI / contradiction-veto.
