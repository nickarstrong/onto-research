"""
ONTO SFT Training - Qwen2.5-Coder-7B + QLoRA
Pure PyTorch loop. No trl, no unsloth.
Dynamic padding (no fixed 2048 waste).
Works on Windows (local) and Colab.

v3.0 - 2026-06-01
"""

# datasets BEFORE torch (reverse = silent crash on Windows)
from datasets import Dataset
import json
import os
import math
import time
import torch
from datetime import datetime
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# -- CONFIG --
BASE_MODEL = "Qwen/Qwen2.5-Coder-7B"
DATA_PATH = r"C:\Projects\onto-research\lab\data\sft\sft_ALL_FINAL.jsonl"
OUTPUT_DIR = r"C:\Projects\onto-research\lab\models\onto-qwen7b-sft-v1"
LOG_PATH = r"C:\Projects\onto-research\lab\logs\sft_log.jsonl"

MAX_SEQ_LEN = 1024
BATCH_SIZE = 1
GRAD_ACCUM = 8
EPOCHS = 3
LR = 2e-5
WARMUP_STEPS = 50
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
EVAL_EVERY = 10
SAVE_EVERY = 50
PATIENCE = 5
SEED = 42

LORA_TARGETS = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]


# -- DATA --
def load_jsonl(path):
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pairs.append(json.loads(line))
    return pairs


def tokenize_all(pairs, tokenizer, max_len):
    """Tokenize without padding. Each sample = its natural length."""
    results = []
    skipped = 0

    for p in pairs:
        user_part = f"<|im_start|>user\n{p['instruction']}<|im_end|>\n<|im_start|>assistant\n"
        asst_part = f"{p['output']}<|im_end|>\n"

        user_ids = tokenizer.encode(user_part, add_special_tokens=False)
        asst_ids = tokenizer.encode(asst_part, add_special_tokens=False)
        full_ids = user_ids + asst_ids

        if len(full_ids) > max_len:
            avail = max_len - len(user_ids)
            if avail < 10:
                skipped += 1
                continue
            asst_ids = asst_ids[:avail]
            full_ids = user_ids + asst_ids

        labels = [-100] * len(user_ids) + asst_ids

        results.append({
            "input_ids": full_ids,
            "labels": labels,
            "attention_mask": [1] * len(full_ids),
        })

    if skipped:
        print(f"  Skipped {skipped} pairs (too long)")

    lengths = [len(r["input_ids"]) for r in results]
    print(f"  Seq lengths: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)//len(lengths)}")

    return results


def collate_fn(batch):
    """Dynamic padding: pad to max length in this batch only."""
    max_len = max(len(b["input_ids"]) for b in batch)

    input_ids = []
    labels = []
    attention_mask = []

    for b in batch:
        pad_len = max_len - len(b["input_ids"])
        input_ids.append(b["input_ids"] + [0] * pad_len)
        labels.append(b["labels"] + [-100] * pad_len)
        attention_mask.append(b["attention_mask"] + [0] * pad_len)

    return {
        "input_ids": torch.tensor(input_ids),
        "labels": torch.tensor(labels),
        "attention_mask": torch.tensor(attention_mask),
    }


# -- LR SCHEDULE --
def get_lr(step, total_steps, warmup_steps, max_lr):
    if step < warmup_steps:
        return max_lr * step / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    return max_lr * 0.5 * (1.0 + math.cos(math.pi * progress))


# -- EVAL --
def evaluate(model, eval_loader):
    model.eval()
    total_loss = 0.0
    count = 0
    with torch.no_grad():
        for batch in eval_loader:
            batch = {k: v.to(model.device) for k, v in batch.items()}
            outputs = model(**batch)
            total_loss += outputs.loss.item()
            count += 1
    model.train()
    return total_loss / max(count, 1)


# -- MAIN --
def main():
    torch.manual_seed(SEED)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    run_dir = os.path.join(OUTPUT_DIR, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    print(f"{'='*60}")
    print(f"ONTO SFT v3 · Qwen2.5-Coder-7B + QLoRA")
    print(f"Output: {run_dir}")
    print(f"CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU: {gpu} ({vram:.1f} GB)")
    print(f"{'='*60}")

    # -- Load data
    raw = load_jsonl(DATA_PATH)
    print(f"Loaded {len(raw)} pairs")

    import random
    random.seed(SEED)
    random.shuffle(raw)
    split = int(len(raw) * 0.9)
    train_raw, eval_raw = raw[:split], raw[split:]
    print(f"Train: {len(train_raw)}, Eval: {len(eval_raw)}")

    # -- Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # -- Tokenize (no padding)
    print("Tokenizing train...")
    train_data = tokenize_all(train_raw, tokenizer, MAX_SEQ_LEN)
    print("Tokenizing eval...")
    eval_data = tokenize_all(eval_raw, tokenizer, MAX_SEQ_LEN)

    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    eval_loader = DataLoader(eval_data, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)

    # -- Model (QLoRA 4-bit)
    print("Loading model in 4-bit...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="sdpa",
    )
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False

    # -- LoRA
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGETS,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    trainable, total = model.get_nb_trainable_parameters()
    print(f"Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # -- Optimizer
    try:
        import bitsandbytes as bnb
        optimizer = bnb.optim.AdamW8bit(model.parameters(), lr=LR, weight_decay=0.01)
    except Exception:
        optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
        print("Warning: using standard AdamW")

    # -- Training loop
    total_steps = EPOCHS * len(train_loader) // GRAD_ACCUM
    print(f"\nTotal steps: {total_steps} ({EPOCHS} epochs x {len(train_loader)} batches / {GRAD_ACCUM} accum)")
    print(f"Eval every {EVAL_EVERY} steps, save every {SAVE_EVERY} steps")
    print(f"Early stopping patience: {PATIENCE}")

    model.train()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})

    global_step = 0
    accum_loss = 0.0
    best_eval_loss = float("inf")
    patience_counter = 0
    log_entries = []
    t_start = time.time()

    for epoch in range(EPOCHS):
        print(f"\n--- Epoch {epoch+1}/{EPOCHS} ---")

        for batch_idx, batch in enumerate(train_loader):
            batch = {k: v.to(model.device) for k, v in batch.items()}

            outputs = model(**batch)
            loss = outputs.loss / GRAD_ACCUM
            loss.backward()
            accum_loss += loss.item()

            if (batch_idx + 1) % GRAD_ACCUM == 0:
                global_step += 1

                # LR schedule
                lr = get_lr(global_step, total_steps, WARMUP_STEPS, LR)
                for pg in optimizer.param_groups:
                    pg["lr"] = lr

                # Gradient clip + step
                torch.nn.utils.clip_grad_norm_(model.parameters(), 0.3)
                optimizer.step()
                optimizer.zero_grad()

                # Log
                if global_step % 5 == 0 or global_step <= 10:
                    elapsed = time.time() - t_start
                    print(f"  step {global_step}: loss={accum_loss:.4f} lr={lr:.2e} [{elapsed:.0f}s]")

                    entry = {"step": global_step, "loss": accum_loss, "lr": lr, "epoch": epoch+1, "time": elapsed}
                    log_entries.append(entry)

                accum_loss = 0.0

                # Eval
                if global_step % EVAL_EVERY == 0:
                    eval_loss = evaluate(model, eval_loader)
                    print(f"  >>> eval_loss={eval_loss:.4f} (best={best_eval_loss:.4f})")

                    log_entries.append({"step": global_step, "eval_loss": eval_loss})

                    if eval_loss < best_eval_loss:
                        best_eval_loss = eval_loss
                        patience_counter = 0
                        # Save best
                        best_dir = os.path.join(run_dir, "best")
                        os.makedirs(best_dir, exist_ok=True)
                        model.save_pretrained(best_dir)
                        tokenizer.save_pretrained(best_dir)
                        print(f"  >>> Saved best model (eval_loss={eval_loss:.4f})")
                    else:
                        patience_counter += 1
                        if patience_counter >= PATIENCE:
                            print(f"  >>> Early stopping at step {global_step}")
                            break

                # Periodic save
                if global_step % SAVE_EVERY == 0:
                    ckpt_dir = os.path.join(run_dir, f"checkpoint-{global_step}")
                    os.makedirs(ckpt_dir, exist_ok=True)
                    model.save_pretrained(ckpt_dir)
                    tokenizer.save_pretrained(ckpt_dir)

        else:
            continue
        break  # early stopping broke inner loop

    # -- Final save
    model.save_pretrained(run_dir)
    tokenizer.save_pretrained(run_dir)

    # -- Log
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

    # -- Summary
    elapsed_total = time.time() - t_start
    summary = {
        "base_model": BASE_MODEL,
        "data_path": DATA_PATH,
        "total_pairs": len(raw),
        "train_pairs": len(train_raw),
        "eval_pairs": len(eval_raw),
        "epochs": EPOCHS,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lr": LR,
        "max_seq_len": MAX_SEQ_LEN,
        "total_steps": global_step,
        "best_eval_loss": best_eval_loss,
        "training_time_seconds": int(elapsed_total),
        "timestamp": timestamp,
    }

    summary_path = os.path.join(run_dir, "training_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nTraining complete in {elapsed_total/60:.1f} minutes")
    print(f"Summary saved: {summary_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
