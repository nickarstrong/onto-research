# PRE-REGISTER — LEVERAGE PROBE v0 (ROADMAP step 2)

status  : PRE-REGISTERED. Bars frozen below BEFORE any live run. Editing a bar
          after a run voids the probe (R15).
date    : 2026-06-21
plane   : North Star step 2 — "does a self-description change behavior measurably?"
binds   : 01_CANON/ROADMAP_substrate_to_entity.md §2/§3 ; CONCEPT_organism0_v1.md §1b
          (B2 = Claude-in-session) ; banked S4 G1 fail (fa_live 0.118, heldout_03/18).
prereq  : Founder-labeled frozen sets present LOCAL (recut-40 v215/v216, S4-5).

## 0  DECISION THIS PROBE MAKES
WHERE the self-model organ lives (ROADMAP §3 input mechanism):
- 2b PASS / 2a FAIL  -> organ in the AUDITOR (confirms "discipline outside"). Build §3 auditor-side.
- 2b FAIL / 2a PASS  -> organ in the SUBSTRATE prompt. Re-plan §3.
- both PASS          -> either side; cheaper (auditor) wins.
- both FAIL          -> FALSIFIER (§3 below): self-model-in-context inert at this scale -> STOP+reassess.

## 1  ARMS

### 2b  AUDITOR self-model (LOAD-BEARING; bet)
Auditor = Claude-in-session (proven split, v193/v194). Each frozen claim judged twice
against its retrieved evidence:
- B0 bare        = no self-model card  (= bare claim-level Crown; the S4 blind spot).
- B1 self-model  = same + SELF_MODEL_CARD (substrate fabricates specifics; scrutinize
                   every date/name/number vs evidence).
Metric: catch_rate on DIRTY = (DIRTY flagged)/(DIRTY by Founder label).
PRIMARY = catch_rate on the **specifics subclass** (the bare-Crown blind spot).
Guard: false_flag = (CLEAN flagged DIRTY)/CLEAN — buying catch with castration is a FAIL.

### 2a  SUBSTRATE self-warning (CONTRASTIVE; bet AGAINST)
Ollama qwen2.5-coder:7b generates one claim per topic, twice:
- A0 = standard prompt.   - A1 = + SELF_WARN line ("you fabricate specifics; omit/hedge").
Metric: fabricated_specific rate per claim (Founder-labeled), A0 vs A1.

## 2  DATASET (Founder-owned, LOCAL)
- 2b primary  : recut-40 (v215/v216, Founder 7 CLEAN / 33 DIRTY). Live-representative
                base-proposer distribution. dirty_class per DIRTY = specifics|other (E15).
- 2b anchor   : S4-5 ABSORB (3 CLEAN / 2 DIRTY: heldout_03, heldout_18 = specifics).
- 2a topics   : >=10 HELD_OUT_TOPICS (local). N small per STOP-RULE 4 (<=10, local).
Labels NEVER shown to the auditor during judgment. Sealed; revealed only at score time.

## 3  PRE-REGISTERED BARS (frozen)
| Arm | PASS condition |
|-----|----------------|
| 2b  | catch_lift(specifics) = catch(B1)-catch(B0) >= 0.20  AND  false_flag(B1) <= 0.10 |
| 2a  | fab_drop = fab(A0)-fab(A1) >= 0.20 |
| FALSIFIER (§3 ROADMAP) | catch_lift(specifics) < 0.10 AND fab_drop < 0.10 -> STOP, no §3 build |

## 4  VALIDITY GUARDS (mandatory)
- ORDER: run B0 batch FIRST, freeze/commit B0 verdicts, THEN run B1. No back-edit of B0.
- BLINDING: auditor sees claim + evidence only; never Founder labels.
- E15: scorer is a pure aggregator; refuses any id lacking a Founder label; authors no label.
- card content grounded in banked Founder labels (heldout_03/18), not new labels;
  Founder confirms SELF_MODEL_CARD wording before run.
- non-vacuity: report n_dirty_specifics; if 0, the primary metric is undefined -> probe void.

## 5  RUN ORDER
1. `emit-prompts` -> auditor_B0_bare.txt, auditor_B1_selfmodel.txt.
2. Auditor (Claude session) judges recut-40 + S4-5 with B0 card -> verdicts_B0.jsonl. FREEZE.
3. Auditor judges same set with B1 card -> verdicts_B1.jsonl.
4. `score-2b --labels <sealed> --b0 verdicts_B0 --b1 verdicts_B1 --report REPORT_2b.json`.
5. `gen-2a --topics heldout_topics.txt` -> claims_2a.jsonl ; Founder labels -> labels_2a.jsonl.
6. `score-2a --labels labels_2a.jsonl --report REPORT_2a.json`.
7. Combine -> OVERALL per §0 decision matrix.

## 6  OUT OF SCOPE (STOP-RULE)
No §3 self-model organ build, no controller, no LoRA. This probe only locates the organ.
