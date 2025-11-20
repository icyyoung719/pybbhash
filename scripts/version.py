#!/usr/bin/env python
"""Version management script for pybbhash.

Usage:
    python scripts/version.py              # Show current version
    python scripts/version.py patch        # Bump patch version (0.1.0 -> 0.1.1)
    python scripts/version.py minor        # Bump minor version (0.1.0 -> 0.2.0)
    python scripts/version.py major        # Bump major version (0.1.0 -> 1.0.0)
    python scripts/version.py set 1.2.3    # Set specific version
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Get project root
ROOT_DIR = Path(__file__).parent.parent


def read_version():
    """Read current version from __init__.py."""
    init_file = ROOT_DIR / "pybbhash" / "__init__.py"
    with open(init_file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise ValueError("Could not find version in __init__.py")


def parse_version(version):
    """Parse version string into components."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(int(p) for p in parts)


def format_version(major, minor, patch):
    """Format version components into string."""
    return f"{major}.{minor}.{patch}"


def bump_version(current, bump_type):
    """Bump version according to bump_type."""
    major, minor, patch = parse_version(current)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return format_version(major, minor, patch)


def update_version_in_file(file_path, old_version, new_version):
    """Update version in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace version
    updated = content.replace(f'"{old_version}"', f'"{new_version}"')
    updated = updated.replace(f"'{old_version}'", f"'{new_version}'")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated)
    
    return content != updated


def update_changelog(new_version):
    """Update CHANGELOG.md with new version."""
    changelog_file = ROOT_DIR / "CHANGELOG.md"
    
    if not changelog_file.exists():
        return
    
    with open(changelog_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Add new version section after [Unreleased]
    new_section = f"\n\n## [{new_version}] - {today}\n\n### Changed\n- Version bump to {new_version}\n"
    
    # Insert after ## [Unreleased]
    updated = re.sub(
        r"(## \[Unreleased\].*?)(\n\n##)",
        rf"\1{new_section}\2",
        content,
        count=1
    )
    
    # Update comparison links at bottom
    if "[Unreleased]" in updated:
        updated = re.sub(
            r"\[Unreleased\]: .*/compare/v[\d.]+\.\.\.HEAD",
            f"[Unreleased]: https://github.com/icyyoung719/pybbhash/compare/v{new_version}...HEAD",
            updated
        )
    
    with open(changelog_file, "w", encoding="utf-8") as f:
        f.write(updated)


def set_version(new_version):
    """Set version in all files."""
    old_version = read_version()
    
    print(f"📝 Updating version: {old_version} -> {new_version}")
    
    files_to_update = [
        ROOT_DIR / "pybbhash" / "__init__.py",
        ROOT_DIR / "pyproject.toml",
    ]
    
    updated_count = 0
    for file_path in files_to_update:
        if file_path.exists():
            if update_version_in_file(file_path, old_version, new_version):
                print(f"   ✅ Updated {file_path.relative_to(ROOT_DIR)}")
                updated_count += 1
    
    # Update changelog
    update_changelog(new_version)
    print(f"   ✅ Updated CHANGELOG.md")
    
    print(f"\n✨ Version updated in {updated_count} files!")
    print(f"\n📋 Next steps:")
    print(f"   1. Review changes: git diff")
    print(f"   2. Commit: git add -A && git commit -m 'Bump version to {new_version}'")
    print(f"   3. Tag: git tag -a v{new_version} -m 'Release {new_version}'")
    print(f"   4. Push: git push && git push --tags")


def main():
    """Main entry point."""
    print("=" * 70)
    print("🔷 pybbhash Version Manager")
    print("=" * 70)
    
    current_version = read_version()
    print(f"\n📌 Current version: {current_version}")
    
    if len(sys.argv) < 2:
        print("\n💡 Usage:")
        print("   python scripts/version.py patch        # 0.1.0 -> 0.1.1")
        print("   python scripts/version.py minor        # 0.1.0 -> 0.2.0")
        print("   python scripts/version.py major        # 0.1.0 -> 1.0.0")
        print("   python scripts/version.py set 1.2.3    # Set to 1.2.3")
        return
    
    command = sys.argv[1]
    
    if command in ["major", "minor", "patch"]:
        new_version = bump_version(current_version, command)
        set_version(new_version)
    elif command == "set":
        if len(sys.argv) < 3:
            print("❌ Error: 'set' requires a version number")
            print("   Example: python scripts/version.py set 1.2.3")
            sys.exit(1)
        new_version = sys.argv[2]
        # Validate version format
        try:
            parse_version(new_version)
        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        set_version(new_version)
    else:
        print(f"❌ Unknown command: {command}")
        print("   Valid commands: major, minor, patch, set")
        sys.exit(1)
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
