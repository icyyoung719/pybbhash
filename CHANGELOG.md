# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-threading support
- Type hints throughout codebase
- Performance optimizations
- Additional hash functors

## [0.2.0] - 2025-12-03

### Added
- Comprehensive cross-language binary compatibility test harness under `tests/cross_language/` (Python↔C++).
- Test orchestration scripts: `run_tests.py`, `generate_test_keys.py`, `export_test_data.py`, `verify_cpp_export.py` and `test_compatibility.cpp` (C++ test program).
- `tests/cross_language/out/` artifact directory for generated MPHF binaries and CSVs.

### Changed
- Reorganized cross-language test assets into `tests/cross_language/` (moved from `cpp-bbhash/`) for clearer project layout.
- Updated GitHub Actions workflow to run cross-language compatibility tests.
- C++ test code and build targets upgraded to C++17.

### Fixed
- Corrected Python hash functor implementation to match C++ behavior (fix in `pybbhash/hashfunctors.py`).
- Fix in `pybbhash/boophf.py` to align collision probability calculation with C++ implementation.
- Replaced non-ASCII console markers in test code to avoid MSVC code page warnings.

### Documentation
- Added `tests/cross_language/README.md` and `tests/cross_language/TEST_FLOW.md` describing the test flow and binary format verification.
- Updated top-level `README.md` to reference the new test location and usage.

### Testing
- Added automation to build and run C++ tests in CI; validated Python→C++ and C++→Python binary interoperability.
- Added scripts to create reproducible test keys and compare Python/C++ hash assignments.

## [0.1.0] - 2025-11-19

### Added
- Initial release of pybbhash
- Core MPHF implementation compatible with C++ BBHash
- `mphf` class for building and querying minimal perfect hash functions
- `bitvector` class with rank support
- Hash functors: `SingleHashFunctor` and `XorshiftHashFunctors`
- Binary save/load functionality compatible with C++ implementation
- Configurable gamma parameter for space-time tradeoffs
- Three comprehensive examples:
  - `basic.py`: Basic usage demonstration
  - `binary_format.py`: Binary format and C++ compatibility
  - `uint64_mapping.py`: Advanced composite key mapping
- Complete test suite with pytest
- Binary format documentation
- MIT License
- PyPI packaging configuration
- Comprehensive README with examples and documentation

### Features
- Pure Python implementation with no external dependencies
- Cross-platform compatibility (Windows, Linux, macOS)
- Python 3.8+ support
- O(1) lookup time for constructed hash functions
- Space-efficient storage with configurable gamma parameter

### Documentation
- API reference in README
- Binary format specification in docs/
- Example scripts with detailed comments
- Inline documentation and docstrings

### Testing
- Unit tests for core functionality
- Binary format compatibility tests
- Example validation tests

---

## Release Notes

### Version 0.1.0

This is the initial release of pybbhash, a Python implementation of the BBHash (BooPHF) minimal perfect hash function algorithm. The implementation is compatible with the original C++ version and provides a simple, portable solution for creating efficient perfect hash functions.

**Key Highlights:**
- 🎯 Minimal perfect hash functions for static key sets
- 🔄 Binary compatibility with C++ BBHash
- 📦 Zero external dependencies
- 🚀 Easy-to-use API
- 💾 Persistent save/load support

**Quick Start:**
```python
from pybbhash import mphf
keys = [10, 20, 30, 40, 50]
mph = mphf(n=len(keys), input_range=keys, gamma=1.5)
idx = mph.lookup(20)  # Returns unique index in [0, 4]
```

For detailed usage examples, see the `examples/` directory.

---

[Unreleased]: https://github.com/icyyoung719/pybbhash/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/icyyoung719/pybbhash/releases/tag/v0.1.0
[0.2.0]: https://github.com/icyyoung719/pybbhash/releases/tag/v0.2.0
