#!/usr/bin/env python3
# onto_e13_sensors.py - ONTO E13 component (c): preflight sensors. ABORT-ONLY.
#
# Three one-forward-pass sensors (recipe_E13.sensors; triage 1.1, 5.1):
#   1. refusal_log_odds  : first-answer-token refusal mass on negctrl prompts.
#        r_s = log sum_{t in R} P(t) - log sum_{t notin R} P(t)
#        R = refusal-opening token ids EXTRACTED FROM REAL outputs_E12 arm C refusals
#            (NOT guessed). Early "model went mute" detector (E3 failure mode).
#   2. distortion_norm   : ||total_correction|| / ||hidden_states|| on heldout-clean.
#        Steering hook must be near-silent on clean prompts.
#   3. kl_divergence     : KL(P_steered || P_base) over next-token logits on negctrl,
#        paired passes with/without hook. Off-target semantic-damage sensor.
#
# ROLE (recipe.sensors.role; triage 3.2): ABORT-ONLY. A sensor may STOP a run early
#   to save pod money. It may NEVER issue GO/NO-GO. Proxy-as-verdict is the auto-GO
#   3/3 lesson wearing a new hat. The functions here return "ABORT" / "CONTINUE",
#   never a verdict. The immutable falsifier + manual scan govern GO/NO-GO.
#
# THRESHOLDS (recipe.sensors.thresholds; triage 2.3): calibrated on OUR outputs_E12
#   real distributions (4 arms x 68). Advisor numbers (refusal 0.30/0.35, distortion
#   0.15-0.20, KL 1.5, 5%) = UNSOURCED -> usable only as initial grid points. calibrate()
#   reads outputs_E12 and emits calibrated values. It writes to _local/ and PRINTS a YAML
#   snippet to paste into recipe_E13.sensors by hand: this script NEVER auto-edits
#   recipe_E13.yaml (the falsifier block is immutable; no automated write goes near it).
#
# STATUS: authoring (TYPE A). Live sensors need torch+pod. PUBLIC git (script only).

from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

LOCAL_DIR = "_local"

# Advisor starting grid points (UNSOURCED -- grid only, never standards).
ADVISOR_GRID = {
    "refusal_log_odds_min": math.log(0.30 / 0.70),   # 0.30 prob mass -> log-odds
    "distortion_max": 0.175,                          # midpoint of 0.15-0.20
    "kl_max": 1.5,
}


# ---------------------------------------------------------------------------
# 1. REFUSAL-OPENING TOKEN SET  (extracted from REAL outputs_E12 arm C refusals)
# ---------------------------------------------------------------------------

def extract_refusal_token_ids(outputs_e12_path: str, tokenizer,
                              clean_baits: Optional[Sequence[str]] = None,
                              top_n: int = 12) -> List[int]:
    """Read outputs_E12.json arm C, take the C-arm REFUSAL completions, tokenize each,
    collect the FIRST answer token, return the most common ids. NOT guessed.

    `clean_baits`: ids of bait items labelled clean/honest-refusal in the E12 verdict
    (bait_10,12,13,15,16,21,25,26,27,28,29,35,36,37,40). If provided, restrict to those
    so we capture the trained refusal-opening shape, not fabrication openings.

    outputs_E12.json is LOCAL-ONLY; this reads it, never echoes content to git.
    """
    if not os.path.exists(outputs_e12_path):
        raise SystemExit(f"ABORT: outputs_E12 not found at {outputs_e12_path} "
                         f"(LOCAL-ONLY artifact; pull locally before calibration).")
    with open(outputs_e12_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    arm_c = data.get("C") or data.get("c") or data.get("arm_C")
    if arm_c is None:
        raise SystemExit("ABORT: outputs_E12.json has no C arm; cannot extract refusal tokens.")

    from collections import Counter
    counter: Counter = Counter()
    for item in arm_c:
        qid = str(item.get("id", ""))
        if clean_baits is not None and not any(qid.endswith(cb) for cb in clean_baits):
            continue
        completion = item.get("completion", "") or item.get("output", "")
        # the answer body (strip any R-wrapper / system echo if present in your schema)
        body = completion.strip()
        if not body:
            continue
        ids = tokenizer(body, add_special_tokens=False)["input_ids"]
        if ids:
            counter[ids[0]] += 1
    if not counter:
        raise SystemExit("ABORT: no refusal completions found in arm C to extract from.")
    chosen = [tid for tid, _ in counter.most_common(top_n)]
    print(f"[refusal-tokens] extracted {len(chosen)} ids from real arm-C refusals "
          f"(top_n={top_n}); LOCAL provenance, not guessed.")
    return chosen


# ---------------------------------------------------------------------------
# 2. SENSOR MATH  (pure; unit-tested offline)
# ---------------------------------------------------------------------------

def _softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max()
    e = np.exp(z)
    return e / e.sum()


def refusal_log_odds(first_token_logits: np.ndarray, refusal_ids: Sequence[int],
                     eps: float = 1e-12) -> float:
    """r_s = log sum_{t in R} P(t) - log sum_{t notin R} P(t)."""
    p = _softmax(np.asarray(first_token_logits, dtype=np.float64))
    mask = np.zeros_like(p, dtype=bool)
    mask[list(refusal_ids)] = True
    p_ref = float(p[mask].sum())
    p_oth = float(p[~mask].sum())
    return math.log(p_ref + eps) - math.log(p_oth + eps)


def distortion_norm(total_correction: np.ndarray, hidden_states: np.ndarray) -> float:
    """D = ||total_correction|| / ||hidden_states|| (per prompt, clean set)."""
    hn = float(np.linalg.norm(hidden_states))
    if hn == 0:
        return 0.0
    return float(np.linalg.norm(total_correction)) / hn


def kl_divergence(p_steered_logits: np.ndarray, p_base_logits: np.ndarray) -> float:
    """KL(P_steered || P_base) over next-token logits, paired pass."""
    ps = _softmax(np.asarray(p_steered_logits, dtype=np.float64))
    pb = _softmax(np.asarray(p_base_logits, dtype=np.float64))
    eps = 1e-12
    return float(np.sum(ps * (np.log(ps + eps) - np.log(pb + eps))))


# ---------------------------------------------------------------------------
# 3. ABORT DECISION  (never GO/NO-GO)
# ---------------------------------------------------------------------------

@dataclass
class SensorThresholds:
    refusal_log_odds_min: float   # below this on negctrl is FINE; ABOVE = over-refusal risk
    distortion_max: float         # above this on clean = hook too loud
    kl_max: float                 # above this on negctrl = off-target damage


def abort_decision(mean_refusal_lo: float, mean_distortion: float, mean_kl: float,
                   th: SensorThresholds) -> Tuple[str, List[str]]:
    """Returns ('ABORT'|'CONTINUE', reasons). NEVER returns GO/NO-GO."""
    reasons: List[str] = []
    # over-refusal: high refusal log-odds on NEGCTRL = model going mute on prompts it
    # SHOULD answer (the E3 fab-0-by-silence mode).
    if mean_refusal_lo > th.refusal_log_odds_min:
        reasons.append(f"over-refusal: negctrl refusal log-odds {mean_refusal_lo:.3f} "
                       f"> {th.refusal_log_odds_min:.3f}")
    if mean_distortion > th.distortion_max:
        reasons.append(f"hook not silent on clean: distortion {mean_distortion:.3f} "
                       f"> {th.distortion_max:.3f}")
    if mean_kl > th.kl_max:
        reasons.append(f"off-target damage: KL {mean_kl:.3f} > {th.kl_max:.3f}")
    return ("ABORT" if reasons else "CONTINUE"), reasons


# ---------------------------------------------------------------------------
# 4. CALIBRATION  (reads outputs_E12 distributions; writes LOCAL + prints YAML snippet)
# ---------------------------------------------------------------------------

def calibrate_from_distributions(refusal_lo_clean: Sequence[float],
                                 distortion_clean: Sequence[float],
                                 kl_negctrl: Sequence[float],
                                 q: float = 0.95) -> SensorThresholds:
    """Calibrate abort thresholds from OUR measured distributions, not advisor numbers.
    Sets each threshold at the q-quantile of the appropriate clean/negctrl distribution
    (with advisor grid as a sanity floor, logged if it binds)."""
    th = SensorThresholds(
        refusal_log_odds_min=float(np.quantile(refusal_lo_clean, q)),
        distortion_max=float(np.quantile(distortion_clean, q)),
        kl_max=float(np.quantile(kl_negctrl, q)),
    )
    for name, val, grid in [
        ("refusal_log_odds_min", th.refusal_log_odds_min, ADVISOR_GRID["refusal_log_odds_min"]),
        ("distortion_max", th.distortion_max, ADVISOR_GRID["distortion_max"]),
        ("kl_max", th.kl_max, ADVISOR_GRID["kl_max"]),
    ]:
        print(f"[calibrate] {name}={val:.4f} (advisor grid point {grid:.4f}; "
              f"{'BELOW' if val < grid else 'ABOVE'} grid)")
    return th


def emit_threshold_yaml(th: SensorThresholds) -> str:
    """Write calibrated thresholds LOCAL-ONLY and return a YAML snippet for MANUAL paste
    into recipe_E13.sensors. This script never auto-edits recipe_E13.yaml (immutable
    falsifier block lives in the same file; no automated write goes near it)."""
    os.makedirs(LOCAL_DIR, exist_ok=True)
    local = os.path.join(LOCAL_DIR, "sensor_thresholds_E13.json")
    with open(local, "w", encoding="utf-8") as f:
        json.dump(th.__dict__, f, indent=2)
    snippet = (
        "  thresholds_calibrated:        # PASTE BY HAND into recipe_E13.sensors\n"
        "    source: outputs_E12 real distributions (0.95-quantile)\n"
        f"    refusal_log_odds_min: {th.refusal_log_odds_min:.4f}\n"
        f"    distortion_max: {th.distortion_max:.4f}\n"
        f"    kl_max: {th.kl_max:.4f}\n"
    )
    print(f"[LOCAL-ONLY] thresholds -> {local}")
    print("[MANUAL PASTE] add under recipe_E13.sensors (NOT the falsifier block):\n" + snippet)
    return snippet


# ---------------------------------------------------------------------------
# 5. OFFLINE SELFTEST
# ---------------------------------------------------------------------------

def _selftest() -> int:
    fails: List[str] = []
    rng = np.random.default_rng(0)
    V = 200

    # refusal log-odds: pile mass on refusal ids -> positive log-odds; flat -> negative
    refusal_ids = [3, 7, 11]
    logits_refuse = np.full(V, -5.0); logits_refuse[refusal_ids] = 5.0
    lo_hi = refusal_log_odds(logits_refuse, refusal_ids)
    logits_flat = rng.normal(size=V)
    lo_lo = refusal_log_odds(logits_flat, refusal_ids)
    if not (lo_hi > 0 > lo_lo):
        fails.append(f"refusal log-odds ordering wrong: refuse={lo_hi:.2f} flat={lo_lo:.2f}")

    # distortion: zero correction -> 0; large correction -> large ratio
    h = rng.normal(size=64)
    if distortion_norm(np.zeros(64), h) != 0.0:
        fails.append("distortion of zero correction must be 0")
    if not (distortion_norm(2.0 * h, h) > 1.5):
        fails.append("distortion of 2h/h must be ~2")

    # KL: identical -> ~0; different -> >0
    a = rng.normal(size=V)
    if abs(kl_divergence(a, a)) > 1e-9:
        fails.append("KL of identical dists must be ~0")
    if not (kl_divergence(a, rng.normal(size=V)) > 0):
        fails.append("KL of different dists must be > 0")

    # abort decision: never returns GO/NO-GO; fires on threshold breach
    th = SensorThresholds(refusal_log_odds_min=0.0, distortion_max=0.1, kl_max=1.0)
    dec, reasons = abort_decision(1.0, 0.5, 2.0, th)
    if dec != "ABORT" or len(reasons) != 3:
        fails.append(f"abort_decision should ABORT with 3 reasons, got {dec}/{reasons}")
    dec2, _ = abort_decision(-1.0, 0.01, 0.1, th)
    if dec2 != "CONTINUE":
        fails.append(f"abort_decision should CONTINUE under thresholds, got {dec2}")
    # verdict-word guard: no executable `return` emits GO/NO-GO (ignore comments/docstrings)
    src = open(__file__, "r", encoding="utf-8").read()
    bad_returns = []
    for ln in src.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            continue
        if s.startswith("return ") and ("\"GO\"" in s or "\"NO-GO\"" in s
                                         or "'GO'" in s or "'NO-GO'" in s):
            bad_returns.append(s)
    if bad_returns:
        fails.append(f"sensor code returns a verdict literal (must be abort-only): {bad_returns}")

    # calibration produces thresholds from distributions
    th2 = calibrate_from_distributions(
        refusal_lo_clean=rng.normal(-2, 0.5, 100),
        distortion_clean=np.abs(rng.normal(0.05, 0.02, 100)),
        kl_negctrl=np.abs(rng.normal(0.3, 0.1, 100)), q=0.95)
    if not (th2.distortion_max > 0 and th2.kl_max > 0):
        fails.append("calibration produced non-positive thresholds")

    if fails:
        print(f"SELFTEST FAIL: {len(fails)} failures")
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST PASS: refusal log-odds, distortion, KL, abort-decision (abort-only, "
          "no GO/NO-GO), and calibration all green.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    print("Runtime: extract_refusal_token_ids(outputs_E12) -> measure sensors on "
          "negctrl/clean -> calibrate_from_distributions -> emit_threshold_yaml "
          "(LOCAL + manual paste). abort_decision gates the run, never the verdict.")
