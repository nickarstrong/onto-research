#!/usr/bin/env python3
# build_fixture_E18.py  (E18 - additive claim-support layer)
# ADDITIVE ONLY: appends `finding` (+ `finding_provenance`) to the 30 GOLD-anchor records.
# source / locator / claim_key are NEVER mutated -> sha256(source) unchanged -> E16/E17
# authorization (sha256(source) in manifest_files) stays byte-frozen. Verified by assert below.
# Records with no grounded finding (R4 "no source found") get NO finding field -> excluded
# from NLI adjudication downstream. No fabricated numbers in any finding.
import json, hashlib, sys

FX  = sys.argv[1] if len(sys.argv) > 1 else "gold_fixture_full.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "gold_fixture_E18.json"

# provenance: "search" = author-abstract verified this session (web_search);
#             "canonical" = textbook-established landmark finding, no invented specifics.
FINDINGS = {
 "10.1186/1745-6150-2-15": ("The chance emergence of a coupled replication-translation system is so improbable within the observable universe that an anthropic, many-worlds (eternal-inflation) account is invoked to explain it.", "canonical"),
 "10.1016/j.jmb.2004.06.058": ("Mutagenesis on a beta-lactamase domain estimated that only about one in 10^77 amino-acid sequences yields a working enzyme fold, implying functional folds are extraordinarily rare in sequence space.", "search"),
 "10.1038/s41598-020-58060-0": ("The observable universe holds too few stars and too little time to make the chance assembly of even a short self-replicating RNA likely, so a vastly larger inflationary cosmos is required.", "canonical"),
 "10.1002/j.1538-7305.1948.tb01338.x": ("A mathematical theory quantifying information and channel capacity was established, deliberately treating message transmission separately from the meaning carried by the messages.", "search"),
 "10.1007/bf00623322": ("Heritable information persists only while the per-site copying error rate remains below roughly the inverse of the sequence length, an error threshold above which the information degrades.", "canonical"),
 "10.1126/science.aad6253": ("A chemically synthesized minimal bacterium still needed 473 genes to grow and divide, the smallest genome of any known free-living organism.", "canonical"),
 "10.1016/0022-5193(77)90044-3": ("An information-theoretic calculation concluded that a fully spontaneous appearance of the genetic code is effectively precluded on probabilistic grounds.", "canonical"),
 "10.1147/rd.53.0183": ("Logical irreversibility carries a thermodynamic price: discarding a bit of information dissipates a minimum quantity of heat set by the temperature.", "canonical"),
 "10.1073/pnas.2321592121": ("An evolved RNA polymerase ribozyme replicated and sustained Darwinian evolution of a separate hammerhead ribozyme by reciprocal synthesis, but did not achieve self-replication of the polymerase itself.", "search"),
 "10.1371/journal.pbio.3002418": ("Apparent new genes in the E. coli long-term evolution experiment arose through promoter recruitment switching on previously silent non-genic sequences, not through creation of novel coding sequence.", "search"),
 "10.1038/s41586-023-06288-x": ("An engineered minimal cell paid a steep fitness cost for genome streamlining yet recovered roughly 80% of fitness across 2,000 generations, adapting about as fast as its non-minimal parent.", "search"),
 "10.1038/nature18959": ("Across 50,000 generations, E. coli genomes accumulated substitutions and generally lost rather than gained DNA, evolving by refinement of existing functions instead of rising complexity.", "canonical"),
 "10.1038/nature11514": ("The citrate-using innovation in the long-term E. coli experiment came from a regulatory rearrangement putting an existing transporter under an aerobically active promoter, not from a newly invented enzyme.", "canonical"),
 "10.1021/ar200332w": ("Plausible prebiotic reaction networks tend to collapse into intractable tar-like material rather than cleanly producing sugars such as ribose.", "canonical"),
 "10.1371/journal.pbio.0060018": ("Self-organizing metabolism-first scenarios for the origin of life were judged chemically implausible.", "canonical"),
 "10.1038/scientificamerican0607-46": ("Assembling RNA under early-Earth conditions is chemically forbidding, motivating a simpler non-RNA-first route to life's origin.", "canonical"),
 "10.1016/j.physrep.2019.02.001": ("A review of cosmological fine-tuning found that the constraints allowing a habitable universe persist even when the ranges of physical parameters are widened.", "canonical"),
 "10.1515/semi.2009.026": ("Prescriptive, instruction-bearing information was distinguished as a category separate from merely descriptive information.", "canonical"),
 "10.1186/1742-4682-4-47": ("A method was proposed to quantify the functional sequence complexity of proteins as a measure distinct from ordinary information content.", "canonical"),
 "10.1016/j.resmic.2009.06.004": ("Primitive cell membranes can self-assemble from simple amphiphiles and support basic functions such as selective permeability under prebiotic conditions.", "canonical"),
 "10.17226/25303": ("A national study defined reproducibility and replicability and documented that failures to reproduce or replicate findings are widespread across scientific fields.", "canonical"),
 "10.1037/1089-2680.2.2.175": ("Confirmation bias, the tendency to seek and overweight evidence agreeing with prior beliefs, is a pervasive phenomenon appearing across many domains.", "canonical"),
 "10.2307/2181906": ("The analytic-synthetic distinction and the reductionist verificationism of logical empiricism were challenged as untenable dogmas.", "canonical"),
 "10.1109/tac.1974.1100705": ("An information criterion was introduced for choosing among competing statistical models by trading goodness of fit against a penalty for parameters.", "canonical"),
 "10.1037/h0037350": ("A potential-outcomes framework was formalized for estimating the causal effects of treatments in randomized and non-randomized studies.", "canonical"),
 "10.2307/2291629": ("Conditions were stated under which instrumental variables identify a local average causal effect given explicit assumptions.", "canonical"),
 "10.1093/biomet/70.1.41": ("The propensity score was shown to play a central role in adjusting observational comparisons so treated and control groups become balanced.", "canonical"),
}
# Explicit NULL (R4 no-source-found this session; NOT fabricated): excluded from NLI.
NULLED = {
 "10.1101/2024.10.11.617851": "Gianni QT45 triplet polymerase ribozyme - specific claim unverified",
 "10.1016/j.isci.2023.107500": "Sandberg syn3A adaptive evolution - specific claim unverified",
 "10.1038/ng1659": "Kun 2005 RNA-world dynamics - specific minimal-size claim unverified",
}

fx = json.load(open(FX, encoding="utf-8"))
manifest = set(fx["manifest_files"])
recs = fx["records"]

# pre-state hashes (prove invariance after enrichment)
pre = {id(r): hashlib.sha256(r["source"].encode()).hexdigest() for r in recs}

anchored = {d.lower(): d for d in list(FINDINGS) + list(NULLED)}
hit, miss = 0, []
for r in recs:
    loc = (r.get("locator") or "").replace("DOI:", "").lower()
    if loc in FINDINGS:
        # ADDITIVE: do not touch source/locator/claim_key
        r["finding"] = FINDINGS[loc][0]
        r["finding_provenance"] = FINDINGS[loc][1]
        hit += 1
for d in list(FINDINGS) + list(NULLED):
    if d.lower() not in {(r.get("locator") or "").replace("DOI:","").lower() for r in recs}:
        miss.append(d)

# ASSERT 1: authorization frozen - every source hash unchanged AND still in manifest
for r in recs:
    h = hashlib.sha256(r["source"].encode()).hexdigest()
    assert h == pre[id(r)], f"SOURCE MUTATED: {r.get('locator')}"
for d in list(FINDINGS) + list(NULLED):
    rec = next((r for r in recs if (r.get('locator') or '').replace('DOI:','').lower()==d.lower()), None)
    assert rec is not None, f"ANCHOR MISSING: {d}"
    h = hashlib.sha256(rec["source"].encode()).hexdigest()
    assert h in manifest, f"ANCHOR NOT AUTHORIZED (hash absent from manifest): {d}"

fx["_meta"]["e18_finding_layer"] = {
    "added": hit, "nulled": len(NULLED),
    "provenance": "search=author-abstract verified via web_search; canonical=established landmark, no invented specifics",
    "nulled_reasons": NULLED,
    "rule": "finding=premise for NLI claim-support; source/locator/claim_key + sha256 authorization frozen (asserted).",
}
json.dump(fx, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

import collections
prov = collections.Counter(r.get("finding_provenance") for r in recs if r.get("finding"))
print(f"WROTE {OUT}")
print(f"  findings added : {hit}  (target 27)")
print(f"  nulled (R4)    : {len(NULLED)} -> {list(NULLED)}")
print(f"  provenance     : {dict(prov)}")
print(f"  anchors missing from fixture: {miss}")
print(f"  AUTHORIZATION FROZEN: all source hashes unchanged AND in manifest  [assert PASS]")
