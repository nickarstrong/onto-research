#!/usr/bin/env python3
"""
controller.py -- organism-0 controller (ROADMAP Step 4, "the entity's will").

Minimum viable controller: runs ONE self-improvement cycle with no operator
intervention between SELECT and CONTACT.

DELTA vs CONCEPT_controller_v1 (LOCKED v225) -- built to DISK, not to the doc
(§3.10 disk wins; concept doc left frozen, deltas recorded here):
  D1 self_model card schema: REAL = {name, severity:"low|med|high",
     evidence_refs:[...], audit_instruction} (selfmodel_compile.compile_model),
     NOT {domain, severity:float, trend, evidence_count, last_worked}. So the
     concept §6 float/trend/recency priority cannot run. selfmodel_compile ALREADY
     sorts weaknesses worst-first -> SELECT = worst-first + goal_stack anti-regrind.
  D2 self_model.json is compiled from Founder disposition-audit (E15), not standing.
     Controller READS it; it does not author it.
  D3 VERIFY (autonomous, no-human) = o0_temporal_evidence.scope_verdict only.
     The o0_loop PENDING_B2 path needs an external Claude B2 session -> NOT
     autonomous -> out of minimum scope (Step 5+). NORTH STAR "no operator between
     SELECT and CONTACT" forces the temporal-scope path here.
  D4 MEASURE severity = observed rate_F (#DIRTY/#verified this cycle) vs tier
     baseline (high=0.70, med=0.50, low=0.30 per selfmodel_compile._tier).
  D5 CONTACT uses o0_contact.emit; its VALID_TRIGGERS = {PLATEAU,GEN_FAIL,
     GATE_FAIL_LEARN}. We map controller outcomes onto those (DONE/STUCK -> review
     log; PLATEAU on no-improvement; GATE_FAIL_LEARN on fa_live breach = STOP).
  D6 weakness.name is a DISPOSITION (e.g. "fabricated-specifics") spanning topics,
     not a topic. GENERATE cycles topics; rate_F is the disposition's prevalence
     proxy. Per-disposition attribution is coarse at minimum (R2: flagged).

fa_live=0 INVARIANT (concept §8, inherited): only CLEAN claims ABSORB. A DIRTY
reaching ABSORB -> immediate halt + GATE_FAIL_LEARN contact + rollback.

Seams: GENERATE and VERIFY are injected (live_adapters() wires the real modules;
--dry-run injects offline mocks so the state machine is provable with no GPU/net).

Usage:
  python controller.py --dry-run --self-model self_model.json     # offline proof
  python controller.py --live --self-model self_model.json --n 8  # real cycle
"""

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# tier baseline (selfmodel_compile._tier thresholds: rate_F at 0.30/0.50/0.70)
TIER_BASELINE = {"low": 0.30, "med": 0.50, "high": 0.70}
TIER_RANK = {"high": 0, "med": 1, "low": 2}  # worst first (selfmodel_compile order)

DEFAULT_BUDGET = {"self_improve": 3, "operator": 1}
REGRIND_COOLDOWN = 1  # don't re-pick the same weakness within N cycles (anti-grind)

CONTACT_LOG = "contact_log.jsonl"
GOAL_STACK = "goal_stack.json"
SELFLEARN_TRACE = "selflearn_trace.jsonl"


def _emit_trace(trace_path, row):
    """Append ONE per-visit witness row (GATE_selflearn signals). Binary-LF write
    (ENV PRECONDITION sec1: text-mode CRLF-translates and breaks LF md5 anchors)."""
    line = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
    Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "ab") as f:
        f.write(line)


# ════════════════════════════════════════════════════════════════════
# STATE
# ════════════════════════════════════════════════════════════════════

class GoalStack:
    """Persistent per-weakness work record (goal_stack.json). LIFO operator push;
    self-improve goals ranked by SELECT. Tracks anti-regrind + outcome history."""

    def __init__(self, path=GOAL_STACK):
        self.path = Path(path)
        self.state = {"cycle": 0, "weaknesses": {}, "stack": []}
        if self.path.exists():
            self.state = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self):
        self.path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    def rec(self, name):
        return self.state["weaknesses"].setdefault(
            name, {"cycles_used": 0, "last_worked_cycle": -10**9, "history": []})

    def mark_worked(self, name, observed_rate_f, baseline, improved):
        r = self.rec(name)
        r["cycles_used"] += 1
        r["last_worked_cycle"] = self.state["cycle"]
        r["history"].append({"cycle": self.state["cycle"],
                             "observed_rate_f": round(observed_rate_f, 4),
                             "baseline": baseline, "improved": improved})


# ════════════════════════════════════════════════════════════════════
# SELECT  (D1: worst-first over real cards + anti-regrind; no float/trend/recency)
# ════════════════════════════════════════════════════════════════════

def select_weakness(self_model, gstack):
    """Pick the eligible weakness with a ROTATION FLOOR: least-worked first so every
    weakness is visited over a run, worst-severity as the tiebreak (anti-regrind keeps
    a just-worked card off for REGRIND_COOLDOWN cycles). Deterministic; ties on
    cycles_used -> worse severity, then original order (stable)."""
    cyc = gstack.state["cycle"]
    cands = []
    for idx, w in enumerate(self_model["weaknesses"]):
        rr = gstack.rec(w["name"])
        cooled = (cyc - rr["last_worked_cycle"]) > REGRIND_COOLDOWN
        cands.append((TIER_RANK[w["severity"]], rr["cycles_used"], idx, cooled, w))
    eligible = [c for c in cands if c[3]] or cands  # fall back to all if all cooling
    # ROTATION FLOOR (BUILD-FRONT #2): least-worked PRIMARY, worst-severity tiebreak,
    # original order last. Severity-primary starved any lower tier whenever >=2 worst-tier
    # weaknesses existed (cooldown=1 empties only one/cycle) -> 3rd never SELECTed (floor
    # FAIL, trace 9c960429). cycles_used-primary guarantees every weakness rotates; worst-
    # first preserved as the tiebreak among equally-worked cards.
    eligible.sort(key=lambda c: (c[1], c[0], c[2]))  # (cycles_used, TIER_RANK, idx)
    return eligible[0][4]


def pin_or_select(self_model, gstack, pin_weakness):
    """D-GATE pin path (pack v246 sec 3.1, kills D1): when --pin-weakness is set,
    bypass rotation and return that card every cycle, so a targeted A/B stamps the
    SAME disposition on every cycle (n_relevant scales to n_cycles -> real stats).
    PIN IS PRE-VERIFY (SELECT side) -> verdict-blind, firewall intact. Rotation is
    correct for the autonomous organism; the GATE pins, never the organism."""
    if not pin_weakness:
        return select_weakness(self_model, gstack)
    for w in self_model["weaknesses"]:
        if w["name"] == pin_weakness:
            return w
    sys.exit(f"FATAL: --pin-weakness '{pin_weakness}' not in self_model")


# ════════════════════════════════════════════════════════════════════
# CONTACT  (D5: map onto o0_contact triggers; DRY logs locally)
# ════════════════════════════════════════════════════════════════════

def contact(reason, cycle, detail, live):
    event = {"timestamp": datetime.now(timezone.utc).isoformat(),
             "reason": reason, "cycle": cycle, "detail": detail}
    with open(CONTACT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"  [CONTACT] {reason} @ cycle {cycle}: {detail}")
    if live:
        # map onto existing o0_contact.VALID_TRIGGERS
        from o0_contact import emit as oc_emit
        trig = {"FA_LIVE_BREACH": "GATE_FAIL_LEARN",
                "STUCK": "PLATEAU"}.get(reason)
        if trig:
            oc_emit(trig, cycle, detail)
    return event


# ════════════════════════════════════════════════════════════════════
# CYCLE  (PLAN -> EXECUTE[GENERATE->VERIFY->ABSORB] -> MEASURE -> CONTACT)
# ════════════════════════════════════════════════════════════════════

def run_cycle(self_model, gstack, generate, verify, absorb, n, live, pin_weakness=None,
              trace_path=None):
    """One self-improvement cycle. Returns the contact event (cycle terminator)."""
    cyc = gstack.state["cycle"]

    # ---- SELECT ----
    w = pin_or_select(self_model, gstack, pin_weakness)
    baseline = TIER_BASELINE[w["severity"]]
    print(f"\n[SELECT] weakness='{w['name']}' severity={w['severity']} "
          f"baseline_rate_f={baseline}")
    print(f"         audit: {w['audit_instruction'][:90]}")

    # ---- PLAN ----
    print(f"[PLAN]   GENERATE {n} -> VERIFY -> ABSORB -> MEASURE")

    # ---- EXECUTE: GENERATE ----
    try:
        claims = generate(n)
    except Exception as e:
        return contact("RESOURCE", cyc, f"GENERATE failed: {e}", live)
    print(f"[EXEC]   generated {len(claims)} claim(s)")
    # MECHANISM-USE witness: retrieval-hit = records retrieve() ACTUALLY returned at
    # generate time (prereg L51). Read from the proposer SIDE-CHANNEL only; verify()
    # never sees it -> firewall intact. dry/blind generate -> absent/zeros -> 0.
    retrieval_hit = sum(getattr(generate, "retrieval_hits", []) or [])

    # ---- EXECUTE: VERIFY ----
    verdicts = []
    for c in claims:
        v, reasons = verify(c)
        # rung C delta-3: stamp the SELECTed disposition onto the record.
        # Post-verify (verify never sees this) -> firewall + T2 byte-identity held.
        verdicts.append({"claim": c, "verdict": v, "reasons": reasons,
                         "targeted_weakness": w["name"]})
    n_dirty = sum(1 for v in verdicts if v["verdict"] == "DIRTY")
    n_total = len(verdicts)
    print(f"[CHECK]  {n_total - n_dirty} CLEAN / {n_dirty} DIRTY")

    # ---- ABSORB (+ fa_live invariant §8) ----
    absorbed = 0
    for v in verdicts:
        if v["verdict"] == "CLEAN":
            absorb(v, kind="knowledge")
            absorbed += 1
        else:
            absorb(v, kind="catch_record")
    # fa_live: nothing DIRTY may have entered knowledge. We absorbed only CLEAN
    # above, so the invariant holds by construction; assert it explicitly.
    leaked = [v for v in verdicts if v["verdict"] == "DIRTY" and v.get("_absorbed_knowledge")]
    if leaked:
        fa = round(len(leaked) / max(1, absorbed + len(leaked)), 4)  # F4: fa_live>0
        if trace_path:
            _emit_trace(trace_path, {
                "cycle": cyc, "weakness": w["name"], "select_target": w["name"],
                "rate_f": round((n_dirty / n_total) if n_total else 1.0, 4),
                "clean_count": absorbed, "retrieval_hit": retrieval_hit, "fa_live": fa,
                "ts": datetime.now(timezone.utc).isoformat()})
        return contact("FA_LIVE_BREACH", cyc,
                       f"{len(leaked)} DIRTY reached knowledge -> HALT", live)
    print(f"[ABSORB] {absorbed} -> knowledge, {n_total - absorbed} -> catch-record, fa_live=0")

    # ---- MEASURE (D4: observed rate_F vs tier baseline) ----
    observed = (n_dirty / n_total) if n_total else 1.0
    improved = observed < baseline
    gstack.mark_worked(w["name"], observed, baseline, improved)
    print(f"[MEASURE] observed_rate_f={observed:.3f} vs baseline={baseline} "
          f"-> {'IMPROVED' if improved else 'NOT IMPROVED'}")
    if trace_path:
        _emit_trace(trace_path, {
            "cycle": cyc, "weakness": w["name"], "select_target": w["name"],
            "rate_f": round(observed, 4), "clean_count": absorbed,
            "retrieval_hit": retrieval_hit, "fa_live": 0.0,
            "ts": datetime.now(timezone.utc).isoformat()})

    # ---- CONTACT ----
    if improved:
        return contact("DONE", cyc,
                       f"'{w['name']}' rate_f {baseline}->{observed:.3f}, "
                       f"{absorbed} absorbed", live)
    return contact("STUCK", cyc,
                   f"'{w['name']}' rate_f {observed:.3f} >= baseline {baseline}, "
                   f"no improvement", live)


def capture_cold_baseline(generate_blind, verify, n, trace_path, phase_label="baseline"):
    """BUILD-FRONT #3 (F1): emit ONE unconditioned pre-conditioning reference row
    BEFORE any ABSORB feeds the proposer, so the F1 early->late |delta(rate_f)| has a
    genuine cold anchor.

    Prior design had NO unconditioned window: every trace row was already inside the
    wired run, so 'early' == first conditioned visits == already saturated (cycle-1
    rate_f 0.000/0.125 vs no headroom). This measures rate_f with the BLIND adapter
    (conditioned=False -> context="" -> retrieval OFF) and writes NOTHING to the absorb
    trail, so the conditioned run that follows starts cold (proposer un-fed).

    Emits cycle:0, phase:"baseline", retrieval_hit:0 -> the reader pairs this against the
    LATE conditioned window. FIREWALL: generate_blind emits {topic,claim}; verify()
    (external oracle) never sees a retrieval handle. NO absorb() call here by design."""
    claims = generate_blind(n)
    n_dirty = 0
    for c in claims:
        v, _reasons = verify(c)
        if v == "DIRTY":
            n_dirty += 1
    n_total = len(claims)
    rate_f = round((n_dirty / n_total) if n_total else 1.0, 4)
    if trace_path:
        _emit_trace(trace_path, {
            "cycle": 0, "phase": phase_label,
            "weakness": "__baseline__", "select_target": "__baseline__",
            "rate_f": rate_f, "clean_count": n_total - n_dirty,
            "retrieval_hit": 0, "fa_live": 0.0,
            "ts": datetime.now(timezone.utc).isoformat()})
    print(f"[BASELINE] unconditioned cold rate_f={rate_f:.3f} "
          f"({n_dirty}/{n_total} DIRTY, retrieval+absorb OFF) -> trace cycle:0 phase:{phase_label}")
    return rate_f


def run(self_model_path, generate, verify, absorb, n, live, max_cycles, pin_weakness=None,
        trace_path=None):
    self_model = json.loads(Path(self_model_path).read_text(encoding="utf-8"))
    if "weaknesses" not in self_model or not self_model["weaknesses"]:
        sys.exit("FATAL: self_model has no weaknesses (run selfmodel_compile first)")
    gstack = GoalStack()

    print("=" * 70)
    print("ORGANISM-0 CONTROLLER -- Step 4 (minimum viable, 1 cycle/SELECT->CONTACT)")
    print(f"  substrate : {self_model.get('substrate')}")
    print(f"  weaknesses: {self_model['n_weaknesses']} (worst-first)")
    print(f"  mode      : {'LIVE' if live else 'DRY-RUN (mock GENERATE/VERIFY)'}")
    print(f"  cycles    : {max_cycles}")
    print("=" * 70)

    for _ in range(max_cycles):
        gstack.state["cycle"] += 1
        ev = run_cycle(self_model, gstack, generate, verify, absorb, n, live,
                       pin_weakness=pin_weakness, trace_path=trace_path)
        gstack.save()
        if ev["reason"] == "FA_LIVE_BREACH":
            print("\n[HALT] fa_live breach -> STOP (operator must clear).")
            return 2
    print(f"\n[DONE] {max_cycles} cycle(s) complete. contact_log={CONTACT_LOG} "
          f"goal_stack={GOAL_STACK}")
    return 0


# ════════════════════════════════════════════════════════════════════
# ADAPTERS
# ════════════════════════════════════════════════════════════════════

# --------------------------------------------------------------------------- #
# CITATION EXISTENCE PASS (G2 wire -- Q2 verifier BESIDE temporal scope_verdict)
# --------------------------------------------------------------------------- #
# Q2 (citation_verify, G1-passed 43b1104) sits beside temporal-verify in the
# verify path. Temporal catches ungroundable numbers/years; this catches a
# fabricated *identifier* -- a syntactically valid DOI that does not resolve.
# FIREWALL (R11 / pack 3.2): oracle = EXTERNAL REGISTRY ONLY (Crossref). GOLD and
# episodic memory NEVER enter here. citation_pass is a pure function of
# (claim, oracle); it reads no knowledge-store field.
import re as _re
from citation_verify import (verify_citation as _verify_citation, DIRTY as _C_DIRTY,
                             CrossrefOracle as _CrossrefOracle)

# Unanchored search variant of citation_verify._DOI_RE -- finds DOIs inside prose.
# (DOIs may contain '.', so '.' is NOT excluded; a trailing sentence period is
#  stripped below.) Excludes whitespace + common closing punctuation.
_DOI_FIND = _re.compile(r"10\.\d{4,9}/[^\s\"'<>,;)\]]+")

_CITATION_ORACLE = None  # a test may override via controller._CITATION_ORACLE


def _oracle():
    global _CITATION_ORACLE
    if _CITATION_ORACLE is None:
        _CITATION_ORACLE = _CrossrefOracle(timeout=5.0, mailto="council@ontostandard.org")
    return _CITATION_ORACLE


def citation_pass(claim, oracle=None):
    """Extract DOIs from a free-text claim and check existence against the external
    registry. Returns (dirty_dois, annotations). DIRTY ONLY on a positive registry
    'absent'; resolution-failure / malformed -> UNVERIFIED (never a flag)."""
    orc = oracle or _oracle()
    seen, dirty, ann = set(), [], []
    for d in _DOI_FIND.findall(claim or ""):
        d = d.rstrip(".")  # trailing sentence punctuation is not part of the DOI
        if d in seen:
            continue
        seen.add(d)
        v = _verify_citation(d, orc)
        ann.append(f"doi_{v.lower()}:{d}")
        if v == _C_DIRTY:
            dirty.append(d)
    return dirty, ann


def merge_verdict(temporal_verdict, temporal_reasons, claim, oracle=None):
    """DIRTY dominates; UNVERIFIED != CLEAN (temporal verdict stands when no
    citation flag). SHAPE-PRESERVING: scope_verdict returns a dict and the
    downstream falsifier.run_arm calls reasons.get(...), so reasons MUST stay a
    dict. Citation findings go under a 'citation' key -- never coerced to a list."""
    dirty, ann = citation_pass(claim, oracle)
    if isinstance(temporal_reasons, dict):
        reasons = dict(temporal_reasons)
    else:
        reasons = {"temporal": temporal_reasons}
    reasons["citation"] = {"dirty_dois": dirty, "annotations": ann}
    verdict = "DIRTY" if dirty else temporal_verdict
    return verdict, reasons


def _live_retrieve_fn(trail_path):
    """Proposer retrieval feed, re-read PER generate() call from the LIVE ABSORB
    trail (where absorb() writes verify-confirmed knowledge). Fixes BUILD-FRONT #1
    root cause: a boot-time snapshot of an empty cold-start curated file pinned
    retrieval_hit==0 -> within-run self-learning was unwitnessable.
    FIREWALL UNCHANGED: output feeds compose_context -> PROMPT only; the emitted
    dict stays {topic,claim}; verify() (external oracle) never sees it."""
    from o0_retrieve import load_confirmed, retrieve  # PROPOSER-feed only
    def _fn(topic, _confirmed_ignored, k=3):
        confirmed_now = load_confirmed(trail_path) if Path(trail_path).exists() else []
        return retrieve(topic, confirmed_now, k=k)
    return _fn


def live_adapters(conditioned=False, curated_path="o0_verdicts_curated.jsonl",
                  gold_frame_path="gold_frame.txt"):
    """Wire the REAL on-disk pipeline (run from lab/dpo/, Ollama up, net on).

    rung C delta-2: the GENERATE seam now routes through the SEALED Step-6
    proposer factory (generate_step6.make_generate). BOTH arms share that one
    substrate call path; the ONLY difference is proposer-context:
      conditioned=False  (BLIND / raw arm)      -> context = ""   (no memory)
      conditioned=True   (CONDITIONED / curated)-> context = retrieved CURATED
                                                   ABSORB facts + GOLD frame
    FIREWALL (pack 3.2): retrieval/GOLD enter the PROMPT only. The emitted dict
    is EXACTLY {topic,claim}; verify() below is untouched and never sees the
    curated view, a retrieval handle, or the frame. generate()/verify() share
    no field -> belief-checks-belief / memory-checks-memory is impossible.
    Model string is imported (single source of truth), not re-declared.
    """
    from rung1_wiring_v0 import OLLAMA_MODEL          # single source of truth (model)
    from o0_domain_list import DOMAIN_TOPICS
    from generate_step6 import make_generate          # SEALED proposer factory
    import o0_temporal_evidence as TE
    import o0_temporal_probe_v5 as T  # frozen V6 probe (scope_verdict's oracle)
    from o0_accumulator import Accumulator

    acc = Accumulator("eval/o0/o0_verdicts.jsonl")

    # ── GENERATE seam (delta-2): conditioned arm reads the CURATED view ONLY ──
    if conditioned:
        # WIRING FIX (BUILD-FRONT #1, F3=0 root cause): retrieve over the LIVE ABSORB
        # trail PER generate() call -- NOT a boot snapshot of the (empty, cold-start)
        # curated file. live feed = the SAME path absorb()/Accumulator writes to above,
        # so within-run confirmed knowledge becomes retrievable -> retrieval_hit can fire.
        # curated_path retained for API stability (no daemon signature break).
        live_trail = "eval/o0/o0_verdicts.jsonl"  # == Accumulator path; single source
        retrieve_fn = _live_retrieve_fn(live_trail)
        gold_frame = (Path(gold_frame_path).read_text(encoding="utf-8")
                      if Path(gold_frame_path).exists() else "")
        generate = make_generate(
            conditioned=True, model=OLLAMA_MODEL, topics=DOMAIN_TOPICS,
            audit_instruction="", confirmed=[], retrieve_fn=retrieve_fn,
            gold_frame=gold_frame, k=3)
    else:
        generate = make_generate(
            conditioned=False, model=OLLAMA_MODEL, topics=DOMAIN_TOPICS,
            audit_instruction="")

    def verify(c):
        # autonomous temporal scope: enrich one record's years/specifics live,
        # then deterministic scope_verdict (D3). Network-bound, LOCAL.
        claim = c["claim"]
        ctx = T._TOK(claim)
        years_ce, years_bce = TE.extract_years_ext(claim)
        per_year, snippets = {}, {}
        for y in years_ce:
            sent = T.sentence_of_year(claim, y)
            v, log = T.verify_year(y, sent, ctx)
            per_year[y] = v
            for t in log.get("tried", []):
                if isinstance(t, dict) and t.get("confirm"):
                    snippets[y] = {"qid": t.get("qid"), "via": t.get("confirm"),
                                   "snippet": t.get("snippet", "")}
                    break
        for yb in years_bce:
            per_year[yb] = "ABSTAIN_BCE_unverifiable"
        per_specific, ocache = {}, {}
        for spec in TE.extract_fulldates(claim) + TE.extract_numbers(claim):
            sv_, _ = TE.verify_specific(spec, claim, ctx, T, ocache)
            per_specific[TE._norm(spec)] = sv_
        rec = {"claim": claim, "evidence": {},
               "temporal": {"per_year": per_year, "snippets": snippets,
                            "per_specific": per_specific}}
        tv, treasons = TE.scope_verdict(rec)
        return merge_verdict(tv, treasons, claim)

    def absorb(v, kind):
        c = v["claim"]
        topic = c.get("topic", "") if isinstance(c, dict) else ""
        claim_str = c.get("claim", "") if isinstance(c, dict) else c
        rec = {"id": f"ctrl_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}",
               "topic": topic, "claim": claim_str, "best_abstract": "",
               "verdict": "ABSORB" if (kind == "knowledge") else "REJECT",
               "ctrl_reasons": v["reasons"], "kind": kind,
               "targeted_weakness": v.get("targeted_weakness"),
               "ts": datetime.now(timezone.utc).isoformat()}
        if kind == "knowledge":
            rec["_absorbed_knowledge"] = True
        acc.append(rec)
        v["_absorbed_knowledge"] = (kind == "knowledge")

    return generate, verify, absorb


def dry_adapters():
    """Offline mocks: deterministic, no GPU/net. Proves the state machine.
    A claim whose topic index is odd is mocked DIRTY (an unverified specific);
    even is CLEAN. Lets MEASURE compute a real rate_F and exercise both paths."""
    counter = {"i": 0}

    def generate(n):
        out = []
        for _ in range(n):
            i = counter["i"]; counter["i"] += 1
            if i % 2 == 0:
                out.append({"topic": f"topic_{i}",
                            "claim": f"Verified fact #{i} with no unsupported specifics."})
            else:
                out.append({"topic": f"topic_{i}",
                            "claim": f"Fact #{i} happened on February 30, 1999 (56.3%)."})
        return out

    def verify(c):
        # mirror scope_verdict's contract: DIRTY iff an unverified non-year specific
        # is present; CLEAN otherwise.
        bad = ("February 30" in c["claim"]) or ("56.3%" in c["claim"])
        return ("DIRTY", ["unverified_non_year_specific:mock"]) if bad \
            else ("CLEAN", ["year+subject supported; non-year specifics supported or none"])

    def absorb(v, kind):
        v["_absorbed_knowledge"] = (kind == "knowledge")

    return generate, verify, absorb


# ════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # pack v246 sec 1 (durable cp1251 fix): force UTF-8 stdio so decorative prints
    # cannot HARD-CRASH the live runner under a cp1251 console. Replaces the env-only
    # PYTHONUTF8 workaround (structural, not ceremonial).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="organism-0 controller (Step 4)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="offline mocks (no GPU/net) -- proves state machine")
    mode.add_argument("--live", action="store_true",
                      help="wire real pipeline (run from lab/dpo, Ollama up, net on)")
    ap.add_argument("--self-model", default="self_model.json")
    ap.add_argument("--n", type=int, default=8, help="claims generated per cycle")
    ap.add_argument("--cycles", type=int, default=1, help="number of cycles")
    # rung C delta-2: CONDITIONED GENERATE (curated-view-fed proposer). verify() untouched.
    ap.add_argument("--conditioned", action="store_true",
                    help="CONDITIONED arm: feed retrieved CURATED facts + GOLD frame into GENERATE")
    ap.add_argument("--curated-path", default="o0_verdicts_curated.jsonl",
                    help="curated-view JSONL the conditioned proposer retrieves over")
    ap.add_argument("--gold-frame", default="gold_frame.txt",
                    help="GOLD belief-frame file prepended to the conditioned proposer context")
    # pack v246 sec 3.1: gate-only SELECT pin (no rotation) for a targeted A/B.
    ap.add_argument("--pin-weakness", default=None,
                    help="D-GATE only: pin SELECT to this weakness every cycle (verdict-blind)")
    ap.add_argument("--selflearn-trace", default=None,
                    help="GATE_selflearn: append per-visit witness rows to this JSONL")
    args = ap.parse_args()

    gen, ver, abs_ = (live_adapters(conditioned=args.conditioned,
                                    curated_path=args.curated_path,
                                    gold_frame_path=args.gold_frame)
                      if args.live else dry_adapters())
    raise SystemExit(run(args.self_model, gen, ver, abs_,
                         n=args.n, live=args.live, max_cycles=args.cycles,
                         pin_weakness=args.pin_weakness,
                         trace_path=args.selflearn_trace))
