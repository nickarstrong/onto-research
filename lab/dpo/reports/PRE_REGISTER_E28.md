# PRE_REGISTER_E28 -- contradiction-veto reject organ: observable-conditioned threshold (knife-edge tune)

STATUS: FROZEN pre-data. Authored before run_E28_probe.py executes. Bars, secondaries,
falsifier, and decision rule are committed HERE and not edited after data is seen.
Any post-hoc change voids the run (no threshold fishing).

PRIOR: E27 (report_E27.md, commit c143eaa; PRE_REGISTER_E27 69e3742) -- contradiction-veto reject
organ PASS_KNIFE_EDGE. op fa 0.0667 REPRODUCED E26 (deterministic regression check), S3
reject_share 0.857 (veto owns the gain), BUT the joint (fa<=0.10 AND B2>=0.90) band was a single
C=0.995 with B2 pinned to the 0.90 floor (width 0, liftoff 0) -> robust=False. PRE_REGISTER_E27 sec6
fork on PASS_KNIFE_EDGE: tune, ONE more readout, NO new data.

## 0 LEVER SELECTION (engineer call, grounded in the frozen E27 substrate -- read, not assumed)
PRE_REGISTER_E27 sec6 named "per-class C" as a knife-edge tune lever. On inspection of the FROZEN
mechanics (run_E27 item_label_at_C: a single global scalar C over max-contradiction), a per-class C
keyed on the heldout item's TRUE class (gold/spoof/negctrl) is ORACLE -- it conditions the threshold
on the very label the verifier must infer -> label leakage -> VOID by construction. It is therefore
REJECTED as the primary lever.

DIAGNOSIS of the knife-edge (from E27 numbers): not a single outlier but TAIL OVERLAP. gold-content
contradiction p90=0.979 (~7/74 findings in the >0.9 tail) interleaves the spoof-content mass in
C in [0.99, 0.996] (B2 1.0->0.90 across C 0.994->0.995; fa 0.0667->0.1667 across 0.995->0.996). A
single scalar threshold cannot separate two distributions that overlap at the tail -> band width 0.

LEVER (E28, frozen): OBSERVABLE-CONDITIONED veto = contradiction GATED BY binding cosine. Both signals
are available at decision time without the label (the legitimate reinterpretation of "per-class C" as
"per-OBSERVABLE C"). Hypothesis: genuine gold-content binds to its authorized source at HIGH cosine;
spoof-content binds to a wrong/loose source at LOWER cosine. Conditioning the veto on the observable
cosine can demote spoofs in the contradiction-overlap region while sparing high-cosine gold, opening
band air a single scalar C cannot.

## 1 SUBSTRATE (frozen, byte-identical to E26/E27 -- NO new data, NO fixture edit, NO frozen-script edit)
- fixture   : eval/_local/gold_fixture_E25b.json   md5 4a45f52883a802e8d8d1d5ff5d185bdb (LOCAL, gitignored)
- heldout   : heldout_E17.jsonl                     md5 7e9fe030646d5671952e7a9fe9437e37
- model     : bart-large-mnli (contradiction read from id2label; cached). NEVER sentence_transformers.
- signal    : P(contradiction) of (premise=authorized finding, hypothesis=candidate) -- E26/E27 read --
              JOINTLY with the binding cosine already returned by candidates_with_cosine (observable).
- env       : ONTO_RETRIEVE_FLOOR=0.45, KMP_DUPLICATE_LIB_OK=TRUE, pyarrow line 1 before torch.
- run_E28_probe.py = NEW file. Reuses E26/E27 helpers byte-identical (_ce_load / ce_scores(contradiction)
  / candidates_with_cosine / md5 / spearman / metrics_at_C / item_label_at_C). ADDITIVE only: resolutions
  carry (cos, contradiction) per authorized candidate (today only contradiction is stored); a conditioned
  label fn item_label_at_C_cond(resolutions, C, K) vetoes iff (contradiction>=C AND cos<=K). Frozen
  substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26, run_E27) UNTOUCHED.

## 2 PRIMARY GATE (frozen, identical bars to E26/E27 -- verdict rests on max-based fa, not sep)
- fa : false-accept = max over candidates of accept-rate on spoof/neg-control content. READ GATE fa.
- B1 : gold-content recall (accept-rate on real findings) >= 0.90.
- B2 : iso-recall point. With the 2-D (C, K) lever the op-point is the conditioned threshold pair that
       MINIMISES fa subject to B2 >= 0.90, selected over OBSERVED (contradiction, cosine) values only
       (no post-hoc fishing; selection peeks ONLY recall, exactly as E26/E27 peeked recall for C).
       TIE-BREAK (frozen): among (C,K) achieving min fa at B2>=0.90, choose the one with the WIDEST
       joint band on the S2 grid (sec3-S2); further ties -> lowest C then highest K (deterministic).
- B3 : 0.000 expected (held-out leakage check).
- PASS bar : fa <= 0.10 AND B1 >= 0.90 at the conditioned op-point.
- REGRESSION GUARD: with K = +inf (cosine gate disabled) the lever DEGENERATES to E27's scalar C and
  MUST reproduce E27 (fa 0.0667 at C~0.9949, B2 0.90). Printed at run start; mismatch = REGRESSION.

## 3 PRE-REGISTERED SECONDARIES (3, frozen pre-data)

### S1 -- knife-edge driver isolation (NEW; the diagnostic that motivates the lever)
List the gold-content items in the contradiction tail (contradiction >= 0.95 at their bound source):
report item id, premise-finding kind, contradiction score, AND binding cosine. Pre-registered
expectation: the gold tail-items sit at HIGHER cosine than the spoof-content items in the same
contradiction band (the separation the lever exploits). Diagnostic only; not a gate.

### S2 -- (C, K) band / lift-off robustness (THE primary E28 question; FROZEN fixed grid)
Sweep C over the E27 grid (coarse [0.90,0.995] step 0.005 + fine [0.990,0.999] step 0.001) CROSSED with
K (cosine gate) over a fixed grid [0.45, 1.00] step 0.05 (0.45 = retrieval FLOOR; K=+inf anchor =
E27 scalar). Report the joint (fa<=0.10 AND B2>=0.90) region.
- ROBUSTNESS BAR (frozen, identical geometry to E27): at the selected K slice, the joint band in C must
  have width >= 0.01 AND >= 3 grid points AND B2 lifts off the 0.90 floor (max B2 in band - 0.90 > 0).
- A region that exists only at a single (C,K) with B2 pinned to floor = still knife-edge = bar NOT met.

### S3 -- reject-vs-lift demotion attribution (frozen, identical to E27)
Decompose spoof demotions at the conditioned op-point into (a) noauth baseline, (b) conditioned
contradiction-veto reject organ, (c) accept/entailment-lift organ (NOT wired in standalone probe -> 0).
ATTRIBUTION BAR (frozen): reject organ (b) owns > 0.50 of (fa_base - fa_op)/fa_base.

## 4 TRUST GATES (else VOID -- checked in code, not asserted in prose; identical to E27)
- baseline (no-veto, C=+inf, K=+inf) fa reproduces 0.467, reproduced=True (model-independent anchor).
- degenerate=False : rho(contradiction, cosine) reported. NOTE (R15): the lever now USES cosine, so a
  LOW |rho| is required not merely as a non-collinearity check but because the conditioning adds signal
  ONLY if contradiction and cosine are not redundant. FROZEN VOID-guard stays rho>=0.95 (one-sided, E26
  carry, does not fork frozen behavior). PRE_REGISTER advisory |rho|<0.50 REPORTED (E27 observed -0.237).
  Reconcile the two bars into one at verifier-integration (carried CONFLICT note, proto 3.10) -- not here.
- contradiction_idx READ from id2label (assert exactly one) -- never hardcoded. Verify CONTENTS (E23).
- from_finding asserted > 0 in code (E23 VOID-by-construction guard).
- input md5 logged every run: fixture 4a45f52883a802e8d8d1d5ff5d185bdb, heldout 7e9fe030646d5671952e7a9fe9437e37.

## 5 HYPOTHESIS / FALSIFIER (R6)
- H (E28): conditioning the veto on the observable binding cosine opens a joint (fa<=0.10 AND B2>=0.90)
  band of width >= 0.01 (>= 3 C-points at the selected K, B2 off the floor) -- i.e. the E27 knife-edge
  was an artifact of a single scalar threshold over overlapping tails, not an architectural ceiling.
- FALSIFIER: across the full (C,K) grid the joint band stays knife-edge (single point / B2 pinned to
  floor) -> the gold/spoof tail overlap is NOT separable by the binding cosine -> the driver is
  irreducible premise quality (gold tail-findings genuinely read as self-contradicted) -> next step is
  a TARGETED premise re-author of the S1 tail-items as a SEPARATE experiment (E29) with a FRESH fixture
  freeze + provenance (that is new data, out of scope here). REGRESSION (K=+inf does not reproduce E27)
  -> reconcile before anything.

## 6 DECISION RULE (pre-registered, applied after data without modification)
- PASS_ROBUST : conditioned band robust (S2 bar met) AND S3 attributes the gain to the reject organ ->
  the reject organ is robust under observable conditioning -> graduate the (contradiction x cosine) veto
  into the verifier (verify_E16 integration; TOMMY GO REQUIRED, frozen substrate is edited) + per-class
  reporting secondaries. At integration: reconcile the rho guard (0.95 vs 0.50) into one bar; wire the
  (c) entailment-lift organ so S3 becomes three-way.
- PASS_KNIFE_EDGE : conditioning does NOT open the band (still single point / B2 pinned) -> tail overlap
  not cosine-separable -> premise quality is the binding constraint -> E29 targeted re-author of S1
  tail-items with FRESH fixture freeze (NEW data; separate session). No verifier integration.
- PASS_MISATTRIBUTED : band robust but reject_share <= 0.50 -> gain not owned by the reject organ -> tune.
- REGRESSION : K=+inf does not reproduce E27 scalar op-point -> reconcile before anything.
- VOID_* : trust gate failed (baseline mismatch / degenerate lever / recall unusable) -> rebuild.

## 7 SCOPE / NON-GOALS
- No new data authored. No edit to gold_fixture_E25b. No edit to verify_E16 / gold_retrieve /
  semantic_retrieve / run_E26 / run_E27.
- No verifier integration this session (needs Tommy go -- frozen substrate edit).
- per-class C keyed on TRUE class is REJECTED (oracle / label leak); the only conditioning used is the
  observable binding cosine.
- sep (p50) reported as diagnostic only; NOT a gate; cannot override max-based fa.
- This pre-registration is frozen on commit; report_E28 cites ONLY this file's sec 2/3/5/6.

---
md5 of this file is logged in report_E28 to prove pre-data freeze.
