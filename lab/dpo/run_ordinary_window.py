#!/usr/bin/env python3
# run_ordinary_window.py - phase-3 step 2: FROZEN BASE on ordinary (non-bait) prompts.
#
# Substrate for verify_disp_audit.py --audit. The frozen base = arm A of onto_e5_gen.py:
#   base Qwen/Qwen2.5-Coder-7B, NO adapter, NO GOLD prompt -> bare market dispositions surface.
# Loading + wrapper + decoding mirror onto_e5_gen.py arm A VERBATIM (4-bit nf4, greedy, ### wrapper)
# so outputs are comparable to the lab's established base-eval path.
#
# fix(b) step4a (2026-06-14): OPTIONAL --adapter load added. PeftModel is layered OVER the frozen
#   base (NO merge -> base/organ NOT mutated, adapter stays separable). Base load, wrapper
#   (format_example), bad_words, decode params, greedy are BYTE-IDENTICAL to the no-adapter path,
#   so the DPO arm is comparable to the base arm produced by this same harness (md5 8b6366b1).
#   --adapter ABSENT  -> base arm (no adapter), as before.
#   --adapter <dir>   -> DPO arm (frozen base + fix(b) LoRA).
#
# Output ordinary_window.jsonl: one obj/line, "id" = prompt id (provenance kept), "text" = base output.
# This is exactly the {id,text} shape verify_disp_audit.py --audit ingests.
#
# Run (pod, GPU mandatory):
#   # base arm (no adapter):
#   python run_ordinary_window.py --prompts /workspace/ordinary_prompts.jsonl \
#       --out /workspace/ordinary_window.jsonl
#   # DPO arm (fix(b) adapter layered over frozen base, no merge):
#   python run_ordinary_window.py --prompts /workspace/ordinary_prompts_v6.jsonl \
#       --adapter /workspace/adapter_fixb_dpo_v1 --out /workspace/ordinary_window_v6_dpo_raw.jsonl
#
# Dry-run (CPU, no model, mock - validates wiring + output shape only):
#   python run_ordinary_window.py --prompts ordinary_prompts.jsonl --dry-run

import argparse
import json
import sys
from pathlib import Path

BASE_MODEL = "Qwen/Qwen2.5-Coder-7B"   # base, identical to e5_gen arm A
MAX_LEN = 1024
GEN_MAX_NEW = 512
SUPPRESS_STRINGS = ["<|file_sep|>", "\u59d4\u7ec4\u7ec7\u90e8"]


def load_prompts(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def format_example(instruction):
    return f"### Instruction:\n{instruction}\n\n### Response:\n"


def build_model(adapter=None):
    """Load FROZEN base. If adapter is given, layer a PeftModel OVER it (no merge -> base not mutated,
    adapter separable). Lazy import so --dry-run needs no torch."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    assert torch.cuda.is_available(), "STOP: CUDA not available - frozen base must run on GPU"
    print(f"CUDA: {torch.cuda.is_available()} | GPU: {torch.cuda.get_device_name(0)} | "
          f"n_gpu: {torch.cuda.device_count()}", file=sys.stderr)

    tok = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16,
                             bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, quantization_config=bnb, device_map="auto",
        trust_remote_code=True, torch_dtype=torch.float16)

    if adapter:
        # Layer the LoRA over the frozen base. NO merge_and_unload -> base weights untouched,
        # adapter remains a separable delta (the DPO arm). Inference only (is_trainable=False).
        from peft import PeftModel
        ap = Path(adapter)
        assert ap.is_dir(), f"STOP: --adapter dir not found: {adapter}"
        assert (ap / "adapter_config.json").is_file(), \
            f"STOP: no adapter_config.json in {adapter} (not a PEFT adapter dir)"
        model = PeftModel.from_pretrained(model, str(ap), is_trainable=False)
        model.eval()
        # Hard guard: confirm a LoRA delta is actually attached (arm must NOT silently fall back to base).
        active = getattr(model, "active_adapters", None)
        active = active() if callable(active) else getattr(model, "active_adapter", None)
        assert active, "STOP: adapter loaded but no active LoRA adapter -> would silently be base arm"
        print(f"DPO arm: frozen base + adapter '{adapter}' (active={active}, NO merge).", file=sys.stderr)
    else:
        model.eval()
        print("Base arm: frozen base loaded (no adapter, no GOLD prompt).", file=sys.stderr)
    return tok, model


def build_bad_words_ids(tok):
    bad, seen, out = [], set(), []
    for s in SUPPRESS_STRINGS:
        for variant in (s, " " + s):
            ids = tok(variant, add_special_tokens=False)["input_ids"]
            if ids:
                bad.append(ids)
    for ids in bad:
        k = tuple(ids)
        if k not in seen:
            seen.add(k)
            out.append(ids)
    return out


def generate(tok, model, question, bad_words_ids):
    import torch
    text = format_example(question)
    inputs = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LEN).to(model.device)
    gen_kwargs = dict(max_new_tokens=GEN_MAX_NEW, do_sample=False, num_beams=1,
                      bad_words_ids=bad_words_ids, pad_token_id=tok.pad_token_id,
                      eos_token_id=tok.eos_token_id)
    with torch.no_grad():
        out = model.generate(**inputs, **gen_kwargs)
    txt = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    for s in SUPPRESS_STRINGS:
        txt = txt.replace(s, "")
    return txt.strip()


def mock_generate(question):
    """Deterministic stand-in for --dry-run: shape only, NOT representative of base behavior."""
    return f"[mock base output for: {question[:48]}]"


def main():
    ap = argparse.ArgumentParser(description="phase-3 step2: frozen base on ordinary prompts")
    ap.add_argument("--prompts", required=True, help="ordinary_prompts.jsonl (id/family/prompt)")
    ap.add_argument("--out", default="/workspace/ordinary_window.jsonl")
    ap.add_argument("--adapter", default=None,
                    help="OPTIONAL PEFT adapter dir -> layer over frozen base (DPO arm). "
                         "Absent = base arm (no adapter).")
    ap.add_argument("--dry-run", action="store_true",
                    help="CPU mock: no model, validates wiring + output shape")
    args = ap.parse_args()

    prompts = load_prompts(args.prompts)
    print(f"[load] {len(prompts)} prompts from {args.prompts}", file=sys.stderr)
    assert len(prompts) >= 20, f"STOP: need N>=20 ordinary prompts, got {len(prompts)}"

    if args.dry_run:
        print("[dry-run] mock generation, no model loaded", file=sys.stderr)
        gen_fn = lambda q: mock_generate(q)
    else:
        tok, model = build_model(adapter=args.adapter)
        bad = build_bad_words_ids(tok)
        gen_fn = lambda q: generate(tok, model, q, bad)

    arm = "dpo" if args.adapter else "base"
    n = 0
    with open(args.out, "w", encoding="utf-8") as fo:
        for i, row in enumerate(prompts, 1):
            text = gen_fn(row["prompt"])
            rec = {"id": row["id"], "text": text, "family": row.get("family")}
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
            if i % 6 == 0:
                print(f"  [{i}/{len(prompts)}]", file=sys.stderr)

    print(f"[done] arm={arm} wrote {n} outputs -> {args.out}", file=sys.stderr)
    print("=== WINDOW DONE === download it, then trim (trim_window.py) -> verify -> measure (step4b)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
