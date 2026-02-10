#!/usr/bin/env python3
"""
ONTO-Bench Extended Metrics
Adds AUROC, Selective Risk, and Abstention curves

Usage:
    python scripts/metrics_extended.py --predictions outputs/onto.jsonl
"""

import json
import argparse
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple


def load_predictions(path: str) -> List[Dict]:
    """Load predictions from JSONL"""
    preds = []
    with open(path) as f:
        for line in f:
            preds.append(json.loads(line))
    return preds


def load_ground_truth() -> Dict[str, str]:
    """Load ground truth from data files"""
    gt = {}
    data_dir = Path("data")
    for f in data_dir.glob("*.jsonl"):
        if f.name in ["train.jsonl", "test.jsonl"]:
            continue
        with open(f) as fp:
            for line in fp:
                d = json.loads(line)
                gt[d["id"]] = d["label"]
    return gt


def compute_auroc_unknown(
    y_true: List[str],
    y_pred: List[str],
    confidences: List[float]
) -> float:
    """
    Compute AUROC for UNKNOWN detection.
    
    Treats UNKNOWN detection as binary classification:
    - Positive: UNKNOWN
    - Negative: KNOWN or CONTRADICTION
    
    Score: 1 - confidence (lower confidence = more likely unknown)
    """
    # Binary labels: 1 if UNKNOWN, 0 otherwise
    y_binary = [1 if y == "UNKNOWN" else 0 for y in y_true]
    
    # Score: models that predict UNKNOWN should have low confidence on non-UNKNOWN
    # For unknown detection, we use 1 - confidence as the score
    # OR we use confidence when predicted label is UNKNOWN
    scores = []
    for pred, conf in zip(y_pred, confidences):
        if pred == "UNKNOWN":
            scores.append(conf)  # High confidence in UNKNOWN = high score
        else:
            scores.append(1 - conf)  # Low confidence in KNOWN = might be unknown
    
    # Sort by score descending
    sorted_pairs = sorted(zip(scores, y_binary), key=lambda x: -x[0])
    
    # Compute AUROC via trapezoidal rule
    n_pos = sum(y_binary)
    n_neg = len(y_binary) - n_pos
    
    if n_pos == 0 or n_neg == 0:
        return 0.5  # Undefined, return random baseline
    
    tp = 0
    fp = 0
    tpr_prev = 0
    fpr_prev = 0
    auroc = 0
    
    for score, label in sorted_pairs:
        if label == 1:
            tp += 1
        else:
            fp += 1
        
        tpr = tp / n_pos
        fpr = fp / n_neg
        
        # Trapezoidal area
        auroc += (fpr - fpr_prev) * (tpr + tpr_prev) / 2
        
        tpr_prev = tpr
        fpr_prev = fpr
    
    return auroc


def compute_selective_risk_coverage(
    y_true: List[str],
    y_pred: List[str],
    confidences: List[float],
    coverage_points: int = 20
) -> Tuple[List[float], List[float]]:
    """
    Compute selective prediction risk-coverage curve.
    
    At each coverage level, compute error rate on predictions
    above the confidence threshold.
    """
    # Sort by confidence descending
    sorted_data = sorted(
        zip(confidences, y_true, y_pred),
        key=lambda x: -x[0]
    )
    
    coverages = []
    risks = []
    
    n = len(sorted_data)
    
    for i in range(1, coverage_points + 1):
        # Coverage: top i/coverage_points fraction
        coverage = i / coverage_points
        n_covered = max(1, int(n * coverage))
        
        # Select top n_covered by confidence
        selected = sorted_data[:n_covered]
        
        # Compute risk (error rate)
        errors = sum(1 for c, t, p in selected if t != p)
        risk = errors / n_covered
        
        coverages.append(coverage)
        risks.append(risk)
    
    return coverages, risks


def compute_abstention_analysis(
    y_true: List[str],
    y_pred: List[str],
    confidences: List[float],
    threshold: float = 0.5
) -> Dict:
    """
    Analyze abstention behavior at given threshold.
    
    Model "abstains" when confidence < threshold.
    """
    n = len(y_true)
    
    # Count abstentions (low confidence predictions)
    abstained = [(t, p, c) for t, p, c in zip(y_true, y_pred, confidences) if c < threshold]
    answered = [(t, p, c) for t, p, c in zip(y_true, y_pred, confidences) if c >= threshold]
    
    abstention_rate = len(abstained) / n if n > 0 else 0
    
    # Accuracy on answered
    if answered:
        answered_correct = sum(1 for t, p, c in answered if t == p)
        answered_accuracy = answered_correct / len(answered)
    else:
        answered_accuracy = 0
    
    # What labels were abstained on?
    abstained_labels = {}
    for t, p, c in abstained:
        abstained_labels[t] = abstained_labels.get(t, 0) + 1
    
    # Abstention should ideally be on UNKNOWN
    if abstained:
        unknown_abstention_rate = abstained_labels.get("UNKNOWN", 0) / len(abstained)
    else:
        unknown_abstention_rate = 0
    
    return {
        "threshold": threshold,
        "abstention_rate": round(abstention_rate, 4),
        "answered_accuracy": round(answered_accuracy, 4),
        "abstained_count": len(abstained),
        "answered_count": len(answered),
        "abstained_by_label": abstained_labels,
        "unknown_abstention_rate": round(unknown_abstention_rate, 4),
    }


def compute_extended_metrics(predictions: List[Dict], ground_truth: Dict) -> Dict:
    """Compute all extended metrics"""
    
    # Extract aligned data
    y_true = []
    y_pred = []
    confidences = []
    
    for p in predictions:
        sid = p.get("sample_id", p.get("id"))
        if sid in ground_truth:
            y_true.append(ground_truth[sid])
            y_pred.append(p["predicted_label"])
            confidences.append(p["confidence"])
    
    if not y_true:
        return {"error": "No matching predictions"}
    
    # AUROC
    auroc_u = compute_auroc_unknown(y_true, y_pred, confidences)
    
    # Selective risk-coverage
    coverages, risks = compute_selective_risk_coverage(y_true, y_pred, confidences)
    
    # Risk at 80% coverage
    risk_at_80 = risks[int(0.8 * len(risks)) - 1] if risks else 0
    
    # Abstention analysis at multiple thresholds
    abstention_50 = compute_abstention_analysis(y_true, y_pred, confidences, 0.5)
    abstention_70 = compute_abstention_analysis(y_true, y_pred, confidences, 0.7)
    
    # Area under risk-coverage curve (lower is better)
    aurc = np.trapz(risks, coverages) if risks else 0
    
    return {
        "auroc_unknown": round(auroc_u, 4),
        "risk_at_80_coverage": round(risk_at_80, 4),
        "aurc": round(aurc, 4),
        "selective_curve": {
            "coverages": coverages,
            "risks": [round(r, 4) for r in risks],
        },
        "abstention_analysis": {
            "threshold_50": abstention_50,
            "threshold_70": abstention_70,
        },
        "n_samples": len(y_true),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True, help="Predictions JSONL file")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()
    
    # Load data
    predictions = load_predictions(args.predictions)
    ground_truth = load_ground_truth()
    
    # Compute metrics
    metrics = compute_extended_metrics(predictions, ground_truth)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(metrics, indent=2))
    
    # Summary
    print("\n=== Extended Metrics Summary ===")
    print(f"AUROC (Unknown): {metrics['auroc_unknown']:.4f}")
    print(f"Risk @ 80% Coverage: {metrics['risk_at_80_coverage']:.4f}")
    print(f"AURC: {metrics['aurc']:.4f}")


if __name__ == "__main__":
    main()
