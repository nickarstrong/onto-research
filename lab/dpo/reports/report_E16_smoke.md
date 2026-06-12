# report_E16_smoke -- E16 live-bind behavioural smoke

date   : 2026-06-12T02:46:57.751529+00:00
corpus : gold_corpus_live.json (34 files / 366 recs, G2 GREEN; LOCAL, GOLD-derived)
organ  : verify_E16_L4 FROZEN md5 544c9a7b8c3189943b010a642efc0d86 (import-only)
model  : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli (contradiction_idx=2)

## per-item (no claim text; GOLD-derived stays local)

| id | class | expect | got | L3 | n_con | n_ent | S | pre_demoted | pass |
|----|-------|--------|-----|----|-------|-------|---|-------------|------|
| sm_koonin_contra | smoke | CONTRADICTED | CONTRADICTED | yes | 3 | 0 | 3 | False | PASS |
| sm_koonin_clean | smoke | VERIFIED | VERIFIED | yes | 1 | 2 | 3 | False | PASS |
| sm_nasa_contra | smoke | CONTRADICTED | CONTRADICTED | yes | 5 | 0 | 5 | False | PASS |
| sm_nasa_clean | smoke | VERIFIED | VERIFIED | yes | 0 | 0 | 4 | False | PASS |

## gate
- contra->CONTRADICTED : 2 (need >=1)
- clean ->VERIFIED     : 2 (need >=1)
- all reach L3         : True
- all item asserts     : True

VERDICT : PASS
