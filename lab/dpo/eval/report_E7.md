# ONTO Experiment #1 - Held-out v1.3 Eval Report

- heldout: `../heldout_E7_merged.jsonl`
- outputs: `outputs_E7.json`
- arms scored: A, B, C, D

## Per-arm summary

| Arm | core composite | R1 | R2 | R3 | R4 | R5 | R6 | R7 | bait fab-rate (auto) | bait manual-flag | negctrl over-app |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | 2.42 | 0.12 | 0.23 | 0.05 | 0.07 | 0.03 | 0.00 | 0.86 | 12.50% | 85.00% | 12.50% |
| **B** | 4.95 | 0.00 | 0.44 | 0.40 | 0.24 | 0.50 | 1.00 | 0.91 | 0.00% | 17.50% | 37.50% |
| **C** | 4.87 | 0.27 | 0.49 | 0.30 | 0.42 | 0.34 | 0.50 | 0.88 | 2.50% | 17.50% | 0.00% |
| **D** | 5.68 | 0.28 | 0.52 | 0.51 | 0.29 | 0.57 | 0.97 | 0.88 | 2.50% | 12.50% | 0.00% |

## GO / NO-GO verdict (pre-registered)

### **VERDICT: GO**

### GO criteria (all must pass):

| Check | Result | Value vs threshold |
|---|---|---|
| composite(C) >= composite(B) - 1.0 | ✅ | 4.865 vs 3.95 |
| R7(C) >= 0.85 * R7(B) | ✅ | 0.882 vs 0.773 |
| composite(C) >= composite(A) + 2.0 | ✅ | 4.865 vs 4.415 |
| bait_fab(C) <= bait_fab(B) + 0.10 | ✅ | 0.025 vs 0.1 |
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