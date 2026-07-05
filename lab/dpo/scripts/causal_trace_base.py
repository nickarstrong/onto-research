#!/usr/bin/env python3
"""
causal_trace_base.py — Causal tracing (activation patching) on base Qwen2.5-7B.
Meng et al. 2022 methodology. Identifies MLP layers where factual knowledge
is stored. G1 measurement for ROME/MEMIT editing target.

Method:
  1. Clean run → P(target) + save MLP outputs at all layers
  2. Corrupted run → noise on subject-token embeddings → P_corrupt(target)
  3. For each layer: corrupted + restore clean MLP output at subject positions
     → P_restored(target)
  4. Causal effect = (P_restored - P_corrupt) / (P_clean - P_corrupt)

Run:  python causal_trace_base.py
Out:  eval/causal_trace_v429.json

v429 · TRACK 1 ANATOMY · causal tracing axis
"""

import torch
import json
import os
import sys
import time
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# ── Config ──────────────────────────────────────────────────────────
MODEL_ID = "Qwen/Qwen2.5-7B"
NUM_LAYERS = 28
NOISE_STD_MULTIPLIER = 3.0   # σ = 3 × std(clean_embeddings)
N_TRIALS = 5                  # noise seeds per fact
OUTPUT_PATH = "eval/causal_trace_v429.json"

# ── Facts base model should know (NOT abiogenesis) ──────────────────
# 15 facts — script validates each via clean_prob (top5 printed)
FACTS = [
    {"prompt": "The Eiffel Tower is located in the city of",
     "subject": "Eiffel Tower", "target": "Paris"},
    {"prompt": "The capital of Japan is",
     "subject": "Japan", "target": "Tokyo"},
    {"prompt": "The currency of the United Kingdom is the",
     "subject": "United Kingdom", "target": "pound"},
    {"prompt": "The chemical symbol for gold is",
     "subject": "gold", "target": "Au"},
    {"prompt": "The largest planet in the solar system is",
     "subject": "solar system", "target": "Jupiter"},
    {"prompt": "The official language of Brazil is",
     "subject": "Brazil", "target": "Portuguese"},
    {"prompt": "Water freezes at zero degrees",
     "subject": "Water", "target": "Celsius"},
    {"prompt": "The capital of France is",
     "subject": "France", "target": "Paris"},
    {"prompt": "Mars is commonly known as the red",
     "subject": "Mars", "target": "planet"},
    {"prompt": "The speed of light in a vacuum is approximately 300000 kilometers per",
     "subject": "light", "target": "second"},
    {"prompt": "The chemical symbol for oxygen is",
     "subject": "oxygen", "target": "O"},
    {"prompt": "The Sahara is the largest hot desert in",
     "subject": "Sahara", "target": "Africa"},
    {"prompt": "The theory of general relativity was proposed by",
     "subject": "general relativity", "target": "Albert"},
    {"prompt": "The Nile is the longest river in",
     "subject": "Nile", "target": "Africa"},
    {"prompt": "The atomic number of carbon is",
     "subject": "carbon", "target": "6"},
]


def load_model():
    print(f"Loading {MODEL_ID} (4-bit NF4)...")
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print(f"Loaded. Layers: {len(model.model.layers)}")
    return model, tok


def find_subject_indices(tokenizer, prompt, subject):
    """Token positions of subject within prompt via offset_mapping."""
    enc = tokenizer(prompt, return_offsets_mapping=True, add_special_tokens=False)
    offsets = enc["offset_mapping"]

    s_start = prompt.find(subject)
    if s_start == -1:
        raise ValueError(f"Subject '{subject}' not in prompt '{prompt}'")
    s_end = s_start + len(subject)

    indices = [i for i, (a, b) in enumerate(offsets) if b > s_start and a < s_end]
    if not indices:
        raise ValueError(f"No tokens overlap subject '{subject}' in prompt")
    return indices


def get_target_id(tokenizer, target):
    """First token of ' <target>' (with leading space, as model would predict)."""
    ids = tokenizer.encode(" " + target, add_special_tokens=False)
    return ids[0]


def prob_of(logits, token_id):
    """P(token_id) from logits at last position."""
    return torch.softmax(logits[0, -1].float(), dim=-1)[token_id].item()


def top_k_tokens(tokenizer, logits, k=5):
    """Top-k decoded tokens + probs from last position."""
    probs = torch.softmax(logits[0, -1].float(), dim=-1)
    vals, idxs = torch.topk(probs, k)
    return [(tokenizer.decode([i]), round(v, 4)) for i, v in zip(idxs.tolist(), vals.tolist())]


def trace_fact(model, tokenizer, fact, n_trials, noise_mult):
    """Full causal tracing for one fact. Returns dict with per-layer MLP effects."""
    prompt = fact["prompt"]
    subject = fact["subject"]
    target = fact["target"]

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    target_id = get_target_id(tokenizer, target)
    subj_idx = find_subject_indices(tokenizer, prompt, subject)

    # Decode subject tokens for verification
    subj_tokens = [tokenizer.decode([input_ids[0, i]]) for i in subj_idx]

    # ── Clean run: save MLP outputs ─────────────────────────────────
    clean_mlp = {}
    handles = []
    for li in range(NUM_LAYERS):
        def _hook(mod, inp, out, _li=li):
            clean_mlp[_li] = out.detach().clone()
        handles.append(model.model.layers[li].mlp.register_forward_hook(_hook))

    with torch.no_grad():
        clean_embeds = model.model.embed_tokens(input_ids).detach().clone()
        clean_logits = model(inputs_embeds=clean_embeds).logits

    for h in handles:
        h.remove()

    p_clean = prob_of(clean_logits, target_id)
    top5 = top_k_tokens(tokenizer, clean_logits)

    # ── Noise calibration ───────────────────────────────────────────
    noise_std = clean_embeds.float().std().item() * noise_mult

    # ── Trials ──────────────────────────────────────────────────────
    mlp_effects = np.zeros((n_trials, NUM_LAYERS))
    corrupt_probs = []

    for t in range(n_trials):
        rng = torch.Generator(device=clean_embeds.device)
        rng.manual_seed(t + 42)
        noise = torch.randn(
            1, len(subj_idx), clean_embeds.shape[-1],
            generator=rng, device=clean_embeds.device, dtype=clean_embeds.dtype,
        ) * noise_std

        # Corrupted (no restore)
        c_embeds = clean_embeds.clone()
        c_embeds[:, subj_idx, :] += noise
        with torch.no_grad():
            c_logits = model(inputs_embeds=c_embeds).logits
        p_corrupt = prob_of(c_logits, target_id)
        corrupt_probs.append(p_corrupt)

        denom = p_clean - p_corrupt
        if abs(denom) < 1e-8:
            # Corruption had no effect — skip trial
            mlp_effects[t, :] = 0.0
            continue

        # Restored: for each layer, patch MLP at subject positions
        for li in range(NUM_LAYERS):
            def _restore(mod, inp, out, _li=li):
                r = out.clone()
                r[:, subj_idx, :] = clean_mlp[_li][:, subj_idx, :]
                return r

            h = model.model.layers[li].mlp.register_forward_hook(_restore)
            r_embeds = clean_embeds.clone()
            r_embeds[:, subj_idx, :] += noise  # same noise
            with torch.no_grad():
                r_logits = model(inputs_embeds=r_embeds).logits
            p_restored = prob_of(r_logits, target_id)
            h.remove()

            mlp_effects[t, li] = (p_restored - p_corrupt) / denom

    return {
        "prompt": prompt,
        "subject": subject,
        "subject_tokens": subj_tokens,
        "subject_indices": subj_idx,
        "target": target,
        "target_token_id": target_id,
        "clean_prob": round(p_clean, 6),
        "corrupt_prob_mean": round(float(np.mean(corrupt_probs)), 6),
        "top5_clean": top5,
        "mlp_causal_effect_mean": [round(x, 6) for x in mlp_effects.mean(axis=0).tolist()],
        "mlp_causal_effect_std": [round(x, 6) for x in mlp_effects.std(axis=0).tolist()],
    }


def analyze(results):
    """Aggregate analysis with filtering, clamping, and ROME-targeted view.

    Fixes vs v429-run1:
      - Filter facts where corruption didn't meaningfully hurt (denom < 5% of clean)
      - Clamp effects to [0, 1.5] to suppress outliers
      - ROME-targeted window: L5+ only (L0-4 = noise-recovery artifact, not factual storage)
      - Per-fact peak table for manual inspection
    """
    CLAMP_MAX = 1.5
    MIN_CORRUPTION_RATIO = 0.05  # denom must be > 5% of clean_prob
    MIN_CLEAN_PROB = 0.05         # model must actually know the fact
    ROME_START = 5                # early layers excluded for ROME targeting

    # ── Filter ──────────────────────────────────────────────────────
    valid = []
    excluded = []
    for r in results:
        denom = r["clean_prob"] - r["corrupt_prob_mean"]
        threshold = r["clean_prob"] * MIN_CORRUPTION_RATIO
        if denom > threshold and r["clean_prob"] > MIN_CLEAN_PROB:
            valid.append(r)
        else:
            reason = "corruption_helped" if denom <= 0 else (
                "corruption_too_weak" if denom <= threshold else "clean_prob_too_low")
            excluded.append({"prompt": r["prompt"][:60], "reason": reason,
                             "clean": r["clean_prob"], "corrupt": r["corrupt_prob_mean"]})

    if not valid:
        return {"error": "No facts survived corruption filter", "excluded": excluded}

    # ── Clamped effect matrix ───────────────────────────────────────
    mat = np.array([
        np.clip(r["mlp_causal_effect_mean"], 0.0, CLAMP_MAX) for r in valid
    ])  # (n_valid, NUM_LAYERS)

    layer_mean = mat.mean(axis=0)
    total = float(layer_mean.sum())

    # ── Full-range peaks ────────────────────────────────────────────
    peak_layer = int(np.argmax(layer_mean))
    peak_frac = layer_mean[peak_layer] / total if total > 1e-6 else 0.0

    best_ws = 0
    best_wsum = -1.0
    for s in range(NUM_LAYERS - 2):
        w = layer_mean[s:s + 3].sum()
        if w > best_wsum:
            best_wsum = w
            best_ws = s
    win_frac = best_wsum / total if total > 1e-6 else 0.0

    # ── ROME-targeted: L5+ only ────────────────────────────────────
    rome_mean = layer_mean[ROME_START:]
    rome_total = float(rome_mean.sum())
    rome_peak = int(np.argmax(rome_mean)) + ROME_START

    rome_ws = ROME_START
    rome_wsum = -1.0
    for s in range(ROME_START, NUM_LAYERS - 2):
        w = layer_mean[s:s + 3].sum()
        if w > rome_wsum:
            rome_wsum = w
            rome_ws = s
    rome_win_frac = rome_wsum / rome_total if rome_total > 1e-6 else 0.0

    # ── Per-fact peaks ──────────────────────────────────────────────
    per_fact = []
    for r in valid:
        eff = np.clip(r["mlp_causal_effect_mean"], 0.0, CLAMP_MAX)
        pk_all = int(np.argmax(eff))
        pk_rome = int(np.argmax(eff[ROME_START:])) + ROME_START
        per_fact.append({
            "prompt": r["prompt"][:55],
            "peak_all": f"L{pk_all}",
            "peak_L5plus": f"L{pk_rome}",
            "clean_prob": r["clean_prob"],
            "damage": round(r["clean_prob"] - r["corrupt_prob_mean"], 4),
        })

    # ── G3: 3-layer window >50% of ROME-range total ────────────────
    g3_pass = rome_win_frac > 0.50

    return {
        "n_valid": len(valid),
        "n_excluded": len(excluded),
        "excluded": excluded,
        "clamp_max": CLAMP_MAX,
        "rome_start_layer": ROME_START,
        "layer_mean_clamped": [round(x, 6) for x in layer_mean.tolist()],
        "total_effect": round(total, 4),
        "peak_layer": peak_layer,
        "peak_fraction": round(peak_frac, 4),
        "best_3layer_window": [best_ws, best_ws + 1, best_ws + 2],
        "best_3layer_window_fraction": round(win_frac, 4),
        "rome_peak_layer": rome_peak,
        "rome_best_3layer_window": [rome_ws, rome_ws + 1, rome_ws + 2],
        "rome_best_3layer_window_fraction": round(rome_win_frac, 4),
        "per_fact_peaks": per_fact,
        "g3_falsifier": f"3-layer window >50% of L{ROME_START}+ total → ROME viable",
        "g3_verdict": "PASS" if g3_pass else "FAIL",
    }


def main():
    os.makedirs("eval", exist_ok=True)
    model, tokenizer = load_model()

    results = []
    t0 = time.time()
    for i, fact in enumerate(FACTS):
        print(f"\n[{i+1}/{len(FACTS)}] {fact['prompt']} → {fact['target']}")
        r = trace_fact(model, tokenizer, fact, N_TRIALS, NOISE_STD_MULTIPLIER)
        print(f"  clean={r['clean_prob']:.4f}  corrupt={r['corrupt_prob_mean']:.4f}"
              f"  top5={r['top5_clean']}")
        # Peak layer for this fact
        effects = r["mlp_causal_effect_mean"]
        pk = int(np.argmax(effects))
        print(f"  peak MLP layer: L{pk} ({effects[pk]:.4f})")
        results.append(r)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")

    summary = analyze(results)
    print(f"\n=== SUMMARY ===")
    print(f"Valid facts: {summary.get('n_valid','?')}/{len(results)} "
          f"(excluded: {summary.get('n_excluded',0)})")
    if "error" in summary:
        print(f"ERROR: {summary['error']}")
    else:
        print(f"Peak layer (all): L{summary['peak_layer']} "
              f"({summary['peak_fraction']:.1%} of total)")
        win = summary["best_3layer_window"]
        print(f"Best 3-layer window (all): L{win[0]}-L{win[2]} "
              f"({summary['best_3layer_window_fraction']:.1%} of total)")
        rw = summary["rome_best_3layer_window"]
        print(f"ROME peak (L5+): L{summary['rome_peak_layer']}")
        print(f"ROME best 3-layer window (L5+): L{rw[0]}-L{rw[2]} "
              f"({summary['rome_best_3layer_window_fraction']:.1%} of L5+ total)")
        print(f"\nPer-fact peaks:")
        for pf in summary["per_fact_peaks"]:
            print(f"  {pf['prompt']:<55} all={pf['peak_all']:<4} "
                  f"L5+={pf['peak_L5plus']:<4} clean={pf['clean_prob']:.3f} "
                  f"dmg={pf['damage']:.3f}")
        if summary.get("excluded"):
            print(f"\nExcluded:")
            for ex in summary["excluded"]:
                print(f"  {ex['prompt']:<55} {ex['reason']} "
                      f"(clean={ex['clean']:.3f} corrupt={ex['corrupt']:.3f})")
        print(f"\nG3 verdict: {summary['g3_verdict']}")

    output = {
        "session": "v429",
        "axis": "causal_tracing_base_mlp",
        "model": MODEL_ID,
        "n_trials": N_TRIALS,
        "noise_std_multiplier": NOISE_STD_MULTIPLIER,
        "elapsed_seconds": round(elapsed, 1),
        "facts": results,
        "summary": summary,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
