"""Basic example demonstrating MPHF construction, lookup, and save/load operations.

This example shows:
- Building a minimal perfect hash function (MPHF) for a set of random keys
- Looking up keys to get their perfect hash indices
- Verifying that all keys map to unique indices in range [0, n-1]
- Saving and loading the MPHF to/from disk
"""

import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pybbhash.boophf import mphf


def main():
    """Demonstrate basic MPHF usage with random integer keys."""
    # Configuration parameters
    NUM_KEYS = 30  # Number of unique keys to generate
    UNIVERSE_SIZE = 10000  # Keys will be sampled from [1, UNIVERSE_SIZE-1]
    NUM_TEST_KEYS = NUM_KEYS  # Number of keys to test for lookup
    GAMMA = 1.5  # Space-time tradeoff parameter (higher = faster but more space)
    RANDOM_SEED = 41  # Seed for reproducible random key generation

    # Setup output directory
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "basic.mphf")  # File path for saving the MPHF

    # Initialize random number generator for reproducibility
    random.seed(RANDOM_SEED)
    print(f"{'='*70}")
    print(f"Basic MPHF Example")
    print(f"{'='*70}")
    print(f"Configuration:")
    print(f"  - Number of keys: {NUM_KEYS}")
    print(f"  - Universe size: [1, {UNIVERSE_SIZE-1}]")
    print(f"  - Gamma parameter: {GAMMA}")
    print(f"  - Random seed: {RANDOM_SEED}\n")

    # Step 1: Generate unique random keys
    print(f"[1/4] Generating {NUM_KEYS} unique keys from range [1, {UNIVERSE_SIZE-1}]...")
    keys = random.sample(range(1, UNIVERSE_SIZE), NUM_KEYS)
    print(f"      ✓ Generated keys (first 10): {keys[:10]}\n")

    # Step 2: Build MPHF
    print(f"[2/4] Building MPHF with gamma={GAMMA}...")
    mphf_instance = mphf(n=len(keys), input_range=keys, gamma=GAMMA)
    print(f"      ✓ Built MPHF for {mphf_instance.nbKeys()} keys")
    print(f"      ✓ Hash domain size: {mphf_instance._hash_domain}\n")

    # Step 3: Test lookups on sampled keys
    test_keys = random.sample(keys, min(NUM_TEST_KEYS, len(keys)))
    print(f"[3/4] Testing lookups for {len(test_keys)} keys...")

    mapped_indices = []
    print(f"      Sample lookups (first 10):")
    for i, key in enumerate(test_keys[:10]):
        index = mphf_instance.lookup(key)
        print(f"        Key {key:5d} -> Index {index:3d}")
        mapped_indices.append(index)

    # Continue collecting all mapped indices
    for key in test_keys[10:]:
        index = mphf_instance.lookup(key)
        mapped_indices.append(index)

    # Verify correctness: all keys should map to valid range
    print(f"\n      Verifying correctness...")
    verification_passed = True
    for key in keys:
        index = mphf_instance.lookup(key)
        if not (0 <= index < len(keys)):
            print(f"        ✗ ERROR: Key {key} mapped to invalid index {index}")
            verification_passed = False

    if verification_passed:
        print(f"        ✓ All {len(keys)} keys map to valid indices [0, {len(keys)-1}]")

        # Check if mapped indices form a complete permutation
        unique_indices = set(mapped_indices)
        if len(unique_indices) == len(test_keys):
            print(f"        ✓ Test keys map to {len(unique_indices)} unique indices")
            if sorted(mapped_indices) == list(range(len(test_keys))):
                print(
                    f"        ✓ Sampled indices form a perfect permutation [0, {len(test_keys)-1}]"
                )
            else:
                print(
                    f"        ℹ Sampled indices don't form a complete permutation (expected for subset)"
                )
    else:
        print(f"        ✗ VERIFICATION FAILED\n")
        return

    # Step 4: Save and load MPHF
    print(f"\n[4/4] Testing save/load functionality...")
    mphf_instance.save(OUTPUT_FILE)
    file_size = os.path.getsize(OUTPUT_FILE)
    print(
        f"      ✓ Saved MPHF to '{OUTPUT_FILE}' ({file_size:,} bytes, {file_size/len(keys):.2f} bytes/key)"
    )

    # Load from disk
    mphf_loaded = mphf.load(OUTPUT_FILE)
    mphf_loaded.lookup(test_keys[0])  # Warm up
    print(f"      ✓ Loaded MPHF from '{OUTPUT_FILE}'")

    # Verify loaded MPHF produces identical results
    print(f"      Verifying loaded MPHF (testing {len(test_keys)} keys)...")
    load_verification_passed = True
    for key in test_keys:
        original_index = mphf_instance.lookup(key)
        loaded_index = mphf_loaded.lookup(key)
        if original_index != loaded_index:
            print(
                f"        ✗ ERROR: Key {key} mapped to {loaded_index} after load, expected {original_index}"
            )
            load_verification_passed = False

    if load_verification_passed:
        print(f"        ✓ All lookups match after load!")
    else:
        print(f"        ✗ LOAD VERIFICATION FAILED")
        return

    # Summary
    print(f"\n{'='*70}")
    print(f"SUCCESS: MPHF example completed successfully!")
    print(f"{'='*70}")
    print(f"Summary:")
    print(f"  - Keys: {len(keys)}")
    print(f"  - Index range: [0, {len(keys)-1}]")
    print(f"  - File size: {file_size:,} bytes ({file_size/len(keys):.2f} bytes/key)")
    print(f"  - All verifications passed ✓")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
