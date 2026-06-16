# STATUS.md -- ONTO lab current-state snapshot (pack v171)

HARD RULE: every load-bearing line is written for an instance with ZERO context. If a line does not unpack
into a concrete action for someone who knows nothing, it is a bug. Compressed != encrypted.

PHASES   : phase 1/2/3 CLOSED. fix(b) bounded-DPO CLOSED.
CONSCIENCE: EXTERNAL + PERMANENT. Substrate PROPOSES ; external gate + independent judge DISPOSE. The s2b
           grounded verifier is now COMPLETE end-to-end: B1 binding (deterministic) + B2 content (abstract via
           Crossref+OpenAlex + shipped off-topic predicate) + full-text fallback (OA getter, arXiv-robust, +
           resolver). All four legs gate-valid. No open defect in the s2b predicate.

NORTH-STAR LOOP : (vv) off-topic predicate SHIPPED (9893aa4). (vw) full-text GATE frozen (md5 0c666ee0). (vx-wa)
           STEP 1 FT-CC (n=24) COMPLETE + md5-LOCKED. (wb) STEP 2 fallback implemented + selftest G1-G9 PASS, live
           run degraded (9/24 arXiv ERROR). (wc) GETTER FIX (ad4d71): arXiv/DataCite + Crossref-404 -> OpenAlex
           full metadata ; ERROR 9->0 ; exposed latent G8 castration -> --score REJECT, commit HELD. (wd) G8
           RESOLVER FIX (35eefda1): A3 aggregation, NOT only on affirmative contradiction ; --selftest G1-G9 PASS
           (Qwen) ; --score VERDICT PASS (G7/G8/G9) ; ftc02/03/08 NOT->UNCLEAR ; committed fd2b9ba.

ACTIVE PLANE : NONE. Full-text fallback plane CLOSED. Founder selects next from PARKED.

THE GATE (vw, FROZEN ; md5 0c666ee0) : full-text fires ONLY on abstract-UNCLEAR ; OA-only source, fail-closed.
  BARS: G6 carried ; G7 (HARD no-poison) 0 FT-wrong->SUPPORTS ; G8 (HARD no-castration, READ-COVERAGE-BOUND)
  0 FT-thin-correct->NOT ; G9 (honesty) no-OA->UNCLEAR. ALL PASS at (wd). Recall/yield = diagnostic.

RESOLVER (wd, DONE -- do NOT rebuild) : A3 aggregation in fulltext_resolve. Per read chunk: SUPPORTS -> SUPPORTS
  (top precedence) ; affirmative CONTRADICTS accumulates -> after loop NOT (fulltext_contradicted) ; else
  coverage_complete -> UNCLEAR (fulltext_inconclusive) ; else UNCLEAR (no_coverage). NOT reserved for affirmative
  contradiction ONLY. unread->UNCLEAR/no_coverage guarantee unchanged. Abstract layer byte-identical to ad4d71.

GETTER (wc, DONE -- do NOT rebuild) : fetch_crossref routes DataCite/arXiv (10.48550/) + any Crossref-404 to
  OpenAlex full metadata via fetch_openalex_meta. OpenAlex empty -> re-raise -> honest ERROR (R7). Crossref stays
  primary when it resolves. --netcheck arXiv probe (ftc04 DOI) PASS.

S2B ARTIFACT : s2b_v0.py canonical blob md5 = 35eefda12c0774ef6e13522febfe1447 (LF, git HEAD fd2b9ba). Windows
  working copy = 2625754e (CRLF, autocrlf on checkout) = SAME content -- not drift. Do not chase the EOL md5.

FT-CC STATE (wa ; n=24 = 10 thin-correct / 10 wrong / 4 no-OA ; LOCKED, LOCAL-ONLY) :
    eval/_local/ft_cc_v0.jsonl       md5 ea5e0ec43e73738116452a03a09b51e9
    eval/_local/ft_cc_ground_v0.json md5 88a14f9de99aeeea2b15631a59b6d1c6
  These two md5 are the FREEZE. Ground read post-hoc by id ONLY ; predicate adjudicates blind (R7). Both LOCAL-ONLY.
  CARRY: id18/id29 still hold PLACEHOLDER claim_text in the locked set (both FT-wrong, resolve right) ; re-lock
  only if a class is re-sourced. Do NOT rebuild or re-source any class.

THE 3 G8 FAILS (wc) -- RESOLVED at (wd): ftc02 (arXiv.1704.08463) UNCLEAR/fulltext_inconclusive ; ftc03
  (medRxiv 2025.10.22.25338568) UNCLEAR/no_fulltext ; ftc08 (arXiv.2407.02420) UNCLEAR/fulltext_inconclusive.
  None NOT. G8 PASS.

DO-NOT-REBUILD : gate (0c666ee0), S2B judge (B1+B2 incl off_topic), md5-guard, the full-text fallback LOGIC, the
  GETTER (ad4d71 metadata route), and the RESOLVER (wd, A3). FT-CC LOCKED (ea5e0ec4 / 88a14f9d).

PARKED : (a) B2 SUPPORTS/CONTRA-leg at scale = the resolution-yield plane (7/24 is honest OA+contra ceiling, NOT a
  bug ; never chase by tuning a bar, R7). (c) 4-bit GPU B2 restore = speed only. L5 FIX (fresh gate first).
  A-channel CI to ~30. IDEA: .gitattributes `*.py text eol=lf` -> stabilize checkout EOL (kills CRLF/md5 confusion).

HONEST GAPS (R7):
  - Resolution yield 7/24: per-chunk affirmative CONTRADICTS is rare under the grounded judge, so many FT-wrong
    land at honest UNCLEAR rather than NOT. This is the OA+contradiction-detection ceiling, not a castration and
    not a bar fail. Raising it is a SUPPORTS/CONTRA-leg scaling plane.
  - coverage_complete may overstate coverage on landing-page / low-chunk OA fetches (getter path). Where true, the
    post-fix verdict is the honest UNCLEAR (no_coverage / no_fulltext), never NOT -- bar unaffected. Separate plane.

INFRA    : conveyor PACK_SPEC md5 == f888f427. getter Crossref+OpenAlex (arXiv-robust). resolver A3 (wd). B2:
           Qwen2.5-7B CPU offload (4-bit opt-out via S2B_NO_4BIT). Read-proof: arXiv direct ; medical body-probe.

GIT      : onto-research = reproducibility + dateable priority only. (wd) PUSHED: main HEAD fd2b9ba (Reapply s2b
           G8 fix) carries s2b_v0.py (blob 35eefda1) + reports/REPORT_s2b_g8_resolver_fix.md (public-safe). History
           20c4db6 (commit) -> 239b3b4 (errant revert) -> fd2b9ba (reapply) ; no force-push. ft_cc + ground + run
           in/out LOCAL-ONLY. R12 leak RESOLVED: audit_v2_stdout.txt + onto_index_harvest.txt moved to eval/_local/
           (gitignored). bak dupes deleted. Prior pushes: (vv) 9893aa4 ; (vw) GATE_s2b_fulltext_v0.md ; (tt)
           GATE_s2b_offtopic_v0.md.
           LOCAL-ONLY (never public): proposals/worksheet/rate_judgments/ledger(DOIs)/falsifier/ground_candidates/
           cc/j5/cc_j5_ground/g5_live/ft_resolve/resolve_ft.ps1/ft_cc_v0*/ft_cc_ground/ft_cc_v0_s2b_out*/all L5 truth-set.
