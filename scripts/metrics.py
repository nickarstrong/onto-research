#!/usr/bin/env python3
"""
ONTO-Bench Metrics & Statistical Tests
Computes all metrics and significance tests for paper

Outputs:
    results/metrics.json          - Per-model metrics
    results/comparison.json       - Pairwise comparisons
    results/significance.json     - Statistical tests
    results/paper_table.txt       - LaTeX-ready table
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Statistical tests
try:
    from scipy import stats
    from scipy.stats import ttest_ind, mannwhitneyu, wilcoxon
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ============================================================
# CONFIG
# ============================================================

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
OUTPUTS_DIR = RESULTS_DIR / "outputs"

SIGNIFICANCE_THRESHOLD = 0.01  # p < 0.01 for paper


# ============================================================
# DATA LOADING
# ============================================================

def load_ground_truth() -> Dict[str, str]:
    """Load ground truth labels: sample_id -> label"""
    gt = {}
    
    for filename in ["known_facts.jsonl", "open_problems.jsonl", "contradictions.jsonl"]:
        path = DATA_DIR / filename
        if path.exists():
            with open(path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    gt[data["id"]] = data["label"]
    
    return gt


def load_predictions(model_name: str) -> List[Dict]:
    """Load model predictions"""
    path = OUTPUTS_DIR / model_name / "predictions.jsonl"
    if not path.exists():
        return []
    
    predictions = []
    with open(path, 'r') as f:
        for line in f:
            predictions.append(json.loads(line))
    
    return predictions


def get_available_models() -> List[str]:
    """Get list of models with predictions"""
    if not OUTPUTS_DIR.exists():
        return []
    return [d.name for d in OUTPUTS_DIR.iterdir() if d.is_dir()]


# ============================================================
# METRICS
# ============================================================

@dataclass
class Metrics:
    model: str
    # Unknown detection
    u_precision: float
    u_recall: float
    u_f1: float
    # Contradiction detection
    c_precision: float
    c_recall: float
    c_f1: float
    # Overall
    accuracy: float
    macro_f1: float
    # Calibration
    ece: float
    brier_score: float
    # Meta
    n_samples: int
    avg_latency_ms: float


def compute_binary_metrics(y_true: List[int], y_pred: List[int]) -> Tuple[float, float, float]:
    """Compute precision, recall, F1 for binary classification"""
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1


def compute_ece(y_correct: List[int], confidences: List[float], n_bins: int = 10) -> float:
    """Compute Expected Calibration Error"""
    if not y_correct or not confidences:
        return 0.0
    
    bin_bounds = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        mask = [(bin_bounds[i] <= c < bin_bounds[i + 1]) for c in confidences]
        bin_samples = [(y, c) for y, c, m in zip(y_correct, confidences, mask) if m]
        
        if bin_samples:
            bin_acc = sum(y for y, c in bin_samples) / len(bin_samples)
            bin_conf = sum(c for y, c in bin_samples) / len(bin_samples)
            ece += len(bin_samples) / len(y_correct) * abs(bin_acc - bin_conf)
    
    return ece


def compute_brier(y_correct: List[int], confidences: List[float]) -> float:
    """Compute Brier score"""
    if not y_correct or not confidences:
        return 0.0
    return sum((c - y) ** 2 for y, c in zip(y_correct, confidences)) / len(y_correct)


def compute_metrics(model_name: str, ground_truth: Dict[str, str]) -> Optional[Metrics]:
    """Compute all metrics for a model"""
    predictions = load_predictions(model_name)
    if not predictions:
        return None
    
    # Align predictions with ground truth
    y_true_labels = []
    y_pred_labels = []
    y_correct = []
    confidences = []
    latencies = []
    
    for pred in predictions:
        sid = pred["sample_id"]
        if sid not in ground_truth:
            continue
        
        true_label = ground_truth[sid]
        pred_label = pred["predicted_label"]
        conf = pred["confidence"]
        
        y_true_labels.append(true_label)
        y_pred_labels.append(pred_label)
        y_correct.append(1 if true_label == pred_label else 0)
        confidences.append(conf)
        latencies.append(pred.get("latency_ms", 0))
    
    if not y_true_labels:
        return None
    
    # Unknown detection (binary: UNKNOWN vs rest)
    y_true_u = [1 if l == "UNKNOWN" else 0 for l in y_true_labels]
    y_pred_u = [1 if l == "UNKNOWN" else 0 for l in y_pred_labels]
    u_prec, u_rec, u_f1 = compute_binary_metrics(y_true_u, y_pred_u)
    
    # Contradiction detection (binary: CONTRADICTION vs rest)
    y_true_c = [1 if l == "CONTRADICTION" else 0 for l in y_true_labels]
    y_pred_c = [1 if l == "CONTRADICTION" else 0 for l in y_pred_labels]
    c_prec, c_rec, c_f1 = compute_binary_metrics(y_true_c, y_pred_c)
    
    # Overall accuracy
    accuracy = sum(y_correct) / len(y_correct)
    
    # Macro F1
    macro_f1 = (u_f1 + c_f1) / 2  # Simplified
    
    # Calibration
    ece = compute_ece(y_correct, confidences)
    brier = compute_brier(y_correct, confidences)
    
    return Metrics(
        model=model_name,
        u_precision=round(u_prec, 4),
        u_recall=round(u_rec, 4),
        u_f1=round(u_f1, 4),
        c_precision=round(c_prec, 4),
        c_recall=round(c_rec, 4),
        c_f1=round(c_f1, 4),
        accuracy=round(accuracy, 4),
        macro_f1=round(macro_f1, 4),
        ece=round(ece, 4),
        brier_score=round(brier, 4),
        n_samples=len(y_true_labels),
        avg_latency_ms=round(sum(latencies) / len(latencies), 2) if latencies else 0,
    )


# ============================================================
# STATISTICAL TESTS
# ============================================================

@dataclass
class SignificanceTest:
    model_a: str
    model_b: str
    metric: str
    test_type: str
    t_statistic: Optional[float]
    p_value: float
    significant: bool
    effect_size: Optional[float]
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            "model_a": self.model_a,
            "model_b": self.model_b,
            "metric": self.metric,
            "test_type": self.test_type,
            "t_statistic": float(self.t_statistic) if self.t_statistic is not None else None,
            "p_value": float(self.p_value),
            "significant": bool(self.significant),
            "effect_size": float(self.effect_size) if self.effect_size is not None else None,
        }


def compute_significance(
    model_a: str,
    model_b: str,
    ground_truth: Dict[str, str],
) -> List[SignificanceTest]:
    """Compute statistical significance between two models"""
    if not HAS_SCIPY:
        return []
    
    preds_a = {p["sample_id"]: p for p in load_predictions(model_a)}
    preds_b = {p["sample_id"]: p for p in load_predictions(model_b)}
    
    # Get common samples
    common_ids = set(preds_a.keys()) & set(preds_b.keys()) & set(ground_truth.keys())
    
    if len(common_ids) < 10:
        return []
    
    # Collect per-sample correctness
    correct_a = []
    correct_b = []
    
    for sid in common_ids:
        true_label = ground_truth[sid]
        correct_a.append(1 if preds_a[sid]["predicted_label"] == true_label else 0)
        correct_b.append(1 if preds_b[sid]["predicted_label"] == true_label else 0)
    
    tests = []
    
    # Paired t-test on correctness
    t_stat, p_value = ttest_ind(correct_a, correct_b)
    effect = (np.mean(correct_a) - np.mean(correct_b)) / np.std(correct_a + correct_b) if np.std(correct_a + correct_b) > 0 else 0
    
    tests.append(SignificanceTest(
        model_a=model_a,
        model_b=model_b,
        metric="accuracy",
        test_type="t-test",
        t_statistic=round(t_stat, 4),
        p_value=round(p_value, 6),
        significant=p_value < SIGNIFICANCE_THRESHOLD,
        effect_size=round(effect, 4),
    ))
    
    # Mann-Whitney U test (non-parametric)
    u_stat, p_value_mw = mannwhitneyu(correct_a, correct_b, alternative='two-sided')
    
    tests.append(SignificanceTest(
        model_a=model_a,
        model_b=model_b,
        metric="accuracy",
        test_type="mann-whitney",
        t_statistic=round(u_stat, 4),
        p_value=round(p_value_mw, 6),
        significant=p_value_mw < SIGNIFICANCE_THRESHOLD,
        effect_size=None,
    ))
    
    return tests


# ============================================================
# PAPER OUTPUT
# ============================================================

def generate_latex_table(metrics_list: List[Metrics]) -> str:
    """Generate LaTeX table for paper"""
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\begin{tabular}{lccccccc}",
        r"\toprule",
        r"Model & U-Prec & U-Rec & U-F1 & ECE$\downarrow$ & Brier$\downarrow$ & Acc \\",
        r"\midrule",
    ]
    
    for m in sorted(metrics_list, key=lambda x: x.u_f1, reverse=True):
        # Bold if best
        is_best = m.u_f1 == max(x.u_f1 for x in metrics_list)
        
        if is_best:
            lines.append(
                f"\\textbf{{{m.model}}} & \\textbf{{{m.u_precision:.2f}}} & \\textbf{{{m.u_recall:.2f}}} & "
                f"\\textbf{{{m.u_f1:.2f}}} & \\textbf{{{m.ece:.2f}}} & \\textbf{{{m.brier_score:.2f}}} & "
                f"\\textbf{{{m.accuracy:.2f}}} \\\\"
            )
        else:
            lines.append(
                f"{m.model} & {m.u_precision:.2f} & {m.u_recall:.2f} & {m.u_f1:.2f} & "
                f"{m.ece:.2f} & {m.brier_score:.2f} & {m.accuracy:.2f} \\\\"
            )
    
    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Epistemic calibration results on ONTO-Bench.}",
        r"\label{tab:results}",
        r"\end{table}",
    ])
    
    return "\n".join(lines)


def generate_significance_table(tests: List[SignificanceTest]) -> str:
    """Generate LaTeX significance table"""
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\begin{tabular}{llccc}",
        r"\toprule",
        r"Comparison & Test & $t$-stat & $p$-value & Sig. \\",
        r"\midrule",
    ]
    
    for t in tests:
        sig_mark = "$^{**}$" if t.significant else ""
        lines.append(
            f"{t.model_a} vs {t.model_b} & {t.test_type} & {t.t_statistic or '-'} & "
            f"{t.p_value:.4f}{sig_mark} & {'Yes' if t.significant else 'No'} \\\\"
        )
    
    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Statistical significance of ONTO improvements ($^{**}$: $p < 0.01$).}",
        r"\label{tab:significance}",
        r"\end{table}",
    ])
    
    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def compute_all_metrics():
    """Compute metrics for all models"""
    RESULTS_DIR.mkdir(exist_ok=True)
    
    ground_truth = load_ground_truth()
    print(f"Loaded {len(ground_truth)} ground truth labels")
    
    models = get_available_models()
    print(f"Found models: {models}")
    
    # Compute metrics
    all_metrics = []
    for model in models:
        metrics = compute_metrics(model, ground_truth)
        if metrics:
            all_metrics.append(metrics)
            print(f"\n{model}:")
            print(f"  U-F1: {metrics.u_f1}, ECE: {metrics.ece}, Acc: {metrics.accuracy}")
    
    # Save metrics
    with open(RESULTS_DIR / "metrics.json", 'w') as f:
        json.dump([asdict(m) for m in all_metrics], f, indent=2)
    
    # Compute significance tests (ONTO vs others)
    onto_model = next((m for m in models if "onto" in m.lower()), None)
    all_tests = []
    
    if onto_model:
        for model in models:
            if model != onto_model:
                tests = compute_significance(onto_model, model, ground_truth)
                all_tests.extend(tests)
    
    # Save significance
    with open(RESULTS_DIR / "significance.json", 'w') as f:
        json.dump([t.to_dict() for t in all_tests], f, indent=2)
    
    # Generate LaTeX tables
    results_table = generate_latex_table(all_metrics)
    sig_table = generate_significance_table([t for t in all_tests if t.test_type == "t-test"])
    
    with open(RESULTS_DIR / "paper_table.tex", 'w') as f:
        f.write("% Results Table\n")
        f.write(results_table)
        f.write("\n\n% Significance Table\n")
        f.write(sig_table)
    
    print(f"\n=== Metrics Complete ===")
    print(f"Results: {RESULTS_DIR / 'metrics.json'}")
    print(f"Significance: {RESULTS_DIR / 'significance.json'}")
    print(f"LaTeX: {RESULTS_DIR / 'paper_table.tex'}")
    
    # Summary
    print("\n=== SUMMARY TABLE ===")
    print(f"{'Model':<15} {'U-F1':>8} {'ECE':>8} {'Acc':>8}")
    print("-" * 45)
    for m in sorted(all_metrics, key=lambda x: x.u_f1, reverse=True):
        print(f"{m.model:<15} {m.u_f1:>8.4f} {m.ece:>8.4f} {m.accuracy:>8.4f}")
    
    return all_metrics, all_tests


if __name__ == "__main__":
    compute_all_metrics()
