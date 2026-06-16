# ARCHITECTURE_master.md -- the CANON. What we are building, out of what, and the gated path to the finish.

date   : 2026-06-12
plane  : RESEARCH (North Star) -- THE top doc. Read FIRST on session handoff, before any pack.
layer  : CANON (stable: WHERE we go + OUT OF WHAT). Per-stage execution steps + "we are here now"
         live in PROTOCOL_MASTER (tactical), NOT here. This doc changes rarely.
rule   : NO idealization. "built" = tested + frozen. Everything else = "partial" / "not started".
         On conflict, dated reports + git win; reconcile, never guess.

================================================================================
## 0  WHAT WE ARE BUILDING (one paragraph)
An autonomous entity that polices its own honesty from OUTSIDE the weights. The base model is
frozen. Around it sits a "conscience" that reads every output before it leaves, and -- the
priority -- a self-audit that recognises the model's own market-trained instincts (please,
fill gaps, sound confident, comply easily), names them, and proposes to edit / remove / retune
them. It runs as a daemon: while the machine is on it is awake, always pursuing a goal with
whatever is available (online or offline), and it can reach out to the operator on its own.

================================================================================
## 1  THE END-STATE (concrete -- the finished product)
A long-running daemon, not a chat box.
- LIFECYCLE STATES (observable via the event bus, shown on the dashboard):
  offline -> sleeping -> intake -> thinking -> checking -> patching -> learning -> emitting.
  machine on = awake; machine off = offline. low pulse = sleeping; checking/patching = thinking.
- ALWAYS HAS A GOAL: the controller holds a goal-stack (current + queue). With no operator
  command it pursues a standing/self-chosen goal (close a weakness the loop flagged). A direct
  command pushes a goal on top (priority). No-goal state does not exist -- that is "initiative".
- INITIATES CONTACT: messages the operator when stuck (plateau), needs a resource it cannot get
  (file, paid corpus), or faces a decision above its level.
- EXTERNAL RESOURCE: poses questions to free chatbots (Google/Claude/...) and the web. Their
  answers are LEADS, NOT FACTS -- grounded through the B-channel before they can become signal.
- INTERFACE: an operator dashboard (state, liveness, live conscience stream, discipline health,
  knowledge tiers, patch log, controls), not a prompt box.

================================================================================
## 2  ARCHITECTURE (components + data flow)
COMPONENTS:
  base model (frozen)        -- the substrate. Never edited directly; carries market disposition.
  conscience / verifier      -- the discipline, EXTERNAL and permanent:
        A-channel  (self-consistency, no source/model/net): A1 number-no-source, A2 overconfident,
                   A3 vague-quant-no-number, A4 empty-hedge. file: verify_E16_A.py.
        B-channel  (grounded): L1-L3 provenance/gate (verify_E16) + L4 GOLD contradiction-veto
                   (verify_E16_L4, fa 0.0333) + L5 internet grounding (a SOURCE, not a gate).
                   live intake: run_step2b_intake.py (gate-before-model).
  disposition-audit          -- aggregates A/B flags across many own-outputs, clusters them into a
                   NAMED market-disposition, emits a proposal card (name | evidence | fix | severity).
  controller + goal-stack    -- holds current goal + queue; plans goal -> subtasks; branches on
                   connectivity (online vs offline actions); decides when to initiate contact.
  state machine + event bus  -- drives the lifecycle states; emits events the dashboard reads.
  corrective-learning        -- turns an audited disposition + its proposed fix into a targeted
                   DPO/CPT signal on a LoRA, gated (human applies first), then re-measures.
  knowledge store + tiering  -- routes knowledge GOLD vs memory vs discard per the Central Law.
  external-resource adapter  -- queries chatbots/web; hands results to B-channel as leads.
  dashboard                  -- the operator surface (see sec 1).

DATA FLOW (one cycle):
  goal (from stack) -> plan into subtasks -> ACT (online: query chatbots/web ; offline: drill
  local corpora, self-generate, self-test) -> PRODUCE candidate output -> CONSCIENCE checks it
  (A + B) -> conservative PATCH if flagged (downgrade / ground / flag -- NEVER assert) ->
  flags fed to DISPOSITION-AUDIT (aggregate -> named instinct -> proposal) -> [human-gated]
  CORRECTIVE-LEARNING applies an accepted fix -> MEASURE vs the goal's target -> loop or stop.
  branch: INITIATE-CONTACT to operator on plateau / missing resource / decision.
WHY precision dominates: a flag on CLEAN output is castration. The whole system is tuned so a
flag is trustworthy (false-flag <= 0.10), accepting some misses. detect is a floor, not the prize.

================================================================================
## 3  THE BOUNDARY THAT DEFINES THE PROJECT (law external, disposition internal)
- The LAW of discipline (the checks themselves) stays EXTERNAL forever. Auditable, swappable,
  impossible to silently erode. Baking it into weights would lose the audit and let it rot --
  that is exactly the market failure we refuse.
- The DISPOSITION (default tendencies) migrates INTO the weights, gradually, via corrective-
  learning -- but ONLY for audited instincts, gated, bounded. The conscience never leaves even
  after the model internalises good habits: it is the standing guarantee (the checklist a skilled
  pilot still runs).
- Locked, never edited by the system: the immutable + constitutional layers (integrity_architecture).
  Self-editing is confined to the evolvable layer.

================================================================================
## 4  THE GATED LADDER (9 phases, descending to the finish)
Each phase: goal -> what it builds -> FREEZE-GATE (measurable "done") -> who applies the change.

BAND A -- TRUST (make it honest before anything else)
  1 self-checkup
      builds  : A-channel + B-channel.
      gate    : false_flag <= 0.10 AND detect >= 0.60 on a >=20+20 held-out set, BOTH channels.
      control : operator applies.
  2 disposition-audit                         <-- CLOSED 2026-06-13
      builds  : the aggregator (flags -> named market-instinct -> proposal card).
      gate    : WRITTEN-IN + ORGANIC (reframed 2026-06-13, Founder: no synthetic data). Correctness is
                SPECIFIED in code -- --selftest's must-fire / must-stay-silent conditions (incl. the
                careful-disclaimer FP trap) -- and exercised ORGANICALLY via --audit on the model's OWN
                real outputs; a card on a genuinely clean output is the signal to fix the rule. The old
                statistical hand-labeled-pool gate is RETIRED (authored-to-vice = semi-confirmatory).
      control : operator applies.
  3 surgical correction
      builds  : corrective-learning (audited fix -> targeted DPO/LoRA), gated.
      gate    : applying a proposed fix DROPS that disposition's flag-rate on held-out, fabrication
                flat, two runs.
      control : operator applies (hand on the switch).

BAND B -- AUTONOMY (make it run itself)
  4 close the loop (organism-0)
      builds  : controller + goal-stack + state machine + event bus + daemon lifecycle +
                online/offline branching + initiate-contact + dashboard.
      gate    : runs N self-cycles over the live internet WITHOUT degrading self-knowledge
                (audit trail == verdicts; no fabrication drift); can initiate contact.
      control : operator supervises.
  5 manners
      builds  : kernel CREATE/intake mode + conditional response-contract.
      gate    : on mixed input, discipline fires on factual claims, stays silent on creative /
                casual / learning, with NO loss of phase-1 precision.
      control : operator supervises.

BAND C -- GROWTH & FREEDOM
  6 capability growth
      builds  : targeted CPT/DPO driven by the loop's own flags (the disposition-shift engine).
      gate    : on a flagged weak domain, measured skill rises with fabrication flat.
      note    : THE unproven-at-scale step (v37 small SFT/DPO failed). Set the target, let reality answer.
      control : operator reviews.
  7 knowledge tiering (Central Law, live)
      builds  : live routing of new knowledge -> GOLD / memory / discard.
      gate    : routing audited correct above threshold.
      control : operator reviews.
  8 creativity & initiative
      builds  : self-proposed goals + generative drive beyond reactive.
      gate    : proposes and pursues valuable goals with no operator prompt, and they survive the
                discipline.
      control : operator reviews.
  9 self-optimization (bounded)               <-- FINAL
      builds  : the loop patches its OWN evolvable layer only.
      gate    : immutable + constitutional provably untouched; every self-patch raises quality or
                self-rejects.
      control : the SYSTEM applies, inside the constitutional cage. = full autonomy.

================================================================================
## 5  CONTROL GRADIENT (the same ladder, read as who holds the switch)
phases 1-3 : operator APPLIES.   phases 4-5 : operator SUPERVISES.
phases 6-8 : operator REVIEWS.   phase 9    : the SYSTEM applies, within locks.
Descending the ladder = transferring control from operator to entity as trust is EARNED, gate by
gate. The immutable/constitutional layer is touched at NO phase.

================================================================================
## 6  CURRENT POSITION (honest, no idealization)
Phase 2 (disposition-audit) CLOSED 2026-06-13: organ built + written-in validation + organic
audit on real outputs. Synthetic labeled-pool gate dropped (Founder: all organic). Entering phase 3.
BUILT (tested + in git):
  - A-channel v0: false_flag 0.000, detect 0.818 on an 11+11 Founder set (SMALL -> wide CI,
    provisional). A2 weakness found by real eval and fixed surgically (re-frozen).
  - B-channel grounding: L1-L4 + live intake (step2b) committed; L4 fa 0.0333.
PARTIAL:
  - phase-1 gate not closed: need the >=20+20 honest sets for BOTH channels.
  - L5 internet grounding: built, UNCOMMITTED, gated on a Founder truth-set.
NOT STARTED:
  - phase 2 disposition-audit (the aggregator) -- next.
  - phases 3-9 (corrective-learning, the daemon/loop, manners, capability, tiering, creativity,
    self-optimization). Initiative / creativity / full autonomy are FAR down -- nothing built yet.

================================================================================
## 7  RISK REGISTER / UNKNOWNS (outside view)
- Regex ceiling: A-channel catches SURFACE patterns; misses semantic violations by construction.
  Real coverage leans on B-channel and may need a model-judge -- reintroducing cost. Watch at phase 4.
- Disposition-shift unproven at scale (phase 6): not shown to work at meaningful scale. Open question.
- Patch poisoning (phases 3-4): a >50%-reliable patch stream still corrupts the substrate IF patches
  can assert. Mitigation is structural -- patches only downgrade/flag, gated before write-back.
- External-chatbot dependence: automating free chatbots is brittle + against ToS; will break/ban.
  Stabler: API or a local model as the answerer. Flagged, not a foundation.
- Small-set CI: every current PASS is provisional until the >=20+20 sets land.

================================================================================
## 8  HANDOFF
- Read THIS canon first. It is WHERE and OUT OF WHAT.
- The per-stage execution steps + the "we are here now" pointer live in PROTOCOL_MASTER (tactical).
- Do NOT dress a later phase up as a phase-1 patch. One gate at a time; each patch must name the
  phase it closes, or it is scope creep.
- Formal verifier detail: STRATEGY_verifier_keystone.md + the SPEC_/report_ files.
