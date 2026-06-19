"""
run_r18_code_eval.py — Track D pipeline
=========================================
Generates bare + R18-prompted outputs via ollama (Qwen-coder:7b),
applies r18_code_v1.strip_filler to bare outputs,
produces blinded eval pairs for discipline comparison.

Requirements: ollama running locally, qwen2.5-coder:7b pulled.
CPU-only, ~5 min for 10 prompts.

Usage:
  python run_r18_code_eval.py

Output files (in ./r18_eval_out/):
  raw_outputs.jsonl       — all outputs (bare, code-filtered, prompted)
  eval_pairs.jsonl        — blinded A/B pairs for discipline eval
  eval_key.json           — which is which (DO NOT READ before judging)
  filler_stats.json       — per-prompt filler analysis
  summary.txt             — one-screen summary
"""

import json
import os
import random
import sys
import time
import hashlib
from pathlib import Path

import requests

# --- local import ---
from r18_code_v1 import strip_filler, score_filler, compute_bpw

# ============================================================
# CONFIG
# ============================================================

MODEL = "qwen2.5-coder:7b"
OLLAMA_URL = "http://localhost:11434/api/generate"
TEMP = 0.7
NUM_PREDICT = 512
OUT_DIR = Path("r18_eval_out")

# R18 system prompt — the PROMPTED arm's discipline instruction
R18_SYSTEM = (
    "Before delivering your response, self-splice:\n"
    "1. Remove all filler phrases (\"it's important to note\", \"overall\", \"in conclusion\", "
    "\"as we can see\", \"let me explain\").\n"
    "2. Remove all empty hedges and qualifiers (\"very\", \"really\", \"basically\", \"obviously\", "
    "\"certainly\", \"clearly\").\n"
    "3. Remove padding sentences that carry no factual content.\n"
    "4. Remove question restaters (\"Great question!\", \"That's an interesting question\").\n"
    "5. Remove closers (\"Hope this helps\", \"Let me know if you have questions\").\n"
    "6. Keep ONLY statements with: specific facts, numbers, mechanisms, explicit unknowns, "
    "or falsifiable claims.\n"
    "7. Do not restate the question. Start directly with content."
)

# 10 explanatory prompts — diverse domains, filler-prone
PROMPTS = [
    "Explain how mRNA vaccines work.",
    "What causes ocean acidification and why does it matter?",
    "How does proof-of-stake consensus work in blockchain?",
    "Explain the greenhouse effect and its role in climate change.",
    "What is CRISPR-Cas9 and how is it used in gene editing?",
    "How do convolutional neural networks recognize images?",
    "What causes antibiotic resistance and how does it spread?",
    "Explain quantum entanglement in simple terms.",
    "How does photosynthesis convert sunlight into chemical energy?",
    "What is dark energy and why do physicists think it exists?",
]


# ============================================================
# OLLAMA INTERFACE
# ============================================================

def generate(prompt: str, system: str = "", retries: int = 2) -> str:
    """Call ollama generate API. Returns response text."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": TEMP,
            "num_predict": NUM_PREDICT,
        },
    }
    if system:
        payload["system"] = system

    for attempt in range(retries + 1):
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
        except Exception as e:
            if attempt == retries:
                print(f"  [ERROR] ollama failed after {retries+1} attempts: {e}")
                return ""
            time.sleep(2)
    return ""


def check_ollama():
    """Verify ollama is running and model is available."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        found = any(MODEL.split(":")[0] in m for m in models)
        if not found:
            print(f"[FAIL] Model {MODEL} not found. Available: {models}")
            print(f"  Run: ollama pull {MODEL}")
            sys.exit(1)
        print(f"[OK] ollama running, {MODEL} available.")
    except Exception as e:
        print(f"[FAIL] Cannot reach ollama at localhost:11434: {e}")
        print("  Start ollama first: ollama serve")
        sys.exit(1)


# ============================================================
# PIPELINE
# ============================================================

def run_pipeline():
    check_ollama()
    OUT_DIR.mkdir(exist_ok=True)

    raw_outputs = []
    filler_stats = []
    eval_pairs = []
    eval_key = {}

    print(f"\n=== Track D: R18 code-filter vs R18 prompt ===")
    print(f"Model: {MODEL}, temp={TEMP}, prompts={len(PROMPTS)}\n")

    for i, prompt in enumerate(PROMPTS):
        pid = f"p{i:02d}"
        print(f"[{pid}] {prompt[:60]}...")

        # --- ARM 1: bare output (no system prompt) ---
        t0 = time.time()
        bare = generate(prompt, system="")
        t_bare = time.time() - t0
        print(f"  bare: {len(bare.split())}w, {t_bare:.1f}s")

        if not bare:
            print(f"  [SKIP] empty bare output")
            continue

        # --- CODE FILTER: strip filler from bare ---
        code_filtered = strip_filler(bare)
        filler_report = score_filler(bare)
        print(f"  filter: {filler_report['filler_stripped']} sentences stripped, "
              f"{filler_report['filler_trimmed']} trimmed, "
              f"{filler_report['qualifier_count']} qualifiers removed")
        print(f"  code-filtered: {len(code_filtered.split())}w "
              f"(was {filler_report['word_count']}w)")

        # --- ARM 2: R18-prompted output ---
        t0 = time.time()
        prompted = generate(prompt, system=R18_SYSTEM)
        t_prompted = time.time() - t0
        print(f"  prompted: {len(prompted.split())}w, {t_prompted:.1f}s")

        if not prompted:
            print(f"  [SKIP] empty prompted output")
            continue

        # --- BPW audit ---
        bpw_bare = compute_bpw(bare)
        bpw_filtered = compute_bpw(code_filtered)
        bpw_prompted = compute_bpw(prompted)
        print(f"  BPW: bare={bpw_bare:.1f}, filtered={bpw_filtered:.1f}, "
              f"prompted={bpw_prompted:.1f}")

        # --- Store raw ---
        raw_outputs.append({
            "id": pid,
            "prompt": prompt,
            "bare": bare,
            "code_filtered": code_filtered,
            "prompted": prompted,
            "bpw_bare": round(bpw_bare, 2),
            "bpw_filtered": round(bpw_filtered, 2),
            "bpw_prompted": round(bpw_prompted, 2),
        })

        filler_stats.append({
            "id": pid,
            "prompt": prompt,
            "word_count_bare": filler_report["word_count"],
            "word_count_filtered": len(code_filtered.split()),
            "word_count_prompted": len(prompted.split()),
            "filler_stripped": filler_report["filler_stripped"],
            "filler_trimmed": filler_report["filler_trimmed"],
            "qualifier_count": filler_report["qualifier_count"],
            "filler_ratio": round(filler_report["filler_ratio"], 3),
            "bpw_bare": round(bpw_bare, 2),
            "bpw_filtered": round(bpw_filtered, 2),
            "bpw_prompted": round(bpw_prompted, 2),
        })

        # --- Blinded eval pair (randomize A/B assignment) ---
        coin = random.random() < 0.5
        if coin:
            pair_a, pair_b = code_filtered, prompted
            key_a, key_b = "code_filtered", "prompted"
        else:
            pair_a, pair_b = prompted, code_filtered
            key_a, key_b = "prompted", "code_filtered"

        eval_pairs.append({
            "id": pid,
            "prompt": prompt,
            "output_A": pair_a,
            "output_B": pair_b,
        })
        eval_key[pid] = {"A": key_a, "B": key_b}

    # --- Save outputs ---
    with open(OUT_DIR / "raw_outputs.jsonl", "w", encoding="utf-8") as f:
        for item in raw_outputs:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(OUT_DIR / "eval_pairs.jsonl", "w", encoding="utf-8") as f:
        for item in eval_pairs:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(OUT_DIR / "eval_key.json", "w", encoding="utf-8") as f:
        json.dump(eval_key, f, indent=2)

    with open(OUT_DIR / "filler_stats.json", "w", encoding="utf-8") as f:
        json.dump(filler_stats, f, indent=2, ensure_ascii=False)

    # --- Summary ---
    n = len(raw_outputs)
    if n == 0:
        print("\n[FAIL] No outputs generated.")
        return

    avg_stripped = sum(s["filler_stripped"] for s in filler_stats) / n
    avg_trimmed = sum(s["filler_trimmed"] for s in filler_stats) / n
    avg_quals = sum(s["qualifier_count"] for s in filler_stats) / n
    avg_ratio = sum(s["filler_ratio"] for s in filler_stats) / n
    avg_wc_bare = sum(s["word_count_bare"] for s in filler_stats) / n
    avg_wc_filt = sum(s["word_count_filtered"] for s in filler_stats) / n
    avg_wc_prom = sum(s["word_count_prompted"] for s in filler_stats) / n

    summary = (
        f"=== Track D: R18 Code Filter — Generation Summary ===\n"
        f"Model: {MODEL}, temp={TEMP}, prompts={n}\n"
        f"\n"
        f"Filler detection (avg per output):\n"
        f"  Sentences stripped (pure filler): {avg_stripped:.1f}\n"
        f"  Sentences trimmed (opener removed): {avg_trimmed:.1f}\n"
        f"  Inline qualifiers removed: {avg_quals:.1f}\n"
        f"  Filler ratio (stripped/total): {avg_ratio:.2f}\n"
        f"\n"
        f"Word counts (avg):\n"
        f"  Bare: {avg_wc_bare:.0f}\n"
        f"  Code-filtered: {avg_wc_filt:.0f}\n"
        f"  R18-prompted: {avg_wc_prom:.0f}\n"
        f"\n"
        f"Output files in {OUT_DIR}/:\n"
        f"  eval_pairs.jsonl  — {n} blinded A/B pairs for discipline eval\n"
        f"  eval_key.json     — answer key (DO NOT read before judging)\n"
        f"  raw_outputs.jsonl — all three versions per prompt\n"
        f"  filler_stats.json — per-prompt filler analysis\n"
        f"\n"
        f"NEXT: paste eval_pairs.jsonl into Claude for blinded discipline eval.\n"
        f"Judge each pair on DISCIPLINE ONLY (filler/hedges/padding), NOT accuracy.\n"
        f"For each pair: A wins / B wins / tie.\n"
        f"Then unblind with eval_key.json and compute:\n"
        f"  code_effective_rate = (code_wins + 0.5*ties) / {n}\n"
        f"  PASS criterion: code_effective_rate >= 0.50\n"
    )

    with open(OUT_DIR / "summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\n{summary}")

    # --- MD5 of outputs ---
    for fname in ["raw_outputs.jsonl", "eval_pairs.jsonl", "eval_key.json", "filler_stats.json"]:
        fpath = OUT_DIR / fname
        h = hashlib.md5(fpath.read_bytes()).hexdigest()
        print(f"  md5 {fname}: {h}")


if __name__ == "__main__":
    run_pipeline()
