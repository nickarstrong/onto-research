#!/usr/bin/env python3
"""
verify_probe_v441.py -- RETRIEVAL-VERIFICATION probe (baseline-vs-GOLD answer consistency).

PURE MEASUREMENT. No gate, no abstain. G1 ground-opening for the NON-geometric trigger
axis BEFORE any verify-gate is built (mirror v438's discipline; do NOT repeat v437's
build-then-discover order).

WHY THIS AXIS: both GEOMETRIC triggers failed transfer --
  v437 max-cosine: separability gap -0.0066 on the 7 (did not discriminate right/wrong).
  v439 margin: dominated the OLD 7 (gap +0.0104) but v440 froze m=0.025 and it did NOT
    transfer to disjoint split B (gap -0.0131, separation INVERTED). m was fit to old 7.
  -> GEOMETRIC-TRIGGER LINE CLOSED (v440 close, DIRECTION_VECTOR).
Pivot (pre-registered v440): NON-geometric trigger = retrieval-verification. Do not ask
"is the detection geometrically clean" (geometry doesn't transfer); ask "does injecting
the retrieved GOLD produce an answer CONSISTENT with the no-context answer, or does an
off-concept GOLD perturb it". Second signal (this probe, minimal) = baseline (no-GOLD)
answer. (top2-GOLD as a richer second signal is a LATER link if this one separates.)

HYPOTHESIS (directional, falsifiable): a WRONG detect injects off-concept GOLD -> larger
perturbation of the answer -> LOWER base-vs-GOLD consistency than a CORRECT detect.
  Expect: min(correct-detect consistency) > max(wrong-detect consistency)  (gap > 0).

METRIC: consistency = cosine( L13 last-token hidden(ans_base), L13 last-token hidden(ans_gold) ).
  Reuses get_hidden_at_layer + cosine_sim (no new deps). Secondary (recorded, not gating):
  token-Jaccard overlap of the two answers. Also record base_ok/gold_ok to expose the
  boost-conflation risk (a CORRECT detect where base was wrong -> gold corrects it also
  diverges; if those land low, baseline-consistency conflates useful-correction with
  corruption -> the probe will SHOW it as gap<=0).

Held-out: ORIGINAL CLOZE_HELD (F1h..F7h), where detect outcomes are KNOWN (detect 5/7;
F3h, F7h are the two wrong-detects). Directly asks: does consistency flag F3h/F7h low?

Inherited from v440/v439/v437 BYTE-FOR-BYTE (evolution = change representation, not logic):
  MODEL_ID, DATA_PATH, DETECT_LAYER, GOLD_FRAGMENTS, KEY, KEY_NEG_SI4, tok_id,
  get_hidden_at_layer, cosine_sim, build_user_content, generate_answer, cloze_to_question,
  answer_correct, the L13 centroid block, detect_concept_full.
New (this axis, honestly new -- not a gate representation swap):
  - measurement loop: per held-out, ans_base + ans_gold + consistency (no gate, no abstain).
  - separability of consistency: min correct vs max wrong; gap.

G3 FALSIFIER (pre-registered, immutable):
  consistency separability gap <= 0 (min correct-detect consistency <= max wrong-detect
  consistency -- the two known wrong-detects F3h/F7h do NOT sit below the correct-detects)
  -> baseline-vs-GOLD consistency is ALSO not a viable trigger (the no-context answer is
     too weak a second signal / boost-conflation dominates)
  -> next link needs a RICHER second signal (top2-GOLD disagreement, or explicit
     entailment of the answer by the injected GOLD), NOT a verify-gate on this signal.

v441 - TRACK 2 ORGANISM - retrieval-verification: baseline-vs-GOLD consistency probe.
Run: LOCAL RTX 4070 8GB, 4-bit NF4. 35 centroid + 7 detect + 14 gen(100tok) + 14 hidden. <2min, $0.
"""

import torch
import json, os, time

MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/verify_probe_v441.json"
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
    print("RETRIEVAL-VERIFICATION PROBE v441 (baseline-vs-GOLD consistency) -- PURE MEASUREMENT")
    print(f"Model: {MODEL_ID}")
    print(f"Detect layer: L{DETECT_LAYER}   NO gate, NO abstain")
    print(f"G3: consistency gap <= 0 -> baseline-vs-GOLD NOT a viable trigger (need richer 2nd signal)")
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

    print(f"\n[3] Baseline vs GOLD answer consistency (no gate)...")
    results = []
    for item in CLOZE_HELD:
        question = cloze_to_question(item["prompt"])

        sims_sorted = detect_concept_full(item["prompt"])
        detected_si = sims_sorted[0][0]
        detect_ok = (detected_si == item["si"])

        ans_base = generate_answer(model, tokenizer, build_user_content(question, None))
        ans_gold = generate_answer(model, tokenizer,
                                   build_user_content(question, GOLD_FRAGMENTS[detected_si]))
        base_ok = answer_correct(item["si"], ans_base)
        gold_ok = answer_correct(item["si"], ans_gold)

        # consistency = cosine of L13 last-token hidden of the two ANSWER texts (empty -> space guard)
        h_base = get_hidden_at_layer(model, tokenizer, ans_base or " ", DETECT_LAYER)
        h_gold = get_hidden_at_layer(model, tokenizer, ans_gold or " ", DETECT_LAYER)
        consistency = cosine_sim(h_base, h_gold).item()
        jaccard = token_jaccard(ans_base, ans_gold)

        r = {
            "id": item["id"], "true_si": item["si"], "question": question,
            "detected_si": detected_si, "detect_ok": detect_ok,
            "consistency": round(consistency, 4), "jaccard": round(jaccard, 4),
            "base_ok": base_ok, "gold_ok": gold_ok,
            "ans_base": ans_base, "ans_gold": ans_gold,
        }
        results.append(r)

        d = "Y" if detect_ok else "N"
        print(f"  {item['id']:4s}: detect={d} cons={consistency:.4f} jac={jaccard:.3f} | "
              f"base={'OK' if base_ok else 'no'} gold={'OK' if gold_ok else 'no'}")

    # -- separability of consistency (correct-detect should be HIGH, wrong-detect LOW) --
    correct = [r for r in results if r["detect_ok"]]
    wrong = [r for r in results if not r["detect_ok"]]
    correct_cons = [r["consistency"] for r in correct]
    wrong_cons = [r["consistency"] for r in wrong]
    min_correct = min(correct_cons) if correct_cons else None
    max_wrong = max(wrong_cons) if wrong_cons else None
    gap = (min_correct - max_wrong) if (min_correct is not None and max_wrong is not None) else None
    sep_clean = (gap is not None and gap > 0)

    # per-fact table sorted by consistency ascending (wrong-detects expected at bottom)
    print(f"\n  {'id':4s} {'ok':2s} {'cons':>8s} {'jac':>6s} {'base':>5s} {'gold':>5s}")
    for r in sorted(results, key=lambda x: x["consistency"]):
        ok = "Y" if r["detect_ok"] else "N"
        print(f"  {r['id']:4s} {ok:2s} {r['consistency']:8.4f} {r['jaccard']:6.3f} "
              f"{'OK' if r['base_ok'] else 'no':>5s} {'OK' if r['gold_ok'] else 'no':>5s}")

    if sep_clean:
        verdict = "PASS"
        conclusion = (f"Consistency separates: min correct-detect consistency {min_correct} > "
                      f"max wrong-detect consistency {max_wrong} (gap {gap} > 0). Baseline-vs-GOLD "
                      f"consistency is a candidate NON-geometric trigger (wrong-detect off-concept GOLD "
                      f"perturbs the answer more). NEXT: build verify-gate (abstain if consistency < c) "
                      f"AND test transfer on split B before trusting it (v439/v440 lesson: fit != transfer).")
    else:
        verdict = "FAIL"
        conclusion = (f"Consistency does NOT separate: min correct-detect consistency {min_correct} <= "
                      f"max wrong-detect consistency {max_wrong} (gap {gap} <= 0). Baseline (no-context) "
                      f"answer is too weak a second signal / boost-conflation dominates. Do NOT build a "
                      f"verify-gate on this signal. Next link: richer second signal -- top2-GOLD "
                      f"disagreement or explicit entailment of the answer by the injected GOLD.")

    print(f"\n{'='*72}")
    print(f"G3 VERDICT: {verdict}")
    print(f"  detects:            correct {len(correct)}/7 | wrong {len(wrong)}/7 (expect F3h,F7h wrong)")
    print(f"  min correct cons:   {min_correct}")
    print(f"  max wrong cons:     {max_wrong}")
    print(f"  CONSISTENCY GAP:    {gap}   (>0 = wrong-detects sit below correct = separable)")
    print(f"  {conclusion}")
    print(f"{'='*72}")

    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v441", "axis": "retrieval-verification-consistency-probe", "track": "ORGANISM",
        "model": MODEL_ID, "detect_layer": DETECT_LAYER,
        "method": "cosine-to-centroid @L13 detect; per held-out ans_base(no-GOLD) + ans_gold(detected-GOLD); consistency=cosine(L13 hidden(ans_base), L13 hidden(ans_gold)); PURE MEASUREMENT (no gate/abstain)",
        "held_out": "ORIGINAL CLOZE_HELD F1h..F7h (detect outcomes known)",
        "separability": {
            "min_correct_consistency": min_correct, "max_wrong_consistency": max_wrong,
            "consistency_gap": gap, "clean_separation": sep_clean,
            "n_correct": len(correct), "n_wrong": len(wrong),
        },
        "results": results, "verdict": verdict, "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
