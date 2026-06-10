# PRE_REGISTER_E32 -- MODEL-CLASS ESCALATION (frozen contract)

- experiment   : E32
- type         : TYPE A (design/author). This file is FROZEN before any data is seen.
- date         : 2026-06-10
- template     : PRE_REGISTER_E30.md (git 791a3d0)
- copy base    : run_E30_probe.py (git 5827095) -- run_E32 = copy + declared lever only
- supersedes   : nothing (E30/E31 closed; E32 opens the model-class family)
- runs at      : E33 (TYPE C supervised run). This session authors + freezes only.

## 0 QUESTION (deferred to E33)
Does a stronger, ANLI-hardened NLI cross-encoder push the scope=any false-accept
BELOW bart-large-mnli's frozen 0.0667 on the SAME frozen substrate, with binding
coverage held (B2 >= 0.90)? E31 proved candidate-scope is NOT the lever (top1 loses
the spoof rejections living in non-top1 candidates; fa monotone 0.0667->0.2333).
bart-large-mnli is therefore the PROVEN ceiling. The only remaining in-family lever
is NLI discriminative class -- tested here, not candidate geometry.

## 1 SUBSTRATE (frozen, byte-identical to E25b..E31; NOT edited)
- fixture   : gold_fixture_E25b.json   md5 4a45f52883a802e8d8d1d5ff5d185bdb  (operative, unchanged)
- heldout   : heldout_E17.jsonl        md5 7e9fe030646d5671952e7a9fe9437e37  (unchanged)
- LOCAL/gitignored. md5-gated at E33 run STEP 0 (not this session).

## 2 LEVER (single, declared; oracle-leak clean)
- LEVER      : NLI cross-encoder MODEL SWAP. Nothing else changes.
- FROM       : facebook/bart-large-mnli      (MNLI-only; MNLI-m/mm ~0.899; no ANLI training)
- TO         : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli
               - license MIT (web-grounded; no hard blocker)
               - foundation microsoft/deberta-v3-large (~304M backbone)
               - MNLI-m/mm 0.912/0.908 ; ANLI-all (r1+r2+r3) 0.702 (web-grounded)
               - trained on 885,242 NLI pairs (MNLI+FEVER+ANLI+LingNLI+WANLI)
               - loads via transformers AutoModelForSequenceClassification (NO sentence_transformers)
- ASSUMPTION (carrying, R1/R7): the escalation is DISCRIMINATIVE CLASS, not param count.
  deberta-v3-large (~304M) is FEWER params than bart-large-mnli (~407M). The lift is
  architecture (DeBERTa-v3 RTD + disentangled attention) + adversarial training (ANLI/WANLI).
  This SHARPENS falsifiability: an ANLI-hardened head that still cannot clear 0.0667 fires
  CEILING_NOT_MODEL_SCALE -- the task, not the model, is the constraint.
- env-overridable via ONTO_CE_MODEL (default = the model above).
- contradiction_idx READ FROM id2label (model-agnostic; ASSERTED at load, never hardcoded).

## 3 VETO CONFIG (E30 proven-best anchor; NOT top1)
- PRIMARY_SCOPE = "any"  (E30/E31: scope=any reproduced 0.0667 at bart; top1 lost it -> 0.2333).
  scope=any is the proven-best veto geometry. E32 holds it fixed and varies ONLY the model.
- NO grid / const / threshold edit vs run_E30. Veto C-constant, retrieval floor, all frozen.

## 4 METRICS (frozen; read GATE fa = max over candidates, NOT sep p50)
- fa_new   : scope=any false-accept under the new model (max-based; confound-immune).
- B2       : binding coverage, same metric the E30/E28 probe emits (unchanged definition).
- baseline : no-veto (C=+inf) false-accept. MODEL-INDEPENDENT invariant.
- E28_OP_FA = 0.0667 : bart-SPECIFIC. Under a NEW model this is the COMPARISON TARGET
  (the bar fa_new is read against), NOT a reproduce-assert / regression gate.

## 5 FORKS (pre-committed; chosen by fa_new + B2 + baseline-sanity)

### 5.0 BASELINE-SANITY (VOID guard, model-INDEPENDENT)
- REQUIRE no-veto fa == 0.467 under the new model.
  no-veto demote comes from the noauth path, NOT the NLI head -> swapping the head must NOT move it.
- fa != 0.467 -> VOID: the swap broke the noauth/baseline path, not the NLI head. Stop, fix wiring,
  re-run. No verdict is read from a VOID run.

### 5.1 ESCALATION_CONFIRMED
- CONDITION : fa_new < 0.0667 (STRICT)  AND  B2 >= 0.90.
- MEANING   : model discriminative scale WAS the ceiling.
- E33 NEXT  : graduate to robustness sweep + verifier-integration question
              (rho guard 0.95-vs-0.50 reconcile, entailment-lift -> S3 three-way, full-GOLD scale).
              REQUIRES EXPLICIT TOMMY GO before integration.

### 5.2 MODEL_HELPS_PARTIAL
- CONDITION : 0.0667 <= fa_new <= 0.10  AND  B2 >= 0.90.
- MEANING   : a bigger/harder model helps but does NOT clear the E28 op point.
- DECISION  : deeper model class vs task reformulation (decided at E33 readout, not pre-committed here).

### 5.3 CEILING_NOT_MODEL_SCALE
- CONDITION : fa_new > 0.10  OR  B2 < 0.90.
- MEANING   : the ceiling is task/data, not model scale. The contradiction-veto task itself
              is the constraint.
- ACTION    : EXIT the NLI-swap family. Reframe the reject task (out of model-escalation entirely).

## 6 ORACLE-LEAK CHECK
- The lever (CE_MODEL swap) conditions on NOTHING held-out: model identity is fixed a priori,
  not selected against the held-out test labels. CLEAN.
- scope=any, cosine, top-1 rank = OBSERVABLE (admissible). True-class label = NOT used. CLEAN.

## 7 PROBE CONTRACT (run_E32_probe.py, built this session, committed at E33)
- run_E32 = copy of run_E30_probe.py with ONLY:
    (a) PRIMARY_SCOPE = "any"            (read proven-best config, not top1)
    (b) CE_MODEL default -> the model in sec 2 (still ONTO_CE_MODEL-overridable)
    (c) E28_OP_FA 0.0667 repurposed: reproduce-assert -> COMPARISON target (printed, not asserted)
    (d) comments
- NO grid / const / threshold change. contradiction_idx still read from id2label (asserted).
- default --out = reports/report_E32.md  (NOT a frozen-report path; no clobber).
- DIFF-PROOF MANDATORY: git diff(run_E30, run_E32) shows ONLY (a)-(d) + threading + --out. Embedded in report_E32 at E33.
- py_compile OK, ASCII-only. On disk UNCOMMITTED after E32 -> commits at E33 paired with report_E32.

## 8 ENV (every run, asserted)
- semantic_retrieve floor 0.45 (env-override; substrate default 0.55) ; KMP_DUPLICATE_LIB_OK=TRUE ;
  pyarrow preload ; NEVER sentence_transformers ; md5 all inputs every run ; assert CUDA (no silent CPU).

## 9 DESIGN GATE (this session PASS criteria)
- [x] candidate model id web-grounded (real HF id + MIT license + has contradiction class), not recalled.
- [ ] PRE_REGISTER_E32 frozen with md5; forks cover baseline-sanity VOID + 3 escalation outcomes.  <- this file
- [ ] run_E32 built, py_compile OK, diff-proof vs run_E30 = ONLY scope/CE_MODEL/anchor-repurpose/comments.
- [ ] pre-register committed (single -m); probe on disk uncommitted.
