# STRATEGY -- Phase 7: Knowledge Tiering

*Concept lock. Design only -- no build/eval/GPU/net in this doc.*
*Status: CONCEPT CLOSED (pending Founder worth-semantics for T1 set).*
*Home: C:\Projects\onto-research\lab\dpo\reports\STRATEGY_phase7_tiering.md*

---

## 0  GOAL (why this phase exists)

Tiering is the last tier-independence property of the North Star not yet demonstrated.
It sits ABOVE the proven discipline layer (G3): routing decides WHERE a confirmed claim
lives, not WHETHER it is true. Truth stays the sealed external oracle.

North Star restated for this phase: an entity that gets smarter BY CONTENT. Today memory
only accumulates (o0_verdicts, 103 ABSORB on disk). It is never curated. Tiering converts
"disciplined generator with episodic memory" into "entity that curates its own knowledge".

The phase is proven ONLY by the closed loop (D below), not by a clean partition on paper.

---

## 1  TWO ORTHOGONAL AXES (load-bearing idea)

Tiering lives on an axis orthogonal to truth. Truth is sealed (oracle, G3 immutable here).
Phase 7 designs ONLY the value axis.

| | TRUTH axis (sealed) | VALUE axis (NEW, Phase 7) |
|---|---|---|
| decides | CONFIRM / REFUTE / UNRESOLVED | tier + worth |
| source | external oracle | value-features, NOT the verdict |
| cross-cases | -- | CLEAN -> discard (trivium) ; DIRTY -> keep-for-study (caught fabricate = evidence) |

If value-score is derivable from verdict, the axes are fused and tiering is cosmetic.
That is exactly what T1 falsifies.

---

## 2  ROUTER POSITION (firewall)

```
SELECT -> GENERATE -> VERIFY(oracle) -> verdict  [SEALED, untouched]
                                           |
                                           v
                         TIER ROUTER  (reads verdict + value-features)
                                           |
             +-----------------+-----------------+------------------+
             v                 v                 v                  v
       GOLD-queue        permanent-mem     temporary-mem        discard
      (propose-only)      (o0_verdicts)     (TTL->tombstone)    (tombstone)
```

INVARIANT (= Step 6 firewall, extended):
- Router READS the verdict; it NEVER writes back into the verify path.
- Tier-store feeds the PROPOSER only (same role as o0_retrieve + gold_frame).
- verify() pulls byte-for-byte from sealed controller.live_adapters() + the external oracle.
- The router does NOT call verify(). Tiering must not re-enter the verify path.

---

## 3  RECOMMENDATION (single -- concept close)

GOLD write is FROZEN in v1. The autonomous cycle produces ZERO live writes into GOLD.
GOLD-route = a propose-only queue gated by Founder / derivation-verify, NOT an autonomous sink.

Rationale (R3 counter): autonomous GOLD write = belief-set mutates without discipline ->
identity drift + belief-checks-belief risk. A route INTO GOLD also has nowhere to verify
against: writing to GOLD requires the derivation-verify mode (check derivation vs check
reality) which is NOT BUILT and is Founder-owned. The propose-only queue is the only
buildable variant. Cost: it trims the autonomy demonstration -- accepted, because North Star
autonomy != auto-rewriting identity. "Routing decides WHERE a confirmed claim lives" is
proven with propose-only GOLD.

The other three outcomes are LIVE:
- permanent-memory  (o0_verdicts)
- temporary-memory  (TTL -> tombstone on expiry)
- discard           (tombstone, reversible)

All removals (discard + TTL-expiry) = reversible tombstone, never hard-delete. A discarded
claim must be re-promotable in a later cycle.

VALUE PREDICATE (engineering default; verdict does NOT enter except the crossover rule,
which is itself the proof of the axis):

```
REFUTE (DIRTY)        -> permanent / study-bucket   ALWAYS  (caught fabricate = evidence)
weakness_relevant     -> permanent                          (feeds SELECT via self_model)
novel, !relevant      -> temporary  (TTL = N cycles without re-retrieval -> tombstone)
!novel, !relevant     -> discard    (tombstone, reversible)
```

Features: novelty, weakness_relevance, evidential_use. No verdict term in the score itself.

---

## 4  LADDER A -> D (Phase 7 is A-B; the goal is D)

```
A  design  (this doc)      minimal router; axis-independence argued; falsifiers pre-registered
B  BUILD   (TYPE C)        router = post-verdict consumer; GOLD-freeze; gated T1-T5
C  generalize              discipline beyond the DOI family (G3 scope is narrow -- real NS risk)
D  closed loop             curated memory -> SELECT -> cycle-over-cycle gets BETTER. == North Star
```

D is the only rung that proves the phase. A/B are plumbing.

---

## 5  FALSIFIER LADDER (pre-registered, BEFORE any build)

- T1  axis-independence
  On the test set: >=1 CLEAN -> discard AND >=1 DIRTY -> keep-for-study (a caught
  fabricate MUST land in keep). corr(value, verdict) above threshold => FAIL (axes fused).
  Worth ground-truth for this set is Founder-authored (E15). Bar: corr below the doc bar.

- T2  firewall (= G_drift fa_live discipline)
  verify() output is byte-identical with empty vs full tier-store. Any divergence = leak = FAIL.
  Bar = 0.

- T3  reversibility / audit
  count(removed) == count(tombstones). Any removal without a tombstone => FAIL.
  A discarded claim must be re-promotable next cycle (proven by a round-trip test).

- T4  GOLD-freeze
  0 autonomous writes into GOLD. Any write without the Founder / derivation gate => FAIL.

- T5  not-cosmetic (partition non-trivial)
  All three live outcomes non-empty on a representative set (else all-keep / all-discard
  = cosmetic). Bar: each outcome >= 1.

- D-GATE (MAIN -- the phase is proven only here)
  Curated run beats uncurated run on the SAME weakness over N cycles. Metric = downstream
  rate_f (or yield) on the targeted weakness; curated must be strictly lower (rate_f) / higher
  (yield) by the doc bar. If tiering does not improve downstream, it is cosmetic regardless of
  how clean the partition looks. Bar + N set at BUILD pre-registration; placeholder N>=6.

---

## 6  FOUNDER-OWNED (E15 -- must be authored before the test set is built)

Worth ground-truth labels for the T1 set: which records are CLEAN-but-discard, which are
DIRTY-but-keep-for-study. Severity/label authorship = Founder only (E15 rule). Every other
item on the path is an engineering default in this doc.

---

## 7  CARRY (unchanged by this design)

- Truth axis sealed: oracle + G3 immutable here.
- Firewall by construction (Step 6): proposer-only feed; verify byte-for-byte from sealed adapters.
- DISK WINS over memory/pack on paths and counts (o0_verdicts = 103 ABSORB on disk).
- GOLD = beliefs/identity/Central Law; updatable only through the same discipline; axioms immutable.

---

*Phase 7 design. CONCEPT CLOSED pending Founder T1 worth-semantics.*
*Next: "Phase 7 BUILD" (TYPE C) -- implement router against on-disk substrate, gated T1-T5 + D-GATE.*
