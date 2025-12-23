"""pybbhash - Python implementation of BBHash minimal perfect hash function.

This package implements a simplified, single-threaded minimal perfect hash builder
in pure Python. It's intended as a reference/portable implementation, not a high-performance
replacement for the C++ original.

Modules:
- bitvector: bit array with rank support
- hashfunctors: simple hash functors used by boophf
- boophf: single-threaded MPH builder (BooPHF-like)

Usage example:
    from pybbhash import boophf
    keys = [10, 20, 30]
    mph = boophf.mphf(len(keys), keys)
    idx = mph.lookup(20)

"""

__version__ = "0.2.0"
__author__ = "pybbhash contributors"
__license__ = "MIT"

from .bitvector import bitvector
from .boophf import mphf
from .hashfunctors import XorshiftHashFunctors, SingleHashFunctor

__all__ = [
    "bitvector",
    "mphf",
    "XorshiftHashFunctors",
    "SingleHashFunctor",
    "__version__",
]
