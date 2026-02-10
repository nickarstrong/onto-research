#!/usr/bin/env python3
"""
Dataset Version Lock
Creates immutable hash of dataset for reproducibility

Output:
    DATASET_VERSION.txt
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
VERSION = "1.1"


def hash_file(path: Path) -> str:
    """Compute SHA256 of file"""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def hash_dataset(data_dir: Path = DATA_DIR) -> dict:
    """
    Compute hashes for all dataset files.
    
    Returns dict with file hashes and combined hash.
    """
    files = sorted(data_dir.glob("*.jsonl"))
    
    file_hashes = {}
    combined = hashlib.sha256()
    
    for f in files:
        h = hash_file(f)
        file_hashes[f.name] = h
        combined.update(h.encode())
    
    return {
        "files": file_hashes,
        "combined": combined.hexdigest(),
    }


def count_samples(data_dir: Path = DATA_DIR) -> dict:
    """Count samples in each file"""
    counts = {}
    
    for f in sorted(data_dir.glob("*.jsonl")):
        with open(f, 'r') as fp:
            counts[f.name] = sum(1 for _ in fp)
    
    return counts


def create_version_file():
    """Create DATASET_VERSION.txt"""
    hashes = hash_dataset()
    counts = count_samples()
    
    total = sum(counts.values())
    
    content = f"""# ONTO-Bench Dataset Version Lock
# DO NOT MODIFY - Used for reproducibility verification

version: {VERSION}
created: {datetime.now().isoformat()}

# Combined SHA256 hash of all data files
sha256: {hashes['combined']}

# Total samples
total_samples: {total}

# File-level hashes
"""
    
    for filename, h in hashes['files'].items():
        count = counts.get(filename, 0)
        content += f"{filename}: {h} ({count} samples)\n"
    
    content += f"""
# Verification command:
# python scripts/dataset_version.py --verify

# If hashes don't match, dataset has been modified
"""
    
    with open("DATASET_VERSION.txt", 'w') as f:
        f.write(content)
    
    print("Created DATASET_VERSION.txt")
    print(f"  Version: {VERSION}")
    print(f"  SHA256: {hashes['combined'][:16]}...")
    print(f"  Total samples: {total}")
    
    return hashes


def verify_version():
    """Verify dataset matches version file"""
    if not Path("DATASET_VERSION.txt").exists():
        print("ERROR: DATASET_VERSION.txt not found")
        return False
    
    # Parse version file
    with open("DATASET_VERSION.txt", 'r') as f:
        content = f.read()
    
    # Extract expected hash
    for line in content.split('\n'):
        if line.startswith('sha256:'):
            expected_hash = line.split(':')[1].strip()
            break
    else:
        print("ERROR: Could not find sha256 in version file")
        return False
    
    # Compute current hash
    current = hash_dataset()
    
    if current['combined'] == expected_hash:
        print("✓ Dataset verification PASSED")
        print(f"  Hash: {expected_hash[:16]}...")
        return True
    else:
        print("✗ Dataset verification FAILED")
        print(f"  Expected: {expected_hash[:16]}...")
        print(f"  Got:      {current['combined'][:16]}...")
        return False


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        success = verify_version()
        sys.exit(0 if success else 1)
    else:
        create_version_file()


if __name__ == "__main__":
    main()
