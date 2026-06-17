# PRIORITY STUB -- Grounded Provenance Verifier v1

purpose : dateable priority + reproducibility for the public record (onto-research). This stub does
          two things only (3.2): (1) establish "we developed exactly this, on this date"; (2) point
          to the scripts + frozen pre-registers + recorded verdicts that reproduce it.
date     : 2026-06-17
status   : v1 FROZEN. Full standard artifact: reports/STANDARD_grounded_verifier_v1.md.

EXCLUDED FROM PUBLIC (LOCAL-ONLY, 3.2): held-out truth labels, held-out DOIs, abstracts, bait-sets,
weights, corpora, GOLD. Only rates, bars, verdicts, md5s, commit hashes, and script names appear here.

--------------------------------------------------------------------------------
## CLAIM (dated)

As of 2026-06-17 we have a frozen, externally-grounded provenance verifier that gates citation
emission -- extract -> resolve+status -> contradiction-veto content-bind -> independence-corroborate
-> tier -- with the binding judgment external to the generating model (tier-independent). Fabricated,
non-resolving, retracted, and wrong-bound citations are rejected before entering the record. A
cross-source net-consensus statistic lifts recall to the gate at constant false-accept.

--------------------------------------------------------------------------------
## FROZEN PRE-REGISTERS + RECORDED VERDICTS

| component            | spec / pre-register (md5)                  | recorded verdict                     |
|----------------------|--------------------------------------------|--------------------------------------|
| A-channel self-check | SPEC_selfcheck_A.md (FROZEN)               | ff 0.000 / detect 0.900 (n=20+20)    |
| L1/L2 turnstile      | report_provenance_L1L2.md                  | 5/5 PASS ; RWD 59011 retracted       |
| L4 content-bind      | SPEC_verifier_v1.md (f7433706)             | fa_op 0.0333 / recall 0.9000         |
| L4 wiring + intake   | report_provenance_L4.md ; report_step2b.md | anchor byte-exact ; 2 arms PASS      |
| L5 PART I            | SPEC_L5_independence_predicate (b96bfb43)  | G1+G2 HARD PASS ; G3 over_prune 0.2727 (doc-ceiling) |
| s2b e2e loop         | ledger_s2b_v0_public.md                    | 4/4 dispositions PASS                |
| E39 net-consensus    | PRE_REGISTER_E39.md (95ca5dff)             | STATISTIC_LIFTS ; B2 0.90 @ fa 0.0333 |

--------------------------------------------------------------------------------
## REPRODUCIBILITY POINTERS (scripts; deterministic legs reproduce byte-exact)

  run_provenance_L1L2.py        L1 existence + L2 status (RWD index)
  wire_provenance_L4.py         provenance -> frozen L4 tier contract
  run_E39_probe.py (c2b908e5)   net-consensus D_lambda statistic + anchors
  run_step2b_intake.py (d93a64e3) live (claim, DOI) intake adapter
  verify_E16_A.py (ea9d688b)    A-channel self-check organ
  model: MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (contradiction idx from id2label)

Deterministic arithmetic legs (L4 wiring, E39) reproduce byte-identical across environments; the
0.0333 / 0.0714 anchors are the transformers-version drift guard. Mismatch = STOP (env drift), not
re-measure.

--------------------------------------------------------------------------------
## DISCLOSED LIMITS (named, not hidden)

- L5 PART I over_prune 0.2727 > 0.10 (structural: unordered author-name set, no rank/ORCID). Gate-v3
  author-rank enrichment parked (predicts 0.0909).
- E39 B2 = 0.90, margin 0.0000.
- A-channel false_flag 95% CI upper ~0.15 > 0.10 HARD bar (point-PASS only).
- L4 recall cap 0.9000 structural (3 golds).
- s2b loop: wrong-binding via abstain (not affirmative contradiction); live-proposer rate n>30 not
  yet measured.

provenance commit: E39 leg committed onto-research/main c854bbb (e19f8b9..c854bbb).
