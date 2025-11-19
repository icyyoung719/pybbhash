"""Demo: Create a binary MPHF file compatible with C++."""
from pybbhash.boophf import mphf
import os

# Parameters
N = 1000
M = 10000
GAMMA = 2.0
SEED = 42

print(f"Creating MPHF with N={N}, M={M}, gamma={GAMMA}")
print(f"Key range: 0 to {N-1}")

# Generate keys
keys = list(range(N))

# Build MPHF
print("\nBuilding MPHF...")
mph = mphf(n=N, input_range=keys, gamma=GAMMA)

# Save to binary file
output_file = "demo.mphf"
mph.save(output_file)

file_size = os.path.getsize(output_file)
print(f"\n✓ Saved to '{output_file}' ({file_size:,} bytes)")

# Test loading
print("\nTesting load...")
mph2 = mphf.load(output_file)

# Verify some lookups
test_keys = [0, 1, N//4, N//2, 3*N//4, N-1]
print(f"\nSample lookups:")
all_match = True
for key in test_keys:
    v1 = mph.lookup(key)
    v2 = mph2.lookup(key)
    match = "✓" if v1 == v2 else "✗"
    print(f"  Key {key:4d}: original={v1:4d}, loaded={v2:4d} {match}")
    all_match = all_match and (v1 == v2)

# Verify complete mapping
print(f"\nVerifying complete 0..{N-1} permutation...")
mapped = set()
for key in keys:
    idx = mph2.lookup(key)
    if idx in mapped:
        print(f"  ✗ Duplicate index: {idx}")
        all_match = False
    mapped.add(idx)

if len(mapped) == N and min(mapped) == 0 and max(mapped) == N-1:
    print(f"  ✓ All {N} keys map to unique indices in range [0, {N-1}]")
else:
    print(f"  ✗ Mapping incomplete or out of range")
    all_match = False

# Summary
print("\n" + "="*60)
if all_match:
    print("SUCCESS: Binary file is valid and can be used with C++")
    print(f"File: {output_file}")
    print(f"Size: {file_size:,} bytes ({file_size/N:.2f} bytes per key)")
else:
    print("ERROR: Verification failed")

print("\nTo use this file in C++:")
print("  std::ifstream is(\"demo.mphf\", std::ios::binary);")
print("  boomphf::mphf<uint64_t, boomphf::SingleHashFunctor<uint64_t>> mph;")
print("  mph.load(is);")
print("  auto idx = mph.lookup(42);")
