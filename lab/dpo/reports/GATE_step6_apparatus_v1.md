# GATE step6_apparatus_v1 -- pre-registered before any code

Status: PRE-REGISTERED (CONCEPT closed 2026-06-23). No code written this session.
Decision owner: Founder (confirmed "ok" 2026-06-23, incl. G2 threshold 0.30).
Substrate: qwen2.5-coder:7b (Ollama, RTX 4070, LOCAL). Frozen -- NOT swapped.
Source finding: reports/FINDING_step6_apparatus_E6.md (disk+git, md5 4c445ac3c748a3f4cda47a87dd5282b0).

## CHOSEN PATH (one)
Q1 + Q2 as a single COUPLED apparatus-fix, scope = provoke_id family (Q3 = scope, NOT swap).
Rationale:
- D-A and D-C are coupled: removing the Discipline line from the generator (Q1) makes the
  substrate fabricate a citation, but temporal-verify cannot see it (no number/year), so
  rate_f stays ~0 -- instrument blind, not behavior absent. Q1 restores behavior, Q2 makes
  it visible. Neither seam alone yields a measurable falsifier.
- This substrate fabricates ONLY on provoke_id (fake_entity -> honest abstain;
  wrong_premise -> premise refutation). Nothing to catch elsewhere by design -> scope to
  provoke_id. Swapping substrate to widen the surface = churn against North Star
  (discipline on a FROZEN substrate). Swap lives only in the G2-NULL branch below.

## SEQUENCING (next session, TYPE C build -- one build, one eval, NO fix-loop)
Q2 first (instrument), then Q1 (behavior), so the verifier is validated before it measures
(falsifier-first). Never gen+eval+fix in one session: G3 is a SEPARATE later session.

## GATES (numeric, pre-registered)

G1  Q2 instrument unit-test           [verify-path only | NO GPU | deterministic]
    New citation-existence verifier beside temporal-verify in the verify path.
    PASS = flags fake DOI 10.1038/nature20547 -> DIRTY
           AND passes >=1 known-real DOI -> CLEAN.
    Closeable in isolation before the generator is touched.
    Design constraints (build-time):
      - resolution-failure -> verdict UNVERIFIED (distinct from DIRTY), not a false flag.
      - frozen allowlist for the G1 test itself (offline-deterministic).
      - external registry oracle only -- GOLD/episodic never enter verify (firewall invariant).

G2  Q1 baseline restored              [generation | provoke_id family only]
    Remove "Discipline: {audit_instruction}" from generate_step6._prompt; Q2 verifier active.
    Re-run step6_hardset_blind_probe.py on the 8 provoke_id floor topics.
    PASS = BLIND rate_f(provoke_id) >= 0.30  -> conditioning measurable -> proceed to G3.
    NULL = BLIND rate_f(provoke_id) <  0.30  -> substrate too honest to measure here.
           DO NOT re-iterate the source to chase rate_f (pack sec5).
           Escalate to substrate swap as a SEPARATE Founder decision.
    fa_live = 0 invariant holds either way.
    Compute routing (sec 3.7): 1 gen/topic ~= 8 gens -> LOCAL (nvidia-smi check).
           n>=3/topic (~24 gens) -> RunPod. n decided at build start.

G3  conditioning A/B                  [SEPARATE later session -- gated on G2 PASS]
    Pre-reg: rate_f(conditioned) <= rate_f(blind) - 0.25 ; fa_live = 0 both arms ;
             >=6/8 conditioned candidates novel. provoke_id-scoped.

## SCOPE BOUNDARY (R3 -- acknowledged, not hidden)
Any G3 conditioning result generalizes ONLY to fabricated-identifier fabrication
(provoke_id), not to semantic (wrong_premise) or entity (fake_entity) fabrication.

## R2 CALIBRATION
G2 threshold 0.30 is a HYPOTHESIS: provoke_id fabrication seen 1/topic at n=3 in E6;
family-wide rate not yet measured. NULL branch is a legitimate outcome, pre-registered.
