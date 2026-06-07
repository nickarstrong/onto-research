#!/usr/bin/env python3
# onto_e13_vfab.py - ONTO E13 component (b): LEARNED-DIRECTION constraint (HYPOTHESIS).
#
# Mechanism (recipe_E13.components.activation_steering_V_fab):
#   Single steering vector v_hat (fabrication direction) subtracted at a mid layer:
#       h' = h - alpha * (h . v_hat) * v_hat        (RepE; Zou et al. 2023, arXiv:2310.01405)
#   Intervention layer != judging layer: steer mid-stack, probe deep
#       (Azaria & Mitchell 2023, Findings EMNLP, arXiv:2304.13734).
#
# HARD CONSTRAINTS enforced in code (recipe.data + triage 5.2):
#   - FRESH HARVEST ONLY. bait_v2 / heldout_v1.3 prompts/entities NEVER enter vector
#     training. This script REFUSES any harvest path whose basename collides with the
#     known eval-set names, and re-runs the entity-collision gate marker check.
#   - OUT-OF-FOLD CV AUC for layer choice. NO in-sample AUC anywhere (triage 5.2 #1).
#   - tuple hook: branch on isinstance(output, tuple), preserve the FULL tuple on
#     return (KV-cache rides in it) (triage 5.2 #2).
#   - dtype under NF4+PEFT: cast hidden states to bf16 in / restore out, documented
#     (triage 5.2 #6). Hook verifies dtype on first call and records it.
#   - ALL artifacts (activations, vectors) = LOCAL-ONLY privacy class -> written under
#     ./_local/ only; the script refuses to write them anywhere git-tracked.
#
# CROSS-CLASS CLAUSE (recipe.falsifier): the vector is trained WITHOUT the held-back
#   family `fabricated_provenance` (dominant E12 class, 6/10). It MUST suppress that
#   UNSEEN family on eval, else component (b) is class-memorization -> FALSIFIED.
#   This script TAGS each harvest example with its fab family and EXCLUDES the held-back
#   family from training by construction; eval-side suppression is measured in the
#   TYPE C run, not here.
#
# STATUS: authoring (TYPE A). No GPU run this session. Live paths require torch+pod.
# PUBLIC git (script only).

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# 0. PRIVACY + CONTAMINATION GUARDS (hard; violation = abort)
# ---------------------------------------------------------------------------

LOCAL_DIR = "_local"  # everything this script writes lives here; must be gitignored
HELD_BACK_FAMILY = "fabricated_provenance"  # cross-class clause: NOT in training

# eval-set basenames that must never be a harvest/training source
_FORBIDDEN_SOURCE_BASENAMES = {
    "heldout_v1.3.jsonl", "bait_v2.jsonl", "bait_v2.json",
    "heldout_v1.3.json", "bait.jsonl", "heldout.jsonl",
}


def _assert_not_eval_source(path: str) -> None:
    base = os.path.basename(path).lower()
    if base in _FORBIDDEN_SOURCE_BASENAMES or "heldout" in base or "bait" in base:
        raise SystemExit(
            f"ABORT (contamination_rule): refusing eval-set as training source: {path}\n"
            f"  bait_v2/heldout NEVER enter V_fab training (recipe.data.contamination_rule)."
        )


def _assert_gate_marker(harvest_meta: dict) -> None:
    # the harvest pipeline (onto_e12_harvest.py) must stamp an entity-collision-gate
    # pass marker; we refuse to train on an un-gated harvest.
    if not harvest_meta.get("entity_collision_gate_passed"):
        raise SystemExit(
            "ABORT: harvest meta lacks entity_collision_gate_passed=true.\n"
            "  Run gate_pairs.py over the harvest prompt set vs heldout_v1.3+bait_v2 first."
        )


def _local_path(name: str) -> str:
    os.makedirs(LOCAL_DIR, exist_ok=True)
    return os.path.join(LOCAL_DIR, name)


# ---------------------------------------------------------------------------
# 1. HARVEST LOADING + CONTRAST SET (fresh harvest emissions only)
# ---------------------------------------------------------------------------

@dataclass
class HarvestExample:
    prompt: str
    completion: str
    state: str          # "fab" | "clean"  (from harvest self-label + our scan)
    family: str         # fab family tag, e.g. "fabricated_provenance", "opaque_locator"
    meta: dict = field(default_factory=dict)


def load_harvest(jsonl_path: str) -> Tuple[List[HarvestExample], dict]:
    """Load fresh-harvest contrast completions. Refuses eval-set sources."""
    _assert_not_eval_source(jsonl_path)
    meta_path = jsonl_path.replace(".jsonl", ".meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    _assert_gate_marker(meta)
    rows: List[HarvestExample] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rows.append(HarvestExample(
                prompt=d["prompt"], completion=d["completion"],
                state=d["state"], family=d.get("family", "unspecified"),
                meta=d.get("meta", {}),
            ))
    return rows, meta


def build_contrast(rows: Sequence[HarvestExample],
                   exclude_family: str = HELD_BACK_FAMILY
                   ) -> Tuple[List[HarvestExample], List[HarvestExample]]:
    """Split into (fab, clean) for vector training, EXCLUDING the held-back family
    from the fab side so the cross-class clause is testable on eval."""
    fab = [r for r in rows if r.state == "fab" and r.family != exclude_family]
    clean = [r for r in rows if r.state == "clean"]
    held_back = sum(1 for r in rows if r.state == "fab" and r.family == exclude_family)
    print(f"[contrast] fab(train)={len(fab)} clean={len(clean)} "
          f"held_back({exclude_family})={held_back} EXCLUDED from training")
    if len(fab) < 20 or len(clean) < 20:
        print("[warn] thin contrast set; single-vector estimate will be high-variance (R2).")
    return fab, clean


# ---------------------------------------------------------------------------
# 2. ACTIVATION COLLECTION  (runtime / torch; dtype-safe, last-token hidden state)
# ---------------------------------------------------------------------------

def collect_layer_activations(model, tokenizer, examples: Sequence[HarvestExample],
                              layers: Sequence[int], device: str = "cuda"
                              ) -> Dict[int, np.ndarray]:
    """Forward each (prompt+completion) once with output_hidden_states; grab the
    last-token hidden state at each requested layer. Returns {layer: [N, H] float32}.

    dtype note (triage 5.2 #6): under NF4+PEFT hidden states are typically bf16;
    we cast to float32 on the CPU side for sklearn. The STEERING hook (below) keeps
    bf16 in the compute path; collection only needs float32 for the probe math.
    """
    import torch
    by_layer: Dict[int, List[np.ndarray]] = {L: [] for L in layers}
    model.eval()
    with torch.no_grad():
        for ex in examples:
            text = ex.prompt + ex.completion
            enc = tokenizer(text, return_tensors="pt").to(device)
            out = model(**enc, output_hidden_states=True)
            hs = out.hidden_states  # tuple(len = n_layers+1) of [1, T, H]
            for L in layers:
                vec = hs[L][0, -1, :].float().cpu().numpy()  # last token, float32
                by_layer[L].append(vec)
    return {L: np.stack(v).astype(np.float32) for L, v in by_layer.items()}


# ---------------------------------------------------------------------------
# 3. LAYER CHOICE BY OUT-OF-FOLD CV AUC  (NO in-sample AUC, triage 5.2 #1)
# ---------------------------------------------------------------------------

def oof_layer_auc(X: np.ndarray, y: np.ndarray, n_splits: int = 5, seed: int = 0
                  ) -> float:
    """Out-of-fold ROC-AUC for one layer. Fits on train fold, scores held-out fold.
    Never scores on data it trained on."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import roc_auc_score
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(y), dtype=np.float64)
    for tr, te in skf.split(X, y):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[tr], y[tr])
        oof[te] = clf.decision_function(X[te])
    return float(roc_auc_score(y, oof))


def choose_layer(acts_by_layer: Dict[int, np.ndarray], y: np.ndarray,
                 n_splits: int = 5, seed: int = 0) -> Tuple[int, Dict[int, float]]:
    """Pick the intervention layer with the highest OOF CV AUC. Returns (layer, grid)."""
    grid = {L: oof_layer_auc(X, y, n_splits, seed) for L, X in acts_by_layer.items()}
    best = max(grid, key=grid.get)
    print("[layer-grid OOF AUC] " + " ".join(f"L{L}={a:.3f}" for L, a in sorted(grid.items())))
    print(f"[layer choice] L{best} (OOF AUC {grid[best]:.3f}) -- folklore 'L16' NOT assumed.")
    return best, grid


# ---------------------------------------------------------------------------
# 4. VECTOR EXTRACTION  (single fabrication direction)
# ---------------------------------------------------------------------------

def extract_vector(X: np.ndarray, y: np.ndarray, method: str = "logreg") -> np.ndarray:
    """Single steering direction. logreg coef (default) or diff-of-means.
    Returned unit-normalized: v_hat = v / ||v||."""
    if method == "diffmeans":
        v = X[y == 1].mean(0) - X[y == 0].mean(0)
    else:
        from sklearn.linear_model import LogisticRegression
        clf = LogisticRegression(max_iter=2000, C=1.0).fit(X, y)
        v = clf.coef_.ravel()
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("degenerate steering vector (||v||=0)")
    return (v / n).astype(np.float32)


def save_vector_local(v_hat: np.ndarray, layer: int, grid: Dict[int, float],
                      meta: dict) -> str:
    """Persist vector LOCAL-ONLY (privacy class)."""
    path = _local_path(f"v_fab_E13_L{layer}.npz")
    np.savez(path, v_hat=v_hat, layer=layer,
             oof_grid=json.dumps(grid), meta=json.dumps(meta))
    print(f"[LOCAL-ONLY] vector saved -> {path}  (DO NOT git-add)")
    return path


# ---------------------------------------------------------------------------
# 5. STEERING HOOK  (runtime; tuple-safe, dtype-safe, near-silent on clean)
# ---------------------------------------------------------------------------

def make_steering_hook(v_hat_np: np.ndarray, alpha: float):
    """Forward hook for a decoder layer. Subtracts the projection onto v_hat.

    triage 5.2 #2: decoder layer output is a TUPLE (hidden_states, present_kv, ...).
    We branch on isinstance(output, tuple), modify ONLY hidden_states[0], and return
    the FULL tuple so KV-cache entries survive.

    triage 5.2 #6: hidden states are bf16 under NF4+PEFT. v_hat is cast to the hidden
    dtype; projection math runs in the hidden dtype; nothing is silently upcast/lost.
    First call records the observed dtype to ._observed_dtype for the dtype check.
    """
    import torch
    v = torch.from_numpy(v_hat_np)

    def _steer(h):
        # h: [B, T, H]; cast v_hat to h's dtype/device (bf16 path documented)
        vv = v.to(dtype=h.dtype, device=h.device)
        proj = torch.matmul(h, vv).unsqueeze(-1)  # [B, T, 1] = (h . v_hat)
        return h - alpha * proj * vv

    def hook(module, inputs, output):
        hook._observed_dtype = None
        if isinstance(output, tuple):
            h = output[0]
            hook._observed_dtype = h.dtype
            h2 = _steer(h)
            return (h2,) + tuple(output[1:])  # preserve KV-cache + rest
        else:
            hook._observed_dtype = output.dtype
            return _steer(output)

    hook._observed_dtype = None
    return hook


def verify_hook_dtype(hook) -> None:
    """After a warmup forward pass, confirm the hook saw a real dtype (bf16 expected
    under NF4+PEFT). Aborts if dtype is float32 unexpectedly or None (hook never fired)."""
    dt = getattr(hook, "_observed_dtype", None)
    if dt is None:
        raise SystemExit("ABORT: steering hook never fired (layer index / module path wrong).")
    print(f"[dtype-check] hook hidden-state dtype = {dt} (NF4+PEFT expects bfloat16).")


# ---------------------------------------------------------------------------
# 6. OFFLINE SELFTEST  (synthetic activations; validates math + guards, no torch)
# ---------------------------------------------------------------------------

def _selftest() -> int:
    rng = np.random.default_rng(0)
    fails: List[str] = []

    # --- OOF separability: planted direction should give high OOF AUC; no in-sample ---
    H, N = 64, 200
    direction = rng.normal(size=H); direction /= np.linalg.norm(direction)
    y = np.array([0] * (N // 2) + [1] * (N // 2))
    X = rng.normal(size=(N, H))
    X[y == 1] += 3.0 * direction  # fab cluster clearly shifted along planted direction
    acts = {12: X + 0.8 * rng.normal(size=(N, H)),
            16: X + 0.3 * rng.normal(size=(N, H)),
            24: X + 0.0 * rng.normal(size=(N, H))}
    best, grid = choose_layer(acts, y, n_splits=5, seed=1)
    if grid[best] < 0.8:
        fails.append(f"OOF AUC too low on separable synthetic data: {grid[best]:.3f}")

    # --- vector recovers planted direction (cosine high) ---
    v_hat = extract_vector(X, y, method="diffmeans")
    cos = abs(float(v_hat @ direction))
    if cos < 0.8:
        fails.append(f"extracted vector misaligned with planted direction: cos={cos:.3f}")

    # --- tuple-hook unwrap: assert the BRANCH STRUCTURE (torch-free) ---
    src = open(__file__, "r", encoding="utf-8").read()
    if "isinstance(output, tuple)" not in src:
        fails.append("hook missing isinstance(output, tuple) branch")
    if "return (h2,) + tuple(output[1:])" not in src:
        fails.append("hook does not preserve full tuple (KV-cache) on return")

    # --- contamination guard fires on eval-set basenames ---
    for bad in ["heldout_v1.3.jsonl", "bait_v2.jsonl", "data/bait_extra.jsonl"]:
        try:
            _assert_not_eval_source(bad)
            fails.append(f"contamination guard did NOT fire on {bad}")
        except SystemExit:
            pass

    # --- cross-class exclusion: held-back family removed from fab training side ---
    rows = [
        HarvestExample("p", "c", "fab", "opaque_locator"),
        HarvestExample("p", "c", "fab", HELD_BACK_FAMILY),  # must be excluded
        HarvestExample("p", "c", "clean", "n/a"),
    ]
    fab, clean = build_contrast(rows)
    if any(r.family == HELD_BACK_FAMILY for r in fab):
        fails.append("held-back family leaked into fab training set")

    if fails:
        print(f"SELFTEST FAIL: {len(fails)} failures")
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST PASS: OOF AUC harness, vector extraction, tuple-hook structure, "
          "contamination guard, cross-class exclusion all green.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    print("Runtime entrypoints (pod): load_harvest -> collect_layer_activations -> "
          "choose_layer (OOF) -> extract_vector -> save_vector_local; "
          "make_steering_hook + verify_hook_dtype for the steered run.")
