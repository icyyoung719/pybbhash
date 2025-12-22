from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from pybbhash.boophf import mphf


def main():
    keys = list(range(1_000))
    h = mphf(n=len(keys), input_range=keys, gamma=2.0)

    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    target = out_dir / "binary_format.mphf"
    h.save(target)

    loaded = mphf.load(target)
    assert all(loaded.lookup(k) == i for i, k in enumerate(keys))

    print(f"Saved C++-compatible MPHF to {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
