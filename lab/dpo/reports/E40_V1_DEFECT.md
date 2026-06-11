# E40_V1_DEFECT -- V3 noauth-ceiling over-assertion (equality vs upper-bound)

STATUS: DEFECT (caught at v1 RUN, pre-verdict). Supersedes contract v1 -> v2. No verdict was emitted.
PARENT: PRE_REGISTER_E40 v1 (md5 72ef32f8dd839cdabc38e57506831893) + run_E40_probe.py v1 (md5 2c9315e5dc95479f7dc32fe820ac04f9).

## DEFECT
V3 (sec7) was specified as EQUALITY: `max_B2_grid == 0.9333 else VOID`.
The premise is a structural UPPER BOUND: 2 golds resolve noauth -> unconditional reject -> recall
CANNOT exceed 28/30 = 0.9333. The faithful gate is therefore `max_B2_grid <= 0.9333`; only `> 0.9333`
implies a noauth-gold was wrongly rescued (the pre_demoted unconditional-reject logic broke).
Equality was copied from the pack sec3 phrasing ("== 0.9333 ... higher => VOID"); the stated rationale
covers ONLY the upper side. Same class as E39 v2/v3: a gate must assert ONLY what the premise requires,
and must NOT gate on the quantity the experiment is measuring (here: realized recall vs the ceiling).

## EVIDENCE (horn A; diag_E40.py over the REAL frozen readout; no frozen artifact touched)
- gold pre_demoted = 2 (ho_g18, ho_g25) -- MATCHES pack sec3. spoof pre_demoted = 16. SUBSTRATE CLEAN.
- a THIRD gold is never accepted anywhere in the refined grid:
    ho_g12 : n_con=2, n_ent=0, S_size=2, con_share=1.000.
    D_lambda = (2 - lambda*0)/2 = 1.0 for ALL lambda in [0.5,1.5] -> >= every tau<=0.75 -> never accepted.
    n_ent=0 => net-consensus has no entail term to subtract; D_lambda rescues only golds with
    con_share>=0.67 AND n_ent>=1 (E39 mechanism). ho_g12 is pure-consensus, indistinguishable from a
    high-consensus spoof on this statistic. STRUCTURALLY unrescuable by D_lambda.
- => grid-wide max B2 = (30-3)/30 = 27/30 = 0.9000, structurally BELOW the 28/30 ceiling.
  v1 V3 read 0.9000 != 0.9333 and VOIDed a correct, informative result.

## IMPACT ON VERDICT MACHINERY: NONE
K=12, span-rule (lambda/tau >=2 steps), and the ordered fork (FLOOR_BOUND -> REGION_ROBUST ->
REGION_SLIVER) were frozen pre-data and are UNCHANGED. With max_B2_grid=0.9000, every feasible point
(B2>=0.90 gate) has B2 exactly 0.9000 -> max_B2_in_R==0.9000 -> FLOOR_BOUND by the original fork's
first clause. K/span do not even gate FLOOR_BOUND. No reverse-fit: nothing in the verdict logic was
re-tuned after seeing data; only the mis-specified VOID gate is corrected.

## FIX (v2)
V3 -> VOID iff `max_B2_grid > 0.9333` (strict; <= is feasible/clean). Contract v1 superseded by v2;
run_E40_probe.py patched paired. New md5s recorded at v2 freeze. Re-run.

## RESEARCH NOTE (carry, not relitigate)
net-consensus D_lambda has a blind spot: golds whose bound set is pure-consensus (n_ent=0, con_share=1.0)
are inseparable from high-consensus spoofs -- the entail-subtraction rescue requires n_ent>=1. This caps
heldout recall at 27/30 here independent of the 2 noauth golds. The noauth channel (pack v90 FLOOR_BOUND
fork) and this pure-consensus blind spot are SEPARATE recall debts; both sit below the cross-source statistic.

-- end defect --
