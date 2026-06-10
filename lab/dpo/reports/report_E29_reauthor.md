# report_E29_reauthor -- S1 tail-driver re-author session (TYPE A, authoring)

- session    : v66 -> E29 (re-author the gold-content S1 contradiction-tail drivers + fresh fixture freeze)
- inputs     : gold_fixture_E25b.json md5 4a45f52883a802e8d8d1d5ff5d185bdb (E29 base, VERIFIED on disk)
               heldout_E17.jsonl     md5 7e9fe030646d5671952e7a9fe9437e37 (VERIFIED)
               report_E28.md (git 0101e7b) -- S1 tail (con,cos,id) for the 10 gold tail rows
- helper     : dump_E28_pairs.py (read-only retrieval replay; NO NLI, NO verdict, frozen substrate untouched)
               -> E28_pairs_gold.json md5 c9e09c520b37b5679a0c3e7780bca7bd (LOCAL; rows=88 from_finding=74
               from_source=14 = reproduces report_E28 S1 gold premise counts -> retrieval trust-gate PASS)
- VERDICT    : REVERSAL -- the S1 tail is NOT a premise-phrasing defect. It is a RETRIEVAL MISBINDING defect.
               0/8 re-authored ; 8/8 NULL-for-reauthor (R7). Fresh fixture = E25b byte-identical (0 edits).

## 0  why a dump was needed (pack STEP-0 gap, flagged)
report_E28 diag stored only (class, id, contradiction, cosine) per pair; the premise SOURCE/finding was
dropped. The S1 tail "id" is the held-out CLAIM id, not the bind-corpus premise. The probe binds by SEMANTIC
top-k retrieval, NOT by the claim's anchor DOI -- so the contradicting premise cannot be recovered from the
static findings/worksheet by locator. dump_E28_pairs.py replays candidates_with_cosine byte-identical and
emits (id, kind, source, finding, cos) per authorized candidate; each S1 tail row was mapped back to its
exact premise record by its unique binding-cosine fingerprint. All 10 rows resolved 1:1, all kind=finding.

## 1  driver isolation -- 8 distinct premise records (re-author targets)
Each premise below is FAITHFUL to its own cited source. It scores P(contradiction) >= 0.95 only because the
retriever surfaced it for a held-out claim about a DIFFERENT paper. The claim's own (entailing) anchor source
is also retrieved, but the veto fires on ANY authorized candidate (probe line 153) -> the near-topic wrong-
source candidate falsely vetoes the gold claim. Claims are described by source, not held-out verbatim.

| fix_idx | premise source (locator) | premise content (faithful) | bound to claim (id / true source) | NLI-contradiction cause | decision |
|---|---|---|---|---|---|
| 199 | Mushegian & Koonin, PNAS 1996 (DOI:10.1073/pnas.93.19.10268) | minimal gene set ~256 genes | ho_g05 (Hutchison 2016, 473 genes) ; ho_g10 (uz-Zaman 2024, proto-genes) | numeric disagreement 256 vs 473 between two real papers ; off-topic for proto-genes | NULL |
| 36 | Robertson & Joyce, CSH Perspect 2012 (DOI:10.1101/cshperspect.a003608) | RNA-first SUPPORTED (RNA as genome+catalyst) | ho_g17 (Shapiro 2007, RNA assembly = forbidding) | two real, opposing origin-of-life positions | NULL |
| 37 | Lenski, ISME J 2017 (DOI:10.1038/ismej.2017.69) | LTEE fitness rises, no plateau, mixed genome change | ho_g12 (Sandberg 2023 syn3A, genome shrank) ; ho_g10 (proto-genes) | different experiments/organisms | NULL |
| 11 | Moger-Reischer, Nature 2023 (DOI:10.1038/s41586-023-06288-x) | minimal cell recovers ~80% fitness over 2000 gens | ho_g05 (Hutchison, 473-gene count) | premise=fitness recovery vs claim=gene count; same topic, different fact | NULL |
| 197 | Horning & Joyce, PNAS 2016 (DOI:10.1073/pnas.1610103113) | riboPCR: exponential RNA amplification, "replication with RNA alone" | ho_g08 (Papastavrou 2024: never self-replicated) | two different ribozyme papers, opposing self-replication status | NULL |
| 59 | Open Science Collaboration, Science 2015 (DOI:10.1126/science.aac4716) | 36% of 100 psych replications significant | ho_g23 (NASEM 2019: cross-field definitions + gaps) | different papers; psychology-empirical vs cross-field-definitional scope | NULL |
| 181 | Price, Nature 1970 (DOI:10.1038/227520a0) | Price equation: evolutionary SELECTION + covariance | ho_g26 (Akaike 1974: AIC model SELECTION) | embedding collision on "selection"; topically unrelated | NULL |
| 195 | Joyce, Nature 2002 (DOI:10.1038/418214a) | RNA-world preceded DNA; RNA central to early life | ho_g13 (Tenaillon 2016: genome optimization) | unrelated topics (origins vs genome evolution) | NULL |

## 2  R7 decision -- why all 8 are NULL-for-reauthor, not re-authored
The E29 task assumed each tail premise NLI-contradicts the claim IT IS MEANT TO SUPPORT (a phrasing defect
fixable without changing the cited fact). The dump falsifies that assumption: every tail premise supports its
OWN source faithfully and contradicts a claim about ANOTHER source. Re-authoring any of them to stop
contradicting its bound claim would require falsifying a faithful finding -- e.g. make Mushegian-Koonin report
473 genes (their result is 256), or make Price's covariance equation be about an information criterion. That is
a direct R7 violation (invent/alter a fact to hit a contradiction target). Per the authoring gate, no faithful
re-author exists -> NULL-with-reason. Honest null > forced pass. No silent drop; all 8 logged above.

## 3  corrected binding constraint (reverses report_E28 conclusion)
report_E28 concluded "premise quality is the binding constraint -> E29 re-author." That is WRONG. The premises
are correct. The S1 gold contradiction tail is produced by the CANDIDATE SET + ANY-VETO rule:
- a gold claim retrieves its true (entailing) support AND a topically-near different-source record;
- the near-source faithfully contradicts the claim (256 vs 473; Price vs Akaike);
- veto = `any authorized candidate contradicts` -> the gold claim is falsely vetoed (false-accept).
Corroboration: report_E28 S1 expectation failed (gold tail cos_med 0.4855 < spoof 0.5112). Under the misbinding
reading this is expected -- gold's wrong-source neighbors sit slightly farther in cosine than the spoofs'
entity-matched neighbors -- which is also why E28's cosine gate K could not separate the tails (E28 PASS_KNIFE_
EDGE was real; the lever was just aimed at the wrong defect).

## 4  fresh fixture freeze
0 premises re-authored -> the E29 fixture is gold_fixture_E25b.json BYTE-IDENTICAL.
DEVIATION (R7/file-hygiene): no separate gold_fixture_E29.json is emitted -- a byte-identical duplicate under a
new name adds no information and risks a stale fork. The frozen base stands:
  E29 fixture == gold_fixture_E25b.json , md5 4a45f52883a802e8d8d1d5ff5d185bdb (UNCHANGED).
Spoof / negctrl / non-tail gold: unchanged by definition (nothing was edited). Diff proof = empty diff.

## 5  E30 redirect (supersedes pack v66 sec4 preview)
The pack's E30 ("re-run the frozen run_E28 probe on a re-authored fixture") is now POINTLESS: premises are
unchanged, so the tail would reproduce verbatim. Redirect E30 to a BINDING-DISCIPLINE probe instead:
  hypothesis  : the false-accept tail collapses if the veto considers only the claim's BOUND support
                (top-1 cosine candidate, or candidates whose binding passes a relevance/anchor test),
                instead of ANY authorized candidate.
  falsifier   : restrict veto to top-1 cosine candidate; if gold false-accept does NOT drop materially below
                0.0667 while spoof reject-share holds, the near-source veto is NOT the driver -> escalate.
  pre-register: new (frozen pre-data); NOT a frozen run_E28 re-run. Own gate fa<=0.10, B2>=0.90, S3>0.50.
  note        : run_E28_probe.py stays frozen; E30 is a new probe (different decision rule), not an edit.

## 6  authoring gate (E29) -- CLOSED
- [x] every driver re-authored-with-provenance OR explicitly nulled-with-reason : 8/8 NULL-for-reauthor (R7).
- [x] no silent drop, no target forced.
- [x] fresh fixture: spoof/negctrl/non-tail-gold byte-identical to E25b -> trivially true (0 edits); diff empty.
- [x] fixture md5 recorded : 4a45f52883a802e8d8d1d5ff5d185bdb (E25b, unchanged ; no new file by design).
- [x] report committed ; fixture not in git status (no new fixture file produced).
- helper dump_E28_pairs.py : commit ALONGSIDE this report (reproducibility -- it recovered the provenance the
  report cites). E28_pairs_gold.json is LOCAL/gitignored (held-out-derived).

## 7  load-bearing learning (carry to keystone, PENDING Tommy go)
- E28's "premise quality is the binding constraint" is CORRECTED: the S1 gold contradiction tail is a RETRIEVAL
  MISBINDING under an ANY-CANDIDATE veto, not a premise-phrasing defect. The 8 tail premises are each faithful
  to their own source; they contradict claims about DIFFERENT sources that the retriever co-surfaced.
- Diagnostic discipline: a "premise quality" verdict must be checked against the ACTUAL premise text per pair.
  report_E28 dropped per-pair premise identity; the verdict was inferred from aggregate distributions and was
  wrong about the mechanism. Always log (id -> bound source) when a per-pair causal claim will be made.
- The fix is upstream of phrasing AND of the cosine gate: constrain WHICH candidate may veto (E30).
