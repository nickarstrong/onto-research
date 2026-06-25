#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
falsifier_v282_quarantine.py -- v282 conditioned-run falsifier (SEALED prereg).

Reads:
  --audit   eval/o0/v282_retrieve_audit.jsonl   (written by o0_retrieve_tap during the run)
  --q97     v282_quarantine_ids.json            (sealed 97-id set; md5 45259b37 over sorted q97)

Bars (ALL must hold -> GREEN; any fail -> RED):
  R-EXCL : union of all retrieved ids in the audit, intersect the 97 quarantine ids == empty.
           (the binding bar -- can FAIL if any bypass pulls an ABSTAIN/quarantined row)
  R-MECH : at least one audit line has non-empty ids  (mechanism EXERCISED; guards the
           v275 "0 exercised cases" non-discriminative trap -- a pure-empty audit is RED).
  R-SEAL : sealed q97 set md5 == 45259b37 (staleness guard on the prereg set).

NON-DISCRIMINATIVE NOTE (honest, R17): R-EXCL is structurally guaranteed at the load
layer because o0_retrieve.load_confirmed is ABSORB-only + pool-hygiene filtered (feed=176,
disjoint from the 97). R-EXCL's real job is to catch a CODE-PATH BYPASS (proposer reading
raw verdicts, an unfiltered retrieve, a topic-collision route) -- not to "discover"
exclusion. R-MECH is what makes the run discriminative vs a no-op.
"""
import argparse, json, hashlib, sys
from pathlib import Path

SEAL_MD5 = "45259b37"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True)
    ap.add_argument("--q97", required=True)
    a = ap.parse_args()

    q = json.loads(Path(a.q97).read_text(encoding="utf-8"))
    q97 = set(q["q97"])
    seal = hashlib.md5(("\n".join(sorted(q97))).encode()).hexdigest()[:8]

    lines = [json.loads(l) for l in Path(a.audit).read_text(encoding="utf-8").splitlines() if l.strip()]
    retrieved = set()
    n_nonempty = 0
    for ln in lines:
        ids = [i for i in (ln.get("ids") or []) if i]
        if ids:
            n_nonempty += 1
        retrieved |= set(ids)

    hit = sorted(retrieved & q97)
    fails = []
    if hit:
        fails.append("R-EXCL: %d quarantined id(s) retrieved: %s" % (len(hit), hit[:10]))
    if n_nonempty == 0:
        fails.append("R-MECH: 0 non-empty retrieval lines -> mechanism NOT exercised (non-discriminative)")
    if seal != SEAL_MD5:
        fails.append("R-SEAL: q97 md5 %s != sealed %s" % (seal, SEAL_MD5))

    print("audit lines      :", len(lines))
    print("topics w/ hits   :", n_nonempty)
    print("distinct retrieved:", len(retrieved))
    print("q97 seal md5     :", seal, "(expect %s)" % SEAL_MD5)
    print("quarantine hits  :", len(hit))
    if fails:
        print("RESULT: RED")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("RESULT: GREEN")


if __name__ == "__main__":
    main()
