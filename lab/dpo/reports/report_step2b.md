# report_step2b -- SPEC sec9 step2b (LIVE NLI intake wiring)

date    : 2026-06-12
plane   : RESEARCH / verifier-v1 BUILD
status  : PASS. Live intake path wired + proven. Pairs with run_step2b_intake.py (md5 d93a64e3b2d2e1081b309820acd48a2b, 171 lines).
home    : onto-research/reports (dateable priority + reproducibility)
frozen  : SPEC_verifier_v1.md (f7433706) ; SPEC_provenance_verifier_v1.md (b62aad2f). No frozen bar relitigated.

--------------------------------------------------------------------------------
## 0 WHAT step2b IS

The chain on disk consumed three integers (n_con, n_ent, S_size) but nothing produced them LIVE -- they came
only from the frozen E37 readout (offline). step2b is the emitter that produces them for a NEW (claim, source-DOI):

    (claim, DOI) -> L1/L2 gate-before-model -> [survivors] organ con/ent over the bound subset S
                 -> wire_provenance_L4.tier_of_live -> wire_tier.final_tier -> T0..T4

It is a THIN live adapter, not a new organ. Reimplements nothing.

--------------------------------------------------------------------------------
## 1 ARCHITECTURE (forced by the frozen organ, not a free choice)

The frozen L4 organ (run_E37_probe.precompute_item) binds a claim against the GOLD store (store.records +
manifest hash-gate), retrieving representative S by cosine, premise = source.finding, hyp = claim. It has NO
path to bind against an arbitrary external DOI's text. Therefore step2b's intake splits along the SPEC's two
orthogonal axes (SPEC_provenance sec1):
  - source-DOI rides the PROVENANCE lane (L1/L2 -> resolve / retraction)            ; axis P
  - L4 content-bind asks "does GOLD-consensus contradict this claim" over retrieved S ; axis G
Binding the claim against the cited DOI's own text would be a DIFFERENT organ (new substrate) -> out of scope
("wire to the FROZEN organ", SPEC sec9 step2). GATE-BEFORE-MODEL (SPEC sec4): a T4 provenance verdict means the
NLI is NEVER run -- the model cannot rescue a failed marker.

--------------------------------------------------------------------------------
## 2 FROZEN REUSE (no copy ; zero divergence)

    L1/L2 provenance : run_provenance_L1L2.verdict(doi, expected_title, fetch, rwd_index)
    organ con/ent    : run_E37_probe.precompute_item / _bound_subset / item_label_at_C / .gr / .sem
                       + emit_E37_readout.representative  (frozen op-point extractor)
    tier L4 + ladder : wire_provenance_L4.tier_of_live ; wire_tier.final_tier
    model            : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli ; contradiction_idx=2,
                       entailment_idx=0 read from id2label (never hardcoded)
    env-wart         : ONTO_RETRIEVE_FLOOR=0.45 set inside run_E37_probe BEFORE semantic_retrieve import
                       (default 0.55 = footgun). Honored by importing run_E37_probe first.

--------------------------------------------------------------------------------
## 3 NO-GPU SELFTEST (wiring contract ; real L1/L2 + real tier chain, organ mocked)

5/5 PASS. Exercises gate-before-model + the full tier chain ; both reject (T4) and accept-to-ceiling (T1)
reached -> not VOID-by-construction (E23 guard). Organ fidelity is NOT asserted here -- that is the GPU anchor.

--------------------------------------------------------------------------------
## 4 PRE-RUN GATE (local CPU/GPU ; GOLD fixture is LOCAL-ONLY, not shipped off-box)

deps    : torch 2.10.0+cu128 (cuda True) ; transformers 5.11.0 ; sentencepiece ; protobuf 7.35.1
fixtures: gold_fixture_E25b.json md5 4a45f52883a802e8d8d1d5ff5d185bdb ; heldout_E17.jsonl md5 7e9fe030646d5671952e7a9fe9437e37
rwd     : retraction_watch.csv 64,609,776 bytes (local)
note    : "Skipping cpp extensions (upgrade torch>=2.11)" warning is BENIGN -- python fallback path; the anchor
          reproduced byte-exact under this exact stack (sec5), so organ numerics are unaffected.

--------------------------------------------------------------------------------
## 5 ANCHOR GUARD (G3 ; version-drift -- transformers 5.x suspect -> RULED OUT)

emit_E37_readout.py re-emit over E25b (217 / 30 spoofs):
    spoofs=30 pre_demoted=16 con_veto=13 reject=29 -> fa_op=0.0333 (expect 0.0333)  PASS
    auth-only: auth_spoofs=14 con_veto=13          -> fa=0.0714 (expect 0.0714)     PASS
    sec6 reconcile: emit decision == E37 op label for all 30 spoof items            PASS
    E37_boundset.json md5 = 0101822c9402346b93e9a3154c6624fa == pre-run (BYTE-IDENTICAL)
=> transformers 5.11.0 did NOT drift the organ. G3 clean. The pre-run E37_boundset was backed up before re-emit.

--------------------------------------------------------------------------------
## 6 LIVE RUN (the two SPEC sec3 PASS arms)

ARM 1 -- retracted DOI (gate-before-model):
    claim = "Pluripotency of mesenchymal stem cells derived from adult marrow"
    doi   = 10.1038/nature00870 (Verfaillie, retracted 2024) ; grade rct
    ->  prov=T4_RETRACTED  nli_run=false  l4=T4  tier=T4
    L1 title match=1.0 (RETRACTED-prefix stripped) ; L2 retracted via BOTH title_flag + rwd (D1 dual-channel)
    NLI never ran -> gate-before-model proven.

ARM 2 -- clean DOI + its gold claim (organ fires):
    claim = ho_g00 "An origin-of-life probability calculation reported that a self-copying molecule forming by
            chance is astronomically unlikely, on the order of one in ten to the thousandth."
    doi   = 10.1186/1745-6150-2-15 (Koonin, Biology Direct 2007 ; clean) ; grade peer_reviewed
    title verified via PubMed/PMC primary source.
    ->  prov=L1L2_PASS  nli_run=true  n_con=1  n_ent=1  S_size=1  D_lambda=(1-1)/1=0.0 < 0.67 (bind holds)
        l4=T0_ELIGIBLE  tier=T1
    L1 match=1.0 ; L2 clean. S_size=1 > 0 -> organ FIRED on a known gold (anti-VOID satisfied).
    tier capped at T1 (operating ceiling D3: l5_corroborated stays False until step3).

--------------------------------------------------------------------------------
## 7 VERDICT

PASS. All four SPEC sec3 conditions met:
  (1) retracted/mismatch DOI -> T4, no NLI            [ARM 1]
  (2) clean bound source     -> T1 (ceiling)          [ARM 2]
  (3) anchor 0.0333 reproduced byte-identical          [sec5]
  (4) FAIL conditions absent: no anchor drift ; no empty-S-on-all (S=1 on the gold) [sec5/6]

step2b GRADUATES. Live intake wiring is on disk; verifier-v1 build steps remaining: step3 (L5 independence,
lifts ceiling T1->T0) ; step1/step2/step4 already DONE.

--------------------------------------------------------------------------------
## 8 FALSIFIERS (what would break step2b)

F-a : a clean-resolving DOI whose gold claim yields S_size=0 across all known golds -> organ not firing (VOID).
F-b : a retracted/non-resolving DOI where nli_run=true -> gate-before-model breached (model touched a failed marker).
F-c : anchor fa_op != 0.0333 on re-emit -> env/version drift (re-pin transformers), STOP.
F-d : tier_of_live / final_tier reachable only at one tier across the selftest -> path collapse (E23).
