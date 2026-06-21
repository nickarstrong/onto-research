# hygiene_step2_dedup.ps1  -- deletes ONLY the 4 confirmed byte-dups in eval\_local\_local.
# Self-guard: re-checks each nested md5 == parent md5 LIVE before delete ; refuses on any mismatch.
# Leaves uniques (gate_E14.log, outputs_E14.json, v_fab_E13_L12.npz) and differs
# (harvest_E13.meta.json, sensor_thresholds_E13.json) UNTOUCHED. _local is gitignored -> no push.
$ErrorActionPreference = "Stop"
$root   = "C:\Projects\onto-research\lab\dpo"
$nested = Join-Path $root "eval\_local\_local"
$parent = Join-Path $root "eval\_local"
$targets = @("outputs_E10.json","outputs_E11.json","outputs_E12.json","probe_labels_E12.json")

function Md5($p) { (Get-FileHash -Algorithm MD5 -LiteralPath $p).Hash.ToLower() }

$deleted = 0
foreach ($name in $targets) {
  $nf = Join-Path $nested $name
  $pf = Join-Path $parent $name
  if (-not (Test-Path $nf)) { Write-Host ("SKIP (gone)   {0}" -f $name) ; continue }
  if (-not (Test-Path $pf)) { Write-Host ("REFUSE (no parent) {0}" -f $name) ; continue }
  if ((Md5 $nf) -eq (Md5 $pf)) {
    Remove-Item -LiteralPath $nf -Force
    Write-Host ("DELETED dup   {0}" -f $name)
    $deleted++
  } else {
    Write-Host ("REFUSE (md5 mismatch) {0}" -f $name)
  }
}
Write-Host ""
Write-Host ("deleted {0}/4 dups" -f $deleted)
Write-Host "=== eval\_local\_local REMAINING ==="
Get-ChildItem -LiteralPath $nested -File | ForEach-Object { Write-Host $_.Name }
Write-Host "(expect 5 remaining: gate_E14.log, harvest_E13.meta.json, outputs_E14.json, sensor_thresholds_E13.json, v_fab_E13_L12.npz)"
