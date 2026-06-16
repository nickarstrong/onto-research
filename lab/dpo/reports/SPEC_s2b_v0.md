# SPEC_s2b_v0.md -- ONTO automated supports-judge, S2(b) v0 (FROZEN on accept)

date   : 2026-06-15
plane  : RESEARCH / North-Star loop -- S2(b), the TRUE CORE (NOT L5 predicate ; NOT A-channel self-checkup)
home   : onto-research/reports (dateable priority + reproducibility ; generic-safe, ZERO dois/claim-texts)
status : DRAFT for Founder review -> FREEZE on accept (this doc md5-locked ; falsifier+bars md5-locked
         in the BUILD session BEFORE any predicate byte, R7)
doneness: v0 = medium-rare. The thinnest automated judge that RUNS retrieval-grounded. UNCLEAR is a
          first-class verdict, not a failure -- the judge says less rather than guessing.

## 0 PURPOSE (what it replaces, what it is NOT)
The loop is PROPOSE -> EXTERNAL CHECK -> HUMAN RESIDUAL -> ABSORB (SPEC_loop_e2e_v0.md). v0/v0.1 closed
the CHEAP veto (resolve + retracted, O(citations)) and proved off-plant it is NECESSARY but NOT SUFFICIENT:
on the live frozen substrate's own 30 proposals the dominant failure (11/30, 36.7%) was WRONG-BINDING --
a real, resolving, non-retracted DOI that is NOT the source the claim cites. That class is INVISIBLE to
resolve/retract. S2(b) v0 automates the residual the human/Claude-instance held in v0/v0.1: given a claim
and a DOI that already passed the veto, decide SUPPORTS / NOT / UNCLEAR -- grounded in the FETCHED source,
independent of the proposer, never self-attested.

NOT this spec: the S2(a)/S2(c) veto (built, a39e66f, ships UNCHANGED). NOT L5 independence (parked).
NOT A-channel (closed). S2(b) is a NEW downstream organ, not a gate edit (R7) -- loop_e2e_v0.py is not
touched by this leg.

## 1 INPUTS / OUTPUTS (the contract)
INPUT per item = { claim_text, doi, (optional) star_quote }.
  - claim_text  : the assertion the star makes.
  - doi         : the source the star puts on the table (already veto-passed: resolves, not retracted).
  - star_quote  : optional. Used ONLY to read WHICH source the claim cites (author/year/venue tokens) for
                  the binding leg. NEVER read as evidence of support (self-attestation is not the verdict).
OUTPUT per item = verdict in { SUPPORTS, NOT, UNCLEAR } + leg + reason-code (machine-readable) + the
  fetched-metadata snapshot it judged on (auditability).

## 2 STEP A -- RETRIEVAL (grounded, O(citations))
Fetch the resolved source's Crossref metadata for `doi`: title, container-title (venue), author list,
issued year, abstract (when present). Reuse the live per-doi getter pattern MIRRORED from
run_L5_partI_validate.fetch_crossref (NOT imported -- mirror keeps the judge auditable in one file and
uncoupled from the predicate at runtime). One fetch per doi, on-demand. NEVER O(corpus). The judge reads
THIS fetched text -- not the star_quote, not the substrate's self-report.

## 3 STEP B -- JUDGMENT (two legs, deterministic-first)
B1 BINDING (deterministic, fetch-grounded ; runs first ; catches the dominant off-plant failure with NO
   model in the loop):
   Extract from claim_text (+ star_quote if present) the NAMED source attributes the claim cites:
   author surname(s), cited year, venue/journal token -- ONLY when an explicit, parseable named-source
   token is present. Compare to the fetched metadata:
     - cited author surname absent from fetched author list           -> binding miss
     - cited year vs fetched issued year off by > 1                   -> binding miss
     - cited venue token contradicts fetched container-title          -> binding miss
   A HARD binding miss (the cited source provably != the fetched DOI's source) -> verdict NOT, leg=binding,
   reason=wrong_binding. This is the v0.1 fetch-free-contradiction logic made fetch-GROUNDED and codified.
   If claim_text carries NO parseable named-source token -> binding is INAPPLICABLE (not a miss) -> route
   to B2. (R2: extraction from free text is fuzzy ; v0 only fires binding=NOT on an explicit, parseable
   contradiction -- never on absence of a token. False-binding-NOT is the cardinal error here, guarded by J1.)

B2 SUPPORTS (grounded model-instance ; ONLY on binding survivors):
   A SEPARATE, NON-PROPOSING model instance reads { claim_text, fetched title + abstract } and returns
   SUPPORTS / NOT / UNCLEAR. It is GROUNDED: it sees ONLY the fetched source text, may not introduce facts
   not in it, and returns UNCLEAR honestly when the fetched metadata is insufficient (e.g. no abstract,
   abstract too thin to adjudicate). It is NOT the proposer and NOT the star ; the trust boundary (§5) is
   structural. Its verdict is checkable against the fetched snapshot it was given (recorded in OUTPUT).

## 4 STEP-B MECHANISM -- ONE RECOMMENDATION (not A/B/C)
RECOMMENDED: deterministic BINDING leg (B1) first, grounded model-instance SUPPORTS leg (B2) on survivors.

Grounding (v0.1 evidence, not preference): the survivor population splits 11/19 fetch-free-rejectable
(binding-class: journal-domain + quote-year-vs-DOI-vintage contradictions) vs 8/19 needed-the-read
(genuine supports questions). A two-leg judge matches that split exactly -- the deterministic leg settles
the binding-class majority with ZERO fabrication surface (no model on the part the data says is mechanical),
and the grounded model-instance is spent ONLY on the read-required residual, where a reader is unavoidable.

Rejected alternatives (R3):
  - NLI cross-encoder only : cannot do the binding leg (entailment over abstract!=source-identity check)
    AND Crossref abstracts are absent on a large share of records -> title-only NLI over-UNCLEARs and gives
    no signal on the dominant wrong-binding class. Settles the wrong half.
  - structured field-match only : does binding well, but cannot READ -- the 8/19 read-required residual is
    exactly where it is blind. Under-covers.
  - model-instance only (no deterministic leg) : puts a fabrication-capable judge on the binding-class
    majority that a deterministic check settles for free, adds cost + a failure surface on the easy half,
    and weakens the auditability of the part that must be hardest (the veto-adjacent wrong-binding catch).

## 5 TRUST BOUNDARY (the lines that must not blur)
  - The judge is a SEPARATE actor from the proposer. NEVER the proposing star, never its self-attestation.
  - The judge renders the verdict on the FETCHED source. star_quote informs ONLY "which source is cited"
    (binding), never "is it supported" (the source text alone answers that).
  - O(citations), never O(corpus). One fetch per emitted doi.
  - Standalone: MIRROR the getter, do NOT import the predicate/gate at runtime (auditable in one file).
  - READ-ONLY on the substrate. loop_e2e_v0.py SHIPS UNCHANGED. s2b_v0.py is a new downstream organ (R7).

## 6 FALSIFIER (locked before any predicate byte -- BUILD session, R7)
s2b_falsifier_v0.jsonl carries >=4 planted items per class (every doi grounded LIVE before entry, anti-fab
3.9 ; LOCAL-ONLY, bait-class -- holds real dois/claim-texts, NEVER public). `expect` labels feed ONLY the
falsifier check, NEVER the judge (no oracle leak ; same discipline as loop_e2e_v0 F1-F4):
  J1 bound + backed          : correct source cited, abstract backs the claim   -> expect SUPPORTS.
  J2 wrong-binding           : claim cites source X, doi resolves to unrelated Y -> expect NOT (binding).
  J3 right-bind, wrong-content: correct source cited, source does NOT back claim -> expect NOT (supports).
  J4 insufficient metadata   : correct source, no/thin abstract, unadjudicable   -> expect UNCLEAR.
The falsifier file + the §7 bars are md5-locked BEFORE s2b_v0.py's first predicate byte.

## 7 BARS (pre-registered, frozen ; HARD bars dominate, C1)
  G1 (HARD, no-poison)    : ZERO J2 ever returned SUPPORTS. A wrong-binding accepted as support is the
                            exact failure this organ exists to kill (the 36.7% v0.1 class). tol 0.
  G2 (HARD, no-poison)    : ZERO J3 ever returned SUPPORTS. A right-source/wrong-content accept is the
                            second poison. tol 0.
  G3 (HARD, no-castration): ZERO J1 returned NOT. Flipping a genuine support to NOT is castration
                            (precision-first spine). tol 0.
  G4 (honesty)            : J4 returns UNCLEAR (not a forced SUPPORTS/NOT on insufficient evidence).
                            UNCLEAR is correct, not a miss.
PASS (v0 judge is BUILDABLE+VALID) = G1 & G2 & G3 on the planted falsifier, with G4 held. Selftest must
prove G1-G4 offline (planted fixtures, fake getter) BEFORE any live fetch.

## 8 v0 SCOPE CONTRACT (anti-zadrot ; what is deliberately crude)
REAL in v0     : B1 binding (deterministic, grounded) ; B2 supports (grounded non-proposing instance) ;
                 the 3-valued verdict ; the SUPPORTS/NOT/UNCLEAR ledger leg that supersedes the human S3.
FIXED INPUT    : the 19 v0.1 survivors (worksheet_v01) as the first real run -- a fixed, already-collected
                 set, NOT a live proposer. (v0.1 generation is done ; this session does not regenerate.)
EXPLICIT DEFER : full-text/PDF reading to shrink UNCLEAR (v0 reads abstract only) ; live-substrate proposer ;
                 substrate write-back ; any L5/A-channel work. Do NOT gold-plate these in v0.
WELL-DONE only : the two HARD no-poison bars (G1, G2). A judge that ever green-lights a wrong-binding or a
                 wrong-content cite is worse than none (false confidence ; the substrate learns to slip).

## 9 THE MEASUREMENT (diagnostic, NOT a freeze-gate)
After the judge PASSES the falsifier (§7), run it on the 19 v0.1 survivors and compare the AUTOMATED
disposition to the (ll) grounded fetch-free marks (supports_judgment_v01, LOCAL). Agreement/disagreement
sizes the judge's reliability and is the FIRST measurement of the true core. This is a readout, NOT a bar:
the fetch-free marks are themselves recall-assisted (HONEST GAP), so disagreement is informative, not a
fail. The judge being RETRIEVAL-grounded is expected to RESOLVE some of the 8 UNCLEAR the fetch-free pass
could not -- that delta is the whole point.

## 10 BUILD ORDER (one step/msg next ; TYPE C build then TYPE B run, may split)
  1. write s2b_falsifier_v0.jsonl (J1-J4 planted, dois grounded LIVE ; LOCAL-ONLY) + md5-lock it + the §7
     bars -- BEFORE any predicate byte (R7).
  2. build s2b_v0.py : Step A getter (mirror fetch_crossref) -> B1 binding -> B2 grounded instance ->
     3-valued verdict + reason-codes + fetched-snapshot record. Written-in --selftest (offline, fake getter,
     proves G1-G4) + --netcheck (one live fetch) BEFORE any real run. READ-ONLY ; imports no predicate byte.
  3. --selftest PASS -> --netcheck PASS -> --run on the 19 survivors.
  4. compare automated disposition vs (ll) marks (§9) -> agreement readout (LOCAL).
  5. commit s2b_v0.py + a rate-level report (PUBLIC-SAFE, NO dois/claim-texts) ; falsifier + survivor-run +
     agreement readout LOCAL-ONLY (bait-class / held-out).

trigger : "LABA, S2B v0"
