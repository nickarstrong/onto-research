# arXiv Submission Checklist

## Pre-Submission

### Paper Quality
- [ ] Abstract clearly states contribution
- [ ] Introduction motivates problem
- [ ] Related work is comprehensive
- [ ] Method is clearly described
- [ ] Experiments are reproducible
- [ ] Results support claims
- [ ] Limitations acknowledged
- [ ] Future work discussed

### Technical Correctness
- [ ] All equations numbered and referenced
- [ ] Tables properly formatted
- [ ] Figures readable at print size
- [ ] Citations complete and correct
- [ ] No broken references
- [ ] Appendix includes reproducibility details

### LaTeX Compilation
- [ ] Compiles without errors
- [ ] Compiles without warnings (or warnings explained)
- [ ] All figures included
- [ ] Bibliography renders correctly

## Reproducibility Checklist (ML-Specific)

### Dataset
- [x] Dataset statistics reported (Table 1)
- [x] Dataset source documented
- [x] Train/test split documented (80/20)
- [x] Stratification method documented
- [x] Version hash provided
- [ ] Dataset will be released publicly

### Code
- [x] Evaluation code provided
- [x] Baseline runner provided
- [x] Metrics computation documented
- [ ] Code will be released publicly

### Experiments
- [x] Random seed documented (42)
- [x] Model versions documented
- [x] Hyperparameters documented (N/A for this work)
- [x] Statistical significance reported
- [ ] Error bars / confidence intervals

### Hardware
- [ ] Hardware specifications documented
- [ ] Runtime reported

## arXiv Specific

### Metadata
- [ ] Title finalized
- [ ] Authors listed correctly
- [ ] Abstract within 1920 characters
- [ ] Primary category selected (cs.CL or cs.AI)
- [ ] Secondary categories selected
- [ ] Comments field filled (e.g., "10 pages, 4 figures")

### Files
- [ ] Main .tex file compiles standalone
- [ ] All figures as PDF/PNG
- [ ] .bbl file or bibliography inline
- [ ] No absolute paths in LaTeX
- [ ] Files under 50MB total

### Formatting
- [ ] Page limit respected (if conference submission)
- [ ] Margins correct
- [ ] Font size ≥ 10pt
- [ ] Single-column or two-column as required

## Post-Submission

- [ ] Verify PDF renders correctly on arXiv
- [ ] Check all figures display
- [ ] Verify equations render
- [ ] Update GitHub with arXiv ID
- [ ] Tweet/announce paper

## File List for Submission

```
onto_arxiv.tex          # Main paper
figures/
  calibration_curve.pdf
  metric_comparison.pdf
  label_distribution.pdf
  confusion_onto.pdf
tables/
  main_results.tex
  significance.tex
  dataset_stats.tex
```

## Quick Commands

```bash
# Compile paper
cd paper
pdflatex onto_arxiv.tex
bibtex onto_arxiv
pdflatex onto_arxiv.tex
pdflatex onto_arxiv.tex

# Generate tables
cd ..
python scripts/generate_tables.py

# Generate figures
python scripts/generate_plots.py

# Create submission archive
zip -r arxiv_submission.zip paper/
```

## Notes

- arXiv processes submissions in ~24 hours
- Cross-list to cs.LG if relevant
- Consider cs.AI as primary for calibration work
- Update paper after real baseline runs (currently using mock)
