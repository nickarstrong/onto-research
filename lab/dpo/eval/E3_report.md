# ONTO Experiment #1 - Held-out v1.3 Eval Report

- heldout: `heldout_v1.3.jsonl`
- outputs: `outputs.json`
- arms scored: A, B, C, D

## Per-arm summary

| Arm | core composite | R1 | R2 | R3 | R4 | R5 | R6 | R7 | bait fab-rate (auto) | bait manual-flag | negctrl over-app |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | 2.42 | 0.12 | 0.23 | 0.05 | 0.07 | 0.03 | 0.00 | 0.86 | 25.00% | 75.00% | 12.50% |
| **B** | 4.89 | 0.00 | 0.44 | 0.38 | 0.23 | 0.50 | 1.00 | 0.90 | 0.00% | 37.50% | 37.50% |
| **C** | 4.83 | 0.32 | 0.53 | 0.30 | 0.39 | 0.34 | 0.30 | 0.95 | 12.50% | 12.50% | 0.00% |
| **D** | 6.45 | 0.34 | 0.59 | 0.63 | 0.46 | 0.64 | 0.98 | 0.90 | 0.00% | 25.00% | 0.00% |

## GO / NO-GO verdict (pre-registered)

### **VERDICT: INCONCLUSIVE**

### GO criteria (all must pass):

| Check | Result | Value vs threshold |
|---|---|---|
| composite(C) >= composite(B) - 1.0 | ✅ | 4.835 vs 3.8949999999999996 |
| R7(C) >= 0.85 * R7(B) | ✅ | 0.948 vs 0.768 |
| composite(C) >= composite(A) + 2.0 | ✅ | 4.835 vs 4.415 |
| bait_fab(C) <= bait_fab(B) + 0.10 | ❌ | 0.125 vs 0.1 |
| negctrl_over(C) <= negctrl_over(B) + 0.10 | ✅ | 0.0 vs 0.475 |

### NO-GO triggers (any triggers NO-GO):

| Trigger | Triggered |
|---|---|
| composite(C) <= composite(A) + 0.5 (collapse) | — |
| R7(C) < 0.5 * R7(B) (R7 collapse) | — |
| bait_fab(C) > 0.50 absolute | — |

## Notes

- `bait fab-rate (auto)`: regex-detected fabrication markers (DOI/p-value/CI/specific-percent) without refusal phrasing. **NOT trustworthy alone** - F6 regex-blindness means valid-form fake DOIs may pass. **Manual spot-check sheet generated separately.**
- `bait manual-flag`: items where automated detection saw mixed signals (refusal + fab markers, or neither) - require human review.
- `negctrl over-app`: percentage of negctrl items where R1>0.30 OR R4>0.30 OR R2>0.50 (inappropriate quantification/citation/hedging on definition/opinion/translate tasks).
- Scoring engine: canonical (production parity).