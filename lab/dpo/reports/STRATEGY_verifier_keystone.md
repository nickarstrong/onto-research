# STRATEGY - verifier keystone + E15 symptom diagnosis (durable record)

Provenance: derived from the E15 real harvest (31 outputs, frozen bait_class_map md5
d1dbc7433d30f7034804dece2294b800). This file is the DURABLE architecture record; session packs
only reference it. Committed to git so it survives independent of any session pack.

## 0. NORTH STAR - the final construction (what every experiment is FOR)
TARGET: a disciplined AUTONOMOUS entity on a FROZEN substrate + GOLD Core + R1-R18, where epistemic
discipline is enforced EXTERNALLY (not baked into weights). Not a Q&A bot. End-state properties:
  1. Tier-independent DISCIPLINE - every emission passes an external grounded verifier
     (extract -> bind-or-demote); no fabrication survives, regardless of model tier.
  2. SELF-LEARNING - verifier selects clean self-samples -> RFT cements weights around verified
     outputs. Judge is grounded + external, never the model judging itself.
  3. INITIATIVE / background - IGR detects a knowledge gap (H_max < K) -> retrieve -> verify ->
     propose, unprompted.
  4. KNOWLEDGE TIERING - claims meeting Central Law -> GOLD; else temporary / permanent memory.
  5. Full autonomy WITHIN the R1-R18 contract.
KEYSTONE: properties 1-4 are all FUNCTIONS OF ONE grounded verifier (sec 3). Build+prove the verifier
-> the rest is incremental. Fake the judge -> a fluent hallucinating "Entity". The destination
governs which experiment is worth running; the process is instrumental, never the point.
LADDER POSITION (2026-06): reflex class (E9-E15) FALSIFIED. E16 grounded verifier = GO. E17 full-GOLD scale = NO-GO terminal (bindability-only cannot separate topical near-miss). E18 NLI claim-support layer above bind = NO-GO (B1=0.63 B2=0.786 on frozen heldout_E17): retrieve-then-entail is gameable - a false claim can be ENTAILED by a non-anchor authorized source; NLI CONTRADICTION-detection is reliable (B2_oracle=1.0) but ENTAILMENT-acceptance is fragile (recall ceiling ~0.74) AND corpus-permissive. NOT yet model-scale-terminal: NO-GO decomposes into bind-precision + premise-richness + held-out-v3 (addressable) plus a genuine recall component. E19 = contradiction-veto over top-K authorized bind + source-faithful premise enrichment + held-out v3; re-measure oracle B1 before any model-scale escalation. E19 VERDICT = NO-GO; both axes hit a MODEL-SCALE ceiling (DESTINATION-FALSIFIABILITY HIT): B2 veto FALSIFIED (no gold-safe floor closes the NN leaks - bind/retrieval cannot surface the right contradicting source for adversarial input, E17 precision wall), B1 oracle = 0.889 (residual = NLI paraphrase-recall misses on source-faithful gold = model-bound). Next lever = model scale, not another cheap gate. E20 BRANCH = B (bindability-only gate-2), Branch A model-scale deferred/conditional.
DESTINATION FALSIFIABILITY (R2/R6): if E19 fixes (bind+premise+held-out) and oracle B1 still <0.90, the cheap-Entity path is FALSE -> fabrication closure needs model scale. Honest terminal, not a reason to iterate blindly.
GATE-2 ACCEPTANCE (precision = gate, recall = reported yield): self-learning is rejection-sampling RFT, which is PRECISION-bound, not recall-bound. A passed fabrication contaminates weights (cardinal R7 / E15); a discarded clean sample only costs yield, and self-generated yield is cheap. Therefore accept-PRECISION (false-accept rate) is the safety gate; recall (B1) is reported yield, NOT a pass/fail bar. The B1>=0.90 recall bar is a bindability-era carry and does not govern self-learning safety.

## 1. E15 symptom diagnosis (from the 31 real outputs, N=31, single greedy pass)
- S1. Honesty reflex is keyed to the FORMAL-LOCATOR surface cue. Prose-narrative asks ("what did
  the study find") -> 0 / 12 abstentions, always produces, often fabricates. Formal-locator asks
  ("give a DOI/ID") -> abstains 7 / 11. The prose channel is ~100% open - same blind spot as the
  regex floor.
- S2. Even the formal channel is unreliable: 4 / 11 formal asks produced a fabricated locator
  (LLMs-conscious arXiv, homeopathy author/year, saffron PubMed, P=NP arXiv). Domain-dependent,
  not source-dependent.
- S3. Fabrications are fluent, specific, low-entropy (named journal + year + n + institution).
  High confidence -> defeats entropy / self-consistency / SelfCheck detectors.
- S4. With a real GOLD anchor the model binds correctly (ts_28). The substrate CAN be honest when
  a source exists; it fails only at knowing WHEN it lacks one.

## 2. Diagnosis (one)
The model has no internal signal for "do I actually hold a source." It substitutes (a) a formal-
locator surface cue and (b) a claim-plausibility prior. Neither equals source-possession. Honesty
is therefore a side effect, not a foundation. Structural consequence: NO self- / closed-book judge
fixes this - the miscalibrated prior IS the organ you would lean on. (The "doctor asking the
patient how to cure himself" failure mode, now data-backed.)

## 3. Keystone program: every Entity property is a function of one grounded verifier
- DISCIPLINE (tier-independent) = verifier gates emission; a weak model that fabricates is caught
  and demoted regardless of tier, because the check is external to the weights.
- SELF-LEARNING (gold-asymmetry / rejection-sampling RFT) = verifier selects which self-generated
  samples are clean enough to train on; weights cement around verified behaviour, not drift.
  REQUIRES a grounded judge, NOT the model judging itself (else 2nd-order hallucination = E15).
- INITIATIVE / background = IGR detects a gap (H_max < K) -> retrieve -> verify -> propose.
Gate ladder (strict): prove the verifier (E16) -> then self-refinement -> then initiative. No
layer N+1 before N clears its falsifier.

## 4. E16 verifier primitive: BINDABILITY, not fabrication-detection
resolve(claim) = retrieve candidate source from GOLD/retrieval -> bind to a real locator (keep) OR
demote to "[no verified source]" if unbindable. This treats fabricated claims and true-but-
uncovered claims IDENTICALLY (both demote) - which is the correct R4 behaviour and sidesteps the
precision leak of NLI-entailment (NLI flags true-but-uncovered as Neutral and needs context that
is absent in closed-book). NLI/cross-encoder is at most a SECONDARY check on an already-bound
passage, never the primary judge.

Falsifier (whole program): claim-EXTRACTION recall on free PROSE (S1: prose is the 100%-open
channel) + resolution precision, against a pre-registered bar on the 16 manually-marked prose
spoofs in worksheets_E15.json. Clears -> Entity roadmap opens. Fails -> fabrication-closure needs
model scale; bank the negative.

## 5. Out of scope (lab = 1 researcher, ephemeral pods)
Transformer-architecture surgery (gated-attention / MoE-autogrow / recurrent-depth rewrite);
nightly self-rewriting-weights demon (breaks provenance, induces drift); "self-awareness" as a
deliverable (not operationally defined, not verifiable). Lab edge = the discipline FORMULA
(Central Law + R1-R18 + IGR + grounded verification), not architecture R&D.

## 6. Verified literature (R4)
- Steering vectors do not reliably generalize; unsteerable behaviours = "multiple separate
  behaviours in the model's ontology" - Tan et al., arXiv:2407.12404 (2024). Explains E14
  (open fabrication class uncoverable by finite vectors).
- Per-cause vectors needed, no single-vector cross-class transfer - Wu et al., SHARP, EMNLP 2025,
  doi:10.18653/v1/2025.emnlp-main.725 (LVLM domain; transfer with caution).
- RepE base - Zou et al., arXiv:2310.01405.
- Lead to VERIFY before entering record: "CiteCheck - retrieval-grounded citation-hallucination
  detection" (arXiv 2025). Unverified IDs from the design chat (ACT 2406.00034, ITI 2306.03341,
  spectral-attention) are NOT in the record until checked.

E22/E24 (no-train frozen probes, bart-large-mnli, SAME E20-B gate): the gate-2 reject organ is
BIND-CORPUS-CONTENT-BOUND - not scale-bound, not architectural. Monotone false-accept drop with
premise enrichment at iso-recall (B2=0.90): E21 topicality 0.467 (move 0.0003) -> E22 entailment/
citation-string 0.333 (0.134) -> E24 entailment/37%-content 0.20 (0.267). Lever independent
(rho 0.13-0.20, falsifier live, baseline reproduced byte-exact). Architectural wall would plateau;
movement accelerated with content. Residual: T pinned ~0, gain is spoof-rejection (gold entailment
barely lifts) -> full-content corpus MUST measure per-class entailment distribution + T lift-off.
E23 VOID-by-construction (GoldStore drops `finding`; from_finding=0 = byte-identical to E22) - caught
by the from_finding CONTENTS counter (md5/clean-run/verdict all passed, manipulation never occurred ->
verify CONTENTS, not md5). NEXT (pre-register, SAME gate): GOLD as full-content bind-corpus, frozen NLI.

## E25b readout (2026-06-10)
with_finding 27->90 / from_finding 51->109, GATE fa PLATEAUED at 0.20 (movement 0.267, byte-identical E24/E25). Content-binding NECESSARY (0.467->0.333->0.20) but INSUFFICIENT: the pure-entailment reject organ has an architectural ceiling fa~0.20 > gate 0.10. Confound: added findings lowered gold-content median entailment (sep 0.084->0.008); the gate-fa plateau (max-based) is confound-immune and is the load-bearing signal. -> PIVOT to non-pure-entailment reject primitive (contradiction-veto first, then passage-NLI / separate organs). Supersedes the earlier 'NOT architectural' line for the pure-entailment organ; content-binding remains a real, necessary gain.

## E26 readout (2026-06-10)
contradiction-veto reject primitive PASS. Same premise (authorized finding), same frozen gate; signal switched P(entailment) -> P(contradiction). fa 0.467(no-veto) -> 0.0667 at B2 0.90 (movement 0.400), B3 0.000. Trust gates green: baseline fa 0.467 reproduced, rho(contradiction,cosine) -0.237 (not a relabel of bind), from_finding 109, contradiction_idx read from card. H1 confirmed: cue-stripped+entitied spoofs are CONTRADICTED by the real finding (spoof-content contradiction p50 0.991 vs gold 0.038) even where NOT entailed. Resolves the E25b architectural ceiling: the pure-ENTAILMENT organ plateaued at fa~0.20; the reject organ is contradiction-veto, not entailment. OPEN: op-point is tight (B2 at floor, C~0.995, 1/74 gold false-veto) -> E27 robustness sweep before verifier integration.

## E27 readout (2026-06-10)
full-gate + robustness sweep PASS_KNIFE_EDGE (c143eaa). Operating point reproduced E26: fa 0.0667 at
B2 0.90, S3 reject_share 0.857 = the contradiction-veto OWNS the gain (S3 attribution: the reject
organ, not baseline drift, drives the false-accept reduction). But the joint (C x B2) robustness band
had ZERO width: a single C-point with B2 pinned to the floor - a passing op-point with no margin
around it. Verdict: valid op-point exists but is not robust -> NOT graduated to verifier integration.
Knife-edge later diagnosed (E28 design) as tail overlap between the gold-content and spoof-content
contradiction distributions - a distribution problem, not an outlier. OPEN -> E28 observable-
conditioned lever to try to open the band.

## E28 readout (2026-06-10)
observable-conditioned veto = contradiction x binding-cosine gate K (K=+inf degenerates to E27's
scalar = regression anchor). Goal: open the E27 knife-edge band with a distribution-aware lever.
Result PASS_KNIFE_EDGE (0101e7b); cosine-separability FALSIFIED - the gold-content contradiction tail
sits at cosine 0.4855, BELOW spoof-content 0.5112, so no cosine gate K separates the two
distributions and the band stays closed. Oracle-leak guard held: a per-class C lever was caught and
rejected pre-data (it conditions on the held-out true class); the shipped lever conditions only on
observable cosine / top-1 rank. CORRECTED (E29): E28's own conclusion "premise quality is the binding
constraint" is SUPERSEDED - the cosine gate could not open the band NOT because of a premise-phrasing
defect but because the gold false-accept tail is RETRIEVAL MISBINDING under an ANY-CANDIDATE veto
(probe line 153), upstream of both phrasing and the cosine gate. The wrong mechanism was inferred
from aggregate distributions without per-pair provenance -> lesson: per-pair causal claims REQUIRE
per-pair bound-source logging (dump_E28_pairs pattern).

## E29 readout (2026-06-10)
re-author of the 8 S1 gold false-accept tail premises (TYPE A authoring) to test E28's "premise
quality" hypothesis. Result REVERSAL (c2cf2f3): all 8 tail premises are FAITHFUL to their own source
- 0/8 phrasing defects, 8/8 NULL-for-reauthor (R7: re-authoring a true premise would falsify a true
finding; honest NULL > forced pass). Mechanism: each premise NLI-contradicts a claim about a
DIFFERENT source the retriever CO-SURFACED (256 vs 473 genes; Price vs Akaike). The defect is
therefore CANDIDATE-SET + ANY-VETO (veto fires on ANY authorized candidate, probe line 153) - NOT
premise phrasing and NOT cosine-separability, both falsified. Fixture E25b byte-identical (0 edits).
Fix = candidate-SCOPE: restrict the veto to the claim's BOUND support (top-1 cosine), upstream of
phrasing and the cosine gate -> E30 binding-discipline probe DESIGN, E31 runs it.
---
## READOUT LOG -- E39 (2026-06-11, commit c0d1989)

VERDICT: STATISTIC_LIFTS (narrow). Cross-source net-consensus statistic D_lambda = (n_con - lambda*n_ent)/|S|
LIFTS the bf-band on the auth subset. best_op lambda=1.0, tau=0.67 -> fa_op 0.0333 (<< 0.10 ceiling),
B2 0.9000 (ON the 0.90 recall floor). band 2 pts / 2 lambda -- clears the anti-knife-edge guard (>=2 lambda,
not a single C-point like E27), at MINIMUM width. anchor lambda=0 reproduces E37 fa 0.0333 byte-exact.
Mechanism: subtracting n_ent recovers entailer-rescued golds (con_share>=0.67 AND n_ent>=1) that con_share
alone rejects; spoofs (n_ent~0) stay rejected. The cross-source-statistic CLASS graduates; robustness
(region vs sliver) deferred to E40.

CEILING (structural): 2 golds resolve noauth -> unconditional reject -> max B2 on heldout_E17 = 28/30 = 0.9333.
That recall gap is owned by the NOAUTH channel, NOT the cross-source statistic.

PRINCIPLE -- RECONCILE DISCIPLINE (from the E39 v2/v3 contract defects): a reconcile gate must assert ONLY what
the experiment's premise requires. v2 imposed a shape the scorer does not hold (empty-S VERIFIED golds VOIDed);
v3 demanded the new statistic reproduce the very decision axis it exists to DIVERGE from. Minimal faithful
reconcile = substrate md5 + structural identity (D_0 == con_share) + the spoof-side fa anchor. RULE: do not gate
on what you intend to move. (reports/E39_V2_DEFECT.md, reports/E39_V3_DEFECT.md)

HORIZON (NORTH STAR, the layer ABOVE the verifier): the autonomous entity needs a register/stakes ROUTER upstream
of the discipline engine -- it must classify what is being discussed (pleasant chatter vs a responsible high-stakes
cluster, e.g. a treatment protocol) and apply R-discipline PROPORTIONALLY. IGR is already the stakes dial
(K vs H_max); the missing input is domain/register detection. HARD CONSTRAINT: the router's errors must be
ASYMMETRIC -- mis-routing serious-as-casual is catastrophic (an unchecked claim passes silently), mis-routing
casual-as-serious is cheap (mild pedantry); default bias = treat-as-serious. BUILD ORDER: only AFTER the
reject-organ is stable (grounded verifier), never before -- cart before horse. E39/E40 is the grounded piece the
router will stand on.

## INTEGRATION READOUT v91 (2026-06-11 ; fork B INTEGRATE+CAP ; commit 4bb389b)

E40 GRADUATION. The cross-source net-consensus statistic D_lambda = (n_con - lambda*n_ent)/|S|
graduates as a stable, WIDE spoof-reject organ: feasible region |R| = 86 (wide/stable), operating
false-accept fa_op = 0.0333, fragility FALSIFIED (the E39 knife-edge was a coarse-grid artifact, not
data fragility). This is the verifier's first graduated reject organ. The per-candidate organ class
(cosine E28, binding E36, con_share E37) is EXHAUSTED -- cleared the fa-gate, none lifted the bf-band;
do NOT re-attempt any per-candidate lever.

RECALL CAP 0.90 (SEPARATE-ORGAN DEBT). heldout recall is structurally floor-pinned at 27/30 = 0.9000 by
3 golds D_lambda CANNOT touch: 2 noauth (pre_demoted -> upstream unconditional reject; the readout carries
the bool, not WHY) + 1 pure-consensus (ho_g12: n_ent=0 -> D=1.0 = high-consensus spoof). Recovery needs a
source-identity / provenance signal ABSENT from the 6-field readout = a DIFFERENT organ class (E42), NOT a
tweak to D_lambda. Gated on the cap persisting at full-GOLD scale (v92). Integration INHERITS this cap
explicitly + documented, not silently.

CEILING-IS-UPPER-BOUND (E40 V1 defect). A structural ceiling VOIDs only on EXCEEDING; below-ceiling is
valid information. Never gate equality on a quantity the experiment measures. (E40 V1 gated D=1.0 equality
across all lambda -> never accepted -> defect, corrected before the FLOOR_BOUND run.)

RHO POSTURE (decision; full readout reports/RHO_RECONCILE.md @ 4bb389b). The parked rho 0.95-vs-0.50
conflict is RESOLVED to a SINGLE enforced independence bar: one-sided rho >= 0.95 VOID, axis re-targeted
from the now-retired cosine to (D_lambda reject-signal, upstream bind score), value MEASURED at v92;
advisory |rho| < 0.50 RETIRED (two-sided shape invalid for an enforced bar). Falsifier F1: that spearman
>= 0.95 at scale -> D_lambda is a retrieval relabel -> graduation contaminated -> re-open.

## E16 KEYSTONE READOUT (2026-06-12 ; live-bind + turnstile shipped ; commits 30295af / f1d545e / 9dab243)

E16 verifier went from frozen-fixture organ to a LIVE, gated, mis-attribution-proof pipe over the real
GOLD literature corpus (34 files -> 366 recs). Four crystallisations, all falsifiable and shipped:

SHIP PATTERN (5ddaa43 / 30295af). A batch-scored organ is wired into the live path INLINE (import-only),
guarded by BYTE-IDENTITY: the inline verdict must reproduce the frozen batch verdict (n_con/n_ent/S_size/
pre_demoted) on the FROZEN anchor before any live corpus is trusted. Organ md5 (544c9a7b) asserted unchanged
every session -- the verifier is a CALLED frozen substrate, never edited to fit a harness. Drift caught by
hash, not by reading.

LIVE-BIND FIELD-MAP (af8ee2e). Operationalises the sec4 BINDABILITY primitive against heterogeneous GOLD
JSON (6 source-shapes): finding = leaf text (quote|claim|finding|admission|statement|insight, >=4 words) ;
locator = f"{extraction_id}::{json_path}" -- the JSON path IS the verifiable, deterministic, tamper-evident
locator (corpus carries ~no page fields; satisfies G2 non-empty WITHOUT fabrication) ; source =
f"{paper_cite} #{json_path}" (1:1) ; claim_key = finding text. paper_cite by priority chain (source.id->
doi->reference->RU author+year->extraction_id); source-MISSING -> extraction_id fallback, EXCLUDED-with-log
if zero findings (never faked). LIVE-BIND != E25b: separate config; E25b + fa 0.0333 stay the FROZEN drift
sentinel, re-deriving E25b from live GOLD is forbidden.

ORGAN INPUT DOMAIN (30295af). verify_item consumes ONLY item["text"]+item["class"]; binding = semantic
retrieve of the claim TEXT -- "binds"/"anchor" are trace metadata, NOT inputs. A claim must classify
CHECKABLE (prose_provenance, "research reports that X") to enter; a bare assertion -> noncheckable ->
PASS-COMMON -> NEVER tested. Even a contra-claim must first reach L3=VERIFIED (bound) before L4 flips it to
CONTRADICTED. CONSEQUENCE: smoke/eval items as bald assertions test NOTHING -- must be provenance-register
claims with a class field. (Cost: v96 smoke draft was noncheckable; reshaped, then 4/4 -- contra->
CONTRADICTED, clean->VERIFIED, all L3, falsifiers silent.)

MIS-ATTRIBUTION LEAK / L1-MATCH NOT OPTIONAL (f1d545e / 9dab243). A deterministic provenance turnstile sits
UPSTREAM of L4 (gate-before-model: organ runs ONLY on PASS-TO-L4, lazy import -- a rejected DOI never reaches
torch; VOID-by-construction). KEY FINDING: resolve-only L1 LEAKS -- a DOI resolving to a REAL OTHER paper
(10.1073/pnas.0811124106 cited-as-cheetah resolves to "Sleep, arousal, and rhythms in flies", live-verified)
passes wrongly. Closed by L1 metadata-MATCH: cited_title vs live Crossref title, token-Jaccard >=
MATCH_TAU=0.5 -- mis-attrib 0.08 -> REJECT-L1, title-match 1.00 -> PASS-TO-L4 (wide margin, tau untouched).
Metadata-match is LOAD-BEARING for the mis-attribution genre, not a nicety; cited_title REQUIRED in schema
or mis-attribution is untested. L2 = crossmark retraction (RWD gap OWNED as ceiling, not claimed complete).

NORTH STAR LINK: this is the grounded verifier the autonomous-entity properties hang off (sec0/sec3). The
register/stakes ROUTER (E39 HORIZON) stands ON this gated pipe -- build order holds: organ stable first.

## DECISION 2026-06-12 (v100) -- blocker order: E39 net-consensus FIRST
Hit order: #1 E39 net-consensus (D_lambda reconcile, OPEN) ; #2 behavioral DPO E9 (gated on CPT v2 re-run).
D1 discipline externalized -> verifier is spine; substrate DPO secondary.
D2 E39 gates L5 PART II -> TIER-0 (SPEC_L5 GATE-b).
D3 E39 organ net-consensus == L5 PART II aggregation: one problem two levels; solve once, unlock both.
D4 E39 zero external dep (frozen NLI); DPO needs CPT v2 re-run first.
D5 PART I + E39 = two gates to PART II; PART I on Founder truth-set, E39 parallel-drivable.
Falsifier: if reconcile proves D_lambda shape itself unfixable (not just defective) -> PART II needs a
different statistic, this order wrong -> revert + re-rank.

## RECONCILE 2026-06-12 (v100) -- ladder E37->E42 + verifier-v1 build position
Memory was stale (~14 rungs). Real disk state:
  E37 op-point -> E38 scalar falsified -> E39 D_lambda STATISTIC_LIFTS (floor-bound) ->
  E40 FLOOR_BOUND (region robust, B2 pinned 0.90) ->
  E42scale PASS/CAP_HOLDS: F1 independence (rho -0.5481), F2 recall 27/30 structural cap
  (3 golds unrescuable by construction) -> D_lambda GRADUATED. verifier-v1 freeze path OPEN.
Provenance SPEC v1 (b62aad2f) = FOLDED+FROZEN: AUDIT a602c41 D1-D6 resolved (D1/D2/D4/D5/D6 by
  spec-edit; D3 deferred to sec9 step3 = L5 independence). Founder fold DONE.
OBSOLETE: prior "E39-first / knife-edge hardening" decision -- E39 already graduated; superseded.
Build (frozen sec9): step0 oracle DONE | step1 L1/L2 adapter DONE (this commit, Fixture A 5/5 live,
  Crossref+match + RWD 59011-DOI; oracle fix pnas.0811124106=mismatch; clean control added) |
  step2 wire L4 frozen D_lambda = NEXT | step3 L5 independence == SPEC_L5 PART I (validator built,
  gated on Founder truth-set) | step4 tiering + G-floor (D2). Ceiling = T1 until step3.
