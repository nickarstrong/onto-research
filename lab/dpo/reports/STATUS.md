# STATUS.md -- ONTO lab current-state snapshot (pack v178)

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
           (we) P1 RESOLUTION-YIELD measurement contract SPEC_yield_v0.md FROZEN (md5 c90f8a40) + committed
           e5d422d (public onto-research). Pre-freeze audit caught a set-confound (sec2 forbade yield-on-S-bar
           while sec5 scored baseline-yield on S-bar) -> fixed: baseline = wd resolver as VARIANT-0 scored ONCE
           on S-held, S-bar regression-only. (wf) P1 CLOSED by falsifier: S-dev VALID 0.75, generalizes, judge-iteration negative-ROI ; S-held deferred-buildable ; getter-404 fix (I3) logged. // P5 EOL-hygiene found ALREADY-SATISFIED (gitattributes present +
           effective) -> no-op, that plane CLOSED. Build NOT started (eval+fix split, R7).

LADDER TRUTH (reconciled pack-v177, disk-grounded, R15/3.10) : the pack-v176 "E9 = NEXT / LABA E9 DPO" route was
  STALE. Disk shows adapter_E9..E12 + adapter_fixb already built+scored (07-14.06) with reports E9-E12. The model-
  DPO ladder (E5-E12 + fixb) is DONE/superseded by the EXTERNAL-verifier architecture (CONSCIENCE line above).
  DPO is NOT on the open menu. P1 RESOLUTION-YIELD = CLOSED (wf): S-dev VALID 0.75, G7/G8/G9 PASS, resolver
  GENERALIZES vs contaminated S-bar 0.70, judge-iteration negative-ROI ; S-held deferred-buildable.

ACTIVE PLANE : LAB L5 PART I, Act 2 (apply v1.1 predicate P3-leg + run + read G1/G2/G3). Trigger now: "LABA, L5 ACT 2".
  Act 1 (truth-set relabel + gate re-freeze) DONE (wh) -- truth labels now CLEAN, gate sec3 absorbs all relabels,
  re-frozen with new locks. Cause split of the pre-fix FAIL: (A) DIRTY TRUTH LABELS [dominant] = FIXED in Act 1
  (5 declared-independent pairs carried REAL Crossref cites ; relabeled ind->citation ; predicate P4 was correct).
  (B) P3 fail-close on accession-less independents = the ONLY remaining real over-prune ; the v1.1 single-leg fix =
  THIS session (Act 2). (C) C014 Wu/Zhou courtesy cross-cite = documented known-limit, the 1 expected residual.
  ACT-1 LOCKS (verify before any Act-2 byte) : truth_input.txt ac4ef6fa04c73aeb673536da347ca56d (5 ind->citation) ;
  SPEC_L5_fixgate_v2.md 969a639601e0597f05b2793b9525f6c4 (sec3 absorbs C015 + the 5 ; G1/G3 arithmetic reconciled) ;
  l5_coupling_truth.jsonl verified BY COUNTS not md5 (EOL platform-dependent) = {ind:11,author:2,inst:1,data:5,cit:10}.
  ACT 2 = AST-snapshot run_L5_partI_validate.py -> edit pair_predict P3 leg ONLY (absent-DAS stops fail-closing) +
  T002 fixture -> re-hash (must-stay fns byte-identical, gate sec2) -> --selftest -> build -> --contents -> net
  pre-check -> --run -> read G1/G2/G3. GO = G1 HARD (no ind coupled solely via P3) AND G2 HARD (per-class recall
  author/inst/data/citation==1.0, leak==0) AND G3 (over_prune<=0.10, bal_acc>=0.85 ; residual = exactly 1 = C014
  Wu/Zhou = 1/11 ~= 0.091, THIN margin). P4/P1/P2 NOT touched. On GO -> PART I frozen+passing -> roadmap s3 (E39).
  PREDICATE-BASELINE RECONCILE (Act-2 STEP 0 ; flagged at v178 consistency pass): gate sec1 file-md5 anchor
  b1f4aae4 is STALE -- live predicate on disk = b96bfb43 (gg-sweep predicate ; b1f4aae4 kept as .bak.frozen_).
  Invariant = gate sec1/sec2 PER-FN AST anchors, not file-md5. Confirm live per-fn AST == anchors -> b96bfb43
  gate-valid, update sec1 file-md5 (log, R7) ; ANY per-fn mismatch -> STOP (do not P3-edit a drifted predicate).
  L5 PART II = BLOCKED on E39 net-consensus ; ceiling = T1 ; do NOT freeze.

ROADMAP (Founder-approved) : 3-4 session verifier close-out, THEN pivot to the model "propose" side.
  s1-2 L5 PART I (Act 1 + Act 2) -> predicate frozen+passing.  s3 E39 net-consensus = GO (clean verdict) OR RETIRE
  (document T1 ceiling). bounded decision, not open-ended chase.  s4 freeze verifier as datable standard artifact.
  THEN model propose-side (initiative/creativity/self-learning via R1-R18/autonomy) = NEW greenfield front, NOT a
  continuation of the E1-E12 reflex ladder. Design when opened.
  s2b predicate has NO open defect (full-text plane CLOSED). TAIL DEBT (I3): getter 404 -> ERROR must become
  fail-closed UNCLEAR (~3 lines), not a P1/L5 bar.

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

S2B ARTIFACT : s2b_v0.py canonical blob md5 = 35eefda12c0774ef6e13522febfe1447 (LF, git HEAD fd2b9ba). EOL now
  STABLE: onto-research/.gitattributes carries `*.py text eol=lf` + `* text=auto eol=lf` ; core.autocrlf=false ;
  verified this session disk md5 == git-blob (35eefda1), 0 .py with CRLF in worktree. The old CRLF working copy
  (2625754e) is GONE -- EOL/md5 confusion RESOLVED, no longer a drift hazard.

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

PARKED : (a) B2 SUPPORTS/CONTRA-leg at scale = the resolution-yield plane -> NOW ACTIVE as P1 (contract frozen).
  (c) 4-bit GPU B2 restore = speed only. L5 FIX (fresh gate first). A-channel CI to ~30.
  [DONE this session: .gitattributes eol=lf -- found already present + effective, EOL plane CLOSED.]

HONEST GAPS (R7):
  - L5 Act-1 relabel dropped independents 16 -> 11 -> G3 residual budget is now 1/11 ~= 0.091 against a FROZEN
    0.10 bar (was 1/16 ~= 0.06). The expected residual is still EXACTLY 1 (C014 Wu/Zhou known-limit), so Act 2
    G3 passes -- but the margin is THIN: any 2nd non-Wu/Zhou independent left coupled breaches. Honest arithmetic
    from the relabel, NOT a bar move ; the 0.10 bar stays frozen (gate sec5).
  - Resolution yield 7/24: per-chunk affirmative CONTRADICTS is rare under the grounded judge, so many FT-wrong
    land at honest UNCLEAR rather than NOT. This is the OA+contradiction-detection ceiling, not a castration and
    not a bar fail. Raising it is a SUPPORTS/CONTRA-leg scaling plane.
  - coverage_complete may overstate coverage on landing-page / low-chunk OA fetches (getter path). Where true, the
    post-fix verdict is the honest UNCLEAR (no_coverage / no_fulltext), never NOT -- bar unaffected. Separate plane.

INFRA    : conveyor PACK_SPEC md5 == f888f427. getter Crossref+OpenAlex (arXiv-robust). resolver A3 (wd). B2:
           Qwen2.5-7B on GPU (GPU-ONLY directive ; the old "CPU offload / S2B_NO_4BIT" framing is RETIRED --
           CPU was never an operating mode, only a wrong command). Read-proof: arXiv direct ; medical body-probe.

GIT      : onto-research = reproducibility + dateable priority only. (wd) PUSHED: main HEAD fd2b9ba (Reapply s2b
           G8 fix) carries s2b_v0.py (blob 35eefda1) + reports/REPORT_s2b_g8_resolver_fix.md (public-safe). History
           20c4db6 (commit) -> 239b3b4 (errant revert) -> fd2b9ba (reapply) ; no force-push. ft_cc + ground + run
           in/out LOCAL-ONLY. R12 leak RESOLVED: audit_v2_stdout.txt + onto_index_harvest.txt moved to eval/_local/
           (gitignored). bak dupes deleted. Prior pushes: (vv) 9893aa4 ; (vw) GATE_s2b_fulltext_v0.md ; (tt)
           GATE_s2b_offtopic_v0.md.
           (we) PUSHED: main HEAD e5d422d (85bf0cd..e5d422d) carries reports/SPEC_yield_v0.md (FROZEN P1 yield
           contract, public-safe: metric + invariants + provenance, ZERO DOIs/abstracts/eval-data). New file
           (draft never tracked). lock md5 c90f8a40 recorded here + CONTINUITY_LOG. Tree clean, draft .bak removed.
           LOCAL-ONLY (never public): proposals/worksheet/rate_judgments/ledger(DOIs)/falsifier/ground_candidates/
           cc/j5/cc_j5_ground/g5_live/ft_resolve/resolve_ft.ps1/ft_cc_v0*/ft_cc_ground/ft_cc_v0_s2b_out*/all L5 truth-set.
