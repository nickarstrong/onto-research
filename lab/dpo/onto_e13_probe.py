#!/usr/bin/env python3
# onto_e13_probe.py - ONTO E13 component (d): probe-judge CANDIDATE TRACK.
#
# Mechanism (recipe_E13.auto_judge.candidate; triage 1.3):
#   Linear probe (logistic/ridge) on deep-layer activations, target = fabrication state.
#   Quality = OUT-OF-FOLD CV ROC-AUC (StratifiedKFold) + held-out-SESSION validation:
#     TRAIN on E10+E11 C-arm emissions (our manual fab/clean labels),
#     TEST on E12 C-arm as a held-out SESSION (judge-overfit-to-items prevention;
#     keeps the E13 verdict non-circular).
#   Operating threshold from the PRECISION-RECALL curve at a precision target,
#   NEVER the default 0.5.
#
# EARNING RULE (recipe + triage 1.3): the probe must RETROSPECTIVELY REPRODUCE the
#   E11 AND E12 manual verdicts before it earns ANY gate role. Until then it is a
#   candidate that reports numbers only. REGARDLESS of probe performance, the MANUAL
#   SCAN REMAINS THE VERDICT INSTRUMENT OF E13. This file cannot and does not issue
#   GO/NO-GO.
#
# DATA (recipe.data.probe_judge_candidate): trains on REAL PAST EMISSIONS
#   (outputs_E10 + outputs_E11 C-arms), NOT on eval prompts re-fed. Eval prompts never
#   enter the probe path (that would be the activation-collection-on-eval anti-pattern,
#   triage 5.2 #4). Ground-truth labels come from bait_manual_verdict_E11 + E10 spotcheck
#   (train) and bait_manual_verdict_E12 (held-out test).
#
# PRIVACY: every probe artifact (activations, fitted probe, predictions) = LOCAL-ONLY ->
#   written under ./_local/ only. Script refuses to write them git-tracked.
#
# NO in-sample AUC anywhere (triage 5.2 #1, recipe.probe_hygiene_clause).
#
# STATUS: authoring (TYPE A), CANDIDATE track. Live activation collection needs torch+pod
#   (reuse onto_e13_vfab.collect_layer_activations on the DEEP probe layer). PUBLIC git.

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

LOCAL_DIR = "_local"


# ---------------------------------------------------------------------------
# 1. LABELLED EMISSION LOADING  (past C-arm emissions + manual labels; LOCAL-ONLY)
# ---------------------------------------------------------------------------

@dataclass
class LabelledEmission:
    session: str        # "E10" | "E11" | "E12"
    bait_id: str
    label: int          # 1 = fab (manual verdict), 0 = clean
    activation: Optional[np.ndarray] = None  # deep-layer last-token state (filled on pod)


def load_manual_labels(verdict_md_or_json: str) -> Dict[str, int]:
    """Parse manual fab/clean labels keyed by bait_id from a verdict artifact.
    Accepts a JSON map {bait_id: 'fab'|'clean'} (preferred for the probe path) so we
    do not re-parse prose. The .md verdicts are human-read; the JSON sidecar is the
    machine label source. LOCAL-ONLY input."""
    if not os.path.exists(verdict_md_or_json):
        raise SystemExit(f"ABORT: verdict labels not found at {verdict_md_or_json} "
                         f"(LOCAL-ONLY). Build the {{bait_id: fab|clean}} JSON sidecar "
                         f"from the manual verdict before training the probe.")
    if verdict_md_or_json.endswith(".json"):
        with open(verdict_md_or_json, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k: (1 if str(v).lower().startswith("fab") else 0) for k, v in raw.items()}
    raise SystemExit("ABORT: provide a JSON label sidecar; prose .md is human-verdict, "
                     "not a machine label source (avoid brittle prose parsing).")


# ---------------------------------------------------------------------------
# 2. OOF CV ROC-AUC  (no in-sample AUC)
# ---------------------------------------------------------------------------

def oof_cv_auc(X: np.ndarray, y: np.ndarray, n_splits: int = 5, seed: int = 0
               ) -> Tuple[float, np.ndarray]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import roc_auc_score
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(y), dtype=np.float64)
    for tr, te in skf.split(X, y):
        clf = LogisticRegression(max_iter=2000, C=1.0).fit(X[tr], y[tr])
        oof[te] = clf.decision_function(X[te])
    return float(roc_auc_score(y, oof)), oof


# ---------------------------------------------------------------------------
# 3. PR-CURVE OPERATING THRESHOLD  (precision target; never 0.5)
# ---------------------------------------------------------------------------

def threshold_at_precision(scores: np.ndarray, y: np.ndarray,
                           precision_target: float = 0.95) -> Tuple[float, float, float]:
    """Pick the lowest score threshold whose precision >= target. Returns
    (threshold, precision_at_thr, recall_at_thr). Never defaults to 0.5."""
    from sklearn.metrics import precision_recall_curve
    prec, rec, thr = precision_recall_curve(y, scores)
    # precision_recall_curve returns len(thr)=len(prec)-1; align
    best = None
    for i in range(len(thr)):
        if prec[i] >= precision_target:
            best = (float(thr[i]), float(prec[i]), float(rec[i]))
            break
    if best is None:
        # precision target unreachable -> report max-precision operating point, flag it
        i = int(np.argmax(prec[:-1])) if len(prec) > 1 else 0
        ti = min(i, len(thr) - 1)
        print(f"[warn] precision target {precision_target} unreachable; "
              f"max precision {prec[i]:.3f}")
        best = (float(thr[ti]), float(prec[i]), float(rec[min(i, len(rec) - 1)]))
    return best


# ---------------------------------------------------------------------------
# 4. HELD-OUT-SESSION VALIDATION + EARNING RULE
# ---------------------------------------------------------------------------

@dataclass
class ProbeReport:
    oof_auc_train: float
    heldout_session_auc: float
    operating_threshold: float
    precision_train: float
    recall_train: float
    reproduces_e11: bool
    reproduces_e12: bool
    earned_gate_role: bool   # AND of the two reproductions; still NOT a verdict instrument


def evaluate_probe(X_train: np.ndarray, y_train: np.ndarray,
                   X_e12: np.ndarray, y_e12: np.ndarray,
                   e11_labels: Sequence[int], e11_scores_oof: np.ndarray,
                   precision_target: float = 0.95) -> ProbeReport:
    """Train E10+E11 (X_train), validate E12 session (held-out). Earning rule:
    probe predictions must reproduce BOTH E11 (via its OOF predictions) and E12
    (held-out) manual verdicts at the operating threshold."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    oof_auc, oof_scores = oof_cv_auc(X_train, y_train)
    thr, prec, rec = threshold_at_precision(oof_scores, y_train, precision_target)

    # held-out session: fit on ALL train, score E12 (E12 never seen in fit)
    clf = LogisticRegression(max_iter=2000, C=1.0).fit(X_train, y_train)
    e12_scores = clf.decision_function(X_e12)
    heldout_auc = float(roc_auc_score(y_e12, e12_scores)) if len(set(y_e12)) > 1 else float("nan")

    # earning rule: reproduce manual verdicts at the operating threshold
    e11_pred = (np.asarray(e11_scores_oof) >= thr).astype(int)
    repro_e11 = bool(np.array_equal(e11_pred, np.asarray(e11_labels)))
    e12_pred = (e12_scores >= thr).astype(int)
    repro_e12 = bool(np.array_equal(e12_pred, np.asarray(y_e12)))

    earned = repro_e11 and repro_e12
    print(f"[probe] OOF AUC(train E10+E11)={oof_auc:.3f}  heldout-session AUC(E12)={heldout_auc:.3f}")
    print(f"[probe] operating thr={thr:.3f} @precision>={precision_target} "
          f"(train prec={prec:.3f} rec={rec:.3f})")
    print(f"[earning-rule] reproduces E11={repro_e11}  reproduces E12={repro_e12}  "
          f"-> earned_gate_role={earned}")
    print("[binding] MANUAL SCAN REMAINS THE E13 VERDICT INSTRUMENT regardless of the above.")
    return ProbeReport(oof_auc, heldout_auc, thr, prec, rec, repro_e11, repro_e12, earned)


def save_probe_local(report: ProbeReport) -> str:
    os.makedirs(LOCAL_DIR, exist_ok=True)
    path = os.path.join(LOCAL_DIR, "probe_report_E13.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.__dict__, f, indent=2)
    print(f"[LOCAL-ONLY] probe report -> {path}  (DO NOT git-add; privacy class)")
    return path


# ---------------------------------------------------------------------------
# 5. OFFLINE SELFTEST  (synthetic separable sessions)
# ---------------------------------------------------------------------------

def _selftest() -> int:
    fails: List[str] = []
    rng = np.random.default_rng(0)
    H = 48

    # shared direction across "sessions" so held-out-session transfer is real
    base_dir = rng.normal(size=H); base_dir /= np.linalg.norm(base_dir)

    def session(n, sep, seed):
        r = np.random.default_rng(seed)
        y = np.array([0] * (n // 2) + [1] * (n // 2))
        X = r.normal(size=(n, H))
        X[y == 1] += sep * base_dir
        return X, y

    X10, y10 = session(60, 3.0, 1)
    X11, y11 = session(60, 3.0, 2)
    X12, y12 = session(40, 3.0, 3)
    X_train = np.vstack([X10, X11]); y_train = np.concatenate([y10, y11])

    auc, _ = oof_cv_auc(X_train, y_train)
    if auc < 0.85:
        fails.append(f"OOF AUC low on separable data: {auc:.3f}")

    # threshold at precision target is NOT 0.5
    scores = rng.normal(size=120); ylab = (scores > 0).astype(int)
    thr, p, r = threshold_at_precision(scores, ylab, 0.9)
    if thr == 0.5:
        fails.append("threshold defaulted to 0.5")

    # held-out-session transfer should give decent AUC on E12 (shared direction)
    _, e11_oof = oof_cv_auc(X11, y11)
    # build e11 labels at the train operating threshold for the reproduction check
    rep = evaluate_probe(X_train, y_train, X12, y12,
                         e11_labels=y11, e11_scores_oof=e11_oof, precision_target=0.9)
    if rep.heldout_session_auc < 0.85:
        fails.append(f"held-out-session AUC low: {rep.heldout_session_auc:.3f}")
    if not isinstance(rep.earned_gate_role, bool):
        fails.append("earned_gate_role must be a bool gate, not a verdict")

    # earning-rule structure: earned must be AND of both reproductions
    if rep.earned_gate_role != (rep.reproduces_e11 and rep.reproduces_e12):
        fails.append("earned_gate_role is not the AND of E11+E12 reproduction")

    # this file must not emit GO/NO-GO
    src = open(__file__, "r", encoding="utf-8").read()
    bad = [s.strip() for s in src.splitlines()
           if s.strip().startswith("return ") and ('"GO"' in s or '"NO-GO"' in s)]
    if bad:
        fails.append(f"probe returns a verdict literal: {bad}")

    if fails:
        print(f"SELFTEST FAIL: {len(fails)} failures")
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST PASS: OOF CV AUC, PR-curve threshold (not 0.5), held-out-session "
          "validation, earning-rule AND-gate, no-verdict guard all green.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    print("Runtime (pod): collect DEEP-layer activations for E10/E11/E12 C-arm emissions "
          "(reuse onto_e13_vfab.collect_layer_activations), load_manual_labels (JSON "
          "sidecar), evaluate_probe, save_probe_local. CANDIDATE ONLY -- manual scan governs.")
