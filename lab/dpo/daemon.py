#!/usr/bin/env python3
"""
daemon.py -- organism-0 unattended daemon (ROADMAP Step 5, "24/7 + memory").

Wraps controller.run WITHOUT redesigning the cycle (pack: "Wrap Controller.run,
not rewrite"). Adds the four Step-5 organs and nothing else:

  1. LIFECYCLE   tick loop, cadence sleep, graceful stop (SIGINT/SIGTERM + STOP-file)
  2. RESUME      cross-reboot: controller.run rebuilds GoalStack() each call, so it
                 re-reads goal_stack.json every tick -> resume is intrinsic. The
                 daemon only READS + LOGS + ASSERTS the resumed state on boot.
  3. CONTACT     real channel = file-drop. Tail contact_log.jsonl; on a new event
                 whose reason maps to a VALID_TRIGGER {PLATEAU,GEN_FAIL,
                 GATE_FAIL_LEARN}, drop one file into contact_drop/.
  4. DRIFT GUARD G_drift = rolling structural fa_live over eval/o0/o0_verdicts.jsonl:
                 absorbed-knowledge must never carry a reject verdict. leak/absorbed
                 > drift_max -> HALT. run()==2 (controller's own breach) also halts.

WRAP CONTRACT (read from controller.py on disk, build 1184d19 / v227 live):
  controller.run(self_model_path, generate, verify, absorb, n, live, max_cycles)->int
    0 = cycles complete, 2 = fa_live breach HALT
  controller.live_adapters()/dry_adapters() -> (generate, verify, absorb)
  per-cycle terminator -> append controller.CONTACT_LOG {timestamp,reason,cycle,detail}
    reason in {DONE, STUCK, RESOURCE, FA_LIVE_BREACH}
  persistence: controller.GOAL_STACK (cycle/weaknesses/cooldown survive reboot),
               controller.CONTACT_LOG, eval/o0/o0_verdicts.jsonl (live absorb trail)

R2 (honest scope): G_drift is a STRUCTURAL leak watchdog (catches absorb-path
corruption / a future cycle-bug that flips _absorbed_knowledge on a reject). It does
NOT re-run Crown. Crown-correctness stays the controller's by-construction guarantee
plus the live VERIFY channel. A SEMANTIC fa_live watchdog needs an independent
verifier pass = Step 6 oracle, out of scope here.

ROUTING: cycles are LOCAL (n<=10/cycle, Ollama + Wikidata, network-bound). The daemon
MUST run from lab/dpo so controller's relative paths resolve. Pre-run check before any
--live unattended start: nvidia-smi + ollama /api/tags.

Usage:
  # offline proof of the machinery (no GPU/net):
  python daemon.py --dry-run --max-ticks 3 --cadence-sec 0
  # the gate run (LOCAL, Ollama up, net on):
  python daemon.py --live --max-ticks 5 --n 8 --cadence-sec 60
  # forever (real 24/7); stop with: New-Item STOP  (or Ctrl-C):
  python daemon.py --live --max-ticks 0 --n 8 --cadence-sec 300
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import controller  # the on-disk cycle we wrap (do NOT redesign)

DEFAULT_TRAIL = "eval/o0/o0_verdicts.jsonl"
DROP_DIR = "contact_drop"
STOP_FILE = "STOP"

# reason (controller) -> VALID_TRIGGER (pack: {PLATEAU,GEN_FAIL,GATE_FAIL_LEARN})
TRIGGER_MAP = {
    "STUCK": "PLATEAU",
    "RESOURCE": "GEN_FAIL",
    "FA_LIVE_BREACH": "GATE_FAIL_LEARN",
    # DONE -> no drop (success is logged, not a contact trigger)
}

_STOP = {"flag": False}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _install_signals():
    def handler(signum, frame):
        _STOP["flag"] = True
        print(f"\n[DAEMON] signal {signum} -> graceful stop after current tick")
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, handler)
        except (ValueError, OSError):
            pass  # not in main thread / unsupported platform


def _read_jsonl(path):
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for ln in p.read_text(encoding="utf-8-sig").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            pass  # tolerate a partially-written tail line; next read picks it up
    return out


# ── 2. RESUME ───────────────────────────────────────────────────────────
def boot_resume_log():
    """Read + log persistent memory at boot. Proves cross-reboot continuity."""
    gs = Path(controller.GOAL_STACK)
    if not gs.exists():
        print("[RESUME] no goal_stack.json -> COLD START (cycle 0)")
        return 0
    st = json.loads(gs.read_text(encoding="utf-8-sig"))
    cyc = st.get("cycle", 0)
    print(f"[RESUME] goal_stack.json found -> RESUME from cycle {cyc}")
    for name, r in st.get("weaknesses", {}).items():
        print(f"         '{name}': cycles_used={r.get('cycles_used')} "
              f"last_worked_cycle={r.get('last_worked_cycle')} "
              f"history={len(r.get('history', []))}")
    return cyc


# ── 4. DRIFT GUARD ──────────────────────────────────────────────────────
def g_drift(trail_path, window, watermark_ts):
    """Rolling structural fa_live over the verdict trail.

    A record is ABSORBED-KNOWLEDGE iff verdict=='ABSORB' / _absorbed_knowledge truthy.
    A LEAK iff a record carries _absorbed_knowledge truthy AND verdict!='ABSORB'
    (i.e. a reject/catch record wrongly flagged into knowledge).
    fa_live = leaks / max(1, absorbed). Returns (fa_live, absorbed, leaks).
    Only records at/after watermark_ts (this run) are counted.
    """
    recs = _read_jsonl(trail_path)
    if watermark_ts:
        recs = [r for r in recs if r.get("ts", "") >= watermark_ts]
    recs = recs[-window:] if window > 0 else recs
    absorbed = leaks = 0
    for r in recs:
        flagged = bool(r.get("_absorbed_knowledge"))
        is_absorb = (r.get("verdict") == "ABSORB")
        if flagged or is_absorb:
            absorbed += 1
            if flagged and not is_absorb:
                leaks += 1
    fa = (leaks / absorbed) if absorbed else 0.0
    return fa, absorbed, leaks


# ── 3. CONTACT CHANNEL ──────────────────────────────────────────────────
def drain_contacts(drop_dir, contact_seen):
    """Tail contact_log.jsonl; drop a file per NEW event on a VALID_TRIGGER.
    Returns (n_new_total, n_dropped, last_reason)."""
    events = _read_jsonl(controller.CONTACT_LOG)
    new = events[contact_seen["n"]:]
    contact_seen["n"] = len(events)
    dropped = 0
    last_reason = None
    Path(drop_dir).mkdir(parents=True, exist_ok=True)
    for ev in new:
        last_reason = ev.get("reason")
        trig = TRIGGER_MAP.get(ev.get("reason"))
        if not trig:
            continue
        fname = f"{drop_dir}/contact_{ev.get('cycle')}_{trig}.json"
        Path(fname).write_text(json.dumps({
            "trigger": trig,
            "reason": ev.get("reason"),
            "cycle": ev.get("cycle"),
            "detail": ev.get("detail"),
            "ts": ev.get("timestamp"),
            "dropped_at": _now(),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        dropped += 1
        print(f"  [DROP] {trig} -> {fname}")
    return len(new), dropped, last_reason


# ── 1. LIFECYCLE ────────────────────────────────────────────────────────
def daemon_loop(args, generate, verify, absorb):
    run_start = _now()
    contact_seen = {"n": len(_read_jsonl(controller.CONTACT_LOG))}  # ignore pre-existing
    drops_total = 0
    tick = 0

    print("=" * 70)
    print("ORGANISM-0 DAEMON -- Step 5 (24/7 + memory; wraps controller.run)")
    print(f"  mode     : {'LIVE' if args.live else 'DRY-RUN'}")
    print(f"  cadence  : {args.cadence_sec}s   max_ticks: "
          f"{args.max_ticks or 'forever'}   window: {args.window}   "
          f"drift_max: {args.drift_max}")
    print(f"  trail    : {args.verdict_trail}")
    print("=" * 70)
    boot_resume_log()

    while True:
        if _STOP["flag"] or Path(STOP_FILE).exists():
            print(f"[DAEMON] stop requested (flag/{STOP_FILE}) -> graceful exit")
            return 0
        if args.max_ticks and tick >= args.max_ticks:
            print(f"[DAEMON] reached max_ticks={args.max_ticks} -> exit")
            return 0

        tick += 1
        print(f"\n----- TICK {tick} @ {_now()} -----")

        # wrap controller.run for exactly ONE cycle (it persists goal_stack itself)
        rc = controller.run(args.self_model, generate, verify, absorb,
                            n=args.n, live=args.live, max_cycles=1,
                            trace_path=args.selflearn_trace)

        # 3. real-channel contact
        n_new, dropped, last_reason = drain_contacts(args.contact_drop, contact_seen)
        drops_total += dropped

        # 4. drift guard (live trail; dry has no trail -> fa=0 structurally)
        fa, absorbed, leaks = g_drift(args.verdict_trail, args.window, run_start)
        print(f"[GDRIFT] fa_live={fa:.3f} (leaks={leaks}/absorbed={absorbed}) "
              f"window<={args.window}  contacts_dropped_total={drops_total}")

        if rc == 2 or fa > args.drift_max:
            why = "controller fa_live HALT" if rc == 2 else \
                  f"G_drift {fa:.3f} > {args.drift_max}"
            print(f"[HALT] {why} -> STOP (operator must clear).")
            Path(args.contact_drop).mkdir(parents=True, exist_ok=True)
            Path(f"{args.contact_drop}/HALT_GATE_FAIL_LEARN_tick{tick}.json").write_text(
                json.dumps({"trigger": "GATE_FAIL_LEARN", "why": why,
                            "fa_live": round(fa, 4), "tick": tick, "ts": _now()},
                           ensure_ascii=False, indent=2), encoding="utf-8")
            return 2

        # 1. cadence sleep (interruptible)
        slept = 0.0
        while slept < args.cadence_sec:
            if _STOP["flag"] or Path(STOP_FILE).exists():
                break
            time.sleep(min(0.25, args.cadence_sec - slept))
            slept += 0.25


def main():
    ap = argparse.ArgumentParser(description="organism-0 daemon (Step 5)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="offline mocks via controller.dry_adapters (no GPU/net)")
    mode.add_argument("--live", action="store_true",
                      help="real pipeline via controller.live_adapters")
    ap.add_argument("--self-model", default="self_model.json")
    ap.add_argument("--n", type=int, default=8, help="claims per cycle (<=10 LOCAL)")
    ap.add_argument("--cadence-sec", type=float, default=60.0,
                    help="sleep between ticks (0 = back-to-back)")
    ap.add_argument("--max-ticks", type=int, default=0,
                    help="0 = run forever; >0 = bounded (gate run uses 5)")
    ap.add_argument("--window", type=int, default=20,
                    help="rolling window of trail records for G_drift")
    ap.add_argument("--drift-max", type=float, default=0.10,
                    help="G_drift fa_live ceiling (pack gate)")
    ap.add_argument("--verdict-trail", default=DEFAULT_TRAIL)
    ap.add_argument("--contact-drop", default=DROP_DIR)
    ap.add_argument("--selflearn-trace", default=None,
                    help="GATE_selflearn: per-visit witness JSONL (off = no trace)")
    ap.add_argument("--conditioned", action="store_true",
                    help="GATE_selflearn: wire CONDITIONED proposer (retrieval+frame)")
    ap.add_argument("--curated-path", default="o0_verdicts_curated.jsonl")
    ap.add_argument("--gold-frame", default="gold_frame.txt")
    args = ap.parse_args()

    if args.live and args.n > 10:
        sys.exit(f"FATAL: --n {args.n} > 10 violates LOCAL routing (pack §3).")

    _install_signals()
    gen, ver, abs_ = (controller.live_adapters(conditioned=args.conditioned,
                                                curated_path=args.curated_path,
                                                gold_frame_path=args.gold_frame)
                      if args.live else controller.dry_adapters())
    raise SystemExit(daemon_loop(args, gen, ver, abs_))


if __name__ == "__main__":
    main()
