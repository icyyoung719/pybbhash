# pybbhash

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**pybbhash** is a Python implementation of the BBHash (BooPHF) minimal perfect hash function (MPHF) algorithm. It provides an efficient way to create bijective mappings from a set of keys to consecutive integers [0, n-1].

## 🌟 Features

- ✅ **Minimal Perfect Hash Function**: Maps n keys to exactly n consecutive integers with no collisions
- 🔄 **Binary Compatible**: Save/load format compatible with the C++ BBHash implementation
- 🚀 **Simple API**: Easy-to-use interface for building and querying MPHFs
- 📦 **Pure Python**: No external dependencies, works on any platform
- 🎯 **Space Efficient**: Configurable gamma parameter for space-time tradeoffs
- 💾 **Persistent**: Save and load MPHFs to/from disk

## 📥 Installation

### From PyPI (coming soon)

```bash
pip install pybbhash
```

### From Source

```bash
git clone https://github.com/icyyoung719/pybbhash.git
cd pybbhash
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```python
from pybbhash import mphf

# Create MPHF for a set of keys
keys = [10, 20, 30, 40, 50]
mph = mphf(n=len(keys), input_range=keys, gamma=1.5)

# Look up keys - returns indices in [0, 4]
for key in keys:
    index = mph.lookup(key)
    print(f"Key {key} -> Index {index}")

# Save to disk
mph.save("my_hash.mphf")

# Load from disk
mph_loaded = mphf.load("my_hash.mphf")
```

### Advanced Example: Composite Keys

```python
from pybbhash import mphf

# Combine two uint32 values into uint64 keys
def make_key(x, y):
    return (x << 32) | y

# Create keys from coordinate pairs
coords = [(100, 200), (150, 250), (200, 300)]
keys = [make_key(x, y) for x, y in coords]

# Build MPHF
mph = mphf(n=len(keys), input_range=keys, gamma=2.0)

# Create value array indexed by MPHF
values = [42.5, 37.8, 91.2]
value_array = [0.0] * len(keys)
for i, key in enumerate(keys):
    idx = mph.lookup(key)
    value_array[idx] = values[i]

# Fast O(1) lookup
key = make_key(150, 250)
idx = mph.lookup(key)
value = value_array[idx]
print(f"Value at ({150}, {250}): {value}")
```

## 📖 Documentation

### API Reference

#### `mphf` Class

**Constructor:**
```python
mphf(n: int, input_range: Iterable[int], gamma: float = 2.0, 
     num_thread: int = 1, progress: bool = False)
```

- `n`: Number of keys
- `input_range`: Iterable of integer keys
- `gamma`: Space-time tradeoff parameter (default: 2.0)
  - Lower values: less memory, slower construction
  - Higher values: more memory, faster construction
  - Typical range: 1.0 to 3.0
- `num_thread`: Reserved for future use (currently ignored)
- `progress`: Show progress during construction (default: False)

**Methods:**

- `lookup(key: int) -> int`: Query the MPHF for a key, returns index in [0, n-1]
- `save(path: str)`: Save MPHF to binary file
- `load(path: str) -> mphf`: Static method to load MPHF from binary file
- `nbKeys() -> int`: Return the number of keys in the MPHF

### Binary Format

The binary format is compatible with the C++ BBHash implementation. See [BINARY_FORMAT.md](docs/BINARY_FORMAT.md) for detailed specification.

## 📚 Examples

The `examples/` directory contains complete working examples:

- **`basic.py`**: Basic MPHF construction and lookup
- **`binary_format.py`**: Binary save/load with C++ compatibility
- **`uint64_mapping.py`**: Advanced example with composite keys and CSV data

Run examples:
```bash
python examples/basic.py
python examples/binary_format.py
python examples/uint64_mapping.py
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_base.py

# Run with coverage
python -m pytest --cov=pybbhash tests/
```

## 🎯 Use Cases

- **Database Indexing**: Create compact indices for static datasets
- **Coordinate Mapping**: Map 2D/3D coordinates to array indices
- **String Hashing**: Perfect hashing for static string sets
- **Sparse Data Structures**: Efficient sparse matrix/array representation
- **Serialization**: Compact binary format for disk storage
- **Bioinformatics**: k-mer indexing and sequence analysis

## ⚡ Performance

While this Python implementation prioritizes correctness and portability over speed, it's suitable for:
- Moderate-sized datasets (up to millions of keys)
- Applications where construction time is not critical
- Prototyping and testing before using C++ implementation
- Cross-platform compatibility requirements

For large-scale high-performance applications, consider the original C++ implementation: [BBHash](https://github.com/rizkg/BBHash)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original BBHash/BooPHF algorithm by Antoine Limasset et al.
- C++ implementation: [BBHash](https://github.com/rizkg/BBHash)
- Paper: "Fast and Scalable Minimal Perfect Hashing for Massive Key Sets" (2017)

## 📬 Contact

- GitHub: [@icyyoung719](https://github.com/icyyoung719)
- Issues: [GitHub Issues](https://github.com/icyyoung719/pybbhash/issues)

## 🔗 Related Projects

- [BBHash (C++)](https://github.com/rizkg/BBHash) - Original C++ implementation
- [BooPHF](https://github.com/rizkg/BBHash) - C++ BooPHF implementation

---

**Made with ❤️ by the pybbhash contributors**
