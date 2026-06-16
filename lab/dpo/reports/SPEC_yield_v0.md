# SPEC_yield_v0.md -- pre-registered measurement contract for B2 full-text RESOLUTION-YIELD (P1)

date   : 2026-06-16
plane  : RESEARCH / S2(b) -- P1 RESOLUTION-YIELD. Raise per-chunk SUPPORTS/CONTRADICTS detection on the
         full-text resolver WITHOUT moving any bar. THIS DOC = measurement design only. NO predicate byte (R7).
home   : onto-research/reports (dateable priority + reproducibility ; generic-safe, ZERO dois/claim-texts/abstracts).
status : FROZEN 2026-06-16 (Founder accept). This doc + sec 1 metric + sec 3 invariants are md5-locked as
         the bar of record for P1 ; the lock md5 is recorded in CONTINUITY_LOG + the pack MANIFEST, NOT inside
         this file (self-reference would recurse the hash). No read/judge byte written before this freeze (R7).
binds  : SPEC_s2b_v0.md (md5 80bdf2a9, frozen ; G1-G4) + GATE_s2b_offtopic_v0.md (frozen ; G5-G6) +
         GATE_s2b_fulltext_v0.md (md5 27e65e60, frozen ; G6-G9 + A3 aggregation). This doc ADDS a yield
         measurement on top of those bars ; it RELITIGATES NONE of G1-G9 and MOVES NO bar.

## 0 WHAT THIS PLANE IS (one paragraph, zero-context reader)
The full-text fallback is COMPLETE and gate-valid (GATE_s2b_fulltext_v0, all bars PASS at wd ; resolver A3,
getter wc). On the frozen FT-CC it resolves only a fraction of the resolvable UNCLEAR bucket: per-chunk
affirmative CONTRADICTS is rare under the grounded non-proposing judge, so many FT-wrong cites land at honest
UNCLEAR instead of NOT. The full-text gate (sec 3) already declares yield a DIAGNOSTIC READOUT, not a bar:
under-resolving is honest, over-resolving in either direction is a G7/G8 failure. P1 asks one falsifiable
question: can a GENUINELY BETTER read/judge (chunking, excerpt targeting, per-chunk judge prompt, read
coverage) raise the resolution yield WHILE keeping G7 (no-poison) and G8 (no-castration) at ZERO on the SAME
frozen bar set -- or is 7/24 the real OA+contradiction-detection ceiling? This doc pins how that is measured so
the answer cannot be manufactured by moving a bar or by overfitting the frozen 24.

## 1 THE METRIC (single, falsifiable, R1/R6)
resolvable surface = the FT-CC items the fallback is ALLOWED to resolve = thin-correct + wrong (the no-OA
items MUST stay UNCLEAR by G9 ; they are never in the yield numerator OR denominator).

  YIELD = ( #thin-correct resolved to SUPPORTS  +  #wrong resolved to NOT ) / ( #thin-correct + #wrong )

On the canonical FT-CC composition (10 thin-correct / 10 wrong / 4 no-OA) the denominator is 20, NOT 24. The
loose "7/24" carried in prior notes uses the full-N denominator and UNDERSTATES the rate ; the contract
denominator is the RESOLVABLE 20. The baseline (sec 5) is the EXACT count from a real run, never recalled.

A resolution counts toward YIELD ONLY when it is CORRECT-DIRECTION (thin-correct->SUPPORTS, wrong->NOT). A
wrong-direction resolution is NEVER yield -- it is a bar failure (sec 3) and REJECTS the variant outright. There
is no partial credit and no aggregate that can trade a poison/castration for a yield point.

## 2 THE THREE SETS (measurement integrity -- the anti-Goodhart spine, R7/R11)
Tuning a judge against the same items on which you report success is overfitting the bar. P1 uses three
disjoint sets, all LOCAL-ONLY, bait-class, never public git:

  (S-bar)  FROZEN FT-CC, n=24 (ft_cc_v0.jsonl md5 ea5e0ec4 / ft_cc_ground_v0.json md5 88a14f9d). UNCHANGED.
           ROLE = REGRESSION BAR ONLY. Every candidate read/judge variant MUST re-clear G6/G7/G8/G9 on S-bar.
           Yield is NOT scored on S-bar (it is contaminated by being the bar) -- S-bar answers "did the variant
           break a bar", nothing else.
  (S-dev)  NEW FT-CC, same composition rules as the frozen gate sec 2 (n>=10 thin-correct / >=10 wrong / >=4
           no-OA ; dois + OA-status grounded LIVE per 3.9 ; CONTENTS verified per 3.7). ROLE = the ONLY set the
           engineer may READ while iterating the read/judge. Tune here freely.
  (S-held) NEW FT-CC, same composition rules, disjoint from S-dev by doi. ROLE = BLIND yield measurement.
           Adjudicated by id ONLY post-hoc ; the predicate sees it blind. Each variant is run on S-held EXACTLY
           ONCE, and only AFTER it has cleared bars on S-bar. No iteration against S-held. A second look at
           S-held for the same variant VOIDS the result (R7).

  The HEADLINE YIELD claim is the S-held number. S-dev yield is engineering telemetry, never the claim.

## 3 INVARIANTS (R7 HARD ; HARD dominates, C1) -- what NO variant may move
  I1 (bars frozen)     : G6/G7/G8/G9 (GATE_s2b_fulltext_v0 sec 3) are CITED, not re-opened. A variant is
                         admissible ONLY if it clears G7=0 poison AND G8=0 castration on BOTH S-bar and S-held.
                         tol 0. A bar failure REJECTS the variant ; it never trades for yield.
  I2 (aggregation A3)  : the STEP-2 aggregation (SUPPORTS if any chunk SUPPORTS ; else NOT only on affirmative
                         CONTRADICTS ; else UNCLEAR inconclusive/no_coverage) is DO-NOT-REBUILD. P1 may change
                         WHAT the per-chunk judge sees and HOW text is chunked/covered ; it may NOT change how
                         per-chunk verdicts are combined. NOT stays reserved for affirmative contradiction.
  I3 (getter / gate)   : the OA getter (wc, ad4d71 metadata route) and the fail-closed UNCLEAR-only firing
                         (gate 0c666ee0) are DO-NOT-REBUILD. P1 adds no new source and changes no firing rule.
  I4 (no bar tuning)   : yield is raised ONLY by a genuinely better read/judge. If the only way to raise yield
                         is to relax a per-chunk threshold such that G7 or G8 fails, that is REJECT, not a win
                         (the falsifier, sec 6). Yield is never a bar (gate sec 3) ; it is never optimized at a
                         bar's expense.

## 4 INTERVENTION SURFACE (what P1 MAY touch -- explicit, so scope cannot creep)
  ALLOWED (the read/judge):
    - chunk size + overlap (so a support/contradiction statement is not split across a boundary).
    - token budget / read-coverage (so coverage_complete is TRUE more often -> fewer no_coverage UNCLEARs).
    - per-chunk judge PROMPT for the THREE-WAY verdict (SUPPORTS / CONTRADICTS / UNCLEAR) -- sharpen the
      recognition of an affirmative contradiction and of genuine support, within the existing non-proposing,
      grounded framing.
    - excerpt targeting WITHIN the pinned linear-full-scan (the gate forbids retrieval top-k / embedding
      pre-select ; every chunk up to the cap is still scored -- P1 may reorder/format, not drop).
  FORBIDDEN (collapses to I1-I4): moving any bar ; changing A3 aggregation ; top-k / drop-chunk retrieval ;
    new sources ; touching abstract-layer (G1-G6) verdicts ; widening NOT beyond affirmative contradiction.

## 5 BASELINE (measure, do NOT recall -- R7/R4)
The baseline is the wd resolver treated as VARIANT-0, scored on the SAME blind set the claim is scored on:
run the CURRENT wd resolver (s2b_v0.py blob 35eefda1) ONCE on S-held (single-shot, sec 2) and record its
YIELD over the resolvable 20 -- THIS S-held number is the baseline any later variant must strictly beat
(sec 6), so baseline and variants share one set and there is NO set-difficulty confound. SEPARATELY run the
wd resolver on S-bar for REGRESSION ONLY: record per-class resolution counts (thin-correct->SUPPORTS,
wrong->NOT, the rest UNCLEAR with reason) and confirm G6-G9 PASS ; yield is NOT scored on S-bar (sec 2). Both
runs are read-only telemetry ; neither writes a predicate byte. "7/24" from memory is never the baseline --
only the measured S-held variant-0 number is.

## 6 ACCEPT / REJECT + FALSIFIER (R6)
A variant is ACCEPTED iff: (a) G6/G7/G8/G9 PASS on S-bar AND on S-held (I1) ; AND (b) YIELD on S-held strictly
exceeds the sec-5 baseline yield (the wd variant-0 S-held number). Otherwise REJECT -- the variant is discarded, the resolver stays at wd.

PLANE-LEVEL FALSIFIER (R6): if NO admissible read/judge variant raises S-held yield above baseline without
failing a bar on S-bar or S-held, then 7/24 (the resolvable-20 baseline) is the REAL OA+contradiction-detection
ceiling, not a build gap. P1 then CLOSES with "ceiling confirmed, residual stays honest UNCLEAR" -- it does NOT
tune a bar to fabricate a yield. A closed-by-falsifier P1 is a valid, honest outcome.

## 7 WHAT THIS DOC DOES NOT DO
  - No predicate byte. s2b_v0.py is UNCHANGED until a variant is built against this frozen contract (eval+fix
    never share -- this doc is the eval contract ; implementation is the step AFTER freeze).
  - No FT-CC items written here (public-safe). S-dev / S-held construction is STEP 1 of the build (sec 8).
  - No tuning loop against S-held. S-held is single-shot per variant. Iteration happens on S-dev only.

## 8 NEXT STEPS (handed to the build ; do NOT start before freeze)
  STEP 1  build S-dev + S-held (each n>=24, composition per gate sec 2), dois + OA-status grounded LIVE,
          CONTENTS verified (3.7), md5-lock each. disjoint from S-bar and from each other by doi. LOCAL-ONLY.
  STEP 2  record BASELINE (sec 5): wd resolver as VARIANT-0 run ONCE on S-held -> yield over resolvable 20
          (this S-held number is the baseline) ; SEPARATELY on S-bar -> per-class counts + G6-G9 PASS
          (regression only, yield NOT scored there).
  STEP 3  iterate the read/judge on S-dev ONLY (surface = sec 4). Each candidate re-proves G6-G9 on S-bar.
  STEP 4  for each S-bar-passing candidate: run ONCE on S-held -> bars + yield. Accept/reject per sec 6.
  STEP 5  report: baseline yield, best admissible variant's S-held yield, G7/G8 PASS on S-bar+S-held, or the
          falsifier-close. Public report = generic-safe (provenance + bars + yield deltas ; no eval data).
  trigger : "LABA, S2B YIELD"

## 9 HONEST GAPS (R7, pre-stated)
  - OA ceiling carries over: S-dev/S-held yield is still bounded by OA availability and by how often a wrong
    cite's OA full text contains an AFFIRMATIVE contradiction (vs simply not mentioning the claim). Many FT-wrong
    have no opposing statement -> honest UNCLEAR by I2, never NOT. A modest yield gain may be the true ceiling,
    not a failure.
  - Existence bars stay wide-CI: G7/G8 are existence bars (one failure rejects), n=10/surface per set. A clean
    PASS on S-bar+S-held is precision-first evidence with a deliberately wide CI, not a live false-fire guarantee.
  - Build cost: two new grounded FT-CC sets (S-dev, S-held) are the dominant cost of P1 and must clear the same
    LIVE-grounding + CONTENTS-verify discipline as the original FT-CC, or the measurement is worthless.
  - Tuning a prompt toward more CONTRADICTS directly stresses BOTH HARD bars (more aggressive contradiction
    detection risks castrating a thin-correct -> G8 ; more aggressive support detection risks poisoning a wrong
    cite -> G7). The three-set + tol-0 design is what keeps that honest ; it is the point, not an obstacle.

freeze: FROZEN 2026-06-16. md5-lock over this doc + sec 1 metric + sec 3 invariants is the bar of record ;
        recorded externally (CONTINUITY_LOG + MANIFEST). The build's first byte comes AFTER this line.
