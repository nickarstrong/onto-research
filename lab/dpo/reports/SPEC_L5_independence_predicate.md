# SPEC -- L5 Corroboration-Independence Predicate v1 (PART I FROZEN ; PART II BLOCKED-on-E39)

Status: PART I FROZEN (pre-register, this commit). PART II = BLOCKED on the open E39 net-
consensus question -- NOT frozen. Fills SPEC_provenance_verifier_v1 sec9 step3 (D3) for PART I only.

## RECONCILE LOG (E37->E39, v100) -- why this is split
- E37 (report_E37, SET_EXHAUSTED): scalar con_share=n_con/|S| over the bound NLI-candidate set does
  NOT lift the bf-band.
- E38 (report_E38, B_STATISTIC_WRONG): the multi-source set is REAL (p50|S|=3-4) but a SCALAR set-
  count cannot separate gold-tail (lone misbound contradictor among corroborators) from spoof (set-
  consensus contradiction); spoofs are richly multi-bound too.
- E39 (net-consensus D_lambda=(n_con-lambda*n_ent)/|S|, DIRECTION-weighted): the right shape -- reads
  entailment, not just contradiction count -- but STUCK in reconcile defects (E39_RECONCILE/V2/V3),
  no clean verdict. The cross-source-statistic question is OPEN.
- E38 sec4 already uses `n_sources = independent gold sources per claim, from the fixture SIDEMAP` --
  independence is COUNTED BY HAND there, never operationally derived.
CONSEQUENCE for this predicate:
  (1) Different layer: E37-E39 = NLI candidates over ONE corpus (organ-set statistic). This L5 =
      real publications (provenance/method/citation). NO duplication of the organ machinery.
  (2) PART I (independence DEFINITION) is exactly the missing operationalization E38/E39 assumed via
      sidemap -> net-new, freezable, supplies their n_sources.
  (3) PART II (aggregation->verdict): my earlier bare-count k>=K_MIN is the SAME scalar-set-count
      shape E38 FALSIFIED. It must be DIRECTION-weighted (E39 D_lambda shape) -- and that statistic
      is the OPEN E39 problem. PART II therefore CANNOT freeze until E39's net-consensus line lands.
  (4) DISCOVERY (R16): L5-tier corroboration and the E39 organ-set net-consensus are the SAME
      aggregation problem at two levels; the independence DEFINITION (PART I) is the shared missing
      primitive both need. Solve PART I once -> feeds both.

================================================================================
## PART I -- INDEPENDENCE DEFINITION  (FREEZE-CANDIDATE; net-new; E39-independent)
================================================================================

### I.0 WHAT THIS PRODUCES
Given a claim C and a candidate source set {S1..Sn}, PART I outputs the COUPLING GRAPH and the
independent-cluster partition -- i.e. it MANUFACTURES the `n_sources` / independence labels that
E38/E39 currently take from a hand sidemap. It does NOT emit a claim verdict (that is PART II).

### I.1 CONTRACT
Input  : claim C ; {S1..Sn} with metadata {authors, affiliations, data-availability, reference-list,
         method-descriptor, tier}.
Output : coupling_graph (edges), clusters (connected components), per-cluster {members, tier,
         support_direction in {entail, contra, neutral}}. NO bool verdict here.

### I.2 PROVENANCE-INDEPENDENCE (mostly metadata-checkable)
Sources are provenance-COUPLED if ANY holds:
  P1 shared author      : author-set intersection non-empty.                 [Crossref; checkable]
  P2 shared institution : affiliation-of-record intersection non-empty.      [Crossref; partial -- dirty strings]
  P3 shared primary data: same dataset/specimen/instrument-run as basis.     [DAS parse; partial -> PROV_UNKNOWN=fail-closed]
  P4 derivation ancestry: one is in the other's basis-citation chain for C.  [reference-list + OpenCitations]
Provenance-independent := none of P1-P4. Missing DAS -> PROV_UNKNOWN -> treated as coupled (fail-closed).

### I.3 METHOD-INDEPENDENCE (weakest leg; partly NLP/judgment)
Method-COUPLED if same instrument modality OR same analytical pipeline / same processed dataset.
Method-independent := different modality class on a per-domain taxonomy. R2 HONEST: modality is not
reliably in metadata -> needs a classifier or manual tag; PART I emits a method-class with a
confidence, and the later harness MUST report inter-annotator kappa before the method leg is trusted
(kappa<0.80 -> method leg downgraded to advisory,  independence rests on provenance+citation legs).
FREEZE DECISION (v1): the method leg is ADVISORY BY DEFAULT. The frozen independence verdict
rests on provenance (I.2) + citation (I.4), both checkable now (Crossref + OpenCitations). The
method leg (I.3) contributes ONLY once a modality classifier lands with kappa>=0.80; until then
it is reported, never decisive. Freeze is NOT blocked on a classifier that does not yet exist.

### I.4 CITATION DISCOUNT (graph-checkable)
If Sk's support for C is established by CITING Sj (not independently re-deriving C), Sk and Sj
collapse to one cluster. Only independent re-derivation seeds a new cluster. [reference-context check]

### I.5 CLUSTERING
Edge(Si,Sj) iff provenance-COUPLED (I.2) OR method-COUPLED (I.3) OR citation-collapsed (I.4).
Connected components = independent support clusters. Each cluster = ONE effective independent witness,
tagged with its support_direction toward C (entail / contra / neutral) and its AXIS-P tier.
NON-REPLICABLE FALLBACK (fossils/historical/one-off): independence measured as MODALITY-independence
on the SAME object (micro-CT + XRF + UV = independent reads); clusters count modalities, not specimens.

### I.6 FALSIFIER FOR PART I (R6)
- FALSE-coupling (over-prune, anti-castration): two genuinely-independent replications merged by one
  incidental shared attribute (an author who changed institutions; a coincidental method tag). High
  false-coupling rate -> PART I castrates. Bar: false-coupling <= 0.10 on a genuinely-independent set.
- FALSE-independence (the dangerous one, INHERITS E38's lesson): coordinated fraud / herd-citation
  whose coupling is NOT metadata-visible -> PART I reports them independent when they share a hidden
  origin. CEILING STATED, never papered: PART I detects METADATA-VISIBLE coupling only. This is the
  same blind spot E38 exposed at the organ level; do not claim PART I catches collusion.

### I.7 ACCEPTANCE BAR FOR PART I (PROPOSED; pre-register targets, NOT measured; R7)
On a labeled set with KNOWN coupling ground-truth (independent / author-coupled / institution-coupled
/ data-coupled / citation-coupled), frozen BEFORE the run:
  - citation-discount correctness: 0 pure-propagation chains survive as distinct clusters. HARD.
  - coupling recovery: PART I recovers the known coupling edges at balanced-accuracy >= 0.85 on the
    provenance+citation legs (method leg conditional on kappa>=0.80, else advisory).
  - false-coupling (over-prune) <= 0.10 on the genuinely-independent class.
FALSIFY PART I = citation discount leaks, OR coupling recovery below target, OR over-prune exceeded.

================================================================================
## PART II -- AGGREGATION -> VERDICT  (BLOCKED; do NOT freeze; inherits open E39)
================================================================================
The verdict rule that turns PART I clusters into a TIER-0 corroboration decision is the SAME problem
E39 is solving at the organ level. E38 proved a bare count (k>=K_MIN) is WRONG (scalar over a set).
The required shape is DIRECTION-weighted net-corroboration over INDEPENDENT clusters, e.g.
  D5 = (entail_clusters - contra_clusters) weighted by cluster tier, over independent clusters only.
This is E39's D_lambda lifted from NLI-candidates to real independent sources. It CANNOT be frozen
here because:
  - E39's net-consensus statistic has no clean verdict yet (reconcile defects open).
  - Freezing a PART II rule now = pre-registering on top of an unresolved lab fork (the exact mistake
    E39_RECONCILE_DEFECT sec4 warns against: do not copy an anchor from an unsettled composite).
GATE: PART II opens only AFTER (a) PART I is frozen + validated, AND (b) the E39 net-consensus line
lands a clean verdict (or is explicitly retired). Until then TIER-0 stays unreachable, ceiling = T1
(unchanged honest state, SPEC_provenance sec7).

## NEXT STEP (recommendation)
Freeze PART I as the pre-register (commit -> datable priority on the independence operationalization).
Do NOT touch PART II until E39's net-consensus reconcile is resolved. The two are now KNOWN to be one
problem at two levels -- resolving E39 unblocks PART II directly.
