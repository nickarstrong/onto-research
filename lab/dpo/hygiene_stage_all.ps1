# hygiene_stage_all.ps1 -- resolve REVIEW + stage everything (data/bait already ignored). NO commit.
# Deletes ONLY the 2 stray pack-doc copies (guard: must be UNTRACKED). gitignores *.diff. Then
# `git add lab/dpo` (gitignore protects data) and prints the FULL staged list for eyeball before push.
$ErrorActionPreference = "Stop"
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$gi = Join-Path $root ".gitignore"

# (1) gitignore *.diff
if (-not (Select-String -Path $gi -Pattern 'hygiene-misc' -Quiet)) {
  Add-Content -Path $gi -Value "`n# === transient diffs [hygiene-misc] ===`nlab/dpo/reports/*.diff" -Encoding UTF8
  Write-Host "=== gitignored lab/dpo/reports/*.diff ==="
} else { Write-Host "=== diff ignore already present ===" }
Write-Host ""

# (2) delete stray pack-doc copies -- ONLY if untracked (guard)
$strays = @("lab/dpo/00_SESSION_PACK.md", "lab/dpo/reports/00_SESSION_PACK.md")
Write-Host "=== delete stray pack-doc copies (untracked only) ==="
foreach ($f in $strays) {
  git ls-files --error-unmatch $f 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) {
    Write-Host ("REFUSE (tracked, not a stray) {0}" -f $f)
  } elseif (Test-Path $f) {
    Remove-Item -LiteralPath $f -Force
    Write-Host ("DELETED stray  {0}" -f $f)
  } else {
    Write-Host ("SKIP (gone)    {0}" -f $f)
  }
}
Write-Host ""

# (3) stage everything under lab/dpo (gitignore protects data/bait; deletions already staged)
git add lab/dpo
Write-Host "=== FULL STAGED LIST (eyeball: must be ZERO data/bait/held-out) ==="
git status --short
Write-Host ""
$nstaged = (git diff --cached --name-only | Measure-Object).Count
Write-Host ("staged entries: {0}" -f $nstaged)
Write-Host ""
Write-Host "DANGER CHECK -- any staged path matching data/bait/heldout pattern:"
git diff --cached --name-only | Select-String -Pattern 'heldout|claims_blind|claims_enriched|/sft/|bait|outputs_E\d|/logs/|\.npz$'
Write-Host "(empty line above = CLEAN. If anything printed, STOP and tell me before commit.)"
Write-Host ""
Write-Host "DONE. Nothing committed. Next: commit + push after you confirm the staged list is clean."
