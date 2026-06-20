# ROADMAP — substrate → entity (gated)

status  : canonical. Supersedes ONTO_guide_substrate_to_entity.html sec 4-9 on the
          load-bearing ordering. Guide remains Founder-facing narrative only.
date    : 2026-06-21
plane   : North Star (chatbot -> autonomous entity)
binds   : STRATEGY_verifier_keystone.md sec 0 ; CONCEPT_organism0_v1.md ;
          ARCHITECTURE_master.md.

## 0  REFRAME (what changed vs the guide)

1. **Self-checkup lives in the capable auditor, not the frozen substrate.** The judge
   seat (strong model in B2, execution-split) already audits substrate output. The
   substrate does NOT introspect itself — the external auditor maintains a self-model
   OF the substrate and feeds divergences back. Consistent with "discipline outside".
2. **Probe-before-build on every load-bearing assumption.** No organ is built before a
   cheap probe shows its enabling assumption holds. The guide jumped to build; this does not.
3. **RFT is NOT in the spine.** Growth = curated data + operator-approved optimization,
   GOLD as fixed axis. RFT/LoRA = optional capability polish, gated separately, never
   load-bearing. (S3/S4: RFT-through-Crown falsified at claim granularity.)
4. **Controller is the heart and it is unbuilt.** "Personality" = the loop firing
   unprompted, which requires a controller. Everything before it is sensing/discipline.

## 0b  ENOUGH-FOR-STAGE (anti-perfectionism)

Polishing every fragment to ideal is the inverse failure of cheap-for-cheap. The model
never leaves the lab; failure is cheap and reversible (rollback, rerun). Therefore the
bar is **enough to learn the next thing**, not enough to trust in the world.

**Rule: "enough" = the minimum at which the NEXT gate stays honest.** Below that is sand;
above that is gold-plating. Raw-but-working beats polished-but-late.

Stage-tunable (raw is fine, refine later): yield height, substrate size (7B as-is),
code cleanliness, auditor-in-session vs always-on. These are lab-exit gates, not now.

NON-NEGOTIABLE even raw (not polish — they decide whether the result means anything):
- fa_live = no fabrication absorbed. Drop it and the experiment "does Crown-gated
  learning preserve discipline" lies to itself.
- measurability on non-empty/correct data (E15). Drop it and we measure nothing.

High-bar concerns (stronger substrate, always-on capable auditor, realtime gating) are
END-STATE / lab-exit, deferred until the entity would actually leave the lab.

## 1  STATE

- DONE: external discipline. Crown verifier fa_live=0.000 (Rung-1, 65 claims, v194).
  disposition-audit (phase 2) + fix(a) rule-level removal (A1 0.361 -> 0.000, phase 3).
- DONE (v202): specifics gate wired post-B2. S4 re-run G1 fa_live 0.000 PASS /
  G3 yield 0.050 FAIL. Closes partial-fabrication hole; yield is the open cost.
- FROZEN: substrate (Qwen-coder:7b), s2b verifier (blob 35eefda1), GOLD axioms.

## 2  STEPS (each gated; build only after its gate passes)

| # | Step | What | Gate (pre-registered) |
|---|------|------|----------------------|
| 1 | Yield recovery | Filter passes enough verified material AND holds fa_live=0. Restrict specifics to fabrication-class tokens and/or widen retrieval coverage. | fa_live <= 0.10 (HARD) AND yield enough to feed §2-4 (stage-relative, not a fixed 0.20; see §0b) |
| 2 | Leverage probe | Does a self-description change behavior measurably? 2a: substrate told "weak in X" -> fewer X failures. 2b: auditor + self-model catches divergences bare Crown misses. Decides WHERE the organ lives (bet: 2b). | measurable shift over no-self-model baseline |
| 3 | Self-model organ | disposition-audit offline cards -> live self_model.json the AUDITOR reads each cycle. The entity's sight. (Build only if §2 passed.) | detect-lift over bare Crown on held-out weak-spots |
| 4 | Controller / goal-stack | Reads self-model -> selects next action ("weak in X -> verify X"), fires UNPROMPTED. The will. **chatbot -> entity transition.** | N cycles, goals target real gaps (not random), every action Crown-gated, fa_live=0 |
| 5 | 24/7 + memory | verdict-trail -> working memory; loop runs unattended; correct contact triggers. | N cycles unattended, G_drift fa_live <= 0.10, >=1 correct contact |

## 3  FALSIFIERS

- §2 fails (no measurable shift either side) -> a self-model in context is inert at this
  scale; need a different input mechanism before any "self-awareness" claim. Stop, reassess.
- §4 controller selects goals no better than random -> "initiative" is cosmetic; the loop
  is a hamster wheel, not a will. Honest NO.
- Any step: fa_live > 0.10 -> discipline leaked; the safety bar overrides progress.

## 4  ORDER RATIONALE

Discipline (done) -> material (yield, §1) -> prove the organ's input works (§2) -> sight
(§3) -> will (§4) -> autonomy (§5). Self-model before controller because a controller
without a self-model chases blind. Probe (§2) before self-model because building a sensor
nothing reads is the failure mode the guide walked into.

## 5  NEXT

Step 1. Trigger: `LABA, SPECIFICS YIELD PROBE`. Cheap, deterministic, frozen claims/abstracts.

---
*ROADMAP_substrate_to_entity.md · 2026-06-21 · gated, probe-before-build, controller=heart, enough-for-stage (§0b).*
