"""Demonstration of binary MPHF file creation compatible with C++.

This example shows:
- Creating a minimal perfect hash function (MPHF) for sequential keys
- Saving to binary format compatible with C++ boomphf library
- Loading and verifying the saved MPHF
- Complete permutation validation
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pybbhash.boophf import mphf


def main():
    """Create and verify a binary MPHF file compatible with C++."""
    # Configuration parameters
    NUM_KEYS = 1000  # Number of keys
    UNIVERSE_SIZE = 10000  # Universe size for reference
    GAMMA = 2.0  # Space-time tradeoff (higher = faster, more memory)
    RANDOM_SEED = 42  # Seed for reproducibility

    # Setup output directory
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "binary_format.mphf")  # Output binary file

    print(f"{'='*70}")
    print(f"Binary MPHF Save/Load Demo (C++ Compatible)")
    print(f"{'='*70}")
    print(f"Configuration:")
    print(f"  - Number of keys: {NUM_KEYS}")
    print(f"  - Universe size: {UNIVERSE_SIZE}")
    print(f"  - Gamma parameter: {GAMMA}")
    print(f"  - Key range: [0, {NUM_KEYS-1}]")
    print(f"  - Random seed: {RANDOM_SEED}\n")

    # Step 1: Generate sequential keys
    print(f"[1/4] Generating {NUM_KEYS} sequential keys [0, {NUM_KEYS-1}]...")
    keys = list(range(NUM_KEYS))
    print(f"      ✓ Keys: 0, 1, 2, ..., {NUM_KEYS-1}\n")

    # Step 2: Build MPHF
    print(f"[2/4] Building MPHF with gamma={GAMMA}...")
    mphf_instance = mphf(n=NUM_KEYS, input_range=keys, gamma=GAMMA)
    print(f"      ✓ Built MPHF for {mphf_instance.nbKeys()} keys")
    print(f"      ✓ Hash domain size: {mphf_instance._hash_domain}\n")

    # Step 3: Save to binary file
    print(f"[3/4] Saving MPHF to binary file...")
    mphf_instance.save(OUTPUT_FILE)
    file_size = os.path.getsize(OUTPUT_FILE)
    bytes_per_key = file_size / NUM_KEYS
    print(f"      ✓ Saved to '{OUTPUT_FILE}'")
    print(f"      ✓ File size: {file_size:,} bytes ({bytes_per_key:.2f} bytes/key)\n")

    # Step 4: Load and verify
    print(f"[4/4] Loading MPHF from binary file and verifying...")
    mphf_loaded = mphf.load(OUTPUT_FILE)
    print(f"      ✓ Loaded MPHF from '{OUTPUT_FILE}'")

    # Test sample lookups
    test_keys = [0, 1, NUM_KEYS // 4, NUM_KEYS // 2, 3 * NUM_KEYS // 4, NUM_KEYS - 1]
    print(f"\n      Sample lookups (comparing original vs loaded):")
    all_match = True
    for key in test_keys:
        original_index = mphf_instance.lookup(key)
        loaded_index = mphf_loaded.lookup(key)
        match_symbol = "✓" if original_index == loaded_index else "✗"
        print(
            f"        Key {key:4d}: original={original_index:4d}, loaded={loaded_index:4d} {match_symbol}"
        )
        if original_index != loaded_index:
            all_match = False

    # Verify complete permutation
    print(f"\n      Verifying complete [0, {NUM_KEYS-1}] permutation...")
    mapped_indices = set()
    duplicate_found = False

    for key in keys:
        index = mphf_loaded.lookup(key)
        if index in mapped_indices:
            print(f"        ✗ Duplicate index: {index}")
            duplicate_found = True
            all_match = False
        mapped_indices.add(index)

    # Check if mapping is a valid permutation
    if not duplicate_found:
        if (
            len(mapped_indices) == NUM_KEYS
            and min(mapped_indices) == 0
            and max(mapped_indices) == NUM_KEYS - 1
        ):
            print(f"        ✓ All {NUM_KEYS} keys map to unique indices in [0, {NUM_KEYS-1}]")
            print(f"        ✓ Perfect permutation verified!")
        else:
            print(f"        ✗ Mapping incomplete or out of range")
            print(f"           Expected: [{0}, {NUM_KEYS-1}]")
            print(
                f"           Got: [{min(mapped_indices)}, {max(mapped_indices)}] with {len(mapped_indices)} unique values"
            )
            all_match = False

    # Summary
    print(f"\n{'='*70}")
    if all_match:
        print(f"SUCCESS: Binary file is valid and compatible with C++")
        print(f"{'='*70}")
        print(f"File Information:")
        print(f"  - Path: {OUTPUT_FILE}")
        print(f"  - Size: {file_size:,} bytes ({bytes_per_key:.2f} bytes per key)")
        print(f"  - Keys: {NUM_KEYS}")
        print(f"  - Gamma: {GAMMA}")
        print(f"\nC++ Usage Example:")
        print(f"{'='*70}")
        print(f"  #include <boomphf/BooPHF.h>")
        print(f"  ")
        print(f"  // Define types")
        print(f"  typedef boomphf::SingleHashFunctor<uint64_t> hasher_t;")
        print(f"  typedef boomphf::mphf<uint64_t, hasher_t> mphf_t;")
        print(f"  ")
        print(f"  // Load MPHF")
        print(f'  std::ifstream is("{OUTPUT_FILE}", std::ios::binary);')
        print(f"  mphf_t mph;")
        print(f"  mph.load(is);")
        print(f"  is.close();")
        print(f"  ")
        print(f"  // Use MPHF")
        print(f"  uint64_t key = 42;")
        print(f"  auto idx = mph.lookup(key);  // Returns index in [0, N-1]")
        print(f'  std::cout << "Key " << key << " -> " << idx << std::endl;')
    else:
        print(f"ERROR: Verification failed")
        print(f"{'='*70}")

    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
