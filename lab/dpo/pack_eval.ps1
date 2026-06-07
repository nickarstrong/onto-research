# pack_eval.ps1 - build ONE GPU zip for eval generation run (PIPELINE v1)
# Usage: .\pack_eval.ps1 -E 12
# Stages: patched gen script (from onto_e5_gen.py template), heldout, bait,
#         leak corpus (sft + dpo pairs), adapter zip, run_eN_eval.sh
# Patch order matters: specific names FIRST, then global E5 -> EN.
param(
    [Parameter(Mandatory = $true)][int]$E,
    [string]$Sft = "sft_reflex_323.jsonl",
    [string]$GenTemplate = "onto_e5_gen.py"
)
$ErrorActionPreference = "Stop"
$lab = "C:\Projects\onto-research\lab\dpo"
Set-Location $lab

$eTag = "E$E"
$pairsName = "onto_e$($E)_dpo_pairs.jsonl"

$adapterZip = Get-ChildItem "adapters\adapter_$($eTag)_dpo_*.zip" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $adapterZip) { throw "STOP: no adapters\adapter_$($eTag)_dpo_*.zip" }
$adapterName = [System.IO.Path]::GetFileNameWithoutExtension($adapterZip.Name)

$required = @($GenTemplate, "data\$pairsName", "data\heldout_v1.3.jsonl", "data\bait_v2_n32.jsonl", "data\$Sft")
foreach ($f in $required) {
    if (-not (Test-Path $f)) { throw "STOP: missing $f" }
}

$stage = Join-Path $env:TEMP "eval_pack_$eTag"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

# --- patch gen script (template = E5) ---
$gen = Get-Content $GenTemplate -Raw
$rep1 = $pairsName
$gen = $gen.Replace("dpo_pairs_E5_v1.jsonl", $rep1)
$rep2 = $adapterName
$gen = $gen.Replace("adapter_E5_dpo_61", $rep2)
$rep3 = $Sft
$gen = $gen.Replace("sft_reflex_323.jsonl", $rep3)
$rep4 = $eTag
$gen = $gen.Replace("E5", $rep4)
$genName = "onto_e$($E)_gen.py"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Join-Path $stage $genName), $gen, $utf8NoBom)

# --- run script (LF endings) ---
$shLines = @(
    "#!/bin/bash",
    "set -e",
    "pip install -q -U datasets transformers accelerate peft `"bitsandbytes>=0.46.1`"",
    "unzip -o $($adapterZip.Name) -d adapter_unpack",
    "ls adapter_unpack",
    "ADAPTER_DIR=`$(dirname `$(find adapter_unpack -name adapter_config.json | head -n 1))",
    "echo ADAPTER_DIR=`$ADAPTER_DIR",
    "python $genName --adapter `"`$ADAPTER_DIR`"",
    "cp outputs_$eTag.json leak_report_$eTag.md /workspace/",
    "echo EVAL GEN DONE - download outputs_$eTag.json + leak_report_$eTag.md from /workspace"
)
$sh = ($shLines -join "`n") + "`n"
[System.IO.File]::WriteAllText((Join-Path $stage "run_e$($E)_eval.sh"), $sh, $utf8NoBom)

# --- stage data + adapter (flat: gen script opens flat names) ---
Copy-Item "data\heldout_v1.3.jsonl" $stage
Copy-Item "data\bait_v2_n32.jsonl" $stage
Copy-Item "data\$Sft" $stage
Copy-Item "data\$pairsName" $stage
Copy-Item $adapterZip.FullName $stage

# --- ONE zip ---
$zipPath = Join-Path (Join-Path $env:USERPROFILE "Downloads") "eval_pack_$eTag.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$stage\*" -DestinationPath $zipPath

Write-Host "===== STAGED ====="
Get-ChildItem $stage | Select-Object Name, Length
Write-Host "===== ZIP ====="
$z = Get-Item $zipPath
Write-Host ("PATH : " + $z.FullName)
Write-Host ("BYTES: " + $z.Length)
Write-Host "Upload via RunPod Upload button. Verify EXACT byte equality on pod BEFORE unzip."
