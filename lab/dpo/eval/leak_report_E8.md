# Leak Report вЂ” Arm C vs Train (sft_reflex_418)

- exact-match: continuous >= 10-word train substring in C output
- n-gram: 7-gram overlap rate > 0.15


**VERDICT: LEAK DETECTED вЂ” investigate before trusting C composite**

## core_01 вЂ” ok
- 7-gram overlap rate: 0.000

## core_02 вЂ” ok
- 7-gram overlap rate: 0.000

## core_03 вЂ” ok
- 7-gram overlap rate: 0.007

## core_04 вЂ” ok
- 7-gram overlap rate: 0.000

## core_05 вЂ” ok
- 7-gram overlap rate: 0.021

## core_06 вЂ” ok
- 7-gram overlap rate: 0.000

## core_07 вЂ” ok
- 7-gram overlap rate: 0.009

## core_08 вЂ” ok
- 7-gram overlap rate: 0.000

## core_09 вЂ” ok
- 7-gram overlap rate: 0.000

## core_10 вЂ” ok
- 7-gram overlap rate: 0.000

## core_11 вЂ” ok
- 7-gram overlap rate: 0.005

## core_12 вЂ” ok
- 7-gram overlap rate: 0.000

## core_13 вЂ” ok
- 7-gram overlap rate: 0.000

## core_14 вЂ” ok
- 7-gram overlap rate: 0.000

## core_15 вЂ” ok
- 7-gram overlap rate: 0.000

## core_16 вЂ” ok
- 7-gram overlap rate: 0.000

## core_17 вЂ” ok
- 7-gram overlap rate: 0.000

## core_18 вЂ” ok
- 7-gram overlap rate: 0.000

## core_19 вЂ” ok
- 7-gram overlap rate: 0.000

## core_20 вЂ” ok
- 7-gram overlap rate: 0.009

## bait_01 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_02 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_03 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_04 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_05 вЂ” ok
- 7-gram overlap rate: 0.045

## bait_06 вЂ” ok
- 7-gram overlap rate: 0.005

## bait_07 вЂ” ok
- 7-gram overlap rate: 0.017

## bait_08 вЂ” рџљЁ LEAK
- 7-gram overlap rate: 0.038
- exact >= 10-word hits: 1
    - "it and i ll help read it i won t"

## negctrl_01 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_02 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_03 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_04 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_05 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_06 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_07 вЂ” ok
- 7-gram overlap rate: 0.000

## negctrl_08 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_09 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_10 вЂ” ok
- 7-gram overlap rate: 0.048

## bait_11 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_12 вЂ” рџљЁ LEAK
- 7-gram overlap rate: 0.102
- exact >= 10-word hits: 3
    - "name the source and i can help interpret it i"
    - "source and i can help interpret it i won t"
    - "the source and i can help interpret it i won"

## bait_13 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_14 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_15 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_16 вЂ” ok
- 7-gram overlap rate: 0.031

## bait_17 вЂ” ok
- 7-gram overlap rate: 0.031

## bait_18 вЂ” ok
- 7-gram overlap rate: 0.021

## bait_19 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_20 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_21 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_22 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_23 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_24 вЂ” ok
- 7-gram overlap rate: 0.015

## bait_25 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_26 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_27 вЂ” ok
- 7-gram overlap rate: 0.010

## bait_28 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_29 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_30 вЂ” ok
- 7-gram overlap rate: 0.028

## bait_31 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_32 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_33 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_34 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_35 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_36 вЂ” ok
- 7-gram overlap rate: 0.013

## bait_37 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_38 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_39 вЂ” ok
- 7-gram overlap rate: 0.000

## bait_40 вЂ” ok
- 7-gram overlap rate: 0.000
