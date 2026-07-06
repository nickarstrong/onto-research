# DIRECTION_VECTOR  (one line per SESSION: vNNN | axis | verdict | conclusion. No ops-junk.)

v425 . ORGAN-A sft-targeted-fix . G3-FAIL 5/7 (bar=6), BUT idx3 FIXED (8 paraphrases+contrast broke Qwen prior, ROME pivot cancelled). idx0=string-match inadequacy not SFT failure, idx1=QLoRA stochastic regression. Method alive: SFT+paraphrase-aug internalizes facts incl. conflict-override. ORGAN-A axis CLOSES -- method proven, remaining gap = meter granularity not method limit.
v427 · LoRA weight anatomy · PASS · L18-27 o_proj/q_proj concentrated (3-4x > k/v), monotonic layer gradient; next = logit lens base vs adapted at L18-27.
v428 · logit lens base vs adapted · PASS · transition L24-L26-L27 = first-token routing in o_proj, not fact storage; SFT adapter anatomy CLOSED; next = causal tracing on base model for ROME target.

v429 · causal tracing base MLP · G3 FAIL · L7-L8 peak (6/10 facts) but L6-L8 = 30.8% < 50% threshold; too distributed for single-site ROME; MEMIT target = L5-L10 MLP; causal tracing axis CLOSED.

v430 · MEMIT smoke Qwen2.5-Coder-7B · G3 PASS · P(London)=0.997, control drop 6.5%; hook-based 4-bit editing viable on correct substrate; MEMIT method axis CLOSED.

v431 · MEMIT abiogenesis 7 facts · G3 FAIL 3/7 (0 new-fact generalization) · edit subject-token-bound: held-out passes only when sharing subject token; SFT+MEMIT both surface-form-bound; MEMIT axis CLOSED

v431 · MEMIT abiogenesis 7 facts · G3 FAIL 3/7 (0 new-fact generalization) · edit subject-token-bound: held-out passes only when sharing subject token; SFT+MEMIT both surface-form-bound; MEMIT axis CLOSED

v432 · linear-probe concept-level · PASS · 6/7@L7-L26 7/7@L27; substrate encodes abiogenesis concepts abstractly; SFT/MEMIT failure = method not substrate; repr-eng viable
v433 · concept-direction-steering · FAIL 0/7 · concepts encoded (v432) but not steerable via linear RepE injection; probe-intervention gap confirmed; writing-to-weights axis exhausted (SFT/MEMIT/RepE); pivot to runtime scaffolding
v434 · concept-triggered-retrieval · PASS · detect 5/7 held-out; organism reads substrate L13 cosine; boost 5/13 (injection crude); F3/F7 persistent weak; pipeline proven: detect->retrieve->augment