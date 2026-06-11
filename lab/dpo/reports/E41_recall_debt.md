# E41 -- RECALL-DEBT CHARACTERIZATION

Scope    : substrate-scoping over already-committed artifacts (E40 FLOOR_BOUND, f15d4d6).
Type     : TYPE B analysis. NO new probe, NO data run, NO contract.
Premise  : the cross-source statistic D_lambda = (n_con - lambda*n_ent)/|S| GRADUATED as a robust
           spoof-reject organ (E40: fa_op 0.0333, |R|=86, region wide/stable, fragility falsified).
           Reject rule (op): D_lambda >= tau -> reject; accept otherwise. best_op lambda=1.0, tau=0.67.
           heldout recall B2 is FLOOR-PINNED at 27/30 = 0.9000 across the entire feasible region by 3
           golds the statistic structurally cannot touch. This document characterizes those 3, per class,
           BEFORE any recall organ is built.
Readout  : eval/_local/E37_boundset.json -- 6 fields:
           item_id, n_con, n_ent, S_size, true_class, pre_demoted.  (con_share = n_con/S_size, derived.)

------------------------------------------------------------------------------------------------------
## DEBT CLASS 1 -- NOAUTH (ho_g18, ho_g25)  | x2

(a) FAILING MECHANISM (readout fields).
    pre_demoted = true for both. These items are rejected by the source-resolution PRE-FILTER, upstream
    of and BEFORE D_lambda is computed. They never reach the cross-source statistic; the reject is owned
    by a different stage. The wide |R|=86 feasible region of D_lambda is therefore irrelevant to them --
    no (lambda, tau) point can re-admit a pre_demoted item, because the demotion fires earlier.
    Readout records ONLY the bool pre_demoted=true. n_con/n_ent/S_size are present but verdict-inert here.

(b) MINIMAL RESCUE SIGNAL (no spoof admission).
    A source-resolution channel that separates "noauth but authority recoverable" (source resolvable via a
    secondary identity path -- alias / mirror / registrar) from "noauth and genuinely unauthoritative."
    Re-admit ONLY golds whose authority is independently recoverable; never an item that is noauth by
    fabrication. This is a false-reject REDUCER, not a relaxation of the spoof gate.

(c) SUBSTRATE GAP -> emit_E37_readout.py MUST BE EXTENDED.
    The 6-field readout collapses the WHY of demotion to a single bool. The source-resolution detail that
    would drive a rescue is NOT carried. Extension fields (minimal):
      - demote_reason   : enum {noauth, stale, conflict, ...}  -- exposes WHY pre_demoted fired.
      - source_resolved : bool -- was an authoritative source found via a secondary identity path.
    At minimum one field exposing the demotion reason; current readout provably cannot drive the rescue.

(d) SPOOF-LEAK RISK -- HIGH.
    A spoof can fabricate a plausible secondary-identity path. The channel MUST reject-by-default and lift
    only on a verifiable authority signal, else it reopens the exact hole pre_demotion closed. This is a
    SEPARATE organ (E42), a distinct reject-stage with its own gate -- not a tweak to D_lambda.

------------------------------------------------------------------------------------------------------
## DEBT CLASS 2 -- PURE-CONSENSUS (ho_g12)  | x1

(a) FAILING MECHANISM (readout fields).
    n_con=2, n_ent=0, S_size=2  ->  con_share = 2/2 = 1.0.
    D_lambda = (n_con - lambda*n_ent)/|S| = (2 - lambda*0)/2 = 1.0  for ALL lambda.
    op tau=0.67  ->  D=1.0 >= 0.67  ->  REJECT.
    The entail term (n_ent) is the ONLY gold-rescue lever inside D_lambda (subtracting entailers pulls a
    gold below tau). Here n_ent=0: nothing to subtract. ho_g12 is byte-identical on (con, ent) to a
    high-consensus spoof. Inseparable on the statistic's own axes.

(b) MINIMAL RESCUE SIGNAL (no spoof admission).
    A signal ORTHOGONAL to con/ent counts. Binding was EXHAUSTED (E36) -> NOT binding. Candidate =
    source-identity / provenance: do the 2 consensus sources resolve to DISTINCT independent authoritative
    origins (genuine corroboration) vs. one origin echoed (spoof signature: consensus manufactured from a
    single source)? Lever = count of independent origins among the consensus set.

(c) SUBSTRATE GAP -> emit_E37_readout.py MUST BE EXTENDED.
    Readout carries S_size (cardinality) but no origin-distinctness. con/ent counts alone PROVABLY cannot
    separate ho_g12 from a spoof (D=1.0 identical). Extension field (minimal):
      - n_distinct_origins : count of independent authoritative origins in the bound set.
        (or origin_independence : ratio in [0,1].)

(d) SPOOF-LEAK RISK -- MEDIUM.
    A sophisticated spoof can present multiple distinct-LOOKING origins (sock-puppet / mirror sources).
    Origin-distinctness reduces but does not eliminate leak; it needs the same authority verification that
    sits under the noauth channel. Without that, n_distinct_origins is itself spoofable.

------------------------------------------------------------------------------------------------------
## CONVERGENCE NOTE

Both debt classes route to the SAME missing substrate axis: source-identity / provenance resolution.
  - NOAUTH        needs "why demoted + is authority recoverable".
  - PURE-CONSENSUS needs "are the consensus origins independent + authoritative".
A single emit_E37 extension exposing source-resolution (demote_reason / source_resolved) + origin
independence (n_distinct_origins) could feed BOTH -> ONE readout re-freeze, not two. The recall organ, if
built, is one source-identity substrate with two consumers (noauth channel + origin-independence sub-organ).

------------------------------------------------------------------------------------------------------
## FOUNDER FORK (recommendation, not A/B/C hand-back)

OPTION A -- CHASE RECALL.
  Extend emit_E37_readout.py with the source-resolution fields (re-freeze readout, new gate); design the
  noauth-channel organ E42 as a separate reject-stage (gold-false-reject reducer, NOT a spoof statistic);
  fold pure-consensus as a second sub-organ on origin-independence.

OPTION B -- INTEGRATE + CAP.
  Freeze the statistic at (fa 0.0333, B2 0.90, |R|=86 stable); trigger the parked rho 0.95-vs-0.50
  reconcile; scale to full-GOLD; write a recall-cap caveat into the keystone; defer the recall organ.

REASONING.
  - The statistic graduated CLEAN and robust (E40). The 3-gold debt is STRUCTURAL and owned by a DIFFERENT
    organ class -- not a defect in what just graduated. Building a second organ now to chase it inverts the
    dependency order.
  - The cap is 27/30 = 0.9000 on a 30-row heldout fixture. Best-case recall recovery is bounded (+3 -> 1.00)
    and BOTH rescues require building + validating a NEW source-identity substrate and a NEW organ with its
    own spoof-leak gate (multi-rung: emit extension -> re-freeze -> E42 design -> run -> gate). Non-trivial
    cost against a 3-item debt.
  - Whether the 0.90 cap is STRUCTURAL or a 30-row-fixture artifact is UNKNOWN at this scale. Full-GOLD scale
    is the cheap test that answers it -- and it is gated behind INTEGRATE, not behind CHASE RECALL.
  - NORTH STAR = an autonomous grounded verifier. The spoof-reject organ at fa=0.0333 is integration-ready
    NOW; integrating it unblocks the actual next structural decision (rho 0.95-vs-0.50 reconcile) and surfaces
    the cap-at-scale signal.

RECOMMENDED DEFAULT: OPTION B (INTEGRATE + CAP).
  Freeze the statistic, write the recall-cap caveat into the keystone, trigger the rho reconcile, scale to
  full-GOLD. Re-open the recall debt as E42 ONLY IF the 0.90 cap PERSISTS at full-GOLD scale.

FALSIFIER (R6) for this recommendation:
  If full-GOLD scale shows the noauth + pure-consensus debt class is LARGE (recall cap drops well below 0.90),
  the recall organ is mandatory-now, not deferred -- and OPTION A was the right fork. The integrate step is
  cheap to reverse on that signal; a recall organ built prematurely on a 3-item fixture is not. Decision is
  reversible in the recommended direction; not reversible in the other.

------------------------------------------------------------------------------------------------------
## PASS/FAIL (self-check, R17)
  [x] per-class failing mechanism, readout fields quoted (Class 1: pre_demoted bool; Class 2: n_con/n_ent/S_size)
  [x] per-class minimal rescue signal stated, no spoof admission
  [x] per-class substrate-gap named (emit_E37 extension fields: demote_reason/source_resolved, n_distinct_origins)
  [x] per-class spoof-leak risk graded (HIGH / MEDIUM)
  [x] one founder fork stated with recommended default + falsifier
  NO new probe, NO data run, NO contract emitted.
