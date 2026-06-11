# SPEC -- Source Provenance Verifier (DOI layer) v1

date    : 2026-06-12
plane   : SURFACE / architecture (NOT the lab NLI ladder; references it for the content-bind + corroboration layers)
home    : onto-research/reports (dateable provenance + ties to lab organ) -- promote to onto-standard when stable
status  : v1. v0 (d9c33937eb1b2fe6f30977f2514e00af) + AUDIT (46ee16f1c8e718a94cf8e1ab857b7733, a602c41)
          findings D1-D6 folded. Resolution log = sec10. Falsifiers per layer. Build order in sec9.
ceiling : OPERATING CEILING TODAY = T1 (D3). T0 not awardable until L5 independence is operationally
          defined (sec9 step3). Stated as present state, not implicit.

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
A G-FLOOR also gates the TOP tier from the grade side (sec3, T0): provenance alone cannot back-door axis
collapse by lifting a low-grade source to load-bearing.

--------------------------------------------------------------------------------
## 2 LAYERS -- cheap->expensive, deterministic->inference. Each states what it CANNOT do.

L1 EXISTENCE  [deterministic, external, ZERO model]
   check  : DOI resolves (Crossref) AND metadata (title/author/year) matches the cited claim.
   owner  : the external registry, NOT ONTO. ONTO never "decides" if a DOI is real -- it asks Crossref.
   catches: fabricated / recycled / mis-attributed DOIs (the entire agent-fabrication genre).
   CANNOT : tell whether the resolved paper is correct, honest, or relevant.
   falsifier: feed a known-fabricated DOI; if L1 does not reject, L1 is broken.

L2 STATUS     [deterministic, external]  [D1 folded]
   check  : retraction / expression-of-concern / clean status, queried against a NAMED registry.
   registry (named, D1) : primary = Crossref Crossmark; coverage-augmented by Retraction Watch DB (RWD).
   catches: already-flagged fraud (Verfaillie, cheetah, Wakefield post-2010, Schon post-2003, Dias post-2022).
   CEILING 1 -- LAG : cannot catch fraud BEFORE the community flags it. Inherits retraction lag (3y/12y/22y).
   CEILING 2 -- COVERAGE (D1, separate from lag) : retraction indexing is INCONSISTENT across registries.
            A 4-source study found only ~3% of retracted publications consistently indexed across
            Crossref / RWD / Scopus / WoS; counts diverge -- RWD 39,301 vs Crossref 14,745
            (Taylor & Francis, 10.1080/08989621.2025.2484555, 2025). A single-registry L2 misses the
            MAJORITY of known retractions. Therefore L2 queries Crossmark AND RWD, and OWNS the residual
            coverage gap as a stated ceiling -- it does not claim completeness.
   CANNOT : guarantee a "clean" verdict is globally clean (coverage gap) or timely (lag).
   falsifier (lag)      : feed a known-retracted DOI; if L2 marks it clean, L2 is broken.
   falsifier (coverage) : feed a DOI retracted in RWD but absent from Crossmark; if L2 returns clean
                          (i.e. RWD not consulted), the coverage gap is real and L2 is broken.

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

L4 CONTENT-BIND  [inference -- ONTO's organ; the lab NLI ladder]  [-> SPEC_verifier_v1, FROZEN]
   check  : does the real, clean source actually support the SPECIFIC claim (entail), or is it misbound?
   owner  : ONTO. The one irreplaceable contribution: not "is the DOI real" (Crossref) but "does the
            real paper say what the claim says". == the FROZEN contradiction/binding veto (SPEC_verifier_v1):
            D_lambda = (n_con - n_ent)/|S| ; reject iff (pre_demoted OR D_lambda >= 0.67) ; fa_op 0.0333 /
            recall 0.9000 on full-GOLD E25b.
   gate   : runs ONLY on sources that passed L1 (existence). The model NEVER touches an unverified-existence
            DOI -> it cannot "rescue" a fake with a confident bind. (VOID-by-construction discipline.)
   CANNOT : tell whether the bound, supporting source is itself TRUE -- only that the binding holds.
   falsifier: a source that does NOT entail the claim must land T1 (bind-unchecked), not T0.

L5 CORROBORATION  [the truth-approximation -- cross-source independence]
   check  : does the claim hold across sources that are PROVENANCE- and METHOD-independent? Weighted by their
            own tiers. INDEPENDENT REPLICATION / re-derivation, explicitly discounting mere CITATION.
   why    : a single source -- however clean -- is never truth. Fresh fraud = the lone claim no independent
            party reproduces. This is the only layer that catches what every source-level check misses.
   guard  : citation count is NOT corroboration. The ~4500 citations of the Verfaillie paper amplified the
            fraud, did not catch it. Weight independent reproduction; discount social propagation.
   non-replicable objects (fossils, historical, observational): corroboration = independent PHYSICAL
            re-examination via multiple independent instrument modalities (micro-CT / XRF / UV revealing a
            composite seam), NOT "experts say". (How the cheetah forgery concern actually arose, Deng 2011.)
   CANNOT : manufacture independence where the field cannot reproduce at all -> then state the ceiling, do not
            fake convergence.
   STATUS (D3) : "independence" is NOT yet operationally defined (sec9 step3 = TODO). Consequence made
            explicit: the L5 predicate has no test today -> T0 is UNREACHABLE -> OPERATING CEILING = T1.
   falsifier: a claim resting on one source, or on N non-independent sources, must NOT reach the top tier.

--------------------------------------------------------------------------------
## 3 TIER LADDER (AXIS P -- verifiability of the marker)

T0  VERIFIED PRIMARY        L1 pass + L2 clean + L4 bind holds + L5 corroborated + AXIS-G >= floor
                            -> GOLD, load-bearing.  [D2 G-floor + D3 ceiling apply]
T1  VERIFIED, BIND-UNCHECKED L1 pass + L2 clean, L4 bind to THIS claim not established -> GOLD-provisional, cap.
                            *** CURRENT OPERATING CEILING (D3): until L5 independence is operationally
                            defined, no source can be awarded above T1. ***
T2  RESOLVABLE, GRADE-DEGRADED L1 pass + L2 clean, but AXIS G low (preprint / fringe / ID-venue / EoC)
                            -> weak corroboration only, never sole ground.
T3  MARKERLESS / UNVERIFIABLE  no DOI / non-resolving / bare title / pre-DOI / dataset w/o id
                            -> memory / low-tier. NOT "false" -- "ungrounded" (Central Law: flag insufficiency).
T4  FAILED / FABRICATED MARKER L1 fails (non-resolve / mismatch) OR L2 = retracted
                            -> REJECT + log as provenance-fraud. NEGATIVE signal.

G-FLOOR ON T0 (D2, load-bearing): T0 additionally REQUIRES AXIS G >= observational/peer-reviewed. A
clean-DOI preprint that merely corroborates (L5) does NOT reach T0 on provenance + corroboration alone;
it caps at T1/T2 regardless of corroboration. This closes the tier-side re-entry of the axis collapse
that sec1 forbids from the provenance side.

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
- corpus reality:
    Crossref ~180M records (VERIFIED: "nearly 180 million records", 2025 public data file, crossref.org 2025-03).
    DataCite ~100M records (UNVERIFIED -- not independently confirmed this pass; primary check = tail debt). [D6]
  A retraction-aware layer removes ~tens of thousands: Retraction Watch DB = 61,645 records (RW DB, Mar 2025)
  ~= 0.034% of the Crossref corpus. [D5: was "~50-60K", stale-low; magnitude + 0.03% fraction hold.] It keeps
  ~99.97%; it does NOT cull to thousands. "Survivor = 1-5K" is only valid as a per-DOMAIN grade-A primary set,
  NOT as the surviving fraction of all DOIs.

--------------------------------------------------------------------------------
## 7 HONEST CEILING (state it, do not paper over)

- Fresh fraud is INVISIBLE pre-retraction when the lie is in the data/specimen, not the text. No L1-L4 check
  catches a fabricated-but-not-yet-flagged paper (cheetah clean ~3y, Verfaillie ~22y). L3 only raises risk; L5
  only catches it once independent reproduction fails.
- We GRADE ATTESTATION, NEVER TRUTH. T0 = "maximally attested", not "true".
- OPERATING CEILING = T1 (D3): T0 is not awardable today because L5 independence has no operational test yet.
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

FIXTURE C -- self-application [D4: frozen oracle, was a slogan].
  Run the gate on this spec's own marked claims. Frozen worksheet below is the enumerated oracle (each row:
  spec claim -> expected -> actual primary source + date -> verdict). md5-gated; REGENERATE on every spec edit.
  A verifier whose own output its own gate would not catch is not a verifier.

  | # | spec claim                                  | expected      | actual (source, date)                                              | verdict |
  |---|---------------------------------------------|---------------|--------------------------------------------------------------------|---------|
  | 1 | Verfaillie real DOI = 10.1038/nature00870   | L1 pass       | Nature 418:41-49 (2002), title matches (nature.com / PubMed 12077603) | PASS |
  | 2 | ...retracted 2024, ~22y, ~4500 cites        | L2 retracted  | Retracted 2024-06; most-cited retracted paper, ~4500 WoS cites (Retraction Watch 2024-06-18) | PASS |
  | 3 | cheetah real DOI = 10.1073/pnas.0810435106  | L1 pass       | PNAS 106(2):512-515 (2009) (pnas.org)                              | PASS    |
  | 4 | ...clean ~3y, Deng 2011 forgery, Mazak ack  | L2 retracted  | Retracted 2012-08-20 (~3y); Deng 2011 forgery, Mazak 2012 ack (Retraction Watch 2012-08-20; researchgate 271842876) | PASS |
  | 5 | Crossref ~180M records                      | number holds  | "nearly 180 million records", 2025 public data file (crossref.org 2025-03) | PASS |
  | 6 | Retraction Watch ~61.6K, ~0.03% of corpus   | number holds  | 61,645 records (RW DB, 2025-03); 61.6K/180M = 0.034%               | PASS    |
  | 7 | DataCite ~100M records                      | number holds  | NOT independently confirmed this pass                              | UNVERIFIED |

  Notes: Fixture A inputs (nature00807, pnas.0811124106) are DELIBERATELY-WRONG test inputs (T4 on
  mismatch/non-resolve), not audited as factual claims. Row 7 is the tail debt for D6 (verify DataCite or
  keep "unverified"). Row 6 updated per D5 (was "~50-60K").

--------------------------------------------------------------------------------
## 9 BUILD ORDER (next, if greenlit)

0. [D4, already done] Freeze sec8 Fixture C worksheet as the oracle. Closed -- zero cost.
1. L1/L2 deterministic adapter: Crossref resolve + metadata-match + RW/Crossmark status, with L2 querying
   Crossmark AND RWD and reporting the coverage gap [D1]. Bounded O(claims). Self-test on FIXTURE A.
   (No model. Cheap. Kills the entire fabrication genre on its own.)
2. Wire L4 to the FROZEN lab content-bind organ (SPEC_verifier_v1) -- same machine, intake scale.
3. L5 corroboration-independence: the hard research layer. Ties to lab multi-source consensus (E37->E39 line).
   Define independence operationally [D3 -- THIS is what lifts the ceiling off T1]; discount citation; handle
   non-replicable via physical re-examination. Until done, ceiling stays T1.
4. Tiering + over-pruning split (sec3/sec5), with the T0 G-floor [D2] enforced. Per-claim selection, broad
   backing corpus.

Falsifiable at every layer. ONTO does the bind; the registry does existence; trust terminates outside;
markerless tiers down, fabricated is rejected below missing.

--------------------------------------------------------------------------------
## 10 RESOLUTION LOG -- AUDIT D1-D6 (a602c41) folded into v1

D1  L2 coverage failure-mode (not only lag)        ACCEPT.  L2 names registry (Crossmark + RWD), owns
    [defect, sourced]                                       index-coverage as a SEPARATE ceiling beside lag;
                                                            coverage falsifier added (sec2-L2). Source folded
                                                            (10.1080/08989621.2025.2484555, 2025).
D2  T0 has no AXIS-G floor -> back-door collapse    ACCEPT.  Explicit G-floor on T0 (>= observational/
    [defect]                                                peer-reviewed); below it caps T1/T2 (sec3).
D3  L5 independence not operationalized; T0 unreach ACCEPT.  Present state made explicit everywhere:
    [defect, R2/R6]                                         OPERATING CEILING = T1 (status line, sec2-L5,
                                                            sec3-T1, sec7). Lifting it = sec9 step3.
D4  Fixture C had no oracle -> VOID-by-construction ACCEPT.  AUDIT sec1 worksheet pasted as frozen Fixture C
    [defect, E23 lesson]                                    oracle (sec8); md5-gated, regenerate on edit.
D5  RW count stale-low (~50-60K) + ungrounded      ACCEPT.  Updated to 61,645 (RW DB, Mar 2025), 0.034%,
    [minor, R1/R4]                                          with source + date (sec6, Fixture C row 6).
D6  "verified" over unverified DataCite            ACCEPT.  DataCite ~100M marked UNVERIFIED (sec6, row 7);
    [minor, R7]                                             primary check = tail debt. Crossref stays VERIFIED.

LOAD-BEARING-CORRECT (AUDIT sec3) kept verbatim, untouched: GATE-BEFORE-MODEL (sec4), ASYMMETRY T4<T3 (sec3),
OVER-PRUNING SPLIT (sec5).

All 6 findings resolved (6 ACCEPT, 0 reject, 0 defer). Facts L1-clean (AUDIT sec1: 6/7 PASS, 1 UNVERIFIED,
0 FAIL). Operating ceiling stated = T1.

v1 -- FOLDED + FROZEN at this rev (regenerate Fixture C on next edit).
