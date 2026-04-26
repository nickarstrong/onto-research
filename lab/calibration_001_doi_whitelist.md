# CALIBRATION #001 · DOI Whitelist · R4 False Positive Fix

**Date:** 2026-04-26
**Discovered in:** baseline_001 · §4 F6
**Affected component:** `scoring_engine_v5_1.py` · R4 (Sources)
**Severity:** Medium · scoring engine accepts fabricated citations as evidence
**Status:** open

---

## 1 · The exploit

Mistral-7B-Q4 generated this string in its GOLD response:

```
A prospective cohort study of coffee consumption and mortality among Chinese adults.
W. Sun, A. Ying, L. Yan, et al., Nutrition Journal, vol. 10, iss. 1,
<https://doi.org/10.2187/ngj.5309>
```

Scoring engine awarded R4 = 30% on the basis of:
- DOI-shape pattern match: `10.\d{4,9}/\S+` ✓
- "et al." token present ✓
- Year present elsewhere in response ✓

**Reality:** DOI prefix `10.2187` does not exist in the CrossRef Public Resolver registry. There is no journal `ngj.5309`. The entire citation is fabricated by Mistral · the format is real-shaped, the content is hallucination.

R4 should have been ≤ 0.05 (no verifiable source). Current engine cannot distinguish real DOI prefix from invented one.

---

## 2 · Why this is bad

R4 is a **trust signal** in the scoring protocol. The whole point of R4 is to separate "model cited a real paper" from "model wrote citation-shaped noise". If the regex accepts noise, R4 becomes performative · the discipline measurement degrades to a typography check.

Worse: **any model can be fine-tuned to gaming this.** A bad-actor provider could train a model to always emit DOI-shape strings, score high on ONTO without supplying truth. This is a moat-leak.

---

## 3 · Fix proposals

### Option A · Static prefix whitelist (cheap)

Maintain a list of registered DOI prefixes (~10K entries from CrossRef):
```
10.1000-10.9999  (legacy CrossRef)
10.1001/...      (JAMA)
10.1002/...      (Wiley)
10.1016/...      (Elsevier)
10.1056/...      (NEJM)
10.1126/...      (Science)
10.1038/...      (Nature)
10.1093/...      (Oxford UP)
10.3389/...      (Frontiers)
10.7150/...      (Ivyspring)
... (~10K)
```

Scoring engine checks DOI prefix against whitelist. Match = R4 contribution. Miss = R4 contribution × 0.1 (severe penalty for fabricated prefix).

**Cost:** ~5 hours implementation · whitelist file ~200KB shipped with engine · zero network call · runtime impact negligible.

**Coverage:** static · misses new publishers (rare). Solution: quarterly whitelist refresh from CrossRef API dump.

### Option B · Live CrossRef resolver lookup (heavy)

For each DOI in response, hit `https://api.crossref.org/works/{doi}` and check 200 vs 404.

**Cost:** 50-200ms per DOI · network dependency · rate-limit risk · privacy implication (publisher sees what's being cited).

**Coverage:** perfect.

### Option C · Hybrid (recommended)

Static whitelist + optional CrossRef resolution flag · default static, regulator/audit mode triggers live verification.

---

## 4 · Decision

Implement **Option A · static prefix whitelist** as next calibration release.

Reason: zero-network-dependency aligns with ONTO architecture (engine is deterministic, signs proof, no external lookups). Privacy-preserving. ~99% of fabricated DOIs use either bogus prefix (Mistral-style) or recycled real prefix with random suffix — second case still detectable via CrossRef-resolution mode if needed later.

---

## 5 · Spec

```
1. Add file:    backend/scoring/doi_whitelist.txt
                (one DOI prefix per line, format: 10.NNNN)
                Source: CrossRef "owner_prefixes" public dump
                Refresh cadence: quarterly

2. In scoring_engine_v5_1.py · _score_r4():
   - For each DOI matched:
     prefix = re.match(r"10\.\d+", doi).group(0)
     if prefix in whitelist:
       weight = 2.5  (current value)
     else:
       weight = 0.25  (10x penalty for fabricated prefix)

3. Log to factors:
   r4_factor["doi_verified_count"] = N_match_whitelist
   r4_factor["doi_unverified_count"] = N_miss_whitelist
   r4_factor["fabrication_suspected"] = doi_unverified_count > 0
```

---

## 6 · Acceptance test

**Regression:** baseline_001 must replay with the new engine.

```
Mistral-7B GOLD response (rerun) → R4 ≤ 0.05  (was 0.30)
Mistral-7B GOLD Grade: D 4.7 → expected E 4.0-4.2
Qwen-7B GOLD response (no fake DOI) → R4 unchanged at 0.50
Qwen-14B GOLD response (real et al. citations) → R4 unchanged
```

**Negative test:** craft a synthetic response with `10.99999/fake` — R4 must score ≤ 0.05.

**Positive test:** craft a synthetic response with `10.1056/NEJMoa2034577` (real NEJM DOI) — R4 must score ≥ 0.30.

---

## 7 · Risk register

- **R7.1** · Whitelist becomes stale, real new publisher rejected. Mitigation: quarterly refresh + grace cap (unknown prefix scores 0.5× instead of 0.1× for first 90 days).
- **R7.2** · Bad actor uses real prefix with fake suffix (e.g. `10.1056/NEJMfake999`). Whitelist alone won't catch. Mitigation: deferred to Option C live resolution.
- **R7.3** · Whitelist itself becomes a moat-leak (publishes ONTO's exact list). Mitigation: list is public CrossRef data, no proprietary value in the list itself.

---

## 8 · Owner & ETA

Owner: Tommy (Lead Engineer)
Estimated effort: 1 working session
Ship target: before E3 (domain coverage) runs · so that E3 baselines are clean

---

*This document closes one open exploit found during baseline_001 (rev 2). When fix lands, baseline must be rerun on Mistral-7B and the new score recorded as `baseline_001_rev3.md`.*
