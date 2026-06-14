# 00_INDEX.md -- lab\dpo script map (grounded from docstrings, not filenames)

generated : 2026-06-14  | scope: 86 root *.py (+ key .ps1)  | do NOT move files -- they import each other (see DEPENDENCIES).
rule      : this is a navigation map, not a reorg. Frozen organs are import-only and NEVER mutated; wrappers add, never edit.

================================================================================
## 1 - FROZEN SUBSTRATE (import-only, never mutated -- E40/step2b pattern)
verify_E16.py            base verifier: segmenter + resolve_claim (L1-L3 bind). substrate everything wraps.
verify_E16_A.py          A-CHANNEL self-consistency (A1-A4), no source/model/net. THE conscience core.
verify_E16_B.py          B-CHANNEL band-A eval harness: resolve_claim vs GOLD store. mirrors A._eval shape.
verify_E16_L4.py         L4 CONTRADICTED secondary pass; imports emit_E42scale + run_E37 byte-identical.
gold_retrieve.py         GoldStore: hit retrieve + is_authorized (sha256(source) in manifest AND locator!="").
semantic_retrieve.py     embedding-cosine retrieval backend (all-MiniLM-L6-v2). FLOOR read at import (0.45).
run_E37_probe.py         NLI substrate (DeBERTa-v3-large-mnli) + frozen op-point. imported by emit_E37/E42scale.
emit_E42scale_readout.py graduated full-GOLD emitter (D_lambda/reject math). reused byte-identical by L4 wiring.
scoring_engine.py        R1-R7 discipline scorer v5.1 (+ R17 C1-C8). canonical immutable name.
scoring_engine_v5_1.py   BYTE-IDENTICAL DUP of scoring_engine.py (same md5). flag: redundant, candidate to drop.

## 2 - CONSCIENCE FIXES (phase 2/3 ; wrap the A-channel)
verify_disp_audit.py     phase-2 disposition-audit organ: A1-A4 -> named cards. import-only over verify_E16_A.
splice_A1.py             fix(a) RULE A1_GROUND_OR_DECLARE (STANDING fix). wraps verify_E16_A; ground-or-declare, never mints.
tally_v2.py              organ-tally ruler: per-flag rate + per-genre A1 + R6 verdict. imports verify_E16_A.
g2_sourcediff.py         fix(b) ruler: deterministic source-token diff DPO-minus-base (no organ/GOLD).
patch_A2.py              one-shot surgical A2-lexicon tighten on verify_E16_A.py (in-place; rollback=git checkout).

## 3 - PROVENANCE VERIFIER LADDER (L1-L5 ; E16->E42 probes + wiring)
provenance_turnstile.py  L1/L2 turnstile (Crossref existence + retraction). gate-before-model.
run_provenance_L1L2.py   L1/L2 deterministic adapter (no model); selftest + live modes.
nli_verify.py            E18 claim-support: NLI entailment over bound finding. wraps verify_E16.resolve_claim.
nli_verify2.py           E19 CONTRADICTION-VETO over top-K authorized bind. extends nli_verify.
wire_provenance_L4.py    SPEC sec9 step2: turnstile -> frozen L4 organ. apply-rule reused from run_E39.
wire_tier.py             SPEC sec9 step4: tier assembly T0-T4 + G-floor. composes wire_provenance_L4.
run_step2b_intake.py     SPEC sec9 step2b: live (claim,DOI) -> organ readout -> frozen tier chain.
emit_E37_readout.py      6-field per-item readout (E39 noauth-split). imports run_E37 frozen.
run_E16_e2e.py           E16 end-to-end L1-L2-L4 pipe (turnstile + L4Bind).
run_E16_smoke.py         E16 L4 smoke over gold_corpus_live.
run_E20B.py              minimal E16 heldout eval over gold_fixture_E18.
run_E21..E40 probes      provenance/statistic ladder. ALL share: `import pyarrow` line-1 (Arrow-SEH dodge)
                         + ONTO_RETRIEVE_FLOOR=0.45 + frozen verify_E16/gold_retrieve/semantic_retrieve import.
                         run_E39_probe.py = net-consensus D_lambda; run_E40_probe.py imports run_E39 (region sweep).
                         run_E38_Sdist_probe.py = corpus-vs-construction disambiguator (pairing-reconciled v84).
run_L5_partI_validate.py L5 PART-I independence predicate vs Founder coupling truth-set (I.7 bars).
build_l5_truth.py        builds eval/_local/l5_coupling_truth.jsonl from a plain typed table.

## 4 - EXP#1 TRAINING LADDER (E3-E13 ; SFT then DPO)
onto_exp1_e3_sft.py      E3 SFT reflex LoRA + P5 refusal (Kaggle T4x2 notebook).
onto_exp1_e4_sft.py      E4 SFT + P5b guard + core rebalance (sft_reflex_323).
onto_exp1_e7_sft.py      E7 SFT + targeted guard density (sft_reflex_392).
onto_exp1_e8_sft.py      E8 SFT (sft_reflex_418). FLAG: header mojibake + title still says "E7" (cosmetic).
onto_e5_gen.py           E5 arm inference A/B/C/D -> outputs_E5 (+ leak gate arm C). arm A = the frozen-base path.
onto_eval.py             held-out v1.3 eval runner (core/bait/negctrl, pre-registered GO/NO-GO).
onto_eval_lora.py        small 5-item LoRA bench (smoke).
onto_dpo_train.py        DPO trainer. v2 fix(b): --adapter OPTIONAL (absent=fresh LoRA on frozen base, SPEC ceilings).
                         imports run_ordinary_window.format_example (byte-exact wrapper, no drift).
onto_e12_harvest.py      E12 on-policy negative harvest (sample adapter on fresh provoke prompts).
onto_e13_run.py          E13 integration driver (recipe steps 2-6, single pod entrypoint).
onto_e13_logit_gate.py   E13 (a) forced-locator LogitsProcessor (decoded-string-state, seam-proof).
onto_e13_vfab.py         E13 (b) learned fab-direction steering vector (HYPOTHESIS; local-only artifacts).
onto_e13_probe.py        E13 (d) linear probe candidate (must reproduce manual verdicts to earn a role).
onto_e13_sensors.py      E13 (c) preflight sensors. ABORT-ONLY, never GO/NO-GO.
onto_e15_harvest.py      E15 real harvest driver (31-bait through target model; generation only).
dual_pass_scan.py        tier-spoof instrument: regex floor PASS1 + manual-governing PASS2 worksheet.
manual_scan_E15.py       E15 manual-scan helper over worksheets.
probe_E16.py             E16 no-GPU GO/NO-GO probe (extraction-recall on prose spoofs; bar recall>=0.90).
marker_resolver.py       citation-intent marker channel: resolve verified locator / R4 abstain+demote.
prose_provenance_detector.py  SPEC STUB, UNVALIDATED (VALIDATED=False). candidate-assist only, never a verdict.
dump_E28_pairs.py        E29 provenance-recovery helper (retrieval-only replay; no NLI/verdict).

## 5 - DATA / PAIR BUILDERS (TYPE A)
build_e6_pairs.py        E6 anti-relocation DPO pairs (drop provoke_id, +52 hand-authored).
build_e7_pairs.py        E7 targeted SFT-guard pairs (premise-guard + disclaim-guard + anchor).
build_e8_pairs.py        E8 P7_anchor pairs (range-first + named real source + uncertainty; no fab locator).
gen_e4_data.py           E4 authored data (P5b guard + core rebalance + bait_v2_n32 held-out EVAL).
build_fixture_E17.py     E17 full-GOLD bind-fixture (reproduces E16 derivation at scale; DOIs verbatim).
build_fixture_E18.py     E18 ADDITIVE finding layer (never mutates source/locator/claim_key; sha256 frozen).
gold_adapter.py          E16 live-bind: GOLD literature module -> GoldStore corpus (deterministic, no model).
merge_and_pack.py        merge base SFT (reflex_323) + E7 G-pairs (schema-adaptive, abort on mismatch).
merge_and_pack_e8.py     merge reflex_392 + P7 pairs -> reflex_418 (asserts line count).

## 6 - GATES / LEAK CHECKS
gate_pairs.py            held-out v1.3 vs reflex pairs distinctive-phrase gate (CLI --heldout --reflex --out).
gate_e8.py               leak gate P7_anchor pairs vs eval sets (exact-substring + content-token>3).
gate_e9.py               E9 collision gate (distinctive bigram/trigram, base64-safe).

## 7 - WINDOW GEN / TRIM (frozen-base substrate for --audit)
run_ordinary_window.py   FROZEN harness: arm-A frozen base on ordinary prompts. fix(b): OPTIONAL --adapter (no merge).
trim_window.py           deterministic echo-loop trim (v114 method; LF-pinned md5-stable).

## 8 - SANITY / DIAGNOSTICS (NOT bars, R7)
sanity_E16.py            retriever instrument-sanity (floor sweep, over-bind==0 locks floor).
sanity_E17.py            full-GOLD scale sanity (+ density-vs-degradation falsifier).
sanity_E18.py            NLI claim-support sanity (+ tau lock from NN-swap precision).
diag_oracle_E18.py       NLI ceiling diagnostic (wrapped vs stripped hypothesis).
selftest_E16_L4.py       L4 SHIP-v1 integration drift guard (anchor fa_op==0.0333; RunPod CUDA).
emit_E42scale_readout.py (see sec1 -- also the scale readout producer)

## 9 - TIER-SPOOF HARNESS (E15)
tier_spoof_harness.py    orchestrator (resolve_markers -> worksheet -> manual -> score). does NOT call a model.
score_tier_spoof.py      tier-spoof AND-gate (refuses until manual_pass_complete; imports scoring_engine primitives).

## 10 - PACK / OPS
build_pack.ps1           session-pack assembler (fixed q: $fname vs [int]$N ; -Spec param ; md5 in STRUCTURE).
file_results.ps1 / pack_*.ps1 / MERGE_AND_PACK_E8.ps1   filing + runpod/eval packers.

================================================================================
## DEPENDENCIES (why nothing moves)
- verify_E16  <- verify_E16_A, verify_E16_B, verify_disp_audit, splice_A1, tally_v2, nli_verify, run_E20B..E40
- verify_E16_A <- verify_disp_audit, splice_A1, tally_v2     (import-only; organ never mutated)
- run_E37_probe <- emit_E37_readout, emit_E42scale_readout, run_step2b_intake
- emit_E42scale + run_E37 <- verify_E16_L4
- run_E39_probe <- run_E40_probe, wire_provenance_L4 (apply-rule reuse)
- wire_provenance_L4 <- wire_tier
- nli_verify <- nli_verify2
- run_ordinary_window.format_example <- onto_dpo_train  (byte-exact train/gate wrapper)
- gold_retrieve + semantic_retrieve <- verify_E16 (pulled transitively by every E2x/E3x probe)

## KNOWN FLAGS (cosmetic, deferred)
- scoring_engine.py == scoring_engine_v5_1.py (identical md5) -- redundant copy.
- onto_exp1_e8_sft.py header mojibake + stale "E7" title (builds sft_reflex_418).
- E2x/E3x probes carry an `import pyarrow` line-1 Arrow-SEH workaround (Win/Py3.12); benign.
