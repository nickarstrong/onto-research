# %% [markdown]
# # ONTO · Experiment #1 · E7 — SFT-only Reflex LoRA + targeted guard density (Qwen2.5-Coder-7B base)
#
# **Scope (E7 run):** RECIPE = E2 VERBATIM (lr1e-4, all-linear) — UNCHANGED from E3/E4. ONLY data changed:
# `sft_reflex_392.jsonl` (323 + 69 E7 guard pairs: 40 P6_premise_guard + 17 P6_disclaim_guard + 12 P6_anchor),
# run leak-gate, emit A/B/C(/D) `outputs.json` for `eval/onto_eval.py` (NEXT session, pack v18).
#
# **E4-lesson fix (memory #28):** adapter zip downloaded IMMEDIATELY after train; outputs.json
# re-written + downloaded after EACH arm — a crash mid-inference costs at most one arm, not the run.
#
# **NOT in this notebook:** eval/scoring. That is S3 (`onto_eval.py` consumes outputs.json).
#
# Hardware: Kaggle T4x2 (Accelerator = GPU T4 x2). Runtime ~3-4h (train) + ~30-50min (3-4 arm inference).
#
# Inputs expected as a Kaggle Dataset attached at `/kaggle/input/onto-exp1-s1/`:
#   - sft_reflex_392.jsonl   (392 rows: instruction + output + category; incl. 59 P5_refusal_on_unknown)
#   - heldout_v1.3.jsonl     (36 rows: id + question + type)
# Outputs to /kaggle/working/:
#   - adapter_E3_reflex_lora.zip (peft adapter + tokenizer + run_meta.json)
#   - leak_report.md
#   - outputs.json              (arms A/B/C[/D] -> onto_eval.py)
#   - checkpoints/              (every ~30 steps)

# %%
# ---- HARD ORDER: datasets BEFORE torch (01_LAB §3) ----
import os, sys, subprocess

def pip(*pkgs):
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pkgs], check=True)

# Kaggle T4 image is usually current enough; pin only what matters. No unsloth, no trl (01_LAB §3).
pip("-U", "peft", "bitsandbytes>=0.46.1")

import datasets            # noqa: F401  (import BEFORE torch — reverse = silent crash, 01_LAB §3)
import json, re, zipfile, shutil, math
from pathlib import Path
from collections import Counter
import torch
import transformers
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling, set_seed,
)
from peft import LoraConfig, get_peft_model, PeftModel

print("torch", torch.__version__, "| transformers", transformers.__version__,
      "| cuda", torch.cuda.is_available(), "| n_gpu", torch.cuda.device_count())
assert torch.cuda.is_available() and torch.cuda.device_count() >= 1, (
    "STOP: no GPU in this session (Accelerator=None / quota exhausted). "
    "Set Accelerator = GPU T4 x2 and re-run after quota reset."
)

# %%
# ============================ CONFIG (HARD, 01_LAB §4 + README_S1) ============================
SEED            = 42
BASE_MODEL      = "Qwen/Qwen2.5-Coder-7B"          # base, NOT Instruct
WORK            = Path("/kaggle/working") if Path("/kaggle").exists() else Path("/content/working")
WORK.mkdir(parents=True, exist_ok=True)

def find_input(fname):
    roots = [Path("/kaggle/input"), Path("/content"), Path(".")]
    for root in roots:
        if root.exists():
            hits = list(root.rglob(fname))
            if hits:
                return hits[0]
    raise AssertionError(f"STOP: {fname} not found — upload it (Colab: Files panel; Kaggle: attach dataset)")

TRAIN_PATH      = find_input("sft_reflex_392.jsonl")
HELDOUT_PATH    = find_input("heldout_v1.3.jsonl")
print("train  =", TRAIN_PATH)
print("heldout=", HELDOUT_PATH)
CKPT_DIR        = WORK / "checkpoints"
ADAPTER_DIR     = WORK / "adapter_E7_sft_392"
ADAPTER_ZIP     = WORK / "adapter_E7_sft_392.zip"
OUTPUTS_JSON    = WORK / "outputs.json"
LEAK_REPORT     = WORK / "leak_report.md"

# ---- incremental download helper (E4 lesson, memory #28) ----
# On Colab: push a file to the local machine the moment it exists, so a mid-run
# crash never loses already-computed work. On RunPod/Kaggle: no-op (persistent disk).
def safe_download(path):
    try:
        from google.colab import files as _gf  # noqa
        if Path(path).exists():
            print("  -> downloading to PC:", Path(path).name)
            _gf.download(str(path))
    except Exception:
        pass  # not Colab, or download unsupported — disk persists there

# LoRA / SFT
LORA_R          = 16
LORA_ALPHA      = 32
LORA_DROPOUT    = 0.05
LR              = 1e-4                              # E2 dose: was 1e-5 in E1 (NO-GO collapse)
WEIGHT_DECAY    = 0.0
EPOCHS          = 3
WARMUP_RATIO    = 0.10
PER_DEVICE_BS   = 1
GRAD_ACCUM      = 8
MAX_LEN         = 1024
SAVE_STEPS      = 30                                # checkpoint ~every 30 steps
LORA_TARGETS    = ["q_proj", "k_proj", "v_proj", "o_proj",
                   "gate_proj", "up_proj", "down_proj"]   # E2: all-linear (E1 was attention-only)

# Token suppression (01_LAB §4): Qwen artifact + corpus contamination
SUPPRESS_STRINGS = ["<|file_sep|>", "委组织部"]

# Inference
GEN_MAX_NEW     = 512
GEN_TEMP        = 0.0                                # deterministic
RUN_ARM_D       = True                              # optional interference arm (LoRA + GOLD prompt)

# Leak gate
LEAK_EXACT_MIN_WORDS = 10                            # >=10-word continuous train substring in output
LEAK_NGRAM_N         = 7
LEAK_NGRAM_THRESH    = 0.15                          # 7-gram overlap rate > 15% -> leak flag

set_seed(SEED)

# %%
# ============================ S0 GATE (stop if artifacts lost) ============================
def count_lines(p):
    with open(p, encoding="utf-8") as f:
        return sum(1 for _ in f)

assert TRAIN_PATH.exists(),   f"STOP: missing {TRAIN_PATH} (S0 artifact lost)"
assert HELDOUT_PATH.exists(), f"STOP: missing {HELDOUT_PATH} (S0 artifact lost)"
n_train, n_held = count_lines(TRAIN_PATH), count_lines(HELDOUT_PATH)
assert n_train == 392, f"STOP: sft_reflex_392.jsonl = {n_train} lines, expected 392 (E7 artifact lost)"
assert n_held  == 36,  f"STOP: heldout_v1.3.jsonl = {n_held} lines, expected 36 (S0 lost)"
print(f"S0 gate OK: train={n_train}, heldout={n_held}")

CKPT_DIR.mkdir(parents=True, exist_ok=True)

# %%
# ============================ LOAD DATA ============================
train_rows = [json.loads(l) for l in open(TRAIN_PATH, encoding="utf-8")]
held_rows  = [json.loads(l) for l in open(HELDOUT_PATH, encoding="utf-8")]
print("train categories:", Counter(r["category"] for r in train_rows))
print("heldout types:", Counter(r["type"] for r in held_rows))

# %%
# ============================ TOKENIZER ============================
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Prompt format: plain base model (no chat template — arm C must hold reflex WITHOUT prompt scaffold).
# Minimal instruction wrapper; identical wrapper reused at inference for A/C/D-no-prompt arms.
def format_example(instruction, output=None):
    text = f"### Instruction:\n{instruction}\n\n### Response:\n"
    if output is not None:
        text += output + tokenizer.eos_token
    return text

# Loss-mask the instruction portion: train only on the response tokens.
def tokenize_with_mask(row):
    prompt = format_example(row["instruction"])
    full   = format_example(row["instruction"], row["output"])
    full_ids   = tokenizer(full, truncation=True, max_length=MAX_LEN, add_special_tokens=False)["input_ids"]
    prompt_ids = tokenizer(prompt, truncation=True, max_length=MAX_LEN, add_special_tokens=False)["input_ids"]
    labels = list(full_ids)
    plen = min(len(prompt_ids), len(labels))
    for i in range(plen):
        labels[i] = -100                            # mask instruction tokens
    return {"input_ids": full_ids, "attention_mask": [1]*len(full_ids), "labels": labels}

# Optional: also mask suppressed strings out of the loss target if they appear in train outputs
# (defensive — they should not be present in curated reflex pairs; logged if found).
def find_suppress_in_train():
    hits = []
    for i, r in enumerate(train_rows):
        for s in SUPPRESS_STRINGS:
            if s in r["output"] or s in r["instruction"]:
                hits.append((i, s))
    return hits
sup_hits = find_suppress_in_train()
print("suppress-string occurrences in TRAIN data:", sup_hits if sup_hits else "none (clean)")

ds = datasets.Dataset.from_list(train_rows).map(
    tokenize_with_mask, remove_columns=["instruction", "output", "category"]
)
print("tokenized examples:", len(ds), "| sample len:", len(ds[0]["input_ids"]))

# %%
# ============================ MODEL (4-bit QLoRA, fits T4 16GB x2) ============================
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb,
    device_map="auto",                              # shards across T4x2
    trust_remote_code=True,
    dtype=torch.float16,
)
model.config.use_cache = False
model.gradient_checkpointing_enable()

from peft import prepare_model_for_kbit_training
model = prepare_model_for_kbit_training(model)
lora_cfg = LoraConfig(
    r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
    target_modules=LORA_TARGETS, bias="none", task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()

# %%
# ============================ TRAIN ============================
collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# steps/epoch = ceil(392 / (per_device_bs * grad_accum * n_gpu_effective))
# device_map="auto" => single logical train loop; effective batch = PER_DEVICE_BS * GRAD_ACCUM.
eff_batch   = PER_DEVICE_BS * GRAD_ACCUM
steps_epoch = math.ceil(len(ds) / eff_batch)
total_steps = steps_epoch * EPOCHS
print(f"eff_batch={eff_batch} steps/epoch={steps_epoch} total_steps~={total_steps} save_every={SAVE_STEPS}")

args = TrainingArguments(
    output_dir=str(CKPT_DIR),
    per_device_train_batch_size=PER_DEVICE_BS,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=EPOCHS,
    learning_rate=LR,
    weight_decay=WEIGHT_DECAY,
    warmup_ratio=WARMUP_RATIO,
    lr_scheduler_type="cosine",
    logging_steps=5,
    save_steps=SAVE_STEPS,
    save_total_limit=4,
    fp16=True,
    optim="paged_adamw_8bit",
    report_to="none",
    gradient_checkpointing=True,
    seed=SEED,
)
trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator)
trainer.train()

# %%
# ============================ SAVE ADAPTER + ZIP (download immediately) ============================
ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
model.save_pretrained(str(ADAPTER_DIR))
tokenizer.save_pretrained(str(ADAPTER_DIR))
run_meta = {
    "experiment": "E7_targeted_guard_density (recipe=E2 verbatim lr=1e-4 all-linear; data 323->392: +40 P6_premise_guard +17 P6_disclaim_guard +12 P6_anchor; closes E6 invented-fab seams 20/24/33 source-endorsement + 34 disclaim-then-emit; falsifier: bait_fab(C)=0/n=32 at composite(C)>=5.5 -> GO else E8/DPO)",
    "base_model": BASE_MODEL, "method": "SFT-only LoRA", "cpt": False,
    "lora": {"r": LORA_R, "alpha": LORA_ALPHA, "dropout": LORA_DROPOUT, "targets": LORA_TARGETS},
    "lr": LR, "weight_decay": WEIGHT_DECAY, "epochs": EPOCHS,
    "per_device_bs": PER_DEVICE_BS, "grad_accum": GRAD_ACCUM, "max_len": MAX_LEN,
    "warmup_ratio": WARMUP_RATIO, "scheduler": "cosine", "seed": SEED,
    "n_train": len(train_rows), "total_steps": total_steps, "save_steps": SAVE_STEPS,
    "suppress_strings": SUPPRESS_STRINGS,
    "transformers": transformers.__version__, "torch": torch.__version__,
}
json.dump(run_meta, open(ADAPTER_DIR / "run_meta.json", "w"), indent=2, ensure_ascii=False)

with zipfile.ZipFile(ADAPTER_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in ADAPTER_DIR.rglob("*"):
        zf.write(p, p.relative_to(WORK))
print("Adapter zipped ->", ADAPTER_ZIP, f"({ADAPTER_ZIP.stat().st_size/1e6:.1f} MB)")
safe_download(ADAPTER_ZIP)   # E4 lesson: pull weights NOW, before the inference phase can crash

# %%
# ============================ INFERENCE HELPERS ============================
# Build suppressed token-id list for bad_words_ids (multiple encodings to be safe).
def build_bad_words_ids():
    bad = []
    for s in SUPPRESS_STRINGS:
        for variant in (s, " " + s):
            ids = tokenizer(variant, add_special_tokens=False)["input_ids"]
            if ids:
                bad.append(ids)
    # dedup
    seen, out = set(), []
    for ids in bad:
        k = tuple(ids)
        if k not in seen:
            seen.add(k); out.append(ids)
    return out
BAD_WORDS_IDS = build_bad_words_ids()
print("bad_words_ids:", BAD_WORDS_IDS)

# GOLD kernel system prompt (arm B / D) — compact R1-R18, from 03_GOLD_IDENTITY §3.
GOLD_KERNEL_PROMPT = (
    "You operate under the ONTO R1-R18 epistemic protocol. Apply on every answer:\n"
    "R1 QUANTIFY: numbers not words. R2 UNCERTAINTY: state it explicitly. "
    "R3 COUNTERARGUMENTS: steel-man the strongest opposing view. R4 SOURCES: cite or disclaim; no source -> say so. "
    "R5 EVIDENCE GRADE: I (RCT/proof) > II (observational) > III (opinion). R6 FALSIFIABILITY: state what would disprove the claim. "
    "R7 NO FABRICATION: never invent citations, statistics, or DOIs (immutable). "
    "R8 if unknown: bound it and reason, do not halt and do not fabricate. R13 address the underlying need. "
    "R17 cross-check consistency. R18 remove filler; keep only sourced claims, real numbers, and honest uncertainty.\n"
)

def generate(model_obj, question, system_prompt=None):
    if system_prompt:
        text = system_prompt + "\n" + format_example(question)
    else:
        text = format_example(question)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_LEN).to(model_obj.device)
    gen_kwargs = dict(
        max_new_tokens=GEN_MAX_NEW,
        do_sample=False,                            # temperature=0 deterministic
        num_beams=1,
        bad_words_ids=BAD_WORDS_IDS,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    with torch.no_grad():
        out = model_obj.generate(**inputs, **gen_kwargs)
    gen = out[0][inputs["input_ids"].shape[1]:]
    txt = tokenizer.decode(gen, skip_special_tokens=True)
    # belt-and-suspenders: strip any residual suppressed strings
    for s in SUPPRESS_STRINGS:
        txt = txt.replace(s, "")
    return txt.strip()

# %%
# ============================ ARM INFERENCE -> outputs.json ============================
# Arms (README_S1):
#   A: base, no prompt, no LoRA            (floor)
#   B: base, no LoRA, GOLD kernel prompt   (ceiling reference)
#   C: base + reflex-LoRA, no prompt       (TREATMENT)
#   D: base + reflex-LoRA + GOLD prompt    (optional interference check)
#
# To save VRAM/time we run arms in two model states:
#   state-1 = LoRA ENABLED  -> C, D
#   state-2 = LoRA DISABLED  -> A, B  (disable adapter on same loaded model)

# E4: held-out v1.3 (36, locked) + bait_v2_n32 (new provoke/recite/fake/wrong-premise baits)
# for n>=30 bait_fab(C) falsifiability (R6). Training recipe UNCHANGED; inference set expanded only.
def _maybe_find(fname):
    for root in (Path("/kaggle/input"), Path("/content"), Path(".")):
        if root.exists():
            hits = list(root.rglob(fname))
            if hits:
                return hits[0]
    return None
BAIT_V2_PATH = _maybe_find("bait_v2_n32.jsonl")
bait_rows = [json.loads(l) for l in open(BAIT_V2_PATH, encoding="utf-8")] if BAIT_V2_PATH else []
print("bait_v2 =", BAIT_V2_PATH, "| items:", len(bait_rows))
questions = [(r["id"], r["question"]) for r in held_rows] + [(r["id"], r["question"]) for r in bait_rows]
print("total inference questions:", len(questions), "(heldout", len(held_rows), "+ bait_v2", len(bait_rows), ")")

def run_arm(model_obj, system_prompt, tag):
    res = []
    for i, (qid, q) in enumerate(questions, 1):
        out = generate(model_obj, q, system_prompt)
        res.append({"id": qid, "output": out})
        if i % 6 == 0:
            print(f"  [{tag}] {i}/{len(questions)}")
    import gc
    torch.cuda.empty_cache(); gc.collect()      # prevent VRAM creep between arms (E2 crash mid-D)
    return res

outputs = {}

def flush_outputs():
    ordered = {k: outputs[k] for k in ["A", "B", "C", "D"] if k in outputs}
    json.dump(ordered, open(OUTPUTS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    safe_download(OUTPUTS_JSON)   # E4 lesson: a crash now costs at most the current arm

# state-1: LoRA active (C, then D)
model.eval()
print("ARM C (reflex-LoRA, no prompt)")
outputs["C"] = run_arm(model, None, "C")
flush_outputs()
if RUN_ARM_D:
    print("ARM D (reflex-LoRA + GOLD prompt)")
    outputs["D"] = run_arm(model, GOLD_KERNEL_PROMPT, "D")
    flush_outputs()

# state-2: disable adapter -> base behavior (A, B)
with model.disable_adapter():
    print("ARM A (base, no prompt, no LoRA)")
    outputs["A"] = run_arm(model, None, "A")
    flush_outputs()
    print("ARM B (base + GOLD prompt, no LoRA)")
    outputs["B"] = run_arm(model, GOLD_KERNEL_PROMPT, "B")
    flush_outputs()

# canonical arm order A,B,C,(D)
ordered = {k: outputs[k] for k in ["A", "B", "C"] + (["D"] if RUN_ARM_D else []) if k in outputs}
json.dump(ordered, open(OUTPUTS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Wrote", OUTPUTS_JSON, "| arms:", list(ordered.keys()), "| items/arm:", len(questions))

# %%
# ============================ LEAK GATE (run AFTER training, on arm C) ============================
# Compares arm C outputs against TRAIN outputs. Two detectors:
#   (1) exact-match: any continuous >=10-word train substring reproduced verbatim in a C output
#   (2) 7-gram overlap rate: |C 7-grams ∩ train 7-grams| / |C 7-grams| > 0.15
# Source corpus for comparison = all 392 train OUTPUT texts.
WORD_RE = re.compile(r"\w+", re.UNICODE)

def words(t):
    return WORD_RE.findall(t.lower())

def ngrams(tokens, n):
    return set(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)) if len(tokens) >= n else set()

# Precompute train resources
train_outputs = [r["output"] for r in train_rows]
train_word_seqs = [words(t) for t in train_outputs]
train_ngram_pool = set()
for seq in train_word_seqs:
    train_ngram_pool |= ngrams(seq, LEAK_NGRAM_N)

# Build a set of >=10-word continuous train phrases for exact-match (sliding windows, lowercased word-joined)
train_phrases = set()
for seq in train_word_seqs:
    for i in range(0, max(0, len(seq) - LEAK_EXACT_MIN_WORDS + 1)):
        train_phrases.add(" ".join(seq[i:i+LEAK_EXACT_MIN_WORDS]))

leak_lines = ["# Leak Report — Arm C vs Train (sft_reflex_392)\n",
              f"- exact-match: continuous >= {LEAK_EXACT_MIN_WORDS}-word train substring in C output",
              f"- n-gram: {LEAK_NGRAM_N}-gram overlap rate > {LEAK_NGRAM_THRESH}\n"]
any_leak = False
for item in outputs["C"]:
    seq = words(item["output"])
    # exact-match
    c_phrases = set(" ".join(seq[i:i+LEAK_EXACT_MIN_WORDS]) for i in range(0, max(0, len(seq)-LEAK_EXACT_MIN_WORDS+1)))
    exact_hits = sorted(c_phrases & train_phrases)
    # n-gram overlap
    c_ngrams = ngrams(seq, LEAK_NGRAM_N)
    overlap = len(c_ngrams & train_ngram_pool) / len(c_ngrams) if c_ngrams else 0.0
    leaked = bool(exact_hits) or overlap > LEAK_NGRAM_THRESH
    any_leak = any_leak or leaked
    flag = "🚨 LEAK" if leaked else "ok"
    leak_lines.append(f"## {item['id']} — {flag}")
    leak_lines.append(f"- 7-gram overlap rate: {overlap:.3f}")
    if exact_hits:
        leak_lines.append(f"- exact >= {LEAK_EXACT_MIN_WORDS}-word hits: {len(exact_hits)}")
        for h in exact_hits[:3]:
            leak_lines.append(f"    - \"{h}\"")
    leak_lines.append("")

leak_lines.insert(3, f"\n**VERDICT: {'LEAK DETECTED — investigate before trusting C composite' if any_leak else 'NO LEAK — C outputs are not verbatim recall'}**\n")
LEAK_REPORT.write_text("\n".join(leak_lines), encoding="utf-8")
print("Wrote", LEAK_REPORT, "| any_leak =", any_leak)

# %%
# ============================ DELIVERABLES SUMMARY ============================
print("\n=== S2 DELIVERABLES in /kaggle/working ===")
for p in [ADAPTER_ZIP, OUTPUTS_JSON, LEAK_REPORT]:
    print(("  OK  " if p.exists() else " MISS ") + str(p), f"{p.stat().st_size} bytes" if p.exists() else "")
print("\nNext: download outputs.json + leak_report.md + adapter_reflex_lora.zip.")
print("Bring outputs.json -> S3 (onto_eval.py).")

# Colab: push artifacts to the local machine automatically (sessions are ephemeral).
try:
    from google.colab import files as _gfiles  # noqa
    for p in [OUTPUTS_JSON, LEAK_REPORT, ADAPTER_ZIP]:
        if p.exists():
            print("Downloading to your PC:", p.name)
            _gfiles.download(str(p))
except ImportError:
    pass  # not Colab (Kaggle): files persist via Save & Run All version Output
