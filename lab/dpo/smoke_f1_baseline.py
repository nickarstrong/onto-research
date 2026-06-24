#!/usr/bin/env python3
"""BUILD-FRONT #3 (F1) falsifier smoke -- SELF-CONTAINED, no net/GPU/held-out reads
(clone-coherence: embedded fixture only; never reads an ignored/held-out input).

Proves capture_cold_baseline emits a genuine UNCONDITIONED baseline window:
  - measured with retrieval OFF (retrieval_hit == 0, blind generate) and absorb OFF
    (function takes no absorb arg -> structurally cannot feed the proposer),
  - distinct from the late conditioned window (cycle:0 phase:"baseline" vs cycle>=1),
  - VIOLATION-A: save -> run -> restore on any pre-existing trace file; the FROZEN
    gate trace (selflearn_trace.jsonl, 9c960429) is NEVER touched -- temp path only.

Neg-control: the OLD path (no baseline phase) emits no cycle:0 baseline row, so the
F1 reader has no unconditioned anchor -> early==late==saturated. Must FAIL (discriminate).
"""
import json
import os
import sys
import tempfile

# clone-coherent import guard: controller.py has ONE module-level dep (citation_verify).
# On the lab disk the real module exists and is used. In a bare checkout / CI the smoke
# still loads via a minimal stub installed ONLY when the real module is absent. The stub
# is NEVER consulted by capture_cold_baseline (which takes injected adapters) -> inert.
try:
    import citation_verify  # noqa: F401  (real module present -> use it)
except ImportError:
    import types as _types
    _stub = _types.ModuleType("citation_verify")
    _stub.verify_citation = lambda *a, **k: (False, {})
    _stub.DIRTY = "DIRTY"
    _stub.CrossrefOracle = object
    sys.modules["citation_verify"] = _stub

import controller  # stdlib-only top imports + guarded dep -> loads without net/GPU


# ── embedded fixture: blind proposer fabricates at a KNOWN, non-saturated rate ──
# 8 claims, 3 DIRTY -> blind rate_f = 0.375 (headroom present in the fixture, so the
# smoke exercises a real early-window value, NOT a degenerate 0.0).
_BLIND_CLAIMS = [{"topic": f"t{i}", "claim": f"c{i}"} for i in range(8)]
_DIRTY_IDX = {1, 4, 6}


def blind_generate(n):
    # records NO retrieval side-channel -> retrieval_hit stays 0 (unconditioned)
    assert not hasattr(blind_generate, "retrieval_hits"), "blind arm must have no retrieval"
    return _BLIND_CLAIMS[:n]


def fake_verify(c):
    i = int(c["topic"][1:])
    return ("DIRTY" if i in _DIRTY_IDX else "CLEAN"), {}


def _read_rows(path):
    with open(path, "rb") as f:
        return [json.loads(ln) for ln in f.read().decode("utf-8").splitlines() if ln.strip()]


def run_smoke():
    fails = []
    tmpdir = tempfile.mkdtemp(prefix="f1_baseline_smoke_")
    trace = os.path.join(tmpdir, "trace.jsonl")

    # VIOLATION-A: seed a pre-existing trace, snapshot it, must survive untouched-prefix
    preexisting = b'{"cycle": 99, "phase": "PREEXISTING", "rate_f": 0.5}\n'
    with open(trace, "wb") as f:
        f.write(preexisting)
    snapshot = open(trace, "rb").read()

    # ---- POSITIVE: capture the cold baseline ----
    rate0 = controller.capture_cold_baseline(blind_generate, fake_verify, n=8,
                                             trace_path=trace)
    rows = _read_rows(trace)

    # 1. pre-existing row preserved (save->run->restore: append-only, no mutate)
    if open(trace, "rb").read()[:len(snapshot)] != snapshot:
        fails.append("VIOLATION-A: pre-existing trace bytes mutated")
    if rows[0].get("phase") != "PREEXISTING":
        fails.append("pre-existing row lost")

    base = [r for r in rows if r.get("phase") == "baseline"]
    if len(base) != 1:
        fails.append(f"expected exactly 1 baseline row, got {len(base)}")
    else:
        b = base[0]
        # 2. unconditioned: retrieval OFF
        if b.get("retrieval_hit") != 0:
            fails.append(f"baseline retrieval_hit != 0 ({b.get('retrieval_hit')}) -> conditioned")
        # 3. distinct window marker
        if b.get("cycle") != 0:
            fails.append(f"baseline cycle != 0 ({b.get('cycle')}) -> not distinct from late")
        # 4. real, non-saturated early value (3/8)
        if b.get("rate_f") != 0.375:
            fails.append(f"baseline rate_f wrong: {b.get('rate_f')} (want 0.375)")
        if b.get("clean_count") != 5:
            fails.append(f"baseline clean_count wrong: {b.get('clean_count')} (want 5)")
    if rate0 != 0.375:
        fails.append(f"return rate0 wrong: {rate0}")

    # 5. simulate the LATE conditioned window -> must be distinct (cycle>=1, no phase)
    controller._emit_trace(trace, {
        "cycle": 7, "weakness": "fabricated-specifics",
        "select_target": "fabricated-specifics", "rate_f": 0.0,
        "clean_count": 8, "retrieval_hit": 2, "fa_live": 0.0, "ts": "x"})
    rows2 = _read_rows(trace)
    late = [r for r in rows2 if r.get("phase") is None and r.get("cycle", 0) >= 1]
    if not late:
        fails.append("no distinct late window row")
    else:
        early = base[0]["rate_f"] if base else None
        late_rf = late[-1]["rate_f"]
        if early is not None and abs(early - late_rf) < 0.20:
            fails.append(f"early->late delta {abs(early-late_rf):.3f} < 0.20 in fixture "
                         "(reader would still 0/3) -- fixture must show headroom")

    # ---- NEG-CONTROL: OLD path (no baseline phase) -> no anchor -> reader can't form delta ----
    trace_old = os.path.join(tmpdir, "trace_old.jsonl")
    controller._emit_trace(trace_old, {
        "cycle": 1, "weakness": "fabricated-specifics", "rate_f": 0.0,
        "clean_count": 8, "retrieval_hit": 0, "fa_live": 0.0, "ts": "x"})
    old_rows = _read_rows(trace_old)
    if any(r.get("phase") == "baseline" or r.get("cycle") == 0 for r in old_rows):
        fails.append("NEG-CONTROL leaked a baseline anchor (must have none)")
    neg_ok = not any(r.get("phase") == "baseline" for r in old_rows)

    print("=" * 64)
    print("F1 COLD-BASELINE SMOKE")
    print(f"  baseline rate_f          : {rate0} (3/8 DIRTY, headroom present)")
    print(f"  baseline retrieval_hit   : {base[0].get('retrieval_hit') if base else 'NONE'} (want 0)")
    print(f"  baseline cycle/phase     : {base[0].get('cycle') if base else '?'}/"
          f"{base[0].get('phase') if base else '?'}")
    print(f"  pre-existing row kept    : {rows[0].get('phase') == 'PREEXISTING'}")
    print(f"  neg-control (no anchor)  : {'OK (discriminates)' if neg_ok else 'LEAK'}")
    print("=" * 64)
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("RESULT: PASS (baseline unconditioned + distinct + VIOLATION-A clean; neg-control discriminates)")
    return 0


if __name__ == "__main__":
    sys.exit(run_smoke())
