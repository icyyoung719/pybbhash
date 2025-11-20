# PyPI Publishing Guide

This guide will help you publish pybbhash to PyPI.

## 📋 Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Create account at https://test.pypi.org/account/register/ (for testing)

2. **Install Build Tools**
   ```bash
   pip install --upgrade build twine
   ```

3. **API Tokens** (Recommended)
   - Generate API token at https://pypi.org/manage/account/token/
   - Generate TestPyPI token at https://test.pypi.org/manage/account/token/
   - Store in `~/.pypirc`:
     ```ini
     [pypi]
     username = __token__
     password = pypi-YOUR_TOKEN_HERE
     
     [testpypi]
     username = __token__
     password = pypi-YOUR_TESTPYPI_TOKEN_HERE
     ```

## 🚀 Publishing Steps

### 1. Prepare for Release

```bash
# Update version
python scripts/version.py patch  # or minor, major

# Run tests
python -m pytest tests/

# Check all examples work
python examples/basic.py
python examples/binary_format.py
python examples/uint64_mapping.py
```

### 2. Build Distribution

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build
python -m build

# Or use the helper script
python scripts/build.py
```

This creates:
- `dist/pybbhash-X.Y.Z-py3-none-any.whl` (wheel)
- `dist/pybbhash-X.Y.Z.tar.gz` (source distribution)

### 3. Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Or use helper script
python scripts/build.py --test

# Test installation
pip install --index-url https://test.pypi.org/simple/ pybbhash

# Test the package
python -c "from pybbhash import mphf; print(mphf.__doc__)"
```

### 4. Publish to PyPI

```bash
# Check distribution
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Or use helper script
python scripts/build.py --publish
```

### 5. Post-Release

```bash
# Create git tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Create GitHub release
# Go to https://github.com/icyyoung719/pybbhash/releases/new
# - Tag: v0.1.0
# - Title: pybbhash 0.1.0
# - Description: Copy from CHANGELOG.md
# - Attach dist files (optional)

# Update documentation
# Verify installation works
pip install pybbhash
```

## 🔄 Version Management

### Semantic Versioning

Follow [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Add functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Bump Version

```bash
# Patch: 0.1.0 -> 0.1.1 (bug fixes)
python scripts/version.py patch

# Minor: 0.1.0 -> 0.2.0 (new features)
python scripts/version.py minor

# Major: 0.1.0 -> 1.0.0 (breaking changes)
python scripts/version.py major

# Set specific version
python scripts/version.py set 1.2.3
```

This updates:
- `pybbhash/__init__.py` - `__version__`
- `pyproject.toml` - version field
- `CHANGELOG.md` - adds new version entry

## 📝 Pre-Release Checklist

- [ ] All tests pass
- [ ] Examples run without errors
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version is bumped appropriately
- [ ] No uncommitted changes
- [ ] Build succeeds without warnings
- [ ] Distribution files checked with twine

## 🐛 Troubleshooting

### "File already exists"

If you get this error, the version already exists on PyPI. You need to bump the version number.

```bash
python scripts/version.py patch
python -m build
twine upload dist/*
```

### Import errors after installation

Make sure the package structure is correct:
```
pybbhash/
├── __init__.py
├── bitvector.py
├── boophf.py
└── hashfunctors.py
```

### Missing dependencies in wheel

Check `pyproject.toml` dependencies section and MANIFEST.in

## 📚 Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)

## 🆘 Getting Help

If you encounter issues:
1. Check the [Python Packaging Guide](https://packaging.python.org/)
2. Search [PyPI Help](https://pypi.org/help/)
3. Ask in project issues

---

**Happy Publishing! 🎉**
