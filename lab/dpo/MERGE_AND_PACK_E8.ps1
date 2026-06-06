# MERGE_AND_PACK_E8.ps1  (ASCII-only, UTF-8 BOM)
# One command. Run from anywhere. Expands genpack -> merges LOCAL base 392 + P7
# -> verifies 418 -> packs RunPod GPU zip. Aborts loudly if any source missing.

$ErrorActionPreference = "Stop"
$lab     = "C:\Projects\onto-research\lab\dpo"
$genzip  = "C:\Users\Arist\Downloads\onto_e8_genpack.zip"
$base    = "$lab\data\sft_reflex_392.jsonl"
$heldout = "$lab\data\heldout_v1.3.jsonl"
$bait    = "$lab\data\bait_v2_n32.jsonl"
$trainer = "$lab\onto_exp1_e8_sft.py"

# 1. expand genpack into lab root
if (!(Test-Path $genzip)) { throw "MISSING genpack: $genzip" }
Expand-Archive -Path $genzip -DestinationPath $lab -Force
Write-Host "expanded genpack -> $lab"

# 2. preflight: every local source must exist (no silent guessing)
foreach ($p in @($base,$heldout,$bait,$trainer
                 "$lab\merge_and_pack_e8.py","$lab\sft_p7_pairs_E8.jsonl",
                 "$lab\recipe_E8.yaml")) {
  if (!(Test-Path $p)) { throw "MISSING required source: $p" }
}
Write-Host "preflight OK: all sources present"

# 3. verify shipped P7 md5 (must match recipe)
$p7md5 = (Get-FileHash "$lab\sft_p7_pairs_E8.jsonl" -Algorithm MD5).Hash.ToLower()
if ($p7md5 -ne "5c37133c92708254ef1d7ca7088f6dcf") {
  throw "P7 md5 mismatch: $p7md5 != 5c37133c92708254ef1d7ca7088f6dcf"
}
Write-Host "P7 md5 OK"

# 4. merge local 392 + 26 P7 -> 418
cd $lab
python merge_and_pack_e8.py --base $base --added "$lab\sft_p7_pairs_E8.jsonl" `
  --out "$lab\data\sft_reflex_418.jsonl" --expect 418
if ($LASTEXITCODE -ne 0) { throw "merge failed (count/schema)" }

# 5. pack RunPod GPU zip (data + frozen trainer/gen + recipe)
$stage = "$lab\_e8_stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item "$lab\data\sft_reflex_418.jsonl" $stage -Force
Copy-Item $heldout $stage -Force
Copy-Item $bait    $stage -Force
Copy-Item $trainer $stage -Force
Copy-Item "$lab\recipe_E8.yaml" $stage -Force
$gpuzip = "C:\Users\Arist\Downloads\onto_e8_runpod.zip"
if (Test-Path $gpuzip) { Remove-Item $gpuzip -Force }
Compress-Archive -Path "$stage\*" -DestinationPath $gpuzip -Force
Remove-Item $stage -Recurse -Force

# 6. clean trash
Get-ChildItem $lab -Recurse -Include "__pycache__","*_cache" -Directory -EA SilentlyContinue |
  Remove-Item -Recurse -Force -EA SilentlyContinue

Write-Host "`nDONE."
Write-Host "GPU zip: $gpuzip"
Write-Host "Upload onto_e8_runpod.zip to RunPod, extract, run recipe_E8 run_command."

