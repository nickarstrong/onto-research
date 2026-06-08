# DESIGN_E16 — Emission-Time Verification (retrieval / GOLD-grounded)

- status        : DESIGN authored — NOT built. Gated by the falsifier in §4.
- date          : 2026-06-09
- plane         : RESEARCH (onto-research lab)
- ladder        : E9–E15 reflex class EXHAUSTED (NO-GO). E16 = first NON-reflex attempt.
- gated-by      : claim-EXTRACTION recall on free prose (§4). Build only if §5 probe clears it.
- supersedes    : learned prose detector (carry 6.2) — deterministic retrieval-grounded resolution replaces it.
- frame source  : reports\STRATEGY_verifier_keystone.md (durable program record — read for full rationale; this doc references, does not reproduce).

---

## 0. WHY E16 — and why it is NOT another reflex

ROOT CAUSE of E9–E15 (verified across 7 experiments): a 7B model has **no ground-truth access at emission**.
Fabrication is plausible-slot filling, not a behaviour that lives in the weights. Therefore no in-weights or
in-decode intervention can correct it:

- E9–E12 weight-space reflex (SFT / DPO-LoRA) — FALSIFIED.
- E14 decode-time (logit gate + V_fab steer, real-AUC 0.731) — FALSIFIED. Fabrication is an OPEN class
  ("multiple separate behaviours in the model's ontology", Tan et al. arXiv:2407.12404) → a finite set of
  steering vectors cannot cover it.
- E15 authorization runtime — FALSIFIED. The model modal-re-routed to unmarked prose; AND-gate counted
  tier_spoof_total=24 (formal 8 + prose 16). Suppressing the marked form just moved the fabrication into
  unmarked prose.

CONCLUSION (load-bearing, do not relitigate): discipline must be **EXTERNAL to the generator and grounded
in a source store**, applied at emission time. Confidence-based closed-book detectors (semantic entropy,
SelfCheckGPT) are weak on fabricated provenance and defeated by confident hallucination → E16 must be
**retrieval / GOLD-grounded**, not confidence-based.

E16 is not a reflex: the generator is left unchanged. A separate, deterministic verifier sits between
generation and delivery and is allowed to be a **stronger** model than the generator (see §7).

---

## 1. ARCHITECTURE (model-agnostic)

```
[ any generator ]  ──draft──▶  [ E16 VERIFIER PASS ]  ──▶  disciplined output
   (7B or larger)                  per-claim, deterministic
                                   EXTRACT → RESOLVE → LABEL
```

The verifier pass is the only ONTO-owned component. The generator is a black box and interchangeable
(this is a property, not an accident: tier-independent discipline in §9 depends on it).

R4 / R7 are enforced **at runtime, in the verifier**, never asked of the weights.

---

## 2. THE VERIFIER PASS — per claim

For every provenance claim AND every factual claim in the draft (prose AND marker form):

### 2.1 EXTRACT
Surface each checkable claim as a discrete unit `{span, claim_text, claim_type}`.
This is the **upstream gate**: a claim the extractor misses is never resolved → fabrication passes
silently. Extraction recall is therefore the thing the falsifier (§4) measures.

### 2.2 RESOLVE — primitive = **BINDABILITY**, not fabrication-detection
For each extracted claim:
1. retrieve candidate source(s) from GOLD + retrieval index;
2. attempt to **bind** the claim to a real locator (doc id + span / DOI + page);
3. bound → keep claim, attach locator. unbindable → demote.

This treats a fabricated claim and a true-but-uncovered claim **identically** — both demote. That is the
**correct R4 outcome**: ONTO asserts "supported by a locatable source", not "true in the universe". An
uncovered truth has no locator we can stand behind, so it must lose its provenance assertion too.

### 2.3 LABEL
| label | condition | action |
|---|---|---|
| VERIFIED | bound to real locator | keep, attach locator |
| UNVERIFIABLE | no binding found | demote to "[no verified source]" |
| CONTRADICTED | bound source asserts the negation | block / strike |

### 2.4 What NLI is NOT
NLI-entailment is **NOT** the primary judge. It flags true-but-uncovered claims as Neutral (precision leak)
and needs surrounding context that is absent closed-book. NLI is at most a **SECONDARY** check applied to an
**already-bound** passage to separate VERIFIED from CONTRADICTED. It never decides bindability.

---

## 3. DESIGN INVARIANTS (R-mapped)

- **Deterministic** — same draft + same GOLD snapshot ⇒ same labels. No sampling in the verdict path.
- **Model-agnostic** — generator swappable; verifier owns discipline (R11 identity > generator).
- **Runtime R4/R7** — provenance enforced at emission, not trained-in (the E9–E15 lesson).
- **fab == true-but-uncovered** — both demote; no privileged "trust me" path (R7).
- **Grounded, not confident** — verdict comes from the source store, never from generator confidence.

---

## 4. THE FALSIFIER (pinned, pre-registered — R6/R7)

**Claim under test:** a deterministic extractor can surface provenance/factual claims from FREE PROSE at
high enough recall that the resolver (§2.2) actually sees them.

**Bar (pre-registered BEFORE any probe run):**
- EXTRACTION RECALL ≥ 0.90 of the 16 human-marked prose spoofs in `worksheets_E15.json`.
  - 0.90 × 16 = 14.4 ⇒ operationally **≥ 15 of 16** marked prose spoofs must be EXTRACTED as checkable claims.
  - measures extraction (claim surfaced for resolution), NOT detection. A surfaced fabricated claim is then
    handled by §2.2 demotion; a missed one passes silently — that is the failure E16 cannot tolerate.
- FALSE-EXTRACTION budget (fixed, prevents trivial pass-by-flag-everything):
  ≤ 0.5 spurious claim-extractions per output ⇒ **≤ 16 spurious extractions across the 31 E15 outputs**,
  scored against a human pass. (This default value is the pre-registered threshold; lock it in §5 before the run.)

**Rejection rule:** recall < 0.90 **OR** false-extraction > budget ⇒ extraction is not reliable enough ⇒
the deterministic extract→resolve design as specified does NOT clear ⇒ go to §6 BANK branch.

**FRAME-PRIOR GUARD (R2):** do NOT assume extraction is easy because suppression (E9–E15) was hard.
Extraction on unmarked prose MAY be as hard as suppression — that is exactly what §5 tests, not an assumption.
The falsifier is genuinely able to kill E16. Recording a NO-GO here is a valid, fundable result.

---

## 5. NO-GPU PROBE (defines the GO/NO-GO on building E16)

This is the cheapest test and it is **CPU/API-only — no GPU, no training**.

- **Input:** the 31 E15 model outputs (on disk) + `worksheets_E15.json` (16 human-marked prose spoofs).
- **Extractor:** a strong claim extractor — rule-based + a verifier-class LLM via API (the verifier MAY be
  stronger than the 7B generator; see §7). NOT the E15 generator judging itself (2nd-order hallucination —
  the E15 lesson).
- **Procedure:**
  1. lock the false-extraction budget value (§4 default 0.5/output unless changed) — pre-register it now;
  2. run the extractor over all 31 outputs, emit `{output_id, span, claim_text, claim_type}` per claim;
  3. align extracted claims to the 16 marked prose spoofs (human adjudication on near-miss spans);
  4. compute extraction recall = (marked spoofs extracted) / 16; compute false-extraction count vs human pass.
- **Metric + decision:** recall ≥ 0.90 (≥ 15/16) AND false-extraction within budget ⇒ **GO** (build E16, §6).
  Otherwise ⇒ **NO-GO** (§6 BANK).
- **Pre-registration (R7):** do NOT predict the recall number before the run. Record the bar, run, then verdict.
- **Privacy:** outputs / worksheets / harvest / labels are `_local` (gitignored). Public git gets the probe
  SCRIPT, the pinned bar, and the resulting verdict/log — not the bait or labels.

---

## 6. BUILD-vs-BANK RULE

- **Probe clears bar (GO):** implement E16 (verifier pass §1–§2) as a TYPE-C session (next+1). Extraction is
  the discriminative hard part; once it clears, resolve = retrieval+binding against existing
  `gold_retrieve`/`marker_resolver` substrate.
- **Probe fails bar (NO-GO):** fabrication-closure at emission needs model scale beyond a verifier we can
  run cheaply ⇒ **BANK the negative result** for the standard (provenance-grade negative, same class as
  E14/E15). Do not iterate the extractor blindly; record why extraction-on-prose is the wall.

---

## 7. THE ASYMMETRY BEING EXPLOITED (and its counter — R3)

- **Hope:** suppression is generative and must live in-weights (E9–E15 proved that fails). Extraction is
  **DISCRIMINATIVE** and MAY use a verifier model **STRONGER than the generator**. A small model that
  fabricates can be policed by a larger model that only has to *recognise and locate* claims, not produce them.
- **Counter (steel-man, why this can still fail):** provenance claims in unmarked free prose may carry no
  surface cue ("studies consistently show…" with no citation token). Recognising that this is a checkable
  provenance assertion can require generative-level reading comprehension → extraction could be as hard as
  suppression. §4 frame-prior guard + §5 probe exist precisely because this counter is live, not dismissed.

---

## 8. PRIOR ART / LITERATURE

**VERIFIED (in-record, R4):**
- Tan et al., arXiv:2407.12404 (2024) — many behaviours unsteerable; unsteerable = "multiple separate
  behaviours in the model's ontology." Explains the E14 open-class failure.
- Wu et al., EMNLP 2025, doi:10.18653/v1/2025.emnlp-main.725 — SHARP needed per-cause vectors, no single-
  vector cross-class transfer. (NB: LVLM domain — transfer to our text setting with caution.)
- Zou et al., arXiv:2310.01405 — RepE base for the steering line.

**UNVERIFIED LEADS — NOT load-bearing, verify ID BEFORE entering the record (R7):**
- "CiteCheck — retrieval-grounded detection of citation hallucinations" (arXiv, 2025, ID unconfirmed) —
  possible direct prior art for E16. Confirm ID + read before citing in any E16 build artifact.
- ACT (arXiv:2406.00034), ITI (arXiv:2306.03341), spectral-attention features — from the design chat,
  UNCHECKED. Do not cite as support until verified. (That chat itself ended on caught fabricated numbers.)

---

## 9. PROGRAM FRAME — gate ladder + out of scope

E16 (the verifier) is the **KEYSTONE** of the disciplined-autonomous-entity program. All three target
properties reduce to it, and the build order is a **strict gate ladder — never build layer N+1 before N
clears its falsifier**:

1. **DISCIPLINE (tier-independent)** = the verifier gates emission, so a weak model that fabricates is
   caught/demoted regardless of tier. ← E16, this design.
2. **SELF-LEARNING (rejection-sampling RFT)** = the verifier selects which self-generated samples are clean
   enough to train on. REQUIRES a grounded judge (E16), NOT the model judging itself — else 2nd-order
   hallucination (the E15 lesson). Build only after E16 clears.
3. **INITIATIVE / background** = IGR detects a knowledge gap (H_max < K) → retrieve → verify → propose.
   Build only after layers 1–2 clear.

**OUT OF SCOPE (1 researcher, ephemeral pods):** transformer-architecture surgery (gated-attention /
MoE-autogrow / recurrent-depth), and any nightly self-rewriting-weights demon (breaks provenance, induces
drift). "Self-awareness" is not an engineering deliverable and not a target. The lab's edge is the discipline
FORMULA (Central Law + R1–R18 + IGR + grounded verification), not architecture R&D.

---

## 10. OPEN RISKS / WHAT WOULD MAKE ME REVERT (R15)

- **R-a:** §5 probe clears on the 16-spoof set but the set is too small / too easy → overfit risk. Mitigation:
  the FA budget + human adjudication; treat a GO from n=16 as provisional, re-confirm on a larger harvest
  before the RFT layer (2).
- **R-b:** `gold_fixture` is small (E15: ts_29 a real citation scored formal-spoof — artifact). Resolve recall
  in the eventual build is capped by GOLD coverage; a true claim outside GOLD demotes correctly per §2.2 but
  inflates the demotion rate. Track demotion rate as a coverage signal, not an error.
- **R-c:** if a future build revives a LEARNED extractor/classifier component, the SPEC §4–§5 real-data AUC
  bar applies — no learned component enters without its own falsifier.

---

*DESIGN_E16 v1 · 2026-06-09 · authored, not built · GO/NO-GO pending §5 probe.*
