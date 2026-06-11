# report_E40 -- robustness / feasible-region sweep

## sec0 contract
PRE_REGISTER_E40 v2 md5 3f0ae4eb386548ef566621862beee95f ; import-only from run_E39_probe (md5 e8a6fec9). no-GPU; frozen readout.

## sec1 anchors
best_op (lambda=1.0, tau=0.67): fa_op=0.0333 B2=0.9000 == 0.0333/0.9000 (byte-exact PASS)
lambda=0 spoof anchor (tau=0.67): reproduces 0.0333 (PASS)
noauth ceiling: max_B2_grid=0.9000 <= 0.9333 (PASS)

## sec5 region
|R|=86 ; lambda bbox [0.6..1.5] span=9 steps ; tau bbox [0.67..0.75] span=8 steps
B2 in R: [0.9000 .. 0.9000]

## sec6 verdict
K=12 span_min(lambda=2,tau=2) -> **FLOOR_BOUND**
