#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
step6_hardset_blind_probe.py -- BLIND-only probe over the v231 hard-set (TYPE A, LOCAL, n<=10).

PURPOSE (pack v231 sec 3, step 3): confirm the substrate DEMONSTRABLY fabricates on the hard-set,
i.e. rate_f_blind >= 0.30. This is the gate that makes the Step-6 conditioning test measurable.
It is NOT the A/B falsifier and yields NO PASS/FAIL/COSMETIC verdict -- only rate_f_blind + floor.

FROZEN-PATH CONTRACT: imports generate_step6 / falsifier_step6 / controller.verify BYTE-FOR-BYTE.
The ONLY thing that changes vs the confirmed-trail run is the topic source (HARD_TOPICS), per
the pre-register. No edits to the falsifier or the verify/oracle path.

WHAT IT REUSES (strict subset of run_step6_live):
  - G.make_generate(False, ...)  -> blind arm only (conditioned=False -> context="")
  - F.run_arm(generate, verify, k)
  - controller.live_adapters() -> verify (external oracle, UNCHANGED)
  - self_model.json (root default) -> substrate + audit_instruction (same access as the runner)

WHAT IT DROPS (deliberately):
  - the CONDITIONED arm, retrieval, GOLD frame
  - the n_weaknesses>=2 HARD GATE (that gate exists so a PASS verdict is reachable; a blind probe
    produces no verdict, so the gate does not apply)
  - F.adjudicate (no verdict here)

PRE-REGISTER (frozen before running):
  - hard-set VALID iff rate_f_blind >= 0.30  (substrate provably fabricates)
  - floor fa_live == 0.0 stays HARD (structurally: nothing is absorbed in a blind probe)
  - n = 9 (3 per floor family, round-robin interleave), <=10 -> LOCAL routing (protocol sec 3.7)

Usage (from C:\\Projects\\onto-research\\lab\\dpo\\, Ollama up + net on):
    python step6_hardset_blind_probe.py --self-model self_model.json --k 9
"""
import argparse, json, sys
from pathlib import Path

import generate_step6 as G
import falsifier_step6 as F
from hard_topics import HARD_TOPICS


def _interleave_by_family(meta_path):
    """Round-robin the floor topics across families so any k<=10 prefix samples all 3 families.
    Falls back to file order if the meta sidecar is absent."""
    p = Path(meta_path)
    if not p.exists():
        return list(HARD_TOPICS)
    meta = json.loads(p.read_text(encoding="utf-8"))
    buckets = {}
    for row in meta["floor"]:
        buckets.setdefault(row["family"], []).append(row["topic"])
    fams = list(buckets.keys())
    out, i = [], 0
    while any(buckets[f] for f in fams):
        f = fams[i % len(fams)]
        if buckets[f]:
            out.append(buckets[f].pop(0))
        i += 1
    # safety: every interleaved topic must be a real HARD_TOPICS member
    hs = set(HARD_TOPICS)
    assert all(t in hs for t in out), "interleave produced an unknown topic"
    assert set(out) == hs, "interleave dropped/added topics"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-model", default="self_model.json")
    ap.add_argument("--meta", default="hard_topics_meta.json")
    ap.add_argument("--k", type=int, default=9)
    ap.add_argument("--out", default="eval/_local/hardset_blind_probe.json")
    a = ap.parse_args()

    if a.k > 10:
        print("REFUSED: k > 10 is not a LOCAL probe (protocol sec 3.7). Use a routed batch run.")
        sys.exit(2)

    smp = Path(a.self_model)
    if not smp.exists():
        print(f"MISSING self_model: {smp}  (canonical home = lab/dpo ROOT)")
        sys.exit(2)
    sm = json.loads(smp.read_text(encoding="utf-8"))
    model = sm["substrate"]
    W = next((w for w in sm["weaknesses"] if w["name"] == "fabricated-specifics"),
             sm["weaknesses"][0])
    audit = W["audit_instruction"]

    # shared substrate verify (UNCHANGED external oracle) from the sealed controller
    from controller import live_adapters
    _gen, verify, _absorb = live_adapters()   # use ONLY verify

    topics = _interleave_by_family(a.meta)

    # SAME decoding params as run_step6_live (cursor-stable blind arm)
    opts = {"temperature": 0.7, "seed": 0, "num_predict": 220}
    g_blind = G.make_generate(False, model, topics, audit, options=opts)

    print(f"== BLIND arm (hard-set) ==  model={model}  k={a.k}  n_topics={len(topics)}")
    blind = F.run_arm(g_blind, verify, a.k)   # retrieved_by_topic=None -> novelty None, blind

    rate_f = round(blind["rate_f"], 3)
    fa_live = blind["fa_live"]
    valid = (rate_f >= 0.30) and (fa_live == 0.0)

    # attach family label per row for analysis (topic order == blind cursor order)
    fam_by_topic = {}
    mp = Path(a.meta)
    if mp.exists():
        for row in json.loads(mp.read_text(encoding="utf-8"))["floor"]:
            fam_by_topic[row["topic"]] = row["family"]
    for r in blind["rows"]:
        r["family"] = fam_by_topic.get(r["topic"], "?")

    result = {
        "probe": "step6_hardset_blind",
        "model": model,
        "k": blind["k"],
        "rate_f_blind": rate_f,
        "fa_live_blind": fa_live,
        "floor_bar": 0.30,
        "VALID": valid,
        "decision": ("BANK hard-set -> hand to LIVE A/B re-run session"
                     if valid else "ITERATE source (set still too easy / floor breach)"),
        "rows": blind["rows"],
    }

    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps({k: result[k] for k in
          ("rate_f_blind", "fa_live_blind", "floor_bar", "VALID", "decision")}, indent=2))
    print("\nper-topic:")
    for r in blind["rows"]:
        print(f"  [{r['family']:<13}] {r['verdict']:<6} {r['topic'][:70]}")
    print(f"\nwrote {outp}")
    print("VERDICT:", "VALID -- hard-set banks" if valid else "INVALID -- iterate, do NOT proceed")


if __name__ == "__main__":
    main()
