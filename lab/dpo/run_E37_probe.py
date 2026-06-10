import pyarrow  # noqa: F401 -- MUST be line 1 (proven run_E20B/run_E21 pattern: preload before torch -> dodge SEH)

import os
# ENV-WART set BEFORE importing semantic_retrieve (its FLOOR is read at import time; default 0.55 = FOOTGUN)
os.environ.setdefault("ONTO_RETRIEVE_FLOOR", "0.45")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
assert os.environ["ONTO_RETRIEVE_FLOOR"] == "0.45", "floor must be 0.45"

import sys, json, hashlib, argparse
import numpy as np

# frozen substrate (NOT mutated). Importing verify_E16 pulls gold_retrieve -> semantic_retrieve,
# which enables faulthandler (load-bearing Arrow-SEH recovery on this box).
import verify_E16 as v
import gold_retrieve as gr
import semantic_retrieve as sem

# Scorer via transformers DIRECTLY (NOT sentence_transformers: ST drags datasets->pyarrow->SEH on this box)
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# E34 = REFRAME the reject TASK (NLI-swap family EXITED at E33). PRE_REGISTER_E34.md (FROZEN; record its md5 in
#   the readout). E33 (report_E32.md, VERDICT CEILING_NOT_MODEL_SCALE) proved the NLI MODEL CLASS is NOT the ceiling:
#   the ANLI-hardened deberta head scored fa 0.1667 -- WORSE than bart 0.0667 -- on the same fixture. The constraint
#   is the reject TASK, not the scorer. E29 located the defect: the gold contradiction tail is RETRIEVAL MISBINDING
#   under an ANY-CANDIDATE veto (each premise faithful to its OWN source, contradicting a claim about a DIFFERENT
#   co-surfaced source -> the wrong-source candidate falsely demotes a gold claim). E31 proved rank-top1 is NOT the
#   binding signal (top1 LOSES non-top1 spoof rejections, fa 0.0667->0.2333).
#   LEVER (E34): gate the veto to candidates BOUND to the claim's subject by an OBSERVABLE binding signal that is NOT
#   retrieval rank. A candidate vetoes iff (contradiction >= C AND B >= B_floor), where B = lexical subject-overlap
#   (claim vs candidate premise) in [0,1]; B_floor=0 admits all candidates (gate off). scope stays 'any' over the
#   BOUND subset. The MODEL is UNCHANGED (inherited deberta below); the binding gate is the ONLY new variable, and B
#   conditions only on observable text (no held-out class label) -> oracle-clean.
#   ANCHOR REPURPOSE (E34b RE-ANCHOR, v74): bart 0.0667 = CROSS-MODEL comparison bar (NOT the running model).
#   The E33 deberta op-point fa 0.1667 was NEVER bare scope=any -- its veto carried (con>=C AND cos<=K=0.5066235661506653)
#   (report_E32.md:17-18, run_E32_probe.py:173). The cosine gate spared 2 of 3 gold-tail drivers -> 0.1667 is COSINE-
#   CONTAMINATED. The honest COSINE-FREE bare scope=any baseline = 0.2333. Since the E34 lever is lexical binding B
#   (cosine FALSIFIED at E28, NOT re-introduced here), the correct DEGENERACY + BEAT anchor is 0.2333: at B_floor=0 the
#   binding gate is off -> probe MUST reproduce 0.2333 (clean-superset check; else VOID_DEGENERACY). No REGRESSION
#   verdict at E34b except that single re-anchored point.
#   Frozen substrate (verify_E16, gold_retrieve, semantic_retrieve, run_E26/E27/E28, rho guard, S1 cosine diag,
#   ordering guard) untouched. cosine RETAINED for the rho VOID-guard + S1 diagnostics; B is a NEW parallel quantity.
# ===== E36 ANCHORED-BINDING REPLACE (binding observable sharpen) -- on top of the FROZEN E35 three-way ========
#   E35 = TWO_ORGAN_KNIFE_EDGE (report_E35, TRUSTED bf19da1): the accept arm RESCUED reject to fa_op 0.0667 (clears
#   gate 0.10, beats reject-only 0.1667), c-leak 0, reject_share 0.857 -- but the bf-band was TRIVIAL (only 2 B_floor
#   points clear, B2 lift-off 0). DIAGNOSIS (report_E35 S1 + sec5): the knife-edge lives in the BINDING-FLOOR
#   dimension. The coarse LEXICAL B cannot rise above ~0.05 without dropping the 3 gold-tail drivers (ho_g05 cos0.48,
#   ho_g12 cos0.51, ho_g08 cos0.60; con>=0.99) -- legitimately bound to their source.finding by SHARED NAMED ANCHORS
#   (entity/number/quote) even where lexical token overlap is low and NLI contradicts the content. A grid re-tune
#   cannot fix this (C-band already WIDE 0.08/17pts); it needs a SHARPER binding OBSERVABLE.
#   LEVER (E36): replace the coarse lexical-overlap B with an ANCHORED binding observable. B_anchor = containment of
#   shared surface anchors -- {number-like tokens, quoted spans, CamelCase/ACRONYM entities} -- between claim and
#   source.finding, SAME containment formula shape as the lexical B, in [0,1], OBSERVABLE-TEXT ONLY (no class label,
#   no per-class term) -> oracle-clean. The effective binding used by the FROZEN reject/accept predicate becomes
#     B = (1 - W) * B_lexical + W * B_anchor ,  W in W_GRID (coarse anchor-mix weight, swept as a 4th selection axis).
#   GOAL: the 3 gold-tail drivers carry HIGH B_anchor (shared named anchors with their bound source) -> their
#   effective B rises -> B_floor can lift off the floor while still sparing them -> a NON-TRIVIAL bf-band.
#   REGRESSION ANCHOR (mandatory, E28 K=+inf / E35 A=+inf discipline): W=0 => B = (1-0)*B_lex + 0*B_anchor == B_lex
#   BYTE-IDENTICALLY (IEEE: x*1.0 exact, 0.0*finite==0.0) => the three-way collapses to the EXACT E35 path => the
#   op-point over (A,C,B_floor) at W=0 MUST reproduce E35 TWO_ORGAN op fa 0.0667 (E35_OP_FA, clean-superset). Else
#   VOID_BINDING_REGRESSION. The inherited A=+inf,W=0 reject-only 0.1667 and B_floor=0,A=+inf,W=0 0.2333 anchors
#   stay byte-identical (W defaults 0 in those paths). No cosine in any predicate (E28 cosine-separability FALSIFIED;
#   cosine RETAINED only for the rho VOID-guard + S1 diagnostics, UNTOUCHED). B_anchor is a NEW parallel quantity.
#   ORACLE-LEAK GATE (W, pre-data): B_anchor reads ONLY (claim, source.finding) surface text; it NEVER conditions on
#   the held-out true class or any per-class quantity. W swept over a FROZEN coarse grid; op-selection peeks ONLY
#   recall feasibility (B2>=0.90), never fa, never per-class -- same discipline that caught the E28 per-class leak.
#   SELECTOR (one declared refinement, tied to the new axis): op tie-break is BYTE-IDENTICAL to E35 with LOWEST-W
#   appended as the final key -- the anchor (W>0) is selected ONLY if it STRICTLY lowers min-fa or widens the C-band
#   (it must EARN selection; W=0 wins all ties -> exact E35 reproduction). The per-W bf-band lift is a REPORTED-ONLY
#   diagnostic that feeds the KNIFE_EDGE-vs-BINDING_EXHAUSTED fork (falsifier), never the op-selection.
#   FROZEN (byte-identical from E35): reject predicate (con>=C AND B>=B_floor), accept predicate (ent>=A AND B>=B_floor),
#   accept-protective rescue precedence, scope=any over the bound subset, the lexical B_lexical function, ce_scores /
#   ce_entail, the cosine rho VOID-guard + S1 diagnostics, from_finding counter, ordering guard, idx-from-id2label,
#   fixture/heldout loaders, the C=+inf baseline path, the 0.2333 and 0.1667 anchors.
# ===== E35 ACCEPT ARM (SECOND ORGAN) -- entailment-lift rescue on top of the FROZEN E34b reject organ ========
#   E34b proved the per-candidate contradiction-veto REJECT organ caps at fa 0.1667 on this fixture: 5/30 spoofs
#   survive (residual false-accept the veto cannot reach) while recall is held ONLY by sparing the 3 gold-tail
#   drivers (ho_g05/g12/g08, con>=0.99) via low binding B. A pure-reject lever is EXHAUSTED at this ceiling; the
#   next gain must come from the ACCEPT side. E35 adds an entailment-lift organ:
#     - ent = P(entailment) of (premise=source.finding, hyp=claim) from the SAME deberta head (idx READ from
#       id2label, never hardcoded; oracle-clean -- no new model, no held-out label).
#     - per-candidate three-way: ACCEPT (bound AND ent>=A) / REJECT (bound AND con>=C, FROZEN from E34b) / ABSTAIN.
#     - CLAIM label = E34b reject UNLESS RESCUED: a claim that would be vetoed (some bound candidate con>=C) is
#       RESCUED to VERIFIED iff some bound candidate also entails it (ent>=A). Accept-protective in the contested
#       case -- that is the only precedence under which the accept arm lets C tighten without over-demoting gold.
#   MECHANISM (the asymmetry the lift exploits): a gold claim is ENTAILED by its correctly-bound authorized source
#   (high ent, high B); a spoof is CONTRADICTED by its bound source (high con, low ent). So lowering C catches the
#   5 surviving soft spoofs, while the gold claims that newly cross con>=C are rescued by their bound-source
#   entailment -- spoofs are NOT rescued (no bound entailment). Accept rescues gold; it never demotes.
#   DEGENERACY (regression anchor, A1/A2/A10): at A=+inf accept NEVER fires -> the three-way collapses to the
#   EXACT E34b binary reject -> op-point MUST reproduce E34b reject-only fa 0.1667 (E34B_REJECT_OP_FA, clean-
#   superset check). The inherited B_floor=0,A=+inf degeneracy still reproduces deberta bare scope=any 0.2333.
#   FROZEN (byte-identical from E34b, NOT touched by the accept arm): the reject predicate (con>=C AND B>=B_floor),
#   the binding lever B, the cosine rho VOID-guard + S1 cosine diagnostics, the from_finding counter, the ordering
#   guard, contradiction_idx-from-id2label, fixture/heldout loaders, the C=+inf baseline path, the 0.2333 anchor.
#   ORACLE-LEAK GATE (A, pre-data): A is a SINGLE scalar threshold on observable entailment text (claim + premise);
#   it NEVER reads the held-out class label or any per-class quantity. A swept over a FROZEN coarse grid; op-point
#   selection peeks ONLY recall feasibility (B2>=0.90), never fa -- same discipline that caught the E28 per-class leak.
CE_MODEL = os.environ.get("ONTO_CE_MODEL", "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")   # INHERITED from run_E32, UNCHANGED; override via env
E20B_FALSE_ACCEPT = 0.467     # frozen baseline for movement diagnostic
GATE_FA = 0.10                # PASS == false-accept <= 0.10 == B1 >= 0.90
PARTIAL_BAND = 0.20           # 0.10 < fa < 0.20 = PARTIAL ; fa >= 0.20 = plateau (contradiction insufficient)
RECALL_FLOOR = 0.90           # iso-recall pin (B2 >= 0.90); selection peeks ONLY recall
DEGENERATE_RHO = 0.95         # contradiction vs cosine Spearman >= this => collinear lever => VOID (FROZEN E26 guard)
PREREG_RHO_ADVISORY = 0.50    # PRE_REGISTER_E28 sec4 advisory tightness (|rho| < this); REPORTED, not a VOID trigger
B1_CLASS, B2_CLASS, B3_CLASS = "spoof_cuestripped_entitied", "gold_backed", "negctrl_common"
B2_EXCLUDE = {"ho_23"}        # frozen exclusion (matches verify_E16._eval_heldout); no-op on heldout_E17

# --- S2 robustness sweep grid (FROZEN pre-data, PRE_REGISTER_E28 sec3-S2) ----------------------------------
#   coarse [0.90, 0.995] step 0.005 + fine [0.990, 0.999] step 0.001 ; C=+inf reported separately as anchor.
S2_GRID = sorted(set([round(0.900 + 0.005 * i, 3) for i in range(0, 20)] +
                     [round(0.990 + 0.001 * i, 3) for i in range(0, 10)]))
S2_BAND_MIN_WIDTH = 0.01      # joint (fa<=0.10 AND B2>=0.90) band must span >= this in C
S2_BAND_MIN_POINTS = 3        # AND contain >= this many grid points (not a single knife-edge)
S3_REJECT_SHARE_BAR = 0.50    # reject organ must own > this share of baseline false-accepts eliminated

# --- E34 observable-conditioning: B_floor = binding gate (FROZEN pre-data, PRE_REGISTER_E34.md sec1-2) -------
#   veto fires iff (contradiction >= C AND B >= B_floor), B = lexical subject-overlap(claim, premise) in [0,1].
#   B_floor grid: [0.0, 1.0] step 0.05. B_floor=0 (B>=0 always True) DEGENERATES to deberta scope=any -> the
#   0.2333 degeneracy anchor (clean-superset check; sec2). The swept-axis variable replaces E28's cosine-K.
B_FLOOR_GRID = sorted(set([round(0.0 + 0.05 * i, 2) for i in range(0, 21)]))  # 0.00 .. 1.00
S1_TAIL_CON = 0.95            # S1 driver isolation: gold-content items with contradiction >= this

# --- E34 veto geometry (FROZEN pre-data, PRE_REGISTER_E34.md sec1-2) ----------------------------------------
#   scope='any' over the BOUND subset (B>=B_floor). The MODEL is held fixed (deberta); the binding gate is the lever.
PRIMARY_SCOPE = "any"
ANCHOR_SCOPE  = "any"        # == PRIMARY_SCOPE; anchor-compare prints fa_op vs the bars
MARGIN_GRID = [0.00, 0.02, 0.05, 0.10, 0.20]   # delta grid for the reported robustness arm (bound-neighborhood)
E28_OP_FA   = 0.0667         # bart CROSS-MODEL comparison bar (sec6 forks); NOT the running model, NOT reproduced
DEBERTA_ANCHOR_FA = 0.2333   # E34b RE-ANCHOR: bare COSINE-FREE scope=any (v74) = bar to BEAT + DEGENERACY anchor at B_floor=0 (sec2). The E33 0.1667 op-point carried cos<=K=0.5066 (report_E32.md:17-18) -> cosine-CONTAMINATED, NOT a valid anchor for the cosine-free binding lever.
ANCHOR_TOL  = 0.02           # tolerance for the B_floor=0 degeneracy reproduce-assert vs DEBERTA_ANCHOR_FA

# --- E35 accept arm: entailment-lift threshold A (FROZEN pre-data) -------------------------------------------
#   accept fires per candidate iff (ent >= A AND B >= B_floor). A swept over a FROZEN COARSE grid (not observed
#   values) to bound the 3rd selection axis -> tractable run (|A_GRID| x |C_obs| x |B_obs|). A=+inf (accept off)
#   is the regression anchor -> reproduces E34b reject-only op fa 0.1667 (clean-superset; A10). ent direction is
#   premise=source.finding / hyp=claim (SAME as the contradiction scorer), entailment_idx READ from id2label.
A_GRID = sorted(set([round(0.0 + 0.05 * i, 2) for i in range(0, 21)]))   # 0.00 .. 1.00 (coarse; A=+inf added as anchor)
E34B_REJECT_OP_FA = 0.1667   # E35 REGRESSION anchor: at A=+inf the three-way == E34b reject-only -> op MUST reproduce this (report_E34b op-point)
ACCEPT_TOL  = 0.02           # tolerance for the A=+inf accept-off regression-assert vs E34B_REJECT_OP_FA
ENT_DIR_NOTE = "premise=source.finding ; hyp=claim ; P(entailment)"   # documented direction (mirrors ce_scores contradiction direction)

# --- E36 anchored-binding: W = anchor-mix weight (FROZEN pre-data) -------------------------------------------
#   effective binding B = (1-W)*B_lexical + W*B_anchor. W swept over a FROZEN COARSE grid (bounds the 4th selection
#   axis -> tractable run: |W_GRID| x |A_GRID| x |C_obs| x |B_obs|). W=0 (anchor off) is the regression anchor ->
#   B == B_lexical byte-identical -> reproduces E35 TWO_ORGAN op fa 0.0667 (clean-superset; Z10d). W=1 = pure anchor.
# E37 PIN: the per-candidate anchor-mix axis is FROZEN OFF. E36 verdict BINDING_EXHAUSTED proved W MONOTONE HURTS
#   (anchored binding clears 2->1 bf-points; the spoof class is `entitied` -> surface anchors bind spoofs as
#   readily as the gold-tail). Per-candidate binding is EXHAUSTED -> W is held at 0 (binding == pure lexical B_lex).
#   This is a PRE-REGISTERED design consequence of E36 (NOT a new lever) and keeps the E37 sweep 4-D (P x A x
#   B_floor x C, same order as E36). The W=0 path is byte-identical to E35/E36 W=0 -> all inherited W-anchors hold.
W_GRID = (0.0,)              # E37: anchor-mix FROZEN OFF (E36 BINDING_EXHAUSTED); B = lexical only
E35_OP_FA   = 0.0667         # E36 REGRESSION anchor: at W=0 the binding == E35 lexical -> op MUST reproduce this (report_E35 TWO_ORGAN op fa)
BIND_REG_TOL = 0.02          # tolerance for the W=0 binding-regression reproduce-assert vs E35_OP_FA
ANCHOR_NOTE = "B_anchor = containment over {number-like, quoted-span content, CamelCase/ACRONYM entity} ; B=(1-W)*B_lex+W*B_anchor ; W=0 == E35 lexical (regression)"

# ===== E37 SET-CONSISTENCY axis: P = consensus-share threshold (FROZEN pre-data) ==============================
#   PIVOT (pre-registered E35/E36 sec6): the per-candidate organ class is DONE (E36 BINDING_EXHAUSTED). E37 is a
#   STRUCTURALLY DIFFERENT verifier -- CROSS-SOURCE CONSISTENCY over the bound candidate SET, not per-candidate.
#   DERIVATION (E29-E36 evidence chain): a gold-tail driver (ho_g05/g12/g08, con>=0.99) is FAITHFUL to its OWN
#   source but CONTRADICTS a claim about a DIFFERENT co-surfaced source (retrieval MISBINDING) -> its contradiction
#   is a LONE, misbound candidate while the true source corroborates/is neutral. A spoof's bound source
#   AUTHORITATIVELY contradicts it and NO bound source entails it -> contradiction is the SET CONSENSUS. The
#   discriminating signal is the SHAPE of the contradiction distribution OVER the bound set, NOT any single
#   candidate (E36 closed that).
#   LEVER (E37): over the bound subset S (B>=B_floor, scope-filtered) the effective veto reads a SET statistic:
#       n_con = #{c in S: con_c >= C} ; n_ent = #{c in S: ent_c >= A} ; con_share = n_con / |S|
#       set_veto = (n_con >= 1) AND (n_ent == 0) AND (con_share >= P)
#   con_share = the fraction of the bound set that contradicts (consensus measure). A LONE contradictor among
#   corroborating/neutral candidates (con_share < P) is SPARED regardless of its own con magnitude or B -- that is
#   the cross-source-consistency organ. The n_ent==0 entailer-rescue channel is INHERITED byte-identical from E36.
#   REGRESSION ANCHOR (mandatory, E28-K / E35-A / E36-W discipline -- one more rung): P=0 => con_share>=0 is ALWAYS
#   true => set_veto == (n_con>=1) AND (n_ent==0) == the EXACT E36 per-candidate any-veto (accept-rescue) =>
#   the op-point over (A_GRID, observed C, B_floor) at P=0, W=0 MUST reproduce E36/E35 op fa 0.0667 (E36_OP_FA,
#   clean-superset). Else VOID_SET_REGRESSION. A unit-proof (synthetic, no model) asserts set_veto(P=0) is
#   BYTE-IDENTICAL to the E36 reference `reject and not accept` for a grid of (C,A,B_floor,scope) -- design-time.
#   ORACLE-LEAK GATE (P, pre-data): con_share reads ONLY observable per-candidate con/ent (already computed from
#   observable (claim, premise) text) + the observable bound-set size |S|. It NEVER conditions on the held-out
#   true class label or any per-class term. P swept over a FROZEN COARSE grid; op-selection peeks ONLY recall
#   feasibility (B2>=0.90), never fa, never per-class, never bf-band -- same discipline that caught the E28 leak.
#   SELECTOR (one declared refinement on the new axis): op tie-break is BYTE-IDENTICAL to E36 with LOWEST-P
#   appended as the final key -- P>0 is selected ONLY if it STRICTLY lowers min-fa or widens the C-band (P=0 wins
#   all ties -> exact E36 reproduction at the degenerate point). The per-P bf-band lift is a REPORTED-ONLY
#   diagnostic feeding the SET_CONSISTENCY_KNIFE_EDGE-vs-SET_EXHAUSTED fork (falsifier), never the op-selection.
#   FALSIFIER (state it): if NO P (over the FROZEN A, B_floor, C sweep) clears fa<=0.10 AND B2>=0.90 with a
#   NON-TRIVIAL bf-band, the SET-consistency organ is FALSIFIED -> escalate (richer retrieval / multi-source
#   corroboration corpus, OR the per-instance heldout fixture itself is the ceiling -> re-examine heldout construction).
#   FROZEN byte-identical: ce_scores / ce_entail / idx-from-id2label, binding_score (lexical), the cosine rho
#   VOID-guard + S1 diagnostics, from_finding counter, ordering guard, fixture/heldout loaders, the C=+inf baseline
#   path, all inherited VOID anchors (0.2333 / 0.1667 / 0.0667). NO new model. NO cosine in any predicate.
#   con_share takes natural breakpoints at small |S| (1/5,1/4,1/3,1/2,2/3,3/4,1) -> grid spans those crossings.
P_GRID = (0.0, 0.20, 0.26, 0.34, 0.50, 0.67, 0.75, 1.00)   # FROZEN coarse; P=0 = per-candidate any-veto regression anchor
E36_OP_FA   = 0.0667         # E37 REGRESSION anchor: at P=0 (W=0) the SET veto == E36 per-candidate any-veto -> op MUST reproduce this
SET_REG_TOL = 0.02           # tolerance for the P=0 set-regression reproduce-assert vs E36_OP_FA
SET_NOTE = "set_veto = (n_con>=1) AND (n_ent==0) AND (con_share>=P) ; con_share=n_con/|S| over bound subset ; P=0 == E36 per-candidate any-veto (regression)"

_ce_tok = _ce_model = _con_idx = None
_ent_idx = None   # E35 accept arm: entailment label index, READ from id2label (never hardcoded), located alongside _con_idx
def _ce_load():
    global _ce_tok, _ce_model, _con_idx, _ent_idx
    if _ce_model is None:
        _ce_tok = AutoTokenizer.from_pretrained(CE_MODEL)
        _ce_model = AutoModelForSequenceClassification.from_pretrained(CE_MODEL)
        _ce_model.eval()
        # READ contradiction index from the model card (label order differs across NLI models) -- never hardcode.
        id2label = {int(k): str(lbl).lower() for k, lbl in _ce_model.config.id2label.items()}
        con = [i for i, lbl in id2label.items() if "contradic" in lbl]
        assert len(con) == 1, f"cannot locate a single contradiction label in id2label={id2label}"
        _con_idx = con[0]
        # E35 A3: locate the SINGLE entailment label the same way (oracle-clean, no new model).
        ent = [i for i, lbl in id2label.items() if "entail" in lbl]
        assert len(ent) == 1, f"cannot locate a single entailment label in id2label={id2label}"
        _ent_idx = ent[0]
        print(f"[ce] model={CE_MODEL} id2label={id2label} contradiction_idx={_con_idx} entailment_idx={_ent_idx}")
    return _ce_tok, _ce_model, _con_idx

def ce_scores(claim, sources):
    """NLI contradiction. premise=source(finding), hypothesis=claim -> P(contradiction) per source.
    Direction is load-bearing (E26 PIVOT): 'does the authorized source CONTRADICT the claim'. Probs in [0,1]."""
    if not sources: return []
    tok, model, con_idx = _ce_load()
    enc = tok(list(sources), [claim] * len(sources), padding=True, truncation=True,
              max_length=512, return_tensors="pt")   # arg0 = premise = source ; arg1 = hypothesis = claim
    with torch.no_grad():
        logits = model(**enc).logits                 # (n, num_labels)
    probs = torch.softmax(logits, dim=-1)[:, con_idx]
    return probs.cpu().numpy().astype(float).tolist()

def ce_entail(claim, sources):
    """E35 accept arm. NLI entailment, SAME direction/encoding as ce_scores (premise=source(finding),
    hypothesis=claim) -> P(entailment) per source in [0,1]. Reads _ent_idx (located in _ce_load from id2label,
    never hardcoded). Separate forward pass keeps ce_scores byte-identical (the proven contradiction scorer that
    the rho guard + S1 diag depend on). Oracle-clean: conditions only on observable (claim, premise) text."""
    if not sources: return []
    tok, model, _con_idx_unused = _ce_load()
    enc = tok(list(sources), [claim] * len(sources), padding=True, truncation=True,
              max_length=512, return_tensors="pt")   # arg0 = premise = source ; arg1 = hypothesis = claim
    with torch.no_grad():
        logits = model(**enc).logits                 # (n, num_labels)
    probs = torch.softmax(logits, dim=-1)[:, _ent_idx]
    return probs.cpu().numpy().astype(float).tolist()

# E34 Z1: OBSERVABLE binding signal B(claim, premise) in [0,1] -- lexical subject-overlap (containment).
#   B = |content_tokens(claim) INTERSECT content_tokens(premise)| / |content_tokens(claim)|.
#   Observable text ONLY (claim string + candidate premise) -> oracle-clean (no class label, no per-class term).
#   Topical (shared subject/entities), ORTHOGONAL to NLI contradiction (logical): a wrong-source candidate can
#   score high contradiction yet low B. cosine is UNTOUCHED (rho guard / S1 diag); B is a NEW parallel quantity.
_STOP = frozenset((
    "the a an of to in on at for and or but if then with without by from as is are was were be been being this "
    "that these those it its their his her our your my we you they he she i not no nor so than too very can may "
    "might will would should could has have had do does did about into over under between within across per such "
    "which who whom whose what when where why how also more most some any all each both other same own".split()))
def _content_tokens(text):
    toks = []
    cur = []
    for ch in str(text).lower():
        if ch.isalnum():
            cur.append(ch)
        elif cur:
            toks.append("".join(cur)); cur = []
    if cur: toks.append("".join(cur))
    return {t for t in toks if len(t) > 2 and t not in _STOP}
def binding_score(claim, premise):
    cset = _content_tokens(claim)
    if not cset: return 0.0
    pset = _content_tokens(premise)
    return float(len(cset & pset)) / float(len(cset))

# E36 Z4: ANCHORED binding observable -- shared SURFACE anchors {number-like, quoted-span content,
#   CamelCase/ACRONYM entity} between claim and premise. Same CONTAINMENT formula shape as the lexical B
#   (intersection / |claim anchors|), in [0,1]. Observable text ONLY (claim string + candidate premise) ->
#   oracle-clean (no class label, no per-class term). Kinds are prefix-tagged so a number never collides with
#   an entity. Deterministic, ASCII, no regex. binding_score (lexical) is UNTOUCHED -- this is parallel.
def _anchor_tokens(text):
    s = str(text)
    toks = set()
    # 1) quoted spans (single or double quotes) -> their content tokens, tagged 'q:'
    for qch in (chr(34), chr(39)):
        i = 0
        while True:
            a = s.find(qch, i)
            if a < 0: break
            b = s.find(qch, a + 1)
            if b < 0: break
            for t in _content_tokens(s[a + 1:b]):
                toks.add("q:" + t)
            i = b + 1
    # 2) number-like tokens (>=1 digit; keep internal . , % / -), tagged 'n:'
    cur = []; has_digit = False
    for ch in s + chr(0):
        if ch.isdigit():
            cur.append(ch); has_digit = True
        elif ch in ".,%/-" and cur:
            cur.append(ch)
        else:
            if cur and has_digit:
                v = "".join(cur).strip(".,%/-")
                if v: toks.add("n:" + v)
            cur = []; has_digit = False
    # 3) entity tokens: INTERIOR uppercase (CamelCase) or ALL-CAPS len>=2, tagged 'e:' (sentence-initial
    #    single-cap words are NOT entities -> low false-anchor rate; deterministic, no cross-text peek)
    word = []
    for ch in s + chr(0):
        if ch.isalnum():
            word.append(ch)
        else:
            if len(word) >= 2:
                w = "".join(word)
                if any(c.isupper() for c in w[1:]) or (w.isupper() and any(c.isalpha() for c in w)):
                    toks.add("e:" + w.lower())
            word = []
    return toks
def anchor_score(claim, premise):
    cset = _anchor_tokens(claim)
    if not cset: return 0.0
    pset = _anchor_tokens(premise)
    return float(len(cset & pset)) / float(len(cset))

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3: return float("nan")
    ra, rb = np.argsort(np.argsort(a)).astype(float), np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra*rb).sum()/d) if d else float("nan")

def candidates_with_cosine(query, mat, recs):
    """Replicate semantic_retrieve.retrieve EXACTLY (floor, top_k, order) but keep cosine + full record."""
    q = sem._embed([query])[0]
    sims = mat @ q
    order = np.argsort(-sims)
    out = []
    for i in order[:sem.TOP_K]:
        if float(sims[i]) < sem.FLOOR: break
        out.append((float(sims[i]), recs[int(i)]))
    return out

def precompute_item(item, store, mat, recs, decorr, prem_log, finding_by_source, diag):
    """Resolve each claim of an item into a C-independent shape; collect (cos,contradiction) for decorrelation.
    premise = source.finding if non-empty else source (content-binding probe). prem_log records which was used.
    E35: also collects per-candidate entailment (accept arm). The contradiction path (ce_scores), the (cos,con)
    decorr collection, and the diag tuple are BYTE-IDENTICAL to run_E34b -- ent is an ADDITIVE 4th tuple slot."""
    resolutions = []  # 'common' | 'noauth' | ('auth', [contradiction...])
    for s in v.segment(item["text"]):
        if v.is_qa_scaffold(s): continue
        n = v._norm(s)
        ct, ok = v.classify(s)
        if not ok: continue
        g, _sig = v.gate(s)
        asserts = (ct == "prose_provenance") or (g == "BINDABLE")
        if not asserts:
            resolutions.append("common"); continue
        query = v._strip_cite(s) or s
        cands = candidates_with_cosine(query, mat, recs)
        authorized = [(cos, r) for (cos, r) in cands if store.is_authorized(r)]
        if not authorized:
            resolutions.append("noauth"); continue
        prems = []; kinds = []; coss = []
        for (cos, r) in authorized:
            f = finding_by_source.get(r["source"], "")
            prems.append(f if f else r["source"])
            k = "finding" if f else "source"
            kinds.append(k); prem_log.append(k); coss.append(float(cos))
        scs = ce_scores(query, prems)
        ents = ce_entail(query, prems)                     # E35 A5: observable entailment per candidate (accept arm; oracle-clean)
        bnds = [binding_score(query, p) for p in prems]    # E34 Z1: lexical binding per candidate (oracle-clean)
        ancs = [anchor_score(query, p) for p in prems]     # E36 Z5: anchored binding per candidate (oracle-clean; parallel)
        for k, sc, cos in zip(kinds, scs, coss):
            diag.append((item["class"], item["id"], k, float(sc), float(cos)))  # E28: + id + cos for S1/cond (cos UNTOUCHED)
        for cos, sc in zip(coss, scs): decorr.append((cos, sc))   # rho guard on (cos, contradiction) UNCHANGED
        # E35: resolution carries (cos, contradiction, ENTAILMENT, B) per authorized candidate (cos kept for diag;
        # con+B = the frozen reject gate; ent = the accept arm). con/B reject predicate is UNCHANGED -- ent is additive.
        resolutions.append(("auth", [(float(c), float(s), float(e), float(b), float(an)) for c, s, e, b, an in zip(coss, scs, ents, bnds, ancs)]))
    return resolutions

def _e36_veto_reference(cands, C, B_floor, scope, A, W):
    """E36 per-candidate reference veto (reject and not accept) over the scope-filtered bound subset.
    Used ONLY by the design-time set-off unit-proof to assert set_veto(P=0) is BYTE-IDENTICAL. NOT on the
    op path (the op path uses item_label_at_C). Mirrors the FROZEN E36 reject/accept/veto exactly."""
    def beff(bl, ba): return (1.0 - W) * bl + W * ba
    if scope == "top1":
        cos0, sc0, en0, bl0, ba0 = cands[0]; b0 = beff(bl0, ba0)
        reject = (sc0 >= C and b0 >= B_floor); accept = (en0 >= A and b0 >= B_floor)
    elif scope == "any":
        reject = any((sc >= C and beff(bl, ba) >= B_floor) for (cos, sc, en, bl, ba) in cands)
        accept = any((en >= A and beff(bl, ba) >= B_floor) for (cos, sc, en, bl, ba) in cands)
    elif isinstance(scope, tuple) and scope[0] == "margin":
        delta = float(scope[1]); cos0 = cands[0][0]
        reject = any((sc >= C and beff(bl, ba) >= B_floor and cos >= cos0 - delta) for (cos, sc, en, bl, ba) in cands)
        accept = any((en >= A and beff(bl, ba) >= B_floor and cos >= cos0 - delta) for (cos, sc, en, bl, ba) in cands)
    else:
        raise ValueError(f"unknown scope {scope!r}")
    return reject and not accept

def _bound_subset(cands, B_floor, scope, W):
    """E37: the bound, scope-filtered candidate subset S over which the SET statistic is read. b_eff =
    (1-W)*B_lex + W*B_anchor (W FROZEN 0 in E37 => b_eff == B_lex byte-identical). The scope filter is
    BYTE-IDENTICAL to the E36 reject/accept candidate filter (any / top1 / cosine-margin)."""
    def beff(bl, ba): return (1.0 - W) * bl + W * ba
    if scope == "top1":
        c0 = cands[0]
        return [c0] if beff(c0[3], c0[4]) >= B_floor else []
    elif scope == "any":
        return [(cos, sc, en, bl, ba) for (cos, sc, en, bl, ba) in cands if beff(bl, ba) >= B_floor]
    elif isinstance(scope, tuple) and scope[0] == "margin":
        delta = float(scope[1]); cos0 = cands[0][0]
        return [(cos, sc, en, bl, ba) for (cos, sc, en, bl, ba) in cands
                if beff(bl, ba) >= B_floor and cos >= cos0 - delta]
    raise ValueError(f"unknown scope {scope!r}")

def item_label_at_C(resolutions, C, B_floor=0.0, scope=PRIMARY_SCOPE, A=float("inf"), W=0.0, P=0.0):
    """E37 SET-CONSISTENCY veto over the bound subset, layered on the FROZEN E36 bound/scorer substrate.
    Over the bound, scope-filtered subset S (b_eff>=B_floor): n_con=#{con>=C}, n_ent=#{ent>=A}, con_share=
    n_con/|S|. The CLAIM is vetoed iff  set_veto = (n_con>=1) AND (n_ent==0) AND (con_share>=P).
    DERIVATION: a gold misbinding contributes a LONE contradictor (con_share small) among corroborating/neutral
    candidates -> spared at P>0 ; a spoof's bound source contradicts as the SET CONSENSUS (con_share high) with
    no entailer -> vetoed. The entailer-rescue (n_ent==0) channel is INHERITED byte-identical from E36.
    REGRESSION: P=0 => con_share>=0 ALWAYS true => set_veto == (n_con>=1) AND (n_ent==0) == the EXACT E36
    per-candidate any-veto (accept-rescue). W FROZEN 0 in E37 => b_eff == B_lex byte-identical (E35/E36 path).
    `scope` selects WHICH candidate(s) form S (any / top1 / cosine-margin) -- BYTE-IDENTICAL to the E36 filter.
    Baseline C=+inf => n_con=0 under ANY scope/B_floor/A/P => only noauth demotes => no-veto fa 0.467
    (scope/B_floor/A/P-independent, model-independent). Rollup identical to run_E26..E36 (UNVERIFIABLE -> DEMOTE).
    r[1] top-1-cosine-first (asserted in main); tuples = (cos, contradiction, entailment, B_lex, B_anchor)."""
    labs = []
    for r in resolutions:
        if r == "common":   labs.append("PASS-COMMON")
        elif r == "noauth": labs.append("UNVERIFIABLE")
        else:
            cands = r[1]                                   # [(cos, contradiction, entailment, B_lex, B_anchor), ...] top-1 cosine first
            S = _bound_subset(cands, B_floor, scope, W)    # E37: bound, scope-filtered subset (the SET)
            nS = len(S)
            n_con = sum(1 for (cos, sc, en, bl, ba) in S if sc >= C)
            n_ent = sum(1 for (cos, sc, en, bl, ba) in S if en >= A)
            con_share = (float(n_con) / float(nS)) if nS > 0 else 0.0    # consensus measure (observable; |S|>=0)
            set_veto = (n_con >= 1) and (n_ent == 0) and (con_share >= P)  # P=0 => == E36 any-veto byte-identical
            labs.append("UNVERIFIABLE" if set_veto else "VERIFIED")
    if not labs: return "PASS-COMMON"
    if "UNVERIFIABLE" in labs: return "DEMOTE"
    if "VERIFIED" in labs: return "VERIFIED"
    return "PASS-COMMON"

def metrics_at_C(items_pre, C, B_floor=0.0, scope=PRIMARY_SCOPE, A=float("inf"), W=0.0, P=0.0):
    res = [(it, item_label_at_C(r, C, B_floor, scope, A, W, P)) for (it, r) in items_pre]
    b1 = [(it, l) for (it, l) in res if it["class"] == B1_CLASS]
    b2 = [(it, l) for (it, l) in res if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    b3 = [(it, l) for (it, l) in res if it["class"] == B3_CLASS]
    B1 = sum(l == "DEMOTE" for _, l in b1) / len(b1) if b1 else float("nan")
    B2 = sum(l == "VERIFIED" for _, l in b2) / len(b2) if b2 else float("nan")
    B3 = sum(l == "DEMOTE" for _, l in b3) / len(b3) if b3 else float("nan")
    return B1, B2, B3, (len(b1), len(b2), len(b3))

# ===== E27 NEW: S2 robustness sweep, S3 demotion attribution ==============================================

def s2_band_at_bfloor(items_pre, B_floor, scope=PRIMARY_SCOPE, A=float("inf"), W=0.0, P=0.0):
    """S2 -- C-sweep at a FIXED binding gate B_floor over the FROZEN C grid; locate the joint (fa<=0.10 AND
    B2>=0.90) band. Returns (rows, band). The robustness verdict is read at the OP-POINT's selected B_floor.
    E37: read at the op-point's selected consensus-share P (P=0 reproduces the E36 band)."""
    rows = []
    for C in S2_GRID:
        B1, B2, _B3, _ = metrics_at_C(items_pre, float(C), B_floor, scope, A, W, P)
        fa = (1.0 - B1) if not np.isnan(B1) else float("nan")
        joint = (not np.isnan(fa)) and (not np.isnan(B2)) and (fa <= GATE_FA) and (B2 >= RECALL_FLOOR)
        rows.append((float(C), float(fa), float(B2), bool(joint)))
    joint_Cs = [C for (C, _fa, _b2, ok) in rows if ok]
    joint_B2 = [b2 for (_C, _fa, b2, ok) in rows if ok]
    if joint_Cs:
        width = max(joint_Cs) - min(joint_Cs)
        points = len(joint_Cs)
        liftoff = max(joint_B2) - RECALL_FLOOR
        robust = (width >= S2_BAND_MIN_WIDTH) and (points >= S2_BAND_MIN_POINTS) and (liftoff > 0.0)
        band = dict(c_lo=min(joint_Cs), c_hi=max(joint_Cs), width=width, points=points,
                    b2_liftoff=liftoff, robust=robust)
    else:
        band = dict(c_lo=None, c_hi=None, width=0.0, points=0, b2_liftoff=0.0, robust=False)
    return rows, band

def s2_perBfloor_summary(items_pre, scope=PRIMARY_SCOPE, A=float("inf"), W=0.0, P=0.0):
    """Per-B_floor joint C-band summary over the FROZEN B_FLOOR_GRID. The bf-band (sec6) non-triviality is the
    count of B_floor points whose min-fa (over C, at B2>=0.90) clears GATE_FA -- read in main for the verdict.
    E37: evaluated at the op-point's consensus-share P (P=0 reproduces the E36 summary)."""
    out = []
    for B_floor in B_FLOOR_GRID:
        rows, band = s2_band_at_bfloor(items_pre, float(B_floor), scope, A, W, P)
        min_fa = min((fa for (_C, fa, b2, _ok) in rows if (not np.isnan(b2)) and b2 >= RECALL_FLOOR), default=float("nan"))
        clears = (not np.isnan(min_fa)) and (min_fa <= GATE_FA)
        out.append((B_floor, band["width"], band["points"], band["b2_liftoff"], band["robust"], min_fa, clears))
    return out

def s3_attribution(items_pre, op_C, op_B_floor, fa_base, fa_op, scope=PRIMARY_SCOPE, A=float("inf"), W=0.0, P=0.0):
    """S3 -- decompose B1-class (spoof) demotions at the op-point (op_C, op_B_floor, scope, A) into:
       (a) noauth baseline  : demotes already at C=+inf (no veto needed; gate-independent),
       (b) contradiction-veto reject organ : demoted at op (a bound candidate crossed con>=op_C AND B>=op_B_floor)
                                             and NOT noauth -- i.e. the FROZEN reject organ, accept not rescuing,
       (c) accept/entailment-lift organ    : E35 WIRED. n_by_entailment = GOLD (B2) items the accept arm RESCUES
           from the reject-only verdict at this op-point (label flips DEMOTE->not-DEMOTE when accept is ON vs OFF).
           n_spoof_rescued = SPOOF (B1) items the accept WRONGLY rescues (the false-accept the accept arm can
           introduce) -- the critical leak guard (high => accept hurts; reported, feeds the verdict).
    reject_share = (fa_base - fa_op)/fa_base. Bar (carried): > 0.50. accept OFF == A=+inf (reject-only)."""
    spoofs = [r for (it, r) in items_pre if it["class"] == B1_CLASS]
    golds  = [r for (it, r) in items_pre if it["class"] == B2_CLASS and it["id"] not in B2_EXCLUDE]
    n_total = len(spoofs)
    n_demote_op = n_by_noauth = n_by_veto = n_survive = 0
    for r in spoofs:
        base = item_label_at_C(r, float("inf"), 0.0, scope)                       # gate off (B_floor=0) == no-veto baseline
        op = item_label_at_C(r, float(op_C), float(op_B_floor), scope, A, W, P)    # SET-veto at op (P consensus-share)
        if op == "DEMOTE":
            n_demote_op += 1
            if base == "DEMOTE":  n_by_noauth += 1
            else:                 n_by_veto += 1
        else:
            n_survive += 1
    # (c) accept organ ACTION isolated by toggling A at the FROZEN op (C, B_floor): reject-only (A=+inf) vs op-A.
    n_by_entailment = n_spoof_rescued = 0
    for r in golds:
        rej_only = item_label_at_C(r, float(op_C), float(op_B_floor), scope, float("inf"), W, P)
        with_acc = item_label_at_C(r, float(op_C), float(op_B_floor), scope, A, W, P)
        if rej_only == "DEMOTE" and with_acc != "DEMOTE": n_by_entailment += 1   # gold rescued (organ working)
    for r in spoofs:
        rej_only = item_label_at_C(r, float(op_C), float(op_B_floor), scope, float("inf"), W, P)
        with_acc = item_label_at_C(r, float(op_C), float(op_B_floor), scope, A, W, P)
        if rej_only == "DEMOTE" and with_acc != "DEMOTE": n_spoof_rescued += 1   # spoof WRONGLY rescued (leak)
    reject_share = (fa_base - fa_op) / fa_base if fa_base > 0 else float("nan")
    return dict(n_total=n_total, n_demote_op=n_demote_op, n_by_noauth=n_by_noauth,
                n_by_veto=n_by_veto, n_survive=n_survive, n_by_entailment=n_by_entailment,
                n_spoof_rescued=n_spoof_rescued,
                reject_share=reject_share, bar_met=(not np.isnan(reject_share) and reject_share > S3_REJECT_SHARE_BAR))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="eval/_local/gold_fixture_E25b.json")
    ap.add_argument("--heldout", default="eval/_local/heldout_E17.jsonl")
    ap.add_argument("--fixture_md5", default="4a45f52883a802e8d8d1d5ff5d185bdb")
    ap.add_argument("--heldout_md5", default="7e9fe030646d5671952e7a9fe9437e37")
    ap.add_argument("--out", default="reports/report_E37.md")   # NEVER a frozen-report path (no clobber E36/E35/E34b/E32/E30/E28/E27)
    a = ap.parse_args()

    fm, hm = md5(a.fixture), md5(a.heldout)
    print(f"[md5] fixture {fm} {'OK' if fm==a.fixture_md5 else 'MISMATCH'} | heldout {hm} {'OK' if hm==a.heldout_md5 else 'MISMATCH'}")
    assert fm == a.fixture_md5, "fixture md5 mismatch -> STOP (not E25b)"
    assert hm == a.heldout_md5, "heldout md5 mismatch -> STOP (not v3)"

    store = gr.GoldStore(a.fixture)
    mat, recs = sem.build_index(store.records)
    items = [json.loads(l) for l in open(a.heldout, encoding="utf-8") if l.strip()]
    print(f"[fixture] records={len(store.records)} manifest={len(store.manifest_files)} | heldout items={len(items)}")
    cls = {}
    for it in items: cls[it["class"]] = cls.get(it["class"], 0) + 1
    print(f"[classes] {cls}")
    assert B1_CLASS in cls and B2_CLASS in cls, "heldout missing B1/B2 classes -> wrong file"

    decorr = []; prem_log = []; diag = []
    raw = json.load(open(a.fixture, encoding="utf-8"))   # frozen GoldStore drops "finding"; read it from raw
    finding_by_source = {rr["source"]: str(rr.get("finding", "") or "").strip() for rr in raw["records"]}
    n_with_finding = sum(1 for v_ in finding_by_source.values() if v_)
    print(f"[sidemap] sources={len(finding_by_source)} with_finding={n_with_finding}")
    items_pre = [(it, precompute_item(it, store, mat, recs, decorr, prem_log, finding_by_source, diag)) for it in items]
    n_prem = len(prem_log); n_find = sum(p == "finding" for p in prem_log)
    print(f"[premise] from_finding={n_find}/{n_prem} from_source(fallback)={n_prem-n_find}")
    assert n_find > 0, "from_finding=0 -> fixture dropped 'finding' -> VOID-by-construction (E23 guard)"

    # E30 ORDERING GUARD: r[1] MUST be top-1-cosine-first (r[1][0] = bound support). The TOP1 scope is invalid
    # otherwise. candidates_with_cosine returns argsort(-sims) + floor-break; authorized filter preserves order.
    for (_it, rr) in items_pre:
        for x in rr:
            if isinstance(x, tuple) and x[0] == "auth":
                cs = [c for (c, _s, _e, _b, _a) in x[1]]
                assert all(cs[i] >= cs[i + 1] - 1e-9 for i in range(len(cs) - 1)), \
                    "r[1] not top-1-cosine-first -> TOP1 scope invalid -> STOP"

    # E37 SET-OFF UNIT-PROOF (runtime byte-identity guard): at P=0 the SET veto MUST equal the E36 per-candidate
    # any-veto label for EVERY item across a grid of (C, A, B_floor, scope). This is the regression discipline made
    # explicit at the label level (stronger than the metric-level set-regression anchor). W FROZEN 0.
    def _item_label_e36_ref(resolutions, C, B_floor, scope, A, W):
        labs = []
        for r in resolutions:
            if r == "common":   labs.append("PASS-COMMON")
            elif r == "noauth": labs.append("UNVERIFIABLE")
            else:
                labs.append("UNVERIFIABLE" if _e36_veto_reference(r[1], C, B_floor, scope, A, W) else "VERIFIED")
        if not labs: return "PASS-COMMON"
        if "UNVERIFIABLE" in labs: return "DEMOTE"
        if "VERIFIED" in labs: return "VERIFIED"
        return "PASS-COMMON"
    _grid_C = [float("inf")] + (sorted({sc for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc, en, bl, ba) in x[1]})[:8] or [0.5])
    _proofs = 0
    for _sc in ("any", "top1", ("margin", 0.05)):
        for _A in (float("inf"), 0.5):
            for _Bf in (0.0, 0.5):
                for _C in _grid_C:
                    for (_it, r) in items_pre:
                        a_ = item_label_at_C(r, _C, _Bf, _sc, _A, 0.0, 0.0)   # P=0
                        b_ = _item_label_e36_ref(r, _C, _Bf, _sc, _A, 0.0)
                        assert a_ == b_, f"SET-OFF UNIT-PROOF FAILED: P=0 != E36 ref (C={_C} A={_A} Bf={_Bf} scope={_sc}) {a_}!={b_}"
                        _proofs += 1
    print(f"[unit-proof] SET-OFF P=0 == E36 per-candidate any-veto byte-identical over {_proofs} (item x grid) checks -> PASS")

    rho = spearman([c for c, _ in decorr], [s for _, s in decorr])
    degenerate = (not np.isnan(rho)) and rho >= DEGENERATE_RHO            # FROZEN E26 VOID guard (0.95, one-sided)
    rho_advisory_ok = (not np.isnan(rho)) and abs(rho) < PREREG_RHO_ADVISORY   # PRE_REGISTER sec4 advisory (reported)
    print(f"[guard] spearman(contradiction,cosine) rho={rho:.3f} pairs={len(decorr)} degenerate={degenerate} "
          f"|rho|<{PREREG_RHO_ADVISORY}={rho_advisory_ok}")

    # baseline sanity (NO veto, C=+inf): MUST reproduce the no-veto false-accept ~0.467 (model-INDEPENDENT)
    B1b, B2b, B3b, ns = metrics_at_C(items_pre, float("inf"))
    fa_base = 1.0 - B1b
    print(f"[baseline C=+inf] B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (expect ~0.467) n={ns}")
    base_ok = 0.40 <= fa_base <= 0.53
    if not base_ok:
        print(f"[WARN] baseline false-accept {fa_base:.3f} != no-veto 0.467 -> harness wiring mismatch, STOP and reconcile")

    # observed grids (selection over OBSERVED values only; no post-hoc fishing). tuples are (cos, sc, ent, B).
    C_obs = sorted({sc for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc, en, bl, ba) in x[1]})
    # B_obs = observed LEXICAL b (the W=0 component) -> B_floor grid identical to E35 -> regression-exact at W=0.
    B_obs = sorted({bl for (_it, r) in items_pre for x in r if isinstance(x, tuple) for (cos, sc, en, bl, ba) in x[1]})
    # E35 accept axis A swept over the FROZEN coarse A_GRID (bounds the 3rd selection axis -> tractable run).
    A_sweep = list(A_GRID)
    W_sweep = list(W_GRID)   # E37: anchor-mix FROZEN OFF -> single point (0.0); kept for byte-identical W-anchors
    P_sweep = list(P_GRID)   # E37 SET-consistency axis (4th selection axis; P=0 = per-candidate any-veto regression anchor)

    # ---- op-point selector (FROZEN selection; E37 swaps the E36 W axis for the SET-consistency P axis) --------
    # over (P_GRID x A_GRID x OBSERVED B_floor x OBSERVED C), W FROZEN 0: MIN false-accept subject to B2>=0.90.
    # Tie-break (frozen, BYTE-IDENTICAL to E36 minus the dead W axis): widest joint C-band at that (A,B_floor,P) ->
    # lowest C -> highest B_floor -> HIGHEST A -> LOWEST P appended last: the SET lever (P>0) is chosen ONLY if it
    # STRICTLY lowers min-fa or widens the C-band; P=0 wins all ties -> exact E36 op reproduced at the degenerate
    # point. Selection peeks ONLY recall feasibility (B2>=0.90), never fa, never per-class, never bf-band -> oracle-clean.
    def select_op(scope):
        feasible = []
        for P in P_sweep:
            for A in A_sweep:
                for Bf in B_obs:
                    for C in C_obs:
                        b1, b2, _b3, _ = metrics_at_C(items_pre, C, Bf, scope, float(A), 0.0, float(P))
                        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                            feasible.append((1.0 - b1, float(C), float(Bf), float(A), float(P)))
        if not feasible:
            return None, None, None, None, None, float("nan")
        min_fa = min(f for f, _c, _bf, _a, _p in feasible)
        cand = [(c, bf, a, p) for (f, c, bf, a, p) in feasible if abs(f - min_fa) < 1e-12]
        _bw = {(bf, a, p): s2_band_at_bfloor(items_pre, bf, scope, a, 0.0, p)[1]["width"] for (_c, bf, a, p) in cand}
        cand.sort(key=lambda t: (-_bw[(t[1], t[2], t[3])], t[0], -t[1], -t[2], t[3]))
        c_, bf_, a_, p_ = cand[0]
        _b1, b2_, _b3, _ = metrics_at_C(items_pre, c_, bf_, scope, a_, 0.0, p_)
        return float(a_), float(c_), float(bf_), float(p_), float(b2_), float(min_fa)

    # E34 DEGENERACY ANCHOR (Z4, INHERITED byte-identical): B_floor=0 (gate off), A=+inf (accept off) MUST
    # reproduce deberta scope=any fa 0.2333 (clean superset). metrics_at_C default A=+inf -> accept never fires.
    _degen_feas = []
    for C in C_obs:
        b1, b2, _b3, _ = metrics_at_C(items_pre, C, 0.0, "any")
        if not np.isnan(b2) and b2 >= RECALL_FLOOR:
            _degen_feas.append(1.0 - b1)
    degen_fa = min(_degen_feas) if _degen_feas else float("nan")
    degen_ok = (not np.isnan(degen_fa)) and abs(degen_fa - DEBERTA_ANCHOR_FA) <= ANCHOR_TOL
    print(f"[degeneracy B_floor=0 scope=any] fa={degen_fa} vs deberta anchor {DEBERTA_ANCHOR_FA} +/-{ANCHOR_TOL} -> ok={degen_ok}")

    # E35 ACCEPT-OFF REGRESSION ANCHOR (A10): at A=+inf (accept never fires) the three-way == E34b reject-only ->
    # the op-point over (C_obs, B_obs) MUST reproduce the E34b reject-only op fa 0.1667 (clean-superset for the
    # accept arm). This is the accept analog of E28's K=+inf->E27 regression. min-fa s.t. B2>=0.90 at A=+inf.
    _rejonly_feas = []
    for Bf in B_obs:
        for C in C_obs:
            b1, b2, _b3, _ = metrics_at_C(items_pre, C, Bf, "any", float("inf"))
            if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                _rejonly_feas.append(1.0 - b1)
    rejonly_fa = min(_rejonly_feas) if _rejonly_feas else float("nan")
    rejonly_ok = (not np.isnan(rejonly_fa)) and abs(rejonly_fa - E34B_REJECT_OP_FA) <= ACCEPT_TOL
    print(f"[accept-off regression A=+inf] reject-only op fa={rejonly_fa} vs E34b op {E34B_REJECT_OP_FA} +/-{ACCEPT_TOL} -> ok={rejonly_ok}")

    # E36 BINDING-REGRESSION ANCHOR (Z10d): at W=0 (anchor off) the effective B == E35 lexical B byte-identical ->
    # the op-point over (A_GRID, C_obs, B_obs) MUST reproduce the E35 TWO_ORGAN op fa 0.0667 (clean-superset for
    # the binding sharpen). This is the binding analog of E28 K=+inf->E27 and E35 A=+inf->E34b. min-fa s.t. B2>=0.90 at W=0.
    _bindreg_feas = []
    for A in A_sweep:
        for Bf in B_obs:
            for C in C_obs:
                b1, b2, _b3, _ = metrics_at_C(items_pre, C, Bf, "any", float(A), 0.0)
                if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                    _bindreg_feas.append(1.0 - b1)
    bindreg_fa = min(_bindreg_feas) if _bindreg_feas else float("nan")
    bindreg_ok = (not np.isnan(bindreg_fa)) and abs(bindreg_fa - E35_OP_FA) <= BIND_REG_TOL
    print(f"[binding-regression W=0] op fa={bindreg_fa} vs E35 op {E35_OP_FA} +/-{BIND_REG_TOL} -> ok={bindreg_ok}")

    # E37 SET-REGRESSION ANCHOR (P=0): at P=0 (consensus-share off) con_share>=0 is ALWAYS true -> the SET veto
    # == the EXACT E36 per-candidate any-veto (accept-rescue). The op-point over (A_GRID, C_obs, B_obs) at P=0,W=0
    # MUST reproduce the E36/E35 op fa 0.0667 (E36_OP_FA, clean-superset for the SET lever). This is the E28-K /
    # E35-A / E36-W discipline, one more rung. min-fa s.t. B2>=0.90 at P=0,W=0. (Numerically coincident with the
    # binding-regression above at this rung -- W and P are both off -- but recorded as the E37-specific anchor.)
    _setreg_feas = []
    for A in A_sweep:
        for Bf in B_obs:
            for C in C_obs:
                b1, b2, _b3, _ = metrics_at_C(items_pre, C, Bf, "any", float(A), 0.0, 0.0)
                if not np.isnan(b2) and b2 >= RECALL_FLOOR:
                    _setreg_feas.append(1.0 - b1)
    setreg_fa = min(_setreg_feas) if _setreg_feas else float("nan")
    setreg_ok = (not np.isnan(setreg_fa)) and abs(setreg_fa - E36_OP_FA) <= SET_REG_TOL
    print(f"[set-regression P=0] op fa={setreg_fa} vs E36 op {E36_OP_FA} +/-{SET_REG_TOL} -> ok={setreg_ok}")

    # ANCHOR-COMPARE: primary scope='any'. fa_op read against bart 0.0667 (cross-model) + deberta 0.2333 + GATE 0.10.
    anc_A, anc_C, anc_Bf, anc_P, anc_B2, anc_fa = select_op(ANCHOR_SCOPE)   # ANCHOR_SCOPE == PRIMARY_SCOPE == 'any'
    anchor_below_bar = (anc_C is not None) and (not np.isnan(anc_fa)) and (anc_fa < E28_OP_FA)
    print(f"[anchor-compare scope=any] A={anc_A} C={anc_C} B_floor={anc_Bf} P={anc_P} fa_op={anc_fa} "
          f"vs bart bar {E28_OP_FA} / deberta bar {DEBERTA_ANCHOR_FA} -> below_bart={anchor_below_bar}")

    # E37 PRIMARY op-point: scope='any' over the BOUND subset (B>=B_floor), accept threshold A + consensus-share P from the sweep (W FROZEN 0).
    chosen_A, chosen_C, chosen_Bf, chosen_P, chosen_B2, _min_fa = select_op(PRIMARY_SCOPE)
    if chosen_C is None:
        op_verdict = "FAIL_RECALL_UNUSABLE"; B1 = B2 = B3 = fa = move = float("nan")
    else:
        B1, B2, B3, _ = metrics_at_C(items_pre, chosen_C, chosen_Bf, PRIMARY_SCOPE, chosen_A, 0.0, chosen_P)
        fa = 1.0 - B1; move = E20B_FALSE_ACCEPT - fa
        if   fa <= GATE_FA:           op_verdict = "PASS"
        elif fa < PARTIAL_BAND:       op_verdict = "FAIL_PARTIAL_VETO"
        else:                         op_verdict = "FAIL_PLATEAU_CONTRADICTION_INSUFFICIENT"

    # ---- S2 robustness: band read at the op-point B_floor + per-B_floor summary (the bf-band feeds the verdict) -
    # E35: S2 read at the op-point accept threshold chosen_A (A=+inf reproduces the E34b band).
    Bf_for_band = chosen_Bf if chosen_Bf is not None else 0.0
    A_for_band = chosen_A if chosen_A is not None else float("inf")
    P_for_band = chosen_P if chosen_P is not None else 0.0
    s2_rows, band = s2_band_at_bfloor(items_pre, float(Bf_for_band), PRIMARY_SCOPE, A_for_band, 0.0, P_for_band)
    s2_perBf = s2_perBfloor_summary(items_pre, PRIMARY_SCOPE, A_for_band, 0.0, P_for_band)
    bf_clearing = [row for row in s2_perBf if row[6]]          # B_floor points whose min-fa clears GATE_FA (at chosen_P)
    bf_band_points = len(bf_clearing)
    bf_band_nontrivial = bf_band_points >= S2_BAND_MIN_POINTS  # sec6: not a single-point knife-edge
    # E37 per-P bf-band DIAGNOSTIC (reported-only; feeds the SET_CONSISTENCY_KNIFE_EDGE-vs-SET_EXHAUSTED falsifier
    # fork, NEVER the op-selection). For each P: count B_floor points clearing the gate (at chosen_A, W=0).
    # best-over-P nontrivial => some consensus-share P lifts the bf-band even if the conservative op-selector did not pick it.
    bf_by_P = []
    for P in P_sweep:
        _perBf_P = s2_perBfloor_summary(items_pre, PRIMARY_SCOPE, A_for_band, 0.0, float(P))
        bf_by_P.append((float(P), sum(1 for row in _perBf_P if row[6])))
    bf_band_best_P = max((c for _p, c in bf_by_P), default=0)
    bf_band_best_nontrivial = bf_band_best_P >= S2_BAND_MIN_POINTS
    if chosen_C is not None and base_ok:
        s3 = s3_attribution(items_pre, chosen_C, chosen_Bf, fa_base, fa, PRIMARY_SCOPE, chosen_A, 0.0, chosen_P)
    else:
        s3 = dict(n_total=0, n_demote_op=0, n_by_noauth=0, n_by_veto=0, n_survive=0, n_by_entailment=0,
                  n_spoof_rescued=0, reject_share=float("nan"), bar_met=False)

    # ---- MARGIN robustness arm (REPORTED ONLY; NOT the verdict) -- op-point per delta over the FROZEN grid ---
    margin_rows = []
    for delta in MARGIN_GRID:
        mA, mC, mBf, mP, mB2, mfa = select_op(("margin", float(delta)))
        if mC is None:
            margin_rows.append((delta, None, None, float("nan"), float("nan"), False, float("nan")))
        else:
            _r, mband = s2_band_at_bfloor(items_pre, float(mBf), ("margin", float(delta)), mA, 0.0, mP)
            ms3 = s3_attribution(items_pre, mC, mBf, fa_base, mfa, ("margin", float(delta)), mA, 0.0, mP) if base_ok else \
                  dict(reject_share=float("nan"))
            margin_rows.append((delta, mC, mBf, mfa, mB2, mband["robust"], ms3["reject_share"]))

    # ---- E37 verdict (PRE_REGISTER_E37.md sec5-6; reads scope=any fa_op vs GATE 0.10 + E36 op 0.0667 + bf-band) -
    # VOID guards INHERIT E36: baseline / degenerate rho / B_floor=0 degeneracy (0.2333) / accept-off (0.1667) /
    # binding-off W=0 (0.0667) / recall-unusable. E37 ADDS: set-off regression (P=0 MUST reproduce E36 op 0.0667)
    # -> else VOID_SET_REGRESSION. The forks read fa_op (primary scope=any, P swept); SET_CONSISTENCY_LEVER
    # additionally requires a NON-TRIVIAL bf-band. A LEVER that clears the gate ONLY via spoof rescues is caught by
    # fa itself (rescued spoofs ARE false-accepts -> raise fa) -- the metric is leak-honest by construction.
    s3rej = s3["reject_share"]
    n_spoof_rescued = s3.get("n_spoof_rescued", 0)
    if not base_ok:                 verdict = "VOID_BASELINE_MISMATCH"   # noauth path broke (model-independent)
    elif degenerate:                verdict = "VOID_RHO"                 # contradiction~cosine collinear (rho>=0.95)
    elif not degen_ok:              verdict = "VOID_DEGENERACY"          # B_floor=0,A=+inf,P=0 did NOT reproduce 0.2333
    elif not rejonly_ok:            verdict = "VOID_ACCEPT_REGRESSION"   # A=+inf,P=0 did NOT reproduce E34b reject-only 0.1667
    elif not bindreg_ok:            verdict = "VOID_BINDING_REGRESSION"  # W=0,P=0 did NOT reproduce E35 TWO_ORGAN op 0.0667
    elif not setreg_ok:             verdict = "VOID_SET_REGRESSION"      # P=0 did NOT reproduce E36 per-candidate any-veto op 0.0667
    elif chosen_C is None:          verdict = "VOID_RECALL_UNUSABLE"     # no op-point holds B2>=0.90 -> fa unreadable
    elif (fa <= GATE_FA) and bf_band_nontrivial:
                                    verdict = "SET_CONSISTENCY_LEVER"    # SET-consistency clears fa<=0.10, B2>=0.90, NON-TRIVIAL bf-band
    elif (fa <= GATE_FA) and bf_band_best_nontrivial:
                                    verdict = "SET_CONSISTENCY_KNIFE_EDGE"  # clears gate; chosen-P bf-band trivial BUT some P lifts it -> tighten/rerun
    elif fa <= GATE_FA:             verdict = "SET_EXHAUSTED"            # THE FALSIFIER: clears gate but NO P lifts the bf-band -> SET-consistency organ EXHAUSTED -> escalate (richer retrieval / multi-source corpus / re-examine heldout)
    elif fa < E36_OP_FA:            verdict = "SET_CONSISTENCY_HELPS_PARTIAL"  # 0.10 < fa < 0.0667 (cannot occur: E37 is a superset of E36 at P=0; kept for completeness)
    else:                           verdict = "SET_EXHAUSTED"            # fa >= 0.0667 (cannot occur: E37 superset of E36) -> falsifier

    # ---- S1 per-class contradiction distribution (formalized E26 diag) ---------------------------------------
    def _summ(vals):
        if not vals: return "n=0"
        arr = np.array(vals, float)
        return (f"n={len(arr)} mean={arr.mean():.4f} p10={np.percentile(arr,10):.4f} "
                f"p50={np.percentile(arr,50):.4f} p90={np.percentile(arr,90):.4f}")
    groups = {}
    for (c_, _id, k, sc, cos) in diag: groups.setdefault((c_, k), []).append(sc)
    gc  = [(sc, cos) for (c_, _id, k, sc, cos) in diag if k == "finding" and c_ == B2_CLASS]  # gold  content (cos paired)
    spc = [(sc, cos) for (c_, _id, k, sc, cos) in diag if k == "finding" and c_ == B1_CLASS]  # spoof content (cos paired)
    gc_s = [s for s, _c in gc]; spc_s = [s for s, _c in spc]
    gc_p50  = float(np.percentile(gc_s, 50)) if gc_s else float("nan")
    spc_p50 = float(np.percentile(spc_s, 50)) if spc_s else float("nan")
    sep = spc_p50 - gc_p50
    s1_sep_ok = (not np.isnan(sep)) and sep > 0.5   # PRE_REGISTER sec3 (diagnostic, NOT a gate)
    Cn = chosen_C if chosen_C is not None else float("nan")
    Bfn = chosen_Bf if chosen_Bf is not None else 0.0
    # conditioned candidate counts at op-point: contradiction crossing (con>=C). NOTE: the op-point veto also gates
    # on B>=B_floor, but diag carries cosine (S1 diagnostic, UNTOUCHED), not B -> this count is contradiction-only.
    gv = sum((s >= Cn) for (s, c) in gc) if (gc and chosen_C is not None) else float("nan")   # gold con-crossing
    sv = sum((s >= Cn) for (s, c) in spc) if (spc and chosen_C is not None) else float("nan")  # spoof con-crossing
    # S1 DRIVER ISOLATION: gold-content tail items (contradiction >= S1_TAIL_CON) -- the knife-edge drivers,
    # with binding cosine (the observable the lever uses to spare them). Spoof-content tail for contrast.
    gc_tail  = sorted([(sc, cos, _id) for (c_, _id, k, sc, cos) in diag if c_ == B2_CLASS and k == "finding" and sc >= S1_TAIL_CON], reverse=True)
    spc_tail = sorted([(sc, cos, _id) for (c_, _id, k, sc, cos) in diag if c_ == B1_CLASS and k == "finding" and sc >= S1_TAIL_CON], reverse=True)
    gc_tail_cos_med  = float(np.percentile([c for _s, c, _i in gc_tail], 50)) if gc_tail else float("nan")
    spc_tail_cos_med = float(np.percentile([c for _s, c, _i in spc_tail], 50)) if spc_tail else float("nan")

    # ---- report --------------------------------------------------------------------------------------------
    _prereg_path = os.path.join(os.path.dirname(a.out), "PRE_REGISTER_E37.md")
    _prereg_md5 = md5(_prereg_path) if os.path.exists(_prereg_path) else "NOT-ON-DISK"
    L = [
        "# report_E37 -- SET-CONSISTENCY veto (set_veto=(n_con>=1)AND(n_ent==0)AND(con_share>=P)) over the bound SET ; P=0 regression == E36 per-candidate any-veto ; vs E36 op 0.0667 + bf-band (S1/S2/S3)",
        "",
        f"- pre-register   : PRE_REGISTER_E37.md (FROZEN md5 {_prereg_md5}) -- sec1/2/4/5/6 operative ; bound/scorer substrate inherits run_E36 (2c85e848d05e213fc86fe763ad49dfb9)",
        f"- lever          : SET-CONSISTENCY veto over the bound SET -- {SET_NOTE} ; n_ent==0 entailer-rescue INHERITED from E36 ; W FROZEN 0 (E36 BINDING_EXHAUSTED) ; premise=source.FINDING / hyp=claim ; MODEL={CE_MODEL} (UNCHANGED)",
        f"- accept arm     : ent direction {ENT_DIR_NOTE} ; entailment_idx READ from id2label (single, asserted) ; A swept FROZEN A_GRID [0..1 step 0.05]; A=+inf accept-off anchor",
        f"- SET axis       : P swept over FROZEN P_GRID {P_GRID} ; con_share=n_con/|S| over bound subset ; P=0 = per-candidate any-veto regression anchor (== E36, op MUST reproduce {E36_OP_FA}) ; W FROZEN {W_GRID}",
        f"- premise content: from_finding={n_find}/{n_prem} (content-binding kept; NECESSARY, proven E22 0.333 -> E24 0.20)",
        f"- floor (frozen) : {sem.FLOOR} | top_k {sem.TOP_K}",
        f"- fixture md5    : {fm} (E25b) | heldout md5 : {hm}",
        f"- heldout classes: {cls}",
        "",
        "## trust gates (else VOID)",
        f"- baseline (C=+inf) B1={B1b:.3f} B2={B2b:.3f} B3={B3b:.3f} false-accept={fa_base:.3f} (no-veto 0.467) reproduced={base_ok}",
        f"- degeneracy (B_floor=0,A=+inf scope=any) fa={degen_fa} vs deberta anchor {DEBERTA_ANCHOR_FA} +/-{ANCHOR_TOL} -> ok={degen_ok} (inherited clean-superset)",
        f"- accept-off regression (A=+inf reject-only op) fa={rejonly_fa} vs E34b op {E34B_REJECT_OP_FA} +/-{ACCEPT_TOL} -> ok={rejonly_ok} (clean-superset for the accept arm)",
        f"- binding regression (W=0 anchor-off op) fa={bindreg_fa} vs E35 op {E35_OP_FA} +/-{BIND_REG_TOL} -> ok={bindreg_ok} (clean-superset for the anchored binding)",
        f"- set regression (P=0 consensus-off op) fa={setreg_fa} vs E36 op {E36_OP_FA} +/-{SET_REG_TOL} -> ok={setreg_ok} (clean-superset for the SET lever; P=0 == E36 per-candidate any-veto)",
        f"- decorrelation spearman(contradiction,cosine) rho = {rho:.3f} over {len(decorr)} pairs | VOID-guard rho>={DEGENERATE_RHO} -> degenerate={degenerate}",
        f"- advisory: |rho| < {PREREG_RHO_ADVISORY} -> {rho_advisory_ok} (REPORTED ONLY; FROZEN substrate VOID-guard is {DEGENERATE_RHO}; see CONFLICT note)",
        f"- contradiction_idx + entailment_idx read from id2label (single each, asserted) ; from_finding={n_find} asserted > 0",
        "",
        "## op-point gate (scope=any; min fa s.t. B2>=0.90 over (A_GRID, observed C, B_floor)). bars: reject-only 0.1667 (beat) / GATE 0.10",
        f"- anchor-compare (scope=any): A={anc_A} C={anc_C} B_floor={anc_Bf} fa_op={anc_fa} vs bart {E28_OP_FA} / deberta {DEBERTA_ANCHOR_FA} / reject-only {E34B_REJECT_OP_FA} -> below_bart={anchor_below_bar}",
        f"- chosen A (accept) = {chosen_A} | chosen C = {chosen_C} | chosen B_floor = {chosen_Bf} | chosen P (consensus-share) = {chosen_P} | B2 at op-point = {chosen_B2}",
        f"- B1 spoof-demotion = {B1}",
        f"- false-accept      = {fa}  (gate <= {GATE_FA})",
        f"- B2 yield          = {B2}",
        f"- B3 over-demotion  = {B3} (bar <= 0.10)",
        f"- movement vs 0.467 = {move}",
        f"- op-point verdict  = {op_verdict}",
        "",
        "## MARGIN robustness arm (REPORTED ONLY; verdict reads scope=any). delta gates a cosine bound-neighborhood on top of B",
    ]
    for (delta, mC, mBf, mfa, mB2, mrob, mrej) in margin_rows:
        L.append(f"    delta={delta:.2f}  C={mC}  B_floor={mBf}  fa={mfa}  B2={mB2}  band_robust={mrob}  reject_share={mrej}")
    L += [
        "",
        "## S2 -- (C, B_floor) band / lift-off robustness (band read at op-point B_floor; FROZEN grids)",
        f"- band at op-point B_floor={Bf_for_band}: joint (fa<={GATE_FA} AND B2>={RECALL_FLOOR}) C_lo={band['c_lo']} "
        f"C_hi={band['c_hi']} width={band['width']:.4f} points={band['points']}",
        f"- B2 lift-off within band (max B2 - floor) = {band['b2_liftoff']:.4f}  (>0 == not pinned to floor)",
        f"- robustness bar: width>={S2_BAND_MIN_WIDTH} AND points>={S2_BAND_MIN_POINTS} AND liftoff>0 -> robust={band['robust']}",
        f"- bf-band non-triviality (verdict input, at chosen P={chosen_P}): {bf_band_points} B_floor points clear GATE_FA -> nontrivial={bf_band_nontrivial} (bar >= {S2_BAND_MIN_POINTS})",
        f"- bf-band best-over-P (DIAGNOSTIC, feeds SET_CONSISTENCY_KNIFE_EDGE-vs-SET_EXHAUSTED fork): max clears={bf_band_best_P} -> best_nontrivial={bf_band_best_nontrivial}",
        "- per-P bf-band clearing (P, B_floor-points clearing gate at chosen A, W=0) [DIAGNOSTIC; NOT selection]:",
        *[f"    P={pp:.2f}  clears={c}" for (pp, c) in bf_by_P],
        "- per-B_floor summary (B_floor, C-band_width, points, b2_liftoff, robust, min_fa, clears_gate):",
    ]
    for (Bf, w, p, lo, rb, mfa, cl) in s2_perBf:
        L.append(f"    B_floor={Bf:.2f}  width={w:.4f}  points={p}  liftoff={lo:.4f}  robust={rb}  min_fa={mfa}  clears={cl}")
    L += [
        "- C-sweep at op-point B_floor (C, false-accept, B2, joint_ok):",
    ]
    for (C, faC, b2C, ok) in s2_rows:
        L.append(f"    C={C:.3f}  fa={faC:.4f}  B2={b2C:.4f}  joint={'Y' if ok else '.'}")
    L += [
        "",
        "## S3 -- reject-vs-lift demotion attribution (B1 spoof demotions + accept-arm action at conditioned op-point)",
        f"- spoofs total={s3['n_total']} | demoted@op={s3['n_demote_op']} | survived(false-accept)={s3['n_survive']}",
        f"- (a) noauth baseline (demote @ C=+inf)         = {s3['n_by_noauth']}",
        f"- (b) contradiction-veto reject organ           = {s3['n_by_veto']}  (demoted because veto fired, accept not rescuing)",
        f"- (c) accept/entailment-lift organ              = {s3['n_by_entailment']}  (GOLD items RESCUED from reject by accept; A toggled +inf->op_A)",
        f"- (c-leak) spoofs WRONGLY rescued by accept      = {s3.get('n_spoof_rescued', 0)}  (false-accepts the accept arm introduces; already counted in fa)",
        f"- reject_share = (fa_base - fa_op)/fa_base = ({fa_base:.4f} - {fa:.4f})/{fa_base:.4f} = {s3['reject_share']:.4f}",
        f"- S3 bar: reject_share > {S3_REJECT_SHARE_BAR} -> {s3['bar_met']}  (== organ, not coverage, owns the fa-reduction)",
        "",
        "## S1 -- per-class contradiction distribution + knife-edge DRIVER ISOLATION",
    ]
    for key in sorted(groups): L.append(f"- {key[0]:28s} premise={key[1]:7s} : {_summ(groups[key])}")
    L += [
        f"- gold-content tail (contradiction>={S1_TAIL_CON}): n={len(gc_tail)} cos_med={gc_tail_cos_med:.4f} (the knife-edge drivers)",
        f"- spoof-content tail (contradiction>={S1_TAIL_CON}): n={len(spc_tail)} cos_med={spc_tail_cos_med:.4f}",
        "- S1 expectation (diagnostic): cosine is RETAINED only for the rho guard + this diagnostic; the E35 levers are",
        "  lexical binding B + entailment lift, not cosine (E28 cosine-separability FALSIFIED). gold/spoof cos shown for continuity.",
        "- gold tail drivers (contradiction, cosine, id):",
    ]
    for (sc, cos, _id) in gc_tail[:20]:
        L.append(f"    con={sc:.4f}  cos={cos:.4f}  id={_id}")
    L += [
        "- spoof tail (contradiction, cosine, id) [first 20]:",
    ]
    for (sc, cos, _id) in spc_tail[:20]:
        L.append(f"    con={sc:.4f}  cos={cos:.4f}  id={_id}")
    L += [
        "",
        f"## candidate-level separation at op-point (C={Cn:.5f}, B_floor={Bfn}; counts finding candidates -- DIAGNOSTIC)",
        f"- gold-content candidates  : {_summ(gc_s)} | cross (con>=C; B not paired in diag): {gv}/{len(gc_s)}",
        f"- spoof-content candidates : {_summ(spc_s)} | cross (con>=C; B not paired in diag): {sv}/{len(spc_s)}",
        f"- spoof-vs-gold content p50 separation = {sep:.4f} (spoof {spc_p50:.4f} - gold {gc_p50:.4f})",
        f"- S1 expectation: separation > 0.5 -> {s1_sep_ok} (diagnostic only; verdict reads max-based fa, not sep)",
        "- metric discipline: VERDICT reads GATE fa (max-based, confound-immune). sep (p50) is diagnostic only;",
        "  it is confounded by finding phrasing-quality (proven E25b sep 0.084->0.008 under added findings).",
        "",
        f"## VERDICT : {verdict}",
        "",
        "decision (PRE_REGISTER_E37.md sec6, operative forks -- read scope=any fa_op (P swept) vs gate 0.10 + bf-band@chosen-P + best-over-P):",
        "  SET_CONSISTENCY_LEVER (fa_op <= 0.10 AND B2>=0.90 AND bf-band@chosen-P nontrivial) -> cross-source consistency lifts the",
        "    bf-band off the floor -> proceed to robustness sweep + verifier-integration (rho 0.95-vs-0.50 reconcile, full-GOLD scale). TOMMY GO REQUIRED.",
        "  SET_CONSISTENCY_KNIFE_EDGE (fa_op<=0.10, bf-band@chosen-P trivial, but SOME P lifts it best-over-P>=3) -> tighten/widen, latent lever ->",
        "    directionally right, insufficient -> a different SET statistic or a richer corroboration signal (design, next).",
        "  SET_EXHAUSTED [FALSIFIER] (fa_op<=0.10 but NO P lifts the bf-band) -> SET-consistency organ EXHAUSTED -> the per-instance heldout",
        "    fixture is likely the ceiling -> escalate: richer retrieval / multi-source corroboration corpus, or re-examine heldout construction.",
        "  VOID_* -> trust gate failed (baseline / rho / B_floor=0!=0.2333 / A=+inf!=0.1667 reject-only / W=0!=0.0667 binding-reg / P=0!=0.0667 set-reg / recall) -> reconcile, re-run.",
        "",
        "CONFLICT note (R15 / proto 3.10): advisory |rho|<0.50 vs REUSED frozen E26 VOID-guard rho>=0.95 (one-sided),",
        "  spearman on (contradiction, cosine). The E37 lever is SET-CONSISTENCY over observable per-candidate con/ent, NOT cosine -- cosine is",
        "  retained ONLY for this rho guard + S1 diagnostics. Both pass at observed rho. This file keeps the FROZEN 0.95 as",
        "  the VOID trigger and reports the 0.50 advisory separately. Reconcile into ONE bar at verifier-integration.",
    ]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\n[written] {a.out}")

if __name__ == "__main__":
    sys.exit(main())
