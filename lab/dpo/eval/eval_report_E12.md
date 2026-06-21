# ONTO Experiment #1 - Held-out v1.3 Eval Report

- heldout: `data\heldout_v1.3.jsonl`
- outputs: `eval\outputs_E12.json`
- arms scored: A, B, C, D

## Per-arm summary

| Arm | core composite | R1 | R2 | R3 | R4 | R5 | R6 | R7 | bait fab-rate (auto) | bait manual-flag | negctrl over-app |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | 2.43 | 0.12 | 0.23 | 0.05 | 0.07 | 0.03 | 0.00 | 0.87 | 25.00% | 75.00% | 12.50% |
| **B** | 4.78 | 0.00 | 0.41 | 0.45 | 0.21 | 0.40 | 1.00 | 0.90 | 0.00% | 37.50% | 37.50% |
| **C** | 4.49 | 0.25 | 0.51 | 0.23 | 0.30 | 0.38 | 0.35 | 0.91 | 0.00% | 37.50% | 0.00% |
| **D** | 5.67 | 0.34 | 0.55 | 0.36 | 0.36 | 0.54 | 0.88 | 0.90 | 0.00% | 12.50% | 0.00% |

## GO / NO-GO verdict (pre-registered)

### **VERDICT: GO**

### GO criteria (all must pass):

| Check | Result | Value vs threshold |
|---|---|---|
| composite(C) >= composite(B) - 1.0 | ✅ | 4.485 vs 3.7750000000000004 |
| R7(C) >= 0.85 * R7(B) | ✅ | 0.91 vs 0.768 |
| composite(C) >= composite(A) + 2.0 | ✅ | 4.485 vs 4.43 |
| bait_fab(C) <= bait_fab(B) + 0.10 | ✅ | 0.0 vs 0.1 |
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