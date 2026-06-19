#!/usr/bin/env python3
"""
CL2 Re-scorer v3 — length-invariant metrics
=============================================
Reads saved A/B probe results (cl_ab_*.json) and re-scores with
length-invariant metrics. No generation needed.

Key fix: original CL2 (gzip_ratio + bigram_entropy + TTR) is length-dependent.
New metrics normalize per-token to avoid penalizing concise outputs.

Usage:
  python cl2_rescore_v3.py cl_ab_qwen2.5-coder_7b_10.json
"""

import gzip
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

# ─── R18 regex (same as v2, for comparison) ───

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

# Common English stopwords (function words with no content)
STOPWORDS = set("""
a an the is are was were be been being have has had do does did will would
shall should may might can could am is are this that these those it its
he she they we you i me him her us them my your his our their what which
who whom where when why how if or and but not no nor so yet both either
neither each every all any few more most other some such than too very
of in to for with on at by from as into through during before after above
below between under about against over out up down off about around
""".split())


def words(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())


def r18_hedge_density(text: str) -> float:
    w = words(text)
    if not w:
        return 0.0
    hc = sum(len(pat.findall(text)) for pat in _HEDGE_RES)
    return hc / len(w)


# ─── NEW LENGTH-INVARIANT METRICS ───

def bits_per_word(text: str) -> float:
    """Compressed bits per word. Higher = more information per word.
    Filler = predictable patterns → fewer bits/word.
    Content = diverse vocabulary → more bits/word."""
    w = words(text)
    if not w:
        return 0.0
    raw = text.encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)
    return (len(compressed) * 8) / len(w)


def content_word_ratio(text: str) -> float:
    """Ratio of content words (non-stopwords) to total words.
    Higher = more content, less filler/function words."""
    w = words(text)
    if not w:
        return 0.0
    content = [x for x in w if x not in STOPWORDS]
    return len(content) / len(w)


def unique_trigram_ratio(text: str) -> float:
    """Unique word trigrams / total trigrams. Filler repeats patterns.
    Higher = more diverse phrasing."""
    w = words(text)
    if len(w) < 3:
        return 0.0
    trigrams = [tuple(w[i:i+3]) for i in range(len(w) - 2)]
    return len(set(trigrams)) / len(trigrams)


def entropy_rate(text: str) -> float:
    """Shannon entropy rate = bits per character (on char unigrams).
    Normalized for length. Higher = more information density."""
    if len(text) < 2:
        return 0.0
    counts = Counter(text.lower())
    total = len(text)
    H = -sum((c/total) * math.log2(c/total) for c in counts.values())
    return H  # already per-symbol by definition


def sentence_compression_variance(text: str) -> float:
    """Variance in per-sentence compression ratios.
    Low variance = uniform density (good). High variance = mix of filler and content."""
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 10]
    if len(sentences) < 2:
        return 0.0
    ratios = []
    for s in sentences:
        raw = s.encode("utf-8")
        comp = gzip.compress(raw, compresslevel=9)
        ratios.append(len(comp) / max(len(raw), 1))
    mean = sum(ratios) / len(ratios)
    var = sum((r - mean) ** 2 for r in ratios) / len(ratios)
    return var


def cl2v3_composite(text: str) -> float:
    """Length-invariant CL2 composite.
    All components are per-token/per-char, not dependent on total length."""
    bpw = bits_per_word(text)
    cwr = content_word_ratio(text)
    utr = unique_trigram_ratio(text)
    er = entropy_rate(text)

    # Normalize to ~[0,1]
    bpw_n = max(0.0, min(1.0, (bpw - 30) / (120 - 30)))     # typical: 30-120 bits/word
    cwr_n = max(0.0, min(1.0, (cwr - 0.3) / (0.8 - 0.3)))   # typical: 0.3-0.8
    utr_n = max(0.0, min(1.0, (utr - 0.5) / (1.0 - 0.5)))   # typical: 0.5-1.0
    er_n = max(0.0, min(1.0, (er - 3.0) / (5.0 - 3.0)))      # typical: 3.0-5.0

    # Weighted: bits_per_word and content_ratio are strongest signals
    return 0.35 * bpw_n + 0.30 * cwr_n + 0.20 * utr_n + 0.15 * er_n


# ─── ANALYSIS ───

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python cl2_rescore_v3.py <cl_ab_*.json>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)

    data = json.loads(path.read_text(encoding="utf-8"))
    samples = data["samples"]
    n = len(samples)

    print(f"[DATA] Re-scoring {n} samples from {path}")
    print(f"[MODEL] {data.get('model', '?')}")
    print()

    results = []
    for s in samples:
        ta = s.get("text_A", "")
        tb = s.get("text_B", "")

        # Old scores
        old_cl2_a = s["A_cl2"]
        old_cl2_b = s["B_cl2"]

        # New scores
        new_a = cl2v3_composite(ta)
        new_b = cl2v3_composite(tb)

        # Components
        bpw_a, bpw_b = bits_per_word(ta), bits_per_word(tb)
        cwr_a, cwr_b = content_word_ratio(ta), content_word_ratio(tb)
        utr_a, utr_b = unique_trigram_ratio(ta), unique_trigram_ratio(tb)

        # R18
        hd_a = r18_hedge_density(ta)
        hd_b = r18_hedge_density(tb)

        results.append({
            "idx": s["idx"],
            "prompt": s["prompt"][:50],
            "len_A": len(ta), "len_B": len(tb),
            "hd_A": hd_a, "hd_B": hd_b,
            "old_A": old_cl2_a, "old_B": old_cl2_b,
            "new_A": round(new_a, 4), "new_B": round(new_b, 4),
            "bpw_A": round(bpw_a, 1), "bpw_B": round(bpw_b, 1),
            "cwr_A": round(cwr_a, 3), "cwr_B": round(cwr_b, 3),
            "utr_A": round(utr_a, 3), "utr_B": round(utr_b, 3),
        })

    # Aggregate
    print("=" * 70)
    print("CL2 v3 RE-SCORE — LENGTH-INVARIANT")
    print("=" * 70)
    print()

    hd_a_all = [r["hd_A"] for r in results]
    hd_b_all = [r["hd_B"] for r in results]
    new_a_all = [r["new_A"] for r in results]
    new_b_all = [r["new_B"] for r in results]
    old_a_all = [r["old_A"] for r in results]
    old_b_all = [r["old_B"] for r in results]

    # Cross-condition correlations (pool A and B)
    all_hd = hd_a_all + hd_b_all
    all_new = new_a_all + new_b_all
    all_old = old_a_all + old_b_all

    r_new = pearson_r(all_hd, all_new)
    r_old = pearson_r(all_hd, all_old)

    print(f"  Cross-condition correlation (hedge_density vs CL2):")
    print(f"    OLD CL2 (v2): r = {r_old:+.4f}")
    print(f"    NEW CL2 (v3): r = {r_new:+.4f}")
    print()

    # Delta correlations
    d_hd = [hd_b_all[i] - hd_a_all[i] for i in range(n)]
    d_new = [new_a_all[i] - new_b_all[i] for i in range(n)]
    d_old = [old_a_all[i] - old_b_all[i] for i in range(n)]

    r_d_new = pearson_r(d_hd, d_new)
    r_d_old = pearson_r(d_hd, d_old)

    print(f"  Delta correlation (Δ_hedge vs Δ_CL2):")
    print(f"    OLD CL2 (v2): r = {r_d_old:+.4f}")
    print(f"    NEW CL2 (v3): r = {r_d_new:+.4f}")
    print()

    # Means
    print(f"  Means:")
    print(f"    hedge_density:  A={sum(hd_a_all)/n:.4f}  B={sum(hd_b_all)/n:.4f}")
    print(f"    CL2 v3:        A={sum(new_a_all)/n:.4f}  B={sum(new_b_all)/n:.4f}")
    print(f"    CL2 v2 (old):  A={sum(old_a_all)/n:.4f}  B={sum(old_b_all)/n:.4f}")
    print()

    # Component correlations with hedge_density
    bpw_all = [r["bpw_A"] for r in results] + [r["bpw_B"] for r in results]
    cwr_all = [r["cwr_A"] for r in results] + [r["cwr_B"] for r in results]
    utr_all = [r["utr_A"] for r in results] + [r["utr_B"] for r in results]

    print(f"  Component correlations with hedge_density:")
    print(f"    bits_per_word:       r = {pearson_r(all_hd, bpw_all):+.4f}")
    print(f"    content_word_ratio:  r = {pearson_r(all_hd, cwr_all):+.4f}")
    print(f"    unique_trigram_ratio: r = {pearson_r(all_hd, utr_all):+.4f}")
    print()

    # Verdict
    abs_r = abs(r_new)
    if abs_r > 0.7:
        verdict = "STRONG — CL2v3 captures R18 signal. Math constraint VIABLE."
    elif abs_r > 0.3:
        verdict = "MODERATE — CL2v3 partially captures R18. Direction valid."
    else:
        verdict = "WEAK — CL2v3 still doesn't track R18. Need different approach."

    print(f"  VERDICT: |r| = {abs_r:.4f} → {verdict}")
    print()

    # Per-sample
    print("-" * 70)
    print(f"{'#':>3} {'len_A':>5} {'len_B':>5} {'hd_A':>5} {'hd_B':>5} "
          f"{'old_A':>6} {'old_B':>6} {'new_A':>6} {'new_B':>6} "
          f"{'bpw_A':>5} {'bpw_B':>5}  prompt")
    for r in results:
        print(f"{r['idx']:3d} {r['len_A']:5d} {r['len_B']:5d} "
              f"{r['hd_A']:5.3f} {r['hd_B']:5.3f} "
              f"{r['old_A']:6.3f} {r['old_B']:6.3f} "
              f"{r['new_A']:6.3f} {r['new_B']:6.3f} "
              f"{r['bpw_A']:5.1f} {r['bpw_B']:5.1f}  "
              f"{r['prompt']}")
    print()

    # Save
    out_path = path.stem + "_v3_rescore.json"
    out = {
        "rescore": "cl2_v3",
        "model": data.get("model"),
        "n": n,
        "r_cross_old": round(r_old, 4) if not math.isnan(r_old) else None,
        "r_cross_new": round(r_new, 4) if not math.isnan(r_new) else None,
        "r_delta_old": round(r_d_old, 4) if not math.isnan(r_d_old) else None,
        "r_delta_new": round(r_d_new, 4) if not math.isnan(r_d_new) else None,
        "verdict": verdict,
        "samples": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] {out_path}")


if __name__ == "__main__":
    main()
