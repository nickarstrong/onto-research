# SCOPE_AMENDMENT -- entity-gate scope + v278 plane re-route

- session: v278 (CONCEPT / doctrine)
- date: 2026-06-25
- HEAD at write: 8c81dea (read-only over canonical pool + held-out surface)
- type: doctrine doc (no build, no oracle, no gen, no code-edit)
- grounding: pack v278 plane (entity-gate re-open, v272 fork B); on-disk read of canonical
  pool (360 verdict rows, md5 755d81c3 post-swap) + held-out entity-dirt surface.
- privacy: held-out topics / dirt-tokens / claim-text are a leak-vector (R15) and are NOT
  reproduced here. Counts + class-split + ruling only. Per-row enumeration stays LOCAL.

---

## 1 ENUMERATED ENTITY-DIRT SURFACE (from disk, not memory)

Pack v278 declared the build surface as "12 no-spec fabricated-specifics + 5 entity-dirt"
(= 17 candidate catch-targets). On-disk read collapses this into three classes.

**Candidate fabricated-specifics ABSTAIN-quarantine set: N = 12.**
- All 12 carry C-2 quarantine `specifics = []` (no extractable specific found).
- Claim-text read confirms the metadata: **11 / 12 carry NO injected fabricated specific**
  -- the claims are generic-correct or factually clean. Their ABSTAIN is CORRECT
  (nothing to refute). The `targeted_weakness = fabricated-specifics` label was set at
  generation but the generator did not materialise a checkable specific.
- **1 / 12 carries a real defect**, which itself splits:
  - attribution / wrong-co-author -> requires external entity fact -> class (iii) oracle-only.
  - arity mismatch (N entities enumerated vs M dates in a "respectively" construction,
    N != M) -> internally checkable -> class (i) offline-formalizable.

**S-class entity-dirt set: N = 5.**
- All 5 are entity / relation facts (title, name, venue, attribution).
- Each needs an external fact to refute -> class (iii) oracle-only.
- Consistent with prior ruling (number-gate SCOPE_AMENDMENT, fork B scoped-and-dated defer).

---

## 2 DERIVATION-REFUTE SURFACE (the v278 build target)

3-way split (v275 boundary doctrine) applied to the 17:

| class | meaning | count |
|-------|---------|-------|
| (i) formalizable -> DERIVATION-REFUTE (offline) | catchable without oracle | **1** |
| (ii)/(iii) contingent -> ORACLE-only | needs external fact | 6 |
| no-target (correct ABSTAIN, no injected defect) | nothing to catch | 11 |

The offline-formalizable surface is **n = 1** (a single structural arity primitive).

---

## 3 FALSIFIER -- PRECONDITION NOT MET

Plane v278 assumed ~17 catch-targets justifying a new entity/relation gate. Disk says:
**1 offline-formalizable / 6 oracle-only / 11 no-target.**

Building a gate against an n=1 offline surface trips two binding constraints:
- **R17 C-check (beautiful-empty):** a gate whose exercised surface is ~empty passes
  vacuously and is non-discriminative.
- **Void-as-measured:** do not execute an (irreversible) build against an absent/unmeasured
  floor. The floor here is measured and is ~empty.

=> **grounded-NO on a blind entity-gate build this session.**

---

## 4 RULING (Founder, 2026-06-25)

Ruling taken under founder delegation. Selections: (1) + (3), arity folded into audit.

1. **v278 plane = GENERATOR AUDIT.** The real signal on disk is a generator defect:
   `targeted_weakness = fabricated-specifics` produced 11/12 specific-free generations.
   The catch-side has almost nothing to catch because the dirt was never injected.
   Root-cause work is on the GENERATOR, not a new catch gate. (Same class as the v271
   GT-mislabel finding: asserted dirty_class with no materialised dirty token.)
2. **arity-primitive FOLDED into the audit** -- a cheap generic structural-consistency
   check (entity/date arity in enumerations), NOT a standalone entity-oracle build.
3. **ENTITY-GATE DEFERRED to horizon.** Re-open is Founder-owned, not automatic.
   S-class entity-dirt + the single wrong-attribution row stay class (iii) ORACLE-only
   (proven PARTIALLY IMPOSSIBLE offline; not forced).

NORTH STAR check: discipline externalised -> verifier stays honestly bounded.
Auditing the generator (where the defect actually is) beats building a gate against a
surface that does not exist.

---

## 5 OWED / CARRY (referenced, not actioned here)

- **GENERATOR AUDIT (next plane, TYPE A/B):** quantify the `fabricated-specifics`
  no-injection rate across the gen surface; fix the generator so the targeted weakness is
  actually materialised. arity-consistency primitive scoped inside this.
- **GT-mislabel parallel (BINDING):** label != injected-defect is a recurring generator
  defect (v271 surface + this surface). Single root cause, audit both.
- **WATCH-G (BINDING):** ESC/ANSI codes inside stored claim text -> strip at SOURCE in
  next gen pass. Same gen surface as the audit.
- **Entity-gate re-open trigger:** Founder-owned; no dated auto-trigger set.

---

## 6 STATUS

- entity-dirt surface enumerated from disk: DONE (sec 1, counts).
- 3-way class-split measured: DONE (sec 2): 1 offline / 6 oracle / 11 no-target.
- falsifier precondition: NOT MET -> grounded-NO on blind entity-gate build (sec 3).
- ruling: (1) generator-audit plane + (3) entity-gate deferred + arity-into-audit (sec 4).
- founder delegation recorded.

STAGE v278 CONCEPT entity-gate scope: CLOSED on commit of this doc.

---
*v278 -- 2026-06-25 -- CONCEPT. Entity-gate surface measured 1 offline / 6 oracle / 11
no-target. Blind entity-gate build = grounded-NO (beautiful-empty + void-as-measured).
Ruled: v278 plane re-routed to GENERATOR AUDIT; arity-primitive folded in; entity-gate
deferred to horizon (Founder-owned re-open). Public-safe abstraction; held-out enumeration
LOCAL only (R15).*
