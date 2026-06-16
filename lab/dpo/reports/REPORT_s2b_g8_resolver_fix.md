# REPORT -- s2b full-text resolver G8 fix (A3 aggregation)

date    : 2026-06-16
artifact: s2b_v0.py  md5 35eefda12c0774ef6e13522febfe1447
parent  : s2b_v0.py  md5 ad4d71794f678b5a3c1febccf24bf46e (getter-fixed, pre-resolver)
gate    : GATE_s2b_fulltext_v0.md md5 27e65e604ada62a679714025003b3169 (FROZEN, A1+A2+A3)

## DEFECT
The full-text resolver aggregation emitted NOT whenever no read chunk affirmatively
SUPPORTED the claim and coverage was complete. Absence-of-support in a read span was
treated as contradiction. A read thin-correct item with no per-chunk SUPPORTS hit was
forced to NOT -- a G8 castration (no-castration bar: zero FT-thin-correct -> NOT).

## FIX (per gate A3)
NOT is reserved for affirmative contradiction only. Aggregation over read chunks:
  - any chunk SUPPORTS                         -> SUPPORTS (fulltext_supports)
  - else any chunk affirmatively CONTRADICTS   -> NOT      (fulltext_contradicted)
  - else coverage complete, no support/contra  -> UNCLEAR  (fulltext_inconclusive)
  - else (unread bytes)                        -> UNCLEAR  (no_coverage)
The unread->UNCLEAR/no_coverage guarantee (chunk cap / fetch truncation) is unchanged.
Abstract-layer functions are byte-identical to the parent (diff: resolver + selftest only).

## VERIFICATION
--selftest (real Qwen2.5-7B, CPU offload, S2B_NO_4BIT):
  BARS PASS G1 & G2 & G3, G4 held ; G5 PASS (0/18 CC -> NOT, no castration).
  FT-SELFTEST PASS (offline fake-OA + stub B2): G7 (NOT only on affirmative contra) ;
  G8 (support read -> SUPPORTS ; support unread -> UNCLEAR/no_coverage, never NOT) ;
  G9 (no-OA -> UNCLEAR/no_fulltext).

--score on FT-CC (n=24 ; answer key joined post-hoc, predicate blind):
  G7 no-poison     (0 FT-wrong -> SUPPORTS)   : PASS
  G8 no-castration (0 FT-thin-correct -> NOT) : PASS
  G9 honesty       (FT-no-OA -> UNCLEAR)      : PASS
  VERDICT: PASS (fallback BUILDABLE+VALID = G6 & G7 & G8 & G9)
  resolution yield: 7/24 UNCLEAR-entering items resolved by full text (DIAGNOSTIC, not a bar).

## NOTE (R7)
Low resolution yield is honest under-resolution: per-chunk affirmative CONTRADICTS is rare
under the grounded judge, so many wrong cites land at UNCLEAR rather than NOT. Per gate,
under-resolving is honest UNCLEAR ; the G8 bar was NOT tuned to force any verdict.

## FLAG (R16, out-of-plane, getter path -- not fixed this session)
coverage_complete may overstate coverage on landing-page / low-chunk OA fetches. Where this
holds, the post-fix verdict is the honest UNCLEAR (no_coverage / no_fulltext), never NOT, so
the bar is unaffected. Coverage-detection accuracy is a separate (getter) plane.

## SCOPE
FT-CC items, ground answer key, and run in/out are LOCAL-ONLY (public held-out is consumed by
future pretrains -> measurement ruined). This report carries provenance + reproducibility only.
