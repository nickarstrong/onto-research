# report_E38 -- corpus-vs-construction disambiguator |S|-distribution readout + branch verdict

- pre-register   : PRE_REGISTER_E38.md (FROZEN md5 15095413f7047074f75bc052cd81cf71) -- sec6 fork UNCHANGED
- parent         : E37 SET_EXHAUSTED [FALSIFIER], 88489f8 (set-veto fa_op 0.0333 best-on-ladder, bf-band FLAT at all P)
- probe          : run_E38_Sdist_probe.py md5 c91993fef02c6ab0c98bac3f0a5061e8 (PAIRING-RECONCILED v84; supersedes v83 design probe d6d5661b)
- inputs (gated) : heldout_E17.jsonl 7e9fe030646d5671952e7a9fe9437e37 | gold_fixture_E25b.json 4a45f52883a802e8d8d1d5ff5d185bdb | run_E37_probe.py 15e694a6690a70b801431d64c0b5c368
- model load     : NLI NOT loaded (binding/resolution only). cosine retrieval embedder (semantic_retrieve) loaded -- required to reproduce E37's bound set. no-GPU, no pod.

## pairing reconcile (sanctioned by the v83 probe header; FORK sec6 NOT touched)
- R1 (VOID-by-construction averted, E23/E15 class): the v83 frozen probe assumed heldout/fixture carry a per-item
  `candidates` list and called bind(claim,cands). FALSE -- heldout items are {text,class,id}; fixture is
  {records,manifest} (NOT keyed by id). The v83 fallback yields [] for EVERY item -> |S|=0 everywhere -> a FAKE
  A_CONSTRUCTION_CEILING. Caught PRE-DATA. The reconciled probe REPLAYS E37's resolution via E37's own imported
  callables (v.segment/classify/gate, candidates_with_cosine, store.is_authorized) -> byte-identical by construction.
- R2 (|S| definition corrected): |S| = AUTHORIZED COSINE-retrieved candidate set per asserting claim (the set
  con_share=n_con/|S| divides by). "floor 0.45, top_k 5" are the COSINE retrieval params (sem.FLOOR/TOP_K), NOT a
  lexical-binding floor.
- R3 (sec0 "no model" -> "no NLI model"): cosine embedder required; NLI head never loaded.

## |S| distribution (per asserting claim; CLASS-BLIND compute, class joined for reporting only)
- fixture records = 217 | heldout items = 75 | asserting authorized claims = 42
- overall  : p10=1 p50=3 p90=5 max=5 min=1 n=42  share[|S|<=1]=0.1667
- gold     : p10=1 p50=3 p90=5 max=5 min=1 n=28  share[|S|<=1]=0.2143
- spoof    : p10=2 p50=4 p90=5 max=5 min=1 n=14  share[|S|<=1]=0.0714
- negctrl  : n=0 (common-knowledge class never binds an authorized source -> demotes via noauth path, not the veto)
- per-item bound set dumped -> reports/E37_boundset.json (future byte-exact P=0 anchor)

## regression anchor (PRE_REGISTER sec5)
- mode = by-construction (E38 imports + calls E37's resolution callables; origin asserted == run_E37_probe.py)
- cross-check: 42 asserting claims x mean |S| ~= 3.3 == E37 n_prem 139 authorized candidates (report_E37 from_finding=109/139).
  The reconciled replay reproduces E37's candidate resolution total -> anchor upheld.
- empty-pass guards (E23): n_asserting=42>0 AND gold asserting claims>0 -> PASS (not VOID-by-construction).

## VERDICT : B_STATISTIC_WRONG
- trigger (frozen sec6): p50(|S|) >= 3 (overall 3 ; gold 3 ; spoof 4) AND share[|S|<=1]=0.167 < 0.50.
- meaning: a real multi-source bound SET exists per claim (p50 3-4, max=5). E37's set-veto cannot lift the bf-band
  NOT because there is no set to consense over (branch A FALSIFIED) but because consensus-share over the bound
  subset is the WRONG cross-source statistic.
- corroboration: this is consistent with E37 SET_EXHAUSTED -- spoofs are richly multi-bound (spoof p50|S|=4,
  share<=1 0.07) so con_share is high for them, while gold claims carry mixed-con sets (E37: 44/74 gold finding
  candidates cross con) -> a SCALAR consensus-share threshold cannot separate gold-tail (lone misbound contradictor
  among corroborators) from spoof (set-consensus contradiction). The set structure is real; the statistic is wrong.

## decision (PRE_REGISTER_E38 sec6, branch B -- operative)
- next rung (v85): design an ALTERNATIVE cross-source statistic over the EXISTING bound set -- NOT consensus-share
  over the same bound subset. Do NOT build a new corpus; the multi-source set is already present (branch A's corpus
  build is NOT triggered).
- candidate directions for v85 design (NOT decided here; design-time, pre-register required):
  * net-consensus / contradiction-dominance: (n_con - n_ent)/|S| or sign(n_con - n_ent) -- exploits the gold-vs-spoof
    ENTAIL asymmetry the scalar con_share discards (gold has a bound entailer; spoof has none -- E35 mechanism).
  * corroboration-core test: does the set contain a high-entail authorized core (gold) vs a contradiction-only set (spoof).
  * lone-contradictor isolation: is the contradiction concentrated in 1 misbound candidate vs distributed across the set.
- one statistic, pre-registered, with a P=0/degenerate anchor back to E37 con_share, swept oracle-clean (recall-only peek).

## R15 note (provenance honesty)
- The in-session aggregate lean toward branch A (from report_E37 "spoof 35" read as full |S|) was FALSIFIED by the
  full |S| replay: 35 was the FINDING-premise subset, not the authorized set. Running the honest probe (rather than
  accepting the offered "A accepted, skip confirmation") prevented an unnecessary GOLD-corpus pivot. Sunk cost = 0.
