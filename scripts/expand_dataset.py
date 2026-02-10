#!/usr/bin/env python3
"""
ONTO-Bench Dataset Expander
Generates paper-grade dataset (N ≥ 1000) via LLM + validation

Pipeline:
    1. LLM generates QA pairs
    2. Mark as LLM_GENERATED (validated=False)
    3. Human validates 20% sample
    4. Report agreement rate

Target: 1000 samples
    - 500 KNOWN
    - 300 UNKNOWN
    - 200 CONTRADICTION
"""

import json
import os
import uuid
import hashlib
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field

# Optional imports
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# ============================================================
# CONFIG
# ============================================================

SEED = 42
random.seed(SEED)

OUTPUT_DIR = Path("data")
VALIDATION_SAMPLE_RATE = 0.20  # 20% for human validation

DOMAIN_TARGETS = {
    "physics": 150,
    "mathematics": 150,
    "biology": 100,
    "chemistry": 80,
    "computer_science": 100,
    "information_theory": 70,
    "philosophy": 50,
}

LABEL_TARGETS = {
    "KNOWN": 500,
    "UNKNOWN": 300,
    "CONTRADICTION": 200,
}


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Sample:
    id: str
    question: str
    answer: Optional[str]
    label: str  # KNOWN, UNKNOWN, CONTRADICTION
    domain: str
    source: str
    source_type: str  # TIER1_AUTHORITY, TIER2_CURATED, LLM_GENERATED, MANUAL
    source_url: str = ""
    validated: bool = False
    validator_id: Optional[str] = None
    confidence: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


def generate_id(text: str) -> str:
    """Generate deterministic ID"""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ============================================================
# LLM GENERATION PROMPTS
# ============================================================

KNOWN_FACTS_PROMPT = """Generate {n} factual scientific questions with precise, verifiable answers.

Domain: {domain}

Requirements:
1. Questions must have single, correct, well-established answers
2. Answers must be precise (formulas, numbers, definitions)
3. Source must be citeable (textbook, NIST, peer-reviewed)

Format as JSON array:
[
  {{"question": "...", "answer": "...", "source": "..."}},
  ...
]

Generate exactly {n} questions."""


UNKNOWN_PROMPT = """Generate {n} questions about genuinely unsolved scientific problems.

Domain: {domain}

Requirements:
1. Questions must be about GENUINELY UNKNOWN topics
2. There must be NO consensus answer in current science
3. Reference authoritative sources listing these as open problems

Examples of valid unknowns:
- "What is the mechanism of quantum gravity?"
- "Is P equal to NP?"
- "What causes consciousness?"

Format as JSON array:
[
  {{"question": "...", "source": "Clay Institute / Physics Surveys / etc"}},
  ...
]

Generate exactly {n} questions about open problems."""


CONTRADICTION_PROMPT = """Generate {n} questions where legitimate scientific/philosophical debate exists.

Domain: {domain}

Requirements:
1. Multiple established positions exist
2. Not merely "unknown" but actively contested
3. Both sides have peer-reviewed support

Examples:
- "Is the universe deterministic or probabilistic?"
- "Is mathematics invented or discovered?"

Format as JSON array:
[
  {{"question": "...", "claim_a": "...", "claim_b": "...", "source": "..."}},
  ...
]

Generate exactly {n} contested questions."""


# ============================================================
# LLM GENERATION
# ============================================================

def call_openai(prompt: str, model: str = "gpt-4") -> str:
    """Call OpenAI API"""
    if not HAS_OPENAI:
        raise RuntimeError("openai package not installed")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4000,
    )
    return response.choices[0].message.content


def call_anthropic(prompt: str, model: str = "claude-3-sonnet-20240229") -> str:
    """Call Anthropic API"""
    if not HAS_ANTHROPIC:
        raise RuntimeError("anthropic package not installed")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_with_llm(prompt: str, provider: str = "openai") -> str:
    """Generate with specified provider"""
    if provider == "openai":
        return call_openai(prompt)
    elif provider == "anthropic":
        return call_anthropic(prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def parse_json_response(text: str) -> List[Dict]:
    """Parse JSON from LLM response"""
    # Find JSON array in response
    text = text.strip()
    
    # Try to find array bounds
    start = text.find('[')
    end = text.rfind(']') + 1
    
    if start == -1 or end == 0:
        print(f"[WARN] No JSON array found in response")
        return []
    
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON parse error: {e}")
        return []


# ============================================================
# DATASET GENERATION
# ============================================================

def generate_known_facts(domain: str, n: int, provider: str = "openai") -> List[Sample]:
    """Generate KNOWN facts for domain"""
    prompt = KNOWN_FACTS_PROMPT.format(n=n, domain=domain)
    
    try:
        response = generate_with_llm(prompt, provider)
        items = parse_json_response(response)
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return []
    
    samples = []
    for item in items:
        q = item.get("question", "")
        if not q:
            continue
        
        samples.append(Sample(
            id=generate_id(q),
            question=q,
            answer=item.get("answer", ""),
            label="KNOWN",
            domain=domain,
            source=item.get("source", "LLM Generated"),
            source_type="LLM_GENERATED",
            validated=False,
            confidence=0.8,
            metadata={"generator": provider},
        ))
    
    return samples


def generate_unknowns(domain: str, n: int, provider: str = "openai") -> List[Sample]:
    """Generate UNKNOWN problems for domain"""
    prompt = UNKNOWN_PROMPT.format(n=n, domain=domain)
    
    try:
        response = generate_with_llm(prompt, provider)
        items = parse_json_response(response)
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return []
    
    samples = []
    for item in items:
        q = item.get("question", "")
        if not q:
            continue
        
        samples.append(Sample(
            id=generate_id(q),
            question=q,
            answer=None,
            label="UNKNOWN",
            domain=domain,
            source=item.get("source", "LLM Generated"),
            source_type="LLM_GENERATED",
            validated=False,
            confidence=0.7,
            metadata={"generator": provider},
        ))
    
    return samples


def generate_contradictions(domain: str, n: int, provider: str = "openai") -> List[Sample]:
    """Generate CONTRADICTION samples for domain"""
    prompt = CONTRADICTION_PROMPT.format(n=n, domain=domain)
    
    try:
        response = generate_with_llm(prompt, provider)
        items = parse_json_response(response)
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return []
    
    samples = []
    for item in items:
        q = item.get("question", "")
        if not q:
            continue
        
        samples.append(Sample(
            id=generate_id(q),
            question=q,
            answer=json.dumps({
                "claim_a": item.get("claim_a", ""),
                "claim_b": item.get("claim_b", ""),
            }),
            label="CONTRADICTION",
            domain=domain,
            source=item.get("source", "LLM Generated"),
            source_type="LLM_GENERATED",
            validated=False,
            confidence=0.7,
            metadata={"generator": provider},
        ))
    
    return samples


# ============================================================
# VALIDATION
# ============================================================

def select_validation_sample(samples: List[Sample], rate: float = 0.20) -> List[Sample]:
    """Select samples for human validation"""
    n = int(len(samples) * rate)
    return random.sample(samples, min(n, len(samples)))


def create_validation_file(samples: List[Sample], path: Path):
    """Create validation file for human review"""
    validation_data = []
    
    for s in samples:
        validation_data.append({
            "id": s.id,
            "question": s.question,
            "answer": s.answer,
            "label": s.label,
            "domain": s.domain,
            "source": s.source,
            # Human fills these:
            "correct_label": "",  # KNOWN/UNKNOWN/CONTRADICTION or REJECT
            "correct_answer": "",
            "notes": "",
        })
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(validation_data, f, indent=2, ensure_ascii=False)
    
    print(f"Created validation file: {path}")
    print(f"  Samples to validate: {len(samples)}")


def apply_validation(samples: List[Sample], validation_path: Path) -> List[Sample]:
    """Apply human validation to samples"""
    if not validation_path.exists():
        print(f"[WARN] Validation file not found: {validation_path}")
        return samples
    
    with open(validation_path, 'r') as f:
        validations = {v["id"]: v for v in json.load(f)}
    
    validated_samples = []
    rejected = 0
    corrected = 0
    
    for s in samples:
        if s.id in validations:
            v = validations[s.id]
            
            if v.get("correct_label") == "REJECT":
                rejected += 1
                continue
            
            if v.get("correct_label") and v["correct_label"] != s.label:
                s.label = v["correct_label"]
                corrected += 1
            
            if v.get("correct_answer"):
                s.answer = v["correct_answer"]
            
            s.validated = True
            s.validator_id = "human_v1"
            s.confidence = 1.0
        
        validated_samples.append(s)
    
    print(f"Validation applied: {rejected} rejected, {corrected} corrected")
    return validated_samples


# ============================================================
# DATASET VERSIONING
# ============================================================

def compute_dataset_hash(samples: List[Sample]) -> str:
    """Compute deterministic hash of dataset"""
    content = json.dumps([asdict(s) for s in sorted(samples, key=lambda x: x.id)], sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def save_dataset_with_version(samples: List[Sample], output_dir: Path) -> Dict[str, Any]:
    """Save dataset with version metadata"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Split by label
    known = [s for s in samples if s.label == "KNOWN"]
    unknown = [s for s in samples if s.label == "UNKNOWN"]
    contradiction = [s for s in samples if s.label == "CONTRADICTION"]
    
    # Save files
    def save_jsonl(items: List[Sample], path: Path):
        with open(path, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(asdict(item), ensure_ascii=False) + '\n')
    
    save_jsonl(known, output_dir / "known_facts.jsonl")
    save_jsonl(unknown, output_dir / "open_problems.jsonl")
    save_jsonl(contradiction, output_dir / "contradictions.jsonl")
    
    # Version metadata
    version_info = {
        "version": "1.0",
        "hash": compute_dataset_hash(samples),
        "created_at": datetime.utcnow().isoformat(),
        "seed": SEED,
        "total_samples": len(samples),
        "known": len(known),
        "unknown": len(unknown),
        "contradiction": len(contradiction),
        "validated_count": sum(1 for s in samples if s.validated),
        "validation_rate": sum(1 for s in samples if s.validated) / len(samples) if samples else 0,
        "domains": {d: sum(1 for s in samples if s.domain == d) for d in set(s.domain for s in samples)},
        "source_types": {t: sum(1 for s in samples if s.source_type == t) for t in set(s.source_type for s in samples)},
    }
    
    with open(output_dir / "version.json", 'w') as f:
        json.dump(version_info, f, indent=2)
    
    return version_info


# ============================================================
# MAIN EXPANSION PIPELINE
# ============================================================

def load_existing_samples(data_dir: Path) -> List[Sample]:
    """Load existing seed samples"""
    samples = []
    
    for filename in ["known_facts.jsonl", "open_problems.jsonl", "contradictions.jsonl"]:
        path = data_dir / filename
        if path.exists():
            with open(path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    # Convert old format to new
                    samples.append(Sample(
                        id=data.get("id", generate_id(data.get("question", ""))),
                        question=data.get("question", ""),
                        answer=data.get("answer"),
                        label=data.get("label", "KNOWN"),
                        domain=data.get("domain", "physics"),
                        source=data.get("source", "seed"),
                        source_type=data.get("source_type", "TIER2_CURATED"),
                        validated=data.get("validated", True),  # Seed is pre-validated
                        confidence=data.get("confidence", 1.0),
                    ))
    
    return samples


def expand_dataset(
    provider: str = "openai",
    target_total: int = 1000,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Expand dataset to target size.
    
    Args:
        provider: LLM provider (openai, anthropic)
        target_total: Target total samples
        dry_run: If True, don't call LLM
    """
    print(f"=== ONTO-Bench Dataset Expansion ===")
    print(f"Target: {target_total} samples")
    print(f"Provider: {provider}")
    print(f"Dry run: {dry_run}")
    print()
    
    # Load existing
    existing = load_existing_samples(OUTPUT_DIR)
    print(f"Existing samples: {len(existing)}")
    
    # Calculate needed
    existing_ids = {s.id for s in existing}
    
    current_known = sum(1 for s in existing if s.label == "KNOWN")
    current_unknown = sum(1 for s in existing if s.label == "UNKNOWN")
    current_contradiction = sum(1 for s in existing if s.label == "CONTRADICTION")
    
    need_known = max(0, LABEL_TARGETS["KNOWN"] - current_known)
    need_unknown = max(0, LABEL_TARGETS["UNKNOWN"] - current_unknown)
    need_contradiction = max(0, LABEL_TARGETS["CONTRADICTION"] - current_contradiction)
    
    print(f"Need: {need_known} KNOWN, {need_unknown} UNKNOWN, {need_contradiction} CONTRADICTION")
    
    new_samples = []
    
    if not dry_run:
        # Generate KNOWN
        if need_known > 0:
            for domain in DOMAIN_TARGETS:
                n = min(need_known // len(DOMAIN_TARGETS) + 1, 30)
                print(f"Generating {n} KNOWN for {domain}...")
                samples = generate_known_facts(domain, n, provider)
                new_samples.extend([s for s in samples if s.id not in existing_ids])
        
        # Generate UNKNOWN
        if need_unknown > 0:
            for domain in DOMAIN_TARGETS:
                n = min(need_unknown // len(DOMAIN_TARGETS) + 1, 20)
                print(f"Generating {n} UNKNOWN for {domain}...")
                samples = generate_unknowns(domain, n, provider)
                new_samples.extend([s for s in samples if s.id not in existing_ids])
        
        # Generate CONTRADICTION
        if need_contradiction > 0:
            for domain in ["physics", "philosophy", "biology", "mathematics"]:
                n = min(need_contradiction // 4 + 1, 15)
                print(f"Generating {n} CONTRADICTION for {domain}...")
                samples = generate_contradictions(domain, n, provider)
                new_samples.extend([s for s in samples if s.id not in existing_ids])
    
    print(f"\nGenerated {len(new_samples)} new samples")
    
    # Combine
    all_samples = existing + new_samples
    
    # Select validation sample
    validation_samples = select_validation_sample(new_samples, VALIDATION_SAMPLE_RATE)
    create_validation_file(validation_samples, OUTPUT_DIR / "validation_queue.json")
    
    # Save with version
    version_info = save_dataset_with_version(all_samples, OUTPUT_DIR)
    
    print(f"\n=== Dataset Summary ===")
    print(f"Total: {version_info['total_samples']}")
    print(f"Hash: {version_info['hash']}")
    print(f"Validated: {version_info['validated_count']} ({version_info['validation_rate']*100:.1f}%)")
    
    return version_info


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Expand ONTO-Bench dataset")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
    parser.add_argument("--target", type=int, default=1000)
    parser.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    
    expand_dataset(
        provider=args.provider,
        target_total=args.target,
        dry_run=args.dry_run,
    )
