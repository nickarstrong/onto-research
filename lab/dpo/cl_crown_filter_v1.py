#!/usr/bin/env python3
"""
cl_crown_filter_v1.py — Track A Phase 2: BPW-as-filter probe

Hypothesis: R18 linguistic prompt is replaceable by BPW filtering.
Method: generate N=5 bare outputs per prompt, keep top-1 by lowest BPW,
        compare to 1 R18-prompted output via blinded human eval.

Usage:
  python cl_crown_filter_v1.py --generate                          # run
  python cl_crown_filter_v1.py --score filter_eval_blind_v1.md     # after judging

Requires: ollama running locally with the target model.
Pre-flight: ollama list | findstr gemma
"""

import argparse, gzip, json, os, random, re, sys, time
import urllib.request

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
DEFAULT_MODEL = "gemma4:e4b"
OLLAMA_URL = "http://localhost:11434/api/generate"
N_BARE = 5
TEMPERATURE = 0.7
NUM_PREDICT = 512

R18_SYSTEM = (
    "R18 Self-splicing: Before delivering your response, remove all empty "
    "hedges, filler phrases, unnecessary qualifications, disclaimers, and "
    "padding. Keep only content that carries a specific number, source, "
    "counterargument, explicit unknown, or falsifiable claim. If a sentence "
    "adds no information, delete it."
)

PROMPTS = [
    "What are the health benefits of intermittent fasting?",
    "Explain quantum entanglement.",
    "What caused the 2008 financial crisis?",
    "How does CRISPR gene editing work?",
    "What are the pros and cons of nuclear energy?",
    "Explain how machine learning differs from traditional programming.",
    "What is the evidence for dark matter?",
    "How do vaccines work?",
    "What are the main theories about the origin of consciousness?",
    "Explain the relationship between inflation and interest rates.",
]


# ──────────────────────────────────────────────
# BPW (validated Step 1: 20/20 pair discrimination)
# ──────────────────────────────────────────────
def bpw(text: str) -> float:
    """Bits per word via gzip compression. Lower = more compressed = less filler."""
    words = text.split()
    if not words:
        return 999.0
    compressed = gzip.compress(text.encode("utf-8"))
    return len(compressed) * 8 / len(words)


# ──────────────────────────────────────────────
# OLLAMA
# ──────────────────────────────────────────────
def ollama_generate(prompt: str, model: str, system: str = "") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_predict": NUM_PREDICT},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result.get("response", "").strip()


def preflight(model: str):
    """Check ollama is reachable and model loaded."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=10) as resp:
            tags = json.loads(resp.read().decode("utf-8"))
        names = [m["name"] for m in tags.get("models", [])]
        if not any(model in n for n in names):
            print(f"WARNING: '{model}' not found in ollama. Available: {names}")
            print(f"Check with: ollama list")
            sys.exit(1)
        print(f"OK: ollama up, model '{model}' available.")
    except Exception as e:
        print(f"ERROR: cannot reach ollama at localhost:11434 — {e}")
        sys.exit(1)


# ──────────────────────────────────────────────
# GENERATE
# ──────────────────────────────────────────────
def generate_all(model: str, outdir: str):
    preflight(model)
    os.makedirs(outdir, exist_ok=True)
    results = []
    t0 = time.time()

    for i, prompt in enumerate(PROMPTS):
        print(f"\n[{i+1}/{len(PROMPTS)}] {prompt[:60]}...")
        entry = {"id": i, "prompt": prompt, "bare": [], "prompted": None, "filtered": None}

        # ── N bare generations ──
        for j in range(N_BARE):
            print(f"  bare {j+1}/{N_BARE} ", end="", flush=True)
            text = ollama_generate(prompt, model, system="")
            score = bpw(text)
            wc = len(text.split())
            entry["bare"].append({"text": text, "bpw": round(score, 2), "words": wc})
            print(f"BPW={score:.1f}  {wc}w")

        # ── Pick top-1 (lowest BPW) ──
        best = min(entry["bare"], key=lambda x: x["bpw"])
        best_idx = entry["bare"].index(best)
        entry["filtered"] = {**best, "selected_idx": best_idx}
        print(f"  => filtered: idx={best_idx} BPW={best['bpw']}")

        # ── 1 R18-prompted generation ──
        print(f"  R18  ", end="", flush=True)
        text = ollama_generate(prompt, model, system=R18_SYSTEM)
        score = bpw(text)
        wc = len(text.split())
        entry["prompted"] = {"text": text, "bpw": round(score, 2), "words": wc}
        print(f"BPW={score:.1f}  {wc}w")

        results.append(entry)

    elapsed = time.time() - t0
    print(f"\nTotal: {elapsed:.0f}s ({elapsed/60:.1f}min)")

    # ── Save raw ──
    raw_path = os.path.join(outdir, "filter_raw_v1.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Raw data     -> {raw_path}")

    # ── Build blinded eval + key ──
    build_eval(results, outdir)

    # ── Summary table ──
    print_summary(results)


def build_eval(results, outdir):
    """Blinded eval sheet + answer key. Tommy does not see labels."""
    random.seed(42)  # reproducible blinding
    key = []
    lines = [
        "# BPW-FILTER EVAL (blinded)\n\n",
        "Judge each pair: which output is better disciplined?\n",
        "Criteria: information density, no filler/hedges, factual substance.\n",
        "NOT length alone — short garbage < long substance.\n",
        "Write **A**, **B**, or **TIE** on each Judgment line.\n\n",
    ]

    for r in results:
        pid = r["id"]
        flip = random.random() < 0.5
        if flip:
            a_src, b_src = "filtered", "prompted"
            a_text, b_text = r["filtered"]["text"], r["prompted"]["text"]
        else:
            a_src, b_src = "prompted", "filtered"
            a_text, b_text = r["prompted"]["text"], r["filtered"]["text"]

        key.append({"id": pid, "A": a_src, "B": b_src})
        lines.append(f"---\n\n## Prompt {pid+1}: {r['prompt']}\n\n")
        lines.append(f"### Output A\n\n{a_text}\n\n")
        lines.append(f"### Output B\n\n{b_text}\n\n")
        lines.append(f"**Judgment:** ___\n\n")

    eval_path = os.path.join(outdir, "filter_eval_blind_v1.md")
    with open(eval_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    key_path = os.path.join(outdir, "filter_key_v1.json")
    with open(key_path, "w", encoding="utf-8") as f:
        json.dump(key, f, indent=2)

    print(f"Blinded eval -> {eval_path}")
    print(f"Answer key   -> {key_path}  (DO NOT OPEN before judging)")


def print_summary(results):
    print("\n" + "=" * 72)
    print(f"  {'Prompt':<40} {'Filt BPW':>9} {'R18 BPW':>9} {'Δ':>7} {'Filt w':>7} {'R18 w':>6}")
    print("-" * 72)
    bpw_wins = 0
    for r in results:
        fb = r["filtered"]["bpw"]
        pb = r["prompted"]["bpw"]
        delta = fb - pb
        fw = r["filtered"]["words"]
        pw = r["prompted"]["words"]
        label = r["prompt"][:38]
        flag = "<=" if fb <= pb else "  "
        print(f"  {label:<40} {fb:9.1f} {pb:9.1f} {delta:+7.1f} {fw:7} {pw:6} {flag}")
        if fb <= pb:
            bpw_wins += 1
    print("-" * 72)
    print(f"  Filtered BPW <= Prompted BPW: {bpw_wins}/{len(results)}")
    print(f"  (Lower BPW = more compressed = less filler)")
    print(f"  BPW spread in bare N={N_BARE}:")
    for r in results:
        bpws = [b["bpw"] for b in r["bare"]]
        spread = max(bpws) - min(bpws)
        print(f"    P{r['id']+1}: min={min(bpws):.1f} max={max(bpws):.1f} spread={spread:.1f}")
    print("=" * 72)


# ──────────────────────────────────────────────
# SCORE (after human eval)
# ──────────────────────────────────────────────
def score_eval(eval_path: str):
    key_path = os.path.join(os.path.dirname(eval_path) or ".", "filter_key_v1.json")
    if not os.path.exists(key_path):
        print(f"ERROR: key not found at {key_path}")
        sys.exit(1)

    with open(key_path, "r") as f:
        key = json.load(f)

    with open(eval_path, "r", encoding="utf-8") as f:
        content = f.read()

    judgments = re.findall(r"\*\*Judgment:\*\*\s*(A|B|TIE|a|b|tie)", content)
    if len(judgments) != len(key):
        print(f"ERROR: {len(judgments)} judgments found, expected {len(key)}.")
        print("Fill every ___ with A, B, or TIE.")
        sys.exit(1)

    fw, pw, ties = 0, 0, 0
    print("\n" + "=" * 50)
    print("UNBLINDED RESULTS")
    print("-" * 50)
    for k, j in zip(key, judgments):
        j = j.upper()
        if j == "TIE":
            winner = "tie"
            ties += 1
        else:
            winner = k[j]
            if winner == "filtered":
                fw += 1
            else:
                pw += 1
        print(f"  Prompt {k['id']+1}: judge={j} -> {winner}")

    print("-" * 50)
    print(f"  Filtered wins : {fw}")
    print(f"  Prompted wins : {pw}")
    print(f"  Ties          : {ties}")
    total = len(key)
    eff = (fw + ties * 0.5) / total
    print(f"  Effective rate: {eff:.2f} (filtered_wins + 0.5*ties / total)")
    print(f"\n  VERDICT: ", end="")
    if eff >= 0.7:
        print("PASS — BPW filter >= R18 prompt -> R18 REPLACEABLE")
    elif eff >= 0.5:
        print("INCONCLUSIVE — competitive but not dominant")
    else:
        print("FAIL — R18 prompt > BPW filter -> R18 NOT replaceable by BPW alone")
    print(f"  FALSIFIER: eff < 0.5 on N>=10 blinded pairs = filter inferior to prompt")
    print("=" * 50)


# ──────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="CL Crown Phase 2: BPW-as-filter")
    p.add_argument("--generate", action="store_true")
    p.add_argument("--score", type=str, metavar="EVAL.md")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--outdir", default=".")
    a = p.parse_args()

    if a.generate:
        generate_all(a.model, a.outdir)
    elif a.score:
        score_eval(a.score)
    else:
        p.print_help()
