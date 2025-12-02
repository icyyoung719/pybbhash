"""Setup script for pybbhash package.

This setup.py is provided for backward compatibility.
The project is configured primarily through pyproject.toml.
"""

from setuptools import setup
import os

# Read version from pyproject.toml or use default
version = "0.2.0"

try:
    # Try to read version from __init__.py
    init_path = os.path.join(os.path.dirname(__file__), 'pybbhash', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                version = line.split('=')[1].strip().strip('"').strip("'")
                break
except Exception:
    pass

setup(
    name="pybbhash",
    version=version,
    description="A Python implementation of the BBHash minimal perfect hash function algorithm",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="pybbhash contributors",
    url="https://github.com/icyyoung719/pybbhash",
    license="MIT",
    packages=["pybbhash"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="hash perfect-hash minimal-perfect-hash mphf bbhash boomphf",
    project_urls={
        "Documentation": "https://github.com/icyyoung719/pybbhash#readme",
        "Source": "https://github.com/icyyoung719/pybbhash",
        "Tracker": "https://github.com/icyyoung719/pybbhash/issues",
        "Changelog": "https://github.com/icyyoung719/pybbhash/blob/main/CHANGELOG.md",
    },
    package_data={
        "pybbhash": ["py.typed", "*.pyi"],
    },
    include_package_data=True,
    zip_safe=False,
)
