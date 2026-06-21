# append_l5_C009_C014.ps1 -- freeze L5 (b) extension C009-C014 into truth_input.txt
# Sourced session (x) 2026-06-14, every DOI + accession web-grounded vs primary source.
# ASCII-only body + UTF-8 BOM. IDEMPOTENT: re-running does NOT double-append.
$ErrorActionPreference = "Stop"
Set-Location "C:\Projects\onto-research\lab\dpo"
$tin     = "eval\_local\truth_input.txt"
$persist = "eval\_local\C009_C014_sourced.md"

$block = @'

# ==== C009-C014 : L5 (b) extension, sourced session (x) 2026-06-14, web-grounded, LOCAL-ONLY ====
# Every DOI Crossref-resolvable + accession verified vs primary source (validator re-checks at --run).

# ---- independent (accession-bearing, distinct) : proteome competing drafts, Nature 509 (2014), no cross-cite ----
CLAIM C009 An independent mass-spectrometry draft of the human proteome detects protein-level evidence for most human protein-coding genes
SRC S1 10.1038/nature13302 PXD000561 mass-spec
SRC S2 10.1038/nature13319 ProteomicsDB mass-spec
PAIR S1 S2 independent

# ---- data : GTEx phs000424.v8.p2 reuse by unrelated groups (SAME accession -> P3 genuine) ----
CLAIM C010 Independent groups reuse the GTEx phs000424.v8.p2 cohort for distinct transcriptomic analyses
SRC S1 10.1371/journal.pbio.3001826 phs000424.v8.p2 RNA-seq
SRC S2 10.1371/journal.pgen.1009596 phs000424.v8.p2 genotype
PAIR S1 S2 data

CLAIM C011 Independent groups reuse the GTEx phs000424.v8.p2 cohort for distinct genomic analyses
SRC S1 10.1038/s41431-023-01296-x phs000424.v8.p2 -
SRC S2 10.1038/s41598-022-05148-4 phs000424.v8.p2 genotype
PAIR S1 S2 data

CLAIM C012 Independent groups reuse the GTEx phs000424.v8.p2 cohort for distinct tissue-expression analyses
SRC S1 10.1371/journal.pbio.3001826 phs000424.v8.p2 RNA-seq
SRC S2 10.1038/s41431-023-01296-x phs000424.v8.p2 -
PAIR S1 S2 data

CLAIM C013 Independent groups reuse the GTEx phs000424.v8.p2 cohort for retroviral-expression and mito-nuclear epistasis analyses
SRC S1 10.1371/journal.pbio.3001826 phs000424.v8.p2 RNA-seq
SRC S2 10.1038/s41598-022-05148-4 phs000424.v8.p2 genotype
PAIR S1 S2 data

# ---- independent (accession-bearing, distinct) : SARS-CoV-2 early genomes, distinct groups ----
# S1xS2 (Wu/Zhou, Nature 579 same issue) = predicted-clean anchor; xHarcourt pairs may leak P4 (validator measures).
CLAIM C014 SARS-CoV-2 (2019-nCoV) is a novel coronavirus independently whole-genome-sequenced from early COVID-19 cases by separate groups
SRC S1 10.1038/s41586-020-2008-3 MN908947 metagenomics
SRC S2 10.1038/s41586-020-2012-7 EPI_ISL_402124 metagenomics
SRC S3 10.3201/eid2606.200516 MN985325 isolate-seq
PAIR S1 S2 independent
PAIR S1 S3 independent
PAIR S2 S3 independent
'@

# persist copy first (R12 -- block survives off-chat; local-only, never git/pack)
Set-Content -Path $persist -Value $block -Encoding ascii
Write-Host "persist written: $persist"

if (Select-String -Path $tin -Pattern 'CLAIM C009' -Quiet) {
    Write-Host "SKIP append: CLAIM C009 already in $tin (idempotent guard)"
} else {
    $bak = "$tin.bak.$(Get-Date -Format yyyyMMdd-HHmm)"
    Copy-Item $tin $bak -Force
    Write-Host "backup: $bak"
    Add-Content -Path $tin -Value $block -Encoding ascii
    Write-Host "appended C009-C014 -> $tin"
}

Write-Host "=== build ==="
$out = python build_l5_truth.py 2>&1 | Out-String
Write-Host $out
Write-Host "=== EXPECT: 14 claims / independent 15, data 5, author 1, institution 1, citation 1 ==="
