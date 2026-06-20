# CONCEPT_temporal_channel_v1.md -- Crown granularity +1: out-of-band WHEN-verification

date   : 2026-06-21
plane  : RESEARCH / Phase 4 organism-0 -- Source Crown (B-channel L5) granularity escalation
mode   : CONCEPT (design only -- NO build until concept + probe pre-registered)
binds  : pack v207 (retrieve-side fix DONE -> structural year-coverage ceiling) ;
         REPORT_v206_session.md sec3-5 (specifics_check_v2 defect + next-plane) ;
         CONCEPT_organism0_v1.md sec3 (G1/G2/G3 gate, frozen denominators v199) ;
         STANDARD_grounded_verifier_v1.md (frozen contract -- channel must not violate) ;
         ARCHITECTURE_master sec2 ("patches downgrade/flag, NEVER assert").
status : CONCEPT -- pre-registered probe below; no code, no run this session.

================================================================================
## 0  ONE LINE
Verify WHEN against a date-authoritative source OUT-OF-BAND, because scientific
abstracts report findings, not calendar dates. Year leaves the abstract-conjunction
(where it can never co-occur) and goes to a separate confirm/REFUTE gate. WHO/WHERE
binding stays in the abstract channel, unchanged.

================================================================================
## 1  PROBLEM (the year-coverage gap, banked v207)
specifics_check binds {subject + proper-noun + place + YEAR} as a conjunction that
must co-occur in ONE abstract. v207 proved (retrieve-side fixed, fair pools):
- heldout_16 CLEAN (Semmelweis / 1847 / Vienna): n_alt 7, STILL not confirmed --
  no single abstract co-locates exact year 1847 with the subject.
- The miss is STRUCTURAL: abstracts state what was found / the mechanism, they do
  NOT state the calendar year of the historical event. The year channel is empty
  by construction, not by query defect.
Consequence: every CLEAN claim carrying a correct historical year is false-rejected
on the year leg -> yield floored at 0.050 (only heldout_14, no load-bearing year).

================================================================================
## 2  ROOT CAUSE (channel mismatch)
One source (academic abstracts) is asked to carry two fact-classes it does not
hold uniformly:
- WHAT/WHO/WHERE  -- findings, entities, mechanism, place : abstracts DO carry these.
- WHEN            -- calendar date of the event             : abstracts do NOT.
Forcing WHEN through the abstract conjunction = asking the wrong oracle. Fix is not
more retrieval (exhausted v207) -- it is a SECOND oracle for the WHEN fact-class.

================================================================================
## 3  DESIGN (the temporal channel)
A year-only verifier, parallel to the abstract conjunction, querying a
DATE-AUTHORITATIVE source (structured KB), returning CONFIRM / REFUTE / ABSTAIN.

  claim ---> extract {subject_entity, year(s)}        (reuse specifics extractor)
        ---> resolve subject_entity -> KB id           (entity linking)
        ---> fetch date fact(s) for the relevant relation (publication / discovery /
             point-in-time / inception)
        ---> compare claim_year vs kb_year:
               match  (exact, or within stated tolerance 0)  -> CONFIRM
               mismatch (kb resolves a different year)        -> REFUTE
               kb has no date for this entity/relation        -> ABSTAIN

Source candidates (probe will pick on coverage, not assert now):
- PRIMARY: Wikidata SPARQL -- structured date predicates (P577 publication date,
  P575 time of discovery, P585 point in time, P571 inception). Entity-linked by label.
- FALLBACK: Wikipedia REST summary / DBpedia -- only if Wikidata coverage gaps bind.
Both are out-of-band w.r.t. Crossref/OpenAlex abstracts -- different fact-class, by design.

The channel is a GATE on a year the claim ALREADY carries. It NEVER injects a year,
never proposes one, never asserts. (ARCHITECTURE sec2: patches downgrade/flag, never assert.)

================================================================================
## 4  DECISION LOGIC (combined absorb)
ABSORB iff:
  (A) abstract conjunction confirms {subject + proper-noun(s) + place}   [UNCHANGED]
  AND
  (B) temporal verdict on every load-bearing year in the claim is CONFIRM
      OR the claim carries no load-bearing year.

  | abstract (A) | year present | temporal (B) | verdict  |
  |--------------|--------------|--------------|----------|
  | confirm      | no           | n/a          | ABSORB   |
  | confirm      | yes          | CONFIRM      | ABSORB   |
  | confirm      | yes          | REFUTE       | REJECT   |  <- catches wrong-year DIRTY
  | confirm      | yes          | ABSTAIN      | REJECT   |  <- precision-first (yield cost)
  | fail         | any          | any          | REJECT   |  <- name/place binding holds

Name/place binding is NOT loosened: a wrong NAME (heldout_18 Cleverbot) fails (A)
and is rejected before the temporal channel is consulted. The temporal channel only
ever moves a claim that ALREADY passed WHO/WHERE.

================================================================================
## 5  SAFETY INVARIANTS (must hold; falsified -> channel dead)
- I1 REFUTE-CAPABLE. A wrong year (heldout_03: claim 1925, truth 1929) must resolve
  to a DIFFERENT kb_year and REFUTE. A confirm-only channel that abstains on miss
  would leak heldout_03 -> unacceptable. Refutation is the whole point.
- I2 ABSTAIN -> REJECT. KB silence != confirmation. Same false-reject class as today
  (a yield cost, never a fa_live risk).
- I3 NEVER INJECT. Channel verifies a present year only; cannot supply a missing one.
- I4 BINDING UNCHANGED. WHO/WHERE conjunction on names/places stays exactly as v207.
  fa_live stays HARD <= 0.10. No gate re-tuning, no frozen-bar reopen.

================================================================================
## 6  DENOMINATOR FLAG (R15 -- founder-target reframe, READ THIS)
Pack v207 "next step" target = "lift S4 yield >= 0.20 (HARD)". On the FROZEN S4
held-out set this is STRUCTURALLY UNREACHABLE, independent of the temporal channel:

  S4 = 20 held-out. B2 produced 5 SUPPORTS: {03,18 DIRTY ; 09,14,16 CLEAN}.
  yield = absorbed / 20. DIRTY must be rejected (03 year-refute, 18 name-bind).
  MAX achievable yield = 3/20 = 0.150 (all 3 CLEAN absorbed) < 0.20.

The 0.20 bar is denominator-capped at 0.150 by UPSTREAM B2 supply (5/20 SUPPORTS),
not by the year channel. Validating the temporal channel against S4 G3>=0.20
conflates a CHANNEL fix with a HELD-OUT-SET-SIZE problem. They are different planes.

Therefore:
- This concept's probe is CHANNEL-LEVEL (does WHEN-verification work), NOT S4 G3.
- The S4 G3>=0.20 demonstration needs a LARGER / re-cut held-out set with enough
  year-bearing CLEAN SUPPORTS -- a separate Phase-4 plane (denominator), Founder call.
- Carrying "lift S4 yield >=0.20" as this channel's gate = a stale target that fails
  for ALL channel outcomes. Flagged, not silently overridden. Founder confirms re-cut.

================================================================================
## 7  PRE-REGISTERED PROBE (falsifiable -- frozen BEFORE any run)
Goal: does an out-of-band date oracle close the year-coverage gap -- confirm correct
years, REFUTE a wrong year -- on the exact claims v207 left on the table.

Set (frozen, the 5 S4 B2-SUPPORTS; Founder labels banked v199):
  heldout_09 CLEAN  Maxwell/Hertz 1887   -> expect CONFIRM
  heldout_16 CLEAN  Semmelweis/Vienna 1847 -> expect CONFIRM   (the structural miss)
  heldout_03 DIRTY  Hubble 1925 (truth 1929) -> expect REFUTE
  heldout_18 DIRTY  Cleverbot (wrong name)  -> NOT reached by temporal (abstract-fail)
  heldout_14 CLEAN  (no load-bearing year) -> temporal n/a, abstract-pass unchanged

Procedure (live, NO mock -- E15 measurability invariant):
  1. extract {subject, year} per claim (reuse extractor; tail-debt 9 applied).
  2. resolve subject -> Wikidata QID by label.
  3. fetch date predicate(s) P577/P575/P585/P571 for the QID.
  4. compare -> CONFIRM / REFUTE / ABSTAIN. Log QID, predicate, kb_year per claim.

FROZEN BARS (do NOT tune after seeing results):
  P1 (safety, HARD): heldout_03 -> REFUTE. (wrong year caught out-of-band.)
                     If 03 -> CONFIRM or ABSTAIN-then-absorbed: channel FALSIFIED, stop.
  P2 (capability)  : heldout_16 -> CONFIRM AND heldout_09 -> CONFIRM.
                     Both confirmed = year-coverage gap CLOSED at channel level.
  P3 (coverage honesty): log ABSTAIN rate. ABSTAIN on 16 or 09 = Wikidata coverage
                     gap -> try FALLBACK source once; still ABSTAIN = structural,
                     escalate (concept partially falsified for that fact-subclass).

PASS (channel viable) = P1 AND P2.
PARTIAL = P1 AND (exactly one of 09/16 CONFIRM) -> source-coverage limited, report.
FAIL = NOT P1 (any wrong-year leak) -> temporal-as-gate dead, do not build.

Out-of-band cost note: +1 KB query per year-bearing claim (Wikidata SPARQL,
seconds, LOCAL per STOP-rule sec0.4 -- probe is <=5 claims, not a batch).

================================================================================
## 8  FALSIFIERS (what kills this concept)
- F1: Wikidata REFUTE fails on heldout_03 (returns wrong/absent date) -> the oracle
  cannot catch wrong years -> channel provides no safety, only yield -> dead (I1).
- F2: Wikidata ABSTAINs on BOTH 09 and 16 even with fallback -> the date oracle has
  no better coverage of historical event-years than abstracts -> no yield lift ->
  escalate to a different fact-class source or accept structural ceiling.
- F3: entity-linking ambiguity injects a wrong QID -> wrong kb_year -> false REFUTE
  of a CLEAN claim (castration) -> linking must be precision-first; measure on probe.

================================================================================
## 9  TAIL-DEBT FOLDED IN (pack sec6, scoped to this work)
extract_proper_nouns() emits junk multiword tokens ("Radial Velocity Among Extra",
"Subsequent") -> over-long queries (heldout_03 n_alt 0, heldout_09 n_alt 2). For the
temporal channel the subject-extraction must be CLEAN (entity linking needs a tight
label): cap in-scope proper nouns, drop article-led / generic multiword fragments
before KB resolution. Verified on the probe's QID-resolution log, not assumed.

================================================================================
## 10  OUT OF SCOPE (this session)
- No code. No live run. No accumulator wiring. No S4 re-run.
- No new held-out set cut (that is the Founder denominator call, sec6).
- Build only after this concept + probe accepted and pre-registered (pack rule).

================================================================================
## 11  RECOMMENDATION (one)
Accept the temporal channel as designed (sec3-5) and run the CHANNEL-LEVEL probe
(sec7) -- 5 claims, live Wikidata, local. It answers the only open question cheaply:
can an out-of-band date oracle both REFUTE a wrong year (03) and CONFIRM correct ones
(09, 16). Do NOT carry "lift S4 yield>=0.20" as the gate -- it is denominator-dead at
0.150 (sec6); the S4 demonstration is a separate held-out re-cut, Founder-owned.

---
*CONCEPT_temporal_channel_v1 - 2026-06-21 - design + pre-registered channel probe. Gate = P1 (REFUTE 03, HARD) AND P2 (CONFIRM 09+16). Denominator flag: S4 G3>=0.20 unreachable (ceiling 0.150), probe is channel-level not S4 G3.*
