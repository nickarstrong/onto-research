# patch_topics.ps1 — replace inline TOPICS list with import
$file = "C:\Projects\onto-research\lab\dpo\rung1_wiring_v0.py"
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

$inBlock = $false
$blockStart = -1
$blockEnd = -1

for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*TOPICS\s*=\s*\[') {
        $inBlock = $true
        $blockStart = $i
    }
    if ($inBlock -and $lines[$i] -match '^\s*\]') {
        $blockEnd = $i
        break
    }
}

if ($blockStart -lt 0 -or $blockEnd -lt 0) {
    Write-Host "ERROR: TOPICS block not found"; exit 1
}

Write-Host "Found TOPICS block: lines $($blockStart+1)..$($blockEnd+1)"

$before = $lines[0..($blockStart-1)]
$after = $lines[($blockEnd+1)..($lines.Count-1)]
$replacement = "from rung1_build_topics import TOPICS  # 65 held-out topics for BUILD"

$newLines = $before + $replacement + $after
[System.IO.File]::WriteAllLines($file, $newLines, [System.Text.Encoding]::UTF8)

Write-Host "PATCHED: $file"
Write-Host "  Removed lines $($blockStart+1)..$($blockEnd+1), inserted import."
