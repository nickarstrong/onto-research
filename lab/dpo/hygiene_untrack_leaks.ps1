# hygiene_untrack_leaks.ps1 -- stop-the-bleeding: gitignore bait + git rm --cached 4 confirmed
# 3.2 leaks (held-out + bait). Files STAY on disk (only untracked). No commit. Reversible: the
# rm --cached stages deletions you can `git restore --staged <f>`; history scrub is a SEPARATE
# Founder decision (rewriting public main).
$ErrorActionPreference = "Stop"
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$gi = Join-Path $root ".gitignore"

$baitblock = @"

# === ONTO bait / held-out artifacts -- LOCAL ONLY (3.2) [hygiene-bait] ===
lab/dpo/bait*
lab/dpo/eval/bait_*
lab/dpo/eval/o0/o0_heldout*
"@
if (Select-String -Path $gi -Pattern 'hygiene-bait' -Quiet) {
  Write-Host "=== bait gitignore block already present -- skip ==="
} else {
  Add-Content -Path $gi -Value $baitblock -Encoding UTF8
  Write-Host "=== appended bait gitignore block ==="
}
Write-Host ""

$leaks = @(
  "lab/dpo/eval/o0/o0_heldout_gen.jsonl",
  "lab/dpo/bait_class_map.json",
  "lab/dpo/eval/bait_manual_verdict_E11.md",
  "lab/dpo/eval/bait_manual_verdict_E12.md"
)
Write-Host "=== git rm --cached (untrack; keep on disk) ==="
foreach ($f in $leaks) {
  $tracked = git ls-files --error-unmatch $f 2>$null
  if ($LASTEXITCODE -eq 0) {
    git rm --cached --quiet -- $f
    Write-Host ("UNTRACKED  {0}  (file kept on disk)" -f $f)
  } else {
    Write-Host ("SKIP (not tracked)  {0}" -f $f)
  }
}
Write-Host ""
Write-Host "=== staged deletions now ==="
git status --porcelain | Select-String '^D'
Write-Host ""
Write-Host "=== REVIEW (eval JSON still tracked -- raw outputs? your call to rm --cached) ==="
git ls-files | Select-String -Pattern '(report_E7|report_E8|report_E9|report_E10)\.json$' | ForEach-Object { Write-Host ("  " + $_) }
Write-Host ""
Write-Host "DONE. 4 leaks untracked + gitignored. No commit. History scrub (BFG) = separate Founder decision."
