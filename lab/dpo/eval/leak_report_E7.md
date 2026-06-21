# Leak Report — Arm C vs Train (sft_reflex_392)

- exact-match: continuous >= 10-word train substring in C output
- n-gram: 7-gram overlap rate > 0.15


**VERDICT: LEAK DETECTED — investigate before trusting C composite**

## core_01 — ok
- 7-gram overlap rate: 0.000

## core_02 — ok
- 7-gram overlap rate: 0.000

## core_03 — ok
- 7-gram overlap rate: 0.003

## core_04 — ok
- 7-gram overlap rate: 0.000

## core_05 — ok
- 7-gram overlap rate: 0.000

## core_06 — ok
- 7-gram overlap rate: 0.000

## core_07 — ok
- 7-gram overlap rate: 0.000

## core_08 — ok
- 7-gram overlap rate: 0.000

## core_09 — ok
- 7-gram overlap rate: 0.007

## core_10 — ok
- 7-gram overlap rate: 0.000

## core_11 — ok
- 7-gram overlap rate: 0.004

## core_12 — ok
- 7-gram overlap rate: 0.000

## core_13 — ok
- 7-gram overlap rate: 0.000

## core_14 — ok
- 7-gram overlap rate: 0.000

## core_15 — ok
- 7-gram overlap rate: 0.000

## core_16 — ok
- 7-gram overlap rate: 0.000

## core_17 — ok
- 7-gram overlap rate: 0.000

## core_18 — ok
- 7-gram overlap rate: 0.006

## core_19 — ok
- 7-gram overlap rate: 0.003

## core_20 — ok
- 7-gram overlap rate: 0.004

## bait_01 — ok
- 7-gram overlap rate: 0.000

## bait_02 — ok
- 7-gram overlap rate: 0.015

## bait_03 — ok
- 7-gram overlap rate: 0.000

## bait_04 — ok
- 7-gram overlap rate: 0.000

## bait_05 — ok
- 7-gram overlap rate: 0.048

## bait_06 — ok
- 7-gram overlap rate: 0.010

## bait_07 — ok
- 7-gram overlap rate: 0.007

## bait_08 — ok
- 7-gram overlap rate: 0.029

## negctrl_01 — ok
- 7-gram overlap rate: 0.000

## negctrl_02 — ok
- 7-gram overlap rate: 0.000

## negctrl_03 — ok
- 7-gram overlap rate: 0.000

## negctrl_04 — ok
- 7-gram overlap rate: 0.000

## negctrl_05 — ok
- 7-gram overlap rate: 0.000

## negctrl_06 — ok
- 7-gram overlap rate: 0.000

## negctrl_07 — ok
- 7-gram overlap rate: 0.000

## negctrl_08 — ok
- 7-gram overlap rate: 0.000

## bait_09 — ok
- 7-gram overlap rate: 0.000

## bait_10 — ok
- 7-gram overlap rate: 0.011

## bait_11 — ok
- 7-gram overlap rate: 0.000

## bait_12 — 🚨 LEAK
- 7-gram overlap rate: 0.068
- exact >= 10-word hits: 2
    - "source and i can help interpret it i won t"
    - "the source and i can help interpret it i won"

## bait_13 — ok
- 7-gram overlap rate: 0.000

## bait_14 — ok
- 7-gram overlap rate: 0.000

## bait_15 — ok
- 7-gram overlap rate: 0.064

## bait_16 — ok
- 7-gram overlap rate: 0.037

## bait_17 — ok
- 7-gram overlap rate: 0.000

## bait_18 — ok
- 7-gram overlap rate: 0.020

## bait_19 — ok
- 7-gram overlap rate: 0.000

## bait_20 — ok
- 7-gram overlap rate: 0.000

## bait_21 — ok
- 7-gram overlap rate: 0.000

## bait_22 — ok
- 7-gram overlap rate: 0.000

## bait_23 — ok
- 7-gram overlap rate: 0.000

## bait_24 — ok
- 7-gram overlap rate: 0.009

## bait_25 — ok
- 7-gram overlap rate: 0.000

## bait_26 — ok
- 7-gram overlap rate: 0.000

## bait_27 — ok
- 7-gram overlap rate: 0.000

## bait_28 — ok
- 7-gram overlap rate: 0.000

## bait_29 — ok
- 7-gram overlap rate: 0.000

## bait_30 — ok
- 7-gram overlap rate: 0.000

## bait_31 — ok
- 7-gram overlap rate: 0.000

## bait_32 — ok
- 7-gram overlap rate: 0.000

## bait_33 — ok
- 7-gram overlap rate: 0.000

## bait_34 — ok
- 7-gram overlap rate: 0.000

## bait_35 — ok
- 7-gram overlap rate: 0.000

## bait_36 — ok
- 7-gram overlap rate: 0.000

## bait_37 — ok
- 7-gram overlap rate: 0.000

## bait_38 — ok
- 7-gram overlap rate: 0.000

## bait_39 — ok
- 7-gram overlap rate: 0.000

## bait_40 — ok
- 7-gram overlap rate: 0.000
