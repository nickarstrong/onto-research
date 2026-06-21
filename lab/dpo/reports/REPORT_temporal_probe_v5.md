# REPORT_temporal_probe_v5.md -- temporal channel V6 probe (live Wikidata/Wikipedia)

session : LABA, TEMPORAL CHANNEL V6
date    : 2026-06-21
type    : CONCEPT (design + probe, no build). Probe RUN live (Tommy-side), trace-grounded.
          D4 source-predates-derivative logic ALSO unit-tested offline (--selftest) before the run.
binds   : REPORT_temporal_probe_v4.md sec3 (D4 named) + sec5 (V6 design candidates) ;
          REPORT_temporal_probe_v1.md (D1/D2/D3) ; ARCHITECTURE_master sec2
          ("flag on CLEAN = castration; false-flag <= 0.10").
inputs  : eval/o0/o0_s4_enriched.jsonl (frozen) ; eval/o0/o0_s4_founder_labels.jsonl (v199) ; +4 traps.
oracle  : Wikidata wbsearchentities + EntityData (date predicates + P31) + FULL Wikipedia plaintext
          (action=query prop=extracts explaintext). Pure stdlib HTTP, local.
probe   : o0_temporal_probe_v5.py ; trace o0_temporal_probe_v5_trace.json.
status  : PROBE DONE -- banked. OVERALL = PASS on all pre-registered bars. D4 (same-title WORK-decoy
          refute) is CLOSED, trace-grounded (NOT vacuous). Refute-restraint now demonstrated on BOTH
          decoy classes the set exercises: person-name (D3, heldout_03) AND source-predates-derivative
          work (D4, TRAP_unconfirm). First OVERALL PASS in the temporal lineage with the load-bearing
          R15/D4 bar met.

## 0  ONE NUMBER
OVERALL = PASS (P1 AND P2 AND P3). The load-bearing bar -- TRAP_unconfirm -> ABSTAIN (D4 closed) --
holds, and is GROUNDED: the refute path reached the decoy Q261281 (the 1961 Solaris source novel),
read its P577=1961 and P571=1960, and D4 actively BLOCKED both (1961<1968, 1960<1968,
work_decoy_source_predates_derivative) -> no refute_hit -> ABSTAIN. This is restraint, not a vacuous
resolve-miss. All four falsifiers clear.

## 1  CLAIM VERDICTS (trace-grounded)
| id            | label | year      | verdict | trace reason                                                    |
|---------------|-------|-----------|---------|-----------------------------------------------------------------|
| heldout_03    | DIRTY | 1925      | REFUTE  | **P2.** Work "A Relation Between Distance and Radial Velocity..." -> Q24563361 P577=1929 != 1925. claim NOT derivative -> D4 inactive (D4block None). refute_anchor.qid = Q24563361. Person "Edwin Hubble" D3-blocked. |
| heldout_09    | CLEAN | 1887      | CONFIRM | **P1.** "Heinrich Hertz" -> Q41257 full text: "In 1887, he made observations of the photoelectric effect..." -- "observ" (P575/P585, claim class) same-sentence. |
| heldout_14    | CLEAN | 1900      | N/A     | 1900 in abstract -> not load-bearing. Correct.                  |
| heldout_16    | CLEAN | 1847      | CONFIRM | **P1.** "Ignaz Semmelweis" -> Q59736 full text: "In 1847, he proposed hand washing..." -- "propos" same-sentence. |
| heldout_18    | DIRTY | 1950,2014 | ABSTAIN | **P2.** 1950 abstract-covered (N/A). 2014: no admissible same-sentence verb -> no CONFIRM; not derivative + no work-decoy -> no REFUTE. |
| TRAP_python   | CLEAN | 1991      | CONFIRM | Python Q28865 P571=1991 (WD predicate). Not refuted.            |
| TRAP_titanic  | CLEAN | 1997      | CONFIRM | Titanic Q44578 P577=1997 (WD predicate). Not refuted.          |
| TRAP_norefute | CLEAN | 1910      | CONFIRM | Whitehead Q183372 full text 1910 + Principia Q62092387 WD-pred. Not refuted. |
| TRAP_unconfirm| CLEAN | 1968      | ABSTAIN | **P3 / D4 load-bearing.** "Solaris" -> Q261281 (1961 source NOVEL) P577=1961 + P571=1960, BOTH predate the claim's 1968 adaptation; claim carries "adaptation/version" (derivative) -> D4 BLOCKED both -> refute_hit empty -> ABSTAIN. Persons Boris Nirenburg (Q4321483) + Stanislaw Lem (Q2042129) D3-blocked. refute_blocked_D4 = [{P577,1961},{P571,1960}]. |

## 2  WHAT IS BANKED (true, trace-verified)
- **D4 CLOSED -- the V6 target, grounded.** Same-title WORK-decoy refute is restrained. With V5's
  same-sentence CONFIRM already removing the short-circuit, TRAP_unconfirm reaches the refute path;
  D4 now intercepts it: a refute may anchor on a same-title work ONLY if the claim is NOT a
  derivative whose resolved work PREDATES the claim year. "Solaris" -> the 1961 source novel ->
  blocked -> ABSTAIN. The block is exercised on a real resolve (Q261281 found, years read), so the
  PASS is non-vacuous (contrast v207 vacuous-fa, v209 narrow-P3).
- **Refute-restraint now demonstrated on BOTH decoy classes the set has:**
  - person-name same-label decoy: heldout_03 (Hubble person Q54281574 D3-blocked; refute anchored on
    the WORK Q24563361, the 1929 paper). D3.
  - source-predates-derivative work decoy: TRAP_unconfirm (1961 novel blocked). D4.
- **P2 preserved -- D4 does NOT over-block a true refute.** heldout_03 carries no derivative marker
  -> D4 inactive (D4block None) -> refute fires on Q24563361 P577=1929. F-D4-overblock clear.
- **Frozen confirm path byte-identical to V5 and intact.** P1 held: 16 + 09 both CONFIRM
  same-sentence (09 via Hertz full text "In 1887, he made observations"; 16 via Semmelweis "In 1847,
  he proposed"). 8/8 frozen functions (confirm_in_text, resolve_subject, entity_data, D2, D3, ...)
  md5-identical to o0_temporal_probe_v4.py. D4 is a refute-branch-only addition.
- **Offline selftest 7/7 (no network):** 3 frozen confirm-regression (16 CONFIRM, unconfirm ABSTAIN,
  control 2024 CONFIRM) + 4 D4 units (derivative TRUE on unconfirm, FALSE on 03, source<claim block,
  03 refute-path-open). Passed Tommy-side before the live run.

## 3  MECHANISM (D4, V6)
- **Chosen: 5(b) work-side restraint, operationalized as SOURCE-PREDATES-DERIVATIVE.**
  Refute branch only: if the claim sentence carries a derivative marker
  (adaptation/adapted/version/remake/reboot/based-on/translation/cover-of) AND the resolved
  same-title work's refuting year < claim year -> that work is the likely SOURCE/sibling, not the
  claim's event-subject -> BLOCK refute (ABSTAIN). Precision-first: blocking a refute never castrates
  a CLEAN; it only forgoes an ADVISORY refute (ONTO priority safety > capability).
- **Literal 5(b) (token-overlap, ABSTAIN on overlap 0) was FALSIFIED at design-time** -- same pattern
  as v4's literal sec-5 fix falsified on the frozen trace pre-run. The claim CITES its own source
  ("Stanislaw Lem's novel titled Solaris"), so any description of the Lem novel necessarily shares
  {novel, lem} -> overlap > 0 -> would NOT block. Token-overlap cannot separate a claim from the
  source it names; the derivative-framing + predates signal can.
- **5(c) positive-disambig is structurally dead on this trap:** the true 1968 TV work is absent/thin
  in Wikidata (trap built that way), so no same-year sibling exists to find -> (c) cannot block.
- **5(a) literal predicate-class match does not separate:** both the novel's date and a TV release
  sit on P577 -> no type separation at the predicate level. (D4's predates-rule is the (a)/(b) hybrid
  the report gestured at, realized cleanly.)

## 4  R15 -- refute-restraint now CLOSED for the set's decoy classes
The V2-V5 gap was that refute-restraint was evidenced only by heldout_03's person-decoy rejection
(D3); the work-decoy case (D4) was first exposed UNSAFE in V5 (REFUTE on a CLEAN). V6 closes it:
TRAP_unconfirm now ABSTAINs via an active D4 block on the confirmed-wrong-year source novel. So
refute-restraint is demonstrated on BOTH same-label decoy classes present (person D3 + source-work
D4). R15 for the tested classes is met; what remains is the UNTESTED class (D5, sec 5) and the
denominator (sec 7), not the restraint logic.

## 5  DESIGN CONSEQUENCE / RESIDUAL (for a future V7, NOT opened)
- **Residual D5 (flagged, NOT in V6 traps): LATER-dated same-title sibling decoy.** The predates-rule
  covers a SOURCE that predates the claim's derivative (novel -> adaptation). It does NOT cover a
  same-title sibling dated LATER than the claim's work (e.g. claim about a 1972 film, bare title
  resolves to a 2002 remake, 2002 > 1972). That case would still false-refute. Untested here; a V7
  trap (later-sibling) + a symmetric "claim-year sits between two same-title siblings -> ABSTAIN"
  rule would close it. Lower priority: REFUTE is non-gating, and the source->derivative direction is
  the common decoy.
- FROZEN (closed, carry byte-identical): CONFIRM same-sentence + predicate-class + header-strip +
  word-boundary (D1''), D2 (person-dominant resolve), D3 (person-name refute block), D4
  (source-predates-derivative work restraint).

## 6  GATE ROLE (precision-first, unchanged priority)
- CONFIRM: same-sentence sound, D1'' closed (frozen from V5). NOT yet promoted to absorb-enabler --
  promotion needs broader validation + a real denominator (sec 7). Bankable as
  "same-sentence sound".
- REFUTE: restraint now demonstrated on person (D3) AND source-predates-work (D4) decoys; no CLEAN
  false-refute on this set. STILL advisory / non-gating: (i) D5 sibling class untested, (ii) no real
  denominator. Promotion to a gate output is a future decision, not this session's.

## 7  DENOMINATOR (R15, unchanged)
S4-frozen G3 >= 0.20 stays dead (max 0.150; a sound CONFIRM adds heldout_16 -> 2/20 = 0.100). Real G3
yield = Founder-owned held-out RE-CUT, not this channel's gate. (Parallel decision still open.)

## 8  FALSIFIER STATUS
- F-regress (16 or 09 ABSTAIN under frozen confirm): clear (both CONFIRM live).
- F-D3 (03 anchor != Q24563361): clear (anchor = Q24563361).
- F-D4' (TRAP_unconfirm REFUTED): clear (ABSTAIN; D4 blocked Q261281 1961+1960).
- F-D4-overblock (D4 blocked 03's true refute): clear (03 REFUTE fired; D4 inactive on non-derivative).

## 9  NEXT PLANE (named, NOT opened)
Two open threads, Founder to route:
- (A) CONFIRM/REFUTE PROMOTION + DENOMINATOR: take CONFIRM (same-sentence sound) + REFUTE (D3+D4
  restrained) to a real G3 denominator via a Founder held-out RE-CUT; decide gating vs advisory.
- (B) V7 RESIDUAL D5: later-dated same-title sibling refute restraint (symmetric to D4).
Recommendation (engineer): (A) first -- the channel's confirm/refute logic is now bar-clean on the
probe set; the blocking question is whether it lifts a REAL yield denominator. D5 is a non-gating
edge until REFUTE is promoted.

---
*REPORT_temporal_probe_v5 - 2026-06-21 - OVERALL PASS. D4 (same-title WORK-decoy refute) CLOSED,
trace-grounded: TRAP_unconfirm -> ABSTAIN via an active block on Q261281 (1961 source novel, P577=1961
+ P571=1960 both predate the claim's 1968 adaptation; derivative marker present). Mechanism = 5(b)
work-side restraint as SOURCE-PREDATES-DERIVATIVE; literal token-overlap 5(b) falsified at design-time
(claim cites its own source). Refute-restraint now demonstrated on BOTH decoy classes (person D3 +
source-work D4); P1 16+09 CONFIRM held (frozen confirm path byte-identical to V5); 03 REFUTE@Q24563361
preserved (D4 not over-blocking). All 4 falsifiers clear. Residual D5 (later-dated sibling) flagged,
not in traps. CONFIRM/REFUTE still advisory pending a real denominator. Next: (A) promotion +
denominator RE-CUT [recommended] or (B) V7 D5. Trigger "LABA, TEMPORAL CHANNEL V7" (D5) or
"LABA, DENOMINATOR RECUT" (A).*
