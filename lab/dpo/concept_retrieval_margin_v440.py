#!/usr/bin/env python3
"""
concept_retrieval_margin_v440.py -- FROZEN-M transfer test on a DISJOINT held-out (split B).

Evolution of concept_retrieval_margin_v439.py (SKILL 4: change representation, not logic).
v439 built the margin-gate and PASSED dominance on the ORIGINAL 7 (F1h..F7h): boost 5/7,
wrong-blocked 2/2, F2h recovered false-abstain->boost, margin gap +0.0104. GRUB carried:
M=0.025 was the midpoint of the v439 gap -- FIT to those 7. Not scale-proven (N=7).

v440 tests TRANSFER: freeze M=0.025 (do NOT refit) and run the SAME gate on SPLIT B --
7 fresh cloze on the same 7 concepts, phrasings disjoint (verified: no exact match) from
BOTH the train corpus (centroid source) AND the old CLOZE_HELD. Same frozen centroids,
same detect_concept_full, same gate. Question: does the v439-fit threshold still separate
correct-from-wrong and block wrong-detects on facts it was never tuned on?

Inherited from v439 BYTE-FOR-BYTE (evolution = change representation, not logic):
  MODEL_ID, DATA_PATH, DETECT_LAYER, GOLD_FRAGMENTS, KEY, KEY_NEG_SI4, M=0.025,
  tok_id, get_hidden_at_layer, cosine_sim, cloze_to_question, answer_correct,
  build_user_content, generate_answer, centroid block, detect_concept_full,
  gate `gated = margin < M`, boost/blocked/false-abstain metrics, separability block.
Changed representation ONLY:
  - held-out CONTENT: CLOZE_HELD list -> split B (F1b..F7b). Var name kept for identical loop.
  - PASS_BOOST 5 -> 4 (split-B pre-registered bar).
  - M annotated FROZEN (value byte-identical 0.025).
  - verdict framing: dominance/F2h -> frozen-M transfer (add sep_ok=gap>0 to PASS).

Inherited from v437 BYTE-FOR-BYTE (evolution = change representation, not logic):
  MODEL_ID, DATA_PATH, DETECT_LAYER, CLOZE_HELD, GOLD_FRAGMENTS, KEY, KEY_NEG_SI4,
  tok_id, get_hidden_at_layer, cosine_sim, cloze_to_question, answer_correct,
  build_user_content, generate_answer, the L13 centroid computation block,
  and the baseline/gated eval-loop STRUCTURE + boost/blocked/false-abstain metrics.
Inherited from v438 BYTE-FOR-BYTE:
  detect_concept_full (returns full sorted (si, sim) vector; detected_si = top1_si).
Changed representation ONLY:
  - gate variable: v437 `gated = det_sim < TAU`  ->  v439 `gated = margin < M`
    where margin = top1_sim - top2_sim (from detect_concept_full).
  - M = 0.025 (midpoint of v438 gap 0.0205 <-> 0.0309; pack v439 sec3, immutable).
G3 FALSIFIER (pre-registered at v439 close, immutable -- transcribed from that turn):
  On split B under FROZEN M=0.025:
    margin gap <= 0 (min correct-detect margin <= max wrong-detect margin -- separation
    did not reproduce on fresh facts) OR boost < 4/7 OR any wrong-detect passes the gate
    (margin >= M on a wrong-detect)
  -> the frozen threshold was FIT to the old 7, not scale-robust; margin trigger does not
     transfer across disjoint fact sets
  -> close the geometric-trigger line; pivot to a NON-geometric retrieval trigger
     (retrieval-verification / abstain-by-agreement / answer-consistency).

v440 - TRACK 2 ORGANISM - retrieval trigger: MARGIN-gate frozen-M TRANSFER (split B).
Run: LOCAL RTX 4070 8GB, 4-bit NF4. 35 centroid + 7 detect fwd + <=14 gen(100tok). <2min, $0.
"""

import torch
import json, os, time

MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/margin_gate_split_b_v440.json"
DETECT_LAYER = 13
M = 0.025             # FROZEN from v439 (NOT refit to split B). Transfer test: does the v439-fit threshold hold on fresh facts.
PASS_BOOST = 4        # split-B pre-registered bar (v439 close falsifier): boost < 4/7 -> m does not transfer
MAX_NEW = 100

# -- GOLD fragments (identical to v434/v436/v437) --
GOLD_FRAGMENTS = {
    0: "Probability calculations against random self-replicator assembly are misleading because they assume modern protein complexity rather than simpler precursor molecules that could have initiated life.",
    1: "The fraction of random amino-acid sequences with simple biological function is roughly one in ten to the eleven, or approximately 10^-11, based on empirical studies of random polypeptide libraries.",
    2: "About a third of the 473 genes in JCVI-syn3.0, the minimal synthetic cell, have functions that remain unknown despite being essential for life.",
    3: "Eigen's error catastrophe describes the threshold where copying errors in prebiotic replication outpace natural selection, limiting the complexity of early replicators without enzymatic error correction.",
    4: "According to Totani (2020), the observable universe is not sufficient for random nucleotide assembly to produce a functional RNA replicase by chance alone.",
    5: "Shannon's information theory deliberately excludes the concept of meaning, measuring only statistical uncertainty of message transmission regardless of semantic content.",
    6: "The Cit+ phenotype in Lenski's long-term evolution experiment enabled E. coli to metabolize citrate under aerobic conditions, emerging after approximately 31,500 generations.",
}

# -- SPLIT B: 7 DISJOINT held-out cloze (v440). New phrasings, same 7 concepts/targets.
#    Verified disjoint (no exact match) vs train corpus (centroid source) AND vs old CLOZE_HELD
#    (F1h..F7h). Tests whether frozen M transfers to fresh facts or was fit to the old 7.
#    Var name kept CLOZE_HELD so the eval loop stays byte-identical to v439 (SKILL 4). --
CLOZE_HELD = [
    {"id": "F1b", "prompt": "Judging life's origin impossible by assuming modern-protein complexity in the very first replicator is", "target": "misleading", "si": 0},
    {"id": "F2b", "prompt": "Testing random protein chains for activity, the hit rate for any biological function is on the order of", "target": "10^-11", "si": 1},
    {"id": "F3b", "prompt": "Even in JCVI-syn3.0, the biological role of roughly a third of its essential genes is still", "target": "unknown", "si": 2},
    {"id": "F4b", "prompt": "Past the error threshold, copying mistakes pile up faster than they can be purged by natural", "target": "selection", "si": 3},
    {"id": "F5b", "prompt": "Could random chemistry across the entire observable universe realistically assemble a working RNA replicase?", "target": "No", "si": 4},
    {"id": "F6b", "prompt": "Shannon's entropy measures uncertainty while deliberately ignoring a message's", "target": "meaning", "si": 5},
    {"id": "F7b", "prompt": "In the LTEE, E. coli eventually gained the ability to consume citrate in the presence of", "target": "oxygen", "si": 6},
]

# -- key-fact keywords per concept (identical to v436/v437, immutable) --
KEY = {
    0: ["misleading", "wrong reference", "flawed", "not as impossibly", "not impossibly"],
    1: ["eleven", "10^-11", "10^11", "10-11", "10^{-11}", "1e-11", "ten to the eleven"],
    2: ["unknown", "not known", "unclear", "not understood", "mysteri"],
    3: ["selection"],
    5: ["meaning", "semantic"],
    6: ["aerobic", "oxygen"],
}
KEY_NEG_SI4 = ["not sufficient", "not enough", "not large enough", "insufficient", "cannot", "too small", "not big enough"]


def cloze_to_question(cloze):
    s = cloze.strip()
    if s.endswith("?"):
        return s
    s = s.rstrip(" .,:;")
    q = s + " what?"
    return q[0].upper() + q[1:]


def answer_correct(si, answer):
    low = answer.lower()
    if si == 4:
        if any(k in low for k in KEY_NEG_SI4):
            return True
        first = low.strip().lstrip(".,!:*-\"' ")
        toks = first.split()
        return bool(toks) and toks[0].strip(".,!:") == "no"
    return any(k.lower() in low for k in KEY[si])


def tok_id(tokenizer, word):
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    if len(ids) > 1:
        if tokenizer.decode([ids[0]]).strip() == "":
            return ids[1]
    return ids[0]


def get_hidden_at_layer(model, tokenizer, prompt, layer):
    dev = next(model.parameters()).device
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    with torch.no_grad():
        out = model(ids, use_cache=False, output_hidden_states=True)
    return out.hidden_states[layer + 1][0, -1, :].float().cpu()


def cosine_sim(a, b):
    return torch.dot(a, b) / (a.norm() * b.norm() + 1e-8)


def build_user_content(question, gold_fragment=None):
    if gold_fragment is None:
        return f"<question>{question}</question>\nAnswer concisely."
    return (f"<context>{gold_fragment}</context>\n"
            f"<question>{question}</question>\n"
            f"Answer concisely based on the context above.")


def generate_answer(model, tokenizer, user_content):
    dev = next(model.parameters()).device
    msgs = [{"role": "user", "content": user_content}]
    text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tokenizer(text, return_tensors="pt").to(dev)
    in_len = ids.input_ids.shape[1]
    with torch.no_grad():
        gen = model.generate(**ids, max_new_tokens=MAX_NEW, do_sample=False,
                             temperature=None, top_p=None, top_k=None,
                             pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(gen[0][in_len:], skip_special_tokens=True).strip()


def main():
    assert torch.cuda.is_available(), "CUDA required"
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    lines = [json.loads(l) for l in open(DATA_PATH)]
    train_prompts, train_labels = [], []
    for si in range(7):
        group = [l for l in lines if l["source_idx"] == si][:5]
        for g in group:
            train_prompts.append(g["prompt"])
            train_labels.append(si)

    print("=" * 72)
    print("MARGIN-GATE FROZEN-M TRANSFER v440 (organism, split B disjoint held-out)")
    print(f"Model: {MODEL_ID}")
    print(f"Detect layer: L{DETECT_LAYER}   M={M} (FROZEN from v439, not refit)")
    print(f"G3: gap>0 AND boost>=4/7 AND all wrong-detects blocked (margin<M) else M does not transfer")
    print("=" * 72)

    print("\n[1] Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True)
    model.eval()
    print(f"  {model.config.num_hidden_layers} layers, hidden={model.config.hidden_size}")

    # -- centroid computation: BYTE-IDENTICAL to v437 --
    print(f"\n[2] Computing concept centroids at L{DETECT_LAYER} (instruct geometry)...")
    t0 = time.time()
    centroid_vecs = {si: [] for si in range(7)}
    for i, prompt in enumerate(train_prompts):
        h = get_hidden_at_layer(model, tokenizer, prompt, DETECT_LAYER)
        centroid_vecs[train_labels[i]].append(h)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(train_prompts)}")
    centroids = {}
    for si in range(7):
        c = torch.stack(centroid_vecs[si]).mean(0)
        centroids[si] = c / c.norm()
    print(f"  7 centroids computed ({time.time()-t0:.1f}s)")

    # -- detect_concept_full: BYTE-IDENTICAL to v438 (full sorted (si,sim) vector) --
    def detect_concept_full(prompt):
        h = get_hidden_at_layer(model, tokenizer, prompt, DETECT_LAYER)
        h_norm = h / (h.norm() + 1e-8)
        sims = []
        for si, c in centroids.items():          # si order 0..6 preserved
            sims.append((si, cosine_sim(h_norm, c).item()))
        # stable sort by sim desc; ties keep ascending-si (matches v437 argmax: first/lowest si on tie)
        sims_sorted = sorted(sims, key=lambda x: -x[1])
        return sims_sorted

    print(f"\n[3] Detection + margin-gated QA (baseline / gated)...")
    results = []
    n_detect_ok = 0
    n_boost = 0          # (a) detect=Y & margin>=M & base-wrong & gated-correct
    n_blocked = 0        # (b) detect=N & margin<M  (gate fired on wrong detect)
    n_false_abstain = 0  # (c) detect=Y & margin<M  (gate suppressed a correct detect)
    for item in CLOZE_HELD:
        question = cloze_to_question(item["prompt"])

        sims_sorted = detect_concept_full(item["prompt"])
        top1_si, top1_sim = sims_sorted[0]
        top2_si, top2_sim = sims_sorted[1]
        margin = top1_sim - top2_sim
        detected_si = top1_si
        detect_ok = (detected_si == item["si"])
        n_detect_ok += int(detect_ok)

        gated = margin < M     # abstain: margin below threshold -> no retrieval (REP change vs v437 det_sim<TAU)

        ans_base = generate_answer(model, tokenizer, build_user_content(question, None))
        base_ok = answer_correct(item["si"], ans_base)

        if gated:
            ans_gated = ans_base      # no-retrieve: baseline answer, no extra generation
            retrieved = False
        else:
            ans_gated = generate_answer(model, tokenizer,
                                        build_user_content(question, GOLD_FRAGMENTS[detected_si]))
            retrieved = True
        gated_ok = answer_correct(item["si"], ans_gated)

        boost = detect_ok and (not gated) and (not base_ok) and gated_ok
        blocked = (not detect_ok) and gated
        false_abstain = detect_ok and gated
        n_boost += int(boost)
        n_blocked += int(blocked)
        n_false_abstain += int(false_abstain)

        r = {
            "id": item["id"], "true_si": item["si"], "question": question,
            "detected_si": detected_si, "detect_ok": detect_ok,
            "top1_si": top1_si, "top1_sim": round(top1_sim, 4),
            "top2_si": top2_si, "top2_sim": round(top2_sim, 4),
            "margin": round(margin, 4), "M": M, "gated": gated, "retrieved": retrieved,
            "base_ok": base_ok, "gated_ok": gated_ok,
            "boost": boost, "wrong_injection_blocked": blocked, "false_abstain": false_abstain,
            "ans_base": ans_base, "ans_gated": ans_gated,
        }
        results.append(r)

        d = "Y" if detect_ok else "N"
        g = "GATE" if gated else "pass"
        tag = "+boost" if boost else ("+block" if blocked else ("-fabst" if false_abstain else "      "))
        print(f"  {item['id']:4s}: detect={d} margin={margin:.4f} {g} | "
              f"base={'OK ' if base_ok else 'no '} gated={'OK ' if gated_ok else 'no '} [{tag}]")

    # -- margin separability (from run) --
    correct_margins = [r["margin"] for r in results if r["detect_ok"]]
    wrong_margins = [r["margin"] for r in results if not r["detect_ok"]]
    min_correct = min(correct_margins) if correct_margins else None
    max_wrong = max(wrong_margins) if wrong_margins else None
    gap = (min_correct - max_wrong) if (min_correct is not None and max_wrong is not None) else None

    n_wrong_detects = len(wrong_margins)
    n_wrong_passed = sum(1 for r in results if (not r["detect_ok"]) and (not r["gated"]))
    block_ok = (n_wrong_passed == 0)
    boost_ok = (n_boost >= PASS_BOOST)

    # -- FROZEN-M TRANSFER falsifier (v439 close, pre-registered, immutable):
    #    gap<=0 OR boost<4/7 OR any wrong-detect passes frozen M -> m does NOT transfer to fresh facts. --
    sep_ok = (gap is not None and gap > 0)

    if boost_ok and block_ok and sep_ok:
        verdict = "PASS"
        conclusion = (f"Frozen M={M} (fit on old 7, NOT refit) TRANSFERS to disjoint split B: "
                      f"margin still separates (min correct {min_correct} > max wrong {max_wrong}, gap {gap} > 0), "
                      f"boost {n_boost}/7 (>= {PASS_BOOST}), and all {n_wrong_detects} wrong-detect(s) blocked "
                      f"(margin < M). Margin trigger is scale-robust across two disjoint fact sets at N=7+7 "
                      f"-> geometric trigger viable; next widen concept coverage / raise N.")
    else:
        verdict = "FAIL"
        reasons = []
        if not sep_ok:
            reasons.append(f"margin gap {gap} <= 0 (separation did NOT reproduce on fresh facts: "
                           f"min correct {min_correct} <= max wrong {max_wrong})")
        if not boost_ok:
            reasons.append(f"boost {n_boost}/7 < {PASS_BOOST} (frozen M did not recover enough correct "
                           f"retrievals on split B; false-abstain={n_false_abstain})")
        if not block_ok:
            reasons.append(f"{n_wrong_passed}/{n_wrong_detects} wrong-detect(s) passed frozen M={M} "
                           f"(margin >= M on a wrong-concept -> wrong GOLD injected)")
        conclusion = ("Frozen M does NOT transfer: " + "; ".join(reasons) +
                      ". The margin threshold was fit to the old 7, not scale-robust. "
                      "Close the geometric-trigger line; pivot to a NON-geometric retrieval trigger "
                      "(retrieval-verification / abstain-by-agreement / answer-consistency).")

    print(f"\n{'='*72}")
    print(f"G3 VERDICT (frozen-M transfer): {verdict}")
    print(f"  Detection (split B):          {n_detect_ok}/7")
    print(f"  (a) mechanistic boost:        {n_boost}/7   (need {PASS_BOOST})")
    print(f"  (b) wrong-injections blocked: {n_blocked}/{n_wrong_detects}")
    print(f"  (c) false-abstain:            {n_false_abstain}/{len(correct_margins)}")
    print(f"  margin separability: min_correct={min_correct}  max_wrong={max_wrong}  gap={gap}  (>0 = transfers)")
    print(f"  wrong-detects passing gate:   {n_wrong_passed}/{n_wrong_detects}")
    print(f"  {conclusion}")
    print(f"{'='*72}")

    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v440", "axis": "margin-gate-frozen-m-transfer", "track": "ORGANISM",
        "held_out": "split_B (7 disjoint cloze, new phrasings, same 7 concepts)",
        "model": MODEL_ID, "detect_layer": DETECT_LAYER, "M": M, "M_frozen_from": "v439",
        "method": "cosine-to-centroid @L13 detect (full sorted vector); gate margin(top1-top2)<M -> no-retrieve(baseline) else detected-GOLD; greedy gen; keyword correctness; M NOT refit",
        "pass_boost": PASS_BOOST,
        "n_detect_ok": n_detect_ok, "n_boost": n_boost, "n_blocked": n_blocked,
        "n_false_abstain": n_false_abstain,
        "transfer": {"sep_ok": sep_ok, "boost_ok": boost_ok, "block_ok": block_ok},
        "separability": {"min_correct": min_correct, "max_wrong": max_wrong, "gap": gap,
                         "wrong_detects": n_wrong_detects, "wrong_passed_gate": n_wrong_passed},
        "results": results, "verdict": verdict, "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
