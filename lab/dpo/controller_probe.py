#!/usr/bin/env python3
# controller_probe.py - Step 1 PROBE for CONTROLLER BUILD (TYPE C)
# Tests CONCEPT_controller_v1 sec6 priority function against sec11 secondary
# falsifier + sec12 modulation cases. Deterministic if/else, no statistical bar.
# Pure stdlib, CPU, no model, no Crown. Runnable anywhere.

from datetime import date

NOW = date(2026, 6, 22)  # fixed reference for reproducibility


def days_since(last_worked):
    return (NOW - date.fromisoformat(last_worked)).days


def priority_score(card):
    # verbatim from CONCEPT_controller_v1 sec6
    severity = card["severity"]                       # 0-1, fraction DIRTY in domain
    recency = days_since(card["last_worked"])
    trend = card["trend"]                             # -1 degrading, 0 flat, +1 improving
    evidence = card["evidence_count"]

    recency_bonus = min(recency / 7.0, 1.0)           # don't grind same weakness; caps at 7d
    trend_weight = {-1: 1.5, 0: 1.0, 1: 0.5}[trend]   # degrading=urgent
    confidence = min(evidence / 10.0, 1.0)            # low evidence = low confidence

    return severity * recency_bonus * trend_weight * confidence


def rank(cards):
    # Pick = argmax; ties broken by evidence_count (sec6).
    return sorted(cards, key=lambda c: (priority_score(c), c["evidence_count"]), reverse=True)


def card(dom, sev, last, trend, ev):
    return {"domain": dom, "severity": sev, "last_worked": last,
            "trend": trend, "evidence_count": ev}


results = []  # (name, passed, detail)


def check(name, condition, detail):
    results.append((name, bool(condition), detail))


# --- sec11 SECONDARY FALSIFIER: severity-only sort, all else neutralized ---
# recency>=7 (bonus=1), evidence>=10 (conf=1), trend=0 (weight=1) -> score = severity
SAT = "2026-06-15"  # 7 days back -> recency_bonus = 1.0
sev_cards = [
    card("A", 0.8, SAT, 0, 10),
    card("B", 0.4, SAT, 0, 10),
    card("C", 0.1, SAT, 0, 10),
]
order = [c["domain"] for c in rank(sev_cards)]
check("sec11_severity_sort", order == ["A", "B", "C"],
      f"expected A,B,C (sev 0.8>0.4>0.1); got {order}")

# --- sec12 RECENCY modulation: freshly-worked weakness deprioritized ---
# equal severity/trend/evidence, different last_worked
rec_cards = [
    card("stale", 0.5, "2026-06-01", 0, 10),  # 21d -> bonus 1.0
    card("fresh", 0.5, "2026-06-21", 0, 10),  # 1d  -> bonus 0.142
]
order = [c["domain"] for c in rank(rec_cards)]
check("sec12_recency_mod", order == ["stale", "fresh"],
      f"stale must outrank fresh (don't grind); got {order} "
      f"scores stale={priority_score(rec_cards[0]):.3f} fresh={priority_score(rec_cards[1]):.3f}")

# --- sec12 TREND modulation: degrading > flat > improving ---
trend_cards = [
    card("degrading", 0.5, SAT, -1, 10),  # weight 1.5
    card("flat", 0.5, SAT, 0, 10),        # weight 1.0
    card("improving", 0.5, SAT, +1, 10),  # weight 0.5
]
order = [c["domain"] for c in rank(trend_cards)]
check("sec12_trend_mod", order == ["degrading", "flat", "improving"],
      f"expected degrading,flat,improving; got {order}")

# --- sec12 CONFIDENCE modulation: thin-evidence severity discounted ---
conf_cards = [
    card("trusted", 0.5, SAT, 0, 10),  # conf 1.0 -> 0.5
    card("thin", 0.9, SAT, 0, 2),      # conf 0.2 -> 0.9*0.2 = 0.18
]
order = [c["domain"] for c in rank(conf_cards)]
check("sec12_confidence_mod", order == ["trusted", "thin"],
      f"thin-evidence 0.9 must NOT beat well-evidenced 0.5; got {order} "
      f"scores trusted={priority_score(conf_cards[0]):.3f} thin={priority_score(conf_cards[1]):.3f}")

# --- TIE-BREAK: equal score -> more evidence wins (sec6) ---
tie_cards = [
    card("more_ev", 0.5, SAT, 0, 20),  # conf caps at 1.0 -> score 0.5
    card("less_ev", 0.5, SAT, 0, 10),  # conf 1.0 -> score 0.5 (tie)
]
order = [c["domain"] for c in rank(tie_cards)]
check("sec6_tiebreak_evidence", order == ["more_ev", "less_ev"],
      f"tie on score -> higher evidence_count first; got {order}")

# --- COMBINED 4-card realistic case (sec12 acceptance) ---
combo = [
    card("biology_dates", 0.45, "2026-06-08", -1, 12),  # 14d, degrading, trusted
    card("chem_names",    0.70, "2026-06-21", 0, 8),     # 1d fresh, flat
    card("physics_const", 0.30, "2026-05-22", 0, 15),    # 31d stale, flat, trusted
    card("history_dates", 0.90, "2026-06-22", +1, 3),    # today, improving, thin
]
ranked = rank(combo)
order = [c["domain"] for c in ranked]
# expected: biology_dates wins (mid-sev * full-recency * 1.5 degrading * full-conf)
scores = {c["domain"]: round(priority_score(c), 4) for c in combo}
check("sec12_combined_top", order[0] == "biology_dates",
      f"top should be biology_dates (degrading+stale+trusted); got order={order} scores={scores}")

# ---- report ----
print("=" * 64)
print("CONTROLLER PROBE  -  priority_function unit test (sec6/11/12)")
print("=" * 64)
passed = 0
for name, ok, detail in results:
    tag = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    print(f"[{tag}] {name}")
    if not ok:
        print(f"       {detail}")
print("-" * 64)
n = len(results)
print(f"RESULT: {passed}/{n} cases pass")
verdict = "PROBE PASS" if passed == n else "PROBE FAIL -> concept broken, revisit sec6"
print(verdict)
print("=" * 64)
