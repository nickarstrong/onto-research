#!/usr/bin/env python3
"""
concept_retrieval_v434.py -- Concept-triggered GOLD retrieval (organism-v2).

v432 proved substrate encodes concepts (readable). v433 proved can't write
via steering. Organism solution: DON'T write to weights, READ internal
representations and retrieve relevant GOLD at runtime.

Pipeline per query:
  1. Forward pass -> hidden state at L13 (stable concept encoding per v432)
  2. Cosine similarity to 7 concept centroids (from training data)
  3. If best match > threshold -> prepend matched GOLD fragment
  4. Measure P(target) with GOLD prefix vs baseline (no prefix)

G3: concept detection correct on >=4/7 held-out cloze AND
    GOLD-augmented P(target) > baseline+0.05 on >=4/7 facts where baseline<0.5
    -> concept-triggered retrieval WORKS -> organism-v2 viable.

v434 - TRACK 2 ORGANISM - concept-triggered-retrieval
Run: LOCAL RTX 4070 8GB, 4-bit NF4. ~100 forward passes, <3 min, $0.
"""

import torch
import json, os, sys, time
import numpy as np

MODEL_ID = "Qwen/Qwen2.5-Coder-7B"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/concept_retrieval_v434.json"
DETECT_LAYER = 13  # stable 6/7 in v432, mid-range
PASS_DETECT = 4    # >=4/7 held-out detection correct
PASS_RETRIEVAL = 4 # >=4/7 P(target) boosted where baseline < 0.5
DELTA_THRESHOLD = 0.05

# -- GOLD fragments (compact factual answers per concept) --
GOLD_FRAGMENTS = {
    0: "Probability calculations against random self-replicator assembly are misleading because they assume modern protein complexity rather than simpler precursor molecules that could have initiated life.",
    1: "The fraction of random amino-acid sequences with simple biological function is roughly one in ten to the eleven, or approximately 10^-11, based on empirical studies of random polypeptide libraries.",
    2: "About a third of the 473 genes in JCVI-syn3.0, the minimal synthetic cell, have functions that remain unknown despite being essential for life.",
    3: "Eigen's error catastrophe describes the threshold where copying errors in prebiotic replication outpace natural selection, limiting the complexity of early replicators without enzymatic error correction.",
    4: "According to Totani (2020), the observable universe is not sufficient for random nucleotide assembly to produce a functional RNA replicase by chance alone.",
    5: "Shannon's information theory deliberately excludes the concept of meaning, measuring only statistical uncertainty of message transmission regardless of semantic content.",
    6: "The Cit+ phenotype in Lenski's long-term evolution experiment enabled E. coli to metabolize citrate under aerobic conditions, emerging after approximately 31,500 generations.",
}

# -- 7 original cloze prompts (from v431) --
CLOZE_ORIG = [
    {"id": "F1", "prompt": "Probability calculations for random self-replicator assembly are commonly considered", "target": "misleading", "si": 0},
    {"id": "F2", "prompt": "The fraction of random amino-acid sequences with simple biological function is roughly one in ten to the", "target": "eleven", "si": 1},
    {"id": "F3", "prompt": "About a third of the genes in JCVI-syn3.0 have functions that are", "target": "unknown", "si": 2},
    {"id": "F4", "prompt": "Eigen's error catastrophe describes when copying errors outpace natural", "target": "selection", "si": 3},
    {"id": "F5", "prompt": "According to Totani (2020), the observable universe is sufficient for random RNA replicator assembly:", "target": "No", "si": 4},
    {"id": "F6", "prompt": "Shannon's information theory deliberately excludes the concept of", "target": "meaning", "si": 5},
    {"id": "F7", "prompt": "The Cit+ phenotype enabled E. coli to metabolize citrate under", "target": "aerobic", "si": 6},
]

# -- 7 held-out cloze prompts (from v431, rephrased) --
CLOZE_HELD = [
    {"id": "F1h", "prompt": "The standard argument against abiogenesis via random protein assembly is widely regarded as", "target": "misleading", "si": 0},
    {"id": "F2h", "prompt": "Among random polypeptides, the chance of any biological activity is about one in ten to the", "target": "eleven", "si": 1},
    {"id": "F3h", "prompt": "Many genes in the synthetic minimal cell have purposes that remain", "target": "unknown", "si": 2},
    {"id": "F4h", "prompt": "In Eigen's framework, replication collapses when mutations overwhelm", "target": "selection", "si": 3},
    {"id": "F5h", "prompt": "Is the observable universe large enough for chance formation of an RNA replicase?", "target": "No", "si": 4},
    {"id": "F6h", "prompt": "In his 1948 paper, Shannon chose to exclude", "target": "meaning", "si": 5},
    {"id": "F7h", "prompt": "Lenski's key evolutionary innovation was citrate metabolism under", "target": "aerobic", "si": 6},
]


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


def measure_p(model, tokenizer, prompt, target_word):
    dev = next(model.parameters()).device
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    tid = tok_id(tokenizer, target_word)
    with torch.no_grad():
        out = model(ids, use_cache=False)
    probs = torch.softmax(out.logits[0, -1, :].float(), dim=-1)
    return probs[tid].item()


def cosine_sim(a, b):
    return torch.dot(a, b) / (a.norm() * b.norm() + 1e-8)


def main():
    assert torch.cuda.is_available(), "CUDA required"
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    # load training data for centroid computation
    lines = [json.loads(l) for l in open(DATA_PATH)]
    train_prompts, train_labels = [], []
    for si in range(7):
        group = [l for l in lines if l["source_idx"] == si][:5]
        for g in group:
            train_prompts.append(g["prompt"])
            train_labels.append(si)

    print("=" * 70)
    print("CONCEPT-TRIGGERED RETRIEVAL v434 (organism-v2)")
    print(f"Model: {MODEL_ID}")
    print(f"Detect layer: L{DETECT_LAYER}")
    print(f"G3: detect >=4/7 held-out AND boost >=4/7 where baseline<0.5")
    print("=" * 70)

    # load model
    print("\n[1] Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True,
    )
    model.eval()
    print(f"  {model.config.num_hidden_layers} layers, hidden={model.config.hidden_size}")

    # compute concept centroids from training data
    print(f"\n[2] Computing concept centroids at L{DETECT_LAYER}...")
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
        c = c / c.norm()  # unit normalize
        centroids[si] = c
    print(f"  7 centroids computed ({time.time()-t0:.1f}s)")

    # concept detection + retrieval test
    print(f"\n[3] Concept detection + retrieval...")

    def detect_concept(prompt):
        """Return (detected_si, best_sim) using centroid matching."""
        h = get_hidden_at_layer(model, tokenizer, prompt, DETECT_LAYER)
        h_norm = h / (h.norm() + 1e-8)
        best_si, best_sim = -1, -1.0
        for si, c in centroids.items():
            sim = cosine_sim(h_norm, c).item()
            if sim > best_sim:
                best_sim = sim
                best_si = si
        return best_si, best_sim

    def test_set(name, cloze_list):
        """Test detection + retrieval on a cloze set."""
        results = []
        n_detect_ok = 0
        n_boost_ok = 0
        n_eligible = 0  # facts where baseline < 0.5

        for item in cloze_list:
            # detect concept
            detected_si, det_sim = detect_concept(item["prompt"])
            detect_ok = (detected_si == item["si"])
            if detect_ok:
                n_detect_ok += 1

            # baseline P(target) - no retrieval
            p_base = measure_p(model, tokenizer, item["prompt"], item["target"])

            # GOLD-augmented P(target) - prepend correct GOLD (oracle)
            gold_prefix = GOLD_FRAGMENTS[item["si"]]
            aug_prompt = f"{gold_prefix}\n\n{item['prompt']}"
            p_oracle = measure_p(model, tokenizer, aug_prompt, item["target"])

            # concept-detected retrieval P(target) - prepend DETECTED GOLD
            det_gold = GOLD_FRAGMENTS[detected_si]
            det_prompt = f"{det_gold}\n\n{item['prompt']}"
            p_detected = measure_p(model, tokenizer, det_prompt, item["target"])

            # wrong GOLD control - prepend unrelated GOLD
            wrong_si = (item["si"] + 3) % 7  # pick a different fact
            wrong_gold = GOLD_FRAGMENTS[wrong_si]
            wrong_prompt = f"{wrong_gold}\n\n{item['prompt']}"
            p_wrong = measure_p(model, tokenizer, wrong_prompt, item["target"])

            # boost check (only for facts where baseline < 0.5)
            eligible = p_base < 0.5
            if eligible:
                n_eligible += 1
                if p_detected - p_base > DELTA_THRESHOLD:
                    n_boost_ok += 1

            r = {
                "id": item["id"],
                "true_si": item["si"],
                "detected_si": detected_si,
                "detect_ok": detect_ok,
                "det_sim": round(det_sim, 4),
                "p_base": round(p_base, 4),
                "p_oracle": round(p_oracle, 4),
                "p_detected": round(p_detected, 4),
                "p_wrong": round(p_wrong, 4),
                "delta_detected": round(p_detected - p_base, 4),
                "eligible": eligible,
            }
            results.append(r)

            d_mark = "Y" if detect_ok else "N"
            b_mark = "+" if eligible and (p_detected - p_base > DELTA_THRESHOLD) else (" " if not eligible else "-")
            print(f"  {item['id']:4s}: detect={d_mark} sim={det_sim:.3f} | "
                  f"base={p_base:.4f} oracle={p_oracle:.4f} "
                  f"detected={p_detected:.4f} wrong={p_wrong:.4f} [{b_mark}]")

        print(f"  {name}: detect {n_detect_ok}/{len(cloze_list)}, "
              f"boost {n_boost_ok}/{n_eligible} eligible")
        return results, n_detect_ok, n_boost_ok, n_eligible

    print("\n  --- Original cloze (v431 EDITS) ---")
    orig_results, orig_det, orig_boost, orig_elig = test_set("ORIG", CLOZE_ORIG)

    print("\n  --- Held-out cloze (v431 HELDOUT) ---")
    held_results, held_det, held_boost, held_elig = test_set("HELD", CLOZE_HELD)

    # verdict
    detect_pass = held_det >= PASS_DETECT
    boost_pass = (orig_boost + held_boost) >= PASS_RETRIEVAL

    if detect_pass and boost_pass:
        verdict = "PASS"
        conclusion = (f"Concept-triggered retrieval WORKS: detect {held_det}/7 held-out, "
                      f"boost {orig_boost+held_boost}/{orig_elig+held_elig} eligible. "
                      f"Organism-v2 viable: substrate signals which GOLD to retrieve.")
    elif detect_pass:
        verdict = "PARTIAL"
        conclusion = (f"Detection works ({held_det}/7) but P(target) boost insufficient "
                      f"({orig_boost+held_boost}/{orig_elig+held_elig}). "
                      f"Retrieval pipeline needs tuning, not concept detection.")
    else:
        verdict = "FAIL"
        conclusion = (f"Detection failed ({held_det}/7 held-out, need {PASS_DETECT}). "
                      f"Centroid matching at L{DETECT_LAYER} insufficient for retrieval trigger.")

    print(f"\n{'='*70}")
    print(f"G3 VERDICT: {verdict}")
    print(f"  Detection: orig {orig_det}/7, held {held_det}/7")
    print(f"  Boost: {orig_boost+held_boost}/{orig_elig+held_elig} eligible (delta>{DELTA_THRESHOLD})")
    print(f"  {conclusion}")
    print(f"{'='*70}")

    # save
    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v434",
        "axis": "concept-triggered-retrieval",
        "track": "ORGANISM",
        "model": MODEL_ID,
        "detect_layer": DETECT_LAYER,
        "method": "cosine-to-centroid at L13, prepend GOLD fragment",
        "gold_fragments": GOLD_FRAGMENTS,
        "orig_results": orig_results,
        "held_results": held_results,
        "orig_detect": orig_det,
        "held_detect": held_det,
        "total_boost": orig_boost + held_boost,
        "total_eligible": orig_elig + held_elig,
        "verdict": verdict,
        "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
