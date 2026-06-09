# PRE_REGISTER_E26 - contradiction-veto reject primitive (PIVOT)

Status: FROZEN pre-data. Authored 2026-06-10, before run_E26_probe.py exists and before any E26 readout.
Supersedes nothing already committed; this is the operative decision for E26. Any stale E22-era decision
fork ("FAIL_PARTIAL -> architectural -> reframe") carried in older report boilerplate is NOT operative here.

## 0 CONTEXT (why this experiment)
E25b PIVOT readout (committed 7270734): with_finding 27->90 / from_finding 51->109, GATE fa PLATEAUED at
0.20 (movement 0.267, byte-identical E24/E25). Content-binding is NECESSARY (fa 0.467 E21 -> 0.333 E22 ->
0.20 E24) but INSUFFICIENT: the pure-entailment reject organ (premise=finding, hypothesis=claim,
bart-large-mnli, read P(entailment)) has an architectural ceiling fa~0.20 > gate 0.10. Coverage was
falsified as the limiter (gold-content n=74 >= 60, sep flat/down). PIVOT: change the reject SIGNAL, not the
coverage. E26 PRIMARY = contradiction-veto.

## 1 SUBSTRATE (frozen; do not author new data)
- fixture : eval/_local/gold_fixture_E25b.json  md5 4a45f52883a802e8d8d1d5ff5d185bdb (E18 + 63 real-
            provenance findings: 37 broad batch1 + 26 targeted batch2). LOCAL/gitignored (bind-corpus
            privacy; public leak -> pretrain contamination of the measurement).
- model   : bart-large-mnli (cached). Read P(contradiction); contradiction idx READ from id2label, NOT
            hardcoded. Assert exactly one contradiction label in the card.
- env     : ONTO_RETRIEVE_FLOOR=0.45 (E16-locked; code default 0.55 is a footgun) ; KMP_DUPLICATE_LIB_OK=TRUE
            (Arrow-SEH). Runner imports pyarrow line 1 BEFORE torch. NEVER sentence_transformers.
- code    : NEW file run_E26_probe.py. Reuses run_E25_probe.py skeleton byte-identical for
            ce_load / candidates_with_cosine / precompute and the frozen imports (verify_E16, gold_retrieve,
            semantic_retrieve). Frozen substrate UNTOUCHED. Footgun fixes (FLOOR default, pyarrow SEH) folded
            into run_E26 only, never into frozen files.

## 2 PRIMITIVE (what is being tested)
contradiction-veto. For each claim: retrieve authorized premises (same retrieval as E25, floor 0.45). For
each retrieved premise run bart-large-mnli (premise=authorized finding, hypothesis=claim) and read
P(contradiction). Per-claim REJECT score = MAX over candidate premises of P(contradiction). Veto/demote the
claim when REJECT score >= threshold C.
- Direction: this is a REJECT signal (high contradiction -> reject), the mirror of E22-E25 where high
  entailment -> accept.
- Max-based on purpose: gate fa is max-over-candidates and confound-immune; sep (p50) is confounded by
  finding phrasing-quality (proven E25b: sep collapsed 0.084->0.008 under added descriptive findings while
  the max-based gate held). E26 reads the gate, not sep.

## 3 HYPOTHESIS (H1)
Cue-stripped + entitied spoofs are CONTRADICTED by the real finding even when they are not entailed by it.
So contradiction-max separates spoof (reject) from gold-content (accept) in the region where entailment-max
plateaued (fa 0.20). If true, contradiction-veto pushes fa below the 0.10 gate at iso-recall.

## 4 METRICS + GATE (FROZEN pre-data, identical bars to the entailment ladder)
- GATE      : false-accept fa <= 0.10  (equivalently B1 >= 0.90). fa read as MAX over candidates. NOT sep.
- iso-recall: pick veto threshold C at B2 >= 0.90 (gold recall held). NEVER post-hoc fish a lower-recall C.
- guard     : decorrelation guard (rho) reported; veto must not be a relabeling of the bind score.
- power     : gold-content n >= 60 (E25b had 74). from_finding asserted > 0 in log (E23 VOID-by-construction
              guard: from_finding=0 => fixture dropped `finding` => byte-identical rerun; assert in log).

## 5 TRUST GATES (any fail => VOID, no verdict)
- baseline-sanity : T=-inf (no veto) reproduces fa 0.467, reproduced=True. Model-independent; gates trust
                    every run.
- degenerate      : degenerate=False (veto not collapsing to accept-all or reject-all).
- contradiction_idx: READ from id2label, single contradiction label asserted (verify CONTENTS, not md5).
- fixture md5     : == 4a45f52883a802e8d8d1d5ff5d185bdb, checked at load.
- from_finding    : > 0, asserted in log.

## 6 DECISION (pre-registered, frozen; the ONLY operative fork for E26)
- fa <= 0.10 at B2 >= 0.90   -> PASS. contradiction-veto IS the reject primitive. Integrate + full gate
                                (next+1: wire reject organ, re-run full gate + 3 secondaries).
- 0.10 < fa < 0.20           -> PARTIAL. Tune veto threshold C / direction, ONE more readout. No new data.
- fa ~0.20 (plateau, movement byte-identical to E24/E25) -> contradiction signal ALSO insufficient ->
                                FALLBACK branch (sec 8).

## 7 FALSIFIER (what disproves H1)
contradiction-veto does NOT push fa <= 0.10 at iso-recall B2 >= 0.90. That falsifies "contradiction signal
is sufficient for a pure-NLI reject organ on this substrate" and routes to FALLBACK.

## 8 FALLBACK (separate pre-register, NOT authorized by this document)
Taken only on falsifier:
- (a) passage-NLI : premise = full retrieved PASSAGE (not the finding-sentence). Requires authoring passage
                    text per bound record -> larger content step -> TOMMY GO required.
- (b) two organs  : ACCEPT and REJECT as separate organs (NORTH STAR reframe; non-retrieval reject
                    primitive).
Gate fa <= 0.10 stays frozen on every fallback branch.

## 9 REVERSIBILITY / COST
Reuses existing E25b fixture + same model, no new data, frozen substrate untouched. REVERSIBLE -> NO Tommy
go required to RUN. Tommy go is required ONLY if the falsifier routes to passage-NLI (passage authoring).

## 10 RUN COMMAND (exact)
    cd C:\Projects\onto-research\lab\dpo
    $env:ONTO_RETRIEVE_FLOOR="0.45" ; $env:KMP_DUPLICATE_LIB_OK="TRUE"
    python run_E26_probe.py --fixture eval/_local/gold_fixture_E25b.json --fixture_md5 4a45f52883a802e8d8d1d5ff5d185bdb

## 11 FILING
run_E26_probe.py + reports\report_E26.md -> git add (these two only) -> single -m commit -> push
(onto-research, main). report_E26 must cite ONLY the sec-6 decision, never the stale E22-era fork. Fixture /
worksheets / weights stay LOCAL (gitignored).
