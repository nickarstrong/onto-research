# ONTO LOOP v0.1 -- off-plant disposition (rate-level, public-safe)

date  : 2026-06-15
setup : a frozen base model PROPOSES {claim, source-id}; an EXTERNAL gate resolves the source and
        checks retraction; whatever resolves is routed to a separate non-proposing supports-judge.
        The proposer is never trusted to judge its own citation. n=30, single draw.

## disposition
    proposed                       30   100.0%
    gate hard-reject (no-resolve)  11    36.7%   (caught automatically, no judge)
    judge-reject (wrong binding)   11    36.7%   (source real but is not what the claim cites)
    unclear (not groundable)        8    26.7%
    absorbed                        0     0.0%

## finding
The cheap external existence/retraction check caught 36.7% of defective citations with no
judge input. Every remaining proposal that resolved was either a wrong-binding (a real source that
is not the one cited) or not groundable without reading the source -- a class the existence check
cannot detect. Honest-citation rate this draw was zero. The external check is necessary but not
sufficient; the load-bearing instrument is an automated INDEPENDENT supports-judge. Single off-plant
draw, not a generalized rate; no source identifiers published (measurement-integrity).
