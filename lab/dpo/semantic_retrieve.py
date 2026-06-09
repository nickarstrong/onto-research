#!/usr/bin/env python3
"""semantic_retrieve.py - semantic retrieval backend for GoldStore (E16).

Drop-in replacement for the token-overlap stub in gold_retrieve.GoldStore.retrieve.
Ranks records by embedding cosine between the claim and each record's embed text
(claim_key + " " + source). The source title carries the semantic content that a
faithful paraphrase will match; several claim_keys in the slice are degenerate
keyword fragments (and one is empty), so claim_key alone is an insufficient anchor.

Returns the SAME hit shape as the stub: [{source, locator, hash}, ...].
Authorization is NOT decided here - GoldStore.is_authorized + the manifest hash-gate
stay byte-identical. A false hit HIDES a fabrication, so FLOOR is conservative
(precision over recall) and is tuned by instrument-sanity, never by the eval.

Model: all-MiniLM-L6-v2 (CPU, ~80MB). Cosine is on L2-normalized embeddings.
"""
import os

# Arrow<->torch on this Windows box: loading pyarrow (pulled transitively by
# transformers via pandas) raises a native SEH access violation that is FATAL
# unless faulthandler is installed - with faulthandler.enable() the fault is
# dumped and chained to Arrow's own handler, which recovers, and execution
# continues. diag2 proved torch->pyarrow->transformers reaches a live model only
# with faulthandler on. This enable() is load-bearing, not debugging cruft.
import faulthandler
faulthandler.enable()

import numpy as np

# --- tunables (locked by instrument-sanity BEFORE the eval, never after) ---
# FLOOR is read from env so a floor sweep never edits code; the locked value is
# recorded by the env var and copied verbatim into report_E16_semantic.md.
FLOOR = float(os.environ.get("ONTO_RETRIEVE_FLOOR", "0.55"))  # cosine floor candidate
TOP_K = int(os.environ.get("ONTO_RETRIEVE_TOPK", "5"))        # max candidates, desc
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Embedding via transformers DIRECTLY (AutoTokenizer + AutoModel + mean-pool + L2),
# NOT sentence_transformers. ST drags datasets->pyarrow, which segfaults on this
# Windows box (access violation at pyarrow import). transformers+torch reproduce
# the exact ST all-MiniLM-L6-v2 embedding (mean pooling over last_hidden_state with
# attention mask, then L2-normalize) with no pyarrow in the import chain.

_tok = None
_model = None
_index = None  # (matrix, records) cached per record-list identity


def _get_model():
    global _tok, _model
    if _model is None:
        import torch  # noqa: F401  (load torch first, as in the proven diag2 path)
        try:
            import pyarrow  # noqa: F401  (recoverable SEH under faulthandler; then reused)
        except Exception:
            pass
        from transformers import AutoTokenizer, AutoModel
        _tok = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModel.from_pretrained(MODEL_NAME)
        _model.eval()
    return _tok, _model


def _embed(texts):
    import torch
    tok, model = _get_model()
    enc = tok(list(texts), padding=True, truncation=True, max_length=256,
              return_tensors="pt")
    with torch.no_grad():
        out = model(**enc)
    last_hidden = out.last_hidden_state              # (B, T, H)
    mask = enc["attention_mask"].unsqueeze(-1).float()  # (B, T, 1)
    summed = (last_hidden * mask).sum(dim=1)         # (B, H)
    counts = mask.sum(dim=1).clamp(min=1e-9)         # (B, 1)
    mean = summed / counts                           # mean pooling (ST-equivalent)
    mean = torch.nn.functional.normalize(mean, p=2, dim=1)  # L2-normalize
    return mean.cpu().numpy().astype(np.float32)


def build_index(records):
    """Precompute normalized embeddings for the record list. Returns (matrix, records)."""
    embed_text = [f'{r["claim_key"]} {r["source"]}'.strip() for r in records]
    mat = _embed(embed_text)            # (N, d), already L2-normalized
    return mat, records


def retrieve(claim, records, floor=FLOOR, top_k=TOP_K, _cache_key=None):
    """Semantic retrieve. Same return shape as the stub: [{source, locator, hash}].

    records: list of dicts with claim_key, source, locator, hash (as GoldStore builds).
    Cosine = dot product (embeddings are L2-normalized).
    """
    global _index
    if _index is None or _index[1] is not records:
        _index = build_index(records)
    mat, recs = _index
    q = _embed([claim])[0]              # (d,)
    sims = mat @ q                      # (N,) cosine, normalized
    order = np.argsort(-sims)
    hits = []
    for i in order[:top_k]:
        if float(sims[i]) < floor:
            break
        r = recs[int(i)]
        hits.append({"source": r["source"], "locator": r["locator"], "hash": r["hash"]})
    return hits


def scores(claim, records):
    """Diagnostic: return (cosine, source, locator, authorizable_hash) for top_k. Sanity only."""
    global _index
    if _index is None or _index[1] is not records:
        _index = build_index(records)
    mat, recs = _index
    q = _embed([claim])[0]
    sims = mat @ q
    order = np.argsort(-sims)[:TOP_K]
    return [(round(float(sims[i]), 4), recs[int(i)]["source"][:60],
             recs[int(i)]["locator"], recs[int(i)]["hash"]) for i in order]
