# hygiene_nonyear_audit.ps1 -- READ-ONLY. Deletes nothing, adds nothing, stages nothing.
# Classifies the CURRENT untracked tree (live git status) into buckets, gitignore-first.
# Run from C:\Projects\onto-research\lab\dpo . Paste the whole output back.
$ErrorActionPreference = "Stop"
Set-Location "C:\Projects\onto-research\lab\dpo"

Write-Host "=== (0) CURRENT .gitignore (root of lab\dpo) ==="
if (Test-Path ".gitignore") { Get-Content .gitignore } else { Write-Host "(no .gitignore here)" }
Write-Host ""
Write-Host "=== branch / remote ==="
git rev-parse --abbrev-ref HEAD
git remote get-url origin
Write-Host ""

# ordered rules: first match wins. ASCII-only patterns on the git-relative path (forward slashes).
$rules = @(
  @{ b="IGNORE-DATA";   re='(^|/)__pycache__/' },
  @{ b="IGNORE-DATA";   re='\.(npz|log)$' },
  @{ b="IGNORE-DATA";   re='(^|/)(\.\./)?(data|logs)/' },
  @{ b="IGNORE-DATA";   re='(claims_enriched|claims_blind|heldout|probe_labels).*\.jsonl$' },
  @{ b="IGNORE-DATA";   re='(^|/)eval/(outputs_E|report_?E?\d|report_e\d|eval_report_E).*\.json$' },
  @{ b="IGNORE-DATA";   re='(^|/)eval/o0/.*\.jsonl$' },
  @{ b="REVIEW";        re='(^|/)(reports/)?00_SESSION_PACK\.md$' },
  @{ b="REVIEW";        re='(^|/)reports/(CONTINUITY_LOG|STATUS)\.md$' },
  @{ b="REVIEW";        re='\.diff$' },
  @{ b="REVIEW";        re='(^|/)eval/_local/' },
  @{ b="COMMIT-REPORT"; re='(^|/)(reports/|eval/).*(report|REPORT|PRE_REGISTER|SPEC_|leak_report|gate_report).*\.md$' },
  @{ b="COMMIT-SCRIPT"; re='\.(py|ps1)$' },
  @{ b="COMMIT-REPORT"; re='(^|/)reports/.*\.md$' }
)

$status = git status --porcelain --untracked-files=all
$buckets = @{}
foreach ($line in $status) {
  if ($line.Length -lt 4) { continue }
  $code = $line.Substring(0,2)
  $path = $line.Substring(3).Trim('"')
  if ($code -notmatch '\?\?') { continue }   # untracked only
  $p = $path -replace '\\','/'
  $hit = "REVIEW"
  foreach ($r in $rules) { if ($p -match $r.re) { $hit = $r.b; break } }
  if (-not $buckets.ContainsKey($hit)) { $buckets[$hit] = New-Object System.Collections.ArrayList }
  [void]$buckets[$hit].Add($path)
}

foreach ($b in @("IGNORE-DATA","COMMIT-SCRIPT","COMMIT-REPORT","DELETE-REGEN","REVIEW")) {
  $items = if ($buckets.ContainsKey($b)) { $buckets[$b] } else { @() }
  Write-Host ("=== {0}  ({1}) ===" -f $b, $items.Count)
  foreach ($i in $items) { Write-Host ("  {0}" -f $i) }
  Write-Host ""
}
Write-Host "READ-ONLY DONE. Nothing changed. Paste the full output; apply step (gitignore + scoped commit + delete) comes next."
