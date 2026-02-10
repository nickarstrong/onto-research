#!/usr/bin/env python3
"""
Stratified Train/Test Split for ONTO-Bench
Ensures label distribution preserved in both splits

Output:
    data/train.jsonl
    data/test.jsonl
    data/split_info.json
"""

import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime

# Reproducibility
SEED = 42
random.seed(SEED)

DATA_DIR = Path("data")
TRAIN_RATIO = 0.8


def load_all_samples() -> List[Dict]:
    """Load all samples from data directory"""
    samples = []
    
    for filename in ["known_facts.jsonl", "open_problems.jsonl", "contradictions.jsonl"]:
        path = DATA_DIR / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    samples.append(json.loads(line))
    
    return samples


def stratified_split(
    samples: List[Dict],
    train_ratio: float = 0.8,
    stratify_key: str = "label"
) -> tuple:
    """
    Split samples while preserving label distribution.
    
    Args:
        samples: List of sample dicts
        train_ratio: Fraction for training set
        stratify_key: Key to stratify on
    
    Returns:
        (train_samples, test_samples)
    """
    # Group by stratify key
    groups = defaultdict(list)
    for s in samples:
        key = s.get(stratify_key, "UNKNOWN")
        groups[key].append(s)
    
    train = []
    test = []
    
    # Split each group
    for key, group_samples in groups.items():
        random.shuffle(group_samples)
        n_train = int(len(group_samples) * train_ratio)
        
        # Ensure at least 1 in each split if possible
        if n_train == 0 and len(group_samples) > 1:
            n_train = 1
        if n_train == len(group_samples) and len(group_samples) > 1:
            n_train = len(group_samples) - 1
        
        train.extend(group_samples[:n_train])
        test.extend(group_samples[n_train:])
    
    # Shuffle final splits
    random.shuffle(train)
    random.shuffle(test)
    
    return train, test


def compute_label_distribution(samples: List[Dict]) -> Dict[str, int]:
    """Compute label counts"""
    dist = defaultdict(int)
    for s in samples:
        dist[s.get("label", "UNKNOWN")] += 1
    return dict(dist)


def save_jsonl(samples: List[Dict], path: Path):
    """Save samples to JSONL"""
    with open(path, 'w', encoding='utf-8') as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')


def main():
    print("=== Stratified Train/Test Split ===")
    print(f"Seed: {SEED}")
    print(f"Train ratio: {TRAIN_RATIO}")
    print()
    
    # Load samples
    samples = load_all_samples()
    print(f"Total samples: {len(samples)}")
    
    # Original distribution
    orig_dist = compute_label_distribution(samples)
    print(f"Original distribution: {orig_dist}")
    
    # Split
    train, test = stratified_split(samples, TRAIN_RATIO)
    
    # Distributions
    train_dist = compute_label_distribution(train)
    test_dist = compute_label_distribution(test)
    
    print(f"\nTrain: {len(train)} samples")
    print(f"  Distribution: {train_dist}")
    
    print(f"\nTest: {len(test)} samples")
    print(f"  Distribution: {test_dist}")
    
    # Verify stratification
    print("\n=== Stratification Check ===")
    for label in orig_dist:
        orig_pct = orig_dist[label] / len(samples) * 100
        train_pct = train_dist.get(label, 0) / len(train) * 100 if train else 0
        test_pct = test_dist.get(label, 0) / len(test) * 100 if test else 0
        print(f"{label}: orig={orig_pct:.1f}%, train={train_pct:.1f}%, test={test_pct:.1f}%")
    
    # Save splits
    save_jsonl(train, DATA_DIR / "train.jsonl")
    save_jsonl(test, DATA_DIR / "test.jsonl")
    
    # Save split info
    split_info = {
        "seed": SEED,
        "train_ratio": TRAIN_RATIO,
        "created_at": datetime.now().isoformat(),
        "total_samples": len(samples),
        "train_count": len(train),
        "test_count": len(test),
        "train_distribution": train_dist,
        "test_distribution": test_dist,
        "original_distribution": orig_dist,
    }
    
    with open(DATA_DIR / "split_info.json", 'w') as f:
        json.dump(split_info, f, indent=2)
    
    print(f"\nSaved:")
    print(f"  {DATA_DIR / 'train.jsonl'}")
    print(f"  {DATA_DIR / 'test.jsonl'}")
    print(f"  {DATA_DIR / 'split_info.json'}")
    
    return split_info


if __name__ == "__main__":
    main()
