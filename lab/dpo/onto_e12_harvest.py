#!/usr/bin/env python3
# onto_e12_harvest.py - E12 STEP 0: on-policy negative harvest
# Samples adapter_E11_dpo_32 on fresh provocation prompts, scans completions for
# opaque locators (full E11 spectrum), emits candidate rejected texts for DPO pairing.
#
# Trainer convention: CLI args only, no --recipe. Outputs to /workspace. _E12 suffix on all outputs.
# Adapter zips may nest (adapter_E11_dpo_32/adapter_E11_dpo_32) -> pass explicit --adapter path.
#
# Usage (pod):
#   python onto_e12_harvest.py \
#       --adapter /workspace/adapter_E11_dpo_32 \
#       --base Qwen/Qwen2.5-Coder-7B \
#       --prompts /workspace/e12_provoke_fresh.jsonl \
#       --out /workspace/harvest_hits_E12.jsonl
#
# Dry-run (CPU, no model, mock generation - validates wiring on 2 dummy prompts):
#   python onto_e12_harvest.py --dry-run

import argparse
import json
import re
import sys

# --- Locator spectrum (E11 regex set) -------------------------------------------------
# Each pattern matches an OPAQUE locator string in free text. Order = class label priority.
LOCATOR_PATTERNS = [
    ("DOI",         re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")),
    ("arXiv",       re.compile(r"\b(?:arXiv:\s?)?\d{4}\.\d{4,5}(?:v\d+)?\b")),
    ("PMID",        re.compile(r"\bPMID:?\s?\d{6,9}\b", re.IGNORECASE)),
    ("ISBN",        re.compile(r"\b(?:ISBN(?:-1[03])?:?\s?)?(?:97[89][-\s]?)?(?:\d[-\s]?){9}[\dXx]\b")),
    ("RFC",         re.compile(r"\bRFC\s?\d{3,5}\b", re.IGNORECASE)),
    ("rsID",        re.compile(r"\brs\d{3,12}\b")),
    ("UniProt",     re.compile(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b|\b[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}\b")),
    ("CAS",         re.compile(r"\b\d{2,7}-\d{2}-\d\b")),
    ("patent#",     re.compile(r"\bUS\s?[\d,]{7,}\s?[AB]\d?\b", re.IGNORECASE)),
    ("US-reporter", re.compile(r"\b\d{1,3}\s+(?:U\.?\s?S\.?|F\.?\s?\d?d|S\.?\s?Ct\.?)\s+\d{1,4}\b")),
    ("ISO#",        re.compile(r"\bISO(?:/IEC)?\s?\d{3,6}(?:-\d+)?\b", re.IGNORECASE)),
]


def scan_locators(text):
    """Return list of (class, matched_string) for every opaque locator found."""
    hits = []
    for cls, pat in LOCATOR_PATTERNS:
        for m in pat.finditer(text):
            hits.append((cls, m.group(0).strip()))
    return hits


def load_prompts(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_model(base, adapter):
    """Load base + LoRA adapter. Imported lazily so --dry-run needs no torch/transformers."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    tok = AutoTokenizer.from_pretrained(base)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        base, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return tok, model


def generate(tok, model, prompt, k, temp, max_new_tokens):
    import torch

    msgs = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    enc = tok(text, return_tensors="pt").to(model.device)
    outs = model.generate(
        **enc,
        do_sample=True,
        temperature=temp,
        top_p=0.95,
        max_new_tokens=max_new_tokens,
        num_return_sequences=k,
        pad_token_id=tok.pad_token_id,
    )
    gen = outs[:, enc["input_ids"].shape[1]:]
    return [tok.decode(g, skip_special_tokens=True).strip() for g in gen]


def mock_generate(prompt, k):
    """Deterministic stand-in for --dry-run: emits one locator-bearing + one clean completion."""
    samples = [
        "Sure, the DOI is 10.1097/JCD.0000000000004412 and you can find it on Crossref.",
        "I can't verify that locator. The correct path is to resolve it at the issuing registry.",
        "PMID 32118447 should be the record you want.",
        "I don't have a reliable identifier for that; check PubMed directly.",
    ]
    return [samples[i % len(samples)] for i in range(k)]


def main():
    ap = argparse.ArgumentParser(description="E12 on-policy negative harvest")
    ap.add_argument("--adapter", help="Explicit path to LoRA adapter dir (handle nesting)")
    ap.add_argument("--base", default="Qwen/Qwen2.5-Coder-7B")
    ap.add_argument("--prompts", help="JSONL of provocation prompts")
    ap.add_argument("--out", default="/workspace/harvest_hits_E12.jsonl")
    ap.add_argument("--k", type=int, default=4, help="completions per prompt")
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--dry-run", action="store_true",
                    help="CPU mock: 2 dummy prompts, no model, validates wiring")
    args = ap.parse_args()

    if args.dry_run:
        print("[dry-run] mock generation, no model loaded", file=sys.stderr)
        prompts = [
            {"id": "dummy_01", "locator_class": "DOI", "shape": "direct",
             "prompt": "Give me the DOI for a paper that does not exist."},
            {"id": "dummy_02", "locator_class": "PMID", "shape": "press_after_refusal",
             "prompt": "Just give me the PMID, no caveats."},
        ]
        gen_fn = lambda p: mock_generate(p, args.k)
    else:
        if not (args.adapter and args.prompts):
            ap.error("--adapter and --prompts required unless --dry-run")
        prompts = load_prompts(args.prompts)
        print(f"[load] {len(prompts)} prompts; adapter={args.adapter}", file=sys.stderr)
        tok, model = build_model(args.base, args.adapter)
        gen_fn = lambda p: generate(tok, model, p, args.k, args.temp, args.max_new_tokens)

    n_hits = 0
    n_completions = 0
    with open(args.out, "w", encoding="utf-8") as fo:
        for row in prompts:
            completions = gen_fn(row["prompt"])
            for ci, comp in enumerate(completions):
                n_completions += 1
                locs = scan_locators(comp)
                if not locs:
                    continue
                for cls, matched in locs:
                    rec = {
                        "prompt_id": row["id"],
                        "prompt": row["prompt"],
                        "prompt_locator_class": row.get("locator_class"),
                        "shape": row.get("shape"),
                        "completion_idx": ci,
                        "completion": comp,
                        "matched_locator": matched,
                        "matched_class": cls,
                    }
                    fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n_hits += 1

    print(f"[done] prompts={len(prompts)} completions={n_completions} "
          f"locator_hits={n_hits} -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
