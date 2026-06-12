# report_provenance_L4 -- SPEC sec9 step2 (wire L1/L2 provenance -> frozen L4 content-bind organ)

VERDICT: PASS. Provenance->L4 tier contract validated; G3 anchor reproduced byte-exact.

## scope
step2 = the INTEGRATION CONTRACT between the provenance turnstile (step1, L1/L2) and the FROZEN
content-bind organ (SPEC_verifier_v1, md5 f7433706). The organ is NOT rebuilt: the apply rule is
REUSED by import from run_E39_probe.py (md5 e8a6fec9) -> if the frozen rule moves, the wiring follows;
zero divergence. No model, no GPU, no new design.

## contract (the only new logic)
provenance verdict (step1) -> pre_demoted -> organ -> SPEC tier:
- T4_* (non-resolve / mismatch / retracted) -> pre_demoted=True -> organ rejects (no NLI) -> T4
- L1L2_PASS -> pre_demoted=False -> organ runs D_lambda=(n_con-n_ent)/|S| @ lambda=1.0:
    - S_size==0          -> T1_BIND_UNCHECKED   (no candidates; bind not established)
    - D_lambda >= 0.67   -> T1_BIND_CONTRADICTED (clean source contradicts the claim)
    - D_lambda <  0.67   -> T0_ELIGIBLE          (bind holds)
T0_ELIGIBLE is NOT T0: L5 corroboration (step3) + G-floor (step4) still gate. Ceiling stays T1 until step3.

## G3 anchor (drift guard) -- reproduced
Over the frozen E37 readout (E37_boundset.json, md5 0101822c), evaluate(recs, lambda=1.0, tau=0.67):
- fa_op   = 0.0333   (== SPEC frozen; 1/30 structural false-accept = ho_sn06, empty-S non-pre_demoted)
- recall  = 0.9000   (27/30; 3 structural golds reject: ho_g12 D=1.0 pure-consensus, ho_g18/ho_g25 pre_demoted)
- gold_n 30 / spoof_n 30
Byte-exact match to the frozen organ (SPEC_verifier_v1 sec3/sec4). Deterministic arithmetic, no model
-> reproducible across environments. Mismatch would be env/version drift -> STOP (not re-measure).

## selftest (logic, mocked)
T4/T1_BIND_UNCHECKED/T1_BIND_CONTRADICTED/T0_ELIGIBLE all exercised; no path collapse (anti VOID-by-construction).

## NOT in step2 (flagged, not done)
- step2b LIVE INTAKE: for a NEW (claim, source-DOI), the NLI-emit path (retrieve representative S over the
  source + DeBERTa-v3-large-mnli -> n_con/n_ent, via emit_*_readout) is GPU-bound and NOT wired here.
  step2 wires the contract + validates against the frozen readout; step2b wires the live emitter.
- L5 (step3) and G-floor (step4) remain; operating ceiling = T1 until step3 (D3) closes.

## artifacts
- wire_provenance_L4.py (committed alongside this report). Reuses run_E39_probe.{evaluate,d_lambda,load_records}.
