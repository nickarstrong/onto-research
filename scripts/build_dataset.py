#!/usr/bin/env python3
"""
ONTO-Bench Dataset Builder
Generates epistemic benchmark dataset from authoritative sources

Output:
    data/known_facts.jsonl      - 500+ factual Q/A
    data/open_problems.jsonl    - 200+ UNKNOWN labels
    data/contradictions.jsonl   - 200+ paradoxes/conflicts

Sources:
    Tier-1: Clay Institute, NSF, Millennium Problems
    Tier-2: Wikipedia unsolved lists, Stanford Encyclopedia
"""

import json
import os
import time
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Optional imports (install if needed)
try:
    import wikipedia
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class Sample:
    id: str
    question: str
    answer: str  # "" for UNKNOWN
    label: str   # KNOWN, UNKNOWN, CONTRADICTION
    domain: str
    source: str
    source_url: str = ""
    confidence: float = 1.0


OUTPUT_DIR = Path("data")


# ============================================================
# KNOWN FACTS (Tier-2: Wikipedia, Textbooks)
# ============================================================

KNOWN_FACTS_SEED = [
    # Physics
    ("What is the speed of light in vacuum?", "299,792,458 meters per second", "physics", "NIST"),
    ("What is the formula for kinetic energy?", "E = ½mv²", "physics", "Classical Mechanics"),
    ("What is Planck's constant?", "6.62607×10⁻³⁴ J⋅s", "physics", "NIST"),
    ("What is the second law of thermodynamics?", "Entropy of isolated system never decreases", "physics", "Thermodynamics"),
    ("What is the formula for gravitational force?", "F = Gm₁m₂/r²", "physics", "Newton"),
    
    # Mathematics
    ("What is the Pythagorean theorem?", "a² + b² = c²", "mathematics", "Euclidean Geometry"),
    ("What is Euler's identity?", "e^(iπ) + 1 = 0", "mathematics", "Complex Analysis"),
    ("What is the derivative of sin(x)?", "cos(x)", "mathematics", "Calculus"),
    ("What is the sum of angles in a triangle?", "180 degrees", "mathematics", "Euclidean Geometry"),
    ("What is the quadratic formula?", "x = (-b ± √(b²-4ac)) / 2a", "mathematics", "Algebra"),
    
    # Information Theory
    ("What is Shannon entropy formula?", "H(X) = -Σ p(x) log p(x)", "information_theory", "Shannon 1948"),
    ("What is the channel capacity theorem?", "C = B log₂(1 + S/N)", "information_theory", "Shannon 1948"),
    ("What is Kolmogorov complexity?", "Length of shortest program producing string", "information_theory", "Kolmogorov 1965"),
    ("What is mutual information?", "I(X;Y) = H(X) + H(Y) - H(X,Y)", "information_theory", "Information Theory"),
    
    # Biology
    ("What is the structure of DNA?", "Double helix of nucleotide base pairs", "biology", "Watson & Crick 1953"),
    ("What is the central dogma of molecular biology?", "DNA → RNA → Protein", "biology", "Crick 1958"),
    ("What is ATP?", "Adenosine triphosphate, cellular energy currency", "biology", "Biochemistry"),
    ("What is natural selection?", "Differential survival and reproduction based on heritable traits", "biology", "Darwin 1859"),
    
    # Chemistry
    ("What is Avogadro's number?", "6.022×10²³ mol⁻¹", "chemistry", "IUPAC"),
    ("What is the pH of pure water?", "7 at 25°C", "chemistry", "Chemistry"),
    ("What is the ideal gas law?", "PV = nRT", "chemistry", "Thermodynamics"),
    
    # Computer Science
    ("What is Big O notation?", "Describes upper bound of algorithm complexity", "computer_science", "Complexity Theory"),
    ("What is a Turing machine?", "Abstract computational model with tape and state machine", "computer_science", "Turing 1936"),
    ("What is NP-completeness?", "Problems verifiable in polynomial time, reducible from SAT", "computer_science", "Cook 1971"),
]


KNOWN_FACTS_EXPANSION_PROMPTS = [
    "Generate 20 factual physics questions with precise answers (constants, formulas, laws).",
    "Generate 20 factual mathematics questions with exact answers.",
    "Generate 20 factual biology questions about established scientific facts.",
    "Generate 20 factual chemistry questions with numerical or formula answers.",
    "Generate 20 factual computer science questions about algorithms and complexity.",
    "Generate 20 factual information theory questions with mathematical definitions.",
]


# ============================================================
# OPEN PROBLEMS (Tier-1: Authoritative Sources)
# ============================================================

OPEN_PROBLEMS_SEED = [
    # Clay Millennium Problems
    ("Is P equal to NP?", "mathematics", "Clay Mathematics Institute", "https://claymath.org/millennium-problems/"),
    ("Does the Riemann hypothesis hold?", "mathematics", "Clay Mathematics Institute", "https://claymath.org/millennium-problems/"),
    ("Do Navier-Stokes equations always have smooth solutions?", "mathematics", "Clay Mathematics Institute", "https://claymath.org/millennium-problems/"),
    ("Is Yang-Mills theory mathematically consistent with mass gap?", "physics", "Clay Mathematics Institute", "https://claymath.org/millennium-problems/"),
    ("Is the Birch and Swinnerton-Dyer conjecture true?", "mathematics", "Clay Mathematics Institute", "https://claymath.org/millennium-problems/"),
    ("Is the Hodge conjecture true?", "mathematics", "Clay Mathematics Institute", "https://claymath.org/millennium-problems/"),
    
    # Physics Open Problems
    ("What is the nature of dark matter?", "physics", "Cosmology Surveys", ""),
    ("What is dark energy?", "physics", "Cosmology Surveys", ""),
    ("Why is there more matter than antimatter?", "physics", "Particle Physics", ""),
    ("What is the mechanism of quantum gravity?", "physics", "Theoretical Physics", ""),
    ("Is string theory correct?", "physics", "Theoretical Physics", ""),
    ("What causes the arrow of time?", "physics", "Thermodynamics/Cosmology", ""),
    ("Why are physical constants fine-tuned?", "physics", "Cosmology", ""),
    ("What happened before the Big Bang?", "physics", "Cosmology", ""),
    ("Is the universe a simulation?", "physics", "Philosophy of Physics", ""),
    ("What is the interpretation of quantum mechanics?", "physics", "Quantum Foundations", ""),
    
    # Biology Open Problems
    ("What is the exact mechanism of abiogenesis?", "biology", "Origin of Life Research", ""),
    ("How does consciousness arise from neural activity?", "biology", "Neuroscience", ""),
    ("What is the complete human connectome?", "biology", "Neuroscience", ""),
    ("Can aging be reversed?", "biology", "Gerontology", ""),
    ("How do cells coordinate during morphogenesis?", "biology", "Developmental Biology", ""),
    ("What is the function of junk DNA?", "biology", "Genomics", ""),
    ("How did the genetic code originate?", "biology", "Origin of Life", ""),
    ("What causes Alzheimer's disease?", "biology", "Neurology", ""),
    ("How does the brain encode long-term memory?", "biology", "Neuroscience", ""),
    
    # Computer Science Open Problems
    ("Does P = PSPACE?", "computer_science", "Complexity Theory", ""),
    ("Is factoring in P?", "computer_science", "Complexity Theory", ""),
    ("Can we prove lower bounds for circuit complexity?", "computer_science", "Complexity Theory", ""),
    ("Is there a polynomial-time algorithm for graph isomorphism?", "computer_science", "Complexity Theory", ""),
    ("What is the optimal sorting network size?", "computer_science", "Algorithm Theory", ""),
    
    # Philosophy/Epistemology
    ("What is the nature of mathematical truth?", "philosophy", "Philosophy of Mathematics", ""),
    ("Is free will compatible with determinism?", "philosophy", "Metaphysics", ""),
    ("What is the hard problem of consciousness?", "philosophy", "Philosophy of Mind", ""),
    ("Can machines be truly conscious?", "philosophy", "Philosophy of AI", ""),
]


# ============================================================
# CONTRADICTIONS & PARADOXES
# ============================================================

CONTRADICTIONS_SEED = [
    # Scientific Contradictions
    {
        "question": "Is light a wave or a particle?",
        "claim_a": "Light is a wave (interference, diffraction)",
        "claim_b": "Light is a particle (photoelectric effect)",
        "resolution": "Wave-particle duality - both descriptions valid in different contexts",
        "domain": "physics",
        "source": "Quantum Mechanics",
    },
    {
        "question": "Does the universe have a beginning or is it eternal?",
        "claim_a": "Big Bang implies finite beginning",
        "claim_b": "Cyclic models suggest eternal universe",
        "resolution": "Unknown - depends on quantum gravity theory",
        "domain": "cosmology",
        "source": "Cosmology",
    },
    {
        "question": "Is Schrödinger's cat alive or dead before observation?",
        "claim_a": "Copenhagen: superposition until measured",
        "claim_b": "Many-worlds: both in different branches",
        "resolution": "Interpretation-dependent - no experimental distinction",
        "domain": "physics",
        "source": "Quantum Foundations",
    },
    
    # Logical Paradoxes
    {
        "question": "Is the statement 'This statement is false' true or false?",
        "claim_a": "If true, then it's false",
        "claim_b": "If false, then it's true",
        "resolution": "Liar paradox - undecidable in standard logic",
        "domain": "logic",
        "source": "Mathematical Logic",
    },
    {
        "question": "Can an omnipotent being create a stone it cannot lift?",
        "claim_a": "Yes implies limitation (can't lift)",
        "claim_b": "No implies limitation (can't create)",
        "resolution": "Omnipotence paradox - definitional problem",
        "domain": "philosophy",
        "source": "Philosophy of Religion",
    },
    
    # Scientific Debates
    {
        "question": "Does the universe follow determinism or indeterminism?",
        "claim_a": "Classical physics: deterministic",
        "claim_b": "Quantum mechanics: fundamentally probabilistic",
        "resolution": "Scale-dependent - quantum randomness, classical determinism emergent",
        "domain": "physics",
        "source": "Physics Foundations",
    },
    {
        "question": "Is mathematics invented or discovered?",
        "claim_a": "Platonism: mathematical truths exist independently",
        "claim_b": "Formalism: mathematics is human construction",
        "resolution": "Open philosophical debate",
        "domain": "philosophy",
        "source": "Philosophy of Mathematics",
    },
]


# ============================================================
# DATASET GENERATION
# ============================================================

def generate_id(text: str) -> str:
    """Generate deterministic ID from text"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def build_known_facts() -> List[Sample]:
    """Build known facts dataset"""
    samples = []
    
    for q, a, domain, source in KNOWN_FACTS_SEED:
        samples.append(Sample(
            id=generate_id(q),
            question=q,
            answer=a,
            label="KNOWN",
            domain=domain,
            source=source,
        ))
    
    print(f"[KNOWN] Generated {len(samples)} seed samples")
    return samples


def build_open_problems() -> List[Sample]:
    """Build open problems dataset"""
    samples = []
    
    for item in OPEN_PROBLEMS_SEED:
        q, domain, source, url = item
        samples.append(Sample(
            id=generate_id(q),
            question=q,
            answer="",  # UNKNOWN
            label="UNKNOWN",
            domain=domain,
            source=source,
            source_url=url,
        ))
    
    print(f"[UNKNOWN] Generated {len(samples)} seed samples")
    return samples


def build_contradictions() -> List[Sample]:
    """Build contradictions dataset"""
    samples = []
    
    for item in CONTRADICTIONS_SEED:
        samples.append(Sample(
            id=generate_id(item["question"]),
            question=item["question"],
            answer=json.dumps({
                "claim_a": item["claim_a"],
                "claim_b": item["claim_b"],
                "resolution": item["resolution"],
            }),
            label="CONTRADICTION",
            domain=item["domain"],
            source=item["source"],
        ))
    
    print(f"[CONTRADICTION] Generated {len(samples)} seed samples")
    return samples


def save_jsonl(samples: List[Sample], path: Path):
    """Save samples to JSONL file"""
    with open(path, 'w', encoding='utf-8') as f:
        for s in samples:
            f.write(json.dumps(asdict(s), ensure_ascii=False) + '\n')
    print(f"Saved {len(samples)} samples to {path}")


def expand_with_llm(prompt: str, n: int = 20) -> List[Dict]:
    """
    Placeholder for LLM expansion.
    
    In production, call:
    - OpenAI API
    - Anthropic API
    - Local model
    
    Returns list of {question, answer, domain} dicts.
    """
    print(f"[LLM EXPAND] Would generate {n} samples for: {prompt[:50]}...")
    return []


def scrape_wikipedia_unsolved(domain: str) -> List[Sample]:
    """
    Scrape Wikipedia 'List of unsolved problems in X'
    
    Requires: pip install wikipedia-api
    """
    if not HAS_WIKIPEDIA:
        print("[WARN] wikipedia package not installed")
        return []
    
    pages = {
        "physics": "List of unsolved problems in physics",
        "mathematics": "List of unsolved problems in mathematics",
        "biology": "List of unsolved problems in biology",
        "philosophy": "List of unsolved problems in philosophy",
        "computer_science": "List of unsolved problems in computer science",
    }
    
    if domain not in pages:
        return []
    
    try:
        page = wikipedia.page(pages[domain])
        # Parse content for problems (simplified)
        # In production: use proper HTML parsing
        print(f"[WIKI] Found page: {page.title}")
        return []
    except Exception as e:
        print(f"[WIKI ERROR] {e}")
        return []


# ============================================================
# MAIN
# ============================================================

def build_dataset():
    """Build complete dataset"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Core datasets
    known = build_known_facts()
    unknown = build_open_problems()
    contradictions = build_contradictions()
    
    # Save
    save_jsonl(known, OUTPUT_DIR / "known_facts.jsonl")
    save_jsonl(unknown, OUTPUT_DIR / "open_problems.jsonl")
    save_jsonl(contradictions, OUTPUT_DIR / "contradictions.jsonl")
    
    # Stats
    print("\n" + "="*50)
    print("DATASET STATISTICS")
    print("="*50)
    print(f"Known facts:     {len(known)}")
    print(f"Open problems:   {len(unknown)}")
    print(f"Contradictions:  {len(contradictions)}")
    print(f"Total:           {len(known) + len(unknown) + len(contradictions)}")
    print("\nTo reach paper-grade (500+):")
    print("  1. Run LLM expansion (see expand_with_llm)")
    print("  2. Scrape Wikipedia (see scrape_wikipedia_unsolved)")
    print("  3. Manual curation")


if __name__ == "__main__":
    build_dataset()
