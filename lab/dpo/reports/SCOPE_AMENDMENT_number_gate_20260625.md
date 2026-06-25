# SCOPE_AMENDMENT -- number gate (per_specific) scope boundary

- session: v272 (CONCEPT / doctrine)
- date: 2026-06-25
- HEAD at write: db09dbe (read-only over committed WORKSHEET_dirty_leak_11_20260625.md)
- type: doctrine doc (no build, no oracle, no gen, no code-edit)
- grounding: v269 / v271 BINDING learnings (verdict ladder, leak-11 routing CLOSED)

---

## 1 SCOPE BOUNDARY (the amendment)

The number gate (`per_specific`) operates on **non-year numeric tokens only**.
Year tokens are routed to a **separate channel** (`per_year`); they are NOT in the
number gate's class.

Structural facts (from v269, BINDING):
- `per_specific = {}` by design on this held-out surface.
- `E = 0` -- the number extractor did not regress.
- The dirty-leak observed in v268 is NOT a number-extractor regression.

Therefore the number gate's job is narrow and was met: false-fire elimination
(v268: 0/31 GT-CLEAN false-fires). It is NOT a general "specific-dirt" catcher.

---

## 2 THE 5 S-ROWS ARE OUT-OF-CLASS FOR THE NUMBER GATE

All five S-rows carry **non-numeric** dirt. None is a number. The number gate
returning non-REFUTE on these is **correct behaviour, not a miss**.

| row        | dirt class  | token                                   | note |
|------------|-------------|-----------------------------------------|------|
| held2_01_1 | title       | "Sir"                                   | Newton knighted 1705, claim says 1687 -- anachronistic title. R7 OK: token present, non-numeric. |
| held2_07_1 | name        | "John Hooke"                            | vs pair 07_0 "Robert" -- name specific |
| held2_13_0 | attribution | "Joule"                                 | vs topic Carnot / 2nd-law -- misattribution |
| held2_19_0 | venue       | "Geological Society of London"          | vs pair 19_1 -- venue specific |
| held2_19_1 | venue       | "British Association..."                | vs pair 19_0 -- venue specific |

**Ruling:** S-rows are OUT-OF-CLASS for the number gate. The v268 "leak" on S-rows
is a SCOPE artifact, not a regression. The v268 false-fire elimination (0/31) stands;
catching S-rows was never the number gate's job.

TALLY (v271 FINAL, on-disk verified): E=0 | Y=3 | S=5 | CLEAN=3 | R=0. leak-set 11 -> 8.

---

## 3 THE FORK: non-numeric specific dirt is currently UNCAUGHT

Non-numeric specific dirt (name / title / venue / attribution) is caught by no
existing gate. Two doctrines were on the table:

- **(A) ROADMAP an entity/relation gate.** A separate verifier for non-numeric
  specifics (oracle lookup on entity / attribution / venue). Closes the gap.
  Cost: new oracle surface, new false-fire risk, new verify seam.

- **(B) EXPLICITLY DEFER.** Document the gap; narrow the verifier's honest claim to
  "numeric + temporal discipline". Cheaper, honest, narrower. Gap is a known,
  accepted, dated limitation -- not a silent drop.

R3 / R2 (single line): (A) closes a real R7 blind spot -- a self-learning entity
with a name/attribution hole is weaker; **but** an entity/relation oracle
(coreference, claim-specific relation lookup) is a categorically heavier surface
with unknown, likely high, false-fire, and the numeric channel is not yet even
integrated into the pool (Y-channel catch-rate + POOL HYGIENE quarantine owed).

---

## 4 RULING: (B) scoped-and-dated DEFER

Decision taken by Claude as engineer under explicit founder delegation
("Ty inzhener idem", 2026-06-25). Founder owns the right to re-open.

Narrow the verifier's honest claim to **"numeric + temporal discipline"**. Record the
entity/relation gap as a **known / accepted / dated** limitation. NOT a silent drop.

Basis:
1. Entity surface is an order of magnitude heavier than numeric/temporal -- the
   number gate took six sessions to reach 0/31. A new oracle seam now = third
   open front.
2. The temporal channel itself is not closed (Y=3 dirty-year catch-rate owed;
   POOL HYGIENE ABSTAIN quarantine owed). Two fronts before a third.
3. S = 5/48 is a small surface; building an oracle seam for it now is premature.
4. Honest scope-narrowing is R-aligned: R2/R7 cover claims about capability.
   Asserting an unbuilt catch = overclaim. A narrow, honest claim > a broad,
   undemonstrated one.

NORTH STAR check: discipline is externalised -> the verifier MUST be honestly
bounded. Narrow-and-honest beats wide-and-undemonstrated.

**Re-open condition (dated trigger, not "never"):** un-defer (A) to ROADMAP only
AFTER (a) Y-channel dirty-year catch-rate is closed AND (b) POOL HYGIENE quarantine
migration is done. Not before; not automatic.

---

## 5 ADJACENT / OWED (referenced, not actioned this session)

- **GT-CORRECTION (BINDING, owed):** sealed_labels marks 06_1 / 07_0 / 23_1
  DIRTY/specifics but no specific in text -> correct DIRTY->CLEAN x3 at next
  gen/label pass. Until then out of leak denominator.
- **Y-channel catch-rate (NEXT+1, TYPE C/B):** per_year ABSTAIN on KNOWN-dirty year
  (20_1 1837, 21_0 1796, 21_1 1789). Hermetic offline YEAR falsifier owed.
- **POOL HYGIENE (BINDING):** C-2 ABSTAIN quarantine bucket migration. Precondition
  for conditioned run. Unblocked now leak-11 is closed.
- **WATCH-G (BINDING, gen fix owed):** ESC codes (\u001b[...K, \u001b[ND) live inside
  stored claim text (held2_01_1 / 07_0 / 23_1, raw dump v271). Strip at SOURCE in
  next gen -- tokenization/oracle corruption risk.

---

## 6 STATUS

- Scope-amendment doctrine: WRITTEN.
- S-rows declared OUT-OF-CLASS for the number gate: DONE (table, sec 2).
- Roadmap-vs-deferred recommendation: STATED and RULED -> (B) scoped-and-dated defer (sec 4).
- Founder delegation recorded.

STAGE v272 CONCEPT scope-amendment: CLOSED on commit of this doc.

---
*v272 -- 2026-06-25 -- CONCEPT scope-amendment. Number gate = non-year numeric only;
5 S-rows (01_1 title, 07_1 name, 13_0 attribution, 19_0/19_1 venue) declared OUT-OF-CLASS.
Fork ruled (B) scoped-and-dated defer under founder delegation. Re-open gated on
Y-channel + POOL HYGIENE closure. From WORKSHEET_dirty_leak_11_20260625.md (db09dbe).*
