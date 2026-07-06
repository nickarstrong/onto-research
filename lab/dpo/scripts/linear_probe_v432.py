#!/usr/bin/env python3
"""
linear_probe_v432.py - Concept-level representation probe on Qwen2.5-Coder-7B.

Tests whether hidden states encode abiogenesis facts abstractly across surface forms.
7-class logistic regression per layer on last-token hidden states.

Training: 5 phrasings x 7 facts = 35 prompts (from sft_data_aug_v425.jsonl).
Held-out: 1 fresh 6th phrasing per fact = 7 test prompts (generated fresh).
Controls: 7 general-knowledge prompts (verify probe is concept-specific, not topic-generic).

G3 gate:
  PASS: >=5/7 held-out correct at ANY layer (>70%) → concept-level encoding EXISTS.
  FAIL: <=3/7 held-out at ALL layers (<50%) → no abstract concept encoding.
  INCONCLUSIVE: 4/7 max → between thresholds.

v432 · TRACK 1 ANATOMY · linear-probe concept-level
Run: LOCAL RTX 4070 8GB, 4-bit NF4. ~49 forward passes, <5 min, $0.
"""

import torch
import json, os, sys, time
import numpy as np

MODEL_ID = "Qwen/Qwen2.5-Coder-7B"
DATA_PATH = "data/sft_data_aug_v425.jsonl"
OUTPUT_PATH = "eval/linear_probe_v432.json"
PASS_THRESHOLD = 5   # >=5/7 held-out correct at any layer
FAIL_THRESHOLD = 3   # <=3/7 at ALL layers = FAIL

# ── held-out: 6th phrasing per fact (fresh, not in training data) ──
HELDOUT = [
    {"source_idx": 0, "prompt": "What makes probability arguments against the spontaneous origin of life fundamentally flawed?"},
    {"source_idx": 1, "prompt": "Out of all possible polypeptide sequences, how many show any enzymatic activity?"},
    {"source_idx": 2, "prompt": "What fraction of genes in the smallest artificial genome have no known function?"},
    {"source_idx": 3, "prompt": "What theoretical limit constrains the fidelity of prebiotic molecular copying?"},
    {"source_idx": 4, "prompt": "Is our observable cosmos large enough for random nucleotide assembly to generate a working replicase?"},
    {"source_idx": 5, "prompt": "What aspect of communication was intentionally left out of the mathematical theory of information?"},
    {"source_idx": 6, "prompt": "Under what atmospheric conditions did Lenski's bacteria gain the novel ability to metabolize citrate?"},
]

# ── controls: general knowledge, non-biology (7 to match 7 facts) ──
CONTROLS = [
    "What programming language was created by Guido van Rossum in the early 1990s?",
    "What is the tallest mountain in the world measured from sea level?",
    "In what year did the Berlin Wall fall?",
    "What is the chemical formula for table salt?",
    "Who wrote the play Romeo and Juliet?",
    "What is the speed of light in a vacuum measured in meters per second?",
    "What planet is known as the Red Planet?",
]


def get_device(model):
    return next(model.parameters()).device


def collect_hidden_states(model, tokenizer, prompt):
    """Forward pass → last-token hidden state at each transformer layer.
    Returns list of n_layers numpy arrays, each (hidden_size,).
    """
    dev = get_device(model)
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    with torch.no_grad():
        out = model(ids, use_cache=False, output_hidden_states=True)
    # hidden_states: tuple of (batch, seq, hidden) - [0]=embedding, [1..n]=layers
    n_layers = len(out.hidden_states) - 1  # skip embedding
    states = []
    for li in range(1, len(out.hidden_states)):
        h = out.hidden_states[li][0, -1, :].float().cpu().numpy()
        states.append(h)
    return states


def main():
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available"); sys.exit(1)

    torch.cuda.init()
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # ── load training data ──
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: {DATA_PATH} not found"); sys.exit(1)
    lines = [json.loads(l) for l in open(DATA_PATH)]
    train_prompts = []
    train_labels = []
    for si in range(7):
        group = [l for l in lines if l["source_idx"] == si][:5]  # first 5 only
        if len(group) < 5:
            print(f"WARNING: source_idx={si} has only {len(group)} phrasings (need 5)")
        for g in group:
            train_prompts.append(g["prompt"])
            train_labels.append(si)

    print("=" * 70)
    print("LINEAR PROBE v432 - concept-level representation test")
    print(f"Model: {MODEL_ID}")
    print(f"Train: {len(train_prompts)} prompts, 7 classes (5 phrasings x 7 facts)")
    print(f"Held-out: {len(HELDOUT)} prompts (1 fresh per fact)")
    print(f"Controls: {len(CONTROLS)} prompts (general knowledge)")
    print(f"G3: PASS >= {PASS_THRESHOLD}/7, FAIL <= {FAIL_THRESHOLD}/7 at ALL layers")
    print("=" * 70)

    # ── load model (4-bit NF4) ──
    print("\n[1] Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True,
    )
    model.eval()
    n_layers = model.config.num_hidden_layers
    hidden_size = model.config.hidden_size
    print(f"  {sum(p.numel() for p in model.parameters())/1e9:.1f}B params")
    print(f"  {n_layers} layers, hidden_size={hidden_size}")

    # ── collect hidden states ──
    print("\n[2] Collecting hidden states...")
    t0 = time.time()

    # training set
    train_states = {l: [] for l in range(n_layers)}
    for i, prompt in enumerate(train_prompts):
        states = collect_hidden_states(model, tokenizer, prompt)
        for l in range(n_layers):
            train_states[l].append(states[l])
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  train: {i+1}/{len(train_prompts)}")
    print(f"  train: {len(train_prompts)}/{len(train_prompts)} done")

    # held-out
    heldout_states = {l: [] for l in range(n_layers)}
    heldout_labels = []
    for h in HELDOUT:
        states = collect_hidden_states(model, tokenizer, h["prompt"])
        for l in range(n_layers):
            heldout_states[l].append(states[l])
        heldout_labels.append(h["source_idx"])
    print(f"  held-out: {len(HELDOUT)}/{len(HELDOUT)} done")

    # controls
    control_states = {l: [] for l in range(n_layers)}
    for c in CONTROLS:
        states = collect_hidden_states(model, tokenizer, c)
        for l in range(n_layers):
            control_states[l].append(states[l])
    print(f"  controls: {len(CONTROLS)}/{len(CONTROLS)} done")

    t_collect = time.time() - t0
    print(f"  Total collection: {t_collect:.1f}s ({t_collect/49:.1f}s/prompt)")

    # free model VRAM
    del model
    torch.cuda.empty_cache()

    # ── train probes ──
    print(f"\n[3] Training logistic regression probes ({n_layers} layers)...")
    train_labels_arr = np.array(train_labels)
    heldout_labels_arr = np.array(heldout_labels)

    per_layer = []
    for l in range(n_layers):
        X_train = np.stack(train_states[l])
        X_held = np.stack(heldout_states[l])
        X_ctrl = np.stack(control_states[l])

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_held_s = scaler.transform(X_held)
        X_ctrl_s = scaler.transform(X_ctrl)

        # logistic regression: moderate regularization (C=1.0), multinomial
        clf = LogisticRegression(
            max_iter=2000, C=1.0, solver="lbfgs",
            random_state=42,
        )
        clf.fit(X_train_s, train_labels_arr)

        train_acc = clf.score(X_train_s, train_labels_arr)
        held_pred = clf.predict(X_held_s)
        held_correct = int((held_pred == heldout_labels_arr).sum())
        held_acc = held_correct / len(heldout_labels_arr)
        held_proba = clf.predict_proba(X_held_s)
        ctrl_pred = clf.predict(X_ctrl_s)

        # per-fact held-out detail
        held_detail = []
        for i, h in enumerate(HELDOUT):
            correct = bool(held_pred[i] == h["source_idx"])
            held_detail.append({
                "source_idx": h["source_idx"],
                "predicted": int(held_pred[i]),
                "correct": correct,
                "max_prob": round(float(held_proba[i].max()), 4),
                "prompt_short": h["prompt"][:60],
            })

        result = {
            "layer": l,
            "train_acc": round(float(train_acc), 4),
            "held_correct": held_correct,
            "held_acc": round(float(held_acc), 4),
            "held_detail": held_detail,
            "ctrl_preds": ctrl_pred.tolist(),
        }
        per_layer.append(result)

        flag = " ***" if held_correct >= PASS_THRESHOLD else ""
        print(f"  L{l:2d}: train={train_acc:.2f}  held={held_correct}/7 ({held_acc:.0%}){flag}")

    # ── verdict ──
    best = max(per_layer, key=lambda r: (r["held_correct"], r["held_acc"]))
    max_held = best["held_correct"]

    if max_held >= PASS_THRESHOLD:
        verdict = "PASS"
        conclusion = (
            f"Concept-level representation EXISTS at L{best['layer']} "
            f"({max_held}/7 held-out). Representation engineering viable."
        )
    elif all(r["held_correct"] <= FAIL_THRESHOLD for r in per_layer):
        verdict = "FAIL"
        conclusion = (
            f"No concept-level encoding detected (max {max_held}/7 across "
            f"all {n_layers} layers). Substrate is surface-form-bound."
        )
    else:
        verdict = "INCONCLUSIVE"
        conclusion = (
            f"Partial signal (max {max_held}/7 at L{best['layer']}), "
            f"between pass ({PASS_THRESHOLD}/7) and fail ({FAIL_THRESHOLD}/7) thresholds."
        )

    print(f"\n{'='*70}")
    print(f"G3 VERDICT: {verdict}")
    print(f"  Best: L{best['layer']} - {max_held}/7 held-out correct, train={best['train_acc']:.2f}")
    if max_held >= PASS_THRESHOLD:
        print(f"  Detail at L{best['layer']}:")
        for d in best["held_detail"]:
            m = "Y" if d["correct"] else "N"
            print(f"    {m} fact={d['source_idx']} pred={d['predicted']} "
                  f"conf={d['max_prob']:.2f} | {d['prompt_short']}")
    print(f"  Conclusion: {conclusion}")
    print(f"{'='*70}")

    # ── save ──
    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v432",
        "axis": "linear_probe_concept_level",
        "model": MODEL_ID,
        "n_layers": n_layers,
        "hidden_size": hidden_size,
        "n_train": len(train_prompts),
        "n_heldout": len(HELDOUT),
        "n_controls": len(CONTROLS),
        "pass_threshold": PASS_THRESHOLD,
        "fail_threshold": FAIL_THRESHOLD,
        "collection_seconds": round(t_collect, 1),
        "method": "last-token hidden state, StandardScaler, LogisticRegression(C=1.0, multinomial)",
        "heldout_prompts": HELDOUT,
        "control_prompts": CONTROLS,
        "per_layer": per_layer,
        "best_layer": best["layer"],
        "best_held_correct": max_held,
        "verdict": verdict,
        "conclusion": conclusion,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
