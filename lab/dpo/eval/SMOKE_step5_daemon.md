# SMOKE — Step 5 daemon.py (offline dry-proof, no GPU/net)

Wraps controller.run (build 1184d19 / v227 live). Cycle NOT redesigned.

Pre-registered falsifiers — all PASS:

| F  | Test                                              | Result |
|----|---------------------------------------------------|--------|
| F1 | lifecycle: tick loop, graceful stop               | PASS — 2 ticks cold, exit at max_ticks; STOP-file exit=0 |
| F2 | cross-reboot resume                               | PASS — restart resumed cycle 2→3, cycles_used 2→3, last_worked persists, no reset |
| F3 | contact channel: VALID_TRIGGER file-drop          | PASS — STUCK→1 PLATEAU drop; DONE→0 drops |
| F4 | drift guard: leak halts, clean continues          | PASS — leak fa_live=0.500>0.10 → HALT exit=2 + GATE_FAIL_LEARN drop; clean trail fa=0 runs all ticks |
| —  | routing guard: live --n>10 refused                | PASS — FATAL exit |

Contracts confirmed against disk:
- run(self_model,gen,ver,abs,n,live,max_cycles)->int  {0 done, 2 fa_live HALT}
- per-cycle terminator appends contact_log.jsonl {timestamp,reason,cycle,detail}
- goal_stack.json re-read every run() call → resume intrinsic
- live absorb trail = eval/o0/o0_verdicts.jsonl

R2 scope: G_drift = STRUCTURAL leak watchdog (absorbed-knowledge must never carry a
reject verdict; = the leak=0 metric v227 verified). NOT a Crown re-run. Semantic
fa_live re-verification = Step 6 oracle, out of scope.

NOT proven offline (needs LOCAL Ollama+net+GPU): the N>=5 unattended gate run.
