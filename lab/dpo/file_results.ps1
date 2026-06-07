# file_results.ps1 - permanent. File run results: Downloads -> lab\dpo layout, clean, git.
# Usage: .\file_results.ps1 -E 11
param([Parameter(Mandatory=$true)][int]$E)
$dpo = "C:\Projects\onto-research\lab\dpo"
$dl = "C:\Users\Arist\Downloads"
# adapter -> adapters\ (NOT git)
$ad = Get-ChildItem "$dl\adapter_E$($E)_*.zip" -ErrorAction SilentlyContinue
if ($ad) { $ad | ForEach-Object { Move-Item $_.FullName "$dpo\adapters\$($_.Name)" -Force; Write-Output "moved: $($_.Name)" } }
else { Write-Output "no adapter zip in Downloads (already filed or not downloaded)" }
# eval artifacts (reports/json/logs with _E<N>) -> eval\
Get-ChildItem "$dl\*_E$E*" -Include *.json,*.md,*.txt,*.log -ErrorAction SilentlyContinue | ForEach-Object {
  Move-Item $_.FullName "$dpo\eval\$($_.Name)" -Force; Write-Output "moved: $($_.Name)" }
# dedup (1)-copies + trash
Get-ChildItem $dpo -Recurse -Filter "*(1)*" | Remove-Item -Force
Get-ChildItem $dpo -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
# git: data + eval + scripts + recipes only (weights/bait/held-out NEVER)
cd C:\Projects\onto-research
git add lab/dpo/eval lab/dpo/data lab/dpo/*.yaml lab/dpo/*.py lab/dpo/*.ps1 2>$null
git status --short
Write-Output "REVIEW status above, then: git commit -m '<msg>' ; git push origin main"
