# STANDARD -- Grounded Provenance Verifier v1 (FROZEN standard artifact)

status   : v1 FROZEN. Write-down of the graduated verifier. No bar here may be relitigated.
date     : 2026-06-17
plane    : s4 FREEZE VERIFIER (verifier line dies clean, R14). The verifier is the INSTRUMENT the
           autonomous-entity front (NORTH STAR) is built against -- not relitigated downstream.
home     : onto-research/reports (dateable priority + reproducibility). PUBLIC-SAFE.
sourcing : every number below is bracketed to its on-disk gate/report (R7). No memory figures.
exclude  : held-out truth labels, held-out DOIs, abstracts, bait-sets, weights, corpora, GOLD
           are LOCAL-ONLY (3.2) and NOT reproduced here. Numbers (rates/bars) are publishable; the
           substrate that produced them is not.

--------------------------------------------------------------------------------
## 0 CLAIM

An external, grounded provenance verifier gates every citation emission through an ordered chain --
extract claim -> resolve + status-check the source -> content-bind by contradiction-veto ->
independence-corroborate -> assign tier -- such that a fabricated, non-resolving, retracted, or
wrong-bound citation does not enter the knowledge record, with the binding judgment EXTERNAL to the
generating model's weights (hence tier-independent). Discipline is enforced outside the substrate;
the substrate proposes, the verifier disposes.

This is NOT a truth oracle. A bound, supporting source can still be wrong; that residual is L5's
ceiling, not the binder's. The organ asserts that the claim-source binding holds or is contradicted.

--------------------------------------------------------------------------------
## 1 ARCHITECTURE (two orthogonal axes + the cross-source statistic)

    (claim)            -> A-channel self-check (pre-emission flag)
    (claim, source-DOI) -> axis P: provenance lane  L1 existence -> L2 status (resolve/retraction)
                        -> axis G: content-bind     L4 contradiction-veto over the bound subset S
                        -> L5 independence corroboration (lifts ceiling)
                        -> tier T4..T0

GATE-BEFORE-MODEL: a T4 provenance verdict means the NLI organ NEVER runs -- the model cannot rescue
a failed marker.

--------------------------------------------------------------------------------
## 2 COMPONENT: A-CHANNEL SELF-CHECK (G3 self-consistency)

spec   : SPEC_selfcheck_A.md (FROZEN) ; impl verify_E16_A.py (md5 ea9d688b)
set    : labeled_A.jsonl (Founder-labeled, LOCAL-ONLY) -- 20 dirty + 20 clean
FROZEN bars:
  - C1 false_flag_rate <= 0.10   (HARD)
  - R1 detect_rate     >= 0.60   (TARGET)
RECORDED result (v1, n=20+20) [report_selfcheck_A_eval_v1.md]:
  - false_flag = 0.000 (0/20 clean)   -> C1 point-PASS
  - detect     = 0.900 (18/20 dirty)  -> R1 PASS ; Wilson 95% CI ~ [0.70, 0.97]
  - per-check fires A1=5 A2=5 A3=5 A4=4 (each >=1) ; selftest 4/4 POS + 5/5 NEG -> not VOID
DISCLOSED CEILING:
  - false_flag 95% upper ~0.15 STILL EXCEEDS the 0.10 HARD bar. Met on the point estimate, NOT
    CI-guaranteed. CI-clear needs ~30 clean @ 0 FP (rule of three). Reported as-is, not relabeled.
  - coverage = 4 gating checks (A1-A4), not full R1-R18 ; detect is a floor, not a ceiling claim.

--------------------------------------------------------------------------------
## 3 COMPONENT: B-CHANNEL L1/L2 -- EXISTENCE + STATUS TURNSTILE

impl   : run_provenance_L1L2.py ; report_provenance_L1L2.md
RECORDED result: 5/5 PASS (0 fail). RWD index = 59011 retracted DOIs (Retraction Watch CSV,
  OriginalPaperDOI x RetractionNature=Retraction).
  reject paths exercised: T4_L1_MISMATCH (resolves to wrong paper) ; T4_RETRACTED ; clean L1L2_PASS.
  L2 dual-signal [D1]: publisher RETRACTED title-flag (primary) + RWD index (augment).
DISCLOSED:
  - L2 coverage gap OWNED (dual-signal mitigates, does not close).
  - L1L2_PASS is provenance-clean, NOT gold: L4 bind / L5 / G-floor still gate.

--------------------------------------------------------------------------------
## 4 COMPONENT: B-CHANNEL L4 -- CONTENT-BIND CONTRADICTION-VETO (the graduated organ)

spec   : SPEC_verifier_v1.md (FROZEN, md5 f7433706) ; rule reused by import from run_E39_probe.py
         (md5 c2b908e5) -> zero divergence, wiring follows the frozen rule.
ORGAN (frozen, verbatim): over the representative bound-subset S of source sentences,
    n_con = count(NLI == contradiction) ; n_ent = count(NLI == entailment)
    D_lambda = (n_con - n_ent) / |S|        ; lambda frozen = 1.0
    reject iff ( pre_demoted OR D_lambda >= 0.67 )    ; tau frozen = 0.67
  pre_demoted = upstream noauth / grade-fail reject arm (does NOT depend on the NLI statistic).
  model = MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli ; contradiction idx read from
  id2label, NEVER hardcoded.
FROZEN bars:
  - fa_op <= 0.10 (max-based GATE false-accept, never p50 separation)
  - rho(D_lambda, upstream_bind) VOID threshold >= 0.95 one-sided (else organ is a retrieval proxy)
RECORDED result (full-GOLD E25b, 217 rec) [SPEC_verifier_v1 sec3 ; report_provenance_L4 ; E42scale]:
  - fa_op   = 0.0333  (<= 0.10 gate)
  - recall  = 0.9000  (27/30 structural golds)
  - auth-only fa = 0.0714 (anchor decomposition)
  - rho = -0.5481 (n=37) NEGATIVE -> INDEPENDENT (measures consensus, not retrieval ; F1 RESOLVED)
DISCLOSED CEILING (F2 CAP_HOLDS):
  - recall cap 0.9000 is STRUCTURAL (== E40 == E41 == E42scale at full-GOLD), not small-sample.
    3 structural golds the con/ent statistic alone cannot recover: 2 via the noauth pre_demoted arm,
    1 pure-consensus (n_ent=0 -> D_lambda=1.0, no contradiction to read). Recovery = a different
    (noauth-channel) organ, OPTIONAL for v1.
  - the per-candidate / per-entailment-coverage organ class is EXHAUSTED (E25b fa~0.20 ceiling ;
    E37 SET_EXHAUSTED). v1 is the contradiction-veto that graduated PAST that ceiling.
  - the "bart-large-mnli" tile is STALE: bart fa 0.0667 is a CROSS-MODEL bar only; running model is
    DeBERTa.

--------------------------------------------------------------------------------
## 5 COMPONENT: B-CHANNEL L4 WIRING + LIVE INTAKE (step2 contract + step2b emitter)

step2 contract [report_provenance_L4.md]: provenance verdict -> pre_demoted -> organ -> tier.
  T4_* (non-resolve / mismatch / retracted) -> pre_demoted=True -> reject, no NLI -> T4
  L1L2_PASS -> pre_demoted=False -> organ runs D_lambda @ lambda=1.0:
    S_size==0        -> T1_BIND_UNCHECKED
    D_lambda >= 0.67 -> T1_BIND_CONTRADICTED
    D_lambda <  0.67 -> T0_ELIGIBLE
  G3 anchor reproduced byte-exact: fa_op 0.0333 / recall 0.9000 over the frozen E37 readout
  (E37_boundset.json md5 0101822c). Deterministic arithmetic -> reproducible across environments;
  mismatch = env/version drift -> STOP, not re-measure.
step2b live intake [report_step2b.md]: thin live adapter (run_step2b_intake.py md5 d93a64e3),
  reimplements no organ. Both SPEC sec3 arms PASS:
  - retracted DOI -> prov=T4_RETRACTED, nli_run=false, tier=T4 (gate-before-model PROVEN).
  - clean DOI + its gold claim -> organ fires, S_size=1, D_lambda=0.0 < 0.67, tier=T1 (anti-VOID).
  - anchor 0.0333 reproduced byte-identical under torch 2.10 + transformers 5.11 (G3 clean).
DISCLOSED: operating ceiling stays T1 until L5 (step3, D3) closes. Binding the claim against the
  cited DOI's OWN text is a different organ (new substrate) -> out of scope for v1.

--------------------------------------------------------------------------------
## 6 COMPONENT: B-CHANNEL L5 -- INDEPENDENCE CORROBORATION, PART I (lifts T1 -> T0)

spec   : SPEC_L5_independence_predicate.md ; predicate FROZEN (md5 b96bfb43) ;
         gate SPEC_L5_fixgate_v2 (md5 f61a4764) ; truth FROZEN (md5 ac4ef6fa, NOT relabeled).
FROZEN bars:
  - G1 HARD : P3-origin over_prune == 0
  - G2 HARD : per-class recall (author/inst/data/citation) == 1.0 AND discount_leak == 0
  - G3      : over_prune <= 0.10 AND balanced_accuracy >= 0.85
RECORDED result (Act-2, predicate b96bfb43) [L5_partI_known_limits_ledger.md]:
  - G1 HARD PASS (P3-origin over_prune = 0)
  - G2 HARD PASS (per-class recall = 1.0 ; discount_leak = 0 ; both real author couples fire)
  - G3 FAIL : over_prune = 3/11 = 0.2727 > 0.10 (balanced_accuracy 0.8636 >= 0.85 OK -> fail is
    over_prune only). PART I does NOT freeze-PASS -> frozen as DOCUMENTED-CEILING. Bar 0.10 UNMOVED.
DISCLOSED CEILING + STRUCTURAL CAUSE (R16):
  - residual = 3 over-couples: 1 courtesy cross-cite (via P4) + 2 real shared-peripheral-author
    couples (via P1). Held-out specifics LOCAL-ONLY (not reproduced).
  - structural cause: the author-coupling predicate reads an UNORDERED normalized author-name SET
    (no sequence, no rank, ORCID not read). The only signal separating the one real principal-author
    couple from the false peripheral couples is author RANK, which is absent from the frozen fetch
    layer -- every in-scope rule that drops the false couples also castrates the real one (G2).
  - PARKED (s3+, Founder-approval): gate-v3 author-rank enrichment (retain author sequence + ORCID;
    fire P1 only on principal-author overlap or >=2 shared). Predicts residual -> 1/11 = 0.0909 <=
    0.10. THIN margin: any non-courtesy couple breaches 0.10.
  - Decision A (Founder): publish with T-ceiling note ; PART II proceeds. PART I truth FROZEN, no
    relabel-to-pass.
NOTE (R15): the committed reports/report_L5_partI.md (over_prune 0.5, bal_acc 0.75) is the EARLIER
  pre-predicate-fix run-record. The authoritative PART I freeze value is the ledger's 0.2727.

--------------------------------------------------------------------------------
## 7 COMPONENT: s2b END-TO-END LOOP (one legible turn)

ledger : ledger_s2b_v0_public.md (2026-06-15, automated, CPU, B2 generation executed)
RECORDED result: VERDICT PASS. Four planted items, four correct dispositions, no human in the
  resolve / retraction / binding path:
  - fabricated citation  -> does not resolve            -> HARD_REJECT at resolve gate
  - retracted citation   -> flagged retracted           -> HARD_REJECT at retraction
  - wrong-binding         -> real source, not supported  -> REJECT at judge
  - clean citation       -> resolves and supports        -> ABSORBED
DISCLOSED BOUNDARY (stated, not hidden):
  - the wrong-binding item was rejected via an ABSTAIN verdict from the judge, not an affirmative
    contradiction. Safe either way (abstain routes to rejection), but an affirmative support/non-
    support separator is the next measurement, not a closed result.
  - a fabrication / wrong-binding RATE over a LIVE proposer on n>30 is NOT yet measured. This turn
    is a single planted draw.

--------------------------------------------------------------------------------
## 8 COMPONENT: E39 NET-CONSENSUS CROSS-SOURCE STATISTIC (PART II keystone leg)

pre-reg : PRE_REGISTER_E39.md (FROZEN v4 noauth-split, md5 95ca5dff) ; probe run_E39_probe.py
          (md5 c2b908e5) ; outputs E39_Dnet.json / gate_E39.log / report_E39.md ; committed c854bbb.
statistic: D_lambda = (n_con - lambda*n_ent) / |S| over the AUTH subset (reads the entailment
           asymmetry con_share discards). 60 records (30 gold / 30 spoof ; 18 pre_demoted).
FROZEN bars + fork: FA_GATE 0.10 ; B2_GATE 0.90 ; STATISTIC_LIFTS iff >=2 distinct op-points across
  >=2 distinct lambda (not a single C-point).
HARD anchors (sec4) [E39_Dnet.json / gate_E39.log]:
  (1) STRUCTURAL : D_0 == con_share exactly, every non-pre_demoted row (drift -> VOID).
  (2) COMPOSITE  : lambda=0 @ tau=0.67 over 30 spoofs = 16 noauth pre_demoted + 13 con-veto + 1
                   survive = 29 reject -> fa_op = 1/30 = 0.0333 (byte-exact PASS).
  (3) AUTH-ONLY  : exclude the 16 pre_demoted -> 14 auth spoofs, 13 con-veto -> fa = 0.0714. The
                   model-INDEPENDENT decomposition proof that the composite is real, not a pure-con
                   artifact (PASS).
RECORDED result [E39_Dnet.json / report_E39.md / gate_E39.log]:
  - VERDICT = STATISTIC_LIFTS ; band_pts = 2 / distinct lambda = 2 (lambda = 1.0, 2.0).
  - best_op : lambda=1.0, tau=0.67, fa_op=0.0333, B2=0.9000.
  - con_share baseline (lambda=0) tops out at B2 = 0.7667 at any tau and CANNOT reach the 0.90 gate.
    The n_ent term (lambda>0) lifts B2 to 0.90 while holding fa_op at 0.0333 = +13.3pp recall at
    constant false-accept.
DISCLOSED MARGIN:
  - B2 = EXACTLY 0.90, margin 0.0000. One gold flip (1/30) drops below the gate. The verdict LIFTS
    by the FROZEN fork definition (keys on lambda-distinctness, not margin); the zero-margin is
    DISCLOSED here, not hidden. A verifier that quantifies its own thin margin is the stronger
    published standard than a cosmetic claim of headroom.

--------------------------------------------------------------------------------
## 9 THE STANDARD NAMES ITS OWN LIMITS (R7 / R17 consolidation)

1. L5 PART I over_prune 0.2727 > 0.10 -- structural (unordered author-name set, no rank/ORCID).
   Documented-ceiling freeze; gate-v3 author-rank enrichment parked (predicts 0.0909).
2. E39 B2 = 0.90 with margin 0.0000 -- one gold flip falls below gate.
3. A-channel false_flag 95% CI upper ~0.15 > 0.10 HARD bar -- point-PASS only, not CI-guaranteed.
4. L4 recall cap 0.9000 STRUCTURAL -- 3 golds unrecoverable by the con/ent statistic alone.
5. s2b e2e loop -- wrong-binding caught via ABSTAIN, not affirmative contradiction; live-proposer
   fabrication/wrong-binding RATE on n>30 NOT yet measured (single planted draw).

--------------------------------------------------------------------------------
## 10 FALSIFIERS (carried; what would break the verifier)

L4 (SPEC_verifier_v1 sec5):
  F-a clean, provenance-clean source rejected (D_lambda>=0.67 with no real contradiction) -> fa past gate.
  F-b rho(D_lambda, upstream_bind) >= 0.95 on any re-emit -> retrieval proxy -> VOID.
  F-c anchor fa_op != 0.0333 (byte) on clean re-run with frozen fixture -> env/version drift -> STOP.
  F-d verdict over an empty spoof or empty gold set (G2 contents counter not asserted) -> VOID.
E39 (PRE_REGISTER_E39 sec7):
  anchor (2) miss (!=0.0333 @ 4dp over 30) ; auth-only != 0.0714 ; sec6 self-check mismatch on any
  item ; heldout/fixture md5 mismatch -> VOID, do not proceed.

--------------------------------------------------------------------------------
## 11 LADDER PROVENANCE (verdicts only; do not relitigate)

E37      SET_EXHAUSTED     88489f8   per-candidate / per-entailment class CLOSED
E39 v4   STATISTIC_LIFTS   c0d1989 / c854bbb   D_lambda; best_op lambda=1.0 tau=0.67 -> fa 0.0333
E40      FLOOR_BOUND       f15d4d6   region WIDE/STABLE |R|=86 -> GRADUATES; recall floor 0.9000
E41      DEBT_CHARACTERIZED 26dc4ce  2 noauth + 1 pure-consensus (ho n_ent=0 -> D=1.0)
v91      INTEGRATION       4bb389b   RHO_RECONCILE (one-sided 0.95; D_lambda vs upstream_bind axis)
E42scale PASS / CAP_HOLDS  2273545   full-GOLD: F1 rho=-0.5481 INDEPENDENT; F2 recall 0.9000 structural
L5 PART I DOC-CEILING (b96bfb43)     G1+G2 HARD PASS; G3 over_prune 0.2727 honest-FAIL; Decision A

--------------------------------------------------------------------------------
## 12 FREEZE MARKER

Grounded Provenance Verifier v1 = FROZEN. The verifier line dies clean (R14). It is the instrument
the autonomous-entity propose-side front (NORTH STAR properties 1-4 = functions of THIS verifier) is
built against, not relitigated. No bar in this artifact may be reopened without a new pre-registered
rung and a recorded falsifier outcome.
