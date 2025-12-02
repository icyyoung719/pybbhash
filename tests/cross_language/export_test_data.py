#!/usr/bin/env python3
"""Export test data and MPHF binary for C++ compatibility testing.

Reads test keys from test_keys.csv, builds MPHF, and exports:
1. Binary MPHF file (test_data_py.mphf)
2. Hash results CSV (test_data_py_hashes.csv) - for comparison with C++
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


def main():
    # Ensure out directory exists and load test keys from out/
    os.makedirs('out', exist_ok=True)
    # Load test keys from CSV
    keys_file = os.path.join('out', 'test_keys.csv')
    if not os.path.exists(keys_file):
        print(f"[ERROR] {keys_file} not found!")
        print(f"  Please run: python generate_test_keys.py")
        return 1

    test_keys = load_test_keys(keys_file)
    print(f"[OK] Loaded {len(test_keys)} test keys from {keys_file}")
    
    print(f"\nBuilding Python MPHF...")
    
    # Build MPHF with gamma=2.0 (same as C++ default)
    mph = mphf(n=len(test_keys), input_range=test_keys, gamma=2.0)
    
    # Save binary file into out/
    binary_file = os.path.join('out', 'test_data_py.mphf')
    mph.save(binary_file)
    print(f"[OK] Saved binary to: {binary_file}")

    # Save test keys and their hash values to CSV for comparison with C++ (into out/)
    hash_csv_file = os.path.join('out', 'test_data_py_hashes.csv')
    with open(hash_csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['key', 'hash_value'])
        for key in test_keys:
            hash_val = mph.lookup(key)
            writer.writerow([key, hash_val])
    
    print(f"[OK] Saved hash results to: {hash_csv_file}")
    
    # Print some statistics
    print(f"\nMPHF Statistics:")
    print(f"  Number of keys: {mph._nelem}")
    print(f"  Gamma: {mph._gamma}")
    print(f"  Number of levels: {mph._nb_levels}")
    print(f"  Last bitset rank: {mph._lastbitsetrank}")
    print(f"  Final hash size: {len(mph._final_hash)}")
    
    # Test a few lookups
    print(f"\nSample lookups:")
    for i in [0, len(test_keys)//2, len(test_keys)-1]:
        key = test_keys[i]
        print(f"  lookup({key}) = {mph.lookup(key)}")
    
    print(f"\n[OK] Python export complete!")
    return 0


if __name__ == "__main__":
    main()
