# pack_runpod_e14.ps1 - E14-shaped stage script (recipe_E14 = decode-time, NOT DPO-train).
# E14 = E13 design with corrected delta-metric sensor calibration (v39 ALL-alpha ABORT
# fix, commit ed2af5a). Copy of pack_runpod_e13.ps1 with E13->E14 names + recipe_E14.
# onto_e13_sensors.py keeps its canonical name (corrected version is in git).
# pack_runpod.ps1 throws on decode-time recipes; this is the E14 sibling stager.
# Usage: .\pack_runpod_e14.ps1
# Stages ONE upload zip for the E14 GPU run (steps 2-6). ASCII-only + UTF-8 BOM.
$ErrorActionPreference = "Stop"

$dpo   = "C:\Projects\onto-research\lab\dpo"
$stage = "C:\Users\Arist\Downloads\e14_stage"
$zip   = "C:\Users\Arist\Downloads\E14_RUNPOD.zip"

# PUBLIC-class scripts (in git): driver + 4 E13 scripts + harvest + gen lineage + recipe.
$scriptsPublic = @(
  "onto_e13_run.py", "onto_e13_logit_gate.py", "onto_e13_vfab.py",
  "onto_e13_sensors.py", "onto_e13_probe.py", "onto_e12_harvest.py",
  "onto_e5_gen.py", "recipe_E14.yaml"
)
# LOCAL-ONLY scripts (gitignored, on disk): entity-collision gate.
$scriptsLocal = @("gate_pairs.py")
# LOCAL-ONLY data: fresh prompts (public) + frozen eval (NEVER public).
$dataPublic = @("data\e13_provoke_fresh.jsonl")
$dataLocal  = @("data\heldout_v1.3.jsonl", "data\bait_v2_n32.jsonl")
# LOCAL-ONLY eval artifacts (gitignored): past emissions + held-out probe labels.
$evalLocal = @(
  "eval\_local\outputs_E10.json", "eval\_local\outputs_E11.json",
  "eval\_local\outputs_E12.json", "eval\_local\probe_labels_E12.json"
)
$adapter = "adapters\adapter_E12_dpo_68.zip"   # LOCAL-ONLY (weights never public)

$all = $scriptsPublic + $scriptsLocal + $dataPublic + $dataLocal + $evalLocal + @($adapter)

# --- presence verification FIRST (STOP on any missing input; no half-pack) ---
$missing = @()
foreach ($f in $all) { if (-not (Test-Path "$dpo\$f")) { $missing += $f } }
if ($missing.Count -gt 0) {
  Write-Output "STOP - missing inputs (pack NOT built):"
  $missing | ForEach-Object { Write-Output "  - $_" }
  throw "pack_runpod_e13: $($missing.Count) input(s) missing"
}

# --- stage ---
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "$stage\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$stage\eval_local" -Force | Out-Null
foreach ($f in ($scriptsPublic + $scriptsLocal)) { Copy-Item "$dpo\$f" $stage }
foreach ($f in ($dataPublic + $dataLocal))       { Copy-Item "$dpo\$f" "$stage\data\" }
foreach ($f in $evalLocal)                        { Copy-Item "$dpo\$f" "$stage\eval_local\" }
Copy-Item "$dpo\$adapter" $stage

# --- run_e14.sh (pod entrypoint; offline gates first, then driver) ---
$adapterName = [IO.Path]::GetFileNameWithoutExtension($adapter)   # adapter_E12_dpo_68
$sh = @"
#!/bin/bash
set -e
cd /content/working
echo '=== UNZIP ADAPTER ==='
unzip -o ADAPTERNAME.zip -d /content/working
echo '=== STAGE LOCAL-ONLY ARTIFACTS (outputs_E12 etc. -> ./_local) ==='
mkdir -p _local
cp eval_local/*.json _local/ 2>/dev/null || true
echo '=== OFFLINE SELFTESTS (must be green before GPU spend) ==='
python onto_e13_logit_gate.py --selftest
python onto_e13_vfab.py --selftest
python onto_e13_sensors.py --selftest
python onto_e13_run.py --selftest
echo '=== TOKENIZER SEAM SELFTEST (real Qwen2.5) ==='
python onto_e13_logit_gate.py --tok-selftest Qwen/Qwen2.5-Coder-7B
echo '=== ENTITY-COLLISION GATE (fresh prompts vs heldout+bait) ==='
python gate_pairs.py --heldout data/heldout_v1.3.jsonl --reflex data/e13_provoke_fresh.jsonl --out _local/gate_E14.log
echo 'REVIEW _local/gate_E14.log: pass --gate-passed below ONLY if collision-clean'
echo '=== E14 RUN (steps 2-6); outputs to ./_local ==='
python onto_e13_run.py \
  --adapter /content/working/ADAPTERNAME \
  --prompts data/e13_provoke_fresh.jsonl \
  --heldout data/heldout_v1.3.jsonl \
  --bait data/bait_v2_n32.jsonl \
  --outputs-e12 _local/outputs_E12.json \
  --out outputs_E14.json \
  --alphas 0.5,1.0,2.0,4.0 \
  --layers 12,16,24 \
  --gate-passed
echo '=== PACK LOCAL DELIVERABLES (NEVER git) ==='
cd /content/working && zip -rq E14_LOCAL_deliverables.zip _local
cp E14_LOCAL_deliverables.zip /workspace/
echo 'DONE: /workspace/E14_LOCAL_deliverables.zip - Download NOW (LOCAL-ONLY)'
"@
$sh = $sh.Replace("ADAPTERNAME", $adapterName).Replace("`r`n", "`n")
[IO.File]::WriteAllText("$stage\run_e14.sh", $sh)

Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force
Get-ChildItem $zip | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,1)}}
Write-Output "STAGED (all verified present):"
Write-Output ("  scripts(public): " + ($scriptsPublic -join ", "))
Write-Output ("  scripts(local):  " + ($scriptsLocal -join ", "))
Write-Output ("  data:            " + (($dataPublic + $dataLocal) -join ", "))
Write-Output ("  eval_local:      " + ($evalLocal -join ", "))
Write-Output ("  adapter:         " + $adapter)
Write-Output ""
Write-Output "ON POD (cell 1 - setup):"
Write-Output "!mkdir -p /content/working && cd /content/working && unzip -o /workspace/E14_RUNPOD.zip -d /content/working && pip install -q -U datasets transformers accelerate peft scikit-learn ``bitsandbytes>=0.46.1``"
Write-Output "ON POD (cell 2 - run):"
Write-Output "!cd /content/working && bash run_e14.sh"
