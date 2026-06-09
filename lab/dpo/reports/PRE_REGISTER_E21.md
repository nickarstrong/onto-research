# PRE_REGISTER_E21 — binder-escalation, SAME E20-B gate (frozen)

Status: PRE-REGISTERED. No post-hoc edit to gate, threshold-rule, hypothesis, or falsifier.
Lineage: E20-B NO-GO (false-accept 0.467, B2 0.933 non-degenerate, 14/14 leaks VERIFIED
retrieval-bound). Pre-registered branch (PRE_REGISTER_E20.md): FAIL + residuals retrieval-bound
-> escalate the BINDER/retriever (NOT NLI), re-run SAME gate.

## 0 ONE-LINE THESIS
A stronger pairwise binder is applied BEFORE authorize on the SAME retrieve->authorize path.
SAME safety gate, no bar edit. R6 bet: it will NOT move false-accept, because the leak is
topical-bind != claim-support; the test is the terminal falsification of bindability-only.

## 1 GATE (frozen, byte-identical to E20-B; R6 — bar is a readout, not a target)
- SAFETY GATE (PASS criterion): false-accept <= 0.10  ==  B1 spoof-demotion >= 0.90.
- B2 (faithful-claim yield / recall) and B3 reported, NOT gated.
- No bar edit. No restating a fair-gloss claim to cross the bar (§5 forbidden).

## 2 LEVER (chosen, STEP 0 closed)
Cross-encoder reranker over the top_k semantic candidates, pairwise (claim x source), applied as
a pre-authorize re-rank + threshold. Frozen verify_E16 / gold_retrieve / semantic_retrieve logic
UNTOUCHED; binder lives in a NEW script. Cosine floor (0.45) NOT touched.
- Model: cross-encoder/ms-marco-MiniLM-L-6-v2 (NLI-free passage-ranking cross-encoder).
- NLI-free is mandatory: E21 is "stronger retriever, NOT NLI" (E18/E19 NLI = NO-GO). The lever is
  a ranking-quality improvement; the hypothesis is precisely that ranking quality cannot fix a
  claim-support gap.

### 2a FALSIFIABILITY GUARD (load-bearing — without it the null is degenerate)
The reranker MUST score a signal NOT collinear with the cosine floor it sits in front of. A joint
claim x source cross-encoder attends to both jointly (can in principle detect that a topically-near
spoof is not claim-supported) -> false-accept CAN drop in principle -> falsifier is live. A pure
topical/relevance score collinear with bi-encoder cosine would reproduce the bind by construction
-> null tautological -> REJECTED design. Implementation must confirm rerank scores decorrelate from
the bi-encoder cosine on the eval set (report Spearman rho; rho ~ 1.0 = degenerate lever, void run).

### 2b THRESHOLD RULE (frozen — prevents fit-to-bar / R7 contamination)
The rerank threshold is the ONE new free parameter. It is fixed by a deterministic pre-registered
rule, NOT swept against the safety gate:
- Rule: select the MOST CONSERVATIVE (highest) rerank threshold that holds B2 (recall) >= 0.90.
- Selection peeks ONLY at recall (reported, non-gated). false-accept is read as the dependent
  variable at that frozen operating point.
- No sweep of the threshold against false-accept. No second pass. One operating point, pre-committed.

## 3 INPUTS (frozen, md5 verified before run — md5 inputs every run)
- gold_fixture_E18.json   md5 493b8ada955edd89c0f169609a121887   (E20-B/E21 fixture; INJECT explicitly)
- heldout_E17.jsonl       md5 7e9fe030646d5671952e7a9fe9437e37   (v3, frozen baseline)
- Drive via an INJECTING runner (run_E20B.py pattern). Bare verify_E16 --eval is UNSAFE (default
  fixture 732abc05 + unset floor + no preload). md5 inputs first.

## 4 ENV-WART (REQUIRED, set BEFORE run)
- ONTO_RETRIEVE_FLOOR = 0.45    (E16-locked; code default 0.55 is a FOOTGUN)
- KMP_DUPLICATE_LIB_OK = TRUE   (Arrow-SEH recovery)
- new binder script imports pyarrow as line 1 BEFORE torch (dodges pyarrow access-violation in _get_model).
- Fold the two frozen-substrate footguns into the NEW script (NOT into frozen code):
  semantic_retrieve FLOOR default 0.55 -> 0.45 ; pyarrow preload (try/except cannot catch the OS SEH).

## 5 R6 HYPOTHESIS (falsifiable, frozen)
A stronger retriever surfaces the SAME on-topic authorized source the spoof is paraphrastically near
-> predicted NOT to move false-accept (leak = topical-bind != claim-support).
- FALSIFIER: false-accept drops <= 0.10 -> hypothesis wrong, bindability holds (E21 PASS).
- Confirmation (expected): false-accept stays > 0.10.

## 6 DECISION RULE (frozen; R8 bounds — three outcomes, two interpretations)
- PASS  (false-accept <= 0.10): falsifier fires, bindability+reranker is sufficient. -> bindability+
  reranker becomes the gate-2 rejection-sampling selector; design the RFT self-sample loop
  (generate K -> bindability-accept -> RFT on accepted), NLI dropped. (NEXT+1)
- FAIL, NO MOVEMENT (false-accept ~ 0.467, +- noise): R6 confirmed. Lever-direction wrong: ranking
  quality is not the bottleneck. Bindability primitive insufficient for gate-2 false-accept safety
  -> TERMINAL for the cheap-Entity substrate -> escalate substrate (model-scale), reopen NORTH STAR
  scope (confirm before committing).
- FAIL, PARTIAL MOVEMENT (e.g. 0.467 -> 0.20-0.30, still > 0.10): lever direction right, substrate
  too weak. Reranker helps but cheap-Entity substrate caps separation. -> same escalate-substrate
  route, but interpretation = substrate-bound not primitive-dead. Report movement magnitude as the
  diagnostic separating "lever-wrong" from "substrate-too-weak".

## 7 OUTPUTS
- reports\report_E21.md (B1 safety gate; B2/B3 reported; rerank-vs-cosine Spearman rho; movement
  magnitude vs 0.467; decision per §6).
- E21 binder script (NEW; frozen substrate untouched).
- Both -> git add reports + scripts -> single -m commit -> push onto-research main.
  Weights / bait / held-out NOT public.

---
*E21 pre-register · same gate as E20-B · lever + threshold-rule frozen · falsifier live*
