# hygiene_gitignore_first.ps1 -- gitignore-first + tracked-data audit. ONE write (root .gitignore).
# No git add, no commit, no delete. Reversible: the appended block is marked; `git checkout .gitignore`.
$ErrorActionPreference = "Stop"
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$gi = Join-Path $root ".gitignore"

Write-Host "=== repo root ==="; Write-Host $root
Write-Host ""
Write-Host "=== (A) TRACKED-DATA AUDIT -- is any data ALREADY committed to public? (3.2) ==="
$tracked = git ls-files | Select-String -Pattern 'heldout|claims_blind|claims_enriched|bait|/sft/|outputs_E|report_E|eval_report_E|\.npz$|/logs/' 
if ($tracked) { Write-Host "FLAG -- data files tracked in public git:"; $tracked | ForEach-Object { Write-Host ("  " + $_) } }
else { Write-Host "CLEAN -- no data/held-out tracked in public git." }
Write-Host ""

$block = @"

# === ONTO lab data / held-out / weights -- LOCAL ONLY (3.2), never public [hygiene-nonyear] ===
lab/data/
lab/logs/
**/__pycache__/
*.npz
lab/dpo/*.log
lab/dpo/claims_enriched*.jsonl
lab/dpo/claims_blind*.jsonl
lab/dpo/*heldout*.jsonl
lab/dpo/data/*.json
lab/dpo/eval/*.json
lab/dpo/eval/o0/*.jsonl
"@

if ((Test-Path $gi) -and (Select-String -Path $gi -Pattern 'hygiene-nonyear' -Quiet)) {
  Write-Host "=== (B) block already present in .gitignore -- skip append ==="
} else {
  Write-Host "=== (B) appending data rules to root .gitignore ==="
  Add-Content -Path $gi -Value $block -Encoding UTF8
  Write-Host "appended. tail:"
  Get-Content $gi -Tail 14
}
Write-Host ""
Write-Host "=== (C) POST-IGNORE untracked count (IGNORE-DATA should be gone) ==="
$u = git status --porcelain --untracked-files=all | Select-String '^\?\?'
Write-Host ("untracked now: {0}" -f $u.Count)
$u | ForEach-Object { Write-Host ("  " + ($_ -replace '^\?\?\s+','')) }
Write-Host ""
Write-Host "DONE (gitignore-first). No commit/delete. If a data path still shows untracked above, tell me."
