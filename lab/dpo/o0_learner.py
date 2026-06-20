#!/usr/bin/env python3
"""
o0_learner.py — organism-0 RFT LoRA learner (S3 BUILD)

WHAT: Train LoRA on Crown-verified ABSORB claims (Rejection Fine-Tuning).
WHY:  The organism learns from its own verified outputs.
HOW:  Extract ABSORB → format SFT → LoRA train (bounded) → generate on held-out.

LoRA bounds (from fix(b), proven safe — CONCEPT §3):
  r = 8, alpha = 16, targets = q,k,v,o_proj
  LR ≤ 5e-6, ≤ 1 epoch, dropout = 0.05, no merge

Usage:
  Step 1 (local):   python o0_learner.py --extract --enriched eval/o0/o0_verdicts.jsonl
                    → data/o0_sft_absorb.jsonl
  Step 2 (RunPod):  python o0_learner.py --train --data data/o0_sft_absorb.jsonl
                    → adapters/o0_lora/
  Step 3 (RunPod):  python o0_learner.py --generate --adapter adapters/o0_lora/final
                    → eval/o0/o0_heldout_gen.jsonl

Spec: CONCEPT_organism0_v1.md §3, §7.
Frozen bars: §4 G_learn (G1 fa_live ≤ 0.10, G2 ff ≤ 0.10, G3 yield ≥ 0.20).
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# CONSTANTS — FROZEN (CONCEPT §3 + fix(b) bounds)
# ---------------------------------------------------------------------------

BASE_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"

# LoRA bounds (fix(b) proven safe, CONCEPT §3)
LORA_R = 8
LORA_ALPHA = 16          # 2 × r
LORA_DROPOUT = 0.05
LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj"]
LEARNING_RATE = 5e-6
NUM_EPOCHS = 1

# Hard ceilings (asserted, not just configured)
MAX_LORA_R = 8
MAX_LEARNING_RATE = 5e-6
MAX_EPOCHS = 1

# Prompt template — MUST match rung1_wiring_v0.py generate_claim() (lines 75-78).
# Verified 2026-06-20 against on-disk source.
CLAIM_PROMPT_TEMPLATE = (
    "State one specific, verifiable scientific fact about {topic}. "
    "Include specific numbers, measurements, dates, or study references "
    "where possible. Be precise and detailed. State it as a single paragraph."
)

# NO system prompt. rung1_wiring_v0.py uses Ollama /api/generate (raw prompt,
# no system message). Training must match inference: user message only.
DEFAULT_SYSTEM_PROMPT = None


# ---------------------------------------------------------------------------
# EXTRACT: verdict trail JSONL → ABSORB records → SFT JSONL
# Source: o0_verdicts.jsonl (accumulator output, NOT o0_enriched.jsonl).
# o0_enriched.jsonl has PENDING_B2 — verdicts live in the trail only.
# Trail has duplicates (2 integrate runs → 212 entries for 112 unique IDs).
# ---------------------------------------------------------------------------

def extract_absorb(trail_path: str, output_path: str, dry_run: bool = False):
    """Extract ABSORB records from verdict trail, write SFT format."""
    records = []
    with open(trail_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    print(f"[extract] Total records in trail: {len(records)}")

    # Verdict distribution (pre-dedup)
    verdicts = {}
    for r in records:
        v = r.get("verdict", "MISSING")
        verdicts[v] = verdicts.get(v, 0) + 1
    print(f"[extract] Verdict distribution (raw): {json.dumps(verdicts)}")

    # Deduplicate by ID (trail has exact duplicates from 2 integrate runs)
    seen_ids = set()
    deduped = []
    for r in records:
        rid = r.get("id", "")
        if rid and rid not in seen_ids:
            seen_ids.add(rid)
            deduped.append(r)
    print(f"[extract] After ID dedup: {len(deduped)} unique records")

    # Filter ABSORB (accumulator sets verdict="ABSORB" for SUPPORTS)
    absorb = [r for r in deduped if r.get("verdict") == "ABSORB"]

    # Secondary safety: skip empty claims
    absorb = [r for r in absorb if r.get("claim", "").strip()]

    print(f"[extract] ABSORB (unique, non-empty): {len(absorb)}")

    if len(absorb) < 50:
        print(f"[extract] WARNING: {len(absorb)} ABSORB < K=50 threshold.")

    # Format SFT pairs (CONCEPT §3)
    sft_records = []
    for r in absorb:
        topic = r.get("topic", "")
        claim = r.get("claim", "").strip()
        sft_records.append({
            "prompt": CLAIM_PROMPT_TEMPLATE.format(topic=topic),
            "completion": claim,
            "source_id": r.get("id", ""),
            "source_doi": r.get("best_doi", ""),
            "source_topic": topic,
        })

    if dry_run:
        print(f"[extract] DRY RUN — {len(sft_records)} SFT records, "
              f"would write to {output_path}")
        if sft_records:
            print(f"[extract] Sample:")
            print(json.dumps(sft_records[0], indent=2, ensure_ascii=False))
        return sft_records

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in sft_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"[extract] Wrote {len(sft_records)} SFT records → {output_path}")
    return sft_records


# ---------------------------------------------------------------------------
# TRAIN: SFT LoRA on ABSORB buffer
# ---------------------------------------------------------------------------

def train_lora(data_path: str, output_dir: str, system_prompt: str = None,
               dry_run: bool = False):
    """Train LoRA on SFT data. Requires GPU (RunPod)."""

    # Hard ceiling checks (R7: bounds frozen before data)
    assert LORA_R <= MAX_LORA_R, f"r={LORA_R} > ceiling {MAX_LORA_R}"
    assert LEARNING_RATE <= MAX_LEARNING_RATE, f"LR > ceiling {MAX_LEARNING_RATE}"
    assert NUM_EPOCHS <= MAX_EPOCHS, f"epochs > ceiling {MAX_EPOCHS}"

    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    # Load SFT data
    sft_records = []
    with open(data_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                sft_records.append(json.loads(line))

    print(f"[train] SFT records: {len(sft_records)}")
    print(f"[train] LoRA: r={LORA_R} alpha={LORA_ALPHA} LR={LEARNING_RATE} "
          f"epochs={NUM_EPOCHS} dropout={LORA_DROPOUT}")
    print(f"[train] Targets: {LORA_TARGETS}")
    print(f"[train] Base: {BASE_MODEL}")
    print(f"[train] System prompt: {'NONE (matches Ollama /api/generate)' if not sys_prompt else sys_prompt[:80]}")


    if dry_run:
        print(f"[train] DRY RUN — would train on {len(sft_records)} records → {output_dir}")
        return

    # GPU check
    import torch
    if not torch.cuda.is_available():
        print("[train] ERROR: no GPU. Train on RunPod, not local.")
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"[train] GPU: {gpu_name} ({gpu_mem:.1f} GB)")

    from transformers import (AutoTokenizer, AutoModelForCausalLM,
                              BitsAndBytesConfig, TrainingArguments)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    import datasets

    # 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"[train] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    print(f"[train] Loading model (4-bit)...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    # LoRA
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGETS,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Format via chat template (NO system message — matches Ollama /api/generate)
    def format_chat(record):
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": record["prompt"]})
        messages.append({"role": "assistant", "content": record["completion"]})
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )

    formatted = [{"text": format_chat(r)} for r in sft_records]
    ds = datasets.Dataset.from_list(formatted)

    print(f"[train] Dataset: {len(ds)} examples")
    print(f"[train] Sample (300 chars): {formatted[0]['text'][:300]}")

    # Training
    os.makedirs(output_dir, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=1,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="constant",
        warmup_steps=0,
        logging_steps=1,
        save_strategy="epoch",
        bf16=True,
        optim="adamw_torch",
        report_to="none",
        max_grad_norm=1.0,
        seed=42,
    )

    # trl SFTTrainer — use tokenizer kwarg for broad compatibility
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        processing_class=tokenizer,
    )

    print(f"[train] Starting training...")
    t0 = time.time()
    result = trainer.train()
    dt = time.time() - t0

    print(f"[train] Done in {dt:.1f}s")
    print(f"[train] Loss: {result.training_loss:.4f}")
    print(f"[train] Steps: {result.global_step}")

    # Save adapter (NO MERGE — adapter stays separable)
    adapter_save_dir = os.path.join(output_dir, "final")
    model.save_pretrained(adapter_save_dir)
    tokenizer.save_pretrained(adapter_save_dir)

    # Verify adapter file exists
    for fname in ("adapter_model.safetensors", "adapter_model.bin"):
        fpath = os.path.join(adapter_save_dir, fname)
        if os.path.exists(fpath):
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            print(f"[train] Adapter: {fpath} ({size_mb:.1f} MB)")
            break
    else:
        print(f"[train] WARNING: no adapter file in {adapter_save_dir}")
        print(f"[train] Contents: {os.listdir(adapter_save_dir)}")

    # Training log (audit trail)
    log = {
        "base_model": BASE_MODEL,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_targets": LORA_TARGETS,
        "lora_dropout": LORA_DROPOUT,
        "learning_rate": LEARNING_RATE,
        "num_epochs": NUM_EPOCHS,
        "train_records": len(sft_records),
        "training_loss": result.training_loss,
        "global_steps": result.global_step,
        "training_time_s": round(dt, 1),
        "system_prompt": sys_prompt or "NONE",
        "adapter_dir": adapter_save_dir,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    log_path = os.path.join(output_dir, "train_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print(f"[train] Log → {log_path}")


# ---------------------------------------------------------------------------
# GENERATE: post-LoRA claims on held-out topics
# ---------------------------------------------------------------------------

def generate_heldout(adapter_dir: str, output_path: str,
                     system_prompt: str = None, dry_run: bool = False):
    """Generate claims on 20 held-out topics using base + LoRA adapter."""

    from o0_domain_list import HELD_OUT_TOPICS

    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    print(f"[generate] Held-out topics: {len(HELD_OUT_TOPICS)}")
    print(f"[generate] Adapter: {adapter_dir}")
    print(f"[generate] System prompt: {'NONE (matches Ollama /api/generate)' if not sys_prompt else sys_prompt[:80]}")


    if dry_run:
        print(f"[generate] DRY RUN — {len(HELD_OUT_TOPICS)} claims → {output_path}")
        for i, t in enumerate(HELD_OUT_TOPICS):
            print(f"  H{i:02d}: {t}")
        return

    # GPU check
    import torch
    if not torch.cuda.is_available():
        print("[generate] ERROR: no GPU. Run on RunPod.")
        sys.exit(1)

    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"[generate] Loading base model + adapter...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

    # Anti silent-base guard (from fix(b) harness rule)
    active = model.active_adapters
    if not active:
        print("[generate] ERROR: no active LoRA adapters. "
              "Refusing to generate on bare base.")
        sys.exit(1)
    print(f"[generate] Active adapters: {active}")

    # Generate
    results = []
    for i, topic in enumerate(HELD_OUT_TOPICS):
        prompt = CLAIM_PROMPT_TEMPLATE.format(topic=topic)
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": prompt})
        input_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,          # greedy = deterministic
                temperature=1.0,
                pad_token_id=tokenizer.pad_token_id,
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
        claim = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

        record = {
            "id": f"heldout_{i:02d}",
            "topic": topic,
            "claim": claim,
            "source": "post_lora",
            "adapter": adapter_dir,
        }
        results.append(record)
        print(f"  H{i:02d}: {topic[:50]:50s} → {claim[:80]}")

    # Write
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in results:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    non_empty = sum(1 for r in results if r["claim"].strip())
    avg_words = sum(len(r["claim"].split()) for r in results) / max(len(results), 1)
    print(f"[generate] Wrote {len(results)} records → {output_path}")
    print(f"[generate] Non-empty: {non_empty}/{len(results)}, "
          f"avg length: {avg_words:.1f} words")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="organism-0 RFT LoRA learner (S3)")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--extract", action="store_true",
                      help="Enriched JSONL → ABSORB → SFT JSONL")
    mode.add_argument("--train", action="store_true",
                      help="Train LoRA on SFT data (GPU required)")
    mode.add_argument("--generate", action="store_true",
                      help="Post-LoRA generation on held-out (GPU required)")

    p.add_argument("--enriched", default="eval/o0/o0_verdicts.jsonl",
                   help="Verdict trail JSONL (--extract input, default: o0_verdicts.jsonl)")
    p.add_argument("--data", default="data/o0_sft_absorb.jsonl",
                   help="SFT JSONL (--extract output / --train input)")
    p.add_argument("--adapter", default="adapters/o0_lora/final",
                   help="Adapter dir (--train output / --generate input)")
    p.add_argument("--output-dir", default="adapters/o0_lora",
                   help="Training output root (--train)")
    p.add_argument("--gen-output", default="eval/o0/o0_heldout_gen.jsonl",
                   help="Held-out generation output (--generate)")
    p.add_argument("--system-prompt", default=None,
                   help="Override system prompt text")
    p.add_argument("--system-prompt-file", default=None,
                   help="Read system prompt from file")
    p.add_argument("--dry-run", action="store_true",
                   help="Validate without training/generating")

    args = p.parse_args()

    # Resolve system prompt
    sys_prompt = None
    if args.system_prompt_file:
        with open(args.system_prompt_file, encoding="utf-8") as f:
            sys_prompt = f.read().strip()
    elif args.system_prompt:
        sys_prompt = args.system_prompt

    if args.extract:
        extract_absorb(args.enriched, args.data, dry_run=args.dry_run)
    elif args.train:
        train_lora(args.data, args.output_dir,
                   system_prompt=sys_prompt, dry_run=args.dry_run)
    elif args.generate:
        generate_heldout(args.adapter, args.gen_output,
                         system_prompt=sys_prompt, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
