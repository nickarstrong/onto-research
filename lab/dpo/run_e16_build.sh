#!/usr/bin/env bash
# run_e16_build.sh -- E16 SHIP v1 L4 self-test on RunPod (A5000, CUDA + DeBERTa).
# Run from the lab/dpo working dir (where the scripts + eval/_local/ fixtures live).
set -euo pipefail

# --- 0. pre-run: deberta-v3 tokenizer deps (fresh pod) -----------------------------------
pip -q install -U pyarrow datasets sentencepiece protobuf transformers accelerate >/dev/null

# --- 1. pre-run CUDA assert (no silent CPU) ----------------------------------------------
python3 - <<'PY'
import torch
assert torch.cuda.is_available(), "CUDA unavailable -> STOP (selftest refuses CPU)"
print("[cuda]", torch.cuda.get_device_name(0))
PY

# --- 2. pre-run: required inputs present + md5 (build_items_pre also gates, this is early) -
test -f eval/_local/gold_fixture_E25b.json || { echo "MISS eval/_local/gold_fixture_E25b.json"; exit 1; }
test -f eval/_local/heldout_E17.jsonl     || { echo "MISS eval/_local/heldout_E17.jsonl";     exit 1; }
md5sum eval/_local/gold_fixture_E25b.json eval/_local/heldout_E17.jsonl

# --- 3. run the self-test (G1/G2/G3 + integration drift guard) ----------------------------
python3 selftest_E16_L4.py
rc=$?

# --- 4. surface deliverables for Download (RunPod file browser shows /workspace) ----------
mkdir -p /workspace/e16_out
cp -f reports/report_E16_L4_selftest.md /workspace/e16_out/ 2>/dev/null || true
cp -f eval/_local/E42scale_readout.json /workspace/e16_out/ 2>/dev/null || true
echo "[out] /workspace/e16_out/  (download report_E16_L4_selftest.md)"
exit $rc
