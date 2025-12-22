from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from pybbhash.boophf import mphf


def main():
    rng = random.Random(41)
    keys = rng.sample(range(1, 10_000), 30)
    h = mphf(n=len(keys), input_range=keys, gamma=1)

    sample = keys[:5]
    sample_results = {k: h.lookup(k) for k in sample}
    print("Sample lookups:")
    for key, idx in sample_results.items():
        print(f"  {key} -> {idx}")

    path = ROOT / "out"
    path.mkdir(exist_ok=True)
    file_path = path / "basic.mphf"
    h.save(file_path)
    loaded = mphf.load(file_path)

    assert all(h.lookup(k) == loaded.lookup(k) for k in keys)
    print(f"Stored {len(keys)} keys, file size {file_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
