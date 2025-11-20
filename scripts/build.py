#!/usr/bin/env python
"""Build and publish script for pybbhash package.

Usage:
    python scripts/build.py          # Build distribution
    python scripts/build.py --test   # Upload to TestPyPI
    python scripts/build.py --publish # Upload to PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Get project root
ROOT_DIR = Path(__file__).parent.parent
os.chdir(ROOT_DIR)


def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"\n🔨 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def clean():
    """Clean build artifacts."""
    print("\n🧹 Cleaning build artifacts...")
    dirs_to_remove = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_remove:
        for path in ROOT_DIR.glob(pattern):
            if path.is_dir():
                print(f"   Removing {path}")
                shutil.rmtree(path)
            else:
                print(f"   Removing {path}")
                path.unlink()


def build():
    """Build distribution packages."""
    print("\n📦 Building distribution packages...")
    clean()
    
    # Install build tools if needed
    run_command(f"{sys.executable} -m pip install --upgrade build twine")
    
    # Build
    run_command(f"{sys.executable} -m build")
    
    print("\n✅ Build complete!")
    print("\n📋 Distribution files:")
    for file in (ROOT_DIR / "dist").glob("*"):
        print(f"   - {file.name}")


def check():
    """Check distribution packages."""
    print("\n🔍 Checking distribution packages...")
    if not (ROOT_DIR / "dist").exists():
        print("❌ No dist/ directory found. Run build first.")
        return False
    
    result = run_command("twine check dist/*", check=False)
    if result:
        print("✅ Distribution packages are valid!")
    else:
        print("❌ Distribution packages have issues!")
    return result


def upload_test():
    """Upload to TestPyPI."""
    print("\n🚀 Uploading to TestPyPI...")
    print("\n⚠️  You will need TestPyPI credentials.")
    print("   Create account at: https://test.pypi.org/account/register/")
    
    if not check():
        print("❌ Cannot upload - distribution check failed!")
        return False
    
    result = run_command("twine upload --repository testpypi dist/*", check=False)
    
    if result:
        print("\n✅ Uploaded to TestPyPI!")
        print("\n📥 Test installation:")
        print("   pip install --index-url https://test.pypi.org/simple/ pybbhash")
    else:
        print("\n❌ Upload failed!")
    
    return result


def upload_pypi():
    """Upload to PyPI."""
    print("\n🚀 Uploading to PyPI...")
    print("\n⚠️  WARNING: This will publish to the REAL PyPI!")
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Upload cancelled.")
        return False
    
    if not check():
        print("❌ Cannot upload - distribution check failed!")
        return False
    
    result = run_command("twine upload dist/*", check=False)
    
    if result:
        print("\n✅ Uploaded to PyPI!")
        print("\n📥 Installation:")
        print("   pip install pybbhash")
    else:
        print("\n❌ Upload failed!")
    
    return result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and publish pybbhash")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--publish", action="store_true", help="Upload to PyPI")
    parser.add_argument("--check", action="store_true", help="Check distribution")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔷 pybbhash Build & Publish Script")
    print("=" * 70)
    
    if args.clean:
        clean()
    elif args.check:
        build()
        check()
    elif args.test:
        build()
        upload_test()
    elif args.publish:
        build()
        upload_pypi()
    else:
        build()
        check()
    
    print("\n" + "=" * 70)
    print("✅ Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()
