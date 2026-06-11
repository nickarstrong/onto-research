# PRE_REGISTER_E40 v2 -- robustness / feasible-region sweep

STATUS: FROZEN. v2 supersedes v1 (md5 72ef32f8dd839cdabc38e57506831893) per E40_V1_DEFECT.md.
  v1 defect: V3 noauth-ceiling gated on EQUALITY (==0.9333) instead of UPPER BOUND; VOIDed a clean
  result (real grid-wide max B2 = 27/30 = 0.9000, a 3rd gold ho_g12 is n_ent=0/con_share=1.0 ->
  D_lambda-unrescuable). Verdict machinery (sec4-6) UNCHANGED -- only V3 (sec7) corrected to <= ceiling.
PARENT: E39 v4 STATISTIC_LIFTS (c0d1989). best_op lambda=1.0, tau=0.67 -> fa_op 0.0333, B2 0.9000.
PLANE: onto-research/lab/dpo. RESEARCH. no-GPU probe over the FROZEN E37 6-field readout.

## 0 QUESTION
E39 lifts the bf-band but at MINIMUM width (band 2pts/2lambda, B2 ON the 0.90 floor).
Decide: does a NON-TRIVIAL feasible operating REGION exist around best_op, or is the lift a
fragile single point / thin diagonal (E27/E35 knife-edge in disguise)?

## 1 STRUCTURAL CEILING (asserted, not discovered)
2 golds resolve noauth -> pre_demoted -> unconditional reject -> D_lambda CANNOT rescue them.
=> max achievable B2 on heldout_E17 = 28/30 = 0.9333. Feasible B2 band is structurally
[0.9000, 0.9333] -- 0.0333 headroom only. This is a known ceiling, NOT a result to find.

## 2 INPUT (gated)
readout: eval/_local/E37_boundset.json  (gitignored, regenerable via emit_E37_readout.py)
  no fixed md5 (regenerable). gate on CONTENTS instead (E15 empty-set lesson):
  READOUT GATE (all must hold, else VOID):
    G1  exactly 60 rows.
    G2  class split 30 gold / 30 spoof.
    G3  6 fields per row present (the E37 boundset schema; n_con, n_ent, S_size, class, pre_demoted, id).
    G4  D_0 (lambda=0 == con_share) on the SPOOF side reproduces E39 spoof fa = 0.0333 byte-exact.
  G4 pins readout content to the E39 substrate without an md5.

## 3 STATISTIC (frozen; REUSE, do not re-implement)
D_lambda(item) = (n_con - lambda * n_ent) / |S|   over the auth subset (|S| = S_size).
decision: item ACCEPTED iff D_lambda >= tau ; else REJECTED (veto).
  pre_demoted (noauth) item -> unconditional REJECT, regardless of D_lambda.
  empty bound set (S_size == 0) on a non-pre_demoted item -> ACCEPT (reproduces E37; NOT VOID).
COMPUTE = class-blind. class label joined ONLY for fa_op / B2 reporting (oracle-leak guard).
run_E40_probe.py MUST import run_E39_probe.load_records + d_lambda + evaluate. No re-derivation.

## 4 SWEEP GRID (frozen; integer-indexed to kill float drift)
lambda = 0.5 + 0.1*i , i in 0..10        -> {0.5,0.6,...,1.5}      11 values
tau    = 0.50 + 0.01*j , j in 0..25      -> {0.50,0.51,...,0.75}   26 values
total grid = 11 * 26 = 286 points. enumerate by (i,j); round only for reporting.
NO perturbation of n_con / n_ent / S_size. region is over (lambda,tau) ONLY.

## 5 METRICS
feasible point: fa_op <= 0.10 AND B2 >= 0.90.
R = { (lambda,tau) in grid : feasible }.
|R| = count of feasible grid points.
bounding box:
  lambda_span_steps = round( (max_R lambda - min_R lambda) / 0.1 )   [0 if |R|<=1]
  tau_span_steps    = round( (max_R tau    - min_R tau   ) / 0.01 )  [0 if |R|<=1]
max_B2_in_R = max B2 over feasible points.
max_B2_grid = max B2 over ALL 286 points (noauth-ceiling check).

## 6 DECISION RULE (K and span-rule LOCKED before sweep)
K = 12 feasible points.  span rule: lambda_span_steps >= 2 AND tau_span_steps >= 2.
  (rationale: a genuine 2D region must be a >=3-lambda x >=3-tau extent AND filled past a thin
   diagonal; 12 pts ~ a 3x4 block, a clear step above E39's 2-pt minimum band. ONE assumption line.)
verdict (total, ordered -- first match wins):
  1. FLOOR_BOUND   : R non-empty AND max_B2_in_R == 0.9000 (no feasible point exceeds the recall floor).
  2. REGION_ROBUST : |R| >= 12 AND lambda_span_steps >= 2 AND tau_span_steps >= 2.
  3. REGION_SLIVER : R non-empty, none of the above (thin diagonal / single-lambda column / |R|<12).
  (R empty is impossible: anchor is feasible by construction -> would trip VOID, see sec 7.)

## 7 VOID CONDITIONS (any -> VOID, no verdict)
V1  readout gate G1-G4 fails.
V2  anchor miss: (lambda=1.0, tau=0.67) NOT feasible, OR fa_op != 0.0333, OR B2 != 0.9000
    (to the reported precision, byte-exact vs E39).
V3  max_B2_grid > 0.9333 (STRICT upper bound; <= is clean). 0.9333 = 28/30 is the structural
    recall CEILING (2 noauth golds unconditionally reject). > ceiling => a noauth-gold was wrongly
    rescued (pre_demoted unconditional-reject broke). max_B2_grid BELOW 0.9333 is a valid result
    (a 3rd gold may be D_lambda-unrescuable, e.g. n_ent=0/con_share=1.0), NOT a void. (v1->v2 fix.)
V4  any spoof rescued by lambda<0 path, or grid emits lambda/tau outside the frozen ranges.

## 8 REGRESSION ANCHORS (byte-identical, mandatory)
  lambda=0 (D_0 == con_share), SPOOF side -> E39 spoof fa 0.0333.
  best_op (lambda=1.0, tau=0.67)          -> fa_op 0.0333, B2 0.9000.
both must reproduce or VOID (V2/G4).

## 9 FALSIFIER (stated)
HYPOTHESIS: E39's narrow lift is a robust feasible region.
FALSIFIED iff verdict in { REGION_SLIVER, FLOOR_BOUND } -- i.e. |R| < 12, OR a span axis
collapses, OR all feasible points pinned to B2==0.9000. That outcome routes to the band-widener
or noauth-channel fork (pack v90 sec4), NOT a clean cross-source-statistic graduation.

## 10 OUTPUTS
reports/report_E40.md   : verdict + |R| + bounding box + anchor reproduction + max_B2 checks.
reports/gate_E40.log    : G1-G4 + V1-V4 pass/fail lines.
reports/E40_region.json : { |R|, R as (lambda,tau) list, bbox, max_B2_in_R, max_B2_grid, anchor }.

-- end frozen contract --
