from pathlib import Path
import csv
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from pybbhash.boophf import mphf


def to_uint64(high: int, low: int) -> int:
    return ((high & 0xFFFFFFFF) << 32) | (low & 0xFFFFFFFF)


def read_csv(path: Path):
    keys, values = [], []
    with path.open() as fh:
        for row in csv.reader(fh):
            if len(row) != 3:
                continue
            try:
                keys.append(to_uint64(int(row[0]), int(row[1])))
                values.append(float(row[2]))
            except ValueError:
                continue
    return keys, values


def build_value_array(h, keys, values):
    arr = [0.0] * len(keys)
    for key, value in zip(keys, values):
        arr[h.lookup(key)] = value
    return arr


def save_values(values, path: Path):
    with path.open("wb") as fh:
        for value in values:
            fh.write(struct.pack("d", value))


def load_values(path: Path):
    data = path.read_bytes()
    return [struct.unpack("d", data[i : i + 8])[0] for i in range(0, len(data), 8)]


def main():
    csv_path = ROOT / "res" / "test_data.csv"
    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    mphf_path = out_dir / "uint64_mapping.mphf"
    values_path = out_dir / "uint64_mapping_values.bin"

    keys, values = read_csv(csv_path)
    if not keys:
        print(f"No data in {csv_path}")
        return

    h = mphf(n=len(keys), input_range=keys, gamma=2.0)
    value_array = build_value_array(h, keys, values)

    print("Lookup samples:")
    for key, value in list(zip(keys, values))[:5]:
        print(f"  {key:#018x} -> {h.lookup(key)} -> {value:.4f}")

    h.save(mphf_path)
    save_values(value_array, values_path)

    loaded = mphf.load(mphf_path)
    loaded_values = load_values(values_path)
    assert all(loaded.lookup(k) == h.lookup(k) for k in keys)
    assert loaded_values == value_array

    print(f"Saved MPHF ({mphf_path.stat().st_size} bytes) and values ({values_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
