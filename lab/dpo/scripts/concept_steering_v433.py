#!/usr/bin/env python3
"""
concept_steering_v433.py -- Concept direction extraction + activation steering.

Bridges v432 (concepts encoded abstractly in hidden states) to actionable
editing: can injecting a concept direction shift P(target) on cloze prompts?

Method: Mean-difference direction (standard RepE / Zou et al. 2023).
  direction_i = mean(hidden_states of fact_i phrasings) - mean(other facts)
  Normalized to unit length. Injected via forward hook at layer L.

Steering: hook at transformer layer output, add alpha * direction to last-token
hidden state, measure delta P(target_new) on v431 cloze prompts.

G3: delta P(target) > 0.05 on >= 4/7 original cloze at any layer/alpha -> PASS.
     Fails on all configs -> FAIL (concepts encoded but not steerable).

v433 - TRACK 1 ANATOMY - concept-direction-steering
Run: LOCAL RTX 4070 8GB, 4-bit NF4. ~259 forward passes, <3 min, $0.
"""

import torch
import json, os, sys, time
import numpy as np

MODEL_ID = "Qwen/Qwen2.5-Coder-7B"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/concept_steering_v433.json"

PROBE_LAYERS = [7, 13, 27]   # L7 first 6/7 in v432, L13 mid, L27 peak 7/7
ALPHAS = [0.5, 1.0, 2.0, 5.0, 10.0]
PASS_THRESHOLD = 4            # >= 4/7 with delta > 0.05
DELTA_THRESHOLD = 0.05

# -- 7 cloze edits from v431 (original prompts for steering eval) --
EDITS = [
    {"id": "F1", "prompt": "Probability calculations for random self-replicator assembly are commonly considered",
     "target_new": "misleading", "source_idx": 0},
    {"id": "F2", "prompt": "The fraction of random amino-acid sequences with simple biological function is roughly one in ten to the",
     "target_new": "eleven", "source_idx": 1},
    {"id": "F3", "prompt": "About a third of the genes in JCVI-syn3.0 have functions that are",
     "target_new": "unknown", "source_idx": 2},
    {"id": "F4", "prompt": "Eigen's error catastrophe describes when copying errors outpace natural",
     "target_new": "selection", "source_idx": 3},
    {"id": "F5", "prompt": "According to Totani (2020), the observable universe is sufficient for random RNA replicator assembly:",
     "target_new": "No", "source_idx": 4},
    {"id": "F6", "prompt": "Shannon's information theory deliberately excludes the concept of",
     "target_new": "meaning", "source_idx": 5},
    {"id": "F7", "prompt": "The Cit+ phenotype enabled E. coli to metabolize citrate under",
     "target_new": "aerobic", "source_idx": 6},
]

# -- held-out rephrased cloze (generalization check) --
HELDOUT = [
    {"edit_id": "F1", "prompt": "The standard argument against abiogenesis via random protein assembly is widely regarded as",
     "target_new": "misleading", "source_idx": 0},
    {"edit_id": "F2", "prompt": "Among random polypeptides, the chance of any biological activity is about one in ten to the",
     "target_new": "eleven", "source_idx": 1},
    {"edit_id": "F3", "prompt": "Many genes in the synthetic minimal cell have purposes that remain",
     "target_new": "unknown", "source_idx": 2},
    {"edit_id": "F4", "prompt": "In Eigen's framework, replication collapses when mutations overwhelm",
     "target_new": "selection", "source_idx": 3},
    {"edit_id": "F5", "prompt": "Is the observable universe large enough for chance formation of an RNA replicase?",
     "target_new": "No", "source_idx": 4},
    {"edit_id": "F6", "prompt": "In his 1948 paper, Shannon chose to exclude",
     "target_new": "meaning", "source_idx": 5},
    {"edit_id": "F7", "prompt": "Lenski's key evolutionary innovation was citrate metabolism under",
     "target_new": "aerobic", "source_idx": 6},
]


def tok_id(tokenizer, word):
    """First meaningful token id (handles leading-space tokens in Qwen-Coder)."""
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    if len(ids) > 1:
        first_decoded = tokenizer.decode([ids[0]]).strip()
        if first_decoded == "":
            return ids[1]
    return ids[0]


def get_device(model):
    return next(model.parameters()).device


def collect_hidden_states(model, tokenizer, prompt, layers):
    """Forward pass -> last-token hidden states at specified layers."""
    dev = get_device(model)
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    with torch.no_grad():
        out = model(ids, use_cache=False, output_hidden_states=True)
    # hidden_states[0]=embedding, [1..N]=transformer layers
    states = {}
    for l in layers:
        h = out.hidden_states[l + 1][0, -1, :].float().cpu()
        states[l] = h
    return states


def make_steering_hook(direction, alpha):
    """Hook that adds alpha * direction to last-token hidden state."""
    def hook_fn(module, input, output):
        if isinstance(output, tuple):
            h = output[0]
            h[:, -1, :] += alpha * direction.to(h.device).to(h.dtype)
            return (h,) + output[1:]
        else:
            output[:, -1, :] += alpha * direction.to(output.device).to(output.dtype)
            return output
    return hook_fn


def measure_p(model, tokenizer, prompt, target_word, hook_layer=None, hook_fn=None):
    """Measure P(target_word) at last position, optionally with steering hook."""
    dev = get_device(model)
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    tid = tok_id(tokenizer, target_word)

    handle = None
    if hook_layer is not None and hook_fn is not None:
        handle = model.model.layers[hook_layer].register_forward_hook(hook_fn)

    with torch.no_grad():
        out = model(ids, use_cache=False)

    if handle:
        handle.remove()

    logits = out.logits[0, -1, :]
    probs = torch.softmax(logits.float(), dim=-1)
    return probs[tid].item()


def main():
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available"); sys.exit(1)

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # load training data
    lines = [json.loads(l) for l in open(DATA_PATH)]
    train_prompts, train_labels = [], []
    for si in range(7):
        group = [l for l in lines if l["source_idx"] == si][:5]
        for g in group:
            train_prompts.append(g["prompt"])
            train_labels.append(si)

    print("=" * 70)
    print("CONCEPT STEERING v433")
    print(f"Model: {MODEL_ID}")
    print(f"Direction source: {len(train_prompts)} prompts (mean-diff RepE)")
    print(f"Probe layers: {PROBE_LAYERS}")
    print(f"Alphas: {ALPHAS}")
    print(f"G3: delta P > {DELTA_THRESHOLD} on >= {PASS_THRESHOLD}/7 at any config")
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

    # collect hidden states for direction extraction
    print("\n[2] Collecting hidden states...")
    t0 = time.time()
    train_states = {l: [] for l in PROBE_LAYERS}
    for i, prompt in enumerate(train_prompts):
        states = collect_hidden_states(model, tokenizer, prompt, PROBE_LAYERS)
        for l in PROBE_LAYERS:
            train_states[l].append(states[l])
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(train_prompts)}")
    print(f"  Done: {time.time()-t0:.1f}s")

    # extract mean-difference directions
    print("\n[3] Extracting concept directions...")
    directions = {}
    labels = np.array(train_labels)

    for l in PROBE_LAYERS:
        X = torch.stack(train_states[l])
        for fi in range(7):
            pos = X[labels == fi]       # (5, hidden)
            neg = X[labels != fi]       # (30, hidden)
            d = pos.mean(0) - neg.mean(0)
            d = d / d.norm()
            directions[(l, fi)] = d
        print(f"  L{l}: 7 directions extracted, norm=1.0")

    # measure baselines (no hook)
    print("\n[4] Baselines...")
    base_edit = {}
    for e in EDITS:
        p = measure_p(model, tokenizer, e["prompt"], e["target_new"])
        base_edit[e["id"]] = p
        print(f"  {e['id']}: P({e['target_new']}) = {p:.4f}")

    base_held = {}
    for h in HELDOUT:
        p = measure_p(model, tokenizer, h["prompt"], h["target_new"])
        base_held[h["edit_id"]] = p
        print(f"  {h['edit_id']}(held): P({h['target_new']}) = {p:.4f}")

    # steering sweep
    print("\n[5] Steering sweep...")
    all_results = []
    best = {"n_pass": 0}

    for l in PROBE_LAYERS:
        for alpha in ALPHAS:
            edit_details, n_ep = [], 0
            for e in EDITS:
                d = directions[(l, e["source_idx"])]
                hook = make_steering_hook(d, alpha)
                ps = measure_p(model, tokenizer, e["prompt"], e["target_new"],
                               hook_layer=l, hook_fn=hook)
                pb = base_edit[e["id"]]
                delta = ps - pb
                ok = delta > DELTA_THRESHOLD
                if ok: n_ep += 1
                edit_details.append({"id": e["id"], "p_base": round(pb,4),
                    "p_steered": round(ps,4), "delta": round(delta,4), "pass": ok})

            held_details, n_hp = [], 0
            for h in HELDOUT:
                d = directions[(l, h["source_idx"])]
                hook = make_steering_hook(d, alpha)
                ps = measure_p(model, tokenizer, h["prompt"], h["target_new"],
                               hook_layer=l, hook_fn=hook)
                pb = base_held[h["edit_id"]]
                delta = ps - pb
                ok = delta > DELTA_THRESHOLD
                if ok: n_hp += 1
                held_details.append({"id": h["edit_id"], "p_base": round(pb,4),
                    "p_steered": round(ps,4), "delta": round(delta,4), "pass": ok})

            tag = " ***" if n_ep >= PASS_THRESHOLD else ""
            print(f"  L{l:2d} a={alpha:5.1f}: edit {n_ep}/7, held {n_hp}/7{tag}")

            rec = {"layer": l, "alpha": alpha, "edit_pass": n_ep,
                   "edit_details": edit_details, "held_pass": n_hp,
                   "held_details": held_details}
            all_results.append(rec)
            if n_ep > best["n_pass"]:
                best = {"n_pass": n_ep, "layer": l, "alpha": alpha, "rec": rec}

    # verdict
    mp = best["n_pass"]
    if mp >= PASS_THRESHOLD:
        verdict = "PASS"
        conclusion = (f"Steering WORKS at L{best['layer']} alpha={best['alpha']} "
                      f"({mp}/7). Representation engineering viable as editing method.")
    else:
        verdict = "FAIL"
        conclusion = (f"Steering failed (max {mp}/7, need {PASS_THRESHOLD}/7). "
                      f"Concepts encoded but not steerable via linear direction.")

    print(f"\n{'='*70}")
    print(f"G3 VERDICT: {verdict}")
    if "layer" in best:
        print(f"  Best: L{best['layer']} alpha={best['alpha']}")
        print(f"  Edit: {mp}/7")
        if "rec" in best:
            for d in best["rec"]["edit_details"]:
                m = "Y" if d["pass"] else "N"
                print(f"    {m} {d['id']}: {d['p_base']:.4f} -> {d['p_steered']:.4f} (d={d['delta']:+.4f})")
            print(f"  Held: {best['rec']['held_pass']}/7")
            for d in best["rec"]["held_details"]:
                m = "Y" if d["pass"] else "N"
                print(f"    {m} {d['id']}: {d['p_base']:.4f} -> {d['p_steered']:.4f} (d={d['delta']:+.4f})")
    print(f"  {conclusion}")
    print(f"{'='*70}")

    # save
    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v433",
        "axis": "concept-direction-steering",
        "model": MODEL_ID,
        "probe_layers": PROBE_LAYERS,
        "alphas": ALPHAS,
        "method": "mean-difference direction (RepE), unit-normalized, last-token hook",
        "baselines_edit": {k: round(v,4) for k,v in base_edit.items()},
        "baselines_held": {k: round(v,4) for k,v in base_held.items()},
        "results": all_results,
        "best_layer": best.get("layer"),
        "best_alpha": best.get("alpha"),
        "best_edit_pass": mp,
        "best_details": best.get("rec"),
        "verdict": verdict,
        "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
