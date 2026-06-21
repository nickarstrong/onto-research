# SPEC -- L5 PART I truth-set EXTENSION (b)  [authoring contract, Founder-authored]

Status   : authoring contract. Hands the exact extension for eval/_local/truth_input.txt.
Frozen   : predicate (SPEC_L5_independence_predicate.md, md5 d83d7a71) NOT touched ; validator
           (run_L5_partI_validate.py, md5 4eb2b874) NOT touched ; the existing 8 blocks C001-C008
           NOT re-authored ; the 3 verified coupled pairs (Thennavan/Taube ; Sattar/LEADER ;
           Parker/Thennavan) NOT re-sourced. This is TRUTH-SET work, EXTEND-only.
Source   : the (v) static trace -- P3 no-DAS fail-close makes the current set a constant-"coupled"
           classifier (DAS coverage 3/19 ; 14/15 pairs fail-closed). Over-prune is unmeasurable
           (0/11 independents carry an accession) and P1/P2/P4 recovery is a P3 masquerade.
R7       : labels are Founder-judged ground-truth. DOIs Crossref-resolvable. Accessions are the REAL
           DAS id you read in the paper. NEVER invent a DOI or an accession to clear a bar.

================================================================================
## 0  WHY THE CURRENT SET CANNOT MEASURE THE PREDICATE (the thing this fixes)

Frozen per-pair logic (run_L5_partI_validate.pair_predict), coupled iff ANY of:
  P1  author-set intersection non-empty
  P2  affiliation-of-record intersection non-empty
  P3  di is None OR dj is None  -> "fail_closed" -> coupled   (the trap)
      di == dj (both present)   -> coupled                    (genuine shared data)
  P4  one DOI in the other's reference list (Crossref + OpenCitations)

Consequence on the current set:
  - all 11 independent pairs have data_id '-' on BOTH sources -> P3 fail_closed -> coupled.
    over_prune = 11/11 = 1.0. The independent class cannot exercise a clean negative.
  - the 4 coupled pairs (author/institution/data/citation) ALSO mostly lack accessions -> P3
    fail-closes them too -> their "coupled" verdict proves P3 fired, NOT that P1/P2/P4 fired.
    recall 1.0 on those classes is CONTAMINATED (only C006 di==dj is a genuine leg).

So every leg except the C006 data leg is UNMEASURED. The fix is not in the predicate (that is a
separate, later session); it is in the truth-set: add pairs where P3 is SILENT, so the leg under
test is the ONLY thing that can couple (or, for independents, the ONLY thing that can fail).

P3 is SILENT on a pair iff BOTH sources carry a data_id AND the two are DISTINCT
(di is not None, dj is not None, di != dj). That is the single structural lever this whole
extension turns.

================================================================================
## 1  WHAT EACH NEW PAIR MUST LOOK LIKE (leg isolation table)

Legend: FIRE = this leg must be true on the pair ; CLEAN = this leg must be false.
"DAS" column = the data_id you write per source.

| class        | P1 author | P2 affil | P3 data            | P4 cite | new pairs to add |
|--------------|-----------|----------|--------------------|---------|------------------|
| independent  | CLEAN     | CLEAN    | present + DISTINCT | CLEAN   | >= 9  (to reach total >= 20) |
| author       | FIRE      | CLEAN    | present + DISTINCT | CLEAN   | >= 4  (to reach total >= 5)  |
| institution  | CLEAN     | FIRE     | present + DISTINCT | CLEAN   | >= 4  (to reach total >= 5)  |
| data         | CLEAN     | CLEAN    | SAME accession     | CLEAN   | >= 4  (to reach total >= 5)  |
| citation     | CLEAN     | CLEAN    | present + DISTINCT | FIRE    | >= 4  (to reach total >= 5)  |

Reading the table:
- independent : the discriminating negative. Both papers have a real accession but DIFFERENT ones,
  distinct authors, distinct institutions, neither cites the other. The frozen predicate ALREADY
  calls these "independent" correctly -> they isolate P3 fail-close as the sole over-prune cause
  (constructive confirmation of (v)) and become the population the later predicate-fix must keep clean.
- author : same author across two papers, each with its OWN dataset (distinct accession) so P3 is
  silent and the ONLY coupler is P1. distinct institutions, no citation edge.
- institution : shared affiliation-of-record, DISTINCT author teams (fixes the C008 Perou caveat
  where P2 was not isolated from P1), each with its own dataset, no citation edge. cooperative-group
  -of-record or core-facility pairs are the clean source here.
- data : the genuine P3. SAME primary accession on both (di == dj), distinct authors, distinct
  institutions, no citation edge -> coupling is data-only.
- citation : one paper establishes its support for C by CITING the other (meta cites the RCT it
  pools, or a re-analysis cites the primary). distinct authors, distinct institutions, and BOTH
  carry distinct accessions so P3 does not mask P4. This pair also feeds the HARD discount_leak==0 bar.

CAUTION on citation: if the citing paper (often a meta-analysis) has NO DAS, leave data_id '-' is
WRONG here -- it re-introduces P3 fail-close and the pair stops isolating P4. Pick citation
exemplars where BOTH sides carry an accession (e.g. a re-analysis that cites a primary, both with
their own deposited data), or pair a primary-with-accession that cites another primary-with-accession.
If no such pair is findable, state it (R2) and the citation leg stays leak-tested only, not P4-isolated.

================================================================================
## 1a  SOURCING WORKFLOW (Claude sources candidate MD / Founder final-validates)

Division of labour (decided 2026-06-14 (w)):
  CLAUDE sources. Per node/theme, Claude web_search + web_fetch real papers, pulls the REAL DAS
  accession with the exact quote, and emits a candidate MD: one block per pair with
  {claim, DOI, accession, PROPOSED label, source-quote for the accession}. Every DOI and accession
  is FETCHED LIVE with a quote -- NEVER from memory (R7 cardinal: invented DOI/accession = fabrication).
  FOUNDER final-validates. Founder is the final gate: confirms each accession against the quote /
  primary source, sets-or-confirms the coupling label, and only what survives enters truth_input.txt.

Verification layers (what actually checks each field -- NOT an AI quorum):
  - DOI       : the validator fetches Crossref LIVE at --run. A wrong DOI fails there.
  - accession : the validator does NOT check it -> Founder confirms it against the paper's DAS
                (Claude supplies the exact quote so the check is seconds, not a re-search).
  - label     : Founder judgement. The set grades the conscience predicate itself, so the ground
                truth must be human + primary-source independent of Claude (oracle independence, R7).
Other AIs (R7 / 3.9): allowed ONLY as extra eyes on framing / "did we miss a coupling" -- their
  output is a LEAD to verify, NEVER a fact. LLMs emit confident FAKE DOIs/accessions (the failure
  this whole L5 plane exists to fix). Nothing from an AI enters the set without Founder confirming it
  against Crossref / the real paper. A quorum of models is false confidence, not verification.

Scale note (R1): a full set is ~20 independent + ~5x4 coupled pairs, each LIVE-fetched -> this is a
  dedicated sourcing session with a real fetch budget, and may span sessions. GOLD-node anchoring
  (sec 1a-independent) needs the relevant GOLD module pulled in that session (full core not loaded
  by default). The claim text is label-only (the predicate never reads it), so node-anchoring is for
  provenance/priority, not a mechanical requirement.



File   : eval/_local/truth_input.txt  (LOCAL-ONLY, gitignored, never public -- held-out).
Action : APPEND new CLAIM blocks below C008. Do NOT edit/move/re-order C001-C008.
Guard  : before editing, copy a .bak (per the (s) incident -- _local has no git undo):
           Copy-Item eval\_local\truth_input.txt eval\_local\truth_input.txt.bak.<date> -Force
Ids    : new claim ids start at C009 and run up, unique, no collision with C001-C008.

Block format (build_l5_truth.py parser ; lines starting with # are comments):
  CLAIM <claim_id> <free text of the claim the sources back>
  SRC   <sid> <doi> <data_id|-> <method|->
  PAIR  <sidA> <sidB> <independent|author|institution|data|citation>

Field rules:
  - <doi>     : real, Crossref-resolvable. The validator fetches authors/affils/refs LIVE at --run;
                a wrong DOI fails there (self-verifying).
  - <data_id> : the REAL accession you read in the paper's data-availability statement
                (GEO GSExxxxx, PRIDE PXDxxxxxx, dbGaP phsxxxxxx, SRA SRPxxxxxx, ArrayExpress
                E-MTAB-xxxx, PDB id, TCGA-xxx, etc). Use '-' ONLY where the real paper truly has no
                DAS -- and for THIS extension a '-' defeats the purpose on every class except none,
                so the new pairs should carry real accessions (distinct, except the data class which
                is SAME). Do not invent an id (R7).
  - <method>  : modality tag or '-'. ADVISORY only, never gates. Optional.
  - every claim needs >= 2 sources ; EVERY C(n,2) pair must get a PAIR line (the build + --contents
    guard rejects a missing or extra pair).

Efficient shapes:
  - coupled classes (author/institution/data/citation): use 2-source claims = 1 clean pair each.
    Avoid 3+ sources in a coupled claim (it forces mixed-class C(n,2) you then must label).
  - independent class: a 3-source claim where all three are mutually clean + each carries a distinct
    accession yields 3 independent pairs from one block -- the cheapest way to reach >= 20.

Worked format templates (placeholders <...> -- fill with REAL values, do not copy literally):

  # ---- independent (accession-bearing, distinct) : isolates P3 fail-close ----
  CLAIM C009 <claim two genuinely separate datasets both support>
  SRC S1 <DOI_A> <ACCESSION_A> <method_a>
  SRC S2 <DOI_B> <ACCESSION_B> <method_b>
  PAIR S1 S2 independent

INDEPENDENT SOURCING METHOD (recommended, GOLD-node-anchored):
  take a GOLD Core node as the claim text, then web-find 2+ sources that INDEPENDENTLY support it,
  each a real DATA-GENERATING paper with its own DEPOSITED accession. Constraints that make it a
  valid accession-bearing independent pair: distinct accessions, distinct authors, distinct
  institutions, no citation edge between them.
  Do NOT reuse GOLD's own L3_sources here -- they are theory/calc/review with no DAS (that is why
  the existing 11 independents are accession-less). The node supplies the CLAIM ; the corroborators
  are fresh data-papers you source. The predicate never reads the claim text (it scores the source
  pair's Crossref metadata + the truth-set accessions), so GOLD-node anchoring is for provenance and
  priority, not a shortcut -- you still read one DAS line per source. This is the bulk of the
  extension (the >= 9 new independents). The 4 coupled classes are NOT sourceable this way (they
  need genuinely COUPLED pairs, the opposite of independent corroboration -> real coupled literature,
  type C006-C008).

  # ---- author (shared author, own datasets) : isolates P1 ----
  CLAIM C0NN <claim>
  SRC S1 <DOI_A> <ACCESSION_A> -
  SRC S2 <DOI_B> <ACCESSION_B> -
  PAIR S1 S2 author

  # ---- institution (shared affiliation, distinct authors) : isolates P2 ----
  CLAIM C0NN <claim>
  SRC S1 <DOI_A> <ACCESSION_A> -
  SRC S2 <DOI_B> <ACCESSION_B> -
  PAIR S1 S2 institution

  # ---- data (same accession) : genuine P3 ----
  CLAIM C0NN <claim>
  SRC S1 <DOI_A> <SHARED_ACCESSION> -
  SRC S2 <DOI_B> <SHARED_ACCESSION> -
  PAIR S1 S2 data

  # ---- citation (one cites the other) : isolates P4 + feeds leak==0 ----
  CLAIM C0NN <claim>
  SRC S1 <DOI_CITING> <ACCESSION_A> -
  SRC S2 <DOI_CITED>  <ACCESSION_B> -
  PAIR S1 S2 citation

================================================================================
## 3  COUNTS (current -> target)

| class        | current pairs | add (min) | target |
|--------------|---------------|-----------|--------|
| independent  | 11            | >= 9      | >= 20  |
| author       | 1             | >= 4      | >= 5   |
| institution  | 1             | >= 4      | >= 5   |
| data         | 1             | >= 4      | >= 5   |
| citation     | 1             | >= 4      | >= 5   |

Of the >= 9 new independent pairs, ALL must be accession-bearing + distinct + P1/P2/P4-clean
(the discriminating sub-population). The 11 pre-existing accession-less independents stay; see sec 4.
Statistically the over-prune estimate on the FIXED predicate rests on the accession-bearing
sub-population -- aim for >= 12 new independents if the sources are findable (wider is firmer, R1).

================================================================================
## 4  WHAT THIS SET MEASURES, AND THE HONEST LIMIT (R2 / R7)

This extension does NOT make over_prune PASS on the CURRENT frozen predicate. The 11 pre-existing
accession-less independents fail-close by design -> they remain a TRUE falsifier of the predicate
(absence-of-DAS treated as coupling). That falsification is correct and stays on the record.

What the extension DOES:
  1. adds an accession-bearing independent sub-population the frozen predicate ALREADY classifies
     correctly -> proves P3 fail-close is the SOLE over-prune cause (turns the (v) trace into a
     measured result, not just a static argument).
  2. un-masks P1/P2/P4 recovery: with P3 silenced on the new author/institution/citation pairs,
     a "coupled" verdict there now proves the named leg fired, not P3.
  3. becomes the FROZEN substrate the predicate-fix (separate, later session) is gated against:
     the fix ("require a positive coupling signal instead of fail-closing absent DAS") must
     (i) drop over-prune to <= 0.10 on BOTH independent sub-populations AND (ii) hold coupled
     recovery >= 0.85 AND discount_leak == 0. None of that is gateable on the current set.

================================================================================
## 5  POST-AUTHORING LADDER (one step per message ; net pre-check before --run)

cwd = C:\Projects\onto-research\lab\dpo

1. build      : python build_l5_truth.py
                expect: RESULT: READY ; Coupling-type counts independent>=20, author/institution/
                data/citation each >=5 ; no MISSING TYPES ; no PROBLEMS.
2. contents   : python run_L5_partI_validate.py --contents eval/_local/l5_coupling_truth.jsonl
                expect: empty classes [] ; problems none.
3. net pre-check (before any live run): confirm Crossref reachable and ONE new DOI resolves
                (Invoke-RestMethod on https://api.crossref.org/works/<one new DOI>, expect author list).
4. run        : python run_L5_partI_validate.py --run eval/_local/l5_coupling_truth.jsonl --out reports/report_L5_partI.md
                read: per_class_recall (author/institution/data/citation each should now reflect the
                REAL leg) ; over_prune split intent (sec 6) ; confusion ; discount_leak == 0 (HARD).
(--selftest is frozen-PASS ; re-run optional, not gating.)

Privacy : truth_input.txt + l5_coupling_truth.jsonl + report_L5_partI.md = LOCAL-ONLY, never public
          git (held-out -> future pretrains would eat it). Only harness + specs are public.

================================================================================
## 6  ADJACENT, NOT THIS SESSION (R12 flag)

The validator emits ONE aggregate over_prune over the whole independent class. To read the
accession-bearing vs accession-less independents separately -- and to gate the predicate-fix on
"over_prune == 0 on the accession-bearing sub-population" -- a READ-ONLY readout that groups
independents by (both data_id present) is needed. That is a small infra addition to the report
emitter, NOT a predicate or validator-logic change, and it belongs in a SEPARATE session (the
harness stays frozen while the truth-set is authored). Flagged here so it is not lost; do not
build it now.

================================================================================
## 7  COMPLETION CRITERIA (authoring stage DONE when ALL hold)

[ ] C001-C008 byte-unchanged ; 3 verified coupled pairs not re-sourced.
[ ] new claims C009+ appended ; .bak of truth_input.txt taken before edit.
[ ] independent total >= 20 ; author/institution/data/citation each >= 5.
[ ] every NEW independent pair: both data_id present + DISTINCT, P1/P2/P4-clean.
[ ] every NEW author/institution/citation pair: both data_id present + DISTINCT (P3 silent),
    only the named leg fires.
[ ] every NEW data pair: SAME accession on both, P1/P2/P4-clean.
[ ] every DOI Crossref-resolvable ; every accession real (R7) ; labels Founder-judged.
[ ] build_l5_truth.py -> READY ; --contents -> empty [] / problems none.
