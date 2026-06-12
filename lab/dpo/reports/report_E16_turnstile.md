# report_E16_turnstile -- L1/L2 PROVENANCE TURNSTILE (v97)
SPEC : SPEC_provenance_verifier_v1 (b62aad2f...) sec2 L1/L2, sec3 tiers, sec4 gate.
organ: verify_E16_L4.py (544c9a7b...) UNTOUCHED -- turnstile is a PRE-STAGE in front.
L1=resolve(+match dormant) ; L2=crossmark retraction(+RWD coverage gap owned).

| id | doi | L1 | L2 | expect | verdict | pass |
|----|-----|----|----|--------|---------|------|
| prov_clean | 10.1186/1745-6150-2-15 | resolve-only(no cited_title; match dormant) | clean(crossmark; RWD=crossref-integrated only -- coverage gap owned) | PASS-TO-L4 | PASS-TO-L4 | Y |
| prov_unresolvable | 10.9999/this-doi-does-not-exist-000 | non-resolve(status=404) | n/a(gated) | REJECT-L1 | REJECT-L1 | Y |
| prov_retracted_verfaillie | 10.1038/nature00870 | resolve-only(no cited_title; match dormant) | retracted[title-prefix,updated-by:retraction] | REJECT-L2 | REJECT-L2 | Y |
| prov_retracted_cheetah | 10.1073/pnas.0810435106 | resolve-only(no cited_title; match dormant) | retracted[title-prefix,updated-by:retraction] | REJECT-L2 | REJECT-L2 | Y |

RESULT: 4/4 -> PASS

PASS criterion (pack v97 sec3): clean-source -> PASS-TO-L4 AND unresolvable -> REJECT-L1 AND retracted -> REJECT-L2.
FAIL = clean source rejected (false provenance veto) OR bad source passed (gate leak) -> diagnose turnstile, do NOT patch the frozen L4 organ.
