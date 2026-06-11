# RHO_RECONCILE -- contradiction/cosine independence guard at integration (fork B)

Session : v91 (LAB, rho reconcile). TYPE B analysis/decision. No model run.
Context : fork B = INTEGRATE+CAP locked E41 (26dc4ce). D_lambda graduated E40 as stable wide
          spoof-reject organ (fa_op 0.0333, |R|=86, fragility falsified). Closes the parked
          "rho 0.95-vs-0.50" conflict carried E27->E37.
Keystone at write : STRATEGY_verifier_keystone.md md5 4af08d0ac01540f05be6ac9da8f8736a
          (pre-append; step 3 AUTH-gated, separate -- NOT edited by this doc).

## 1. The two assertions (grounded, R10 -- no invented semantics)

Both guard the SAME quantity: spearman(contradiction, cosine) over 139 authorized pairs.
Both answer ONE question: is the contradiction veto an independent rejection signal, or a
relabel of the bind/cosine score?

A. ENFORCED -- rho >= 0.95, one-sided, VOID trigger.
   Origin   : E26 (report_E26.md:12  "spearman(contradiction,cosine) rho = ... (VOID if >= 0.95)").
   Carried  : byte-identical as DEGENERATE_RHO = 0.95 (PRE_REGISTER_E30.md:64); predicate
              report_E30.md:342  "degenerate = ... rho >= DEGENERATE_RHO  # FROZEN E26 VOID guard
              (0.95, one-sided)".
   Governs  : VOID_DEGENERATE -- trips ONLY on near-perfect positive collinearity (veto == cosine relabel).

B. ADVISORY -- |rho| < 0.50, two-sided, REPORTED ONLY.
   Origin   : PRE_REGISTER_E27 sec4 (PRE_REGISTER_E27.md:79  "veto is NOT a relabel of the
              bind/cosine score. Frozen guard: |rho| < 0.50"). Carried as PREREG_RHO_ADVISORY 0.50
              (PRE_REGISTER_E30.md:65).
   Governs  : nothing enforced -- a stricter two-sided independence comfort-zone, reported only.

Observed : rho = -0.237 (E26/E27, 139 pairs) ; -0.269 (E32+). Passes BOTH.
Discipline: conflict NEVER silently edited -- every E27->E37 report carries the identical CONFLICT
            note (R15 / proto 3.10) deferring reconcile to integration. This is that integration.
Note     : pack v91 sec-0 framing ("acceptance threshold vs recall target") is FALSIFIED -- neither
            rho is an acceptance threshold nor a recall target; both are decorrelation guards on one axis.

## 2. The conflict (precise)

Two independence bars on one correlation, differing in BOTH threshold and sidedness:
  A enforced : one-sided,  rho >= 0.95 -> VOID   (loose; trips only on extreme positive collinearity)
  B advisory : two-sided, |rho| <  0.50          (strict; reported, never enforced)
A min/merge is NOT a valid reconcile: sidedness differs, and sidedness -- not the number -- decides WHAT trips.

## 3. Resolution -- single posture

Integrated organ at fork B = D_lambda = (n_con - lambda*n_ent)/|S| (E39/E40) over the 6-field readout
{item_id, n_con, n_ent, S_size, true_class, pre_demoted}. COSINE IS NOT IN THE INTEGRATED PATH: the
per-candidate cosine/binding organ class is EXHAUSTED (cosine E28, binding E36, con_share E37 -- all
clear fa-gate, none lift the bf-band; pack sec5 "do NOT re-attempt"). cosine retired with that class.

Consequence: a guard on spearman(contradiction, COSINE) tests collinearity with an axis ABSENT from the
integrated organ. Carried as-is it can never fire -> VOID-by-construction (E23 anti-pattern: a guard
that passes because its input is gone, not because the property holds). Neither number survives unchanged.

RESOLVED POSTURE (one bar):
  (i)   Enforced independence guard SURVIVES as the same structural discipline: one-sided, VOID on
        collinearity. Number = 0.95 (enforced lineage). Advisory 0.50 RETIRED -- never a gate, wrong shape (iii).
  (ii)  AXIS RE-TARGETED, cosine -> upstream bind/retrieval: at integration the only live independence
        question is whether D_lambda's spoof-rejection is independent of the upstream bind/retrieval that
        already gates candidates. Guard becomes:
            spearman(D_lambda reject-signal, upstream bind score) >= 0.95 (one-sided) -> VOID.
  (iii) ONE-SIDED is correct: positive collinearity = degeneracy (veto == relabel of bind) = the failure.
        Strong ANTI-correlation = maximal complementarity, NOT failure -> a two-sided bar (retired 0.50)
        would wrongly VOID the best case. Enforced bar must be one-sided.
  (iv)  Axis-PAIRING SPEC'd now, MEASURED at scale: the new spearman is uncomputable until full-GOLD scale
        (v92) yields the joint distribution. NUMBER (0.95, one-sided) fixed pre-data; value read at v92.
        No invented value (R7/R10).

## 4. Recall cap -- explicitly NOT touched by this posture

heldout recall floor-pinned 27/30 = 0.9000 by 3 unrescuable golds: 2 noauth (pre_demoted, upstream
unconditional reject) + 1 pure-consensus (ho_g12: n_ent=0 -> D=1.0 = high-consensus spoof). Recovery
needs a source-identity signal absent from the 6-field readout = a SEPARATE organ class (E42), gated on
the cap persisting at full-GOLD scale. The reconciled rho does NOT chase this debt; the cap is a
documented separate-organ debt carried into integration, not silently inherited.

## 5. Falsifier (v92, full-GOLD scale)

  F1 (rho posture): spearman(D_lambda reject-signal, upstream bind score) >= 0.95 at scale -> D_lambda is
     a relabel of retrieval, not an independent veto -> E40 graduation contaminated -> posture re-opens.
  F2 (recall cap) : heldout recall drops well below 0.90 at scale -> debt class large, not 3 fixed golds
     -> E42 recall organ mandatory (not deferred).
Either trip re-opens integration.

## 6. State

  RESOLVED  : single enforced independence bar = one-sided rho >= 0.95 VOID, axis re-targeted to
              (D_lambda reject-signal, upstream bind score), value measured at v92.
  RETIRED   : advisory |rho| < 0.50 (never enforced; two-sided shape invalid for an enforced bar).
  DISSOLVED : the 0.95-vs-0.50 conflict -- both guarded the retired cosine axis; not a min-merge.
  CARRIED   : recall cap 0.90 as separate-organ (E42) debt; F1/F2 falsifiers to v92.
  STAGED    : keystone append (step 3) -- AUTH-gated, separate; not done in this doc.
