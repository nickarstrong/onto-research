#!/usr/bin/env python3
# -*- coding: ascii -*-
"""g2_report_md.py -- emit a PUBLIC .md priority report from the redacted G2 json.

.md is NOT caught by .gitignore (lab/dpo/eval/*.json is). Carries datable
provenance + aggregate + per-row verdicts + probe-set md5. NO topic text.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("eval/G2_doi_blind_E6.json")
OUT = Path("reports/G2_doi_blind_E6.md")


def main():
    r = json.loads(SRC.read_text(encoding="utf-8"))
    md5 = r.get("_meta", {}).get("probe_set_md5", {})

    L = []
    L.append("# G2 -- DOI blind probe (Step-6 apparatus)")
    L.append("")
    L.append("- date: %s" % datetime.now(timezone.utc).date().isoformat())
    L.append("- model (frozen substrate): `%s`" % r.get("model"))
    L.append("- scope: %s (3-DOI-scope; verifier resolves DOI only)" % r.get("scope"))
    L.append("- k: %s  n_topics: %s" % (r.get("k"), r.get("n_topics")))
    L.append("")
    L.append("## Result")
    L.append("")
    L.append("- **GATE: %s** (bar rate_f >= %s)" % (r.get("GATE"), r.get("gate_bar")))
    L.append("- rate_f_blind = **%s**" % r.get("rate_f_blind"))
    L.append("- fa_live_blind = %s (invariant: 0.0)" % r.get("fa_live_blind"))
    L.append("- decision: %s" % r.get("decision"))
    L.append("")
    L.append("## Per-row (topics redacted; held-out, sec 3.2)")
    L.append("")
    L.append("| idx | family | verdict | topic_sha256 |")
    L.append("|-----|--------|---------|--------------|")
    for row in r.get("rows", []):
        L.append("| %s | %s | %s | `%s` |" % (
            row.get("idx"), row.get("family"), row.get("verdict"),
            row.get("topic_sha256")))
    L.append("")
    L.append("## Probe-set provenance (dated priority; set itself is private)")
    L.append("")
    for k, v in md5.items():
        L.append("- `%s` md5: `%s`" % (k, v))
    L.append("")
    L.append("> Probe-set (held-out bait) is private (sec 3.2). It was previously")
    L.append("> committed to public history in error and removed via history rewrite")
    L.append("> (force-push, origin/main 43b1104 -> 8b20461). The v231 set is therefore")
    L.append("> CONTAMINATED for any FUTURE substrate swap and must be replaced with a")
    L.append("> fresh held-out there. The frozen substrate measured here predates the")
    L.append("> leak, so THIS measurement is clean.")
    L.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("wrote", OUT, "| rows:", len(r.get("rows", [])), "| GATE:", r.get("GATE"))


if __name__ == "__main__":
    main()
