# REPORT -- HELD-OUT ff RE-SATURATION RE-MEASURE (v264)

- session type: TYPE B (Analysis) + one live run. No build, no re-design, no fix.
- substrate: HEAD ad84df5 ; o0_temporal_evidence.py verify_specific seam AST-hash c6eafcdb (L128) ; offline gate GREEN.
- spend: held-out claims_blind_ev.jsonl (N=48) -> claims_blind_ev_temporal_v264.jsonl. ONE run. CONSUMED + TERMINAL.
- ground truth: sealed_labels_heldout.jsonl (Founder labels) = 30 CLEAN / 18 DIRTY (all dirty_class=specifics).
- date: 2026-06-24.

## SEALED QUESTION (PREREG_AMENDMENT_v3 sec B, do NOT move)
Do TRUE bare quantities on EMPTY abstracts survive (rescued by topic-anchored live oracle) keeping ff
acceptable -- OR does the widened extractor re-saturate ff to DIRTY?
Decision rule: ff acceptable AND fabrications read DIRTY -> proceed HEADROOM v4. ff re-saturates
(TRUE quantities mass-DIRTY) -> back to CONCEPT (hard-set-scoped number class vs crossref class).

## RESULT (confusion: ground-truth x verifier scope verdict)
    gt=CLEAN -> CLEAN    6
    gt=CLEAN -> DIRTY   24   (false-fire)
    gt=DIRTY -> DIRTY   18
    gt=DIRTY -> CLEAN    0

    ff_all  (GT-CLEAN -> DIRTY)              = 24/30 = 0.800
    ff_bq   (GT-CLEAN bare-quantity -> DIRTY) =  9/9  = 1.000
    fab recall (GT-DIRTY -> DIRTY)            = 18/18 = 1.000
    DIRTY precision                          = 18/42 = 0.429
    live oracle CONFIRM tokens in whole set  =  2/48 items carry any CONFIRM

## ROOT CAUSE (grounded, read-only -- not a fix)
1. _NUMBER branch 4 `(?<![\w-])\d+(?:\.\d+)?` matches 4-digit YEARS as bare integers
   (verified: '... 1856 and 1864' -> ['1856','1864'] ; 'confirmed in 1785' -> ['1785']).
   No year-range exclusion. Years flow into extract_numbers -> the non-year-specific gate ->
   reason `unverified_non_year_specific:'1856'` -> DIRTY whenever the live oracle cannot confirm.
   => DOMINANT ff driver: 14 of 24 false-fires are YEAR-ONLY items (no bare quantity present).
   Bare quantities are a subset, not the whole re-saturation.
2. Topic-anchored live oracle is near-dead on empty-abstract crossref evidence: only 2/48 items
   carry any CONFIRM token. The §5 mitigant ("oracle confirms a true bare quantity on empty abstract")
   is FALSIFIED for this evidence class.

## HONESTY NOTE (fab recall 18/18 is NON-DISCRIMINATIVE)
At ff_all=0.80 the verifier marks DIRTY almost every claim carrying any unconfirmed specific.
The 18/18 fabrication catch is the SAME blanket over-rejection, not fabrication detection.
The decision rule's first conjunct ("fabrications read DIRTY") is technically true but vacuous:
the gate is non-selective. This is exactly why branch 2 is correct -- there is no valid reading
under which this verifier is "fixed".

## VERDICT (sealed, branch 2)
ff RE-SATURATED (TRUE quantities mass-DIRTY: ff_bq=1.000, ff_all=0.800). -> BACK TO CONCEPT.
HEADROOM v4 REMOVED from active queue: it was conditioned-on-verifier-fixed; condition not met.

## CONCEPT SCOPE FOR NEXT SESSION (sharper than "number vs crossref")
C-1. _NUMBER branch 4 must not capture year-range integers (or per_year tokens must be subtracted
     before the non-year-specific gate). FALSIFIER: after the edit, year-only GT-CLEAN items stop
     being false-fires (target: the 14 year-only FFs clear; fab recall on GT-DIRTY year items holds).
C-2. live-confirm path is dead on empty-abstract crossref (2/48). number-class needs hard-set scope,
     NOT oracle rescue. FALSIFIER: a number-class scoping that keeps fab catch on GT-DIRTY bare-qty
     (11/11 currently caught) while releasing TRUE bare-qty GT-CLEAN (9/9 currently FF).

## ANOMALY (R12, 1 flag -- separate surface, not this plane)
held2_08_1: GT-CLEAN, driver `year_refuted:1785` (Coulomb's law, 1785 is historically correct).
Year oracle FALSE-REFUTE on a true year. Distinct from the number-class question. Log; do not fix here.

## SPEND ACCOUNTING
held-out claims_blind_ev.jsonl is CONSUMED + TERMINAL. ff cannot be re-measured on this set.
Any post-CONCEPT-fix re-measure REQUIRES a freshly generated held-out set (gen_heldout.py + Founder labels).
