# S2B RATE v01 -- first automated rate of the live substrate (DIAGNOSTIC)
Date: 2026-06-15. n = 30 raw {claim, doi, star_quote} proposals from the frozen 7B substrate,
run end to end through the FROZEN automated pipeline: gate veto (resolve + retracted, HARD)
-> s2b supports-judge (B1 binding deterministic -> B2 supports, separate non-proposing model).
No human, no `expect`. NO PASS/FAIL bar (SPEC sec9): this sizes a rate, it does not gate.

## Disposition (automated)

| bucket | this run (automated) | (ll) Claude-fetch-free |
|---|---|---|
| HARD_REJECT (gate veto) | 11 | 11 |
| NOT (judge wrong-binding) | 8 | 11 |
| UNCLEAR = HELD (safe) | 11 | 8 |
| SUPPORTS = ABSORBED | 0 | 0 |

HARD_REJECT breakdown: no_resolve 11.

## Honest-citation rate

ABSORBED / n = 0 / 30 = 0.000.

## Reading (R7, honest)

DIAGNOSTIC measurement, not a freeze-gate -- no number is relabeled to look better. The (ll)
baseline column was marked by a separate non-proposing Claude instance fetch-free (recall-
assisted, an honest gap) ; THIS run is the SAME gate + an automated retrieval-grounded judge.
Agreement sizes the automated judge's reliability ; disagreement is informative, not a fail.
The judge holds the safety property by construction: UNCLEAR routes to HELD (never absorbed),
so a thin/absent abstract or an unseparable binding fails safe rather than minting a citation.
