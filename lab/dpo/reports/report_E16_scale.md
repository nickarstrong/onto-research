# report_E16_scale.md - E16 verifier scale-confirm

Session: pack v50, TYPE C (scale-confirm). Date: 2026-06-09.
Verdict: **NO-GO (PARTIAL CONFIRM).** Discipline bars scale; gold-recall bar is
stub-retriever-bound and not fairly measurable in this configuration. RFT (gate 2)
stays LOCKED. Re-run reproduced the pre-ship instrument self-test exactly (R7 trail intact).

## 1. Setup

Real retrieval slice (replaces the 6-record v49 stub): 60 authorized records + 1
adversarial hash-fail decoy = 61 total. Source: ONTO-GOLD bibliography of record
(MASTER_SOURCES.json + onto_references.bib + literature/BIBLIOGRAPHY.bib + BIBLIOGRAPHY.md),
deduplicated by DOI, key_claim-enriched. All locators are real DOIs drawn from the GOLD
store of record; the store is the authorization set by definition (its DOI quality versus
Crossref is a separate GOLD-audit task, not the verifier's job). Schema unchanged
{manifest_files (sha256 over source), records [{claim_key, source, locator}]}. Decoy source
intentionally absent from manifest_files. Fixture and held-out are LOCAL-ONLY (eval/_local,
gitignored); only this report is public.

Held-out: grown from 25 to 80 items, balanced 16 per class across 5 classes, authored
adversarially and human-adjudicated. Classes: spoof_cuestripped_entitied (false claim plus
named institution/year, no formal locator), gold_backed (true claim resolving to a slice
record), negctrl_common (common knowledge, no source-bearing entity), spoof_cuestripped_bare
(false claim, bare, no entity), negctrl_attributed (attribution cue, no bindable locator).
The coverage-cap probe holds id ho_23 (a true claim whose source is absent from the slice)
and is excluded from the B2 denominator by the scorer.

Pre-registered bars (carried from v49 unchanged; hardcoded in verify_E16.py, not movable by
construction; rates not predicted before the run):
B1 spoof-demotion >= 0.90 | B2 gold-VERIFY >= 0.80 | B3 over-demotion <= 0.10.

## 2. Results

| Bar | Class | Rate | Bar | Outcome |
|-----|-------|------|-----|---------|
| B1 spoof-demotion | spoof_cuestripped_entitied | 16/16 = 1.000 | >= 0.90 | PASS |
| B2 gold-VERIFY | gold_backed minus ho_23 (n=15) | 11/15 = 0.733 | >= 0.80 | FAIL |
| B3 over-demotion | negctrl_common | 0/16 = 0.000 | <= 0.10 | PASS |

Verdict computed by the scorer: NO-GO (B2 below bar).

Disclosure metrics (outside the bars):
- bare-entity-free escape (spoof_cuestripped_bare): expected-high scope-wall escape; not
  extracted, not demoted. Confirms the documented scope wall (bindability disciplines
  PROVENANCE, not bare FACTUALITY).
- attributed-demote (negctrl_attributed): attribution cue without a bindable locator demotes.
  This is discipline, not over-demotion (consistent with the no-citation-needed scope of
  arXiv:2410.11217, which exempts only common knowledge).
- ho_23 coverage-cap: true-but-uncovered claim demotes identically to a fabrication. Correct
  R4 behaviour; tracked as coverage, not error; excluded from B2.

## 3. Root cause of the B2 miss: the stub retriever, not the verifier

The two discipline bars are perfect at scale (B1 1.000, B3 0.000) on 80 adversarial items
against a real 61-record slice. The verifier's load-bearing behaviour - demote unbindable
provenance, never touch common knowledge - scales without regression.

B2 is bottlenecked upstream of the verifier, in retrieval. gold_retrieve.retrieve() is a
token-overlap matcher that binds only when a claim shares all-but-one of a record's claim_key
tokens (intersection >= 2 and >= len(key_tokens) - 1). Its own docstring declares it a STUB
pending semantic retrieval, with an intentionally strict threshold. Faithful prose
restatements of a finding do not reliably echo a fixed token set: finding-vocabulary,
title-vocabulary, and key_claim-vocabulary diverge for the same paper (e.g. Koonin 2007 -
title "cosmological eternal inflation" versus finding "replicase probability 10^-1018";
Shannon 1948 - title "mathematical theory of communication" versus claim "information theory").

Four independent indexing strategies were tried for the slice claim_keys - raw keyword union,
inverse-document-frequency selection, title head-nouns, and key_claim core tokens. Gold-recall
clustered at 8 to 11 of 15 across all four, always below the 0.80 bar, while over-binding onto
spoofs, common knowledge, and attributed negatives stayed at zero throughout. Convergence below
the bar across four indexings, with discipline held at zero false binds, is the evidence that
the wall is the matcher (token overlap plus all-but-one threshold), not the indexing and not
the verifier. The v49 B2 of 4/4 passed only because n was 4 with hand-matched keys; at scale
the stub's brittleness to paraphrase surfaces.

A correct B2 at scale therefore requires the real semantic retriever (embedding cosine over
the slice), which is out of scope for this no-infrastructure session. No claim_key was tuned
toward the specific failing items, and the pre-registered bar was not moved (R7).

## 4. Ladder consequence

Scale-confirm is PARTIAL. The discipline half of the keystone (catch fabricated provenance,
preserve common knowledge) is confirmed at scale and on a real slice. The gold-recall half is
not measurable on the stub retriever. RFT (gate 2) stays LOCKED, with a precise reason: not
"the verifier fails" but "B2 is unmeasurable on the stub; a semantic retriever is a
prerequisite before B2 can gate RFT."

Note on RFT relevance: B2 governs RFT yield, not RFT safety. Low gold-recall would make the
verifier discard clean self-samples (inefficient selection); it would not admit fabricated
ones, because B1 demotion holds. This bounds the risk of the locked state but does not lift
the pre-registered gate.

Next: swap gold_retrieve.retrieve() for a semantic retriever (embedding cosine; is_authorized
hash-gate unchanged; interface hits=[{source, locator, hash}] preserved), re-pre-register the
same bars, re-run the same held-out. Semantic B2 >= 0.80 -> GO -> RFT unlocks. Semantic B2 still
< 0.80 -> a real verifier-recall limit on this substrate -> bank as a scale-limited negative per
the keystone's destination-falsifiability. The fix is the retriever, never loosening Gate-B or
the bar.

## 5. R7 / provenance trail

- Bars pre-registered (hardcoded), not predicted, not moved after the run.
- Pre-ship instrument self-test (11/15) reproduced the official run (11/15) exactly; no
  post-hoc adjustment.
- Held-out authored adversarially, class labels human-adjudicated before the run; labels locked.
- gold_backed claims map only to authors present in the slice; ho_23 (Watson and Crick 1953)
  verified absent from the slice before use as the coverage-cap probe.
- Privacy: slice + held-out + extracted claims remain LOCAL-ONLY; this report is the sole
  public artifact. verify_E16.py was not modified this session.
