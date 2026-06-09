# report_E26 -- contradiction-veto reject primitive (PIVOT), SAME frozen gate

- lever          : facebook/bart-large-mnli -- P(CONTRADICTION), premise=source.FINDING (fallback source) / hypothesis=claim
- pivot rationale: E25b falsified coverage; pure-entailment reject organ ceiling fa~0.20 > gate 0.10 (architectural).
                   E26 changes the SIGNAL not the data: veto a claim when an authorized premise CONTRADICTS it.
- premise content: from_finding=109/139 (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)
- floor (frozen) : 0.45 | top_k 5
- fixture md5    : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b) | heldout md5 : 7e9fe030646d5671952e7a9fe9437e37
- heldout classes: {'gold_backed': 30, 'spoof_cuestripped_entitied': 30, 'negctrl_common': 15}

## decorrelation guard (falsifiability)
- spearman(contradiction,cosine) rho = -0.237 over 139 authorized pairs (VOID if >= 0.95)

## baseline sanity (NO veto, C=+inf) -- model-independent, must reproduce no-veto fa 0.467
- B1=0.533 B2=0.933 B3=0.000 false-accept=0.467 (no-veto 0.467) reproduced=True

## iso-recall veto rule (frozen: LOWEST C with B2>=0.90; peek only recall)
- chosen C = 0.9949175119400024 | B2 at op-point = 0.9

## gate (frozen: false-accept <= 0.10 == B1 >= 0.90)
- B1 spoof-demotion = 0.9333333333333333
- false-accept      = 0.06666666666666665
- B2 yield          = 0.9
- B3 over-demotion  = 0.0 (bar <= 0.10)
- movement vs 0.467 = 0.4003333333333334

## VERDICT : PASS

decision (PRE_REGISTER_E26.md sec6, the ONLY operative fork -- ignore any stale E22-era boilerplate): PASS (fa<=0.10 at B2>=0.90) -> contradiction-veto IS the reject primitive -> integrate + full gate + 3 secondaries | FAIL_PARTIAL_VETO (0.10<fa<0.20) -> tune veto threshold/direction, ONE more readout, no new data | FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT (fa>=0.20) -> contradiction signal ALSO insufficient -> FALLBACK branch: passage-NLI (Tommy go for passage authoring) OR ACCEPT/REJECT as separate organs (NORTH STAR reframe) | FAIL_RECALL_UNUSABLE -> veto destroys gold recall | VOID_* -> rebuild before any conclusion.

## E26 diagnostics -- CONTRADICTION score by (item-class, premise-kind)
- gold_backed                  premise=finding : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793
- gold_backed                  premise=source  : n=14 mean=0.3259 p10=0.0110 p50=0.1098 p90=0.9096
- spoof_cuestripped_entitied   premise=finding : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998
- spoof_cuestripped_entitied   premise=source  : n=16 mean=0.7737 p10=0.1500 p50=0.9889 p90=0.9984

## contradiction separation (chosen_C=0.99492; veto when contradiction >= C)
- gold-content  (want LOW)  : n=74 mean=0.3306 p10=0.0001 p50=0.0377 p90=0.9793 | vetoed(>=C, false): 1/74
- spoof-content (want HIGH) : n=35 mean=0.7323 p10=0.0275 p50=0.9909 p90=0.9998 | vetoed(>=C, true): 14/35
- spoof-vs-gold content p50 separation = 0.9532 (spoof 0.9909 - gold 0.0377)
- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;
  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).
