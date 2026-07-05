#!/usr/bin/env python3
"""
memit_smoke.py  вЂ”  MEMIT smoke test on base Qwen2.5-7B (4-bit NF4).
Single-fact edit: "Eiffel Tower in Paris" -> "London".
MEMIT target layers L5-L10 (v429 causal tracing).

4-bit + gradient checkpointing for z* phase (backward fits 8GB).
Hook-based weight correction (no direct 4-bit weight surgery).

Run: pip install transformers accelerate bitsandbytes && python memit_smoke.py
Out: eval/memit_smoke_v430.json

v430 В· TRACK 1 ANATOMY В· MEMIT editing axis
"""

import torch
import json, os, sys, time

MODEL_ID = "Qwen/Qwen2.5-Coder-7B"
EDITING_LAYERS = [5, 6, 7, 8, 9, 10]
CRITICAL_LAYER = 10
LAMBDA = 0.0001
Z_LR = 0.5
Z_STEPS = 25
OUTPUT_PATH = "eval/memit_smoke_v430.json"

EDIT_PROMPT = "The Eiffel Tower is located in the city of"
EDIT_SUBJECT = "Eiffel Tower"
TARGET_OLD = "Paris"
TARGET_NEW = "London"

CONTROLS = [
    {"prompt": "The capital of Japan is", "target": "Tokyo"},
    {"prompt": "The chemical symbol for gold is", "target": "Au"},
    {"prompt": "The official language of Brazil is", "target": "Portuguese"},
    {"prompt": "Water freezes at zero degrees", "target": "Celsius"},
    {"prompt": "The capital of France is", "target": "Paris"},
]


def get_device(model):
    return next(model.parameters()).device


def tok_id(tokenizer, word):
    return tokenizer.encode(" " + word, add_special_tokens=False)[0]


def subject_positions(tokenizer, prompt, subject):
    enc = tokenizer(prompt, return_offsets_mapping=True, add_special_tokens=False)
    s = prompt.find(subject)
    e = s + len(subject)
    return [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > s and a < e]


def next_token_prob(model, tokenizer, prompt, word):
    dev = get_device(model)
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(dev)
    with torch.no_grad():
        logits = model(ids, use_cache=False).logits
    return torch.softmax(logits[0, -1].float(), dim=-1)[tok_id(tokenizer, word)].item()


def extract_h(output):
    return output[0] if isinstance(output, tuple) else output


def rebuild_output(output, new_h):
    return (new_h,) + output[1:] if isinstance(output, tuple) else new_h


def measure_all(model, tokenizer, label):
    p_old = next_token_prob(model, tokenizer, EDIT_PROMPT, TARGET_OLD)
    p_new = next_token_prob(model, tokenizer, EDIT_PROMPT, TARGET_NEW)
    ctrls = []
    for c in CONTROLS:
        p = next_token_prob(model, tokenizer, c["prompt"], c["target"])
        ctrls.append({"prompt": c["prompt"], "target": c["target"], "prob": round(p, 6)})
    print(f"  [{label}] P({TARGET_OLD})={p_old:.4f}  P({TARGET_NEW})={p_new:.4f}")
    for c in ctrls:
        print(f"    {c['prompt'][:40]:<40} P({c['target']})={c['prob']:.4f}")
    return {"p_old": round(p_old, 6), "p_new": round(p_new, 6), "controls": ctrls}


def optimize_z_star(model, tokenizer):
    dev = get_device(model)
    ids = tokenizer(EDIT_PROMPT, return_tensors="pt").input_ids.to(dev)
    subj_idx = subject_positions(tokenizer, EDIT_PROMPT, EDIT_SUBJECT)
    pos = subj_idx[-1]
    new_id = tok_id(tokenizer, TARGET_NEW)

    container = {}

    def save_hook(module, inp, out):
        h = extract_h(out)
        container["z"] = h[:, pos, :].detach().clone().float()

    handle = model.model.layers[CRITICAL_LAYER].register_forward_hook(save_hook)
    with torch.no_grad():
        model(ids, use_cache=False)
    handle.remove()
    z_clean = container["z"]
    print(f"  z_clean at L{CRITICAL_LAYER} pos={pos}, norm={z_clean.norm():.2f}")

    z_star = z_clean.clone().requires_grad_(True)
    opt = torch.optim.Adam([z_star], lr=Z_LR)

    for step in range(Z_STEPS):
        def inject(module, inp, out, _z=z_star):
            h = extract_h(out).clone()
            h[:, pos, :] = _z.to(h.dtype)
            return rebuild_output(out, h)

        handle = model.model.layers[CRITICAL_LAYER].register_forward_hook(inject)
        logits = model(ids, use_cache=False).logits
        handle.remove()

        lp = torch.log_softmax(logits[0, -1].float(), dim=-1)
        loss = -lp[new_id]

        opt.zero_grad()
        loss.backward()
        opt.step()

        if step % 5 == 0 or step == Z_STEPS - 1:
            p = torch.exp(-loss.detach()).item()
            print(f"    step {step:2d}: P({TARGET_NEW})={p:.4f}  loss={loss.item():.3f}")

    return z_star.detach(), z_clean, pos


def apply_hooks(model, tokenizer, z_star, z_clean, subj_pos):
    """Hook-based rank-1 correction on down_proj (no weight surgery)."""
    dev = get_device(model)
    ids = tokenizer(EDIT_PROMPT, return_tensors="pt").input_ids.to(dev)
    delta = (z_star - z_clean).squeeze()
    share = delta / len(EDITING_LAYERS)
    print(f"  delta norm={delta.norm():.4f}, per-layer={share.norm():.4f}")

    persistent = []
    for li in EDITING_LAYERS:
        container = {}

        def cap(mod, inp, out, _li=li):
            container["k"] = inp[0][:, subj_pos, :].detach().clone().float()

        h = model.model.layers[li].mlp.down_proj.register_forward_hook(cap)
        with torch.no_grad():
            model(ids, use_cache=False)
        h.remove()

        k = container["k"].squeeze()
        denom = (k @ k + LAMBDA).item()
        dW = torch.outer(share, k) / denom
        dW_T = dW.T.contiguous().to(dev)

        def make_hook(dwt):
            def hook(mod, inp, out):
                return out + inp[0] @ dwt.to(inp[0].dtype)
            return hook

        ph = model.model.layers[li].mlp.down_proj.register_forward_hook(make_hook(dW_T))
        persistent.append(ph)
        print(f"    L{li}: |k|={k.norm():.1f}  |dW|={dW.norm():.6f}  denom={denom:.1f}")

    return persistent


def main():
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available"); sys.exit(1)
    torch.cuda.init()
    try:
        _ = torch.zeros(1, device="cuda")
    except Exception as e:
        print(f"ERROR: CUDA alloc failed: {e}"); sys.exit(1)
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    print("=" * 60)
    print("MEMIT SMOKE TEST v430")
    print(f"Model: {MODEL_ID}  Layers: {EDITING_LAYERS}")
    print(f"Edit: '{EDIT_PROMPT}' -> '{TARGET_NEW}'")
    print("=" * 60)

    print("\n[1] Loading model (4-bit NF4)...")
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto", trust_remote_code=True,
    )
    model.eval()
    print(f"  {sum(p.numel() for p in model.parameters())/1e9:.1f}B params on {get_device(model)}")
    print(f"  '{TARGET_OLD}'={tok_id(tokenizer, TARGET_OLD)}  "
          f"'{TARGET_NEW}'={tok_id(tokenizer, TARGET_NEW)}")

    print("\n[2] PRE-EDIT")
    pre = measure_all(model, tokenizer, "pre")

    print(f"\n[3] z* optimization (L{CRITICAL_LAYER}, {Z_STEPS} steps, lr={Z_LR})")
    torch.cuda.empty_cache()
    model.gradient_checkpointing_enable(
        gradient_checkpointing_kwargs={"use_reentrant": False})
    model.train()
    t0 = time.time()
    z_star, z_clean, subj_pos = optimize_z_star(model, tokenizer)
    t_z = time.time() - t0
    model.eval()
    model.gradient_checkpointing_disable()
    torch.cuda.empty_cache()
    print(f"  Done in {t_z:.1f}s")

    print(f"\n[4] Applying hook-based edits to {len(EDITING_LAYERS)} layers")
    hooks = apply_hooks(model, tokenizer, z_star, z_clean, subj_pos)

    print("\n[5] POST-EDIT")
    post = measure_all(model, tokenizer, "post")

    edit_ok = post["p_new"] > 0.3
    ctrl_pre = sum(c["prob"] for c in pre["controls"]) / len(pre["controls"])
    ctrl_post = sum(c["prob"] for c in post["controls"]) / len(post["controls"])
    ctrl_drop = (ctrl_pre - ctrl_post) / ctrl_pre if ctrl_pre > 1e-6 else 0
    ctrl_ok = ctrl_drop < 0.20
    g3 = "PASS" if (edit_ok and ctrl_ok) else "FAIL"

    print(f"\n{'='*60}")
    print(f"edit_success: {edit_ok}  P({TARGET_NEW})={post['p_new']:.4f} (threshold 0.3)")
    print(f"control_safe: {ctrl_ok}  drop={ctrl_drop:.1%} (threshold 20%)")
    print(f"G3 verdict: {g3}")
    if not edit_ok:
        print("  -> MEMIT edit did not take effect")
    if not ctrl_ok:
        print("  -> Collateral damage exceeds threshold")
    print("=" * 60)

    for h in hooks:
        h.remove()

    os.makedirs("eval", exist_ok=True)
    out = {
        "session": "v430", "axis": "memit_smoke", "model": MODEL_ID,
        "editing_layers": EDITING_LAYERS, "critical_layer": CRITICAL_LAYER,
        "lambda": LAMBDA, "z_lr": Z_LR, "z_steps": Z_STEPS,
        "method": "4bit_NF4 + gradient_checkpointing + hook_correction",
        "edit": {"prompt": EDIT_PROMPT, "subject": EDIT_SUBJECT,
                 "old": TARGET_OLD, "new": TARGET_NEW},
        "pre_edit": pre, "post_edit": post,
        "z_opt_seconds": round(t_z, 1),
        "edit_success": edit_ok, "control_safe": ctrl_ok,
        "control_pre_mean": round(ctrl_pre, 6),
        "control_post_mean": round(ctrl_post, 6),
        "control_drop_pct": round(ctrl_drop * 100, 2),
        "g3_verdict": g3,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
