# Cross-Language Binary Compatibility Tests

This directory contains tests to verify binary format compatibility between Python (pybbhash) and C++ (BBHash) implementations of Minimal Perfect Hash Functions (MPHF).

## Directory Structure

```
tests/cross_language/
├── cpp_headers/           # C++ BBHash library headers
│   ├── BooPHF.h          # Main MPHF implementation
│   ├── bitvector.hpp     # Bit vector utilities
│   ├── platform_time.h   # Platform-specific timing
│   └── progress.hpp      # Progress display utilities
├── docs/                 # Detailed documentation
│   ├── README.md         # Original detailed guide
│   ├── ARCHITECTURE.md   # Architecture explanation
│   ├── HASH_FUNCTION_FIX.md  # Hash function bug fix details
│   └── TESTING_PHILOSOPHY.md # Testing approach
├── test_compatibility.cpp    # C++ test program
├── export_py_binary.py      # Generate Python MPHF binary
├── verify_cpp_export.py     # Verify C++ MPHF binary in Python
└── run_tests.py            # Master test orchestrator
```

## Quick Start

Run all tests:
```bash
cd tests/cross_language
python run_tests.py
```

This will:
1. Generate test data using Python (1000 keys)
2. Build Python MPHF and export binary format
3. Compile C++ test program
4. Test loading Python binary in C++
5. Build C++ MPHF and export binary format
6. Test loading C++ binary in Python

## What We Test

### Binary Format Compatibility
- Header format (gamma, nb_levels, lastbitsetrank, nelem)
- Bitset serialization (level-by-level)
- Final hash table format
- Endianness handling (little-endian)

### MPHF Properties
- All keys can be looked up successfully
- Hash values are in valid range [0, n-1]
- No collisions (all hash values are unique)
- Consistent behavior across implementations

### Note on Hash Values
The Python and C++ implementations produce **different hash values** for the same keys. This is expected and correct! What matters is:
- Both implementations can read each other's binary format
- Both produce valid MPHFs (no collisions, correct range)
- Binary format is fully compatible

See `docs/TESTING_PHILOSOPHY.md` for detailed explanation.

## Requirements

- Python 3.8+ with pybbhash installed
- C++17 compiler (g++ or MSVC)
- pytest (for running via pytest)

## Manual Compilation

If `run_tests.py` fails to compile, you can compile manually:

**Linux/macOS:**
```bash
g++ -std=c++17 -O2 -Wall test_compatibility.cpp -o test_compatibility -I. -I./cpp_headers
```

**Windows (g++):**
```bash
g++ -std=c++17 -O2 -Wall test_compatibility.cpp -o test_compatibility.exe -I. -I./cpp_headers
```

**Windows (MSVC):**
```bash
cl /std:c++17 /EHsc test_compatibility.cpp /I. /I.\cpp_headers
```

Then run:
```bash
./test_compatibility      # Linux/macOS
test_compatibility.exe    # Windows
```

## CI Integration

These tests run automatically in GitHub Actions on every push/PR. See `.github/workflows/ci.yml`.

## Documentation

For more details, see the `docs/` subdirectory:
- `README.md` - Comprehensive guide with examples
- `ARCHITECTURE.md` - Technical architecture details
- `HASH_FUNCTION_FIX.md` - Hash function bug fix history
- `TESTING_PHILOSOPHY.md` - Why hash values differ and why it's OK
