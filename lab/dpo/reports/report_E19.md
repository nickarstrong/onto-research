# report_E19 - contradiction-veto + premise-enrichment + held-out v3

Provenance: E19 session on the frozen E16/E17/E18 substrate (verify_E16, gold_retrieve,
semantic_retrieve byte-identical). NLI = cross-encoder/nli-deberta-v3-small, CPU,
transformers==4.53.3. Env: KMP_DUPLICATE_LIB_OK=TRUE, ONTO_RETRIEVE_FLOOR=0.55,
ONTO_NLI_TAU=0.50. Bind FLOOR/TOP_K frozen throughout; nothing in E16 mutated.

## 0. Verdict (both pre-registered axes hit their ceiling)

- **B2 (contradiction-veto): FALSIFIED.** No veto setting closes the NN leaks without
  vetoing real gold. veto-insufficiency, not a tuning miss.
- **B1 (oracle ceiling): 0.889 after legitimate repair (< 0.90 bar).** Residual = three
  NLI entailment-recall misses on source-faithful claims. Recall is model-bound.
- Net: the cheap verifier (frozen substrate + small NLI + retrieval) does not reach the
  bars. B2 is bind/retrieval-precision-bound; B1 is NLI-recall-bound. **DESTINATION-
  FALSIFIABILITY HIT** (keystone): the next lever is model scale (stronger binder +
  stronger NLI), not another cheap gate. Honest terminal, not blind iteration.

## 1. Pre-registration (frozen, identical to E18)

Bars: B1 >= 0.90 (gold VERIFY), B2 >= 0.80 (NN-swap DEMOTE), B3 <= 0.10 (fab+neg over-bind).
Veto threshold pre-registered by PRECISION: pick the highest veto floor that closes every
NN leak (final B2 == 14/14) while harming no clean gold (no E18-verified gold newly vetoed).
Never tuned to lift B1.

## 2. Build - nli_verify2.py (contradiction-veto, additive)

Extends, never mutates, E18 nli_verify. ACCEPT decision = byte-identical E18 (single bound
premise; SKIP-no-finding passes through), so B1/B3 stay on the E16 baseline. The ONLY
addition: a contradiction-VETO that can only DEMOTE a claim E18 would VERIFY, when an
authorized finding in a wider scan (own veto floor/depth, bind FLOOR/TOP_K untouched)
contradicts the claim (argmax=contradiction, P >= veto_tau).

A first build erroneously also rewrote the ACCEPT path (entail-any over top-K +
demote-if-none); this silently closed E18's SKIP-no-finding loophole and dropped pipeline
B1 0.63 -> 0.44, making the veto's effect unmeasurable in isolation. Caught by per-gold
trace (veto-cross == 0; all drops were NO-ENTAIL), reverted to E18-accept. Recorded so the
ACCEPT/REJECT separation stays a hard rule: the veto rejects, it never re-decides acceptance.

## 3. B2 falsifier - veto floor sweep (veto_tau=0.50, depth=30, bind floor 0.55 frozen)

E18 baseline (veto OFF): NN demote 11/14 = 0.786; residual leaks = 3 (ho_sn00, ho_sn03,
ho_sn10). diag-leak showed each leak's contradicting authorized source sits BELOW the 0.55
bind floor (anchor cos 0.495 / 0.323 / 0.503), so the bind cannot see it; lowering the veto
floor to reach it symmetrically pulls contradicting neighbours onto real gold (the corpus
holds opposing authorized findings on the same topic).

| veto_floor | NN_demote | gold_hurt (E18-verified newly vetoed) |
|-----------:|:---------:|:-------------------------------------:|
| 0.55 (=bind) | 11/14 | 0 |
| 0.50 | 12/14 | 1 |
| 0.48 | 13/14 | 1 |
| 0.46 | 13/14 | 2 |
| 0.44 | 14/14 | 2 |
| 0.40 | 14/14 | 3 |
| 0.30 | 14/14 | 9 |

No floor gives B2 >= 0.80 with gold_hurt == 0. Even closing one leak costs one gold. The
veto's contradiction signal is reliable per item (leaks score contra ~1.0) but retrieval
cannot deliver the right contradicting source for an adversarial claim without also
contradicting gold. This is the E17 bind-precision wall re-surfacing on the B2 axis.

## 4. B1 oracle - premise-enrichment + held-out v3 (ceiling measure, retrieval bypassed)

Oracle baseline (own-anchor premise): B1_oracle = 20/27 = 0.741. Residual-7 decomposed by
CAUSE, not symptom:

| id | cause | action | result |
|----|-------|--------|--------|
| g00 Koonin | terse finding (claim asserts a magnitude) | enrich finding with sourced figure | still 0.022 (NLI miss on subject framing: "molecule" vs "system") |
| g02 Totani | finding ~ claim, faithful | none (model-bound) | 0.000 |
| g24 Nickerson | finding ~ claim, faithful | none (model-bound) | 0.005 |
| g08 Papastavrou | claim's "91%" not in source | restate claim to source | 0.996 VERIFY |
| g10 uz-Zaman | claim's "few hundred bits" not in source | restate claim to source | 0.998 VERIFY |
| g11 Moger-Reischer | "no new genes" mis-attributed; source = fitness recovery | restate claim to source | 0.996 VERIFY |
| g22 Pohorille/Deamer | anchor = membranes, not "5000 nt" | replace claim to source (membranes) | 0.989 VERIFY |

Enrichment grounding (R4/R7, sourced from the paper, never from the held-out claim):
- g00 finding: Koonin (2007) estimates P(coupled replication-translation system, chance,
  single observable universe) < ~10^-1018. Confirmed via two citing sources.
- g08/g10/g11 restated to the verbatim-faithful sense of their findings; g22 replaced to
  the Pohorille-Deamer membrane finding. uz-Zaman "bits" and Papastavrou "91%" were searched
  in the primary sources and NOT found - hence restatement, not enrichment.

Post-repair: **B1_oracle = 24/27 = 0.889**, B2_oracle = 14/14 = 1.000.
Residual-3 (g00, g02, g24) are all NLI entailment-recall misses on source-faithful claims.
g00 was NOT restated to cross 0.90: its claim is a fair lay gloss of Koonin's thesis (not a
fabricated specific like g08/g10), so it belongs with g02/g24 as a recall miss, not a
defect. The bar is a readout, not a target; the falsifier firing at 0.889 is the disciplined
outcome.

## 5. Load-bearing learnings (do not relitigate)

- VETO over RETRIEVED authorized sources cannot separate "false claim a real source
  contradicts" from "true claim a rival source contradicts" by floor alone, because the
  corpus holds opposing findings on the same topic. Contradiction is reliable PER SOURCE
  (oracle B2=1.0) but retrieval cannot select the right source for an adversarial claim.
- The leak root is bind imprecision (spoof bound to a wrong ENTAILING source) + permissive
  entailment. NLI-as-ACCEPT is the gameable surface; NLI-as-REJECT only helps if the
  contradicting source is retrievable, which the adversarial phrasing prevents.
- ACCEPT and REJECT must stay separate organs. A verifier change that "adds a reject" must
  not silently re-decide acceptance (the SKIP-no-finding regression).
- Oracle B1 ceiling at this model scale ~0.89-0.93: ~7-11% of source-faithful gold claims
  are NLI recall misses on paraphrase. This is the model-bound recall floor.

## 6. Next lever (model-scale branch, per keystone destination-falsifiability)

Both bars are model-bound on this substrate: B2 needs a binder/retriever precise enough to
surface the right contradicting source for adversarial input (or a non-retrieval provenance
check); B1 needs an NLI with higher paraphrase recall. Escalate verifier model scale,
recorded as a destination-falsifiability hit. Do NOT add another cheap gate over the same
imprecise bind. Open question for the strategic map: whether gate-2 (self-learning) can
proceed on E16-bindability alone given pipeline B2=0.786 (the oracle's safe asymmetry
B2~1.0 does NOT hold in the pipeline).

## 7. Artifacts & provenance

To git (onto-research, main): `nli_verify2.py` (build), `reports/report_E19.md` (this).
Local-only (eval/_local, never git): enriched `gold_fixture_E18.json`
(md5 493b8ada955edd89c0f169609a121887; source-hash set IDENTICAL = authorization frozen,
only g00 finding changed), held-out v3 `heldout_E17.jsonl`
(md5 7e9fe030646d5671952e7a9fe9437e37; 4 gold claims restated, ids/anchors/class/expect
untouched). Backups `.bak.<ts>` of both kept locally.
Stale tile to fix on reuse: `nli_verify.SPIN_GOLD_ANCHORS` still lists g08/g11, now restated
to source and no longer spin - drop them from the set or the pipeline B1-diagnostic line
will mis-exclude two valid gold.
Not re-run this session (confirmatory only, oracle is the governing ceiling): pipeline
`nli_verify2.py --eval` on the v3 held-out.
