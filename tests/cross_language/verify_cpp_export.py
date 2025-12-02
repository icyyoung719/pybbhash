#!/usr/bin/env python3
"""Verify C++-generated MPHF binary can be loaded in Python.

This script:
1. Loads test keys from test_keys.csv
2. Loads C++ MPHF binary (test_data_cpp.mphf)
3. Verifies binary compatibility (all keys can be looked up)
4. Compares hash values with C++ results (optional observation)
"""

import sys
import os
import csv

# Add parent directory to import pybbhash
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pybbhash.boophf import mphf


def load_test_keys(csv_file):
    """Load test keys from CSV file."""
    keys = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            keys.append(int(row['key']))
    return keys


def load_hash_results(csv_file):
    """Load hash results from CSV file."""
    hashes = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = int(row['key'])
            hash_val = int(row['hash_value'])
            hashes[key] = hash_val
    return hashes


def main():
    print("\n=== Test 4: Load C++ Binary (Python Side) ===\n")
    
    # Ensure out directory used and load test keys
    keys_file = os.path.join('out', 'test_keys.csv')
    if not os.path.exists(keys_file):
        print(f"[ERROR] Test keys file not found: {keys_file}")
        print(f"  Please run: python generate_test_keys.py")
        return 1

    test_keys = load_test_keys(keys_file)
    print(f"[OK] Loaded {len(test_keys)} test keys")

    # Load MPHF from C++ binary (from out/)
    binary_file = os.path.join('out', 'test_data_cpp.mphf')
    if not os.path.exists(binary_file):
        print(f"[ERROR] Binary file not found: {binary_file}")
        print(f"  Please run C++ test first: ./test_compatibility")
        return 1

    mph = mphf.load(binary_file)
    print(f"[OK] Loaded MPHF from C++ binary")
    
    # Verify MPHF properties
    print(f"\nVerifying MPHF properties...")
    
    hash_values = set()
    errors = 0
    
    for key in test_keys:
        hash_val = mph.lookup(key)
        
        # Check range
        if hash_val < 0 or hash_val >= len(test_keys):
            print(f"✗ Out of range for key {key}: {hash_val} not in [0, {len(test_keys)-1}]")
            errors += 1
            if errors >= 10:
                print("  (stopping after 10 errors)")
                break
        else:
            hash_values.add(hash_val)
    
    if errors > 0:
        print(f"\n✗ Binary compatibility test failed")
        return 1
    
    # Check uniqueness
    if len(hash_values) != len(test_keys):
        print(f"✗ Hash collision detected!")
        print(f"  Expected {len(test_keys)} unique hashes, got {len(hash_values)}")
        return 1
    
    print(f"✓ All {len(test_keys)} keys can be looked up")
    print(f"✓ All hash values in valid range [0, {len(test_keys)-1}]")
    print(f"✓ All hash values are unique (perfect hash)")
    print(f"✓ Binary compatibility verified!")
    
    # Optional: Compare with C++ hash values (from out/)
    hash_csv_file = os.path.join('out', 'test_data_cpp_hashes.csv')
    if os.path.exists(hash_csv_file):
        print(f"\n--- Optional: Comparing with C++ hash values ---")
        cpp_hashes = load_hash_results(hash_csv_file)
        
        matches = 0
        mismatches = 0
        samples_shown = 0
        
        for key in test_keys:
            py_hash = mph.lookup(key)
            cpp_hash = cpp_hashes.get(key)
            
            if cpp_hash is None:
                continue
            
            if py_hash == cpp_hash:
                matches += 1
                if samples_shown < 3:
                    print(f"  Match:     key={key} → hash={py_hash}")
                    samples_shown += 1
            else:
                mismatches += 1
                if samples_shown < 10:
                    print(f"  Mismatch:  key={key} → Python={py_hash}, C++={cpp_hash}")
                    samples_shown += 1
        
        print(f"\nComparison with C++ hashes:")
        print(f"  Matches:    {matches} ({100.0 * matches / len(test_keys):.1f}%)")
        print(f"  Mismatches: {mismatches} ({100.0 * mismatches / len(test_keys):.1f}%)")
        
        if matches == len(test_keys):
            print(f"  → Python and C++ produce identical hash assignments!")
        elif mismatches == len(test_keys):
            print(f"  → Python and C++ produce different hash assignments (expected)")
        else:
            print(f"  → Partial match (some keys have same assignments)")
    
    print(f"\n[OK] Python verification complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
