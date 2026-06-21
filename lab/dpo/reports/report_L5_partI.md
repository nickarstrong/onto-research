# report_L5_partI -- PART I independence predicate validation

VERDICT: FAIL

## I.7 bars
- recovery>=0.85: FAIL
- discount_leak==0(HARD): PASS
- over_prune<=0.10: FAIL

## metrics
- balanced_accuracy : 0.75 (tpr 1.0 / tnr 0.5)
- citation_discount_leak : 0 (HARD==0)
- over_prune : 0.5 (8/16 indep pairs)
- confusion : {'tp': 13, 'tn': 8, 'fp': 8, 'fn': 0}
- per_class_recall : {'independent': 0.5, 'author': 1.0, 'institution': 1.0, 'data': 1.0, 'citation': 1.0}
- per_class_n : {'independent': 16, 'author': 2, 'data': 5, 'citation': 5, 'institution': 1}
- method leg (ADVISORY, kappa N/A single-annotator) agree_rate : 0.5172
- excluded : []

## per-pair readout (READ-ONLY ; re-applies frozen pair_predict, does NOT gate)
| claim | pair | declared | verdict | legs | data_id |
|---|---|---|---|---|---|
| C001 | S1xS2 | independent | independent | - | [None, None] |
| C002 | S1xS2 | independent | coupled | P4 | [None, None] |
| C003 | S1xS2 | independent | independent | - | [None, None] |
| C003 | S1xS3 | independent | independent | - | [None, None] |
| C003 | S2xS3 | independent | coupled | P4 | [None, None] |
| C004 | S1xS2 | author | coupled | P1,P4 | [None, None] |
| C004 | S1xS3 | independent | coupled | P4 | [None, None] |
| C004 | S1xS4 | independent | coupled | P1 | [None, None] |
| C004 | S2xS3 | independent | coupled | P1,P4 | [None, None] |
| C004 | S2xS4 | independent | coupled | P1,P4 | [None, None] |
| C004 | S3xS4 | independent | coupled | P1 | [None, None] |
| C005 | S1xS2 | independent | independent | - | [None, None] |
| C006 | S1xS2 | data | coupled | P3 | ['TCGA-BRCA', 'TCGA-BRCA'] |
| C007 | S1xS2 | citation | coupled | P4 | [None, None] |
| C008 | S1xS2 | institution | coupled | P1,P4 | [None, 'TCGA-BRCA'] |
| C009 | S1xS2 | independent | independent | - | ['PXD000561', 'ProteomicsDB'] |
| C010 | S1xS2 | data | coupled | P3 | ['phs000424.v8.p2', 'phs000424.v8.p2'] |
| C011 | S1xS2 | data | coupled | P3 | ['phs000424.v8.p2', 'phs000424.v8.p2'] |
| C012 | S1xS2 | data | coupled | P3 | ['phs000424.v8.p2', 'phs000424.v8.p2'] |
| C013 | S1xS2 | data | coupled | P3 | ['phs000424.v8.p2', 'phs000424.v8.p2'] |
| C014 | S1xS2 | independent | coupled | P4 | ['MN908947', 'EPI_ISL_402124'] |
| C014 | S1xS3 | independent | independent | - | ['MN908947', 'MN985325'] |
| C014 | S2xS3 | independent | independent | - | ['EPI_ISL_402124', 'MN985325'] |
| C015 | S1xS2 | citation | coupled | P4 | ['6VSB', '6VXX'] |
| C015 | S1xS3 | citation | coupled | P4 | ['6VSB', '6M17'] |
| C015 | S1xS4 | author | coupled | P1,P4 | ['6VSB', '6CRZ'] |
| C015 | S2xS3 | independent | independent | - | ['6VXX', '6M17'] |
| C015 | S2xS4 | citation | coupled | P4 | ['6VXX', '6CRZ'] |
| C015 | S3xS4 | citation | coupled | P4 | ['6M17', '6CRZ'] |

## independent sub-group split (gate substrate for the predicate FIX)
- accession-bearing : 1/5 false-coupled ; ids ['S1xS2', 'S1xS2', 'S1xS3', 'S2xS3', 'S2xS3']
- accession-less    : 7/11 false-coupled ; ids ['S1xS2', 'S1xS2', 'S1xS2', 'S1xS3', 'S2xS3', 'S1xS3', 'S1xS4', 'S2xS3', 'S2xS4', 'S3xS4', 'S1xS2']

## WATCH (frozen-predicate interactions, reported not edited)
- P3 fail-closed on missing DAS can inflate over-prune on real no-DAS independents -> if
  over_prune FAIL traces to P3 fail-closed, that is a legit FALSIFY(over-prune): file DEFECT + v1.1, do NOT edit frozen.
- citation leg has no reference-context (APIs give edges not context) -> any basis-citation
  edge treated as collapse (conservative; safe for leak==0, adds over-prune risk).
- method leg ADVISORY by default (I.3); excluded from gating verdict.
