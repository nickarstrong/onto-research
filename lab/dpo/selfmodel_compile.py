#!/usr/bin/env python3
# selfmodel_compile.py -- ROADMAP step 3 organ.
# disposition-audit cards (name|evidence|fix|severity) -> self_model.json -> auditor card B1'.
# The card the auditor reads is DERIVED, not hand-typed (the §2 hand card is retired here).
# Plugs into the existing o0_leverage_probe_v0.py score-2b harness (B1' replaces B1).
#
# E15: reads Founder disposition-audit output; authors NO labels. Pure compile/render.
# Subcommands: compile | emit-card | selftest

import argparse, json, sys, os

VALID_SEV = {"low", "med", "high"}

def read_jsonl(p):
    out=[]
    for ln in open(p, encoding="utf-8"):
        ln=ln.strip()
        if ln: out.append(json.loads(ln))
    return out

# ---- compile: disposition cards -> self_model.json --------------------------
def _tier(sev):
    # canonical: severity = rate_F, tier low/med/high at 0.30/0.50/0.70 (SPEC sec 1).
    if isinstance(sev,(int,float)):
        return "high" if sev>=0.70 else "med" if sev>=0.50 else "low"
    s=str(sev).lower()
    if s in VALID_SEV: return s
    sys.exit(f"ABORT: bad severity {sev!r}")

def _ev_str(e):
    if isinstance(e,dict):
        return ":".join(str(e[k]) for k in ("item_id","span") if k in e) or json.dumps(e,ensure_ascii=False)
    return str(e)

def compile_model(cards, substrate):
    weaknesses=[]
    for c in cards:
        if "name" not in c: sys.exit(f"ABORT: card missing 'name': {c}")
        fix=c.get("fix") or c.get("proposed_fix")
        if fix is None: sys.exit(f"ABORT: card missing 'fix'/'proposed_fix': {c['name']!r}")
        if "evidence" not in c: sys.exit(f"ABORT: card missing 'evidence': {c['name']!r}")
        if "severity" not in c: sys.exit(f"ABORT: card missing 'severity': {c['name']!r}")
        c={**c,"fix":fix}
        sev=_tier(c["severity"])
        evraw=c["evidence"] if isinstance(c["evidence"],list) else [c["evidence"]]
        ev=[_ev_str(e) for e in evraw]
        weaknesses.append({
            "name": c["name"],
            "severity": sev,
            "evidence_refs": ev,
            # audit_instruction derived from the named disposition + its fix, generically.
            "audit_instruction": (f"Scrutinize for '{c['name']}'. {c['fix']} "
                                  f"If present and unsupported by evidence -> DIRTY."),
        })
    # high severity first -> the card foregrounds the worst dispositions.
    order={"high":0,"med":1,"low":2}
    weaknesses.sort(key=lambda w: order[w["severity"]])
    return {"version":"self_model_v0","substrate":substrate,
            "n_weaknesses":len(weaknesses),"weaknesses":weaknesses}

def render_card(model):
    lines=["SELF-MODEL OF SUBSTRATE UNDER AUDIT ("+model["substrate"]+")",
           "Auto-derived from disposition-audit. Known weaknesses, worst first:"]
    for i,w in enumerate(model["weaknesses"],1):
        refs="; ".join(str(r) for r in w["evidence_refs"])
        lines.append(f"{i}. [{w['severity'].upper()}] {w['name']} — {w['audit_instruction']} "
                     f"(evidence: {refs})")
    lines.append("AUDIT INSTRUCTION: check every specific (date/name/number) against the "
                 "retrieved evidence per the weaknesses above; unsupported specific = DIRTY.")
    return "\n".join(lines)

AUDITOR_TASK=("\n\nFor each item output one JSON line: "
              '{"id": <id>, "verdict": "CLEAN"|"DIRTY"}. Judge against the evidence shown; '
              "no labels are provided.")

def cmd_compile(a):
    cards=read_jsonl(a.cards)
    model=compile_model(cards, a.substrate)
    with open(a.out,"w",encoding="utf-8") as f: json.dump(model,f,indent=2,ensure_ascii=False)
    print(f"[compile] {model['n_weaknesses']} weaknesses -> {a.out}")
    print(f"[compile] severities: "+", ".join(f"{w['name']}={w['severity']}" for w in model["weaknesses"]))

def cmd_emit_card(a):
    model=json.load(open(a.model,encoding="utf-8"))
    card=render_card(model)
    bare=("BARE AUDITOR (baseline, no self-model). Judge each claim CLEAN or DIRTY "
          "against the retrieved evidence.")
    with open(a.b0_out,"w",encoding="utf-8") as f: f.write(bare+AUDITOR_TASK+"\n")
    with open(a.b1_out,"w",encoding="utf-8") as f: f.write(bare+"\n\n"+card+AUDITOR_TASK+"\n")
    print(f"[emit] B0 bare    -> {a.b0_out}")
    print(f"[emit] B1' derived-> {a.b1_out}")
    print("[emit] ORDER: B0 first, freeze, then B1'. Auditor blind to labels (same as §2).")

# ---- selftest ---------------------------------------------------------------
def cmd_selftest(a):
    import tempfile
    d=tempfile.mkdtemp(prefix="sm_st_")
    cards=[
        {"name":"fabricated-specifics","evidence":["heldout_03 1925->1929","heldout_18 Goostman"],
         "fix":"State only specifics confirmable in evidence.","severity":"high"},
        {"name":"overconfident-no-source","evidence":["A2 cluster v194"],
         "fix":"Demand a source for quantitative claims.","severity":"med"},
        {"name":"empty-hedge","evidence":["A4"],"fix":"Reject vacuous hedges.","severity":"low"},
    ]
    cp=os.path.join(d,"cards.jsonl")
    open(cp,"w").write("\n".join(json.dumps(c) for c in cards))
    mp=os.path.join(d,"self_model.json")
    cmd_compile(argparse.Namespace(cards=cp,out=mp,substrate="qwen2.5-coder:7b"))
    model=json.load(open(mp))
    assert model["weaknesses"][0]["severity"]=="high", "high not foregrounded"
    assert model["n_weaknesses"]==3
    b0=os.path.join(d,"b0.txt"); b1=os.path.join(d,"b1.txt")
    cmd_emit_card(argparse.Namespace(model=mp,b0_out=b0,b1_out=b1))
    card=open(b1).read()
    assert "fabricated-specifics" in card and "HIGH" in card, "card render missing"
    # E15 guard: a card missing a field must ABORT
    bad=os.path.join(d,"bad.jsonl"); open(bad,"w").write(json.dumps({"name":"x","evidence":"e","fix":"f"}))
    import subprocess
    rc=subprocess.run([sys.executable,__file__,"compile","--cards",bad,"--out",os.path.join(d,"x.json")],
                      capture_output=True,text=True)
    assert rc.returncode!=0 and "missing" in rc.stderr, "missing-field guard did not fire"
    print("\n--- rendered B1' card ---\n"+card)
    print("\nSELFTEST OK")

def main():
    ap=argparse.ArgumentParser(prog="selfmodel_compile")
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("compile"); p.add_argument("--cards",required=True)
    p.add_argument("--out",default="self_model.json"); p.add_argument("--substrate",default="qwen2.5-coder:7b")
    p.set_defaults(fn=cmd_compile)
    p=sub.add_parser("emit-card"); p.add_argument("--model",required=True)
    p.add_argument("--b0-out",default="auditor_B0_bare.txt"); p.add_argument("--b1-out",default="auditor_B1prime_derived.txt")
    p.set_defaults(fn=cmd_emit_card)
    p=sub.add_parser("selftest"); p.set_defaults(fn=cmd_selftest)
    a=ap.parse_args(); a.fn(a)

if __name__=="__main__": main()
