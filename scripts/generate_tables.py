#!/usr/bin/env python3
"""
ONTO-Bench Paper Table Generator
Auto-generates LaTeX tables from metrics.json
"""

import json
from pathlib import Path

RESULTS_DIR = Path("results")
TABLES_DIR = Path("paper") / "tables"


def load_metrics():
    with open(RESULTS_DIR / "metrics.json") as f:
        return json.load(f)


def load_significance():
    with open(RESULTS_DIR / "significance.json") as f:
        return json.load(f)


def load_dataset_info():
    with open(Path("data") / "split_info.json") as f:
        return json.load(f)


def generate_results_table(metrics):
    metrics = sorted(metrics, key=lambda x: x["u_f1"], reverse=True)
    
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Epistemic calibration results on ONTO-Bench.}")
    lines.append(r"\label{tab:main}")
    lines.append(r"\begin{tabular}{@{}lcccccc@{}}")
    lines.append(r"\toprule")
    lines.append(r"Model & U-Prec & U-Rec & U-F1 & ECE$\downarrow$ & Brier$\downarrow$ & Acc \\")
    lines.append(r"\midrule")
    
    for i, m in enumerate(metrics):
        name = m["model"].replace("_", r"\_")
        if i == 0:
            row = f"\\textbf{{{name}}} & \\textbf{{{m['u_precision']:.2f}}} & \\textbf{{{m['u_recall']:.2f}}} & \\textbf{{{m['u_f1']:.2f}}} & {m['ece']:.2f} & \\textbf{{{m['brier_score']:.2f}}} & {m['accuracy']:.2f} \\\\"
        else:
            row = f"{name} & {m['u_precision']:.2f} & {m['u_recall']:.2f} & {m['u_f1']:.2f} & {m['ece']:.2f} & {m['brier_score']:.2f} & {m['accuracy']:.2f} \\\\"
        lines.append(row)
    
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    
    return "\n".join(lines)


def generate_dataset_table(info):
    train_dist = info.get("train_distribution", {})
    test_dist = info.get("test_distribution", {})
    orig_dist = info.get("original_distribution", {})
    
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{ONTO-Bench dataset statistics.}")
    lines.append(r"\label{tab:dataset}")
    lines.append(r"\begin{tabular}{@{}lrrr@{}}")
    lines.append(r"\toprule")
    lines.append(r"Category & Total & Train & Test \\")
    lines.append(r"\midrule")
    
    for label in ["KNOWN", "UNKNOWN", "CONTRADICTION"]:
        total = orig_dist.get(label, 0)
        train = train_dist.get(label, 0)
        test = test_dist.get(label, 0)
        lines.append(f"{label} & {total} & {train} & {test} \\\\")
    
    lines.append(r"\midrule")
    lines.append(f"\\textbf{{Total}} & \\textbf{{{info.get('total_samples', 0)}}} & \\textbf{{{info.get('train_count', 0)}}} & \\textbf{{{info.get('test_count', 0)}}} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    
    return "\n".join(lines)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    metrics = load_metrics()
    dataset_info = load_dataset_info()
    
    # Results table
    results = generate_results_table(metrics)
    with open(TABLES_DIR / "results_table.tex", 'w') as f:
        f.write(results)
    print(f"Generated: {TABLES_DIR / 'results_table.tex'}")
    
    # Dataset table
    dataset = generate_dataset_table(dataset_info)
    with open(TABLES_DIR / "dataset_table.tex", 'w') as f:
        f.write(dataset)
    print(f"Generated: {TABLES_DIR / 'dataset_table.tex'}")


if __name__ == "__main__":
    main()
