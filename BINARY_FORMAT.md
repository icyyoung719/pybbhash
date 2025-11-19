# Binary Format Specification

This document describes the binary serialization format used by pybbhash, which is compatible with the C++ BBHash library.

## File Format Overview

The binary file format uses little-endian byte order (`<` in Python struct format) and follows the exact layout of the C++ implementation.

## mphf Binary Format

### Header (28 bytes)

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 8 | double | `_gamma` | Load factor parameter (typically 1.5-2.0) |
| 8 | 4 | uint32_t | `_nb_levels` | Number of cascade levels (typically 25) |
| 12 | 8 | uint64_t | `_lastbitsetrank` | Rank value at end of last bitset |
| 20 | 8 | uint64_t | `_nelem` | Number of elements in the hash |

### Level Bitsets (variable size)

For each level (0 to `_nb_levels-1`), a `bitVector` is serialized:

#### bitVector Format

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 8 | uint64_t | `_size` | Total number of bits |
| 8 | 8 | uint64_t | `_nchar` | Number of 64-bit words |
| 16 | 8×`_nchar` | uint64_t[] | `_bitArray` | Bit array data |
| 16+8×`_nchar` | 8 | uint64_t | `ranks_size` | Number of rank samples |
| 24+8×`_nchar` | 8×`ranks_size` | uint64_t[] | `_ranks` | Rank sample array |

### Final Hash Table (variable size)

After all level bitsets:

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 8 | uint64_t | `final_hash_size` | Number of entries in final hash |

For each entry (0 to `final_hash_size-1`):

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 8 | uint64_t | `key` | Element key |
| 8 | 8 | uint64_t | `value` | Hash value |

## Data Types

All numeric types use standard sizes:
- `double`: 8 bytes, IEEE 754 double-precision
- `uint64_t`: 8 bytes, unsigned integer
- `uint32_t`: 4 bytes, unsigned integer

## Byte Order

All multi-byte values are stored in **little-endian** format.

## Python Struct Format Codes

- `<d`: little-endian double (8 bytes)
- `<Q`: little-endian uint64_t (8 bytes)
- `<I`: little-endian uint32_t (4 bytes)

## Compatibility Notes

1. The Python implementation uses `struct.pack()` and `struct.unpack()` with format codes matching C++ `sizeof()` values
2. Keys are assumed to be `uint64_t` (Python `int` values are packed as unsigned 64-bit)
3. The format is binary-identical to C++ BBHash save/load functions
4. Files can be shared between Python and C++ implementations

## Example Usage

### Python Save
```python
from pybbhash.boophf import mphf

keys = list(range(1000))
mph = mphf(n=len(keys), input_range=keys, gamma=2.0)
mph.save("example.mphf")  # Saves in binary format
```

### Python Load
```python
from pybbhash.boophf import mphf

mph = mphf.load("example.mphf")  # Loads binary format
result = mph.lookup(42)
```

### C++ Load (compatible)
```cpp
#include "BooPHF.h"
typedef boomphf::mphf<uint64_t, boomphf::SingleHashFunctor<uint64_t>> mphf_t;

std::ifstream is("example.mphf", std::ios::binary);
mphf_t mph;
mph.load(is);
auto result = mph.lookup(42);
```

## Version Information

- Format Version: 1.0
- Compatible with: BBHash C++ library (single-threaded port)
- Python Implementation: pybbhash 1.0
