# GATE_selflearn -- PRE-REG DELTA: retrieval-wiring fix (BUILD-FRONT #1)

Amends: GATE_selflearn pre-reg v2 (sealed 5ee4402f).
Scope: wiring fix ONLY. Sealed BEFORE the rebuilt gate run (a SEPARATE session).
No re-fire over the FROZEN trace 9c960429. F1/F2/F4 definitions unchanged.

## 1 Root cause witnessed (against on-disk bytes)
TYPE B verdict on trace 9c960429 (40 rows): F3 FAIL, `retrieval_hit` sum = 0 across all 40 rows.

Cause located by source audit (controller.py / generate_step6.py / daemon.py) + disk state:
- The witness mechanism is SOUND -- side-channel write (generate_step6 L91
  `generate.retrieval_hits = hits`), object-identity-preserving read (controller L183
  `getattr(generate, "retrieval_hits", [])`), aggregation/emit (L214/L230). A
  trace-recording bug (hypothesis a) is REJECTED.
- `retrieval_hit == 0` therefore means `len(retrieved) == 0` every cycle, i.e.
  `retrieve(topic, confirmed, k)` returned `[]` for all 40 cycles.
- DISK: `o0_verdicts_curated.jsonl` = 0 lines / 0 bytes / md5 d41d8cd9 (empty;
  GATE-SETUP cold-start zeroing). `DOMAIN_TOPICS` = 100 (non-empty).
- Two compounding wiring defects:
  1. **Wrong feed.** The conditioned proposer retrieved over `o0_verdicts_curated.jsonl`,
     which nothing populates during a run. `absorb()` writes verify-confirmed knowledge to
     `eval/o0/o0_verdicts.jsonl` (Accumulator) -- a different file.
  2. **Boot-frozen snapshot.** `confirmed = load_confirmed(curated_path)` was loaded ONCE in
     `live_adapters` (built in `daemon.main` before the tick loop). Even a populated pool
     would never refresh within-run.
- Net: a cold-started conditioned run can NEVER witness retrieval of knowledge it absorbs
  during the run -> `retrieval_hit` is pinned at 0 structurally. F3=0 was honest, not noise.

## 2 Fix (single site; firewall preserved)
Patch in `controller.live_adapters` conditioned branch + one module-level helper
`_live_retrieve_fn(trail_path)`:
- Retrieval feed = the LIVE ABSORB trail `eval/o0/o0_verdicts.jsonl` (== the Accumulator path
  `absorb()` writes to), re-read PER `generate()` call. `load_confirmed` filters to
  verdict==ABSORB, so the feed = verify-confirmed knowledge only.
- `confirmed=[]` passed to the sealed proposer (the per-call live read supersedes the boot snapshot).
- `curated_path` retained in the signature for API stability (daemon call unbroken); now unused.

Firewall UNCHANGED and proven:
- `generate_step6.py` byte-identical (md5 5e9ab2e5) -- sealed proposer untouched.
- `verify()` block byte-identical pre/post patch (md5 09cd1d0c) -- external oracle never sees
  retrieval/GOLD; emitted dict stays EXACTLY {topic, claim}.
- No circular confirmation: `verify()` checks claims against external oracles
  (temporal Wikidata + Crossref), independent of the absorb trail the proposer reads.

Smoke (save->run->restore isolation, no Ollama/net, FROZEN trace untouched):
`retrieve_n=1  hits=[1,1]  sum=2  emit_keys_ok=True` -> PASS (retrieval_hit>0 on a synthetic
populated trail through the real patched feed + real sealed proposer).

## 3 Amended F3 falsifier (the only measurement-facing change)
Prior F3 read the whole run as one pool: sum(retrieval_hit) over 40 rows = 0 -> FAIL. With the
fix, the COLD WINDOW is honestly empty: a topic's ABSORB record cannot be retrieved until that
topic is revisited (proposer iterates DOMAIN_TOPICS cursor-stable; at n/tick over 100 topics the
first revisit occurs after the first cursor wrap). Reading the cold window as failure would be a
mis-target (same class as the F1 saturation defect).

Amended F3 PASS condition (rebuilt conditioned gate run):
- (F3a) sum(retrieval_hit) over the full run > 0 (conditioned arm retrieval witnessed), AND
- (F3b) retrieval_hit==0 is permitted ONLY in the pre-first-revisit cold window; from the first
  topic revisit onward, retrieval_hit>0 on >=1 cycle whose SELECTed topic has a prior ABSORB on
  the same topic. BLIND arm structural 0 throughout (unchanged, prereg L53).

F3 FALSIFIER (what disproves the fix): rebuilt conditioned run STILL shows
sum(retrieval_hit)==0 across the full run, OR retrieval_hit stays 0 after the first topic revisit
despite >=1 same-topic ABSORB present in `eval/o0/o0_verdicts.jsonl` -> feed wiring still wrong.

## 4 Out of scope (separate build-fronts, one session each)
- BUILD-FRONT #2: SELECT free-rotation (worst-first locked top-2; `empty-hedge` never selected -> floor FAIL).
- BUILD-FRONT #3: F1 baseline redesign (early window already saturated vs baseline 0.7).
- The rebuilt gate run + its TYPE B read are ALWAYS further-separate sessions (never build+eval together).
