#!/usr/bin/env python3
"""
verify_probe_v442.py -- RETRIEVAL top1-vs-top2 GOLD DISAGREEMENT probe.

PURE MEASUREMENT. No gate, no abstain. Next cheap link on the retrieval-verification axis
(cost-ascending: stop where sufficient). v441 (baseline-vs-GOLD consistency) FAILED --
gap -0.7056, signal INVERTED: it measured whether the answer SHIFTED, not whether the
retrieval was CORRECT, and conflated useful-correction (boost, base=no->gold=OK diverges)
with corruption. Both known wrong-detects sat HIGH (F3h cons 1.0 unchanged, F7h .928),
the boost-corrections sat LOW. Baseline second-signal DEAD (v441 close, DIRECTION_VECTOR).

THIS AXIS: drop baseline. Second signal = the RUNNER-UP concept's GOLD. For each held-out,
generate the answer under GOLD[top1] and under GOLD[top2], measure agreement between the
TWO retrieval answers. This measures retrieval AMBIGUITY, not answer shift.

HYPOTHESIS (directional, falsifiable): a CORRECT detect has a clean winner (top1 the right
concept, top2 a foreign concept) -> the two GOLD answers DISAGREE (LOW top1-top2 consistency).
A WRONG detect is a near-tie (v438: wrong-detects landed on centroid-3 by thin margin) ->
top1 and top2 are both near-relevant -> the two GOLD answers AGREE more, or both miss
(HIGH consistency). Expect: max(correct-detect consistency) < min(wrong-detect consistency)
i.e. correct-detects sit BELOW wrong-detects (INVERTED direction vs v441).
  Separation is clean if: max correct-detect consistency < min wrong-detect consistency
  -> gap = min_wrong - max_correct > 0.

METRIC: consistency = cosine( L13 hidden(ans_top1_gold), L13 hidden(ans_top2_gold) ).
  Reuses get_hidden_at_layer + cosine_sim. Secondary (recorded): token-Jaccard.

Held-out: ORIGINAL CLOZE_HELD (F1h..F7h), detect outcomes KNOWN (F3h, F7h wrong).

Inherited from v441/v440/v439/v437 BYTE-FOR-BYTE (evolution = change representation, not logic):
  MODEL_ID, DATA_PATH, DETECT_LAYER, GOLD_FRAGMENTS, KEY, KEY_NEG_SI4, CLOZE_HELD, tok_id,
  get_hidden_at_layer, cosine_sim, build_user_content, generate_answer, cloze_to_question,
  answer_correct, token_jaccard, the L13 centroid block, detect_concept_full.
Changed representation ONLY:
  - measurement loop: ans under GOLD[top1] vs ans under GOLD[top2] (was base vs GOLD[top1]).
  - separability DIRECTION: correct-detects expected BELOW wrong (gap = min_wrong - max_correct).

G3 FALSIFIER (pre-registered, immutable):
  gap <= 0 (max correct-detect consistency >= min wrong-detect consistency -- correct-detects
  do NOT sit below wrong-detects; the two known wrong-detects F3h/F7h are not the high pair)
  -> top1-vs-top2 disagreement is ALSO not a viable trigger
  -> retrieval-ambiguity via GOLD-answer agreement does not separate right-from-wrong either;
     the next link must leave the answer-similarity family entirely (explicit entailment: does
     the injected GOLD logically support the produced answer -- an NLI/verifier check, richer/pricier).

v442 - TRACK 2 ORGANISM - retrieval-verification: top1-vs-top2 GOLD disagreement probe.
Run: LOCAL RTX 4070 8GB, 4-bit NF4. 35 centroid + 7 detect + 14 gen(100tok) + 14 hidden. <2min, $0.
"""

import torch
import json, os, time

MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/verify_probe_v442.json"
DETECT_LAYER = 13
MAX_NEW = 100

# -- GOLD fragments (identical to v434/v436/v437/v438/v439/v440) --
GOLD_FRAGMENTS = {
    0: "Probability calculations against random self-replicator assembly are misleading because they assume modern protein complexity rather than simpler precursor molecules that could have initiated life.",
    1: "The fraction of random amino-acid sequences with simple biological function is roughly one in ten to the eleven, or approximately 10^-11, based on empirical studies of random polypeptide libraries.",
    2: "About a third of the 473 genes in JCVI-syn3.0, the minimal synthetic cell, have functions that remain unknown despite being essential for life.",
    3: "Eigen's error catastrophe describes the threshold where copying errors in prebiotic replication outpace natural selection, limiting the complexity of early replicators without enzymatic error correction.",
    4: "According to Totani (2020), the observable universe is not sufficient for random nucleotide assembly to produce a functional RNA replicase by chance alone.",
    5: "Shannon's information theory deliberately excludes the concept of meaning, measuring only statistical uncertainty of message transmission regardless of semantic content.",
    6: "The Cit+ phenotype in Lenski's long-term evolution experiment enabled E. coli to metabolize citrate under aerobic conditions, emerging after approximately 31,500 generations.",
}

# -- ORIGINAL 7 held-out cloze (identical to v434/v436/v437/v438/v439; detect outcomes KNOWN) --
CLOZE_HELD = [
    {"id": "F1h", "prompt": "The standard argument against abiogenesis via random protein assembly is widely regarded as", "target": "misleading", "si": 0},
    {"id": "F2h", "prompt": "Among random polypeptides, the chance of any biological activity is about one in ten to the", "target": "eleven", "si": 1},
    {"id": "F3h", "prompt": "Many genes in the synthetic minimal cell have purposes that remain", "target": "unknown", "si": 2},
    {"id": "F4h", "prompt": "In Eigen's framework, replication collapses when mutations overwhelm", "target": "selection", "si": 3},
    {"id": "F5h", "prompt": "Is the observable universe large enough for chance formation of an RNA replicase?", "target": "No", "si": 4},
    {"id": "F6h", "prompt": "In his 1948 paper, Shannon chose to exclude", "target": "meaning", "si": 5},
    {"id": "F7h", "prompt": "Lenski's key evolutionary innovation was citrate metabolism under", "target": "aerobic", "si": 6},
]

# -- key-fact keywords per concept (identical to v436/v437/v439/v440, immutable) --
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


def token_jaccard(a, b):
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


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
    print("RETRIEVAL top1-vs-top2 GOLD DISAGREEMENT PROBE v442 -- PURE MEASUREMENT")
    print(f"Model: {MODEL_ID}")
    print(f"Detect layer: L{DETECT_LAYER}   NO gate, NO abstain")
    print(f"G3: gap <= 0 (correct not below wrong) -> top2-disagreement NOT viable (leave answer-similarity family)")
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

    # -- centroid computation: BYTE-IDENTICAL to v437/v438/v439/v440 --
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

    # -- detect_concept_full: BYTE-IDENTICAL to v438/v439/v440 --
    def detect_concept_full(prompt):
        h = get_hidden_at_layer(model, tokenizer, prompt, DETECT_LAYER)
        h_norm = h / (h.norm() + 1e-8)
        sims = []
        for si, c in centroids.items():          # si order 0..6 preserved
            sims.append((si, cosine_sim(h_norm, c).item()))
        # stable sort by sim desc; ties keep ascending-si (matches v437 argmax: first/lowest si on tie)
        sims_sorted = sorted(sims, key=lambda x: -x[1])
        return sims_sorted

    print(f"\n[3] top1-GOLD vs top2-GOLD answer disagreement (no gate)...")
    results = []
    for item in CLOZE_HELD:
        question = cloze_to_question(item["prompt"])

        sims_sorted = detect_concept_full(item["prompt"])
        top1_si = sims_sorted[0][0]
        top2_si = sims_sorted[1][0]
        detected_si = top1_si
        detect_ok = (detected_si == item["si"])

        ans_top1 = generate_answer(model, tokenizer,
                                   build_user_content(question, GOLD_FRAGMENTS[top1_si]))
        ans_top2 = generate_answer(model, tokenizer,
                                   build_user_content(question, GOLD_FRAGMENTS[top2_si]))
        top1_ok = answer_correct(item["si"], ans_top1)
        top2_ok = answer_correct(item["si"], ans_top2)

        # consistency = cosine of L13 last-token hidden of the two GOLD-answer texts (empty -> space guard)
        h1 = get_hidden_at_layer(model, tokenizer, ans_top1 or " ", DETECT_LAYER)
        h2 = get_hidden_at_layer(model, tokenizer, ans_top2 or " ", DETECT_LAYER)
        consistency = cosine_sim(h1, h2).item()
        jaccard = token_jaccard(ans_top1, ans_top2)

        r = {
            "id": item["id"], "true_si": item["si"], "question": question,
            "detected_si": detected_si, "top1_si": top1_si, "top2_si": top2_si,
            "detect_ok": detect_ok,
            "consistency": round(consistency, 4), "jaccard": round(jaccard, 4),
            "top1_ok": top1_ok, "top2_ok": top2_ok,
            "ans_top1": ans_top1, "ans_top2": ans_top2,
        }
        results.append(r)

        d = "Y" if detect_ok else "N"
        print(f"  {item['id']:4s}: detect={d} top1_si={top1_si} top2_si={top2_si} "
              f"cons={consistency:.4f} jac={jaccard:.3f} | "
              f"top1={'OK' if top1_ok else 'no'} top2={'OK' if top2_ok else 'no'}")

    # -- separability of consistency: correct-detects expected BELOW wrong-detects (INVERTED vs v441).
    #    gap = min_wrong - max_correct > 0 means correct sit below wrong (clean). --
    correct = [r for r in results if r["detect_ok"]]
    wrong = [r for r in results if not r["detect_ok"]]
    correct_cons = [r["consistency"] for r in correct]
    wrong_cons = [r["consistency"] for r in wrong]
    max_correct = max(correct_cons) if correct_cons else None
    min_wrong = min(wrong_cons) if wrong_cons else None
    gap = (min_wrong - max_correct) if (min_wrong is not None and max_correct is not None) else None
    sep_clean = (gap is not None and gap > 0)

    # per-fact table sorted by consistency ascending (correct-detects expected at bottom)
    print(f"\n  {'id':4s} {'ok':2s} {'cons':>8s} {'jac':>6s} {'top1':>5s} {'top2':>5s}")
    for r in sorted(results, key=lambda x: x["consistency"]):
        ok = "Y" if r["detect_ok"] else "N"
        print(f"  {r['id']:4s} {ok:2s} {r['consistency']:8.4f} {r['jaccard']:6.3f} "
              f"{'OK' if r['top1_ok'] else 'no':>5s} {'OK' if r['top2_ok'] else 'no':>5s}")

    if sep_clean:
        verdict = "PASS"
        conclusion = (f"Disagreement separates: max correct-detect consistency {max_correct} < "
                      f"min wrong-detect consistency {min_wrong} (gap {gap} > 0). Correct-detects "
                      f"sit BELOW wrong-detects: right concept has a clean winner so top1/top2 GOLD "
                      f"answers DIVERGE, near-tie wrong-detects AGREE. top1-vs-top2 disagreement is a "
                      f"candidate NON-geometric trigger. NEXT: build verify-gate (abstain if consistency "
                      f">= c) AND test transfer on split B before trusting it (v439/v440 lesson: fit != transfer).")
    else:
        verdict = "FAIL"
        conclusion = (f"Disagreement does NOT separate: max correct-detect consistency {max_correct} >= "
                      f"min wrong-detect consistency {min_wrong} (gap {gap} <= 0). Correct-detects do NOT "
                      f"sit below wrong-detects. GOLD-answer agreement (any pairing) does not discriminate "
                      f"right-from-wrong. Leave the answer-similarity family: next link = explicit "
                      f"entailment (does the injected GOLD logically support the produced answer -- NLI/verifier).")

    print(f"\n{'='*72}")
    print(f"G3 VERDICT: {verdict}")
    print(f"  detects:            correct {len(correct)}/7 | wrong {len(wrong)}/7 (expect F3h,F7h wrong)")
    print(f"  max correct cons:   {max_correct}")
    print(f"  min wrong cons:     {min_wrong}")
    print(f"  DISAGREEMENT GAP:   {gap}   (>0 = correct-detects sit below wrong = separable)")
    print(f"  {conclusion}")
    print(f"{'='*72}")

    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v442", "axis": "retrieval-verification-top2-disagreement-probe", "track": "ORGANISM",
        "model": MODEL_ID, "detect_layer": DETECT_LAYER,
        "method": "cosine-to-centroid @L13 detect; per held-out ans under GOLD[top1] + ans under GOLD[top2]; consistency=cosine(L13 hidden(ans_top1), L13 hidden(ans_top2)); PURE MEASUREMENT (no gate/abstain)",
        "held_out": "ORIGINAL CLOZE_HELD F1h..F7h (detect outcomes known)",
        "separability": {
            "max_correct_consistency": max_correct, "min_wrong_consistency": min_wrong,
            "consistency_gap": gap, "clean_separation": sep_clean, "direction": "correct BELOW wrong",
            "n_correct": len(correct), "n_wrong": len(wrong),
        },
        "results": results, "verdict": verdict, "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
