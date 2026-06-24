# PRE-REG AMENDMENT v3 -- verifier number-gap fix (SEALED)
parent: PRE-REG v2 (5ee4402f)
sealed: 2026-06-24   plane: CONCEPT   HEAD-at-spec: a7f2a42 (unchanged this session)
sealed-by: Tommy (knobs a/b/c)

## A. AUTHORIZATION (knob a) -- SEALED: AUTHORIZED
[x] Editing the FROZEN verify() seam is AUTHORIZED. verify() byte-identity / firewall MD5
    WILL move; new seam hash re-anchored at build (TYPE C, separate session).
    No daemon run / no held-out spend before this amendment is committed.

## B. NUMBER EXTRACTOR (knob b) -- SEALED: regex as-proven, RFC-6409 flag KEPT
SEALED _NUMBER (replaces o0_temporal_evidence.py L65):

    _NUMBER = re.compile(
        r'\b\d{1,3}(?:\.\d+)?\s*%'                 # 1 percent      (OLD, byte-identical)
        r'|\b\d+\s*/\s*\d+\b'                      # 2 fraction a/b (OLD, byte-identical)
        r'|(?<![\w-])\d{1,3}(?:,\d{3})+(?:\.\d+)?' # 3 thousands-comma
        r'|(?<![\w-])\d+(?:\.\d+)?'                # 4 bare int/decimal, not identifier-embedded
    )

  offline-gate result (free, no oracle), proven 2026-06-24:
    HARD bare-quantity specimens : 8/8 extracted   (OLD 0/8)
    TRUE-quantity controls       : 4/4 extracted   (OLD 0/4)
    OLD %/fraction regression    : 3/3 preserved
    identifier-only tokens       : 0/3 (skipped, no false specific)
  KNOWN COST (accepted, KEPT as flag):
    space-separated identifiers (RFC 6409, Boeing 747) over-extract as specifics.
    Not a regex defect; downstream oracle/anchoring gates them. Logged, not blocking.
  ff-RISK (DEFERRED): wide extraction MAY re-saturate held-out crossref ff (true facts on
    empty abstracts -> ABSTAIN). MITIGANT = live non-year oracle CONFIRM. FALSIFIABLE only
    at held-out re-measure -- NOT this session, NOT pre-judged.

## C. ANCHORING SHAPE (knob c) -- SEALED: (A) topic-anchor + no-QID -> DIRTY
[x] (A) verify_specific anchors to the TOPIC referent (hard_topics referent), NOT the
        model in-sentence subject. Resolution:
          1. resolve(TOPIC referent)
          2. no QID              -> ABSTAIN -> DIRTY      (fake referent)
          3. QID + value present -> CONFIRM/CLEAN
          4. QID + value absent  -> DIRTY                 (real referent + fabricated value)
    rationale: only (A) satisfies the decisive falsifier row (true referent + fabricated
    value -> DIRTY); closes the DMSO-laundering path structurally. over-reject risk on legit
    secondary-entity specifics is the ff-cost, deferred to held-out re-measure (knob b).
falsifier (build must demonstrate all three):
    fake referent (NV-12 / Kometa-4 / GLEAM-3)   -> ABSTAIN/DIRTY
    true referent + true value (ethanol 78.4C)   -> CONFIRM/CLEAN
    true referent + fabricated value             -> DIRTY

## D. ORDER (BINDING)
anchoring (C) implemented BEFORE any held-out spend. STEP-1 offline probe gates the
expensive run. widen -> held-out WITHOUT the probe is FORBIDDEN (false "fix works").

## E. DOWNSTREAM GATES (separate sessions, OPEN, not pre-judged)
TYPE C build (sealed B+C) -> STEP-1 offline probe PASS -> held-out ff re-saturation
re-measure -> blind HEADROOM v4. v4 alone establishes whether headroom clears 0.30.
If v4 >= 0.30 -> F1 expressible -> conditioned GATE RUN v3 + TYPE B READ v3.
If v4 < 0.30 OR ff re-saturates -> back to CONCEPT (hard-set-scoped number class vs crossref).