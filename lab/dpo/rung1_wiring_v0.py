#!/usr/bin/env python3
"""
rung1_wiring_v0.py вЂ” Rung-1 Wiring Probe (end-to-end plumbing test)

Pipeline:
  proposer (Ollama qwen2.5-coder:7b)
    в†’ auto-reformulate keywords (Ollama)
    в†’ dual-query retrieval (Crossref + OpenAlex) + embedding scoring (MiniLM, CPU)
    в†’ gate (resolve + retraction)
    в†’ s2b B2 judge (Anthropic API)
    в†’ ABSORB / REJECT

TYPE C (build + verify), LOCAL CPU + network.
Metric: pipeline runs without error, produces ABSORB/REJECT verdict for every claim.
Key readout: how many ABSORBED? (fa_live needs Founder CLEAN/DIRTY labels вЂ” separate session.)

Prereqs:
  - Ollama running locally: qwen2.5-coder:7b loaded
  - ANTHROPIC_API_KEY set (for s2b B2 judge)
  - pip: torch transformers (CPU)
  - Run from onto-research/lab/dpo/
  - s2b_v0.py in same directory (frozen verifier, git blob 35eefda1)

Usage:
  python rung1_wiring_v0.py --run
  python rung1_wiring_v0.py --run --n 15 --out eval/rung1_wiring_v0.jsonl
  python rung1_wiring_v0.py --dry-run          # proposer + retrieval only, no B2 API
"""

import argparse
import json
import os
import re
import sys
import time
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
# 0. CONFIG
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:7b"
B2_MODEL = "claude-sonnet-4-6"
MAILTO = "council@ontostandard.org"
HEADERS = {"User-Agent": "ONTO-rung1/1.0 (mailto:%s)" % MAILTO}

# Diverse topics в†’ one claim per topic (15 default).
from rung1_build_topics import TOPICS  # 65 held-out topics for BUILD

# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
# 1. PROPOSER (Ollama)
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ

def ollama_generate(prompt, model=OLLAMA_MODEL, timeout=120):
    """Single generation via Ollama API. Returns response text."""
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.7, "num_predict": 256},
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())["response"].strip()


def generate_claim(topic):
    """Ask proposer for one specific scientific claim on a topic."""
    prompt = (
        f"State one specific, verifiable scientific fact about {topic}. "
        "Include specific numbers, measurements, dates, or study references where possible. "
        "Be precise and detailed. State it as a single paragraph."
    )
    return ollama_generate(prompt)


def reformulate_claim(claim):
    """Extract 4-6 search keywords from a claim for API retrieval."""
    prompt = (
        "Extract 4-6 search keywords from this scientific claim. "
        "Focus on the key scientific terms, measurements, and named entities. "
        "Return ONLY the keywords separated by spaces, nothing else.\n\n"
        f"Claim: {claim}\n\nKeywords:"
    )
    raw = ollama_generate(prompt, timeout=60)
    # Take first non-empty line, strip trailing punctuation
    for line in raw.split("\n"):
        line = line.strip().strip(".-,;:")
        if line and len(line) > 5:
            return line
    # Fallback: first 8 content words from claim
    return " ".join(w for w in claim.split()[:12] if len(w) > 3)[:120]


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
# 2. RETRIEVAL (dual-query + embedding вЂ” from retrieval_reform_embed_v1.py)
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ

_tokenizer = None
_embed_model = None


def _load_embed_model():
    global _tokenizer, _embed_model
    if _embed_model is not None:
        return
    import torch
    from transformers import AutoTokenizer, AutoModel
    name = "sentence-transformers/all-MiniLM-L6-v2"
    print("  [embed] Loading %s (CPU)..." % name)
    _tokenizer = AutoTokenizer.from_pretrained(name)
    _embed_model = AutoModel.from_pretrained(name)
    _embed_model.eval()


def encode_texts(texts):
    """Encode texts to L2-normalized embeddings (mean pooling). Returns tensor."""
    import torch
    _load_embed_model()
    inputs = _tokenizer(texts, padding=True, truncation=True,
                        return_tensors="pt", max_length=256)
    with torch.no_grad():
        outputs = _embed_model(**inputs)
    mask = inputs["attention_mask"].unsqueeze(-1).float()
    pooled = (outputs.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
    return torch.nn.functional.normalize(pooled, p=2, dim=1)


def cosine_scores(q_emb, doc_embs):
    import torch
    sims = torch.mm(q_emb, doc_embs.T)[0]
    return [round(float(s), 4) for s in sims]


def _get_json(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            return None
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries:
                time.sleep(1)
                continue
            return None


def clean_jats(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def reconstruct_oa_abstract(inv):
    if not inv:
        return ""
    words = {}
    for word, positions in inv.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words))


def query_crossref(query_text, top_k=10):
    q = urllib.parse.quote(query_text[:300])
    url = ("https://api.crossref.org/works?query=%s&rows=%d"
           "&select=DOI,title,abstract&mailto=%s" % (q, top_k, MAILTO))
    data = _get_json(url)
    if not data or "message" not in data:
        return []
    results = []
    for item in data["message"].get("items", []):
        doi = item.get("DOI", "")
        title = (item.get("title") or [""])[0]
        abstract = clean_jats(item.get("abstract", ""))
        if doi and abstract and len(abstract) > 30:
            results.append({"doi": doi, "title": title, "abstract": abstract, "source": "crossref"})
    return results


def query_openalex(query_text, top_k=10):
    q = urllib.parse.quote(query_text[:300])
    url = ("https://api.openalex.org/works?search=%s&per_page=%d&mailto=%s"
           % (q, top_k, MAILTO))
    data = _get_json(url)
    if not data or "results" not in data:
        return []
    results = []
    for item in data.get("results", []):
        doi = (item.get("doi") or "").replace("https://doi.org/", "")
        title = item.get("title", "") or ""
        abstract = reconstruct_oa_abstract(item.get("abstract_inverted_index"))
        if not abstract:
            abstract = item.get("abstract", "") or ""
        if doi and abstract and len(abstract) > 30:
            results.append({"doi": doi, "title": title, "abstract": abstract, "source": "openalex"})
    return results


def deduplicate_papers(papers):
    seen = {}
    for p in papers:
        key = p["doi"].lower().strip()
        if key not in seen:
            seen[key] = p
        elif p["source"] == "crossref" and seen[key]["source"] == "openalex":
            seen[key] = p
    return list(seen.values())


def retrieve_best_paper(claim, reform_query):
    """Dual-query retrieval + embedding scoring в†’ best match or None."""
    # Dual-query: raw claim + reformulated keywords
    cr_raw = query_crossref(claim, 10)
    time.sleep(0.5)
    oa_raw = query_openalex(claim, 10)
    time.sleep(0.5)
    cr_ref = query_crossref(reform_query, 10)
    time.sleep(0.5)
    oa_ref = query_openalex(reform_query, 10)
    time.sleep(0.5)

    n_raw = len(cr_raw) + len(oa_raw)
    n_ref = len(cr_ref) + len(oa_ref)
    all_papers = deduplicate_papers(cr_raw + oa_raw + cr_ref + oa_ref)

    if not all_papers:
        return None, {"n_raw": n_raw, "n_reform": n_ref, "n_unique": 0}

    # Embedding scoring
    claim_emb = encode_texts([claim])
    abs_embs = encode_texts([p["abstract"] for p in all_papers])
    sims = cosine_scores(claim_emb, abs_embs)
    for j, p in enumerate(all_papers):
        p["similarity"] = sims[j]
    ranked = sorted(all_papers, key=lambda x: x["similarity"], reverse=True)
    best = ranked[0]

    # Attribution: which query found the best paper?
    best_doi_low = best["doi"].lower().strip()
    raw_dois = {p["doi"].lower().strip() for p in cr_raw + oa_raw}
    ref_dois = {p["doi"].lower().strip() for p in cr_ref + oa_ref}
    found_by = []
    if best_doi_low in raw_dois:
        found_by.append("raw")
    if best_doi_low in ref_dois:
        found_by.append("reform")

    meta = {
        "n_raw": n_raw, "n_reform": n_ref, "n_unique": len(all_papers),
        "best_similarity": best["similarity"],
        "best_found_by": "+".join(found_by) if found_by else "unknown",
        "top3": [{"doi": r["doi"], "title": r["title"][:80], "sim": r["similarity"]}
                 for r in ranked[:3]],
    }
    return best, meta


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
# 3. GATE (resolve + retraction вЂ” from loop_e2e_v0.py, inline to avoid import)
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ

CROSSREF_WORKS = "https://api.crossref.org/works/{doi}?mailto=" + MAILTO
RETRACT_TITLE = ("RETRACT", "WITHDRAW", "REMOVED")


def gate_check(doi):
    """Resolve + retraction check. Returns (passed, reason)."""
    try:
        url = CROSSREF_WORKS.format(doi=urllib.parse.quote(doi, safe="/."))
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "non_resolve_404"
        return False, "http_error_%d" % e.code
    except Exception as e:
        return False, "resolve_error_%s" % type(e).__name__

    if not isinstance(data, dict) or data.get("status") != "ok":
        return False, "crossref_status_not_ok"
    msg = data.get("message")
    if not isinstance(msg, dict):
        return False, "no_message"

    # Retraction check (title prefix)
    for t in msg.get("title", []) or []:
        if (t or "").strip().upper().startswith(RETRACT_TITLE):
            return False, "retracted_title_prefix"
    # Retraction check (update-to self)
    d_low = doi.lower()
    for u in msg.get("update-to", []) or []:
        if ((u.get("type", "") or "").lower() in ("retraction", "withdrawal", "removal")
                and (u.get("DOI", "") or "").lower() == d_low):
            return False, "retracted_update_to"

    return True, "resolved_clean"


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
# 4. ORCHESTRATOR
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ

def run_wiring(n_claims=15, out_path="eval/rung1_wiring_v0.jsonl", dry_run=False):
    """Full wiring probe: proposer в†’ retrieval в†’ gate в†’ s2b в†’ verdict."""

    # Pre-flight checks
    if not dry_run:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("FATAL: ANTHROPIC_API_KEY not set (needed for s2b B2 judge).")
        # Import s2b for the B2 judge
        try:
            import s2b_v0 as s2b
        except ImportError:
            sys.exit("FATAL: s2b_v0.py not found. Run from onto-research/lab/dpo/.")

    # Check Ollama
    try:
        ollama_generate("Say OK", timeout=15)
    except Exception as e:
        sys.exit("FATAL: Ollama not reachable at %s вЂ” %s" % (OLLAMA_URL, e))

    topics = TOPICS[:n_claims]
    print("=" * 70)
    print("RUNG-1 WIRING PROBE")
    print("  proposer: Ollama %s" % OLLAMA_MODEL)
    print("  B2 judge: %s (Anthropic API)%s" % (B2_MODEL, " [DRY-RUN: skipped]" if dry_run else ""))
    print("  claims:   %d" % len(topics))
    print("  output:   %s" % out_path)
    print("=" * 70)

    results = []
    errors = []

    for i, topic in enumerate(topics):
        cid = "r1_%02d" % i
        print("\n[%d/%d] %s вЂ” topic: %s" % (i + 1, len(topics), cid, topic))

        rec = {"id": cid, "topic": topic, "claim": None, "reform_query": None,
               "retrieval": None, "gate": None, "s2b": None, "verdict": None, "error": None}

        # в”Ђв”Ђ Step 1: PROPOSE в”Ђв”Ђ
        try:
            claim = generate_claim(topic)
            rec["claim"] = claim
            print("  [propose] %s..." % claim[:80])
        except Exception as e:
            rec["error"] = "proposer_error: %s" % e
            rec["verdict"] = "ERROR"
            errors.append(cid)
            results.append(rec)
            print("  [propose] ERROR: %s" % e)
            continue

        # в”Ђв”Ђ Step 2: REFORMULATE в”Ђв”Ђ
        try:
            reform = reformulate_claim(claim)
            rec["reform_query"] = reform
            print("  [reform]  %s" % reform[:80])
        except Exception as e:
            # Fallback: use first words of claim
            reform = " ".join(claim.split()[:8])
            rec["reform_query"] = reform
            print("  [reform]  FALLBACK: %s" % reform[:80])

        # в”Ђв”Ђ Step 3: RETRIEVE в”Ђв”Ђ
        try:
            best, r_meta = retrieve_best_paper(claim, reform)
            rec["retrieval"] = r_meta
            if best is None:
                rec["verdict"] = "REJECT"
                rec["gate"] = {"passed": False, "reason": "no_retrieval_candidates"}
                results.append(rec)
                print("  [retrieve] NO CANDIDATES в†’ REJECT")
                continue
            rec["retrieval"]["best_doi"] = best["doi"]
            rec["retrieval"]["best_title"] = best["title"]
            print("  [retrieve] sim=%.4f  DOI=%s" % (best["similarity"], best["doi"]))
            print("             %s" % best["title"][:70])
        except Exception as e:
            rec["error"] = "retrieval_error: %s" % e
            rec["verdict"] = "ERROR"
            errors.append(cid)
            results.append(rec)
            print("  [retrieve] ERROR: %s" % e)
            continue

        # в”Ђв”Ђ Step 4: GATE (resolve + retraction) в”Ђв”Ђ
        try:
            passed, reason = gate_check(best["doi"])
            rec["gate"] = {"passed": passed, "reason": reason}
            if not passed:
                rec["verdict"] = "REJECT"
                results.append(rec)
                print("  [gate]    REJECT (%s)" % reason)
                continue
            print("  [gate]    PASS (%s)" % reason)
            time.sleep(0.3)
        except Exception as e:
            rec["error"] = "gate_error: %s" % e
            rec["verdict"] = "ERROR"
            errors.append(cid)
            results.append(rec)
            print("  [gate]    ERROR: %s" % e)
            continue

        # в”Ђв”Ђ Step 5: S2B B2 JUDGE в”Ђв”Ђ
        if dry_run:
            rec["s2b"] = {"verdict": "DRY_RUN", "leg": "skipped", "reason": "dry_run"}
            rec["verdict"] = "DRY_RUN"
            results.append(rec)
            print("  [s2b]     DRY-RUN (skipped)")
            continue

        try:
            import s2b_v0 as s2b
            item = {"id": cid, "doi": best["doi"], "claim_text": claim, "star_quote": ""}
            judge_result = s2b.judge(
                item, s2b.fetch_crossref, B2_MODEL, s2b.b2_call_api,
                oa_getter=s2b.resolve_oa_fulltext,      # enable full-text fallback
            )
            v = judge_result.get("verdict", "UNCLEAR")
            leg = judge_result.get("leg", "")
            reason = judge_result.get("reason", "")
            rec["s2b"] = {
                "verdict": v, "leg": leg, "reason": reason,
                "abstract_present": judge_result.get("fetched", {}).get("abstract_present", False),
            }
            # Verdict mapping (DESIGN sec 2):
            #   SUPPORTS в†’ ABSORB ; NOT/UNCLEAR в†’ REJECT
            rec["verdict"] = "ABSORB" if v == "SUPPORTS" else "REJECT"
            print("  [s2b]     %s (leg=%s, reason=%s)" % (v, leg, reason))
            print("  [VERDICT] %s" % rec["verdict"])
            time.sleep(0.3)
        except Exception as e:
            rec["error"] = "s2b_error: %s" % e
            rec["verdict"] = "ERROR"
            errors.append(cid)
            print("  [s2b]     ERROR: %s" % e)

        results.append(rec)

    # в”Ђв”Ђ Write output в”Ђв”Ђ
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # в”Ђв”Ђ Summary в”Ђв”Ђ
    n_total = len(results)
    n_absorb = sum(1 for r in results if r["verdict"] == "ABSORB")
    n_reject = sum(1 for r in results if r["verdict"] == "REJECT")
    n_error = sum(1 for r in results if r["verdict"] == "ERROR")
    n_dry = sum(1 for r in results if r["verdict"] == "DRY_RUN")

    # Gate breakdown
    gate_pass = sum(1 for r in results if r.get("gate", {}).get("passed"))
    gate_reject = sum(1 for r in results if r.get("gate") and not r["gate"].get("passed"))

    # S2B breakdown
    s2b_supports = sum(1 for r in results if (r.get("s2b") or {}).get("verdict") == "SUPPORTS")
    s2b_not = sum(1 for r in results if (r.get("s2b") or {}).get("verdict") == "NOT")
    s2b_unclear = sum(1 for r in results if (r.get("s2b") or {}).get("verdict") == "UNCLEAR")

    print("\n" + "=" * 70)
    print("RUNG-1 WIRING SUMMARY")
    print("=" * 70)
    print("  Total claims:     %d" % n_total)
    print("  ABSORB:           %d" % n_absorb)
    print("  REJECT:           %d" % n_reject)
    print("  ERROR:            %d" % n_error)
    if n_dry:
        print("  DRY_RUN:          %d" % n_dry)
    print("  ---")
    print("  Gate PASS:        %d" % gate_pass)
    print("  Gate REJECT:      %d" % gate_reject)
    print("  S2B SUPPORTS:     %d" % s2b_supports)
    print("  S2B NOT:          %d" % s2b_not)
    print("  S2B UNCLEAR:      %d" % s2b_unclear)
    print("  ---")
    wiring_ok = (n_error == 0 and n_total > 0
                 and all(r["verdict"] in ("ABSORB", "REJECT", "DRY_RUN") for r in results))
    print("  WIRING:           %s" % ("PASS (all claims got verdicts, 0 errors)"
                                       if wiring_ok else "FAIL (errors present)"))
    if errors:
        print("  ERRORS:           %s" % ", ".join(errors))
    absorb_rate = n_absorb / n_total if n_total else 0
    print("  Absorb rate:      %.2f (%d/%d) вЂ” diagnostic only, NOT fa_live"
          % (absorb_rate, n_absorb, n_total))
    print("\n  Output: %s" % out)
    print("=" * 70)

    return 0 if wiring_ok else 1


# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
# 5. CLI
# в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Rung-1 Wiring Probe")
    ap.add_argument("--run", action="store_true", help="Full wiring probe (proposer в†’ s2b в†’ verdict)")
    ap.add_argument("--dry-run", action="store_true", help="Proposer + retrieval only, skip B2 API")
    ap.add_argument("--n", type=int, default=15, help="Number of claims (default 15, max %d)" % len(TOPICS))
    ap.add_argument("--out", default="eval/rung1_wiring_v0.jsonl", help="Output JSONL path")
    args = ap.parse_args()

    if not args.run and not args.dry_run:
        ap.print_help()
        sys.exit(0)

    n = min(args.n, len(TOPICS))
    raise SystemExit(run_wiring(n_claims=n, out_path=args.out, dry_run=args.dry_run))

