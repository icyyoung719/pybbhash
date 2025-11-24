#!/usr/bin/env python3
"""Export test data and MPHF binary for C++ compatibility testing."""

import sys
import os
import csv

# Add parent directory to import pybbhash
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pybbhash.boophf import mphf


def main():
    # Generate test keys - simple sequential keys for easy verification
    test_keys = list(range(1000, 2000))  # 1000 keys from 1000-1999
    
    print(f"Generating MPHF for {len(test_keys)} keys...")
    
    # Build MPHF with gamma=2.0 (same as C++ default)
    mph = mphf(n=len(test_keys), input_range=test_keys, gamma=2.0)
    
    # Save binary file
    binary_file = "test_data_py.mphf"
    mph.save(binary_file)
    print(f"✓ Saved binary to: {binary_file}")
    
    # Save test keys and their hash values to CSV for verification
    csv_file = "test_data_py.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['key', 'hash_value'])
        for key in test_keys:
            hash_val = mph.lookup(key)
            writer.writerow([key, hash_val])
    
    print(f"✓ Saved test data to: {csv_file}")
    
    # Print some statistics
    print(f"\nMPHF Statistics:")
    print(f"  Number of keys: {mph._nelem}")
    print(f"  Gamma: {mph._gamma}")
    print(f"  Number of levels: {mph._nb_levels}")
    print(f"  Last bitset rank: {mph._lastbitsetrank}")
    print(f"  Final hash size: {len(mph._final_hash)}")
    
    # Test a few lookups
    print(f"\nSample lookups:")
    for key in [1000, 1500, 1999]:
        print(f"  lookup({key}) = {mph.lookup(key)}")
    
    print(f"\n✓ Export complete!")


if __name__ == "__main__":
    main()
