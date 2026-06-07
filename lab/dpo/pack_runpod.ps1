# pack_runpod.ps1 - permanent. Stage one upload zip for a RunPod run.
# Usage: .\pack_runpod.ps1 -E 11 [-Adapter adapter_E4_reflex_lora]
param(
  [Parameter(Mandatory=$true)][int]$E,
  [string]$Adapter = "adapter_E4_reflex_lora"
)
$dpo = "C:\Projects\onto-research\lab\dpo"
$stage = "C:\Users\Arist\Downloads\e$($E)_stage"
$zip = "C:\Users\Arist\Downloads\E$($E)_RUNPOD.zip"
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "$stage\data" -Force | Out-Null
Copy-Item "$dpo\onto_dpo_train.py" $stage
Copy-Item "$dpo\recipe_E$E.yaml" $stage
Copy-Item "$dpo\data\onto_e$($E)_dpo_pairs.jsonl" "$stage\data\"
Copy-Item "$dpo\adapters\$Adapter.zip" $stage
# read params from recipe (lr / epochs / beta) - simple grep, recipe keys are flat
$rec = Get-Content "$dpo\recipe_E$E.yaml" -Raw
$lr     = if ($rec -match 'learning_rate:\s*([0-9eE.\-]+)') { $Matches[1] } else { throw "lr not found in recipe" }
$epochs = if ($rec -match 'num_train_epochs:\s*(\d+)')      { $Matches[1] } else { throw "epochs not found in recipe" }
$beta   = if ($rec -match 'beta:\s*([0-9.]+)')              { $Matches[1] } else { throw "beta not found in recipe" }
$md5 = (Get-FileHash "$dpo\data\onto_e$($E)_dpo_pairs.jsonl" -Algorithm MD5).Hash.ToLower()
$sh = "#!/bin/bash`nset -e`ncd /content/working`necho '=== MD5 CHECK ==='`nmd5sum data/onto_e$($E)_dpo_pairs.jsonl`necho 'expect: $md5 (mismatch = STOP)'`nunzip -o $Adapter.zip -d /content/working`necho '=== TRAIN ==='`npython onto_dpo_train.py --data data/onto_e$($E)_dpo_pairs.jsonl --adapter $Adapter --epochs $epochs --lr $lr --beta $beta --output adapter_E$($E)_dpo_32`necho '=== PACK ==='`nzip -rq adapter_E$($E)_dpo_32.zip adapter_E$($E)_dpo_32`ncp adapter_E$($E)_dpo_32.zip /workspace/`necho 'DONE: /workspace/adapter_E$($E)_dpo_32.zip - Download NOW'"
[IO.File]::WriteAllText("$stage\run_e$E.sh", $sh)
Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force
Get-ChildItem $zip | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,1)}}
Write-Output "ON POD (notebook cell):"
Write-Output "!mkdir -p /content/working && cd /content/working && unzip -o /workspace/E$($E)_RUNPOD.zip -d /content/working && pip install -q -U datasets transformers accelerate peft `"bitsandbytes>=0.46.1`""
Write-Output "!cd /content/working && bash run_e$E.sh"
