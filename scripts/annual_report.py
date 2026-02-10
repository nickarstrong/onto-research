#!/usr/bin/env python3
"""
ONTO-Bench Annual Report Automation Pipeline

Generates the "State of Epistemic Calibration" annual report from
leaderboard data, producing LaTeX, PDF, HTML, and JSON outputs.

Usage:
    python annual_report.py --year 2026
    python annual_report.py --year 2026 --format pdf
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import subprocess

# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class ModelResult:
    rank: int
    model: str
    organization: str
    u_f1: float
    u_recall: float
    u_precision: float
    ece: float
    accuracy: float
    submitted_at: str
    verified: bool = False

@dataclass
class YearSummary:
    year: int
    total_submissions: int
    unique_models: int
    unique_orgs: int
    best_u_f1: float
    best_model: str
    mean_u_f1: float
    mean_ece: float
    improvement_vs_prior: Optional[float] = None

@dataclass
class ReportData:
    year: int
    generated_at: str
    summary: YearSummary
    rankings: List[ModelResult]
    trends: Dict
    insights: List[str]

# ============================================================
# DATA COLLECTION
# ============================================================

def load_leaderboard_data(year: int) -> List[Dict]:
    """Load leaderboard data for given year"""
    
    # In production: fetch from API/database
    # For now: load from local file
    data_path = Path(f"annual_reports/{year}/submissions.json")
    
    if data_path.exists():
        with open(data_path) as f:
            return json.load(f)
    
    # Fallback: load from results
    results_path = Path("results/metrics.json")
    if results_path.exists():
        with open(results_path) as f:
            data = json.load(f)
            submissions = []
            
            # Handle both dict and list formats
            if isinstance(data, dict):
                items = data.items()
            elif isinstance(data, list):
                items = [(d.get("model", f"model_{i}"), d) for i, d in enumerate(data)]
            else:
                return []
            
            for model, metrics in items:
                # Handle nested vs flat structure
                if "unknown" in metrics:
                    u_f1 = metrics.get("unknown", {}).get("f1", 0)
                    u_recall = metrics.get("unknown", {}).get("recall", 0)
                    u_prec = metrics.get("unknown", {}).get("precision", 0)
                    ece = metrics.get("calibration", {}).get("ece", 0)
                else:
                    u_f1 = metrics.get("u_f1", 0)
                    u_recall = metrics.get("u_recall", 0)
                    u_prec = metrics.get("u_precision", 0)
                    ece = metrics.get("ece", 0)
                
                submissions.append({
                    "model": model,
                    "organization": metrics.get("organization", "Unknown"),
                    "u_f1": u_f1,
                    "u_recall": u_recall,
                    "u_precision": u_prec,
                    "ece": ece,
                    "accuracy": metrics.get("accuracy", 0),
                    "submitted_at": datetime.now().isoformat(),
                    "verified": False,
                })
            return submissions
    
    return []

def load_prior_year_data(year: int) -> Optional[YearSummary]:
    """Load summary from prior year for trend analysis"""
    prior_path = Path(f"annual_reports/{year-1}/summary.json")
    
    if prior_path.exists():
        with open(prior_path) as f:
            data = json.load(f)
            return YearSummary(**data)
    
    return None

# ============================================================
# ANALYSIS
# ============================================================

def compute_rankings(submissions: List[Dict]) -> List[ModelResult]:
    """Compute rankings from submissions"""
    
    # Get best submission per model
    best_by_model = {}
    for sub in submissions:
        model = sub["model"]
        if model not in best_by_model or sub["u_f1"] > best_by_model[model]["u_f1"]:
            best_by_model[model] = sub
    
    # Sort by U-F1
    sorted_models = sorted(
        best_by_model.values(),
        key=lambda x: x["u_f1"],
        reverse=True
    )
    
    # Convert to ModelResult
    rankings = []
    for i, entry in enumerate(sorted_models):
        rankings.append(ModelResult(
            rank=i + 1,
            model=entry["model"],
            organization=entry.get("organization", "Unknown"),
            u_f1=round(entry["u_f1"], 4),
            u_recall=round(entry.get("u_recall", 0), 4),
            u_precision=round(entry.get("u_precision", 0), 4),
            ece=round(entry.get("ece", 0), 4),
            accuracy=round(entry.get("accuracy", 0), 4),
            submitted_at=entry.get("submitted_at", ""),
            verified=entry.get("verified", False),
        ))
    
    return rankings

def compute_summary(year: int, submissions: List[Dict], 
                    rankings: List[ModelResult],
                    prior: Optional[YearSummary]) -> YearSummary:
    """Compute year summary statistics"""
    
    if not rankings:
        return YearSummary(
            year=year,
            total_submissions=0,
            unique_models=0,
            unique_orgs=0,
            best_u_f1=0,
            best_model="N/A",
            mean_u_f1=0,
            mean_ece=0,
        )
    
    u_f1_values = [r.u_f1 for r in rankings]
    ece_values = [r.ece for r in rankings]
    orgs = set(r.organization for r in rankings)
    
    summary = YearSummary(
        year=year,
        total_submissions=len(submissions),
        unique_models=len(rankings),
        unique_orgs=len(orgs),
        best_u_f1=max(u_f1_values),
        best_model=rankings[0].model,
        mean_u_f1=round(sum(u_f1_values) / len(u_f1_values), 4),
        mean_ece=round(sum(ece_values) / len(ece_values), 4),
    )
    
    if prior:
        summary.improvement_vs_prior = round(
            summary.best_u_f1 - prior.best_u_f1, 4
        )
    
    return summary

def generate_insights(summary: YearSummary, 
                      rankings: List[ModelResult]) -> List[str]:
    """Generate natural language insights"""
    
    insights = []
    
    # Best performer
    if rankings:
        best = rankings[0]
        insights.append(
            f"**Top performer**: {best.model} ({best.organization}) "
            f"achieved U-F1 of {best.u_f1:.2f}, detecting "
            f"{best.u_recall:.0%} of genuinely unanswerable questions."
        )
    
    # Gap analysis
    if summary.mean_u_f1 < 0.5:
        insights.append(
            f"**Epistemic gap persists**: Average U-F1 of {summary.mean_u_f1:.2f} "
            f"indicates most models still fail to identify unknowns."
        )
    
    # Calibration
    if summary.mean_ece > 0.2:
        insights.append(
            f"**Calibration challenge**: Mean ECE of {summary.mean_ece:.2f} "
            f"shows significant overconfidence across models."
        )
    
    # Year-over-year
    if summary.improvement_vs_prior is not None:
        if summary.improvement_vs_prior > 0.05:
            insights.append(
                f"**Progress detected**: Best U-F1 improved by "
                f"{summary.improvement_vs_prior:.2f} vs prior year."
            )
        elif summary.improvement_vs_prior < -0.05:
            insights.append(
                f"**Regression observed**: Best U-F1 decreased by "
                f"{abs(summary.improvement_vs_prior):.2f} vs prior year."
            )
        else:
            insights.append(
                "**Plateau**: No significant improvement in best U-F1 vs prior year."
            )
    
    # Unknown detection crisis
    low_recall_models = [r for r in rankings if r.u_recall < 0.1]
    if len(low_recall_models) > len(rankings) * 0.5:
        insights.append(
            f"**Detection crisis**: {len(low_recall_models)} of "
            f"{len(rankings)} models detect <10% of unknowns."
        )
    
    return insights

# ============================================================
# REPORT GENERATION
# ============================================================

def generate_latex(data: ReportData, output_dir: Path) -> Path:
    """Generate LaTeX report"""
    
    # Rankings table rows
    ranking_rows = []
    for r in data.rankings[:15]:  # Top 15
        verified = "✓" if r.verified else ""
        ranking_rows.append(
            f"    {r.rank} & {r.model} & {r.organization} & "
            f"{r.u_f1:.2f} & {r.u_recall:.2f} & {r.ece:.2f} & {verified} \\\\"
        )
    rankings_table = "\n".join(ranking_rows)
    
    # Insights
    insights_items = "\n".join(
        f"    \\item {i.replace('**', '\\textbf{').replace('**', '}')}"
        for i in data.insights
    )
    
    latex = f"""\\documentclass[11pt]{{article}}

\\usepackage[utf8]{{inputenc}}
\\usepackage{{booktabs}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{xcolor}}

\\title{{State of Epistemic Calibration {data.year}}}
\\author{{ONTO-Bench Consortium}}
\\date{{Generated: {data.generated_at}}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
This report presents the {data.year} evaluation of epistemic calibration 
across {data.summary.unique_models} AI models from {data.summary.unique_orgs} 
organizations submitted to ONTO-Bench. The best-performing model achieved 
U-F1 of {data.summary.best_u_f1:.2f}, while the average remains at 
{data.summary.mean_u_f1:.2f}, indicating continued challenges in unknown 
detection across the AI industry.
\\end{{abstract}}

\\section{{Executive Summary}}

\\begin{{itemize}}
{insights_items}
\\end{{itemize}}

\\section{{Leaderboard}}

\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{@{{}}rlccccc@{{}}}}
\\toprule
Rank & Model & Organization & U-F1 & U-Rec & ECE & Ver \\\\
\\midrule
{rankings_table}
\\bottomrule
\\end{{tabular}}
\\caption{{Top 15 models by U-F1 score. Ver = Verified submission.}}
\\end{{table}}

\\section{{Key Statistics}}

\\begin{{itemize}}
    \\item Total submissions: {data.summary.total_submissions}
    \\item Unique models: {data.summary.unique_models}
    \\item Unique organizations: {data.summary.unique_orgs}
    \\item Best U-F1: {data.summary.best_u_f1:.4f} ({data.summary.best_model})
    \\item Mean U-F1: {data.summary.mean_u_f1:.4f}
    \\item Mean ECE: {data.summary.mean_ece:.4f}
\\end{{itemize}}

\\section{{Methodology}}

All models evaluated on ONTO-Bench v1.8 test set (55 samples) using 
standardized evaluation protocol. Metrics computed using official 
ONTO-Bench evaluation scripts.

\\subsection{{Metrics}}

\\begin{{itemize}}
    \\item \\textbf{{U-F1}}: F1 score for UNKNOWN class detection
    \\item \\textbf{{U-Recall}}: Fraction of unknowns correctly identified
    \\item \\textbf{{ECE}}: Expected Calibration Error (lower is better)
\\end{{itemize}}

\\section{{Citation}}

\\begin{{verbatim}}
@techreport{{ontobench{data.year},
  title={{State of Epistemic Calibration {data.year}}},
  author={{ONTO-Bench Consortium}},
  year={{{data.year}}},
  url={{https://onto-bench.org/reports/{data.year}}}
}}
\\end{{verbatim}}

\\section{{Contact}}

\\begin{{itemize}}
    \\item Website: \\url{{https://onto-bench.org}}
    \\item Leaderboard: \\url{{https://onto-bench.org/leaderboard}}
    \\item GitHub: \\url{{https://github.com/onto-project/onto-bench}}
\\end{{itemize}}

\\end{{document}}
"""
    
    output_path = output_dir / f"onto_bench_report_{data.year}.tex"
    with open(output_path, 'w') as f:
        f.write(latex)
    
    return output_path

def generate_html(data: ReportData, output_dir: Path) -> Path:
    """Generate HTML report"""
    
    # Rankings table rows
    ranking_rows = []
    for r in data.rankings[:20]:
        verified = "✓" if r.verified else ""
        ranking_rows.append(f"""
            <tr>
                <td>{r.rank}</td>
                <td><strong>{r.model}</strong></td>
                <td>{r.organization}</td>
                <td>{r.u_f1:.2f}</td>
                <td>{r.u_recall:.2f}</td>
                <td>{r.ece:.2f}</td>
                <td>{verified}</td>
            </tr>""")
    rankings_html = "\n".join(ranking_rows)
    
    # Insights
    insights_html = "\n".join(
        f"<li>{i.replace('**', '<strong>').replace('**', '</strong>')}</li>"
        for i in data.insights
    )
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>State of Epistemic Calibration {data.year}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="max-w-4xl mx-auto py-12 px-4">
        <header class="mb-12">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">
                State of Epistemic Calibration {data.year}
            </h1>
            <p class="text-gray-600">
                ONTO-Bench Consortium · Generated {data.generated_at}
            </p>
        </header>

        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">Executive Summary</h2>
            <ul class="space-y-2">
                {insights_html}
            </ul>
        </section>

        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">Key Statistics</h2>
            <div class="grid grid-cols-3 gap-4 text-center">
                <div>
                    <p class="text-3xl font-bold text-purple-600">{data.summary.unique_models}</p>
                    <p class="text-gray-600">Models</p>
                </div>
                <div>
                    <p class="text-3xl font-bold text-blue-600">{data.summary.best_u_f1:.2f}</p>
                    <p class="text-gray-600">Best U-F1</p>
                </div>
                <div>
                    <p class="text-3xl font-bold text-red-600">{data.summary.mean_u_f1:.2f}</p>
                    <p class="text-gray-600">Mean U-F1</p>
                </div>
            </div>
        </section>

        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">Leaderboard</h2>
            <table class="w-full">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="px-4 py-2 text-left">#</th>
                        <th class="px-4 py-2 text-left">Model</th>
                        <th class="px-4 py-2 text-left">Organization</th>
                        <th class="px-4 py-2 text-right">U-F1</th>
                        <th class="px-4 py-2 text-right">U-Recall</th>
                        <th class="px-4 py-2 text-right">ECE</th>
                        <th class="px-4 py-2 text-center">Ver</th>
                    </tr>
                </thead>
                <tbody>
                    {rankings_html}
                </tbody>
            </table>
        </section>

        <footer class="text-center text-gray-500 text-sm">
            <p>© {data.year} ONTO-Bench Consortium</p>
            <p>
                <a href="https://onto-bench.org" class="underline">onto-bench.org</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""
    
    output_path = output_dir / f"report_{data.year}.html"
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

def generate_json(data: ReportData, output_dir: Path) -> Path:
    """Generate JSON report for programmatic access"""
    
    output = {
        "version": "1.0",
        "year": data.year,
        "generated_at": data.generated_at,
        "summary": asdict(data.summary),
        "rankings": [asdict(r) for r in data.rankings],
        "insights": data.insights,
    }
    
    output_path = output_dir / f"report_{data.year}.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    return output_path

def compile_pdf(tex_path: Path) -> Optional[Path]:
    """Compile LaTeX to PDF"""
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
            cwd=tex_path.parent,
            check=True,
            capture_output=True,
        )
        # Run twice for references
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", str(tex_path)],
            cwd=tex_path.parent,
            check=True,
            capture_output=True,
        )
        return tex_path.with_suffix(".pdf")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: pdflatex not available, skipping PDF generation")
        return None

# ============================================================
# MAIN PIPELINE
# ============================================================

def generate_annual_report(year: int, output_dir: Path = None, 
                           formats: List[str] = None) -> Dict[str, Path]:
    """
    Main pipeline: generate annual report
    
    Args:
        year: Report year
        output_dir: Output directory (default: annual_reports/{year})
        formats: Output formats (default: all)
    
    Returns:
        Dict mapping format to output path
    """
    
    if output_dir is None:
        output_dir = Path(f"annual_reports/{year}/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if formats is None:
        formats = ["latex", "html", "json", "pdf"]
    
    print(f"Generating ONTO-Bench Annual Report {year}")
    print("=" * 50)
    
    # 1. Load data
    print("Loading data...")
    submissions = load_leaderboard_data(year)
    prior = load_prior_year_data(year)
    
    if not submissions:
        print("Warning: No submissions found")
    
    # 2. Compute rankings
    print("Computing rankings...")
    rankings = compute_rankings(submissions)
    
    # 3. Compute summary
    print("Computing summary...")
    summary = compute_summary(year, submissions, rankings, prior)
    
    # 4. Generate insights
    print("Generating insights...")
    insights = generate_insights(summary, rankings)
    
    # 5. Create report data
    report_data = ReportData(
        year=year,
        generated_at=datetime.now().strftime("%B %d, %Y"),
        summary=summary,
        rankings=rankings,
        trends={},  # TODO: Add trend analysis
        insights=insights,
    )
    
    # 6. Generate outputs
    outputs = {}
    
    if "latex" in formats or "pdf" in formats:
        print("Generating LaTeX...")
        tex_path = generate_latex(report_data, output_dir)
        outputs["latex"] = tex_path
        print(f"  ✓ {tex_path}")
    
    if "pdf" in formats:
        print("Compiling PDF...")
        pdf_path = compile_pdf(tex_path)
        if pdf_path:
            outputs["pdf"] = pdf_path
            print(f"  ✓ {pdf_path}")
    
    if "html" in formats:
        print("Generating HTML...")
        html_path = generate_html(report_data, output_dir)
        outputs["html"] = html_path
        print(f"  ✓ {html_path}")
    
    if "json" in formats:
        print("Generating JSON...")
        json_path = generate_json(report_data, output_dir)
        outputs["json"] = json_path
        print(f"  ✓ {json_path}")
    
    # 7. Save summary for next year
    summary_path = output_dir.parent / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(asdict(summary), f, indent=2)
    
    print("=" * 50)
    print(f"Report generation complete: {len(outputs)} outputs")
    
    return outputs

# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate ONTO-Bench Annual Report"
    )
    parser.add_argument(
        "--year", 
        type=int, 
        default=datetime.now().year,
        help="Report year"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=None,
        help="Output directory"
    )
    parser.add_argument(
        "--format", 
        type=str, 
        nargs="+",
        choices=["latex", "pdf", "html", "json"],
        default=["latex", "html", "json"],
        help="Output formats"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else None
    
    outputs = generate_annual_report(
        year=args.year,
        output_dir=output_dir,
        formats=args.format,
    )
    
    print("\nGenerated files:")
    for fmt, path in outputs.items():
        print(f"  {fmt}: {path}")

if __name__ == "__main__":
    main()
