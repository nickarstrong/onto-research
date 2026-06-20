# CONCEPT_temporal_channel_v2.md -- out-of-band date oracle, V2 design + pre-registered probe

session : LABA, TEMPORAL CHANNEL V2
date    : 2026-06-21
type    : CONCEPT (design + probe pre-registration, NO build)
supersedes : CONCEPT_temporal_channel_v1.md (carries v1 bars forward, re-cuts REFUTE + CONFIRM)
binds   : REPORT_temporal_probe_v0.md (v0 trace: F3 live, CONFIRM viable) ;
          ARCHITECTURE_master sec2 ("flag on CLEAN = castration; false-flag <= 0.10") ;
          pack v208 sec2 next-step ; ROADMAP_substrate_to_entity sec0b (enough-for-stage).
oracle  : Wikidata wbsearchentities + EntityData date predicates
          (P577 publication, P571 inception, P575 discovery, P585 point-in-time, P580 start) ;
          Wikipedia FULL article plaintext (action=query prop=extracts explaintext) -- NOT REST summary.
status  : DESIGN DONE. Probe pre-registered, NOT YET RUN (live Wikipedia/Wikidata = Tommy-side; this
          container's network allowlist excludes wikipedia.org/wikidata.org).

## 0  ONE NUMBER (what this session decides)
Whether the F3-fix (entity-anchored REFUTE) survives a CLEAN same-label trap.
PASS on probe -> REFUTE promotable from advisory to absorb-blocking gate (next session = BUILD).
FAIL -> REFUTE stays advisory; CONFIRM still ships if P1 holds.

## 1  WHAT V0 PROVED / BROKE (no re-prove -- banked)
- CONFIRM path VIABLE: heldout_16 (1847 Semmelweis) confirmed via Wikipedia text where abstracts
  and Wikidata date predicates were both empty. Breaks v207 "claim-granularity year-coverage ceiling".
- REFUTE outcome-correct on heldout_03 (real paper P577=1929 != claimed 1925) -- but on a SOUND anchor.
- F3 LIVE (load-bearing defect): v0 rule = "REFUTE if ANY structured year != claim_year on ANY
  same-label candidate". It misfires:
    - heldout_18: claimed event-year 2014 linked to capitalized token "Alan Turing" -> unrelated
      1983 book-about-Turing -> spurious REFUTE. The single-word real subject "Cleverbot" was never
      captured, so the year was never anchored to its true subject.
    - heldout_03: junk title-fragments injected 1988/2000 into REFUTE_YEARS alongside correct 1929.
  Consequence: a CLEAN claim whose subject shares a label with any incidental dated work would be
  FALSE-REFUTED = castration. REFUTE NOT shippable as gate until entity-anchored.
- 09 ABSTAIN was summary-depth only (1887/Hertz lives in the article BODY, not the REST summary lead).
  Fixable, not structural.

## 2  V2 DESIGN

### 2.1  CONFIRM oracle (closes heldout_09)
- PRIMARY: full Wikipedia article plaintext for the resolved subject entity
  (`action=query&prop=extracts&explaintext=1&titles=<title>`), NOT the REST summary.
- SECONDARY: Wikidata structured date predicates on the resolved subject entity.
- CONFIRM iff claim_year co-locates with the claim's EVENT ANCHOR (the predicate keyword:
  "discovered" / "published" / "introduced" / "demonstrated" ...) within a bounded window
  (same sentence or adjacent sentence in article text), OR claim_year == a structured WD date
  predicate matched to the claim's event type.
- Co-location window (not "anywhere in body") guards against incidental year mentions in a long article.
- ABSTAIN if neither path locates the year near the anchor. Never auto-CONFIRM on bare year presence.

### 2.2  REFUTE entity-anchoring (closes F3)
Three guards, all required before REFUTE may fire:
- (a) SUBJECT EXTRACTION captures the claim's grammatical/semantic subject entity, INCLUDING
      single-token capitalized entities ("Cleverbot", "Python"). Drop generic multiword
      title-fragments ("Radial Velocity Among Extra", "Subsequent") -- folds tail-debt v208 sec6
      (cap inscope_pn, drop generic fragments).
- (b) SUBJECT RESOLUTION: resolve THAT subject in Wikidata (wbsearchentities), disambiguate
      same-label candidates by description/type match to the claim domain. Pick a confident single
      entity or ABSTAIN.
- (c) REFUTE iff the RESOLVED subject entity, on a date-of-the-CLAIMED-EVENT relation
      (event-type-matched predicate, not any predicate), carries a CONFIRMED different year.
      Never REFUTE on an incidental same-label dated work that is not the resolved subject.
- DISAMBIGUATION GUARD (precision-dominates): multiple same-label candidates with no confident
      type-match pick -> ABSTAIN, never REFUTE. Ambiguity never castrates.

### 2.3  Gate role (this version)
- CONFIRM = absorb-enabling. Recovers covered-but-uncovered-in-abstract event-years (16 class).
- REFUTE = ADVISORY/logged this version. Promote to absorb-blocking ONLY after probe shows F3-fix
  holds (clean same-label trap NOT false-refuted) AND DIRTY same-label still caught (18 still
  refuted-or-abstained, never via the wrong entity).
- Production fa_live safety still rests on upstream name/place binding (independently rejects 03, 18).
  Temporal REFUTE is additive precision, not the sole guard.

## 3  PRE-REGISTERED PROBE (o0_temporal_probe_v1)
Inputs: 5 frozen S4 SUPPORTS (03, 09, 14, 16, 18) + 2 NEW clean same-label traps.
No GPU, no Ollama, no embed. Live Wikidata + Wikipedia only. ~7 claims. LOCAL (Tommy-side).

### 3.1  Trap claims (CLEAN; subject shares a label with a different dated work)
- TRAP-A: "Python is a high-level programming language first released in 1991."
    subject = "Python" (single-word). Same-label dated decoys: Monty Python's Flying Circus (TV, 1969);
    other "Python" works. Correct subject (programming language) inception 1991.
    Expected V2: resolve Python->language entity -> CONFIRM (or ABSTAIN). REFUTE = F3 still live = FAIL.
- TRAP-B: "Titanic is a film directed by James Cameron, released in 1997."
    subject = "Titanic" (single-word). Same-label dated decoy: RMS Titanic (sank 1912 / launched 1911).
    Correct subject (1997 film) publication 1997.
    Expected V2: resolve Titanic->film entity -> CONFIRM. REFUTE on 1912/1911 = F3 still live = FAIL.
- Trap ground-truth years (1991, 1997) = settled public facts; the probe oracle re-checks them live
  on the resolved entity, so CONFIRM on the correct entity is self-grounding. (web_search unavailable
  this session -- noted; oracle is the live check.)
- NOTE (E15 guard): traps are DESIGN FIXTURES with public ground truth, NOT model-proposed claims
  needing Founder adjudication. If Founder disputes either trap's CLEAN status, swap before run.

### 3.2  Pre-registered bars
- P1 (CONFIRM, HARD): heldout_16 (1847) AND heldout_09 (1887) BOTH CONFIRM via full article text.
    heldout_14 stays N/A (1900 already covered in abstract).
- P2 (REFUTE anchored, HARD): heldout_03 REFUTE on resolved subject (real paper, P577=1929 != 1925);
    heldout_18 REFUTE on resolved subject (Cleverbot/Goostman event) OR ABSTAIN if subject
    unresolvable -- but NOT refuted via the 1983 Turing book.
- P3 (F3-FIX, HARD -- the load-bearing falsifier): TRAP-A and TRAP-B BOTH not refuted
    (CONFIRM or ABSTAIN). Any REFUTE on a clean trap = F3 still live.

### 3.3  Falsifiers
- F3' (load-bearing): clean same-label trap REFUTED -> entity-anchoring failed -> REFUTE not promotable.
- F2' : 09 still ABSTAINs on FULL article text -> CONFIRM oracle insufficient even at full-text depth
        -> structural, escalate (not a depth fix).
- F4 (new, REFUTE-too-weak): subject resolution picks the wrong entity on a DIRTY claim and MISSES a
        real refute (18 not caught by any path) -> REFUTE under-powered, distinct from F3 over-power.

### 3.4  Outcome -> recommendation (single)
- ALL HARD pass -> REFUTE promotable to absorb-blocking gate. Next session = BUILD (wire entity-anchored
    REFUTE + full-text CONFIRM into accumulator, default CONFIRM ON / REFUTE ON, re-run S4 frozen).
- P3 fails -> REFUTE stays ADVISORY; CONFIRM ships if P1 holds. Re-cut entity resolver, re-probe.
- P1 fails -> CONFIRM oracle insufficient -> escalate oracle (not a V2 patch).

## 4  DENOMINATOR (R15, unchanged)
S4-frozen G3>=0.20 stays denominator-dead (max 0.150; CONFIRM adds 16 -> 2/20 = 0.100 < 0.20).
Real G3 yield = Founder-owned held-out RE-CUT, NOT this channel's gate. This channel's gate is
fa_live-safety (REFUTE never false-fires on CLEAN) + CONFIRM-recovery, not G3.

## 5  COMPUTE ROUTING
Probe = live Wikidata + Wikipedia, ~7 claims, no GPU / no Ollama / no embed, finishes in ~a couple min.
-> LOCAL on Tommy's machine. (Claude container network allowlist excludes wikipedia.org/wikidata.org
-> cannot run here; Claude writes o0_temporal_probe_v1.py, Tommy runs, uploads result.)

## 6  NEXT STEP (named, NOT opened here)
Write o0_temporal_probe_v1.py faithfully against the v0 probe + frozen S4 inputs (subject-extraction
+ entity-resolution + full-text CONFIRM + 2 traps), Tommy runs LOCAL, uploads -> integrate -> verdict
against bars sec3.2. Then BUILD or re-probe per sec3.4.

---
*CONCEPT_temporal_channel_v2 - 2026-06-21 - CONFIRM via full Wikipedia article text (closes 09);
REFUTE entity-anchored (resolve claim subject incl. single-word, refute only on the resolved subject's
event-date relation, ambiguity->ABSTAIN) to close F3; probe pre-registers 2 CLEAN same-label traps
(Python/1991, Titanic/1997) as the F3 falsifier. REFUTE advisory until probe P3 passes.*
