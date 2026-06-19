"""
R18 Code-Based Filler Filter v1
================================
Externalizes R18 (self-splicing) as deterministic code:
  - Sentence-level: strips pure-filler sentences (hedge openers, padding, disclaimers, closers)
  - Phrase-level: strips filler openers from content-bearing sentences, removes empty qualifiers
  - BPW (bits-per-word via gzip) as audit metric, NOT enforcement

Usage:
  from r18_code_v1 import strip_filler, score_filler, compute_bpw
  cleaned = strip_filler(text)
  report  = score_filler(text)

Track D / CL Crown code-externalization probe.
"""

import re
import gzip
import json
import sys

# ============================================================
# PATTERN BANK — each list = compiled regexes, IGNORECASE
# ============================================================

def _compile(patterns):
    return [re.compile(p, re.IGNORECASE) for p in patterns]

# --- Cat 1: Hedge openers ("It's important to note that...") ---
_HEDGE_OPENERS_RAW = [
    r"it['\u2019]?s\s+(?:important|crucial|essential|key|vital|necessary)\s+to\s+(?:note|mention|understand|remember|recognize|consider|keep\s+in\s+mind)",
    r"it['\u2019]?s\s+worth\s+(?:noting|mentioning|pointing\s+out|remembering|considering)",
    r"it\s+should\s+be\s+(?:noted|mentioned|understood|recognized|pointed\s+out)",
    r"it\s+bears?\s+mentioning",
    r"one\s+(?:thing|point|aspect)\s+to\s+(?:keep\s+in\s+mind|consider|note|remember)",
    r"(?:we|you)\s+(?:should|must|need\s+to)\s+(?:note|remember|keep\s+in\s+mind|understand)\s+that",
    r"(?:an?\s+)?(?:important|key|crucial|critical|vital|notable)\s+(?:thing|point|aspect|factor|consideration)\s+(?:is|here\s+is)\s+that",
    r"what\s+(?:is|makes\s+this)\s+(?:particularly\s+)?(?:interesting|notable|important|remarkable)\s+is\s+that",
]
HEDGE_OPENERS = _compile(_HEDGE_OPENERS_RAW)

# --- Cat 2: Padding transitions (sentence-initial) ---
_PADDING_TRANS_RAW = [
    r"^(?:in\s+)?(?:conclusion|summary|closing|short)\s*[,:\-]",
    r"^overall\s*[,:\-]",
    r"^to\s+(?:summarize|sum\s+up|conclude|wrap\s+up)\s*[,:\-]",
    r"^as\s+(?:we|you)\s+can\s+see\s*[,:\-]",
    r"^as\s+(?:mentioned|noted|discussed|stated)\s+(?:above|earlier|previously|before)\s*[,:\-]",
    r"^(?:having\s+said\s+that|that\s+(?:being\s+)?said|with\s+(?:that|this)\s+(?:being\s+)?said)\s*[,:\-]",
    r"^(?:let\s+me|allow\s+me\s+to|i['\u2019]?d\s+like\s+to)\s+(?:explain|elaborate|clarify|break\s+(?:this|it)\s+down)",
    r"^(?:first(?:ly)?|second(?:ly)?|third(?:ly)?|finally|lastly|additionally|furthermore|moreover)\s*[,:\-]",
]
PADDING_TRANS = _compile(_PADDING_TRANS_RAW)

# --- Cat 3: Empty qualifiers (word-level, inline strip) ---
_EMPTY_QUALS_RAW = [
    r"\b(?:very|really|quite|rather|somewhat|fairly)\b",
    r"\b(?:basically|essentially|fundamentally|literally)\b",
    r"\b(?:obviously|clearly|naturally|certainly|undoubtedly|undeniably|arguably)\b",
    r"\b(?:actually|simply|just)\b",
]
EMPTY_QUALS = _compile(_EMPTY_QUALS_RAW)

# --- Cat 4: Disclaimer preambles (full sentence match) ---
_DISCLAIMER_RAW = [
    r"(?:while|although)\s+there\s+are\s+(?:many|several|various|numerous|multiple)\s+(?:factors?|aspects?|things?|considerations?|elements?)",
    r"this\s+is\s+a\s+(?:complex|complicated|nuanced|multifaceted|broad)\s+(?:topic|issue|subject|question|area)",
    r"there\s+are\s+(?:many|several|various|numerous|multiple)\s+(?:factors?|aspects?|things?|ways?|perspectives?)\s+to\s+(?:consider|take\s+into\s+account|think\s+about)",
    r"^(?:well|so)\s*,",
]
DISCLAIMERS = _compile(_DISCLAIMER_RAW)

# --- Cat 5: Filler closers ---
_CLOSER_RAW = [
    r"^(?:i\s+)?hope\s+(?:this|that)\s+(?:helps?|answers?|clarifies?|(?:makes?\s+sense))",
    r"^(?:please\s+)?(?:let\s+me\s+know|feel\s+free)\s+(?:if|to)",
    r"^if\s+you\s+have\s+(?:any\s+)?(?:further\s+)?(?:questions?|concerns?|doubts?)",
    r"^(?:don['\u2019]t\s+hesitate\s+to\s+(?:ask|reach\s+out))",
]
CLOSERS = _compile(_CLOSER_RAW)

# --- Cat 6: Question restaters (intro padding) ---
_RESTATER_RAW = [
    r"^(?:great|good|excellent|interesting)\s+question",
    r"^(?:that['\u2019]s|this\s+is)\s+(?:a\s+)?(?:great|good|excellent|interesting|important|common)\s+question",
    r"^(?:sure|absolutely|of\s+course|certainly)[,!.]?\s*(?:i['\u2019]?(?:d|ll)\s+be\s+happy\s+to|let\s+me)",
    r"^thank\s+you\s+for\s+(?:asking|(?:your|the)\s+question)",
]
RESTATERS = _compile(_RESTATER_RAW)

# ============================================================
# BPW (bits-per-word via gzip) — audit metric
# ============================================================

def compute_bpw(text: str) -> float:
    """Bits-per-word: len(gzip(text))*8 / word_count. Validated 20/20 in v187."""
    words = text.split()
    if not words:
        return 0.0
    compressed = gzip.compress(text.encode("utf-8"))
    return (len(compressed) * 8) / len(words)


# ============================================================
# SENTENCE SPLITTER (simple, covers .!? boundaries)
# ============================================================

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"\'\(])")

def _split_sentences(text: str) -> list[str]:
    """Split text into sentences. Keeps original casing."""
    return [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]


# ============================================================
# SCORING
# ============================================================

def _match_any(text: str, compiled_patterns: list) -> list[str]:
    hits = []
    for rx in compiled_patterns:
        for m in rx.finditer(text):
            hits.append(m.group())
    return hits


def _content_words(text: str) -> int:
    """Count words with len > 2 (skip articles, prepositions)."""
    return len([w for w in text.split() if len(w) > 2])


def score_sentence(sentence: str) -> dict:
    """Classify one sentence: filler (pure), filler_opener (strip prefix), or content."""
    s = sentence.strip()
    if not s:
        return {"sentence": s, "verdict": "empty", "hits": [], "category": None}

    hits = []
    category = None

    # Check each category
    for cat_name, patterns in [
        ("restater",           RESTATERS),
        ("hedge_opener",       HEDGE_OPENERS),
        ("padding_transition", PADDING_TRANS),
        ("disclaimer",         DISCLAIMERS),
        ("closer",             CLOSERS),
    ]:
        h = _match_any(s, patterns)
        if h:
            hits.extend(h)
            category = category or cat_name

    if not hits:
        return {"sentence": s, "verdict": "content", "hits": [], "category": None}

    # Has filler pattern — check if there's substantial content AFTER the pattern
    remainder = s
    for h_match in hits:
        remainder = re.sub(re.escape(h_match), "", remainder, count=1, flags=re.IGNORECASE)
    remainder = re.sub(r"\s{2,}", " ", remainder).strip().lstrip(",.:;- ")
    # Strip orphaned leading "that" left after hedge opener removal
    remainder = re.sub(r"^that\s+", "", remainder, flags=re.IGNORECASE).strip()

    if _content_words(remainder) > 6:
        # Substantial content behind filler opener — strip opener, keep content
        return {"sentence": s, "verdict": "filler_opener", "hits": hits,
                "category": category, "remainder": remainder}
    else:
        # Pure filler sentence — strip entirely
        return {"sentence": s, "verdict": "filler", "hits": hits, "category": category}


def score_filler(text: str) -> dict:
    """Full filler analysis. Returns counts, hits, BPW, per-sentence breakdown."""
    sentences = _split_sentences(text)
    scored = [score_sentence(s) for s in sentences]

    filler_full = [r for r in scored if r["verdict"] == "filler"]
    filler_opener = [r for r in scored if r["verdict"] == "filler_opener"]
    content = [r for r in scored if r["verdict"] == "content"]

    # Inline qualifier count across full text
    qual_hits = _match_any(text, EMPTY_QUALS)

    bpw = compute_bpw(text)

    return {
        "total_sentences": len(scored),
        "filler_stripped": len(filler_full),
        "filler_trimmed": len(filler_opener),
        "content_kept": len(content),
        "filler_ratio": len(filler_full) / max(len(scored), 1),
        "qualifier_count": len(qual_hits),
        "bpw": round(bpw, 2),
        "word_count": len(text.split()),
        "details": scored,
    }


# ============================================================
# STRIP — the R18 externalization
# ============================================================

def strip_filler(text: str) -> str:
    """
    R18 as code: remove filler, return cleaned text.
    - Pure filler sentences → removed entirely
    - Filler-opener sentences → opener stripped, content kept
    - Inline empty qualifiers → stripped from all kept sentences
    """
    sentences = _split_sentences(text)
    kept = []

    for s in sentences:
        result = score_sentence(s)

        if result["verdict"] == "filler":
            continue  # drop entirely
        elif result["verdict"] == "filler_opener":
            cleaned = result["remainder"]
        else:
            cleaned = s

        # Strip inline qualifiers
        for rx in EMPTY_QUALS:
            cleaned = rx.sub("", cleaned)

        # Clean orphaned leading punctuation left after stripping
        cleaned = re.sub(r"^[,;:\-]+\s*", "", cleaned)
        # Normalize whitespace and orphaned double-punctuation
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([,;:.])", r"\1", cleaned)
        cleaned = cleaned.strip()

        # Capitalize first letter — but only plain lowercase, not acronyms (mRNA, pH)
        if cleaned and cleaned[0].islower() and (len(cleaned) < 2 or cleaned[1].islower()):
            cleaned = cleaned[0].upper() + cleaned[1:]

        if cleaned:
            kept.append(cleaned)

    return " ".join(kept)


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python r18_code_v1.py <text_file> [--strip | --score]")
        print("  --strip  : print cleaned text")
        print("  --score  : print JSON filler report (default)")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read().strip()

    if "--strip" in sys.argv:
        print(strip_filler(text))
    else:
        report = score_filler(text)
        # Remove per-sentence details for compact output unless --verbose
        if "--verbose" not in sys.argv:
            report.pop("details", None)
        print(json.dumps(report, indent=2, ensure_ascii=False))
