# hygiene_stage_all_v2.ps1 -- stderr-safe rewrite. Resolve REVIEW + stage. NO commit.
$ErrorActionPreference = "Continue"   # git plumbing writes stderr on normal misses; do not treat as fatal
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$gi = Join-Path $root ".gitignore"

# (1) gitignore *.diff (idempotent)
if (-not (Select-String -Path $gi -Pattern 'hygiene-misc' -Quiet)) {
  Add-Content -Path $gi -Value "`n# === transient diffs [hygiene-misc] ===`nlab/dpo/reports/*.diff" -Encoding UTF8
  Write-Host "=== gitignored *.diff ==="
} else { Write-Host "=== *.diff ignore already present ===" }
Write-Host ""

# (2) delete stray pack-doc copies -- ONLY if UNTRACKED (string check, no --error-unmatch)
$strays = @("lab/dpo/00_SESSION_PACK.md", "lab/dpo/reports/00_SESSION_PACK.md")
Write-Host "=== delete stray pack-doc copies (untracked only) ==="
foreach ($f in $strays) {
  $tracked = (git ls-files -- $f) 2>$null
  if (-not [string]::IsNullOrWhiteSpace($tracked)) {
    Write-Host ("REFUSE (tracked) {0}" -f $f)
  } elseif (Test-Path $f) {
    Remove-Item -LiteralPath $f -Force
    Write-Host ("DELETED stray  {0}" -f $f)
  } else {
    Write-Host ("SKIP (gone)    {0}" -f $f)
  }
}
Write-Host ""

# (3) stage everything under lab/dpo (gitignore protects data/bait; the 4 deletions already staged)
git add lab/dpo
Write-Host "=== FULL STAGED LIST ==="
git status --short
Write-Host ""
$nstaged = (git diff --cached --name-only | Measure-Object).Count
Write-Host ("staged entries: {0}" -f $nstaged)
Write-Host ""
Write-Host "=== DANGER CHECK (any staged data/bait/heldout) ==="
$danger = git diff --cached --name-only | Select-String -Pattern 'heldout|claims_blind|claims_enriched|/sft/|bait|outputs_E\d|/logs/|\.npz$'
if ($danger) { Write-Host "STOP -- data staged:"; $danger | ForEach-Object { Write-Host ("  " + $_) } }
else { Write-Host "CLEAN -- no data/bait/heldout staged." }
Write-Host ""
Write-Host "DONE. Nothing committed."
