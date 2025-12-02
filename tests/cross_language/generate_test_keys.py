#!/usr/bin/env python3
"""Generate test keys for cross-language compatibility testing.

This script generates a fixed set of test keys that will be used by both
Python and C++ implementations to ensure they process the same data.
"""

import csv
import random
import os


def main():
    # Use fixed seed for reproducible test keys
    random.seed(42)
    
    # Generate 1000 random unique keys
    test_keys = sorted(random.sample(range(1000, 100000), 1000))
    
    # Ensure output directory exists and save to out/
    os.makedirs('out', exist_ok=True)
    # Save to CSV
    csv_file = os.path.join('out', 'test_keys.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['key'])
        for key in test_keys:
            writer.writerow([key])
    
    print(f"✓ Generated {len(test_keys)} test keys")
    print(f"✓ Saved to: {csv_file}")
    print(f"\nKey range: [{min(test_keys)}, {max(test_keys)}]")
    print(f"First 5 keys: {test_keys[:5]}")
    print(f"Last 5 keys: {test_keys[-5:]}")


if __name__ == "__main__":
    main()
