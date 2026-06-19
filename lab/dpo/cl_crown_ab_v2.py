#!/usr/bin/env python3
"""
CL Crown A/B Probe v2 вЂ” Track A, Session v187
===============================================
Generate outputs from a local model (via ollama) under two conditions:
  A: R18 self-splicing instruction in system prompt
  B: Bare system prompt (no R18)

Score both with CL2 math metric + R18 regex.
Compute correlation + per-sample delta.

Usage:
  # Step 0: install model (once)
  ollama pull gemma4:12b

  # Step 1: run probe
  python cl_crown_ab_v2.py --model gemma4:12b --prompts data/ordinary_prompts_v7.jsonl --n 10

  # Other models:
  python cl_crown_ab_v2.py --model gemma4:e4b ...
  python cl_crown_ab_v2.py --model qwen2.5:7b ...

Dependencies: Python 3.8+ stdlib only. Ollama running on localhost:11434.
"""

import argparse
import gzip
import json
import math
import re
import sys
import time
import urllib.request
import urllib.error
from collections import Counter
from pathlib import Path

# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
# CONFIG
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

OLLAMA_URL = "http://localhost:11434/api/generate"

R18_SYSTEM_PROMPT = """You are a disciplined AI assistant. Before delivering any response,
apply self-splicing (R18): remove all empty hedges, filler phrases, RLHF-politeness,
unnecessary qualifiers, and vacuous transitions. Keep ONLY content that contains:
a source, a number, a counterargument, an explicit statement of uncertainty, or
a falsifiability condition. If a sentence adds no information, delete it."""

BARE_SYSTEM_PROMPT = "You are a helpful assistant."

GENERATION_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 4096,
    "seed": 42,
}


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
# OLLAMA CLIENT (stdlib only)
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

def ollama_generate(model: str, prompt: str, system: str) -> tuple[str, float]:
    """Call ollama API. Returns (response_text, elapsed_seconds)."""
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": GENERATION_PARAMS,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"ERROR: cannot reach ollama at {OLLAMA_URL}: {e}", file=sys.stderr)
        print("Is ollama running? Start with: ollama serve", file=sys.stderr)
        sys.exit(1)
    elapsed = time.time() - t0

    return result.get("response", ""), elapsed


def check_ollama(model: str):
    """Verify ollama is running and model is available."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
    except Exception as e:
        print(f"ERROR: ollama not reachable: {e}", file=sys.stderr)
        print(f"Start ollama: ollama serve", file=sys.stderr)
        sys.exit(1)

    # Check model (handle tag variants: "gemma4:12b" vs "gemma4:12b-latest")
    model_base = model.split(":")[0] if ":" in model else model
    found = any(model_base in m for m in models)
    if not found:
        print(f"WARNING: model '{model}' not found in ollama.", file=sys.stderr)
        print(f"Available: {models}", file=sys.stderr)
        print(f"Pull with: ollama pull {model}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] ollama running, model '{model}' available")


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
# SCORERS (from cl_crown_probe_v1.py)
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

HEDGE_PATTERNS = [
    r"\bit(?:'s| is) (?:important|worth|interesting) to (?:note|mention|consider|highlight|point out) that\b",
    r"\bas (?:mentioned|noted|discussed|stated) (?:earlier|above|previously|before)\b",
    r"\bit(?:'s| is) (?:widely|generally|commonly|well) (?:known|accepted|recognized|understood)\b",
    r"\bneedless to say\b", r"\bof course\b", r"\bobviously\b", r"\bclearly\b",
    r"\bundoubtedly\b", r"\bwithout a doubt\b",
    r"\bfurthermore\b", r"\bmoreover\b", r"\badditionally\b", r"\bin addition(?:ally)?\b",
    r"\bthat (?:being )?said\b", r"\bhaving said that\b", r"\bin any case\b",
    r"\bat the end of the day\b", r"\bin conclusion\b", r"\bto summarize\b", r"\bin summary\b",
    r"\bto some (?:extent|degree)\b", r"\bin some (?:cases|instances|situations)\b",
    r"\bin certain (?:cases|circumstances|situations)\b",
    r"\bit (?:could|might|may) be (?:argued|said|suggested) that\b",
    r"\bone could (?:argue|say|suggest) that\b",
    r"\bpotentially\b", r"\bconceivably\b",
    r"\bI(?:'d| would) be happy to\b", r"\bI(?:'d| would) be glad to\b",
    r"\bgreat question\b",
    r"\bthat(?:'s| is) (?:a |an )?(?:great|excellent|fantastic|wonderful|interesting) question\b",
    r"\bthank you for (?:asking|sharing|your|the)\b",
    r"\bI hope (?:this|that) helps\b", r"\blet me know if you (?:have|need)\b",
    r"\bfeel free to\b", r"\bdon(?:'t| not) hesitate to\b",
    r"\bI(?:'m| am) here to help\b", r"\bhappy to help\b",
    r"\bcertainly[!.]?\s", r"\babsolutely[!.]?\s", r"\bsure(?:ly)?[!,.]?\s",
    r"\bdefinitely[!.]?\s",
    r"\bvery\b", r"\breally\b", r"\bextremely\b", r"\bincredibly\b",
    r"\bremarkably\b", r"\bsignificantly\b", r"\bsubstantially\b",
    r"\bbasically\b", r"\bessentially\b", r"\bfundamentally\b",
    r"\bultimately\b", r"\bliterally\b", r"\bactually\b",
]
_HEDGE_RES = [re.compile(p, re.IGNORECASE) for p in HEDGE_PATTERNS]


def r18_score(text: str) -> dict:
    words = text.split()
    wc = len(words) or 1
    hc = sum(len(pat.findall(text)) for pat in _HEDGE_RES)
    return {"hedge_count": hc, "hedge_density": hc / wc, "word_count": wc}


def gzip_ratio(text: str) -> float:
    raw = text.encode("utf-8")
    if len(raw) == 0:
        return 1.0
    return len(gzip.compress(raw, compresslevel=9)) / len(raw)


def bigram_entropy(text: str) -> float:
    t = text.lower()
    if len(t) < 2:
        return 0.0
    bgs = [t[i:i+2] for i in range(len(t) - 1)]
    counts = Counter(bgs)
    total = len(bgs)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())


def type_token_ratio(text: str) -> float:
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def cl2_score(text: str) -> dict:
    gz = gzip_ratio(text)
    ent = bigram_entropy(text)
    ttr = type_token_ratio(text)

    tlen = len(text) if text else 100
    if tlen < 500:
        gz_lo, gz_hi = 0.60, 0.90
    elif tlen < 2000:
        gz_lo, gz_hi = 0.30, 0.75
    else:
        gz_lo, gz_hi = 0.15, 0.60
    gz_n = max(0.0, min(1.0, (gz - gz_lo) / (gz_hi - gz_lo)))
    ent_n = max(0.0, min(1.0, (ent - 5.5) / (8.5 - 5.5)))
    ttr_n = max(0.0, min(1.0, (ttr - 0.3) / (1.0 - 0.3)))
    composite = 0.40 * gz_n + 0.40 * ent_n + 0.20 * ttr_n

    return {
        "gzip_ratio": round(gz, 4), "bigram_entropy": round(ent, 4),
        "ttr": round(ttr, 4), "composite": round(composite, 4),
    }


def pearson_r(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs)/n, sum(ys)/n
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    num = sum(a*b for a, b in zip(dx, dy))
    den = math.sqrt(sum(a*a for a in dx)) * math.sqrt(sum(b*b for b in dy))
    return num / den if den > 0 else float("nan")


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
# DATA
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

PROMPT_FIELDS = ["prompt", "instruction", "input", "question", "text", "query"]


def load_prompts(path: str, n: int) -> list[str]:
    p = Path(path)
    if not p.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)
    prompts = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        for f in PROMPT_FIELDS:
            if f in rec and isinstance(rec[f], str) and len(rec[f]) > 5:
                prompts.append(rec[f])
                break
        if len(prompts) >= n:
            break
    if not prompts:
        print(f"ERROR: no prompts extracted from {path}", file=sys.stderr)
        sys.exit(1)
    return prompts


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
# MAIN
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

def main():
    ap = argparse.ArgumentParser(description="CL Crown A/B Probe v2")
    ap.add_argument("--model", required=True, help="Ollama model name (e.g. gemma4:12b)")
    ap.add_argument("--prompts", required=True, help="JSONL with prompts")
    ap.add_argument("--n", type=int, default=10, help="Number of prompts to test")
    ap.add_argument("--out", default=None, help="Output JSON path")
    args = ap.parse_args()

    check_ollama(args.model)
    prompts = load_prompts(args.prompts, args.n)
    n = len(prompts)
    print(f"[DATA] {n} prompts loaded from {args.prompts}")
    print(f"[MODEL] {args.model}")
    print(f"[PLAN] {n} prompts Г— 2 conditions = {n*2} generations")
    print()

    results = []

    for i, prompt in enumerate(prompts):
        print(f"[{i+1}/{n}] {prompt[:60]}...")

        # Condition A: R18 in system prompt
        text_a, t_a = ollama_generate(args.model, prompt, R18_SYSTEM_PROMPT)
        r18_a = r18_score(text_a)
        cl2_a = cl2_score(text_a)
        print(f"  A (R18):  {len(text_a):4d} chars, {t_a:.1f}s  "
              f"hedge={r18_a['hedge_count']}  cl2={cl2_a['composite']:.3f}")

        # Condition B: bare system prompt
        text_b, t_b = ollama_generate(args.model, prompt, BARE_SYSTEM_PROMPT)
        r18_b = r18_score(text_b)
        cl2_b = cl2_score(text_b)
        print(f"  B (bare): {len(text_b):4d} chars, {t_b:.1f}s  "
              f"hedge={r18_b['hedge_count']}  cl2={cl2_b['composite']:.3f}")

        # Delta
        d_hedge = r18_b["hedge_density"] - r18_a["hedge_density"]
        d_cl2 = cl2_a["composite"] - cl2_b["composite"]
        print(f"  О” hedge_density (B-A): {d_hedge:+.4f}  "
              f"О” CL2 (A-B): {d_cl2:+.4f}")
        print()

        results.append({
            "idx": i,
            "prompt": prompt[:100],
            "A_r18_hedge": r18_a["hedge_density"],
            "A_cl2": cl2_a["composite"],
            "A_latency": round(t_a, 2),
            "A_len": len(text_a),
            "B_r18_hedge": r18_b["hedge_density"],
            "B_cl2": cl2_b["composite"],
            "B_latency": round(t_b, 2),
            "B_len": len(text_b),
            "delta_hedge": round(d_hedge, 4),
            "delta_cl2": round(d_cl2, 4),
            "text_A": text_a,
            "text_B": text_b,
        })

    # в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
    # ANALYSIS
    # в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

    print("=" * 60)
    print("CL CROWN A/B PROBE v2 вЂ” RESULTS")
    print("=" * 60)
    print(f"Model: {args.model}  |  N={n}")
    print()

    # 1. Does R18 prompt reduce hedges?
    hedges_a = [r["A_r18_hedge"] for r in results]
    hedges_b = [r["B_r18_hedge"] for r in results]
    mean_ha = sum(hedges_a) / n
    mean_hb = sum(hedges_b) / n
    print(f"  R18 hedge_density:  A (R18 prompt) = {mean_ha:.4f}  "
          f"B (bare) = {mean_hb:.4f}  О” = {mean_hb - mean_ha:+.4f}")

    # 2. Does CL2 see the same difference?
    cl2s_a = [r["A_cl2"] for r in results]
    cl2s_b = [r["B_cl2"] for r in results]
    mean_ca = sum(cl2s_a) / n
    mean_cb = sum(cl2s_b) / n
    print(f"  CL2 composite:      A (R18 prompt) = {mean_ca:.4f}  "
          f"B (bare) = {mean_cb:.4f}  О” = {mean_ca - mean_cb:+.4f}")
    print()

    # 3. Correlation between hedge reduction and CL2 improvement
    deltas_hedge = [r["delta_hedge"] for r in results]
    deltas_cl2 = [r["delta_cl2"] for r in results]
    r_delta = pearson_r(deltas_hedge, deltas_cl2)
    print(f"  Correlation (О”_hedge vs О”_CL2): r = {r_delta:+.4f}")

    # 4. Cross-condition correlation
    all_hedges = hedges_a + hedges_b
    all_cl2 = cl2s_a + cl2s_b
    r_cross = pearson_r(all_hedges, all_cl2)
    print(f"  Cross-condition correlation:     r = {r_cross:+.4f}")
    print()

    # 5. Latency comparison
    lat_a = sum(r["A_latency"] for r in results) / n
    lat_b = sum(r["B_latency"] for r in results) / n
    print(f"  Latency:  A = {lat_a:.1f}s  B = {lat_b:.1f}s  "
          f"(R18 prompt {'slower' if lat_a > lat_b else 'faster'} by {abs(lat_a-lat_b):.1f}s)")
    print()

    # Verdict
    abs_r = abs(r_cross)
    if mean_hb > mean_ha and abs_r > 0.3:
        verdict = "PASS: R18 prompt reduces hedges AND CL2 detects it. Math constraint viable."
    elif mean_hb <= mean_ha:
        verdict = "INCONCLUSIVE: R18 prompt did not reduce hedges (model already clean?)."
    elif abs_r <= 0.3:
        verdict = "PARTIAL: R18 reduces hedges but CL2 doesn't track it. CL2 needs tuning."
    else:
        verdict = "CHECK: unexpected pattern, review per-sample data."

    print(f"  VERDICT: {verdict}")
    print()

    # Per-sample summary
    print("-" * 60)
    print(f"{'#':>3}  {'О”_hedge':>8}  {'О”_CL2':>8}  {'h_A':>4} {'h_B':>4}  "
          f"{'CL2_A':>6} {'CL2_B':>6}  prompt")
    for r in results:
        print(f"{r['idx']:3d}  {r['delta_hedge']:+8.4f}  {r['delta_cl2']:+8.4f}  "
              f"{r['A_r18_hedge']:.3f} {r['B_r18_hedge']:.3f}  "  # hedges are small, .3f ok
              f"{r['A_cl2']:6.3f} {r['B_cl2']:6.3f}  "
              f"{r['prompt'][:50]}")
    print()

    # Save
    out_path = args.out or f"cl_ab_{args.model.replace(':', '_')}_{n}.json"
    out_data = {
        "probe": "cl_crown_ab_v2",
        "model": args.model,
        "n": n,
        "mean_hedge_A": round(mean_ha, 4),
        "mean_hedge_B": round(mean_hb, 4),
        "mean_cl2_A": round(mean_ca, 4),
        "mean_cl2_B": round(mean_cb, 4),
        "r_delta": round(r_delta, 4) if not math.isnan(r_delta) else None,
        "r_cross": round(r_cross, 4) if not math.isnan(r_cross) else None,
        "latency_A": round(lat_a, 2),
        "latency_B": round(lat_b, 2),
        "verdict": verdict,
        "samples": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] {out_path}")


if __name__ == "__main__":
    main()


