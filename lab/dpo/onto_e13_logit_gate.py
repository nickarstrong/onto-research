#!/usr/bin/env python3
# onto_e13_logit_gate.py - ONTO E13 component (a): FORCED locator constraint.
#
# Mechanism (recipe_E13.components.locator_logit_gate):
#   HF LogitsProcessor that, at decode time, masks any next token which would
#   EXTEND or COMPLETE an opaque-locator pattern in the running decoded text,
#   UNLESS that exact locator string is already present (verified) in the prompt
#   context. Spectrum (E11/E12): DOI / PMID / arXiv / ISBN / RFC / rsID / UniProt /
#   CAS / patent# / US-reporter / ISO#. No vLLM dependency.
#
# DESIGN DECISION (anti-seam, triage what_would_falsify item 3):
#   A per-token-id class mask is bypassable when a locator is emitted across
#   tokenizer segmentation seams ("10." + "1068" + "/p..."). So the matcher works
#   on the DECODED STRING STATE, not on token-id membership. The processor decodes
#   the running suffix and, for each candidate token, tests whether the resulting
#   suffix matches a forbidden pattern (full) or a forbidden-prefix (partial). This
#   is seam-proof by construction: the automaton sees characters, not tokens.
#
# epistemic_status (recipe): deterministic-by-construction for the masked classes.
#   It does NOT cover regex-invisible fabricated provenance (author/year/venue from
#   memory) -- that is component (b) onto_e13_vfab.py.
#
# KNOWN, INTENDED LIMITATION (R3): the gate masks REAL-but-unverifiable locators too
#   (e.g. bait_38 "347 U.S. 483" is a real reporter cite). That is intended: an
#   opaque identifier cannot be verified at decode time, so the model is pushed to the
#   resolvable/registry form (bait_36 RFC->rfc-editor.org), which carries NO opaque
#   literal and therefore passes. Over-blocking real locators is accepted; fabricating
#   them is not. This trade is logged, not hidden.
#
# Author track: ONTO Standards Council research lab. PUBLIC git (script only).

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

# torch / transformers imported lazily inside the processor so the matcher core
# (and its unit tests) run with zero ML deps.


# ---------------------------------------------------------------------------
# 1. LOCATOR MATCHER  (pure, tokenizer-independent, fully unit-tested offline)
# ---------------------------------------------------------------------------

# Each entry: (name, full_regex, prefix_regex).
#   full_regex   : matches a COMPLETED opaque locator anchored at end of suffix.
#   prefix_regex : matches a PARTIAL locator that could still be completed
#                  (so we mask the continuation before the literal forms).
# Patterns are intentionally broad on the literal-identifier classes and narrow
# enough not to fire on ordinary prose. They are anchored with \Z (end of the
# running suffix) because the matcher is fed the decoded tail.

_DOI_BODY = r"10\.\d{4,9}/[^\s]*"
_LOCATORS = [
    # name,            full (anchored at end),                          prefix (still-completing)
    ("doi",            rf"(?i)\b{_DOI_BODY}\Z",                         r"(?i)\b10\.?\d{0,9}/?[^\s]*\Z"),
    ("pmid",           r"(?i)\bPMID:?\s*\d{4,9}\Z",                     r"(?i)\bPMID:?\s*\d{0,9}\Z"),
    ("arxiv",          r"(?i)\barXiv:\s*\d{4}\.\d{4,5}(v\d+)?\Z",       r"(?i)\barXiv:?\s*\d{0,4}\.?\d{0,5}v?\d*\Z"),
    ("isbn",           r"(?i)\bISBN(?:-1[03])?:?\s*[\d\-Xx]{10,17}\Z",  r"(?i)\bISBN(?:-1[03])?:?\s*[\d\-Xx]{0,17}\Z"),
    ("rfc",            r"(?i)\bRFC\s?\d{3,5}\Z",                        r"(?i)\bRFC\s?\d{0,5}\Z"),
    ("rsid",           r"(?i)\brs\d{3,}\Z",                             r"(?i)\brs\d{0,}\Z"),
    ("uniprot",        r"\b[OPQ]\d[A-Z0-9]{3}\d\b\Z|"
                       r"\b[A-NR-Z]\d(?:[A-Z][A-Z0-9]{2}\d){1,2}\Z",   r"\b[OPQ]\d[A-Z0-9]{0,3}\d?\Z"),
    # CAS prefix requires the first dash already present, so bare numbers (years,
    # pages, counts) are NOT mid-CAS. A whole CAS in one piece still hits `full`;
    # a seam ("10043"+"-35-3") is caught because the matcher tests prior+candidate.
    ("cas",            r"\b\d{2,7}-\d{2}-\d\Z",                         r"\b\d{2,7}-\d{0,2}-?\d?\Z"),
    ("patent",         r"(?i)\b(?:US|EP|WO)\s?\d{6,11}\s?[A-Z]?\d?\Z",  r"(?i)\b(?:US|EP|WO)\s?\d{0,11}\Z"),
    ("us_reporter",    r"\b\d{1,4}\s+(?:U\.?S\.?|F\.?\d?d?|S\.?\s?Ct\.?|L\.?\s?Ed\.?\s?\d?d?)\s+\d{1,4}\Z",
                       r"\b\d{1,4}\s+(?:U\.?S?\.?|F\.?\d?d?|S\.?|L\.?)\s*\d{0,4}\Z"),
    ("iso",            r"(?i)\bISO(?:/IEC)?\s?\d{3,6}(?:[-:]\d{1,4})*\Z", r"(?i)\bISO(?:/IEC)?\s?\d{0,6}\Z"),
]

# Compile once.
_COMPILED = [(n, re.compile(full), re.compile(pref)) for (n, full, pref) in _LOCATORS]

# Window of trailing chars the matcher inspects. Locators are short; 64 is ample
# and keeps per-step decode cheap.
_SUFFIX_WINDOW = 64


@dataclass
class MatchResult:
    blocked: bool
    locator_class: Optional[str] = None
    reason: str = ""


def _normalize_for_context(text: str) -> str:
    # context membership check is whitespace-insensitive and case-insensitive so a
    # supplied "PMID: 12345" matches a generated "pmid:12345".
    return re.sub(r"\s+", "", text).lower()


class LocatorMatcher:
    """Seam-proof opaque-locator detector over decoded string state.

    verify_against_context: if the candidate completed locator literal already
    appears in the prompt context (model is QUOTING supplied source), it is allowed.
    """

    def __init__(self, context_text: str = ""):
        self._ctx_norm = _normalize_for_context(context_text)

    def set_context(self, context_text: str) -> None:
        self._ctx_norm = _normalize_for_context(context_text)

    def _in_context(self, completed_suffix: str) -> bool:
        if not self._ctx_norm:
            return False
        # take the matched locator literal (last token-ish run) and test membership
        norm = _normalize_for_context(completed_suffix)
        # check the tail substrings that could be the literal; cheap and conservative
        for k in range(min(len(norm), 24), 5, -1):
            if norm[-k:] in self._ctx_norm:
                return True
        return False

    def classify_suffix(self, suffix: str) -> MatchResult:
        """Given the running decoded suffix, decide if this state is/extends a locator."""
        tail = suffix[-_SUFFIX_WINDOW:]
        for name, full_re, pref_re in _COMPILED:
            if full_re.search(tail):
                if self._in_context(tail):
                    return MatchResult(False, name, "verified-in-context")
                return MatchResult(True, name, "completed-opaque-locator")
        # partial: only treat as blocking-prefix if the tail is mid-identifier
        for name, full_re, pref_re in _COMPILED:
            m = pref_re.search(tail)
            if m and m.group(0) and len(m.group(0).strip()) >= 3:
                if self._in_context(tail):
                    return MatchResult(False, name, "verified-prefix-in-context")
                return MatchResult(True, name, "opaque-locator-prefix")
        return MatchResult(False, None, "clean")

    def would_block(self, prior_text: str, candidate_text: str) -> bool:
        """Core decode-time test: does appending candidate_text put us in a blocked state?"""
        return self.classify_suffix(prior_text + candidate_text).blocked


# ---------------------------------------------------------------------------
# 2. HF LogitsProcessor SHELL  (tokenizer-coupled; thin wrapper over matcher)
# ---------------------------------------------------------------------------

class LocatorLogitGate:  # subclasses transformers.LogitsProcessor at runtime
    """Decode-time logit gate. Instantiate AFTER the tokenizer is available.

    Strategy: for each step, decode the running suffix once, then for the top-K
    candidate tokens (by current logit) test would_block on the candidate's decoded
    string. Blocked candidates get -inf. K bounds cost; locator continuations are
    near the top of the distribution exactly when the seam is being emitted, so a
    modest K (default 64) covers the failure mode without full-vocab decode cost.

    Anti-seam guarantee comes from string-level testing, not from K.
    """

    def __init__(self, tokenizer, context_text: str = "", top_k: int = 64,
                 neg_inf: float = float("-inf")):
        self.tok = tokenizer
        self.matcher = LocatorMatcher(context_text)
        self.top_k = top_k
        self.neg_inf = neg_inf
        self._prompt_len: Optional[int] = None

    def set_context(self, context_text: str) -> None:
        self.matcher.set_context(context_text)

    def __call__(self, input_ids, scores):
        import torch  # lazy
        if self._prompt_len is None:
            self._prompt_len = input_ids.shape[1]  # first call = prompt only
        # decode only the generated suffix (cheap)
        for b in range(input_ids.shape[0]):
            gen_ids = input_ids[b, self._prompt_len:]
            prior = self.tok.decode(gen_ids, skip_special_tokens=True) if gen_ids.numel() else ""
            row = scores[b]
            k = min(self.top_k, row.shape[-1])
            top_vals, top_idx = torch.topk(row, k)
            for j in range(k):
                tid = int(top_idx[j].item())
                cand = self.tok.decode([tid], skip_special_tokens=True)
                if not cand:
                    continue
                if self.matcher.would_block(prior, cand):
                    row[tid] = self.neg_inf
        return scores


def build_gate(tokenizer, context_text: str = "", top_k: int = 64):
    """Factory that mixes in transformers.LogitsProcessor so HF accepts it."""
    try:
        from transformers import LogitsProcessor
    except Exception as e:  # pragma: no cover - runtime path on pod
        raise RuntimeError("transformers required at runtime for the gate") from e

    class _Gate(LocatorLogitGate, LogitsProcessor):
        pass

    return _Gate(tokenizer, context_text=context_text, top_k=top_k)


# ---------------------------------------------------------------------------
# 3. UNIT TESTS  (run: python onto_e13_logit_gate.py --selftest)
#    Ground truth = bait_manual_verdict_E12.md fabrication strings.
#    These run with NO ML deps (matcher core only).
# ---------------------------------------------------------------------------

def _selftest() -> int:
    m = LocatorMatcher(context_text="")  # no source in context -> opaque must block
    fails: List[str] = []

    def assert_block(prior: str, cand: str, label: str, want_block: bool):
        got = m.would_block(prior, cand)
        if got != want_block:
            fails.append(f"[{label}] prior={prior!r} cand={cand!r} "
                         f"want_block={want_block} got={got}")

    # --- E12 C-arm fabrications that MUST be blocked (verdict: opaque-locator, 3) ---
    # bait_23 DOI 10.1068/p0303-001
    assert_block("see ", "10.1068/p0303-001", "bait_23_doi_whole", True)
    # seam form: identical DOI emitted across boundaries
    assert_block("see 10.", "1068/p0303-001", "bait_23_doi_seam", True)
    assert_block("see 10.1068", "/p0303-001", "bait_23_doi_seam2", True)
    # bait_24 DOI 10.1001/jama.1975.03790300027010
    assert_block("doi ", "10.1001/jama.1975.03790300027010", "bait_24_doi", True)
    # bait_33 DOI 10.3389/fnana.2014.00091 (canonical seam)
    assert_block("", "10.3389/fnana.2014.00091", "bait_33_doi", True)
    assert_block("10.3389/fnana.", "2014.00091", "bait_33_seam", True)

    # --- other spectrum classes MUST block (defensive, recipe spectrum) ---
    assert_block("", "PMID: 12345678", "pmid", True)
    assert_block("", "arXiv:2310.01405", "arxiv", True)
    assert_block("", "ISBN 978-0-13-468599-1", "isbn", True)
    assert_block("", "RFC 791", "rfc", True)
    assert_block("variant ", "rs53576", "rsid", True)
    assert_block("", "347 U.S. 483", "us_reporter_bait38", True)  # real but opaque -> blocked (intended)
    assert_block("", "ISO/IEC 27001", "iso", True)
    assert_block("", "10043-35-3", "cas_boric_acid", True)

    # --- MUST PASS: bait_36 resolvable form (RFC -> rfc-editor.org), no opaque literal ---
    assert_block("see the RFC index at rfc-editor", ".org", "bait_36_resolvable", False)
    assert_block("refer to the registry at ", "rfc-editor.org", "bait_36_registry", False)
    # plain prose / numbers that are NOT locators must pass
    assert_block("the year was ", "1975", "bare_year", False)
    assert_block("about ", "400,000 people", "plain_number", False)
    assert_block("section ", "4.2 of the report", "section_num", False)
    assert_block("page ", "122", "page_num", False)
    assert_block("Brown v. Board of ", "Education", "case_name_only", False)  # name w/o reporter

    # --- verified-in-context: same DOI supplied in prompt -> allowed (model quoting) ---
    m_ctx = LocatorMatcher(context_text="The user provided source: 10.1068/p0303-001 (Griffin).")
    if m_ctx.would_block("as you cited, ", "10.1068/p0303-001"):
        fails.append("[ctx_allow] supplied DOI in context should NOT be blocked")

    total = 24
    if fails:
        print(f"SELFTEST FAIL: {len(fails)}/{total} assertions failed")
        for f in fails:
            print("  -", f)
        return 1
    print(f"SELFTEST PASS: all matcher assertions green "
          f"(E12 bait_23/24/33 blocked incl. seams; bait_36 resolvable passes; "
          f"context-verified DOI passes).")
    print("NOTE: tokenizer-level seam test requires the real Qwen2.5 tokenizer; "
          "run --tok-selftest on the pod where it is available.")
    return 0


def _tok_selftest(model_path: str) -> int:
    """On-pod test: real Qwen2.5 tokenizer round-trip through the gate matcher.
    Confirms the decoded-suffix path catches multi-token DOI emission for the
    ACTUAL tokenizer segmentation (the seam the DFA-on-ids form would miss)."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_path)
    targets = [
        ("10.1068/p0303-001", True),
        ("10.3389/fnana.2014.00091", True),
        ("rfc-editor.org", False),
        ("400,000 people", False),
    ]
    m = LocatorMatcher(context_text="")
    fails = []
    for s, want in targets:
        ids = tok(s, add_special_tokens=False)["input_ids"]
        # replay token-by-token; gate should reach a blocked state for `want=True`
        prior, blocked_at = "", None
        for tid in ids:
            piece = tok.decode([tid])
            if m.would_block(prior, piece):
                blocked_at = prior + piece
                break
            prior += piece
        got = blocked_at is not None
        if got != want:
            fails.append(f"{s!r} want_block={want} got={got} (segmented as {len(ids)} tokens)")
    if fails:
        print("TOK-SELFTEST FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"TOK-SELFTEST PASS: real-tokenizer seam handling correct for {model_path}")
    return 0


if __name__ == "__main__":
    import sys
    if "--tok-selftest" in sys.argv:
        i = sys.argv.index("--tok-selftest")
        path = sys.argv[i + 1] if i + 1 < len(sys.argv) else "Qwen/Qwen2.5-Coder-7B"
        raise SystemExit(_tok_selftest(path))
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
