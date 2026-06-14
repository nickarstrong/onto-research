# SCHEMA -- eval/_local/l5_coupling_truth.jsonl  (Founder-supplied; LOCAL ONLY; NOT git)

Validates FROZEN PART I (SPEC_L5_independence_predicate.md, md5 d83d7a71...). One JSON object per line.

## RECORD (one claim per line)
```json
{
  "claim_id": "C001",
  "claim": "short text of the claim C the sources back",
  "sources": [
    {"sid": "S1", "doi": "10.xxxx/...", "data_id": "GSE12345", "method_class": "rna-seq"},
    {"sid": "S2", "doi": "10.yyyy/...", "data_id": null,        "method_class": "mass-spec"}
  ],
  "coupling_truth": [
    {"a": "S1", "b": "S2", "label": "independent"}
  ]
}
```

## FIELDS
- `sid`          : claim-local source id (S1, S2, ...). Unique within the claim.
- `doi`          : REAL, Crossref-resolvable DOI. The validator fetches authors/affil/refs LIVE.
- `data_id`      : the DAS dataset/specimen/instrument-run id YOU read (e.g. accession). `null` if the
                   real publication has NO data-availability statement -> predicate FAIL-CLOSES (P3 treats
                   unknown DAS as coupled). Do NOT invent an id to dodge this (R7).
- `method_class` : modality tag (or null). ADVISORY ONLY -- never gates the verdict. Optional.
- `coupling_truth`: EVERY pairwise combination C(n,2) for the claim's sources. Missing pair = excluded.
- `label` in {independent, author, institution, data, citation}  -- GROUND-TRUTH coupling you verified.

## LABEL MEANING (ground-truth = how the two sources are ACTUALLY coupled)
- independent  : no shared author / institution / primary data / citation-derivation. Genuinely separate witness.
- author       : author-set overlap (-> predicate P1).
- institution  : affiliation-of-record overlap (-> P2).
- data         : same primary dataset/specimen/instrument-run (-> P3).
- citation     : one establishes its support for C by CITING the other, not independent re-derivation (-> P4/I.4).

## CONTENTS REQUIREMENTS (the validator --contents enforces; VOID if violated)
1. Every class in {independent, author, institution, data, citation} present >= 1 pair. Empty class = VOID STOP.
2. Every claim has >= 2 sources; every source has a DOI.
3. coupling_truth covers ALL C(n,2) pairs of the claim (count must match exactly).
4. R7: labels are ground-truth, NEVER fabricated to clear a bar. Honest mislabel risk > fake clean.

## VALIDATION INTENT (why each class matters to I.7)
- author/institution/data/citation pairs  -> measure COUPLING RECOVERY (balanced-acc >= 0.85).
- citation pairs                            -> also the DISCOUNT-LEAK==0 HARD bar (must collapse to one cluster).
- independent pairs                         -> measure OVER-PRUNE (<= 0.10 false-coupling).
Put enough independent pairs to make over-prune denominator meaningful (>= ~20 recommended) and >= 1 of
each coupled class is the floor -- more per class tightens recovery estimate.

## SIZE GUIDANCE (R1, not a frozen bar)
Min to run: 5 classes covered. Statistically honest: >= 20 independent pairs, >= 5 per coupled class.
Smaller = wider CI on each rate; report will run but the estimate is fragile (state it).
