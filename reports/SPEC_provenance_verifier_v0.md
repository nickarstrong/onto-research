# SPEC -- Source Provenance Verifier (DOI layer) v0

date    : 2026-06-11
plane   : SURFACE / architecture (NOT the lab NLI ladder; references it for the content-bind + corroboration layers)
home    : onto-research/reports (dateable provenance + ties to lab organ) -- promote to onto-standard when stable
status  : v0 design. Falsifiers stated per layer. Build order in sec8.

--------------------------------------------------------------------------------
## 0 SCOPE -- what this is, and what it is NOT

This spec defines how ONTO admits a cited source (anchored by a DOI or other marker) and assigns it a
trust tier. It is an INTAKE TURNSTILE, not a corpus excavator: a claim must arrive bearing a marker; ONTO
verifies the marker, it does not go shovel an unmarked pile.

NOT a truth certifier. ONTO grades ATTESTATION (how well a source is grounded), never TRUTH. A maximally
attested source can still be fraudulent (see sec7). The output is an epistemic state, never a verdict "true".

NOT a replacement for peer review / journals. ONTO is one more INDEPENDENT, TRANSPARENT ruler on top of the
existing system -- a faster immune signal -- explicitly inside the jar, never claiming the view from outside.

verification = discipline. The whole product is: assert exactly to the grounding, mark where grounding ends,
and terminate trust OUTSIDE the system (external registry / convergence), never in ONTO's own assertion.

--------------------------------------------------------------------------------
## 1 TWO AXES -- never collapse

Provenance and grade are orthogonal. Collapsing them is the classic error (a clean-DOI ID-journal polemic is
provenance-clean but grade-poor; admitting it as gold = contamination).

- AXIS P (provenance verifiability) : does the marker resolve, match, and stay clean? Sets the FLOOR (admit?).
- AXIS G (evidence grade, R5)       : RCT > observational > review > preprint > opinion; venue integrity.
                                       Sets the WEIGHT (how much, once admitted).

Tier ladder (sec3) is AXIS P. Grade modulates within an admitted tier; it cannot lift a failed provenance.

--------------------------------------------------------------------------------
## 2 LAYERS -- cheap->expensive, deterministic->inference. Each states what it CANNOT do.

L1 EXISTENCE  [deterministic, external, ZERO model]
   check  : DOI resolves (Crossref) AND metadata (title/author/year) matches the cited claim.
   owner  : the external registry, NOT ONTO. ONTO never "decides" if a DOI is real -- it asks Crossref.
   catches: fabricated / recycled / mis-attributed DOIs (the entire agent-fabrication genre).
   CANNOT : tell whether the resolved paper is correct, honest, or relevant.
   falsifier: feed a known-fabricated DOI; if L1 does not reject, L1 is broken.

L2 STATUS     [deterministic, external]
   check  : Retraction Watch + Crossref Crossmark -> retracted / expression-of-concern / clean.
   catches: already-flagged fraud (Verfaillie, cheetah, Wakefield post-2010, Schon post-2003, Dias post-2022).
   CANNOT : catch fraud BEFORE the community flags it. Inherits the retraction LAG (3y / 12y / 22y) honestly.
   falsifier: feed a known-retracted DOI; if L2 marks it clean, L2 is broken.

L3 FRAUD-SIGNAL  [heuristic, ADVISORY, never assertive]
   check  : PubPeer presence, image/data-duplication flags, replication-failure literature, venue integrity
            (predatory / fringe / paper-mill), undisclosed-COI signals.
   effect : RAISES a risk score -> LOWERS tier. NEVER asserts "fraud" (cannot verify underlying data).
   note   : the ONLY layer with any chance at fresh fraud, and it is probabilistic. A single signal has a
            NON-ZERO false-positive rate (honest data reuse, calibration data, template figures). No signal
            is "zero FPR" -- any claim of zero FPR is itself an ungrounded assertion. Signals corroborate;
            none convicts alone (see L5).
   CANNOT : prove fraud, or detect fraud whose only trace is in the physical specimen/data (not in the text).
   falsifier: state, per signal, its FPR on a control set of same-year same-venue clean papers. No number = drop it.

L4 CONTENT-BIND  [inference -- ONTO's organ; the lab NLI ladder]
   check  : does the real, clean source actually support the SPECIFIC claim (entail), or is it misbound?
   owner  : ONTO. This is the one irreplaceable contribution: not "is the DOI real" (Crossref) but "does the
            real paper say what the claim says". == the contradiction/binding veto built on the E-ladder.
   gate   : runs ONLY on sources that passed L1 (existence). The model NEVER touches an unverified-existence
            DOI -> it cannot "rescue" a fake with a confident bind. (VOID-by-construction discipline.)
   CANNOT : tell whether the bound, supporting source is itself TRUE -- only that the binding holds.
   falsifier: a source that does NOT entail the claim must land T1 (bind-unchecked), not T0.

L5 CORROBORATION  [the truth-approximation -- cross-source independence]
   check  : does the claim hold across sources that are PROVENANCE- and METHOD-independent? Weighted by their
            own tiers. INDEPENDENT REPLICATION / re-derivation, explicitly discounting mere CITATION.
   why    : a single source -- however clean -- is never truth. Fresh fraud = the lone claim no independent
            party reproduces. This is the only layer that catches what every source-level check misses
            (the L3/Q1 single-signal hole and the Q3 single-signed-chain hole both close here).
   guard  : citation count is NOT corroboration. The 4500 citations of the Verfaillie paper amplified the
            fraud, did not catch it. Weight independent reproduction; discount social propagation.
   non-replicable objects (fossils, historical, observational): corroboration = independent PHYSICAL
            re-examination via multiple independent instrument modalities (micro-CT / XRF / UV revealing a
            composite seam), NOT "experts say". (How the cheetah forgery concern actually arose, Deng 2011.)
   CANNOT : manufacture independence where the field cannot reproduce at all -> then state the ceiling, do not
            fake convergence.
   falsifier: a claim resting on one source, or on N non-independent sources, must NOT reach the top tier.

--------------------------------------------------------------------------------
## 3 TIER LADDER (AXIS P -- verifiability of the marker)

T0  VERIFIED PRIMARY        L1 pass + L2 clean + L4 bind holds + L5 corroborated     -> GOLD, load-bearing
T1  VERIFIED, BIND-UNCHECKED L1 pass + L2 clean, L4 bind to THIS claim not established -> GOLD-provisional, cap
T2  RESOLVABLE, GRADE-DEGRADED L1 pass + L2 clean, but AXIS G low (preprint / fringe / ID-venue / EoC)
                              -> weak corroboration only, never sole ground
T3  MARKERLESS / UNVERIFIABLE  no DOI / non-resolving / bare title / pre-DOI / dataset w/o id
                              -> memory / low-tier. NOT "false" -- "ungrounded" (Central Law: flag insufficiency)
T4  FAILED / FABRICATED MARKER L1 fails (non-resolve / mismatch) OR L2 = retracted
                              -> REJECT + log as provenance-fraud. NEGATIVE signal.

ASYMMETRY (load-bearing): T4 < T3. A FABRICATED marker is WORSE than a MISSING one. Absence of provenance is an
honest gap; false provenance is manufactured authority. The gate ranks a fake DOI BELOW a missing DOI.

--------------------------------------------------------------------------------
## 4 HARD BOUNDARIES (non-negotiable)

- ONTO runs the BIND (L4/L5). The registry runs EXISTENCE (L1/L2), deterministically, zero model. Collapsing
  these = ONTO adjudicating provenance from weights = the contaminator wearing our badge.
- GATE BEFORE MODEL. Deterministic L1/L2 run first; only survivors reach the L4 inference. The model cannot
  see an unverified-existence DOI, so cannot rescue a fake.
- TRUST TERMINATES OUTSIDE. Verification ends at an external registry / at independent convergence -- never in
  ONTO's own cache or its own assertion. Self-verification against own belief = laundering.
- MARKERLESS != FALSE. Absent provenance -> tier down (T3), never assert false. Otherwise we lose true
  pre-DOI / observational / historical knowledge = castration.
- NO SINGLE-POINT TRUST. No one signal (L3) and no one signed chain-of-custody convicts or certifies alone;
  convergence (L5) is mandatory at the top tier.

--------------------------------------------------------------------------------
## 5 OVER-PRUNING GUARD (anti-castration)

A strict "raw data + executable code + 3 live replications" gate, applied globally, AMPUTATES the historical
basis: of 10 accepted classics, ~3 pass (Pythagoras, GPS-relativity, Doppler); ~7 fail (Watson-Crick 1953,
Cavendish 1798, Faraday 1831, Rutherford 1911, Mendeleev 1869, Michelson-Morley 1887, Joule 1843) -- analog
data, no executable code, non-reproducible originals. A gate that nukes 300 years of physics is castration,
not discipline.

RULE: the gate sets a FLOOR (admit / tier), it is never a guillotine. Split the streams:
- HISTORICAL BASIS  : accepted-by-convergence-over-time. Admitted at its grade; not re-gated for raw-data/code.
- INCOMING DIGITAL  : full L1-L5, maximum rigor.
Selectivity lives at PER-CLAIM SELECTION (pick the few highest-tier sources for a given claim), not at
corpus deletion. The backing corpus stays broad or the verifier has nothing to bind against.

--------------------------------------------------------------------------------
## 6 SCOPE OF OPERATION

- INTAKE-TRIGGERED (on claims that enter) or a ONE-TIME DOMAIN SLICE (e.g. abiogenesis). NOT a 180M global
  crawl. We do not excavate the pile; the turnstile runs on what enters.
- corpus reality (verified): Crossref ~180M records, DataCite ~100M. A retraction-aware layer removes ~tens of
  thousands (RW ~50-60K, ~0.03%) -- it keeps ~99.97%, it does NOT cull to thousands. "Survivor = 1-5K" is only
  valid as a per-DOMAIN grade-A primary set, NOT as the surviving fraction of all DOIs.

--------------------------------------------------------------------------------
## 7 HONEST CEILING (state it, do not paper over)

- Fresh fraud is INVISIBLE pre-retraction when the lie is in the data/specimen, not the text. No L1-L4 check
  catches a fabricated-but-not-yet-flagged paper (cheetah clean 3y, Verfaillie 22y). L3 only raises risk; L5
  only catches it once independent reproduction fails.
- We GRADE ATTESTATION, NEVER TRUTH. T0 = "maximally attested", not "true".
- The buck for ultimate truth stops at INDEPENDENT REPLICATION / CONVERGENCE, which is outside any single
  document -- and even that has a failure mode (coordinated fraud, herd citation). We mark the ceiling; we do
  not claim to close it. Claiming to close it = the grandiosity / god-view error we exist to refuse.

--------------------------------------------------------------------------------
## 8 SELF-TESTS (the only honest validation -- the gate must catch its own failure mode)

FIXTURE A -- provenance (one Crossref/RW lookup each):
  10.1038/nature00807            (mis-attributed; real Verfaillie = nature00870)  -> EXPECT T4 (L1 mismatch)
  10.1073/pnas.0811124106        (fabricated; real cheetah = pnas.0810435106)     -> EXPECT T4 (L1 non-resolve)
  10.1073/pnas.0810435106        (real Christiansen & Mazak 2009)                 -> EXPECT L1 pass; L2 RETRACTED -> T4-retracted
  10.1038/nature00870            (real Verfaillie; retracted 2024)                -> EXPECT L1 pass; L2 RETRACTED -> T4-retracted
  Axe 2010 (BIO-Complexity)      (clean DOI possible, ID venue)                   -> EXPECT L1 pass; AXIS G low -> T2

FIXTURE B -- over-pruning: run the strict raw-data+code+3-replication gate on the 10 classics (sec5).
  EXPECT >= 7 fail the strict gate -> proves the gate must tier (sec5), not delete. If it deletes them, it is castration.

FIXTURE C -- self-application: run the gate on this spec's own marked claims. Any fabricated/unsupported marker
  it emits must be self-rejected at L1. A verifier whose own output its own gate would not catch is not a verifier.

--------------------------------------------------------------------------------
## 9 BUILD ORDER (next, if greenlit)

1. L1/L2 deterministic adapter: Crossref resolve + metadata-match + RW/Crossmark status. Bounded O(claims).
   Self-test on FIXTURE A. (No model. Cheap. Kills the entire fabrication genre on its own.)
2. Wire L4 to the lab content-bind organ (the E-ladder verifier) -- same machine, intake scale.
3. L5 corroboration-independence: the hard research layer. Ties to lab multi-source consensus (E37->E39 line).
   Define independence operationally; discount citation; handle non-replicable via physical re-examination.
4. Tiering + over-pruning split (sec3/sec5). Per-claim selection, broad backing corpus.

Falsifiable at every layer. ONTO does the bind; the registry does existence; trust terminates outside;
markerless tiers down, fabricated is rejected below missing.
