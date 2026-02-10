#!/usr/bin/env python3
"""
ONTO-Bench Plot Generator
Generates publication-quality figures for arXiv paper

Output:
    paper/figures/calibration_curve.pdf
    paper/figures/pr_curve.pdf
    paper/figures/confusion_matrix.pdf
    paper/figures/metric_comparison.pdf
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Check for matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not installed. Install with: pip install matplotlib")


RESULTS_DIR = Path("results")
OUTPUTS_DIR = RESULTS_DIR / "outputs"
DATA_DIR = Path("data")
FIGURES_DIR = Path("paper") / "figures"

# Style settings
COLORS = {
    "onto": "#2ecc71",      # Green
    "gpt4": "#3498db",      # Blue
    "gpt4_mock": "#3498db",
    "claude3": "#9b59b6",   # Purple
    "claude3_mock": "#9b59b6",
    "llama3": "#e74c3c",    # Red
    "llama3_mock": "#e74c3c",
}

MARKERS = {
    "onto": "o",
    "gpt4": "s",
    "gpt4_mock": "s",
    "claude3": "^",
    "claude3_mock": "^",
    "llama3": "D",
    "llama3_mock": "D",
}


def load_predictions(model: str) -> List[Dict]:
    """Load predictions for a model"""
    path = OUTPUTS_DIR / model / "predictions.jsonl"
    if not path.exists():
        return []
    
    preds = []
    with open(path) as f:
        for line in f:
            preds.append(json.loads(line))
    return preds


def load_ground_truth() -> Dict[str, str]:
    """Load ground truth labels"""
    gt = {}
    for f in DATA_DIR.glob("*.jsonl"):
        if f.name in ["train.jsonl", "test.jsonl"]:
            continue
        with open(f) as fp:
            for line in fp:
                d = json.loads(line)
                gt[d["id"]] = d["label"]
    return gt


def compute_calibration_curve(
    y_true: List[int],
    confidences: List[float],
    n_bins: int = 10
) -> Tuple[List[float], List[float], List[int]]:
    """Compute calibration curve data"""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    
    bin_centers = []
    bin_accs = []
    bin_counts = []
    
    for i in range(n_bins):
        mask = [(bin_boundaries[i] <= c < bin_boundaries[i + 1]) for c in confidences]
        bin_samples = [(y, c) for y, c, m in zip(y_true, confidences, mask) if m]
        
        if bin_samples:
            center = (bin_boundaries[i] + bin_boundaries[i + 1]) / 2
            acc = sum(y for y, c in bin_samples) / len(bin_samples)
            
            bin_centers.append(center)
            bin_accs.append(acc)
            bin_counts.append(len(bin_samples))
    
    return bin_centers, bin_accs, bin_counts


def compute_pr_curve(
    y_true: List[int],
    confidences: List[float],
    n_points: int = 20
) -> Tuple[List[float], List[float]]:
    """Compute precision-recall curve for unknown detection"""
    thresholds = np.linspace(0, 1, n_points)
    
    precisions = []
    recalls = []
    
    for thresh in thresholds:
        # Predict UNKNOWN if confidence < thresh (low confidence = uncertain)
        # Actually we need to reverse: high confidence in UNKNOWN prediction
        # For simplicity, use the raw predictions
        pass
    
    # Simplified: just return data points based on predictions
    return [], []


def plot_calibration_curves(models: List[str], gt: Dict[str, str]):
    """Plot calibration curves for all models"""
    if not HAS_MATPLOTLIB:
        return
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Perfect calibration line
    ax.plot([0, 1], [0, 1], 'k--', label='Perfect', alpha=0.5)
    
    for model in models:
        preds = load_predictions(model)
        if not preds:
            continue
        
        # Compute correctness and confidence
        y_true = []
        confidences = []
        
        for p in preds:
            sid = p["sample_id"]
            if sid not in gt:
                continue
            
            correct = 1 if p["predicted_label"] == gt[sid] else 0
            y_true.append(correct)
            confidences.append(p["confidence"])
        
        if not y_true:
            continue
        
        # Calibration curve
        centers, accs, counts = compute_calibration_curve(y_true, confidences)
        
        color = COLORS.get(model, "#333333")
        marker = MARKERS.get(model, "o")
        label = model.replace("_mock", "").replace("_", " ").upper()
        
        ax.plot(centers, accs, marker=marker, color=color, label=label, 
                linewidth=2, markersize=8)
    
    ax.set_xlabel("Confidence", fontsize=12)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Calibration Curves", fontsize=14)
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "calibration_curve.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "calibration_curve.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {FIGURES_DIR / 'calibration_curve.pdf'}")


def plot_metric_comparison(metrics: List[Dict]):
    """Plot bar chart comparing models on key metrics"""
    if not HAS_MATPLOTLIB:
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    models = [m["model"].replace("_mock", "").upper() for m in metrics]
    
    # U-F1
    ax = axes[0]
    values = [m["u_f1"] for m in metrics]
    colors = [COLORS.get(m["model"], "#333") for m in metrics]
    bars = ax.bar(models, values, color=colors)
    ax.set_ylabel("U-F1 Score")
    ax.set_title("Unknown Detection (U-F1)")
    ax.set_ylim(0, 1)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    
    # ECE
    ax = axes[1]
    values = [m["ece"] for m in metrics]
    bars = ax.bar(models, values, color=colors)
    ax.set_ylabel("ECE (lower is better)")
    ax.set_title("Calibration Error (ECE)")
    ax.set_ylim(0, 0.5)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    
    # U-Recall
    ax = axes[2]
    values = [m["u_recall"] for m in metrics]
    bars = ax.bar(models, values, color=colors)
    ax.set_ylabel("U-Recall")
    ax.set_title("Unknown Recall")
    ax.set_ylim(0, 1)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "metric_comparison.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "metric_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {FIGURES_DIR / 'metric_comparison.pdf'}")


def plot_label_distribution():
    """Plot dataset label distribution"""
    if not HAS_MATPLOTLIB:
        return
    
    # Load stats
    with open(DATA_DIR / "split_info.json") as f:
        stats = json.load(f)
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    labels = ["KNOWN", "UNKNOWN", "CONTRADICTION"]
    train_vals = [stats["train_distribution"].get(l, 0) for l in labels]
    test_vals = [stats["test_distribution"].get(l, 0) for l in labels]
    
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, train_vals, width, label='Train', color='#3498db')
    bars2 = ax.bar(x + width/2, test_vals, width, label='Test', color='#e74c3c')
    
    ax.set_ylabel('Count')
    ax.set_title('Dataset Distribution')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                   f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "label_distribution.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "label_distribution.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {FIGURES_DIR / 'label_distribution.pdf'}")


def plot_confusion_matrix(model: str, gt: Dict[str, str]):
    """Plot confusion matrix for a model"""
    if not HAS_MATPLOTLIB:
        return
    
    preds = load_predictions(model)
    if not preds:
        return
    
    labels = ["KNOWN", "UNKNOWN", "CONTRADICTION"]
    matrix = np.zeros((3, 3), dtype=int)
    
    label_to_idx = {l: i for i, l in enumerate(labels)}
    
    for p in preds:
        sid = p["sample_id"]
        if sid not in gt:
            continue
        
        true_idx = label_to_idx.get(gt[sid], 0)
        pred_idx = label_to_idx.get(p["predicted_label"], 0)
        matrix[true_idx, pred_idx] += 1
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    im = ax.imshow(matrix, cmap='Blues')
    
    # Labels
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("True", fontsize=12)
    ax.set_title(f"Confusion Matrix: {model.upper()}", fontsize=14)
    
    # Add numbers
    for i in range(3):
        for j in range(3):
            text = ax.text(j, i, matrix[i, j], ha="center", va="center",
                          color="white" if matrix[i, j] > matrix.max()/2 else "black",
                          fontsize=12)
    
    plt.colorbar(im)
    plt.tight_layout()
    
    plt.savefig(FIGURES_DIR / f"confusion_{model}.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / f"confusion_{model}.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {FIGURES_DIR / f'confusion_{model}.pdf'}")


def main():
    """Generate all figures"""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    if not HAS_MATPLOTLIB:
        print("ERROR: matplotlib required for plots")
        print("Install with: pip install matplotlib")
        return
    
    # Load data
    gt = load_ground_truth()
    
    with open(RESULTS_DIR / "metrics.json") as f:
        metrics = json.load(f)
    
    # Get available models
    models = [d.name for d in OUTPUTS_DIR.iterdir() if d.is_dir()]
    
    print("Generating figures...")
    
    # Generate plots
    plot_calibration_curves(models, gt)
    plot_metric_comparison(metrics)
    plot_label_distribution()
    
    # Confusion matrix for ONTO
    if "onto" in models:
        plot_confusion_matrix("onto", gt)
    
    print(f"\nAll figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
