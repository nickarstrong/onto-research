# SPEC -- Content-Bind Verifier v1 (FROZEN)

date     : 2026-06-12
plane    : RESEARCH / lab NLI ladder (the L4 content-bind organ of the provenance verifier)
home     : onto-research/reports (dateable priority + reproducibility)
status   : v1 FROZEN. This is a WRITE-DOWN of the graduated organ, not a new design.
           No bar in this file may be relitigated. Re-opening a frozen bar = FAIL.
provenance: E40 FLOOR_BOUND (f15d4d6) graduates the statistic; E42scale PASS/CAP_HOLDS (2273545)
           confirms at full-GOLD. Both v91 falsifiers RESOLVED (F1 INDEPENDENT, F2 CAP_HOLDS).

--------------------------------------------------------------------------------
## 0 SCOPE

This organ is L4 (CONTENT-BIND) of SPEC_provenance_verifier (reject iff the real, clean source does
NOT support the specific claim). It is a CONTRADICTION/BINDING VETO, not a coverage classifier:
the per-entailment-coverage organ class is EXHAUSTED (E25b ceiling fa~0.20; E37 SET_EXHAUSTED).
v1 is the contradiction-veto that graduated past that ceiling.

NOT a truth check. The organ asserts only that the binding between claim and source holds or is
contradicted. A bound, supporting source can still be false (that is L5's ceiling, not L4's).

--------------------------------------------------------------------------------
## 1 ORGAN (frozen, verbatim)

Per heldout candidate, over its representative bound-subset S of source sentences:
  n_con = count(NLI verdict == contradiction) over S
  n_ent = count(NLI verdict == entailment)    over S
  D_lambda = (n_con - n_ent) / |S|            ; lambda frozen = 1.0 (E39 v4 best_op)

  reject  iff  ( pre_demoted  OR  D_lambda >= 0.67 )

  tau frozen = 0.67 (E39 v4 best_op tau ; E40 region WIDE/STABLE |R|=86 around it).
  pre_demoted = upstream provenance/grade demotion channel (noauth, grade-fail) -- a reject
                that does NOT depend on the NLI statistic. Carried as a separate OR-arm so a
                source with no contradiction signal but failed provenance still rejects.

Model : MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli
        id2label {0: entailment, 1: neutral, 2: contradiction}. Contradiction index read from
        id2label, NEVER hardcoded. Fresh pod requires sentencepiece + protobuf (deberta-v3 tokenizer).
        The "bart-large-mnli" tile is STALE: bart fa 0.0667 is a CROSS-MODEL bar only; the running
        and frozen model is DeBERTa.

--------------------------------------------------------------------------------
## 2 GUARDS (frozen, enforced)

G1 ONE-SIDED RHO VOID. one-sided spearman rho(D_lambda, upstream_bind) >= 0.95 -> VOID (organ would
   be a proxy for retrieval, not an independent consensus signal). ENFORCED + satisfied: measured
   rho = -0.5481 (n=37), NEGATIVE -> stronger binding trends consensus-SUPPORTED, not contradicted
   -> D_lambda measures CONSENSUS, not retrieval. Graduation NOT contaminated. (F1 RESOLVED.)
   upstream_bind = mean beff(B_lex, B_anchor) over the representative bound-subset S ; W frozen 0
   -> B_lex ; null when S_size == 0 (EXCLUDED from the rho computation, not coerced to 0).

G2 CONTENTS COUNTER (mandatory, not optional). Non-empty spoof set AND non-empty gold set, and
   upstream_bind non-null where S>0, asserted before any verdict. md5/filename pass != usable
   artifact (E15 worksheets, E23 VOID-by-construction). A clean verdict over an empty recall set
   is a VOID, not a PASS.

G3 ANCHOR (regression / version-drift guard). fa_op 0.0333 (anchor) and auth-only 0.0714 reproduce
   byte-identical across runs. Anchor reproduction is the transformers-version drift guard; it did
   not trip at full-GOLD scale. Mismatch = STOP (env drift), not a re-measure.

G4 VERDICT METRIC. Verdict reads the MAX-BASED GATE false-accept rate, NEVER p50 separation.
   sep is confounded on E25b; fa (max-based) is confound-immune.

--------------------------------------------------------------------------------
## 3 PERFORMANCE (full-GOLD E25b, 217 rec ; frozen)

fa_op  : 0.0333   (meets <= 0.10 gate)
recall : 0.9000   (27/30 structural golds recovered)
auth-only fa : 0.0714 (anchor)

E25b IS full-GOLD: build_fixture_E17 supersedes the E16 61-record slice. E17->E18->E25b grew the
`finding` field (0->27->90), NOT the record count (all three = 217 rec / 216 manifest). Full-GOLD
scale = re-emit over the already-full E25b, NO rebuild (rebuild would break the gated fixture, the
0.0333 anchor, and the anchored ladder).

--------------------------------------------------------------------------------
## 4 RECALL-DEBT (characterized, frozen ; F2 CAP_HOLDS)

recall cap = 0.9000 is STRUCTURAL, not small-sample (== E40/E41 == E42scale at full-GOLD).
3 structural golds the organ cannot recover with the con/ent statistic alone:
  - ho_g18  : noauth -> recovered via pre_demoted arm (not the NLI statistic)
  - ho_g25  : noauth -> recovered via pre_demoted arm
  - ho_g12  : pure-consensus, n_ent = 0 -> D_lambda = 1.0 (degenerate; no contradiction to read)

Recovery of these = a DIFFERENT organ (E42 noauth-channel: a source-identity signal orthogonal to
con/ent, ABSENT from the 7-field readout). OPTIONAL for v1 -- the cap holds and v1 is shippable
without it. Do NOT re-attempt the per-candidate organ class (cosine/binding/con_share clear the
fa-gate but none lift the bf-band -> CLASS EXHAUSTED, E37 SET_EXHAUSTED).

--------------------------------------------------------------------------------
## 5 FALSIFIERS (what would break v1)

F-a : a heldout source that does NOT contradict its claim and is provenance-clean, rejected by the
      organ (D_lambda >= 0.67 with no real contradiction) -> false-accept inflation past the 0.10 gate.
F-b : rho(D_lambda, upstream_bind) measured >= 0.95 on any re-emit -> organ is a retrieval proxy -> VOID.
F-c : anchor fa_op != 0.0333 (byte) on a clean re-run with frozen fixture -> env/version drift -> STOP.
F-d : a verdict produced over an empty spoof or empty gold set (G2 not asserted) -> VOID, discard.

--------------------------------------------------------------------------------
## 6 LADDER PROVENANCE (verdicts only ; do not relitigate)

E37      SET_EXHAUSTED [FALSIFIER]   88489f8   per-candidate class CLOSED
E39 v4   STATISTIC_LIFTS             c0d1989   D_lambda form; best_op lambda=1.0 tau=0.67 -> fa 0.0333
E40      FLOOR_BOUND                 f15d4d6   region WIDE/STABLE |R|=86 -> GRADUATES; recall floor 0.9000
E41      DEBT_CHARACTERIZED          26dc4ce   2 noauth + 1 pure-consensus (ho_g12 n_ent=0 -> D=1.0)
v91      INTEGRATION                 4bb389b   RHO_RECONCILE (one-sided 0.95; axis D_lambda vs upstream_bind)
E42scale PASS / CAP_HOLDS            2273545   full-GOLD: F1 rho=-0.5481 INDEPENDENT; F2 recall 0.9000 structural

--------------------------------------------------------------------------------
## 7 FROZEN BARS (re-opening any = FAIL)

- D_lambda = (n_con - n_ent)/|S| @ tau 0.67 ; lambda 1.0 ; reject iff (pre_demoted OR D_lambda>=0.67)
- fa_op 0.0333 / auth-only 0.0714 (anchors, byte-identical)
- recall 0.9000 cap STRUCTURAL ; 3 structural golds named (ho_g18, ho_g25, ho_g12)
- rho VOID threshold 0.95 one-sided ; measured -0.5481 INDEPENDENT
- model = DeBERTa-v3-large-mnli-fever-anli-ling-wanli ; contradiction idx from id2label
- verdict = max-based GATE fa, never p50 sep

v1 FROZEN.
