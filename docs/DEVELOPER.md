# Developer Quick Start

Quick reference guide for pybbhash developers.

## 🚀 Setup

```bash
# Clone repository
git clone https://github.com/icyyoung719/pybbhash.git
cd pybbhash

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_base.py -v

# Run with coverage
python -m pytest --cov=pybbhash tests/

# Run examples
python examples/basic.py
python examples/binary_format.py
python examples/uint64_mapping.py
```

## 📦 Building

```bash
# Clean build artifacts
python scripts/build.py --clean

# Build distribution
python scripts/build.py

# Build and check
python scripts/build.py --check

# Upload to TestPyPI
python scripts/build.py --test

# Publish to PyPI
python scripts/build.py --publish
```

## 🔢 Version Management

```bash
# Show current version
python scripts/version.py

# Bump patch version (0.1.0 -> 0.1.1)
python scripts/version.py patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/version.py minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/version.py major

# Set specific version
python scripts/version.py set 1.2.3
```

## 📁 Project Structure

```
pybbhash/
├── pybbhash/           # Main package
│   ├── __init__.py     # Package initialization with version
│   ├── __init__.pyi    # Type stubs
│   ├── py.typed        # PEP 561 marker
│   ├── bitvector.py    # Bit vector with rank support
│   ├── boophf.py       # Main MPHF implementation
│   └── hashfunctors.py # Hash functors
├── tests/              # Test suite
│   ├── test_base.py
│   └── test_binary_format.py
├── examples/           # Example scripts
│   ├── basic.py
│   ├── binary_format.py
│   └── uint64_mapping.py
├── scripts/            # Development scripts
│   ├── build.py        # Build and publish script
│   └── version.py      # Version management
├── docs/               # Documentation
│   ├── BINARY_FORMAT.md
│   └── PUBLISHING.md
├── res/                # Test resources
│   └── test_data.csv
├── out/                # Output directory (gitignored)
├── pyproject.toml      # Project configuration
├── setup.py            # Setup script (backward compat)
├── MANIFEST.in         # Package manifest
├── LICENSE             # MIT License
├── README.md           # Main documentation
├── CHANGELOG.md        # Version history
├── CONTRIBUTING.md     # Contribution guidelines
└── .gitignore          # Git ignore rules
```

## 🔧 Common Tasks

### Add a new feature

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Test
python -m pytest tests/ -v

# Format code (optional)
black pybbhash tests examples

# Commit
git add .
git commit -m "Add feature: description"

# Push and create PR
git push origin feature/my-feature
```

### Fix a bug

```bash
# Create bugfix branch
git checkout -b bugfix/issue-123

# Make changes and add test
# ... edit files ...
# ... add test in tests/ ...

# Test
python -m pytest tests/ -v

# Commit
git add .
git commit -m "Fix: description (fixes #123)"

# Push and create PR
git push origin bugfix/issue-123
```

### Release new version

```bash
# Update version
python scripts/version.py patch  # or minor/major

# Review changes
git diff

# Commit version bump
git add -A
git commit -m "Bump version to X.Y.Z"

# Tag release
git tag -a vX.Y.Z -m "Release X.Y.Z"

# Push
git push && git push --tags

# Build and publish
python scripts/build.py --test     # Test on TestPyPI first
python scripts/build.py --publish  # Publish to PyPI
```

## 📚 Documentation

- **README.md**: Main project documentation
- **BINARY_FORMAT.md**: Binary format specification
- **PUBLISHING.md**: PyPI publishing guide
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history

## 🔍 Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for public APIs
- Keep functions focused and modular
- Add tests for new features

## 🐛 Debugging

```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Test specific key lookup
from pybbhash import mphf
keys = [10, 20, 30]
mph = mphf(n=len(keys), input_range=keys, progress=True)
idx = mph.lookup(20)
print(f"Key 20 -> Index {idx}")
```

## 📊 Performance Testing

```python
import time
from pybbhash import mphf

# Test with different sizes
for n in [100, 1000, 10000]:
    keys = list(range(n))
    
    start = time.time()
    mph = mphf(n=n, input_range=keys, gamma=2.0)
    build_time = time.time() - start
    
    start = time.time()
    for key in keys[:100]:
        mph.lookup(key)
    lookup_time = (time.time() - start) / 100
    
    print(f"n={n}: build={build_time:.3f}s, lookup={lookup_time*1e6:.1f}μs")
```

## 🆘 Help

- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines
- See [PUBLISHING.md](docs/PUBLISHING.md) for release process
- Open an issue on GitHub for questions
- Review existing issues and PRs

---

**Happy Coding! 💻**
