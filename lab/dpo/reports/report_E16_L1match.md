# report_E16_turnstile -- L1/L2 PROVENANCE TURNSTILE (v97)
SPEC : SPEC_provenance_verifier_v1 (b62aad2f...) sec2 L1/L2, sec3 tiers, sec4 gate.
organ: verify_E16_L4.py (544c9a7b...) UNTOUCHED -- turnstile is a PRE-STAGE in front.
L1=resolve(+match dormant) ; L2=crossmark retraction(+RWD coverage gap owned).

| id | doi | L1 | L2 | expect | verdict | pass |
|----|-----|----|----|--------|---------|------|
| match_clean | 10.1186/1745-6150-2-15 | resolve+match(jaccard=1.00) | clean(crossmark; RWD=crossref-integrated only -- coverage gap owned) | PASS-TO-L4 | PASS-TO-L4 | Y |
| match_misattrib | 10.1073/pnas.0811124106 | metadata-mismatch(jaccard=0.08 < 0.50) | n/a(gated) | REJECT-L1 | REJECT-L1 | Y |

RESULT: 2/2 -> PASS

PASS criterion (pack v97 sec3): clean-source -> PASS-TO-L4 AND unresolvable -> REJECT-L1 AND retracted -> REJECT-L2.
FAIL = clean source rejected (false provenance veto) OR bad source passed (gate leak) -> diagnose turnstile, do NOT patch the frozen L4 organ.
