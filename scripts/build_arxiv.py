#!/usr/bin/env python3
"""
arXiv Submission Builder
Creates submission-ready archive for arXiv

Output:
    arxiv_submission.zip
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(".")
PAPER_DIR = Path("paper")
OUTPUT_DIR = Path("arxiv_submission")


def clean_output():
    """Remove old submission directory"""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()


def copy_paper_files():
    """Copy paper LaTeX files"""
    # Main paper
    shutil.copy(PAPER_DIR / "onto_arxiv.tex", OUTPUT_DIR / "main.tex")
    
    # Appendix
    if (PAPER_DIR / "appendix_reproducibility.tex").exists():
        shutil.copy(PAPER_DIR / "appendix_reproducibility.tex", OUTPUT_DIR)
    
    # Tables
    tables_dir = OUTPUT_DIR / "tables"
    tables_dir.mkdir(exist_ok=True)
    for f in (PAPER_DIR / "tables").glob("*.tex"):
        shutil.copy(f, tables_dir)
    
    # Figures
    figures_dir = OUTPUT_DIR / "figures"
    figures_dir.mkdir(exist_ok=True)
    for f in (PAPER_DIR / "figures").glob("*.pdf"):
        shutil.copy(f, figures_dir)


def create_bbl_file():
    """Create .bbl bibliography (inline for arXiv)"""
    # arXiv prefers .bbl file or inline bibliography
    # Our template has inline bibliography, so skip this
    pass


def verify_compilation():
    """Attempt to compile LaTeX"""
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd=OUTPUT_DIR,
            capture_output=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("✓ LaTeX compilation successful")
            return True
        else:
            print("✗ LaTeX compilation failed (warnings may be OK)")
            return False
    except FileNotFoundError:
        print("⚠ pdflatex not found, skipping compilation check")
        return True
    except subprocess.TimeoutExpired:
        print("⚠ LaTeX compilation timed out")
        return False


def create_readme():
    """Create submission README"""
    readme = f"""# ONTO: Epistemically-Calibrated Reasoning for LLMs

## arXiv Submission

Submission date: {datetime.now().strftime('%Y-%m-%d')}

## Files

- main.tex: Main paper
- appendix_reproducibility.tex: Reproducibility appendix
- tables/: Auto-generated LaTeX tables
- figures/: Publication-quality figures

## Compilation

```bash
pdflatex main.tex
pdflatex main.tex  # Run twice for references
```

## Contact

anonymous@example.com
"""
    with open(OUTPUT_DIR / "README.txt", 'w') as f:
        f.write(readme)


def create_archive():
    """Create submission zip"""
    archive_name = "arxiv_submission"
    shutil.make_archive(archive_name, 'zip', OUTPUT_DIR)
    print(f"✓ Created {archive_name}.zip")
    return Path(f"{archive_name}.zip")


def generate_checklist():
    """Generate submission checklist status"""
    checks = {
        "Main paper exists": (PAPER_DIR / "onto_arxiv.tex").exists(),
        "Tables generated": (PAPER_DIR / "tables" / "results_table.tex").exists(),
        "Figures generated": (PAPER_DIR / "figures" / "metric_comparison.pdf").exists(),
        "Metrics computed": (Path("results") / "metrics.json").exists(),
        "Dataset versioned": Path("DATASET_VERSION.txt").exists(),
    }
    
    print("\n=== Submission Checklist ===")
    all_pass = True
    for item, status in checks.items():
        mark = "✓" if status else "✗"
        print(f"  {mark} {item}")
        if not status:
            all_pass = False
    
    return all_pass


def main():
    print("=== arXiv Submission Builder ===\n")
    
    # Check prerequisites
    if not generate_checklist():
        print("\n⚠ Some checks failed. Fix issues before submission.")
        print("  Run: python scripts/generate_tables.py")
        print("  Run: python scripts/generate_plots.py")
    
    print("\nBuilding submission package...")
    
    # Build
    clean_output()
    copy_paper_files()
    create_readme()
    
    # Verify
    verify_compilation()
    
    # Archive
    archive = create_archive()
    
    # Cleanup temp
    # shutil.rmtree(OUTPUT_DIR)  # Keep for inspection
    
    print(f"\n=== Done ===")
    print(f"Submission archive: {archive}")
    print(f"Submission folder: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("  1. Review PDF output")
    print("  2. Upload to arxiv.org")
    print("  3. Select categories: cs.CL, cs.AI")


if __name__ == "__main__":
    main()
