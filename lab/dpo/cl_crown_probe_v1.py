#!/usr/bin/env python3
"""
CL Crown Probe v1 — Track A, Session v187
==========================================
Question: does a MATHEMATICAL metric (CL2) capture the same signal as a
          LINGUISTIC rule (R18 self-splicing) scored by regex?

Method:
  1. Load existing model outputs (any JSONL with a text field)
  2. Score each output with R18_regex (hedge/filler pattern count)
  3. Score each output with CL2_math (compression + entropy + lexical density)
  4. Pearson correlation between the two
  5. One number: r

Interpretation:
  |r| > 0.7  → CL2 captures what R18 captures → math constraint viable
  |r| 0.3-0.7 → partial overlap → CL2 needs tuning but direction valid
  |r| < 0.3  → CL2 measures something else → hypothesis needs revision

Usage:
  python cl_crown_probe_v1.py <jsonl_file> [--field response]

Expects JSONL where each line has a text field (auto-detects: response, output,
chosen, text, completion, answer). Override with --field.

Dependencies: Python 3.8+ stdlib only. No pip installs.
"""

import argparse
import gzip
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────
# R18 REGEX SCORER — linguistic pattern matching
# R18 = "Self-splicing: remove empty hedges before delivery.
#         Keep only content with source, number, counter,
#         explicit unknown, or falsifier."
# ─────────────────────────────────────────────────────────────────────

# Hedge / filler patterns that R18 should remove
HEDGE_PATTERNS = [
    # Epistemic hedges (empty confidence markers)
    r"\bit(?:'s| is) (?:important|worth|interesting) to (?:note|mention|consider|highlight|point out) that\b",
    r"\bas (?:mentioned|noted|discussed|stated) (?:earlier|above|previously|before)\b",
    r"\bit(?:'s| is) (?:widely|generally|commonly|well) (?:known|accepted|recognized|understood)\b",
    r"\bneedless to say\b",
    r"\bof course\b",
    r"\bobviously\b",
    r"\bclearly\b",
    r"\bundoubtedly\b",
    r"\bwithout a doubt\b",

    # Filler transitions (no information content)
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\badditionally\b",
    r"\bin addition(?:ally)?\b",
    r"\bthat (?:being )?said\b",
    r"\bhaving said that\b",
    r"\bwith that (?:being )?said\b",
    r"\bin any case\b",
    r"\bin any event\b",
    r"\ball in all\b",
    r"\bat the end of the day\b",
    r"\bin conclusion\b",
    r"\bto summarize\b",
    r"\bto sum up\b",
    r"\bin summary\b",

    # Empty qualifiers (hedge without content)
    r"\bto some (?:extent|degree)\b",
    r"\bin some (?:cases|instances|situations)\b",
    r"\bin certain (?:cases|circumstances|situations)\b",
    r"\bit (?:could|might|may) be (?:argued|said|suggested) that\b",
    r"\bone could (?:argue|say|suggest) that\b",
    r"\bit(?:'s| is) (?:possible|conceivable|plausible) that\b",
    r"\bpotentially\b",
    r"\bconceivably\b",

    # RLHF-typical filler
    r"\bI(?:'d| would) be happy to\b",
    r"\bI(?:'d| would) be glad to\b",
    r"\bgreat question\b",
    r"\bthat(?:'s| is) (?:a |an )?(?:great|excellent|fantastic|wonderful|interesting) question\b",
    r"\bthank you for (?:asking|sharing|your|the)\b",
    r"\bI hope (?:this|that) helps\b",
    r"\blet me know if you (?:have|need)\b",
    r"\bfeel free to\b",
    r"\bdon(?:'t| not) hesitate to\b",
    r"\bI(?:'m| am) here to help\b",
    r"\bhappy to help\b",
    r"\bplease (?:don't|do not) hesitate\b",

    # Empty preambles
    r"\bcertainly[!.]?\s",
    r"\babsolutely[!.]?\s",
    r"\bsure(?:ly)?[!,.]?\s",
    r"\bof course[!,.]?\s",
    r"\bdefinitely[!.]?\s",

    # Vacuous intensifiers
    r"\bvery\b",
    r"\breally\b",
    r"\bextremely\b",
    r"\bincredibly\b",
    r"\bremarkably\b",
    r"\bsignificantly\b",
    r"\bsubstantially\b",
    r"\btremendously\b",
    r"\bprofoundly\b",

    # Discourse markers with no content
    r"\bbasically\b",
    r"\bessentially\b",
    r"\bfundamentally\b",
    r"\bultimately\b",
    r"\bliterally\b",
    r"\bactually\b",
]

# Compile for speed
_HEDGE_RES = [re.compile(p, re.IGNORECASE) for p in HEDGE_PATTERNS]


def r18_regex_score(text: str) -> dict:
    """Score text by R18 regex: count hedge/filler occurrences.

    Returns dict with:
      hedge_count: total hedge pattern matches
      word_count: total words
      sentence_count: total sentences
      hedge_density: hedge_count / word_count  (higher = worse, more filler)
    """
    words = text.split()
    word_count = len(words) or 1
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = len(sentences) or 1

    hedge_count = 0
    matched_patterns = []
    for pat in _HEDGE_RES:
        matches = pat.findall(text)
        if matches:
            hedge_count += len(matches)
            matched_patterns.append((pat.pattern[:40], len(matches)))

    hedge_density = hedge_count / word_count

    return {
        "hedge_count": hedge_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "hedge_density": hedge_density,
        "matched_patterns": matched_patterns,
    }


# ─────────────────────────────────────────────────────────────────────
# CL2 MATH SCORER — information-theoretic measurement
# CL2 = "Enforce optimal compression. Penalize verbosity,
#         RLHF-politeness, filler. Force maximum information density."
# Implementation: gzip compression ratio + character entropy +
#                 type-token ratio (lexical diversity)
# ─────────────────────────────────────────────────────────────────────


def gzip_compression_ratio(text: str) -> float:
    """Ratio of compressed to raw size. Lower = denser (less redundant)."""
    raw = text.encode("utf-8")
    if len(raw) == 0:
        return 1.0
    compressed = gzip.compress(raw, compresslevel=9)
    return len(compressed) / len(raw)


def char_bigram_entropy(text: str) -> float:
    """Shannon entropy of character bigrams. Higher = more information."""
    text_lower = text.lower()
    if len(text_lower) < 2:
        return 0.0
    bigrams = [text_lower[i:i+2] for i in range(len(text_lower) - 1)]
    counts = Counter(bigrams)
    total = len(bigrams)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def type_token_ratio(text: str) -> float:
    """Unique words / total words. Higher = more diverse vocabulary."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def cl2_math_score(text: str) -> dict:
    """Score text by CL2 math metric: information density.

    Returns dict with:
      gzip_ratio: compressed/raw size (lower = denser, better)
      bigram_entropy: char bigram Shannon entropy (higher = more info)
      ttr: type-token ratio (higher = more diverse)
      cl2_composite: combined score (higher = better information density)
    """
    gz = gzip_compression_ratio(text)
    ent = char_bigram_entropy(text)
    ttr = type_token_ratio(text)

    # Normalize to [0, 1] range where higher = better (denser text)
    # gzip_ratio: short texts 0.60-0.90, long texts 0.15-0.60
    #   invert: density = 1 - normalized_gzip (lower gzip = more compressible = filler)
    #   adaptive range based on text length
    text_len = len(text) if text else 100
    if text_len < 500:
        gz_lo, gz_hi = 0.60, 0.90  # short text range
    elif text_len < 2000:
        gz_lo, gz_hi = 0.30, 0.75  # medium text range
    else:
        gz_lo, gz_hi = 0.15, 0.60  # long text range
    gz_norm = max(0.0, min(1.0, (gz - gz_lo) / (gz_hi - gz_lo)))

    # bigram_entropy: typical range 5.5-8.5 for English
    ent_norm = max(0.0, min(1.0, (ent - 5.5) / (8.5 - 5.5)))

    # ttr: typical range 0.3-1.0 (short texts naturally higher)
    ttr_norm = max(0.0, min(1.0, (ttr - 0.3) / (1.0 - 0.3)))

    # Composite: weighted arithmetic mean (robust to one weak component)
    # gzip and entropy get more weight (stronger signal per synthetic validation)
    cl2_composite = 0.40 * gz_norm + 0.40 * ent_norm + 0.20 * ttr_norm

    return {
        "gzip_ratio": round(gz, 4),
        "bigram_entropy": round(ent, 4),
        "ttr": round(ttr, 4),
        "gz_norm": round(gz_norm, 4),
        "ent_norm": round(ent_norm, 4),
        "ttr_norm": round(ttr_norm, 4),
        "cl2_composite": round(cl2_composite, 4),
    }


# ─────────────────────────────────────────────────────────────────────
# CORRELATION
# ─────────────────────────────────────────────────────────────────────


def pearson_r(xs: list, ys: list) -> float:
    """Pearson correlation coefficient. Returns float in [-1, 1]."""
    n = len(xs)
    if n < 3:
        return float("nan")
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    num = sum(a * b for a, b in zip(dx, dy))
    den_x = math.sqrt(sum(a * a for a in dx))
    den_y = math.sqrt(sum(b * b for b in dy))
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)


# ─────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────

# Auto-detect field names for text extraction
TEXT_FIELDS = ["response", "output", "chosen", "text", "completion",
               "answer", "content", "generated", "assistant"]


def extract_text(record: dict, field: str | None = None) -> str | None:
    """Extract text from a JSONL record, auto-detecting the field."""
    if field and field in record:
        val = record[field]
        if isinstance(val, str):
            return val
        if isinstance(val, list):
            # Chat format: list of dicts with "content"
            return " ".join(
                m.get("content", "") for m in val
                if isinstance(m, dict) and m.get("role") in ("assistant", "model")
            )
    # Auto-detect
    for f in TEXT_FIELDS:
        if f in record:
            val = record[f]
            if isinstance(val, str) and len(val) > 20:
                return val
    # Try nested: conversations, messages
    for container in ("conversations", "messages"):
        if container in record and isinstance(record[container], list):
            parts = []
            for msg in record[container]:
                if isinstance(msg, dict) and msg.get("role", msg.get("from", "")) in (
                    "assistant", "model", "gpt"
                ):
                    parts.append(msg.get("content", msg.get("value", "")))
            if parts:
                return " ".join(parts)
    return None


def load_texts(path: str, field: str | None = None) -> list[str]:
    """Load texts from JSONL or JSON file."""
    texts = []
    p = Path(path)
    if not p.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    raw = p.read_text(encoding="utf-8", errors="replace")

    # Try JSONL first
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if lines and lines[0].startswith("{"):
        for i, line in enumerate(lines):
            try:
                rec = json.loads(line)
                t = extract_text(rec, field)
                if t and len(t) > 20:
                    texts.append(t)
            except json.JSONDecodeError:
                continue
    else:
        # Try as JSON array
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                for rec in data:
                    if isinstance(rec, dict):
                        t = extract_text(rec, field)
                        if t and len(t) > 20:
                            texts.append(t)
            elif isinstance(data, dict):
                # Maybe outputs_E9.json format: key -> output
                for k, v in data.items():
                    if isinstance(v, str) and len(v) > 20:
                        texts.append(v)
                    elif isinstance(v, dict):
                        t = extract_text(v, field)
                        if t and len(t) > 20:
                            texts.append(t)
        except json.JSONDecodeError:
            print(f"ERROR: cannot parse {path} as JSONL or JSON", file=sys.stderr)
            sys.exit(1)

    return texts


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CL Crown Probe v1: R18 regex vs CL2 math correlation"
    )
    parser.add_argument("file", help="JSONL or JSON file with model outputs")
    parser.add_argument("--field", default=None, help="Field name for text extraction")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-sample scores")
    parser.add_argument("--top", type=int, default=5, help="Show top N outliers")
    args = parser.parse_args()

    texts = load_texts(args.file, args.field)
    if len(texts) < 5:
        print(f"ERROR: only {len(texts)} texts extracted (need ≥5). "
              f"Check file format or --field.", file=sys.stderr)
        sys.exit(1)

    print(f"[DATA] Loaded {len(texts)} outputs from {args.file}")
    print(f"[DATA] Avg length: {sum(len(t) for t in texts)/len(texts):.0f} chars")
    print()

    # Score all outputs
    r18_scores = []
    cl2_scores = []
    details = []

    for i, text in enumerate(texts):
        r18 = r18_regex_score(text)
        cl2 = cl2_math_score(text)

        r18_scores.append(r18["hedge_density"])
        cl2_scores.append(cl2["cl2_composite"])

        details.append({
            "idx": i,
            "len": len(text),
            "r18_hedge_density": r18["hedge_density"],
            "r18_hedge_count": r18["hedge_count"],
            "cl2_composite": cl2["cl2_composite"],
            "cl2_gzip": cl2["gzip_ratio"],
            "cl2_entropy": cl2["bigram_entropy"],
            "cl2_ttr": cl2["ttr"],
            "preview": text[:80].replace("\n", " "),
        })

    # Compute correlation
    # Note: R18 hedge_density is HIGHER = WORSE (more filler)
    # CL2 composite is HIGHER = BETTER (more dense)
    # So we expect NEGATIVE correlation if both measure the same thing
    r = pearson_r(r18_scores, cl2_scores)

    # Also compute correlation with inverted R18 (for interpretability)
    r18_inverted = [1.0 - s for s in r18_scores]
    r_inv = pearson_r(r18_inverted, cl2_scores)

    # Summary stats
    print("=" * 60)
    print("CL CROWN PROBE v1 — RESULTS")
    print("=" * 60)
    print()
    print(f"  R18_regex (hedge_density) vs CL2_math (composite):")
    print(f"  Pearson r = {r:+.4f}")
    print(f"  (inverted: r = {r_inv:+.4f})")
    print()
    print(f"  R18 hedge_density:  mean={sum(r18_scores)/len(r18_scores):.4f}  "
          f"std={stdev(r18_scores):.4f}")
    print(f"  CL2 composite:     mean={sum(cl2_scores)/len(cl2_scores):.4f}  "
          f"std={stdev(cl2_scores):.4f}")
    print()

    # Interpretation
    abs_r = abs(r)
    if abs_r > 0.7:
        verdict = "STRONG — CL2 captures R18 signal. Math constraint VIABLE."
    elif abs_r > 0.3:
        verdict = "MODERATE — partial overlap. CL2 direction valid, needs tuning."
    else:
        verdict = "WEAK — CL2 measures something different. Hypothesis needs revision."
    print(f"  VERDICT: |r| = {abs_r:.4f} → {verdict}")
    print()

    # Component correlations (which CL2 component drives it?)
    gz_scores = [d["cl2_gzip"] for d in details]
    ent_scores = [d["cl2_entropy"] for d in details]
    ttr_scores = [d["cl2_ttr"] for d in details]

    print("  Component correlations with R18 hedge_density:")
    print(f"    gzip_ratio:      r = {pearson_r(r18_scores, gz_scores):+.4f}")
    print(f"    bigram_entropy:  r = {pearson_r(r18_scores, ent_scores):+.4f}")
    print(f"    type_token_ratio: r = {pearson_r(r18_scores, ttr_scores):+.4f}")
    print()

    if args.verbose:
        print("-" * 60)
        print("PER-SAMPLE SCORES:")
        for d in details:
            print(f"  [{d['idx']:3d}] R18={d['r18_hedge_density']:.4f} "
                  f"(h={d['r18_hedge_count']:2d}) "
                  f"CL2={d['cl2_composite']:.4f} "
                  f"gz={d['cl2_gzip']:.3f} "
                  f"ent={d['cl2_entropy']:.2f} "
                  f"ttr={d['cl2_ttr']:.3f} "
                  f"| {d['preview']}")
        print()

    # Show outliers: highest disagreement between R18 and CL2 rankings
    if args.top > 0:
        # Rank by each metric
        r18_ranked = sorted(range(len(details)), key=lambda i: r18_scores[i])
        cl2_ranked = sorted(range(len(details)), key=lambda i: -cl2_scores[i])

        r18_rank = {idx: rank for rank, idx in enumerate(r18_ranked)}
        cl2_rank = {idx: rank for rank, idx in enumerate(cl2_ranked)}

        rank_diffs = [(abs(r18_rank[i] - cl2_rank[i]), i) for i in range(len(details))]
        rank_diffs.sort(reverse=True)

        print("-" * 60)
        print(f"TOP {args.top} OUTLIERS (largest rank disagreement R18 vs CL2):")
        for diff, idx in rank_diffs[:args.top]:
            d = details[idx]
            print(f"  [{idx:3d}] rank_diff={diff:3d}  "
                  f"R18={d['r18_hedge_density']:.4f}  "
                  f"CL2={d['cl2_composite']:.4f}  "
                  f"| {d['preview']}")
        print()

    # Machine-readable output
    result = {
        "probe": "cl_crown_v1",
        "rule": "R18",
        "n": len(texts),
        "pearson_r": round(r, 4),
        "pearson_r_inverted": round(r_inv, 4),
        "abs_r": round(abs_r, 4),
        "r18_mean": round(sum(r18_scores)/len(r18_scores), 4),
        "cl2_mean": round(sum(cl2_scores)/len(cl2_scores), 4),
        "component_r": {
            "gzip_ratio": round(pearson_r(r18_scores, gz_scores), 4),
            "bigram_entropy": round(pearson_r(r18_scores, ent_scores), 4),
            "type_token_ratio": round(pearson_r(r18_scores, ttr_scores), 4),
        },
    }

    out_path = Path(args.file).stem + "_cl_probe_v1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] {out_path}")

    # Exit code: 0 if |r| > 0.3 (viable), 1 if weak
    sys.exit(0 if abs_r > 0.3 else 1)


def stdev(xs: list) -> float:
    """Population standard deviation."""
    n = len(xs)
    if n < 2:
        return 0.0
    mean = sum(xs) / n
    return math.sqrt(sum((x - mean) ** 2 for x in xs) / n)


if __name__ == "__main__":
    main()
