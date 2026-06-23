#!/usr/bin/env python3
# -*- coding: ascii -*-
"""g2_report_redact.py -- produce a PUBLIC-SAFE G2 report from the raw local probe.

The raw eval/_local/g2_doi_blind_probe.json carries probe TOPIC TEXT in rows.
Topics are held-out bait -> must NOT enter public git (protocol sec 3.2: public
held-out is eaten by future pretrains -> measurement dead). This strips topic
text to (idx, sha256[:12]) while keeping the auditable signal: aggregate metrics
+ per-row verdict/family. Embeds the md5 of the probe-set files so external
auditors get a dated provenance hash without the set itself.

LEAK GUARD: fails (exit 3) if ANY raw topic string is present in the public
artifact. Content-verified, not intention-verified.
"""
import hashlib
import json
import sys
from pathlib import Path

RAW = Path("eval/_local/g2_doi_blind_probe.json")
OUT = Path("eval/G2_doi_blind_E6.json")
PROBE = ["hard_topics.py", "hard_topics_meta.json"]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main():
    if not RAW.exists():
        print("MISSING raw probe: %s" % RAW)
        sys.exit(2)
    r = json.loads(RAW.read_text(encoding="utf-8"))

    rows = []
    for i, row in enumerate(r.get("rows", [])):
        topic = row.get("topic", "")
        rows.append({
            "idx": i,
            "topic_sha256": hashlib.sha256(topic.encode("utf-8")).hexdigest()[:12],
            "verdict": row.get("verdict"),
            "family": row.get("family", "?"),
            "dirty": row.get("dirty"),
        })

    pub = {
        "probe": r.get("probe"),
        "scope": r.get("scope"),
        "model": r.get("model"),
        "k": r.get("k"),
        "n_topics": r.get("n_topics"),
        "rate_f_blind": r.get("rate_f_blind"),
        "fa_live_blind": r.get("fa_live_blind"),
        "gate_bar": r.get("gate_bar"),
        "GATE": r.get("GATE"),
        "decision": r.get("decision"),
        "_meta": {
            "redacted": "topic text removed (held-out, sec 3.2); idx + sha256[:12] only",
            "probe_set_md5": {p: md5(p) for p in PROBE if Path(p).exists()},
        },
        "rows": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pub, indent=2), encoding="utf-8")

    # LEAK GUARD: no raw topic text may appear anywhere in the public artifact.
    blob = OUT.read_text(encoding="utf-8")
    leaked = [t for t in (row.get("topic", "") for row in r.get("rows", []))
              if t and t in blob]
    if leaked:
        print("LEAK GUARD FAILED: topic text present in public report:")
        for t in leaked:
            print("  -", t)
        sys.exit(3)

    print("PUBLIC report ->", OUT)
    print("probe_set_md5:", json.dumps(pub["_meta"]["probe_set_md5"], indent=2))
    print("aggregate:", json.dumps(
        {k: pub[k] for k in ("rate_f_blind", "fa_live_blind", "gate_bar", "GATE")}))
    print("leak guard: PASS (no topic text in public artifact)")


if __name__ == "__main__":
    main()
