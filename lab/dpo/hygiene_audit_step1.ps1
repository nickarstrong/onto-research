# hygiene_audit_step1.ps1  -- READ-ONLY. Deletes nothing. Tree-hygiene plane, step 1.
# (1) classify eval\_local\_local\ vs parent by LIVE md5  (DUP = safe-delete ; UNIQUE = keep)
# (2) list __pycache__ dirs (regenerable, safe-delete later)
# (3) harvest first 20 lines of every root *.py -> onto_index_harvest.txt (grounds 00_INDEX)
$ErrorActionPreference = "Stop"
$root   = "C:\Projects\onto-research\lab\dpo"
$nested = Join-Path $root "eval\_local\_local"
$parent = Join-Path $root "eval\_local"

function Md5($p) { (Get-FileHash -Algorithm MD5 -LiteralPath $p).Hash.ToLower() }

Write-Host "=== (1) NESTED eval\_local\_local CLASSIFY ==="
if (Test-Path $nested) {
  foreach ($f in Get-ChildItem -LiteralPath $nested -File) {
    $sib = Join-Path $parent $f.Name
    if (Test-Path $sib) {
      $a = Md5 $f.FullName ; $b = Md5 $sib
      if ($a -eq $b) { Write-Host ("DUP     {0}" -f $f.Name) }
      else           { Write-Host ("DIFFERS {0}  nested={1} parent={2}" -f $f.Name,$a.Substring(0,8),$b.Substring(0,8)) }
    } else {
      Write-Host ("UNIQUE  {0}  (no parent sibling -- KEEP/relocate)" -f $f.Name)
    }
  }
} else { Write-Host "nested dir absent" }

Write-Host ""
Write-Host "=== (2) __pycache__ DIRS (regenerable) ==="
$pyc = Get-ChildItem -LiteralPath $root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
if ($pyc) { $pyc | ForEach-Object { Write-Host $_.FullName } } else { Write-Host "none" }

Write-Host ""
Write-Host "=== (3) HARVEST root *.py docstrings -> onto_index_harvest.txt ==="
$out = Join-Path $root "onto_index_harvest.txt"
$sb  = New-Object System.Text.StringBuilder
foreach ($f in Get-ChildItem -LiteralPath $root -File -Filter "*.py" | Sort-Object Name) {
  [void]$sb.AppendLine("########## " + $f.Name + " ##########")
  $head = Get-Content -LiteralPath $f.FullName -TotalCount 20 -Encoding UTF8
  foreach ($ln in $head) { [void]$sb.AppendLine($ln) }
  [void]$sb.AppendLine("")
}
[System.IO.File]::WriteAllText($out, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))
$n = (Get-ChildItem -LiteralPath $root -File -Filter "*.py").Count
Write-Host ("harvested {0} root .py files -> {1}" -f $n,$out)
Write-Host ""
Write-Host "DONE. Upload onto_index_harvest.txt + paste the (1)/(2) output above."
