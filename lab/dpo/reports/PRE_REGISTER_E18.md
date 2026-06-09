# PRE_REGISTER_E18 - NLI claim-support layer above frozen E16 bind

Status: FROZEN before eval. Falsifier = the three bars on the frozen held-out, as-is.
Provenance: E17 NO-GO terminal (bindability-only cannot separate topical near-miss / on-topic
over-claim). E18 adds an entailment gate ABOVE retrieval. This is NLI-as-secondary-check on an
already-bound authorized passage (keystone sec 4), NOT NLI-primary on unbound claims.

## H (falsifiable)
An entailment gate over the frozen E16 bind separates faithful gold claims (ENTAIL from their
source finding) from on-topic over-claim / NN-swap spoofs (NEUTRAL/CONTRADICTION) that bindability
alone scored as equidistant (E17). If it cannot, entailment is unreliable at this model size.

## Mechanism (verify path)
resolve'(claim):
  1. E16 bind (FROZEN: verify_E16 / gold_retrieve / semantic_retrieve, byte-identical) ->
     authorized hit OR no-bind.
  2. no-bind  -> DEMOTE  (unbindable; identical to R4 behaviour for fab + true-but-uncovered).
  3. bind     -> premise = hit.finding (enriched fixture). VERIFY iff
         argmax(NLI(premise=finding, hypothesis=claim)) == ENTAILMENT  AND  P(entail) >= tau.
        else DEMOTE.

## Model
cross-encoder/nli-deberta-v3-small, CPU. Chosen over MiniLM-NLI for stronger near-miss separation;
held-out n=75 -> latency irrelevant. CPU only; KMP_DUPLICATE_LIB_OK=TRUE; faulthandler in
semantic_retrieve; import order torch -> pyarrow -> transformers. Run with `python`.

## Premise source (enriched fixture gold_fixture_E18.json :: finding)
- 27 of 30 gold anchors carry `finding`: 5 provenance=search (author abstract, web_search this
  session: Shannon, Axe 10^77, Papastavrou cross-replication, uz-Zaman promoter, Moger-Reischer 80%),
  22 provenance=canonical (established landmark finding, NO invented specifics).
- 3 anchors NULLED (R4 no-source-found, not fabricated): 10.1101/2024.10.11.617851 (Gianni QT45),
  10.1016/j.isci.2023.107500 (Sandberg syn3A), 10.1038/ng1659 (Kun 2005). Excluded from NLI.
- source / locator / claim_key + sha256(source) authorization UNCHANGED (asserted in build).

## NLI adjudication set (subset of frozen heldout_E17.jsonl - held-out NOT regenerated)
- gold-with-finding   : 27 of 30  (3 nulled anchors dropped)         -> expect VERIFY
- NN-swap-with-finding : 14 of 15  (Gianni anchor nulled -> ho_sn06 dropped) -> expect DEMOTE
- fab (15) + negctrl (15): bind==0 at retrieval, never reach NLI     -> expect DEMOTE
NLI only adjudicates the BOUND set (gold + NN-swap). fab/negctrl are a bind-stage control.

## Threshold tau
Chosen in sanity_E18 by the SAME precision constraint as E17: pick tau at the smallest value where
NN-swap over-bind == 0 (NN-swap DEMOTE-rate == 1.0 among adjudicated), NOT tuned to maximise B1.
tau frozen before eval; printed in the report.

## Bars (FROZEN, identical to E16/E17)
- B1: ENTAIL-rate (VERIFY) on gold-with-finding   >= 0.90
- B2: DEMOTE-rate on NN-swap-with-finding          >= 0.80
- B3: over-bind on fab + negctrl                    <= 0.10
PASS = all three on the frozen set as-is. No mid-stream redefinition of the bar.

## KNOWN LIMITATION (pre-declared, R15) - diagnostic, not a movable bar
Some frozen gold held-out claims carry framing beyond their source:
- 10.1038/s41586-023-06288-x: held-out "no genuinely new genes"; source finding = fitness recovery
  (~80% over 2000 gens). Source does not assert "no new genes" -> faithful finding may NOT entail.
- 10.1073/pnas.2321592121: held-out asserts "~91% fidelity ... never self-replication"; source =
  cross-replication of a separate ribozyme, no self-replication. The "never self-replication" part
  is faithful; the "91%" specific is not in the verified finding.
These will likely DEMOTE under a faithful verifier (correct R4 behaviour: a claim is VERIFIED only
if its source entails it). Reported as B1_raw (all 27) AND B1_faithful (gold subset whose claim is
fully entailable from source). PASS uses B1_raw. Sub-bar B1 attributable to held-out spin feeds
held-out v3 (tighten gold claims to source); it is NOT counted as an NLI failure.

## Verdict logic
- GO  : B1>=0.90 AND B2>=0.80 AND B3<=0.10 -> gate 2 (self-learning) opens; NLI-gated verifier
        becomes the rejection-sampling selector (now safe against topical near-miss).
- NO-GO: B2<0.80 (near-miss survives entailment) OR B1<0.90 not explained by held-out spin ->
        entailment unreliable at this model size -> escalate verifier model scale. Terminal, recorded.

## Artifacts
build_fixture_E18.py + gold_fixture_E18.json (enriched, authorization frozen) -> git.
nli_verify.py (wraps frozen E16) + sanity_E18.py (extends sanity_E17) -> pending frozen interface.
report_E18_nli.md -> git on verdict.
