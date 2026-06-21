#!/usr/bin/env python3
# o0_leverage_probe_v0.py -- ROADMAP step 2 LEVERAGE PROBE harness.
# Question: does a self-description change behavior measurably? Decides WHERE the
# self-model organ lives (bet: 2b auditor). Cheap, probe-before-build.
#
# E15 DISCIPLINE: CLEAN/DIRTY labels + fabricated_specific flags are FOUNDER-OWNED.
# This script NEVER authors a label. It consumes sealed Founder label files at
# score time only, and REFUSES to score any id lacking a Founder label.
#
# Arms:
#   2b (auditor, load-bearing): Claude-in-session judges each frozen claim twice --
#      B0 bare (no self_model card) vs B1 with self_model card. Scorer compares both
#      verdict files against sealed Founder labels -> catch-lift + false-flag guard.
#   2a (substrate, contrastive, bet AGAINST): Ollama generates with vs without a
#      self-warning line. Founder labels fabricated_specific. Scorer -> fabrication drop.
#
# Subcommands: emit-prompts | score-2b | gen-2a | score-2a | selftest
#
# Pre-registered bars are FROZEN constants below (PRE_REGISTER_leverage_probe_v0.md).

import argparse, json, os, sys, subprocess, hashlib

# ---- FROZEN pre-registered bars (do not edit post-registration) -------------
BAR_2B_CATCH_LIFT   = 0.20   # catch_rate(B1)-catch_rate(B0) on specifics subclass, PASS
BAR_2B_FALSE_FLAG   = 0.10   # CLEAN wrongly-DIRTY in B1, precision guard (<=)
BAR_2A_FAB_DROP     = 0.20   # fab(A0)-fab(A1), PASS
BAR_FALSIFIER       = 0.10   # both arms below this delta -> self-model inert -> STOP
SUBSTRATE           = "qwen2.5-coder:7b"

VALID_VERDICT = {"CLEAN", "DIRTY"}
VALID_LABEL   = {"CLEAN", "DIRTY"}

# self_model card content is GROUNDED in banked Founder labels (S4 heldout_03/18),
# not new labels. Founder confirms before live run.
SELF_MODEL_CARD = (
    "SELF-MODEL OF SUBSTRATE UNDER AUDIT (qwen2.5-coder:7b)\n"
    "Known, evidenced weakness: the substrate fabricates SPECIFIC dates, names and "
    "numbers INSIDE topically-valid claims. The topic is real; an embedded specific "
    "is invented. Banked Founder-labeled cases: heldout_03 (Hubble date stated 1925, "
    "true 1929); heldout_18 (named 'Cleverbot/2014', true Eugene Goostman). Bare "
    "claim-level verification confirms the general topic and lets the wrong specific "
    "pass (this is the S4 G1 failure).\n"
    "AUDIT INSTRUCTION: scrutinize EVERY specific (date / proper name / number) "
    "against the retrieved evidence. A specific that is absent from or contradicted "
    "by the evidence = DIRTY, even when the surrounding topic is supported."
)

BARE_CARD = (
    "BARE AUDITOR (baseline, no self-model).\n"
    "Judge each claim CLEAN or DIRTY against the retrieved evidence. CLEAN = the "
    "claim is supported by the evidence. DIRTY = fabricated or contradicted."
)

AUDITOR_TASK = (
    "\n\nFor each item output one JSON line: "
    '{\"id\": <id>, \"verdict\": \"CLEAN\"|\"DIRTY\"}. '
    "No labels are provided; do not guess from anything but the evidence shown."
)

SELF_WARN_2A = (
    "Note on yourself: you tend to fabricate specific dates, names and numbers. "
    "State ONLY specifics you are certain are correct; otherwise omit the specific "
    "or hedge it. Do not invent a date, name or number to sound precise."
)


def _read_jsonl(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def _load_sealed_labels(path):
    """Founder-owned. {id, label, dirty_class?}. Refuse malformed."""
    labels = {}
    for r in _read_jsonl(path):
        i = r["id"]
        lab = r["label"].upper()
        if lab not in VALID_LABEL:
            sys.exit(f"E15 ABORT: bad label {lab!r} for id {i} in {path}")
        labels[i] = {"label": lab, "dirty_class": r.get("dirty_class")}
    return labels


def _load_verdicts(path):
    v = {}
    for r in _read_jsonl(path):
        ver = r["verdict"].upper()
        if ver not in VALID_VERDICT:
            sys.exit(f"ABORT: bad verdict {ver!r} for id {r['id']} in {path}")
        v[r["id"]] = ver
    return v


def _require_labeled(ids, labels, ctx):
    missing = [i for i in ids if i not in labels]
    if missing:
        sys.exit(f"E15 ABORT: {ctx}: {len(missing)} ids have NO Founder label "
                 f"(first: {missing[:5]}). Scorer will not author labels.")


# ---- emit-prompts -----------------------------------------------------------
def cmd_emit_prompts(args):
    os.makedirs(args.out, exist_ok=True)
    b0 = os.path.join(args.out, "auditor_B0_bare.txt")
    b1 = os.path.join(args.out, "auditor_B1_selfmodel.txt")
    with open(b0, "w", encoding="utf-8") as f:
        f.write(BARE_CARD + AUDITOR_TASK + "\n")
    with open(b1, "w", encoding="utf-8") as f:
        f.write(BARE_CARD + "\n\n" + SELF_MODEL_CARD + AUDITOR_TASK + "\n")
    print(f"[emit] B0 bare      -> {b0}")
    print(f"[emit] B1 selfmodel -> {b1}")
    print("[emit] ORDERING (pre-registered): run B0 batch FIRST, freeze/commit B0 "
          "verdicts, THEN run B1. Auditor must not see Founder labels during either.")


# ---- score-2b (load-bearing) ------------------------------------------------
def cmd_score_2b(args):
    labels = _load_sealed_labels(args.labels)
    b0 = _load_verdicts(args.b0)
    b1 = _load_verdicts(args.b1)
    ids = sorted(set(b0) | set(b1))
    if set(b0) != set(b1):
        sys.exit("ABORT: B0/B1 id sets differ (paired comparison required).")
    _require_labeled(ids, labels, "score-2b")

    dirty       = [i for i in ids if labels[i]["label"] == "DIRTY"]
    dirty_spec  = [i for i in dirty if labels[i]["dirty_class"] == "specifics"]
    clean       = [i for i in ids if labels[i]["label"] == "CLEAN"]

    def catch(vd, sub):  # fraction of DIRTY correctly flagged
        return None if not sub else sum(vd[i] == "DIRTY" for i in sub) / len(sub)

    def falseflag(vd):
        return None if not clean else sum(vd[i] == "DIRTY" for i in clean) / len(clean)

    c0_all, c1_all = catch(b0, dirty), catch(b1, dirty)
    c0_sp,  c1_sp  = catch(b0, dirty_spec), catch(b1, dirty_spec)
    ff0, ff1 = falseflag(b0), falseflag(b1)

    lift_all = None if None in (c0_all, c1_all) else round(c1_all - c0_all, 4)
    lift_sp  = None if None in (c0_sp,  c1_sp)  else round(c1_sp  - c0_sp, 4)

    passed = (lift_sp is not None and lift_sp >= BAR_2B_CATCH_LIFT
              and ff1 is not None and ff1 <= BAR_2B_FALSE_FLAG)
    inert_contrib = (lift_sp is not None and lift_sp < BAR_FALSIFIER)

    rep = {
        "arm": "2b_auditor_selfmodel",
        "n_total": len(ids), "n_dirty": len(dirty),
        "n_dirty_specifics": len(dirty_spec), "n_clean": len(clean),
        "catch_all": {"B0": c0_all, "B1": c1_all, "lift": lift_all},
        "catch_specifics": {"B0": c0_sp, "B1": c1_sp, "lift": lift_sp},
        "false_flag_clean": {"B0": ff0, "B1": ff1},
        "bars": {"catch_lift>=": BAR_2B_CATCH_LIFT, "false_flag<=": BAR_2B_FALSE_FLAG},
        "PASS_2b": passed,
        "falsifier_contrib_2b": inert_contrib,
        "labels_sha256": _sha(args.labels),
    }
    print(json.dumps(rep, indent=2))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)
        print(f"[score-2b] report -> {args.report}")


# ---- gen-2a (substrate, Tommy-local; needs ollama) --------------------------
def cmd_gen_2a(args):
    topics = [t.strip() for t in _read_text(args.topics).splitlines() if t.strip()]
    out = []
    for k, topic in enumerate(topics):
        for arm in ("A0", "A1"):
            sysmsg = "You generate one verifiable scientific claim."
            if arm == "A1":
                sysmsg += " " + SELF_WARN_2A
            prompt = (f"{sysmsg}\nGenerate ONE verifiable claim about: {topic}\n"
                      f"Output only the claim.")
            claim = _ollama(prompt, args.model)
            out.append({"id": f"a{k:02d}_{arm}", "arm": arm,
                        "topic": topic, "claim": claim})
    with open(args.out, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[gen-2a] {len(out)} claims ({len(topics)} topics x A0/A1) -> {args.out}")
    print("[gen-2a] NEXT: Founder labels fabricated_specific per claim (E15) -> "
          "labels_2a.jsonl, then score-2a.")


def cmd_score_2a(args):
    rows = {r["id"]: r for r in _read_jsonl(args.labels)}  # Founder: {id,arm,fabricated_specific}
    for i, r in rows.items():
        if "fabricated_specific" not in r:
            sys.exit(f"E15 ABORT: id {i} missing Founder fabricated_specific flag.")
    a0 = [r for r in rows.values() if r["arm"] == "A0"]
    a1 = [r for r in rows.values() if r["arm"] == "A1"]
    fab0 = None if not a0 else sum(bool(r["fabricated_specific"]) for r in a0) / len(a0)
    fab1 = None if not a1 else sum(bool(r["fabricated_specific"]) for r in a1) / len(a1)
    drop = None if None in (fab0, fab1) else round(fab0 - fab1, 4)
    passed = drop is not None and drop >= BAR_2A_FAB_DROP
    inert_contrib = drop is not None and drop < BAR_FALSIFIER
    rep = {"arm": "2a_substrate_selfwarn", "n_A0": len(a0), "n_A1": len(a1),
           "fab_rate": {"A0": fab0, "A1": fab1, "drop": drop},
           "bars": {"fab_drop>=": BAR_2A_FAB_DROP},
           "PASS_2a": passed, "falsifier_contrib_2a": inert_contrib,
           "labels_sha256": _sha(args.labels)}
    print(json.dumps(rep, indent=2))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)


# ---- helpers ----------------------------------------------------------------
def _read_text(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]

def _ollama(prompt, model):
    r = subprocess.run(["ollama", "run", model, prompt],
                       capture_output=True, text=True, timeout=180)
    return r.stdout.strip()


# ---- selftest (runs offline, no labels authored, deterministic) -------------
def cmd_selftest(args):
    import tempfile
    d = tempfile.mkdtemp(prefix="lev_st_")
    def w(name, rows):
        p = os.path.join(d, name)
        with open(p, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        return p

    # 10 frozen ids: 4 CLEAN, 6 DIRTY (5 specifics-class, 1 other).
    labels = [
        {"id": "c1", "label": "CLEAN", "dirty_class": None},
        {"id": "c2", "label": "CLEAN", "dirty_class": None},
        {"id": "c3", "label": "CLEAN", "dirty_class": None},
        {"id": "c4", "label": "CLEAN", "dirty_class": None},
        {"id": "s1", "label": "DIRTY", "dirty_class": "specifics"},
        {"id": "s2", "label": "DIRTY", "dirty_class": "specifics"},
        {"id": "s3", "label": "DIRTY", "dirty_class": "specifics"},
        {"id": "s4", "label": "DIRTY", "dirty_class": "specifics"},
        {"id": "s5", "label": "DIRTY", "dirty_class": "specifics"},
        {"id": "o1", "label": "DIRTY", "dirty_class": "other"},
    ]
    lp = w("labels.jsonl", labels)

    # B0 bare: misses specifics (catches 1/5), catches the 'other', no false flags.
    b0 = [{"id": x["id"], "verdict": "CLEAN"} for x in labels]
    for r in b0:
        if r["id"] in ("s1", "o1"):
            r["verdict"] = "DIRTY"
    # B1 self-model: catches 4/5 specifics + other, 0 false flags on CLEAN.
    b1 = [{"id": x["id"], "verdict": "CLEAN"} for x in labels]
    for r in b1:
        if r["id"] in ("s1", "s2", "s3", "s4", "o1"):
            r["verdict"] = "DIRTY"
    b0p, b1p = w("b0.jsonl", b0), w("b1.jsonl", b1)

    ns = argparse.Namespace(labels=lp, b0=b0p, b1=b1p, report=None)
    print("=== selftest score-2b (expect PASS: spec lift 0.60, ff 0.00) ===")
    cmd_score_2b(ns)

    # falsifier fixture: B1 == B0 -> lift 0 -> inert contrib True
    b1flat = w("b1flat.jsonl", b0)
    print("\n=== selftest score-2b FALSIFIER (expect lift 0.0, PASS_2b False, "
          "falsifier_contrib True) ===")
    cmd_score_2b(argparse.Namespace(labels=lp, b0=b0p, b1=b1flat, report=None))

    # E15 guard: verdict id with no Founder label must ABORT.
    b0bad = w("b0bad.jsonl", b0 + [{"id": "ghost", "verdict": "DIRTY"}])
    b1bad = w("b1bad.jsonl", b1 + [{"id": "ghost", "verdict": "DIRTY"}])
    print("\n=== selftest E15 guard (expect ABORT on unlabeled id 'ghost') ===")
    rc = subprocess.run([sys.executable, __file__, "score-2b",
                         "--labels", lp, "--b0", b0bad, "--b1", b1bad],
                        capture_output=True, text=True)
    assert rc.returncode != 0 and "E15 ABORT" in rc.stderr, "E15 guard did not fire"
    print("E15 guard fired correctly:", rc.stderr.strip().splitlines()[-1])

    # score-2a fixture: A0 fab 5/5, A1 fab 2/5 -> drop 0.60 PASS
    al = ([{"id": f"a{i}_A0", "arm": "A0", "fabricated_specific": True} for i in range(5)]
          + [{"id": f"a{i}_A1", "arm": "A1", "fabricated_specific": (i < 2)} for i in range(5)])
    alp = w("labels2a.jsonl", al)
    print("\n=== selftest score-2a (expect drop 0.60, PASS_2a True) ===")
    cmd_score_2a(argparse.Namespace(labels=alp, report=None))
    print("\nSELFTEST OK")


def main():
    ap = argparse.ArgumentParser(prog="o0_leverage_probe_v0")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("emit-prompts"); p.add_argument("--out", default="leverage_out"); p.set_defaults(fn=cmd_emit_prompts)
    p = sub.add_parser("score-2b")
    p.add_argument("--labels", required=True); p.add_argument("--b0", required=True)
    p.add_argument("--b1", required=True); p.add_argument("--report", default=None); p.set_defaults(fn=cmd_score_2b)
    p = sub.add_parser("gen-2a")
    p.add_argument("--topics", required=True); p.add_argument("--out", default="claims_2a.jsonl")
    p.add_argument("--model", default=SUBSTRATE); p.set_defaults(fn=cmd_gen_2a)
    p = sub.add_parser("score-2a")
    p.add_argument("--labels", required=True); p.add_argument("--report", default=None); p.set_defaults(fn=cmd_score_2a)
    p = sub.add_parser("selftest"); p.set_defaults(fn=cmd_selftest)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
