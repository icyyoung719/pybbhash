#!/usr/bin/env python3
"""Verify C++-generated MPHF binary can be loaded in Python."""

import sys
import os
import csv

# Add parent directory to import pybbhash
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pybbhash.boophf import mphf


def main():
    print("\n=== Python verification of C++ export ===\n")
    
    # Load keys from CSV (we only need the keys, not hash values)
    csv_file = "test_data_cpp.csv"
    
    if not os.path.exists(csv_file):
        print(f"✗ CSV file not found: {csv_file}")
        print("  Please run the C++ test first to generate the file.")
        return False
    
    keys = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            keys.append(int(row['key']))
    
    print(f"✓ Loaded {len(keys)} test keys from CSV")
    
    # Load MPHF from C++ binary
    binary_file = "test_data_cpp.mphf"
    if not os.path.exists(binary_file):
        print(f"✗ Binary file not found: {binary_file}")
        print("  Please run the C++ test first to generate the file.")
        return False
    
    mph = mphf.load(binary_file)
    print(f"✓ Loaded MPHF from C++ binary")
    
    # Print MPHF info
    print(f"\nMPHF Statistics:")
    print(f"  Number of keys: {mph._nelem}")
    print(f"  Gamma: {mph._gamma}")
    print(f"  Number of levels: {mph._nb_levels}")
    print(f"  Last bitset rank: {mph._lastbitsetrank}")
    print(f"  Final hash size: {len(mph._final_hash)}")
    
    # Verify MPHF properties:
    # 1. All keys can be looked up without errors
    # 2. All hash values are in range [0, n-1]
    # 3. All hash values are unique (perfect hash)
    print(f"\nVerifying MPHF properties...")
    
    hash_values = []
    lookup_errors = 0
    out_of_range = 0
    
    for key in keys:
        hash_val = mph.lookup(key)
        
        if hash_val == -1:
            print(f"✗ Lookup error for key {key}: returned -1")
            lookup_errors += 1
            if lookup_errors >= 10:
                print("  (stopping after 10 errors)")
                break
        elif hash_val < 0 or hash_val >= len(keys):
            print(f"✗ Out of range for key {key}: {hash_val} not in [0, {len(keys)-1}]")
            out_of_range += 1
            if out_of_range >= 10:
                print("  (stopping after 10 errors)")
                break
        else:
            hash_values.append(hash_val)
    
    if lookup_errors > 0 or out_of_range > 0:
        print(f"\n{'='*50}")
        print(f"✗ MPHF verification failed!")
        print(f"  Lookup errors: {lookup_errors}")
        print(f"  Out of range: {out_of_range}")
        return False
    
    # Check for uniqueness (no collisions)
    unique_hashes = len(set(hash_values))
    if unique_hashes != len(hash_values):
        print(f"\n{'='*50}")
        print(f"✗ Hash collision detected!")
        print(f"  Expected {len(hash_values)} unique hashes, got {unique_hashes}")
        return False
    
    # Print results
    print(f"✓ All {len(keys)} keys can be looked up")
    print(f"✓ All hash values in valid range [0, {len(keys)-1}]")
    print(f"✓ All hash values are unique (perfect hash)")
    
    print(f"\n{'='*50}")
    print(f"✓ C++ → Python binary format compatibility verified!")
    print(f"✓ MPHF properties validated successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
