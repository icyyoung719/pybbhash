"""Advanced example: MPHF for uint64 composite keys mapping to double values.

This example demonstrates a real-world use case:
- Reading composite keys from CSV (two uint32_t values per row)
- Combining two uint32_t into a single uint64_t key
- Building MPHF for efficient O(1) lookup
- Creating a compact double array indexed by MPHF
- Performing fast lookups to retrieve associated double values

Use case: Efficient coordinate-to-value mapping where coordinates are 
represented as (x, y) uint32_t pairs and need to be mapped to double values.
"""
import sys
import os
import struct
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pybbhash.boophf import mphf


def combine_uint32_to_uint64(high: int, low: int) -> int:
    """Combine two uint32_t values into a single uint64_t.
    
    Args:
        high: Upper 32 bits (uint32_t)
        low: Lower 32 bits (uint32_t)
    
    Returns:
        Combined uint64_t value
    """
    # Ensure inputs are valid uint32_t
    high = high & 0xFFFFFFFF
    low = low & 0xFFFFFFFF
    return (high << 32) | low


def split_uint64_to_uint32(value: int) -> tuple:
    """Split uint64_t value back into two uint32_t values.
    
    Args:
        value: uint64_t value
    
    Returns:
        Tuple of (high, low) uint32_t values
    """
    high = (value >> 32) & 0xFFFFFFFF
    low = value & 0xFFFFFFFF
    return high, low


def load_csv_data(csv_path: str):
    """Load composite keys and values from CSV file.
    
    CSV format: uint32_high, uint32_low, double_value
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        Tuple of (composite_keys, values) where:
        - composite_keys: list of uint64_t values
        - values: list of double values
    """
    composite_keys = []
    values = []
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue
            
            try:
                uint32_high = int(row[0])
                uint32_low = int(row[1])
                double_value = float(row[2])
                
                # Combine into uint64_t
                composite_key = combine_uint32_to_uint64(uint32_high, uint32_low)
                composite_keys.append(composite_key)
                values.append(double_value)
            except ValueError:
                continue
    
    return composite_keys, values


class CompositeKeyValueStore:
    """Efficient key-value store using MPHF for composite uint64 keys.
    
    This class provides O(1) lookup for (uint32_high, uint32_low) -> double mappings
    using minimal perfect hashing.
    """
    
    def __init__(self, composite_keys: list, values: list, gamma: float = 2.0):
        """Initialize the store with keys and values.
        
        Args:
            composite_keys: List of uint64_t composite keys
            values: List of double values corresponding to keys
            gamma: MPHF gamma parameter (space-time tradeoff)
        """
        if len(composite_keys) != len(values):
            raise ValueError("Keys and values must have same length")
        
        self.num_entries = len(composite_keys)
        self.composite_keys = composite_keys
        
        # Build MPHF
        print(f"      Building MPHF for {self.num_entries} composite keys...")
        self.mphf_instance = mphf(n=self.num_entries, input_range=composite_keys, gamma=gamma)
        
        # Create compact value array indexed by MPHF
        self.value_array = [0.0] * self.num_entries
        for i, key in enumerate(composite_keys):
            index = self.mphf_instance.lookup(key)
            self.value_array[index] = values[i]
        
        print(f"      ✓ MPHF built successfully")
    
    def lookup(self, uint32_high: int, uint32_low: int) -> float:
        """Look up value by composite key.
        
        Args:
            uint32_high: Upper 32 bits
            uint32_low: Lower 32 bits
        
        Returns:
            Associated double value, or None if key not found
        """
        composite_key = combine_uint32_to_uint64(uint32_high, uint32_low)
        index = self.mphf_instance.lookup(composite_key)
        
        if 0 <= index < self.num_entries:
            return self.value_array[index]
        return None
    
    def lookup_by_uint64(self, composite_key: int) -> float:
        """Look up value by uint64 composite key directly.
        
        Args:
            composite_key: uint64_t composite key
        
        Returns:
            Associated double value, or None if key not found
        """
        index = self.mphf_instance.lookup(composite_key)
        
        if 0 <= index < self.num_entries:
            return self.value_array[index]
        return None
    
    def save(self, mphf_path: str, values_path: str):
        """Save MPHF and values to separate files.
        
        Args:
            mphf_path: Path to save MPHF binary
            values_path: Path to save values array (binary doubles)
        """
        # Save MPHF
        self.mphf_instance.save(mphf_path)
        
        # Save values as binary doubles
        with open(values_path, 'wb') as f:
            for value in self.value_array:
                f.write(struct.pack('d', value))
    
    @classmethod
    def load(cls, mphf_path: str, values_path: str, composite_keys: list):
        """Load store from saved files.
        
        Args:
            mphf_path: Path to MPHF binary
            values_path: Path to values array
            composite_keys: Original composite keys (needed for reconstruction)
        
        Returns:
            CompositeKeyValueStore instance
        """
        # Load MPHF
        mphf_instance = mphf.load(mphf_path)
        
        # Load values
        with open(values_path, 'rb') as f:
            data = f.read()
            num_values = len(data) // 8  # 8 bytes per double
            value_array = []
            for i in range(num_values):
                value = struct.unpack('d', data[i*8:(i+1)*8])[0]
                value_array.append(value)
        
        # Create instance
        store = cls.__new__(cls)
        store.num_entries = len(value_array)
        store.composite_keys = composite_keys
        store.mphf_instance = mphf_instance
        store.value_array = value_array
        
        return store
    
    def get_memory_usage(self):
        """Calculate approximate memory usage.
        
        Returns:
            Dictionary with memory usage statistics
        """
        # Value array: 8 bytes per double
        values_bytes = self.num_entries * 8
        
        # MPHF: approximate based on gamma
        gamma = self.mphf_instance._gamma
        mphf_bits_per_key = gamma * 1.44  # theoretical bits per key
        mphf_bytes = int(self.num_entries * mphf_bits_per_key / 8)
        
        return {
            'values_bytes': values_bytes,
            'mphf_bytes': mphf_bytes,
            'total_bytes': values_bytes + mphf_bytes,
            'bytes_per_entry': (values_bytes + mphf_bytes) / self.num_entries
        }


def main():
    """Demonstrate advanced MPHF usage with composite keys and values."""
    # Configuration
    CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            'res', 'test_data.csv')
    GAMMA = 2.0
    
    # Setup output directory
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    MPHF_OUTPUT = os.path.join(OUTPUT_DIR, 'uint64_mapping.mphf')
    VALUES_OUTPUT = os.path.join(OUTPUT_DIR, 'uint64_mapping_values.bin')
    NUM_TEST_LOOKUPS = 20
    
    print(f"{'='*70}")
    print(f"Advanced Example: Composite uint64 Key to Double Value Mapping")
    print(f"{'='*70}")
    print(f"Use Case: Efficient (x, y) coordinate to value mapping")
    print(f"  - Keys: Two uint32_t combined into uint64_t")
    print(f"  - Values: Double-precision floating point")
    print(f"  - Data source: {os.path.basename(CSV_PATH)}\n")
    
    # Step 1: Load data from CSV
    print(f"[1/5] Loading data from CSV...")
    print(f"      Reading: {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        print(f"      ✗ ERROR: CSV file not found: {CSV_PATH}")
        return
    
    composite_keys, values = load_csv_data(CSV_PATH)
    print(f"      ✓ Loaded {len(composite_keys)} key-value pairs")
    
    if len(composite_keys) == 0:
        print(f"      ✗ ERROR: No valid data found in CSV")
        return
    
    # Show sample data
    print(f"\n      Sample data (first 5 entries):")
    for i in range(min(5, len(composite_keys))):
        high, low = split_uint64_to_uint32(composite_keys[i])
        print(f"        [{i}] uint64=0x{composite_keys[i]:016X} "
              f"(high={high}, low={low}) -> value={values[i]:.4f}")
    
    # Step 2: Build MPHF-based key-value store
    print(f"\n[2/5] Building MPHF-based key-value store with gamma={GAMMA}...")
    store = CompositeKeyValueStore(composite_keys, values, gamma=GAMMA)
    
    mem_usage = store.get_memory_usage()
    print(f"      ✓ Store created successfully")
    print(f"      Memory usage:")
    print(f"        - Values array: {mem_usage['values_bytes']:,} bytes")
    print(f"        - MPHF structure: ~{mem_usage['mphf_bytes']:,} bytes")
    print(f"        - Total: ~{mem_usage['total_bytes']:,} bytes")
    print(f"        - Per entry: ~{mem_usage['bytes_per_entry']:.2f} bytes")
    
    # Step 3: Test lookups
    print(f"\n[3/5] Testing lookups ({NUM_TEST_LOOKUPS} random samples)...")
    
    import random
    test_indices = random.sample(range(len(composite_keys)), 
                                  min(NUM_TEST_LOOKUPS, len(composite_keys)))
    
    print(f"      Sample lookups (first 10):")
    all_correct = True
    for i, idx in enumerate(test_indices[:10]):
        key = composite_keys[idx]
        expected_value = values[idx]
        high, low = split_uint64_to_uint32(key)
        
        # Lookup using separate uint32 values
        retrieved_value = store.lookup(high, low)
        
        is_correct = abs(retrieved_value - expected_value) < 1e-9
        status = "✓" if is_correct else "✗"
        
        print(f"        [{i}] Key(0x{high:08X}, 0x{low:08X}) -> "
              f"value={retrieved_value:.4f} (expected={expected_value:.4f}) {status}")
        
        if not is_correct:
            all_correct = False
    
    # Verify all lookups
    print(f"\n      Verifying all {len(composite_keys)} lookups...")
    verification_errors = 0
    for i, key in enumerate(composite_keys):
        expected_value = values[i]
        retrieved_value = store.lookup_by_uint64(key)
        
        if abs(retrieved_value - expected_value) > 1e-9:
            verification_errors += 1
            if verification_errors <= 3:  # Show first 3 errors
                high, low = split_uint64_to_uint32(key)
                print(f"        ✗ Error at index {i}: "
                      f"Key(0x{high:08X}, 0x{low:08X}) -> "
                      f"{retrieved_value:.4f} (expected {expected_value:.4f})")
    
    if verification_errors == 0:
        print(f"        ✓ All {len(composite_keys)} lookups correct!")
    else:
        print(f"        ✗ {verification_errors} lookup errors found")
        all_correct = False
    
    # Step 4: Save to disk
    print(f"\n[4/5] Saving store to disk...")
    store.save(MPHF_OUTPUT, VALUES_OUTPUT)
    
    mphf_size = os.path.getsize(MPHF_OUTPUT)
    values_size = os.path.getsize(VALUES_OUTPUT)
    total_size = mphf_size + values_size
    
    print(f"      ✓ Saved MPHF to '{MPHF_OUTPUT}' ({mphf_size:,} bytes)")
    print(f"      ✓ Saved values to '{VALUES_OUTPUT}' ({values_size:,} bytes)")
    print(f"      Total size: {total_size:,} bytes ({total_size/len(composite_keys):.2f} bytes/entry)")
    
    # Step 5: Load and verify
    print(f"\n[5/5] Loading store from disk and verifying...")
    store_loaded = CompositeKeyValueStore.load(MPHF_OUTPUT, VALUES_OUTPUT, composite_keys)
    print(f"      ✓ Loaded store from disk")
    
    # Verify loaded store
    print(f"      Verifying loaded store (testing {min(10, len(composite_keys))} samples)...")
    load_verification_errors = 0
    for idx in test_indices[:10]:
        key = composite_keys[idx]
        expected_value = values[idx]
        high, low = split_uint64_to_uint32(key)
        
        original_value = store.lookup(high, low)
        loaded_value = store_loaded.lookup(high, low)
        
        if abs(loaded_value - expected_value) > 1e-9 or abs(loaded_value - original_value) > 1e-9:
            load_verification_errors += 1
            print(f"        ✗ Error: Key(0x{high:08X}, 0x{low:08X}) -> "
                  f"{loaded_value:.4f} (expected {expected_value:.4f})")
    
    if load_verification_errors == 0:
        print(f"        ✓ Loaded store verified successfully!")
    else:
        print(f"        ✗ {load_verification_errors} errors in loaded store")
        all_correct = False
    
    # Summary
    print(f"\n{'='*70}")
    if all_correct and load_verification_errors == 0:
        print(f"SUCCESS: Advanced MPHF example completed successfully!")
        print(f"{'='*70}")
        print(f"Summary:")
        print(f"  - Entries: {len(composite_keys):,}")
        print(f"  - Key type: uint64_t (composite of two uint32_t)")
        print(f"  - Value type: double (8 bytes)")
        print(f"  - Total size: {total_size:,} bytes ({total_size/len(composite_keys):.2f} bytes/entry)")
        print(f"  - MPHF gamma: {GAMMA}")
        print(f"  - Lookup time: O(1)")
        print(f"  - All verifications passed ✓")
        print(f"\nUse Cases:")
        print(f"  - Coordinate-to-value mapping (e.g., (x,y) -> temperature)")
        print(f"  - Composite key dictionaries")
        print(f"  - Memory-efficient sparse matrix representation")
        print(f"  - Fast hash table alternative for static data")
    else:
        print(f"ERROR: Verification failed")
        print(f"{'='*70}")
    
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
