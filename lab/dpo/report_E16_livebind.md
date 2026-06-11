# report_E16_livebind.md -- E16 LIVE-BIND (pack v95, TYPE C BUILD)

STATUS: ADAPTER BUILT + G2 GREEN. Behavioural L4 smoke DEFERRED (REQUIRED INPUT b absent +
        DeBERTa/CUDA pod-side). This is the TYPE-A fallback the pack prescribes when (b) is
        absent: build the adapter + G2-gate only; do NOT fake a behavioural run.

## What was wired
Deterministic adapter `gold_adapter.py`: ONTO-GOLD/literature/extractions/*.json -> the EXACT
GoldStore record shape (read off the committed organ, byte-verified):
  corpus = { "manifest_files": [sha256(source), ...],
             "records": [ {claim_key, source, locator, finding}, ... ] }
No model. One pass. Same record shape as the frozen E25b fixture; DIFFERENT path/content -- this
is the OPERATIONAL bind-corpus, NOT a re-derivation of E25b (SPEC sec3). The E25b fixture and its
0.0333 anchor are untouched and remain the separate drift sentinel.

Record contract verified against committed organ (md5 == pack manifest):
  verify_E16_L4.py  544c9a7b8c3189943b010a642efc0d86
  gold_retrieve.py / semantic_retrieve.py / run_E37_probe.py / emit_E42scale_readout.py (fetched
  from onto-research/main, byte-exact). GoldStore requires claim_key+source (KeyError otherwise),
  locator!="" for is_authorized; L4Bind reads record["finding"] keyed by record["source"] (=>
  source must be unique per finding); build_index embeds f'{claim_key} {source}'.

## G2 gate (CONTENTS, not md5) -- GREEN
  files in           : 34
  records out        : 366
  manifest_files     : 366  (== set(sha256(source)), no orphan/extra)
  unique source      : 366  (path-suffixed, finding_by_source 1:1, no collapse)
  every rec source   : non-empty   PASS
  every rec locator  : non-empty   PASS  (structural GOLD address, never fabricated)
  every rec finding  : >= 4 words  PASS
  sha256(source)inman: ALL         PASS
  exclusions         : 0  (every file yielded >= 1 finding leaf)
  VOID-by-construction: NO (records>0, contents real, manipulation-bearing)

Per-file finding counts span 4..27 (lit_4.1_TOUR=27, lit_2.7_ABEL=4). Heterogeneous source
schema (dict+id+doi | dict+reference | dict bare | source-as-string RU | source MISSING) handled
by an explicit prioritized cite map; source-MISSING files (5.1/5.2/5.3/6.0/FI-02/1.1) fall back
to extraction_id + target_source, NOT dropped, NOT faked.

## FROZEN field-map (load-bearing, this session)
  finding   = leaf text T (quote|claim|finding|admission|statement|insight|...), >= 4 words
  locator   = f"{extraction_id}::{json_path}" (+ " | " + explicit location sibling if present)
              -- real, deterministic, tamper-evident structural address; resolves the G2
              "every rec locator" requirement WITHOUT fabrication (corpus carries ~no explicit
              page/section fields; the JSON path IS the verifiable locator).
  source    = f"{paper_cite} #{json_path}"  (unique per finding)
  claim_key = T  (finding text as retrieval key: retrieve embeds claim_key+source, NLI compares
              claim vs finding -- coherent retrieval/premise pairing)
  paper_cite= first of: source.id -> source.doi -> source.reference/primary_reference ->
              RU top-level author+year -> source-as-string -> extraction_id ; enriched with
              author(s)+year+title when present.

## FLAGS (R1/R10)
1. COUNT MISMATCH: pack v95 sec0/sec1 declared "44 per-paper records" for the live module; the
   on-disk module has 34 extraction files (json=34, probed). Build ran over the real 34. Pack
   counter is stale, not the corpus. -> fix the v95->v96 count to 34.
2. LOCATOR is path-derived, not bibliographic page/section (the source data carries explicit
   location only on a handful of leaves). This is honest and G2-clean, but means a "locator"
   here = "where in the GOLD JSON", not "page N of the paper". Note for any downstream consumer
   that treats locator as a human page cite.

## FALSIFIER (R6)
This build is WRONG if, when wired on a pod with the real embedding model + a labelled smoke set:
  (a) GoldStore(corpus) / build_index raise on any record (shape mismatch), OR
  (b) a known-contradiction claim against a gold finding does NOT yield CONTRADICTED, OR
  (c) a known-clean gold claim yields CONTRADICTED (false veto).
Until (a)-(c) are run, the adapter is G2-proven but behaviourally UNCONFIRMED.

## DEFERRED to next session (pack v96)
  STEP 4 wire   : GoldStore(gold_corpus_live.json) ; verify_E16_L4.verify_item unchanged.
  STEP 5 smoke  : REQUIRED INPUT b -- >=1 known-contradiction claim -> assert CONTRADICTED ;
                  >=1 clean gold claim -> assert VERIFIED. Needs DeBERTa-v3-large-mnli (CUDA,
                  pod). Anchor 0.0333 NOT expected here (different corpus) -- E25b stays the
                  frozen guard; do NOT re-derive E25b from live GOLD.

## Privacy (§3.2)
  COMMIT (public onto-research): gold_adapter.py + this report (code + G2 readout; no GOLD text).
  LOCAL ONLY (gitignored, eval/_local): gold_corpus_live.json -- it is GOLD-derived corpus
  content; NEVER to public git.
