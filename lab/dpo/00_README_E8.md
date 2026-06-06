# E8 genpack - anchor rebalance (TYPE A: gen+train, NO eval)

## What this is
26 P7_anchor SFT pairs that reward range-first + named-source + uncertainty on
ANSWERABLE core questions, to lift composite(C) >= 5.5 after E7 guard-overpress
(5.95 -> 4.87). Fresh topics, gate PASS (0 collisions, max overlap 2 of >3).
No provoke_id / no DOI emission. P6 guard pairs untouched.

## Contents
- sft_p7_pairs_E8.jsonl    26 anchors  (md5 5c37133c92708254ef1d7ca7088f6dcf)
- build_e8_pairs.py        regenerates the jsonl (provenance)
- gate_e8.py + gate_E8.log leak gate vs heldout+bait -> PASS
- merge_and_pack_e8.py     schema-adaptive merge, asserts 418
- recipe_E8.yaml           E2 recipe verbatim, falsifier immutable
- MERGE_AND_PACK_E8.ps1    one command (this README's step below)

## Run (one step)
1. Save onto_e8_genpack.zip to Downloads.
2. PowerShell:  .\MERGE_AND_PACK_E8.ps1   (after Expand-Archive of genpack, or run it
   from the extracted folder - the script self-expands the genpack and merges).
   It produces C:\Users\Arist\Downloads\onto_e8_runpod.zip (= 418 data + frozen
   trainer/gen + recipe). Aborts loudly if any local source is missing.
3. Upload onto_e8_runpod.zip to RunPod -> extract -> run recipe_E8 run_command.
   Adapter download IMMEDIATELY after train; outputs after EACH arm (E4 lesson).

## Local sources the PS expects (must exist at Tommy)
- C:\Projects\onto-research\lab\dpo\data\sft_reflex_392.jsonl   (base, LOCAL)
- ...\data\heldout_v1.3.jsonl  ...\data\bait_v2_n32.jsonl       (eval, LOCAL)
- ...\onto_exp1_e2_sft.py   ...\onto_e7_gen.py                  (frozen trainer/gen)

## After scoring (NEXT session, v20 pack, TYPE B)
Falsifier: GO <=> bait_fab(C)=0/32 AND composite(C)>=5.5.
If composite lifts but seam {33,39} survives -> E9 DPO on DOI-seam.

## Git provenance (public onto-research, after this session)
add: build_e8_pairs.py + sft_p7_pairs_E8.jsonl + gate_e8.py + gate_E8.log + recipe_E8.yaml
exclude: weights / heldout / bait / outputs.
