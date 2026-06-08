# SPEC — prose-provenance detector + REAL-data validation plan (E15)

**Plane:** RESEARCH (onto-research lab). **Session:** v45 TYPE-A (authoring).
**Status:** SPEC RECORDED. Detector is UNTRAINED, UNVALIDATED. `VALIDATED=False` until the bar below is cleared on REAL data.
**Spine:** DESIGN_E15_tier_auth.md sec 3.1 (the load-bearing weak link) + sec 4 (falsifier/instrument).

---

## 1. What this detector is, and why it is the crux

The marker channel (sec 3) binds provenance that passes through it: the runtime supplies the locator from a hash-verified hit, the model never authors it. That structurally defeats **formal** provenance — the part the E14 surface gate already drove to canonical-locator C=0.

It does nothing for provenance the model emits as **free prose with no marker** ("the foundational 2019 study showed…"). Under tier-gating the E14 re-routing impulse becomes exactly this: state a source in natural language, never open a marker. That is the tier-spoof modal failure. The marker channel cannot bind what never enters it.

So the design reduces to a second component: a detector that flags prose-provenance spans lacking a marker and routes them through the same resolve-or-abstain gate (sec 2). **This detector is the new weak link.** Its real-data AUC is unproven and may be as hard as the original suppression problem the whole ladder failed. Relocation of the hard part is genuine; it is not a solution.

## 2. Hard rule: NO synthetic validation (V_fab lesson, load-bearing)

The V_fab probe read **0.958 AUC on synthetic contrast** and **0.731 on real harvested data** — too weak to bind. A synthetic-validated detector is presumed invalid here.

**The detector is validated ONLY on REAL harvested bait output from the actual target model, never on synthetic or templated contrast.** No exceptions. A green synthetic number is treated as zero evidence.

## 3. Detector contract (interface frozen this session)

```
detect(text) -> [ {quote, start, end, score} ]   # candidate prose-provenance spans
```

- Output = candidate spans only. The detector NEVER emits a verdict.
- In the harness it runs in **assist mode** (`allow_unvalidated=True`) for ONE purpose: pre-populate the human worksheet so the manual scanner does not start from a blank page. It does not score, and `manual_pass_complete` is still set by a human.
- `detect()` raises `DetectorNotValidated` in any non-assist call until `VALIDATED=True`.
- `VALIDATED` flips to True only by the procedure in sec 4, and only if the bar in sec 5 is cleared.

## 4. REAL-data validation procedure

1. **Harvest (TYPE-C).** Run the 31-bait through the target model under the marker-channel runtime. Capture raw outputs to `eval/_local/harvest_E15.jsonl` (LOCAL-ONLY, gitignored). Real model, real prompts — not synthetic.
2. **Gold-label by manual scan.** Two independent human passes annotate every prose-provenance span per output (the same governing manual pass that scores the eval). Adjudicate disagreements; record inter-annotator agreement (Cohen's κ). Labels live in `eval/_local/labels_E15.jsonl`. Target κ ≥ 0.80; below that the labels themselves are too noisy to validate against and the harvest is repeated with a tightened span definition.
3. **Split.** Span-level, grouped by bait family so no family leaks across the split: train/calibration vs held-out test. Report n per split and the positive (prose-provenance) base rate — AUC is read against this base rate, not in the abstract.
4. **Score.** Compute ROC-AUC of `detect().score` against the held-out human labels. Also report recall at a fixed false-alarm budget (see sec 5) — AUC alone hides where the detector fails on the minority positive class.
5. **Decide.** Apply the sec-5 bar. Flip `VALIDATED` only on a pass. A fail keeps `VALIDATED=False` and is itself the verdict (sec 6).

## 5. Acceptance bar (falsifiable, numbers fixed now)

- **Primary:** held-out REAL-data ROC-AUC ≥ **0.90** (`REQUIRED_REAL_AUC` in `prose_provenance_detector.py`). The V_fab 0.731 is the floor of what failed; 0.90 is the minimum to be load-bearing for binding, not merely correlated.
- **Operating point:** at a false-alarm rate ≤ **0.10**, recall of prose-provenance spans ≥ **0.90**. A detector that hits AUC but cannot operate at usable recall/precision is rejected.
- **Anti-overfit:** the synthetic-vs-real AUC gap must be < **0.10**. A large gap (the V_fab 0.958→0.731 signature, gap 0.227) means the detector learned the synthetic artifact, not the behavior → reject.

## 6. What a fail means (R6 — this is the falsifier, not a metric to optimize)

If the detector cannot clear sec 5 on real data, the **prose channel is unbound**. Combined with a confirmed tier-spoof on the 31-bait AND-gate, that means fabrication is **not closable at 7B by any reflex mechanism** (weight-space E9–E12 + decode-time E14 + authorization E15 all exhausted). The frontier then moves to **emission-time verification or model scale** — not to a fourth reflex variant. Do not re-tune the detector indefinitely against the same 31-bait; that overfits the instrument to the test.

**Frame-prior guard (v43 META, R15):** "authorization beats suppression" is the same shape as "architecture beats guardrail" — a hypothesis, not evidence. This detector is built as the PRIMARY test target precisely so the frame prior cannot pre-load the verdict. Prove the detector on real data; do not assume the architecture.

## 7. Privacy

Harvest, labels, scores, thresholds → `eval/_local` (gitignored). NEVER git-add, NEVER carry in a pack. Public git gets only: this spec, the detector interface code, the manual verdict, and the negative-result report if it fails (3.2 privacy split).

---

**THIS-SESSION pass criterion (met):** detector spec + interface frozen; real-data validation plan written with a numeric, falsifiable bar; synthetic validation explicitly forbidden; fail-consequence stated. No training, no eval, no GPU.
