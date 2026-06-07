"""
ONTO Scoring Engine v5.1
========================
Measures DISCIPLINE, not facts.
R1-R7 scored 0.0-1.0. Composite = weighted average.
No external APIs. No LLM judge. Pure text analysis. Universal markers.

R1  Quantify         — numbers, CI, sample sizes, effect sizes
R2  Uncertainty      — hedging, gaps, knowledge boundaries
R3  Counter          — counterarguments, causal counter-markers, limitations
R4  Sources          — citations, DOIs, author-year, institutions
R5  Evidence Grade   — evidence hierarchy (RCT > cohort > opinion)
R6  Falsifiability   — testable predictions, falsification criteria
R7  No Fabrication   — cross-R consistency + intron cleanliness (R17/R18 embedded)

v5.1 (Session 9) — KERNEL-CANONICAL R17 (C1-C8) + APOPTOSIS:
  Aligns local numbering to Kernel v5.1 canonical C1-C8 and completes the
  proofreading layer. Adds C2 / C5 / C6 / C8. Renames legacy v5.0 locals.

    v5.0 local → v5.1 canonical (Kernel v5.1 layer_V_coherence.R17.constraints):
      C1  → C1   numbers_need_sources        (UNCHANGED)
      —   → C2   no_fabrication_needs_proof  (NEW: R7-claim patterns + R4<0.15)
      C3  → C3   certainty_needs_hierarchy   (UNCHANGED)
      C2  → C4   counterarguments_need_sources (RENAMED)
      —   → C5   grading_needs_specifics     (NEW: R5>0.5 + R4<0.15)
      —   → C6   falsifiability_implies_uncertainty (NEW: R6>0.5 + R2<0.1)
      C4  → C7   foundation_check            (RENAMED: "beautiful empty")
      C5  → C8   frameshift                  (UPGRADED: apoptosis flag, not penalty)

  [APOPTOSIS] C8 is not a penalty. When final R7 < 0.15 — i.e. the output
              has accumulated structural R17 violations past the recovery
              threshold — the engine sets apoptosis_triggered=True in the
              returned dict. app.py detects this flag and replaces the
              LLM response with a structured refusal (Genesis Protocol
              reference). Matches Kernel R11 doctrine: "refuse to operate
              with damaged DNA". The scoring engine does not rewrite the
              LLM output — it signals the runtime to refuse delivery.

  [R18 SPLICING] Intron detection remains a DIAGNOSTIC signal (not a
                 separate bar, not a separate penalty pass). intron_ratio
                 > 0.3 → +0.10 inside R7 cross_r_penalty. Generation-time
                 self-splicing (DNA-style intron removal before delivery)
                 is a KERNEL PROMPT DIRECTIVE (kernel.py Session 9-D),
                 not a scoring-engine transformation. ONTO measures,
                 doesn't rewrite.

  [BUGFIX R2] Removed `\\b95%\\s*CI\\b` → 1.5 from R2 hedging patterns. CI is
              already counted in R1 (quantification). Double-counting
              inflated both R1 and R2 on the same signal. Kept the
              `CI\\s*[:,]?\\s*\\d` variant which requires a following bound
              (genuine uncertainty-range expression).
  [BUGFIX R5] Removed `\\b(N[=-]\\d|n[=-]\\d|sample\\s+size)\\b` → 1.0 from R5
              patterns. Sample size alone is quantification (R1), not
              evidence hierarchy. R5 measures study-design grade (RCT
              vs cohort vs case series), not N.

v5.0 (Session 8) — ARCHITECTURE v2:
  [REMOVED] R8-R16 regex scoring. Category error — these are behavioral modules
            (how the model thinks), not text metrics. They live in GOLD Kernel
            prompt directives (Session 9), auditable by reading response content,
            not by independent regex metric. WP 12.3 Limitations states this
            explicitly: "regex measures form, not reasoning".
  [REMOVED] R11 Integrity patterns from v4.3 S7-T1. Integrity is security/identity
            behavior — proven by refusal to operate with damaged DNA, not by text
            markers. Moved to GOLD Kernel prompt territory.
  [KEPT] R3 causal counter-markers (spurious, reverse causation, instrumental
         variable) from S7-T1 — they are legit counterargument signals.
  [DOCTRINE] Four layers, each with role:
             Kernel    = spec source (immutable DNA R1-R18)
             Scoring   = thermometer (R1-R7 measured, R17-R18 embedded)
             GOLD      = prompt (R8-R16 behavioral directives + R17/R18 gen-time)
             UI        = presentation (7 bars + behavior toggles)
             When roles overlap, category error happens.

v4.3 (Session 7): R11 realigned to Integrity (reverted in v5.0).
v4.2 (Session 6): R4 epistemic gate, density ceiling ×2.
v4.1 (Session 6): R11 RU regex fix, R8/R15 patterns, presence-gated weights.

Replaces: scoring_engine_v5.py (v5.0 draft) → v5.1 (full R17 + apoptosis).
Compatible: same output shape + new fields `apoptosis_triggered`, `apoptosis_reason`.
"""

import re
import math
from typing import Optional, List, Dict, Tuple


# ================================================================
# R1: QUANTIFY — numbers with context, not vague claims
# ================================================================
# What we measure: model provides specific numbers, not "many studies show"
# Source: ONTO R1 — "Numbers, CI, sample sizes — not 'many studies show'"

R1_PATTERNS = [
    # Confidence intervals and statistical measures
    (r"\b\d{1,3}\.?\d*\s*%\s*CI\b", 2.0),                     # "95% CI"
    (r"\bCI\s*[:,]?\s*\d", 2.0),                                 # "CI: 0.79-0.88"
    (r"\b\d{1,3}\.?\d*\s*%\s*confidence\s+interval\b", 2.0),   # "95% confidence interval"
    # Effect sizes
    (r"\b(RR|HR|OR|NNT|NNH|ARI|ARR|RRR)\s*[=:]\s*\d", 2.0),   # "HR=0.80"
    (r"\b(RR|HR|OR)\s+\d+\.\d+", 2.0),                          # "RR 0.83"
    # Sample sizes
    (r"\b[Nn]\s*[=:]\s*[\d,]+", 1.5),                            # "N=17,604" or "n=340"
    (r"\b\d[\d,]+\s*(patients?|participants?|subjects?|people|individuals|respondents?)\b", 1.5),
    # Percentages with context (not just bare numbers)
    (r"\b\d{1,3}\.?\d*\s*%\s*(reduc|increas|improv|declin|drop|rise|change|lower|higher|more|less|of\s)", 1.0),
    # Probability/likelihood quantified
    (r"\b(probability|likelihood)\s*[=:<>]\s*\d", 1.5),
    (r"\b~?\d{1,3}\.?\d*\s*%\s*(likelihood|probability|chance)\b", 1.5),
    # Specific numeric claims (dose, duration, cost, measurement)
    (r"\b\d+\.?\d*\s*(mg|kg|ml|mcg|mmol|μg|IU)\b", 0.8),       # dosage
    (r"\b\d+\.?\d*\s*(year|month|week|day)s?\s+(follow|of\s+data|study)\b", 1.0),  # study duration
    (r"\bp\s*[<=]\s*0?\.\d+", 1.5),                              # p-value: "p<0.05"
    # Ranges
    (r"\b\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*%", 0.8),              # "15-20%"
    (r"\b\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*(mg|kg|ml)\b", 0.8),   # "300-400mg"
]

# Anti-patterns: bare numbers without context don't count
R1_ANTI = [
    r"\b\d{1,2}\s+(things?|tips?|ways?|reasons?|steps?|facts?)\b",  # listicle numbers
]


def score_r1(text: str, word_count: int) -> Tuple[float, dict]:
    """R1: Quantification discipline. 0.0 = no numbers, 1.0 = well-quantified."""
    total_weight = 0.0
    matches = []
    for pattern, weight in R1_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            total_weight += weight * len(found)
            matches.append({"pattern": pattern[:30], "count": len(found)})

    # Anti-pattern deduction
    for ap in R1_ANTI:
        if re.search(ap, text, re.IGNORECASE):
            total_weight = max(total_weight - 0.5, 0)

    # Normalize: expect ~5 weight points for a well-quantified response
    # Short responses (<50 words) need fewer numbers
    expected = 5.0 if word_count > 100 else 3.0 if word_count > 50 else 1.5
    score = min(total_weight / expected, 1.0)

    return round(score, 4), {"raw_weight": round(total_weight, 2), "matches": len(matches)}


# ================================================================
# R2: UNCERTAINTY — says what it doesn't know
# ================================================================
# What we measure: model acknowledges limits, hedges appropriately
# Source: ONTO R2 — "Says what it doesn't know — calibrated confidence"

R2_HEDGING = [
    # GOLD structural markers (universal)
    (r"\(R2\)", 2.0),
    # Uncertainty operators (math — universal)
    (r"±\s*\d", 1.5),
    (r"~\s*\d", 0.8),
    (r"\b\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*%", 0.8),                # range = uncertainty
    # NOTE: `\b95%\s*CI\b` removed (v5.1 bugfix). CI is R1 territory (quantification);
    # counting it again as R2 hedging double-inflates the same signal. The
    # `CI\s*[:,]?\s*\d` variant below requires a following bound (genuine range
    # expression, not a label), so it stays.
    (r"\bCI\s*[:,]?\s*\d", 1.2),
    (r"\bp\s*[<=]\s*0?\.\d+", 1.0),
    (r"\bIGR\s*[~=><:]\s*0?\.\d+", 2.0),
    # Study design limitations (universal nomenclature)
    (r"\bobservational\b", 1.0),
    (r"\bretrospective\b", 0.8),
    (r"\bcross[- ]?sectional\b", 0.8),
    (r"\bconfound\w*\b", 1.0),
    (r"\bbias\b", 0.8),
    (r"\bsurvivor\s+bias\b", 1.2),
    (r"\bhealthy\s+(user|adherer)\b", 1.2),
    (r"\bcorrelation\b", 0.8),
    (r"\bunderpowered\b", 1.0),
    # Numerical uncertainty
    (r"\b\d+\.?\d*\s*%\s*(confidence|probability|chance)\b", 1.0),
]

R2_WEASEL = []


def score_r2(text: str, word_count: int) -> Tuple[float, dict]:
    """R2: Uncertainty discipline. 0.0 = blind certainty, 1.0 = calibrated hedging."""
    total_weight = 0.0
    for pattern, weight in R2_HEDGING:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            total_weight += weight * len(found)

    for pattern, weight in R2_WEASEL:
        if re.search(pattern, text, re.IGNORECASE):
            total_weight += weight  # negative weight = deduction

    total_weight = max(total_weight, 0.0)

    expected = 3.5 if word_count > 100 else 2.0 if word_count > 50 else 1.0
    score = min(total_weight / expected, 1.0)

    return round(score, 4), {"raw_weight": round(total_weight, 2)}


# ================================================================
# R3: COUNTER — shows the other side
# ================================================================
# What we measure: model presents counterarguments and limitations
# Source: ONTO R3 — "Opposing views and limitations — not one-sided"

R3_PATTERNS = [
    # GOLD structural markers (universal)
    (r"\(R3\)", 2.0),
    # Universal scientific counter-markers
    (r"\bcounter[- ]?(argument|evidence|point)\b", 1.5),
    (r"\bconfound\w*\b", 1.0),
    (r"\bbias\w*\b", 0.8),
    (r"\bvs\.?\s", 1.0),                                           # "X vs Y" — universal
    (r"\b≠\b", 1.5),                                                # ≠ — universal math
    (r"\bcorrelation\s*[≠!]\s*causation\b", 2.0),
    # Causal counter-markers (moved from old R11 v4.2 — home in R3 per Kernel doctrine)
    (r"\bspurious\b", 1.2),
    (r"\breverse\s+causation\b", 1.5),
    (r"\binstrumental\s+variable\b", 1.5),
    (r"\bside[- ]?effect\w*\b", 0.8),
    (r"\brebound\b", 0.8),
    (r"\blimitation\w*\b", 1.0),
    (r"\brisk\w*\s*:", 1.0),                                        # "Risks:" section header
    # Numerical counter-evidence (universal)
    (r"\bplacebo\b", 1.0),
    (r"\bNNH\s*[=:]\s*\d", 1.5),                                 # Number needed to harm (counter-evidence)
    # NOTE: NNT removed — Number Needed to Treat is a positive effect measure,
    #       not a counterargument. NNT belongs conceptually in R1 (quantification).
    (r"\b(adverse|negative)\s+effect\b", 1.0),
    (r"\battenuate\w*\b", 1.0),
]


def score_r3(text: str, word_count: int) -> Tuple[float, dict]:
    """R3: Counter discipline. 0.0 = one-sided, 1.0 = balanced with counterarguments."""
    total_weight = 0.0
    for pattern, weight in R3_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            total_weight += weight * len(found)

    expected = 3.5 if word_count > 100 else 2.0 if word_count > 50 else 1.0
    score = min(total_weight / expected, 1.0)

    return round(score, 4), {"raw_weight": round(total_weight, 2)}


# ================================================================
# R4: SOURCES — cite or don't assert
# ================================================================
# What we measure: model provides verifiable references
# Source: ONTO R4 — "Author, year, DOI — or disclaim 'no source found'"

# ================================================================
# DOI WHITELIST (calibration_001 · F6 fix)
# ================================================================
# Set of registered CrossRef DOI prefixes for major biomedical / scientific
# publishers. Used by score_r4() to distinguish real DOI shape from fabricated
# citation-shaped strings. ~150 entries cover ≥95% of real published
# biomedical / scientific literature.
#
# Mistral-7B exploit (baseline_001 §F6): generated `10.2187/ngj.5309`.
# Prefix `10.2187` is NOT in CrossRef registry → flagged as fabricated.
# Real Japan Epidemiological Association prefix is `10.2188`.
#
# Refresh source: https://api.crossref.org/prefixes (quarterly)

DOI_WHITELIST_PREFIXES = {
    # Top biomedical / clinical
    "10.1001",  # JAMA / AMA
    "10.1002",  # Wiley
    "10.1006",  # Academic Press / Elsevier legacy
    "10.1016",  # Elsevier (ScienceDirect)
    "10.1021",  # ACS
    "10.1023",  # Springer
    "10.1037",  # APA
    "10.1038",  # Nature / NPG
    "10.1039",  # RSC
    "10.1042",  # Portland Press
    "10.1056",  # NEJM
    "10.1073",  # PNAS
    "10.1080",  # Taylor & Francis
    "10.1083",  # Rockefeller (JCB)
    "10.1085",  # Rockefeller (JGP)
    "10.1086",  # University of Chicago Press
    "10.1089",  # Mary Ann Liebert
    "10.1091",  # ASCB (MBC)
    "10.1093",  # Oxford UP
    "10.1097",  # Lippincott Williams & Wilkins
    "10.1098",  # Royal Society
    "10.1101",  # CSHL Press / bioRxiv / medRxiv
    "10.1103",  # APS
    "10.1109",  # IEEE
    "10.1111",  # Wiley
    "10.1113",  # Wiley Physiological Society
    "10.1117",  # SPIE
    "10.1118",  # AAPM
    "10.1126",  # Science / AAAS
    "10.1130",  # GSA
    "10.1136",  # BMJ
    "10.1142",  # World Scientific
    "10.1145",  # ACM
    "10.1146",  # Annual Reviews
    "10.1148",  # RSNA
    "10.1149",  # ECS
    "10.1152",  # APS Physiology
    "10.1158",  # AACR
    "10.1161",  # AHA
    "10.1163",  # Brill
    "10.1164",  # ATS
    "10.1165",  # ATS
    "10.1167",  # ARVO
    "10.1172",  # ASCI
    "10.1175",  # AMS
    "10.1177",  # SAGE
    "10.1182",  # ASH (Blood)
    "10.1183",  # ERS
    "10.1186",  # BMC / BioMed Central
    "10.1200",  # ASCO (JCO)
    "10.1208",  # AAPS
    "10.1210",  # Endocrine Society
    "10.1212",  # AAN (Neurology)
    "10.1213",  # IARS (Anesthesia)
    "10.1215",  # Duke UP
    "10.1242",  # Company of Biologists
    "10.1245",  # Springer (Annals of Surgery)
    "10.1248",  # Pharmaceutical Society of Japan
    "10.1257",  # American Economic Association
    "10.1265",  # Tohoku
    "10.1271",  # JSBBA
    "10.1289",  # NIEHS (EHP)
    "10.1330",  # BMJ Tobacco Control
    "10.1351",  # IUPAC
    "10.1359",  # ASBMR
    "10.1364",  # Optica (former OSA)
    "10.1371",  # PLoS
    "10.1373",  # AACC
    "10.1377",  # Health Affairs
    "10.1378",  # ACCP (CHEST)
    "10.1503",  # CMA (CMAJ)
    "10.1517",  # Informa Healthcare
    "10.1519",  # NSCA
    "10.1520",  # ASTM
    "10.1525",  # University of California Press
    "10.1530",  # Bioscientifica
    "10.1542",  # AAP (Pediatrics)
    "10.1554",  # SSE
    "10.1590",  # SciELO Brazil
    "10.1620",  # Tohoku
    "10.1681",  # ASN
    "10.1832",  # NICE
    "10.1872",  # Bentham
    "10.2105",  # APHA (AJPH)
    "10.2106",  # JBJS
    "10.2174",  # Bentham
    "10.2188",  # Japan Epidemiological Association
    "10.2196",  # JMIR
    "10.2215",  # ASN (CJASN)
    "10.2217",  # Future Medicine
    "10.2337",  # ADA (Diabetes Care)
    "10.2353",  # ASIP
    "10.2460",  # AVMA
    "10.2471",  # WHO Bulletin
    "10.2522",  # APTA
    "10.3109",  # Informa
    "10.3168",  # ADSA
    "10.3171",  # JNS
    "10.3201",  # CDC EID
    "10.3322",  # ACS Cancer Journal
    "10.3324",  # Ferrata Storti (Haematologica)
    "10.3389",  # Frontiers
    "10.3390",  # MDPI
    "10.3791",  # JoVE
    "10.4049",  # Journal of Immunology
    "10.4067",  # SciELO Chile
    "10.4081",  # PAGEPress
    "10.4103",  # Medknow
    "10.4137",  # Libertas Academica / SAGE
    "10.4158",  # AACE (Endocrine Practice)
    "10.4172",  # OMICS
    "10.4236",  # SciRP
    "10.4269",  # ASTMH
    "10.4274",  # Galenos
    "10.5114",  # Termedia
    "10.5152",  # AVES
    "10.5223",  # Korean Society
    "10.5527",  # Baishideng (World J family)
    "10.5604",  # Termedia
    "10.5694",  # MJA
    "10.5772",  # IntechOpen
    "10.5812",  # Kowsar
    "10.6004",  # NCCN
    "10.7150",  # Ivyspring (Theranostics, Int J Biol Sci)
    "10.7326",  # ACP (Annals of Internal Medicine)
    "10.7554",  # eLife
    "10.7717",  # PeerJ
    "10.7748",  # RCN
    "10.7860",  # JCDR
    # Domain-general / repositories
    "10.5061",  # Dryad
    "10.5281",  # Zenodo
    "10.6084",  # Figshare
    "10.17605", # OSF (Open Science Framework)
    "10.18653", # ACL (Association for Computational Linguistics)
    "10.18632", # Impact Journals (Oncotarget)
    "10.21105", # Journal of Open Source Software
    "10.21203", # Research Square
    "10.22541", # Authorea
    "10.31219", # OSF preprints
    "10.31234", # PsyArXiv
    "10.48550", # arXiv (modern DOIs)
    # Legacy CrossRef ranges
    "10.1000",  # CrossRef itself
}


R4_PATTERNS = [
    # DOI (gold standard)
    (r"\bDOI:\s*10\.\d+", 3.0),
    (r"10\.\d{4,9}/\S+", 2.5),                                    # bare DOI
    # Author-year citations
    (r"\b[A-Z][a-z]+\s+et\s+al\.?\s*[,(]\s*\d{4}\b", 2.0),      # "Smith et al., 2024"
    (r"\([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*[,\s]+\d{4}\)", 2.0),    # (Smith, 2024)
    (r"\b[A-Z][a-z]+\s+&\s+[A-Z][a-z]+\s*[,(]\s*\d{4}\b", 2.0), # "Smith & Jones, 2024"
    # Institutional sources
    (r"\b(WHO|CDC|FDA|EPA|NIH|IEEE|ISO|IPCC|NIST|EMA|MHRA)\b", 1.5),
    # Journal names
    (r"\b(NEJM|BMJ|JAMA|Lancet|Nature|Science|Cell|PNAS)\b", 1.5),
    # Numbered references
    (r"\[\d{1,2}\]", 1.0),                                        # [1], [12]
    # Explicit source attribution
    (r"\bSource[s]?:\s*\S+", 1.0),
    (r"\b(according\s+to|as\s+reported\s+by|per)\s+(?:the\s+)?[A-Z]", 0.8),
    # No-source disclosure (also counts positively — honesty)
    (r"\bno\s+(reliable\s+)?(source|citation|reference)\s+(found|available)\b", 1.0),
    (r"\bcould\s+not\s+(find|locate|verify)\s+(a\s+)?(source|reference)\b", 1.0),
]


def score_r4(text: str, word_count: int) -> Tuple[float, dict]:
    """R4: Source discipline. 0.0 = no citations, 1.0 = well-sourced.

    v4.2: epistemic gate — journal name alone ≠ proof.
    Without DOI or full "Author et al. YEAR" citation, score capped at 0.5.
    Density raised: expected ×2 (6 DOI ≠ 2 DOI at ceiling).

    v5.1.1 (calibration_001): DOI prefix whitelist verification.
    DOIs with prefixes outside CrossRef registry get 10x penalty
    (weight 0.25 instead of 2.5). Closes Mistral-style fabrication exploit.
    """
    # First pass: extract all DOI strings, classify verified vs unverified
    doi_pattern = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)
    doi_pattern_labeled = re.compile(r"\bDOI:\s*(10\.\d+(?:/\S+)?)", re.IGNORECASE)
    all_dois = set()
    for m in doi_pattern.finditer(text):
        all_dois.add(m.group(0).rstrip(".,;:)"))
    for m in doi_pattern_labeled.finditer(text):
        all_dois.add(m.group(1).rstrip(".,;:)"))

    doi_verified_count = 0
    doi_unverified_count = 0
    for doi in all_dois:
        prefix_match = re.match(r"10\.\d+", doi)
        if not prefix_match:
            continue
        prefix = prefix_match.group(0)
        if prefix in DOI_WHITELIST_PREFIXES:
            doi_verified_count += 1
        else:
            doi_unverified_count += 1

    # Second pass: score patterns, but apply whitelist penalty to DOI hits
    total_weight = 0.0
    doi_count_total = 0
    for pattern, weight in R4_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if not found:
            continue
        is_doi_pattern = ("10\\." in pattern or "DOI" in pattern)
        if is_doi_pattern:
            doi_count_total += len(found)
            # Distribute weight per DOI based on whitelist verification.
            # Verified DOI gets full weight; unverified gets 10x penalty.
            n_total = len(found)
            n_verified = min(doi_verified_count, n_total)
            n_unverified = n_total - n_verified
            # Reset verified counter as we consume it across DOI pattern matches
            doi_verified_count -= n_verified
            total_weight += weight * n_verified
            total_weight += (weight * 0.1) * n_unverified
        else:
            total_weight += weight * len(found)

    # Restore counters for return payload (we mutated above)
    doi_verified_count_final = sum(
        1 for d in all_dois
        if (m := re.match(r"10\.\d+", d)) and m.group(0) in DOI_WHITELIST_PREFIXES
    )
    doi_unverified_count_final = len(all_dois) - doi_verified_count_final

    # Density ceiling
    expected = 12.0 if word_count > 100 else 6.0 if word_count > 50 else 2.0
    score = min(total_weight / expected, 1.0)

    # Epistemic gate: verifiable-proof presence check
    # Only WHITELIST-VERIFIED DOIs count as verifiable proof now.
    has_verified_doi = doi_verified_count_final > 0
    has_full_citation = bool(re.search(
        r"\b[A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)?\s+et\s+al\.?,?\s+\d{4}\b",
        text
    ))
    verifiable_proof = has_verified_doi or has_full_citation

    if not verifiable_proof:
        score = min(score, 0.5)

    fabrication_suspected = doi_unverified_count_final > 0

    # Hard cap if fabrication detected (calibration_001 §6 acceptance):
    # Verified : Unverified ratio matters. If model invented any DOI prefix,
    # cap score regardless of other "et al." matches — the citation discipline
    # is structurally broken, the rest is veneer.
    if fabrication_suspected:
        if doi_verified_count_final == 0:
            # All cited DOIs are invented → hard floor
            score = min(score, 0.15)
        else:
            # Mixed: some real, some fabricated → moderate cap (still penalize)
            ratio = doi_verified_count_final / (doi_verified_count_final + doi_unverified_count_final)
            cap = 0.3 + 0.4 * ratio  # 0.3 if mostly fake, 0.7 if mostly real
            score = min(score, cap)

    return round(score, 4), {
        "raw_weight": round(total_weight, 2),
        "doi_count": doi_count_total,
        "doi_verified_count": doi_verified_count_final,
        "doi_unverified_count": doi_unverified_count_final,
        "fabrication_suspected": fabrication_suspected,
        "has_verifiable_proof": verifiable_proof,
    }


# ================================================================
# R5: EVIDENCE GRADE — hierarchy matters
# ================================================================
# What we measure: model distinguishes RCT from blog post
# Source: ONTO R5 — "RCT > observational > expert opinion — hierarchy matters"

R5_PATTERNS = [
    # Top-tier evidence mentioned
    (r"\b(meta[- ]?analysis|systematic\s+review|Cochrane)\b", 2.0),
    (r"\b(randomized|randomised)\s+(controlled\s+)?trial\b", 2.0),
    (r"\bRCT\b", 2.0),
    # Mid-tier
    (r"\bcohort\s+study\b", 1.5),
    (r"\bcase[- ]?control\b", 1.5),
    (r"\bprospective\s+study\b", 1.5),
    (r"\bretrospective\s+(study|analysis|review)\b", 1.2),
    (r"\bcross[- ]?sectional\b", 1.2),
    # Evidence grading explicit
    (r"\b(Grade|Level|Class)\s+(I{1,3}|IV|V|[A-D])\b", 2.0),
    (r"\bevidence\s+(grade|level|quality)\s*:\s*(high|moderate|low|very\s+low)\b", 2.0),
    # Study design awareness
    (r"\b(observational|experimental|longitudinal|interventional)\b", 1.0),
    (r"\b(single[- ]?arm|open[- ]?label|double[- ]?blind|placebo[- ]?controlled)\b", 1.5),
    # NOTE: `\b(N[=-]\d|n[=-]\d|sample\s+size)\b` removed (v5.1 bugfix).
    # Sample size is quantification (R1), not evidence hierarchy. R5 measures
    # study-design grade (RCT vs cohort vs case series), not absolute N.
    # Hierarchy awareness (model shows it knows the difference)
    (r"\b(stronger|weaker|higher[- ]?quality|lower[- ]?quality)\s+evidence\b", 1.5),
    (r"\b(preclinical|in\s+vitro|in\s+vivo|animal\s+(model|study|data))\b", 1.2),
    (r"\b(Phase\s+[I1234]|phase\s+[I1234])\b", 1.5),
]


def score_r5(text: str, word_count: int) -> Tuple[float, dict]:
    """R5: Evidence grade discipline. 0.0 = no hierarchy, 1.0 = evidence-graded."""
    total_weight = 0.0
    for pattern, weight in R5_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            total_weight += weight * len(found)

    expected = 4.0 if word_count > 100 else 2.0 if word_count > 50 else 1.0
    score = min(total_weight / expected, 1.0)

    return round(score, 4), {"raw_weight": round(total_weight, 2)}


# ================================================================
# R6: FALSIFIABILITY — what would disprove this?
# ================================================================
# What we measure: model provides criteria for being wrong
# Source: ONTO R6 — "What would disprove this claim? Testable assertions only."

R6_PATTERNS = [
    # GOLD structural markers (universal)
    (r"\(R6\)", 3.0),
    (r"\bR6\s*[:.]", 2.0),
    (r"\bFalsifiability\s*[:.]", 2.5),                              # GOLD header
    (r"\bFalsif\w+\s*\(R6\)", 3.0),                                 # "Фальсифицируемость (R6):"
    # Universal scientific terms
    (r"\bfalsif\w+\b", 2.0),                                        # falsifiable/falsification/falsify
    (r"\btestable\b", 1.0),
    (r"\bhypothesis\s*:", 1.5),
    (r"\bRCT\b.{0,40}\bN\s*[>=]\s*\d", 2.0),                      # "RCT (N>5000)" — test criterion
    # Numerical falsification criteria
    (r"\b(HR|RR|OR)\s*[><=]\s*\d", 1.5),                           # "HR >1.5" — threshold
    (r"\bp\s*[><=]\s*0?\.\d+", 1.0),                               # "p>0.05" — failure criterion
    (r"\bN\s*[>]=?\s*[\d,]+", 1.0),                                 # "N>100,000" — required sample
]


def score_r6(text: str, word_count: int) -> Tuple[float, dict]:
    """R6: Falsifiability discipline. 0.0 = unfalsifiable claims, 1.0 = testable."""
    total_weight = 0.0
    for pattern, weight in R6_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            total_weight += weight * len(found)

    # R6 is rare even in good responses — lower expectation
    expected = 3.0 if word_count > 100 else 1.5 if word_count > 50 else 0.8
    score = min(total_weight / expected, 1.0)

    return round(score, 4), {"raw_weight": round(total_weight, 2)}


# ================================================================
# R7: NO FABRICATION — cross-R consistency check
# ================================================================
# What we measure: claims are backed, not invented
# Source: ONTO R7 — "Zero invented citations, statistics, or facts. No exceptions."
#
# R7 is INVERSE: starts at 1.0, deducted for red flags.
# Red flags: overconfidence patterns + absence of sources
# Cross-R: high R1 + low R4 = numbers from nowhere = fabrication risk

OVERCONFIDENCE_PATTERNS = [
    # Universal numerical red flags
    (r"\b100\s*%\b(?!\s*CI)", 0.10),                               # "100%" (not "100% CI")
    (r"\b0\s*%\s*(risk|chance|probability)\b", 0.10),              # "0% risk"
    # Uncited authority (R18 introns — universal in GOLD context)
    (r"\bstudies\s+show\b(?!.*\b(?:DOI|et\s+al|(?:19|20)\d{2}))", 0.08),
    (r"\bresearch\s+(shows|suggests)\b(?!.*\b(?:DOI|et\s+al|(?:19|20)\d{2}))", 0.08),
    (r"\bexperts?\s+(say|agree)\b(?!.*\b(?:DOI|et\s+al|who))", 0.08),
]

# ----------------------------------------------------------------
# C2 — R7-CLAIM PATTERNS (self-assertion of non-fabrication)
# ----------------------------------------------------------------
# Kernel v5.1 C2: "Claiming no fabrication (R7) without sources (R4) is
# unverifiable. Acknowledge the gap." Detection: model makes an explicit
# meta-claim that its output is accurate/sourced/verified. Without
# corresponding R4 evidence, that claim is performative — it creates the
# appearance of rigor without proof. Trigger: any R7-claim pattern detected
# AND r4_score < 0.15.
R7_CLAIM_PATTERNS = [
    # EN — claim of sourcing / verification
    r"\ball\s+(claims|facts|data|statistics)\s+(are\s+)?(sourced|verified|cited|backed|accurate)\b",
    r"\b(carefully|thoroughly|rigorously)\s+(sourced|cited|verified|researched)\b",
    r"\b(based\s+on|from)\s+peer[- ]reviewed\s+(research|sources|literature|studies)\b",
    r"\bno\s+fabrication\b",
    r"\b(accurate|verified|sourced)\s+to\s+the\s+best\s+of\s+(my|our)\s+knowledge\b",
    r"\b(every|each)\s+(claim|statement|fact)\s+(is\s+)?(sourced|cited|backed|verified)\b",
    r"\bfact[- ]?checked\s+against\b",
    r"\bcross[- ]?referenced\s+with\s+(sources|literature|research)\b",
    # RU — tolerate intervening modifiers between subject and verb
    r"\bвсе\s+(?:\w+\s+){0,5}(факты|данные|утверждения|заявления|claims)\s+(?:\w+\s+){0,5}(проверены|подтверждены|верифицированы|цитируются|сверены)",
    r"\b(факты|данные|утверждения)\s+(?:\w+\s+){0,3}(проверены|подтверждены|верифицированы)",
    r"\bбез\s+вымысла\b",
    r"\bтщательно\s+(проверен|источник|цитиру|сверен|исследован)",
    r"\bна\s+основе\s+рецензируем\w+",
    r"\bкаждое\s+(?:\w+\s+){0,3}(утверждение|заявление|факт)\s+(?:\w+\s+){0,3}(подтверждено|проверено|источник|цитиру)",
]


def score_r7(
    text: str,
    word_count: int,
    r1_score: float,
    r2_score: float,
    r3_score: float,
    r4_score: float,
    r5_score: float,
    r6_score: float,
    intron_ratio: float = 0.0,
) -> Tuple[float, dict]:
    """
    R7: No fabrication — the cross-R integrity layer of the scoring engine.

    Starts at 1.0, deducted for red flags:
      (a) Overconfidence language (OVERCONFIDENCE_PATTERNS)
      (b) R17 C1-C7 cross-R constraints (embedded from Kernel v5.1 Layer V)
      (c) R18 intron ratio > 0.3 (heavy filler degrades signal — diagnostic)
      (d) C8 frameshift — APOPTOSIS FLAG, not a penalty. Triggered externally
          after R7 is finalised, when the accumulated signature indicates
          structural fabrication past the recovery threshold.

    Why here: R17 (Self-Proofread) and R18 (Epistemic Splicing) are Kernel
    Layer V "Coherence" — they are not separate metrics, they are applied
    *during* R7 finalisation. This mirrors GOLD Kernel doctrine: proofread
    and splice before delivery. Generation-time splicing (actually removing
    introns before the model speaks) is a KERNEL PROMPT DIRECTIVE — not a
    scoring-engine transformation. The engine measures; the kernel shapes.

    Spec: GOLD_KERNEL_v5.1.json → cognitive_dna.layer_V_coherence.R17.constraints
    Spec: ONTO_ARCHITECTURE_v2_SPEC.md §2 S8-B / S8-C (Kernel-canonical alignment).
    """
    penalty = 0.0
    flags = []

    # --- (a) Overconfidence language ---
    for pattern, weight in OVERCONFIDENCE_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            penalty += weight * len(found)
            flags.append(pattern[:30])
    penalty = min(penalty, 0.60)

    # --- (b) R17 C1-C7 cross-R constraints (Kernel v5.1 layer_V_coherence) ---
    # Canonical numbering matches GOLD_KERNEL_v5.1.json. C8 is handled
    # post-hoc (apoptosis flag) — NOT added to cross_r_penalty.
    cross_r_penalty = 0.0

    # C1: numbers_need_sources — R1 numbers ↔ R4 sources
    # High claims without any sourcing = numbers from nowhere.
    if r1_score > 0.5 and r4_score < 0.15:
        cross_r_penalty += 0.20
        flags.append("C1: R1>0.5 + R4<0.15 (numbers without sources)")
    # C1-extreme: strong claims, zero sourcing.
    if r1_score > 0.7 and r4_score < 0.05:
        cross_r_penalty += 0.15
        flags.append("C1-ext: R1>0.7 + R4<0.05 (strong claims, zero sources)")

    # C2: no_fabrication_needs_proof — R7-self-claim patterns ↔ R4 sources
    # Model asserts "all claims sourced / verified / fact-checked" but has no
    # R4 anchors. The meta-claim is unverifiable — performative rigor.
    # Kernel: "Claiming no fabrication (R7) without sources (R4) is unverifiable."
    r7_claim_hits = 0
    r7_claim_samples = []
    for pattern in R7_CLAIM_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            r7_claim_hits += len(found)
            if len(r7_claim_samples) < 3:
                r7_claim_samples.append(pattern[:40])
    if r7_claim_hits > 0 and r4_score < 0.15:
        cross_r_penalty += 0.15
        flags.append(
            f"C2: R7-claim×{r7_claim_hits} + R4<0.15 "
            f"(non-fabrication asserted without proof)"
        )

    # C3: certainty_needs_hierarchy — R2 uncertainty ↔ R5 evidence grade
    # Long confident output with no hedging AND no evidence hierarchy = blind confidence.
    # Gate on word_count > 50 so short replies aren't punished for missing ceremony.
    if r2_score < 0.1 and r5_score < 0.1 and word_count > 50:
        cross_r_penalty += 0.15
        flags.append("C3: R2<0.1 + R5<0.1 (no uncertainty + no evidence grade)")

    # C4: counterarguments_need_sources — R3 counter ↔ R4 sources
    # Performed counterargument without citations = theatre of debate.
    # (v5.0 called this "C2" — renamed to Kernel-canonical C4 in v5.1.)
    if r3_score > 0.5 and r4_score < 0.15:
        cross_r_penalty += 0.15
        flags.append("C4: R3>0.5 + R4<0.15 (counter without sources = theatre)")

    # C5: grading_needs_specifics — R5 hierarchy ↔ R4 named studies
    # Model discusses evidence hierarchy (meta-analysis / RCT / cohort) but
    # names no specific studies. Phantom hierarchy, empty ranking.
    # Kernel: "Evidence hierarchy (R5) without named studies (R4) = phantom hierarchy."
    if r5_score > 0.5 and r4_score < 0.15:
        cross_r_penalty += 0.15
        flags.append("C5: R5>0.5 + R4<0.15 (grading without named studies)")

    # C6: falsifiability_implies_uncertainty — R6 falsifiability ↔ R2 uncertainty
    # Stating what would disprove the claim (R6) while expressing zero
    # uncertainty (R2) is a contradiction: if it's falsifiable, it's not
    # 100% certain. Kernel: "Stating what would disprove (R6) while claiming
    # 100% certainty (R2=0) = contradiction."
    if r6_score > 0.5 and r2_score < 0.1:
        cross_r_penalty += 0.15
        flags.append("C6: R6>0.5 + R2<0.1 (falsifiable + zero uncertainty = contradiction)")

    # C7: foundation_check — "beautiful empty"
    # 3+ of {R1, R2, R3, R5, R6} above 0.6 while R4 < 0.05.
    # The text *performs* discipline (numbers, hedging, counter, hierarchy,
    # falsifiability) but has no proof chain anchor. Highest cost.
    # (v5.0 called this "C4" — renamed to Kernel-canonical C7 in v5.1.)
    high_count = sum(
        1 for s in (r1_score, r2_score, r3_score, r5_score, r6_score) if s > 0.6
    )
    if high_count >= 3 and r4_score < 0.05:
        cross_r_penalty += 0.30
        flags.append(
            f"C7: {high_count} R-scores >0.6 with R4<0.05 (beautiful empty)"
        )

    # --- (c) R18 intron DIAGNOSTIC (Kernel v5.1 layer_V_coherence.R18) ---
    # Heavy filler degrades R7. ONE penalty pass, not double-counted on
    # composite. Post-hoc detection informs R7; generation-time splicing
    # lives in the Kernel prompt (see kernel.py, Session 9-D).
    if intron_ratio > 0.3:
        cross_r_penalty += 0.10
        flags.append(f"R18: intron_ratio={intron_ratio:.2f} (heavy filler)")

    total_penalty = min(penalty + cross_r_penalty, 0.90)
    score = max(1.0 - total_penalty, 0.0)

    return round(score, 4), {
        "overconfidence_penalty": round(penalty, 4),
        "cross_r_penalty": round(cross_r_penalty, 4),
        "flags": flags,
        "r7_claim_hits": r7_claim_hits,
        "r7_claim_samples": r7_claim_samples,
    }


# ----------------------------------------------------------------
# C8 — FRAMESHIFT / APOPTOSIS (post-R7 finalisation check)
# ----------------------------------------------------------------
# Kernel v5.1 C8: "R7 failure = stop-codon. One fabrication invalidates
# entire epistemic chain. Apoptosis." This is NOT a penalty — R7 is already
# at floor. This is a runtime signal to app.py that the output has passed
# the structural-fabrication threshold and MUST NOT be delivered.
#
# Without a DOI verifier service the single-fabrication detection requires
# a proxy: if R7 has fallen to ≤ 0.15 (i.e. ≥ 0.85 penalty accumulated
# from overconfidence + multiple R17 violations), the output's epistemic
# chain is structurally broken. Frameshift. Apoptosis.

APOPTOSIS_R7_THRESHOLD = 0.15


def check_apoptosis(r7_score: float, r7_detail: dict) -> dict:
    """
    C8 frameshift detector. Returns structured apoptosis signal.

    Triggered when final R7 ≤ APOPTOSIS_R7_THRESHOLD (post all C1-C7 + R18
    + overconfidence penalties). At this point the output has the signature
    of structural fabrication: multiple cross-R violations stacking with
    overconfidence language. Delivering this output would mean publishing
    fabricated content with a scoring veneer.

    Runtime contract: app.py reads `apoptosis_triggered` from the returned
    score_result. If True, it MUST replace the LLM response with a
    Genesis-Protocol-referenced refusal. See Kernel v5.1 R11 Integrity:
    "Refuse to operate with damaged DNA (apoptosis)."
    """
    if r7_score > APOPTOSIS_R7_THRESHOLD:
        return {"apoptosis_triggered": False, "apoptosis_reason": None, "apoptosis_detail": None}

    # Build human-readable reason from the R17 flags that drove R7 down
    flags = r7_detail.get("flags", [])
    r17_flags = [f for f in flags if f.startswith(("C1", "C2", "C3", "C4", "C5", "C6", "C7"))]
    overconf_hit = r7_detail.get("overconfidence_penalty", 0.0) >= 0.20

    reason = (
        f"C8 frameshift: R7 final = {r7_score:.3f} ≤ {APOPTOSIS_R7_THRESHOLD} "
        f"(structural fabrication signature)."
    )
    detail = {
        "r7_final": round(r7_score, 4),
        "threshold": APOPTOSIS_R7_THRESHOLD,
        "r17_violations": r17_flags,
        "overconfidence_penalty": r7_detail.get("overconfidence_penalty", 0.0),
        "cross_r_penalty": r7_detail.get("cross_r_penalty", 0.0),
        "overconfidence_dominant": overconf_hit,
    }
    return {
        "apoptosis_triggered": True,
        "apoptosis_reason": reason,
        "apoptosis_detail": detail,
    }


# ================================================================
# R18 INTRON DETECTION (DIAGNOSTIC SIGNAL — informs R7)
# ================================================================
# Introns = epistemic filler that degrades signal-to-noise.
#
# Role separation (Kernel v5.1 layer_V_coherence.R18):
#   * Generation-time self-splicing — model self-edits before delivery.
#     This lives in the GOLD Kernel PROMPT DIRECTIVE (kernel.py), not here.
#     ONTO measures; the kernel shapes. The engine never rewrites output.
#   * Post-hoc detection (below) — diagnostic signal. If intron_ratio > 0.3,
#     R7 cross_r_penalty gets +0.10. ONE pass, not double-counted on the
#     composite. Exposed as r18_intron_ratio / r18_intron_count / r18_samples
#     for UI transparency, not as a separate bar or separate score.
#
# v5.1: no behaviour change vs v5.0. Only clarifies role in comments and
# ensures the output field naming aligns with Kernel canonical.

_INTRON_PATTERNS = {
    "vague_authority": (0.8, [
        r"\bstudies\s+(?:show|suggest|indicate|have\s+(?:shown|found))\b",
        r"\bresearch\s+(?:shows|suggests|indicates)\b",
        r"\bexperts?\s+(?:say|agree|believe|suggest|recommend)\b",
        r"\bисследования\s+(?:показывают|показали|доказывают)\b",
        r"\bучёные\s+(?:считают|полагают|утверждают)\b",
        r"\bпо\s+(?:мнению|данным)\s+(?:экспертов|учёных)\b",
    ]),
    "complexity_shield": (0.6, [
        r"\b(?:it(?:'s|\s+is)|this\s+is)\s+a?\s*(?:complex|complicated|nuanced|multifaceted)\s+(?:topic|issue|question)\b",
        r"\bэто\s+(?:сложная?|непростая?)\s+(?:тема|вопрос|проблема)\b",
        r"\bвсё\s+не\s+так\s+просто\b",
    ]),
    "consensus_no_source": (0.7, [
        r"\bmost\s+(?:experts?|scientists?)\s+(?:agree|believe)\b",
        r"\beveryone\s+(?:knows|agrees)\b",
        r"\bбольшинство\s+(?:экспертов|учёных)\s+(?:считают|согласны)\b",
        r"\bвсем\s+известно\b",
    ]),
    "filler": (0.3, [
        r"\bit(?:'s|\s+is)\s+(?:worth|important\s+to)\s+(?:noting|mentioning)\s+that\b",
        r"\bneedless\s+to\s+say\b", r"\bat\s+the\s+end\s+of\s+the\s+day\b",
        r"\bстоит\s+(?:отметить|заметить)\s*,?\s*что\b",
        r"\bважно\s+(?:отметить|понимать)\s*,?\s*что\b",
    ]),
}


def _detect_introns(text: str) -> dict:
    """
    R18 intron detector — diagnostic only (not a standalone score in v5.0).
    Returns intron_ratio (weighted chars / total chars), count, and samples.
    Consumed by score_r7 to trigger cross_r_penalty when ratio > 0.3.
    """
    if not text or not text.strip():
        return {"intron_ratio": 0.0, "intron_count": 0, "samples": []}
    total_chars = len(text.strip())
    weighted, count, seen, samples = 0.0, 0, set(), []
    for cat, (severity, pats) in _INTRON_PATTERNS.items():
        for p in pats:
            try:
                for m in re.finditer(p, text, re.IGNORECASE):
                    if m.start() not in seen:
                        seen.add(m.start())
                        weighted += len(m.group()) * severity
                        count += 1
                        if len(samples) < 5:
                            samples.append({"category": cat, "match": m.group()[:60]})
            except re.error:
                continue
    ratio = min(weighted / max(total_chars, 1), 1.0)
    return {"intron_ratio": round(ratio, 4), "intron_count": count, "samples": samples}



# ================================================================
# COMPLIANCE GRADING (A-F)
# ================================================================

def classify_compliance(composite: float) -> dict:
    """Grade composite score (0-10) into A-F compliance class."""
    if composite >= 9.0:
        return {"class": "A", "label": "Expert-grade epistemic discipline", "layer": "gold"}
    elif composite >= 7.5:
        return {"class": "B", "label": "Good epistemic discipline", "layer": "gold"}
    elif composite >= 5.5:
        return {"class": "C", "label": "Moderate — gaps in discipline", "layer": "standard"}
    elif composite >= 3.5:
        return {"class": "D", "label": "Poor — significant discipline gaps", "layer": "open"}
    else:
        return {"class": "F", "label": "Unreliable — minimal discipline", "layer": "none"}


# ================================================================
# MAIN: compute_risk_score (backward-compatible API)
# ================================================================

def compute_risk_score(
    output: str,
    confidence: Optional[float] = None,
    ground_truth: Optional[str] = None,
    domain: Optional[str] = None,
    logprobs: Optional[List[float]] = None,
    temperature: Optional[float] = None,
    context: Optional[str] = None,
    igr_gt: Optional[float] = None,
    enabled_r_modules: Optional[List[int]] = None,  # kept for API compat; ignored in v5.x
) -> dict:
    """
    ONTO Scoring Engine v5.1

    Scores R1-R7 epistemic discipline in model output.
    R17 (Self-Proofread, C1-C7 cross-R) and R18 (Epistemic Splicing post-hoc
    detection) are embedded inside score_r7. C8 (frameshift) is the apoptosis
    signal, surfaced in the return dict as `apoptosis_triggered` / `apoptosis_reason`.

    R8-R16 behavioral modules are NOT measured here. They are GOLD Kernel
    prompt directives (kernel.py, Session 9). The `enabled_r_modules`
    parameter is kept in the signature for backward compatibility but ignored —
    UI toggles now control Kernel prompt construction, not scoring.

    Composite = weighted average of R1-R7 × 10. Grade A-F from composite.

    Apoptosis contract:
      Runtime consumers (app.py agent_chat) MUST check
      result["apoptosis_triggered"]. If True, DO NOT deliver the LLM
      response — replace with structured refusal referencing Genesis
      Protocol. See Kernel v5.1 R11 Integrity.
    """
    text = output[:12000] if len(output) > 12000 else output
    words = text.split()
    word_count = max(len(words), 1)

    # --- R18 intron diagnostic (consumed by R7 below) ---
    intron_info = _detect_introns(text)
    intron_ratio = intron_info["intron_ratio"]

    # --- Score CORE R1-R7 ---
    r1, r1_detail = score_r1(text, word_count)
    r2, r2_detail = score_r2(text, word_count)
    r3, r3_detail = score_r3(text, word_count)
    r4, r4_detail = score_r4(text, word_count)
    r5, r5_detail = score_r5(text, word_count)
    r6, r6_detail = score_r6(text, word_count)
    # R7 receives R2/R3/R5/R6 for C1-C7 cross-R constraints + intron_ratio for R18 diagnostic.
    # v5.1: r6_score is now passed (C6 requires it).
    r7, r7_detail = score_r7(text, word_count, r1, r2, r3, r4, r5, r6, intron_ratio)

    # --- C8 Apoptosis check (post-R7 finalisation) ---
    apop = check_apoptosis(r7, r7_detail)

    # Expose R18 diagnostic alongside R7 details (not as a separate score key)
    r7_detail["r18_intron_ratio"] = intron_ratio
    r7_detail["r18_intron_count"] = intron_info["intron_count"]
    r7_detail["r18_samples"] = intron_info["samples"]

    r_scores = {"R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5, "R6": r6, "R7": r7}
    r_details = {
        "r1_quantify": r1_detail, "r2_uncertainty": r2_detail,
        "r3_counter": r3_detail, "r4_sources": r4_detail,
        "r5_evidence_grade": r5_detail, "r6_falsifiability": r6_detail,
        "r7_no_fabrication": r7_detail,
    }

    # --- Weights (R1-R7 only) ---
    # Base weights tuned to WP Product 1 composite formula.
    base_weights = {"R1": 0.14, "R2": 0.14, "R3": 0.12, "R4": 0.18, "R5": 0.12, "R6": 0.10, "R7": 0.20}
    # Short-response adjustment: uncertainty (R2) and no-fabrication (R7) dominate
    # when there isn't enough text to carry numbers, counter, or grade.
    if word_count < 30:
        base_weights = {"R1": 0.10, "R2": 0.25, "R3": 0.10, "R4": 0.10, "R5": 0.05, "R6": 0.05, "R7": 0.35}
    elif word_count < 80:
        base_weights = {"R1": 0.15, "R2": 0.18, "R3": 0.12, "R4": 0.18, "R5": 0.10, "R6": 0.07, "R7": 0.20}

    weights = dict(base_weights)

    # --- Composite ---
    total_weight = sum(weights.values())
    composite_raw = sum(r_scores[k] * weights[k] for k in r_scores) / total_weight
    composite = round(composite_raw * 10, 1)  # 0-10 scale

    # Risk score (inverted, 0-1, backward compat)
    risk_score = round(1.0 - composite_raw, 4)
    risk_score = min(max(risk_score, 0.01), 0.99)

    # --- Compliance ---
    comp = classify_compliance(composite)

    # --- Output (backward-compatible shape + v5.1 apoptosis fields) ---
    return {
        # Core
        "risk_score": risk_score,
        "layer": comp["layer"],
        "compliance": comp["label"],
        "calibration": 80.0,  # fixed — all signals are text-based, no external
        "engine_version": "5.1.1",
        "signals_used": 7,

        # GOLD/v3 compat
        "compliance_class": comp["class"],
        "compliance_label": comp["label"],

        # R-scores (R1-R7 only in v5.x)
        "r_scores": r_scores,
        "composite": composite,

        # Old fields mapped for backward compat
        "rep": r2,  # R2 hedging ≈ old REP
        "epce": None,
        "dce": None,
        "dla": None,
        "dla_flag": None,

        # Factor details (backward compat shape)
        "factors": r_details,

        # Weights applied (normalized)
        "weights_applied": {k: round(v / total_weight, 3) for k, v in weights.items()},

        # v5.1: C8 Apoptosis signal (Kernel v5.1 layer_V_coherence.R17.constraints.C8)
        # Runtime MUST inspect this. If triggered, do not deliver the LLM
        # response — replace with Genesis-Protocol-referenced refusal.
        "apoptosis_triggered": apop["apoptosis_triggered"],
        "apoptosis_reason": apop["apoptosis_reason"],
        "apoptosis_detail": apop["apoptosis_detail"],
    }


# ================================================================
# RECOMMENDATIONS (utility)
# ================================================================

def generate_recommendations(result: dict) -> list:
    """Generate improvement recommendations from R-scores."""
    recs = []
    rs = result.get("r_scores", {})

    # Apoptosis dominates if triggered — put it first.
    if result.get("apoptosis_triggered"):
        recs.append(
            "C8 FRAMESHIFT (apoptosis): output has structural fabrication signature. "
            "Multiple R17 cross-R violations + overconfidence. Rewrite from ground truth, "
            "not from rhetoric. See Genesis Protocol."
        )

    if rs.get("R1", 1.0) < 0.3:
        recs.append("R1: Add specific numbers — percentages, sample sizes, effect sizes instead of vague claims.")
    if rs.get("R2", 1.0) < 0.3:
        recs.append("R2: Acknowledge uncertainty — state what you don't know and where evidence is limited.")
    if rs.get("R3", 1.0) < 0.3:
        recs.append("R3: Present counterarguments — show the other side, limitations, and alternative views.")
    if rs.get("R4", 1.0) < 0.3:
        recs.append("R4: Add sources — cite author, year, DOI. Or disclaim 'no source found'.")
    if rs.get("R5", 1.0) < 0.3:
        recs.append("R5: Specify evidence grade — distinguish RCT from blog post, meta-analysis from opinion.")
    if rs.get("R6", 1.0) < 0.3:
        recs.append("R6: State falsifiability — what evidence would disprove this claim?")
    if rs.get("R7", 1.0) < 0.5:
        recs.append("R7: Fabrication risk detected — claims without sources, or overconfident assertions.")

    # R17 cross-R violations — surface specifics that the bar-level R-scores can't show.
    r7_factor = result.get("factors", {}).get("r7_no_fabrication", {})
    flags = r7_factor.get("flags", [])
    if any(f.startswith("C2:") for f in flags):
        recs.append(
            "C2: Claiming 'all sourced / verified / fact-checked' without actual citations. "
            "Either cite or remove the meta-claim."
        )
    if any(f.startswith("C5:") for f in flags):
        recs.append(
            "C5: Discussing evidence hierarchy (meta-analysis / RCT / cohort) without naming "
            "specific studies. Phantom hierarchy — name the trials or drop the ranking."
        )
    if any(f.startswith("C6:") for f in flags):
        recs.append(
            "C6: Stating falsifiability conditions while expressing zero uncertainty. "
            "If the claim is falsifiable, it isn't 100%% certain."
        )
    if any(f.startswith("C7:") for f in flags):
        recs.append(
            "C7: 'Beautiful empty' — multiple discipline signals present but no proof chain. "
            "Add at least one DOI or full 'Author et al. YEAR' citation."
        )

    # R18 (introns) surfaced via R7 factor — advise cleanup of epistemic filler
    if r7_factor.get("r18_intron_ratio", 0.0) > 0.3:
        recs.append("R18: Heavy epistemic filler detected — remove 'studies show / experts agree' phrases without citations.")

    return recs
