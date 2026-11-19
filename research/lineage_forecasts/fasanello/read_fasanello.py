"""Extract two assigned barcode read counts from the published Fasanello table."""
import argparse
import csv
import hashlib
import math
from pathlib import Path

import pyreadr

SOURCE_SHA256 = "f10be28895efc07a2106f8de08e38661ccc75139826e919ffe54b170aa41d9e0"
DAYS = (0, 10, 15, 20, 22, 24, 25)
CONDITIONS = (
    "CMdiploid0.001", "CMhaploid0.001", "CM+Ethanoldiploid0.001",
    "CM+Saltdiploid0.001", "CMdiploid0.004", "CMdiploid0.00025",
)
COLUMNS = (
    "population_id", "pair_id", "label_pair_id", "strain_pair_id",
    "condition_id", "day", "reads_A", "reads_B",
)


def normalized_label(source_set, label):
    # The native preparation script appends a B in two specific sets.
    last_number = {"S14": 6, "S2": 7}.get(source_set, 1)
    duplicates = {f"d1{row}{number}B" for row in ("A", "H")
                  for number in range(2, last_number + 1)}
    return label[:-1] if label in duplicates else label


def keyed_ids(keys, prefix):
    return {key: f"{prefix}{index:03d}"
            for index, key in enumerate(sorted(set(keys)), 1)}


def extract(source, destination):
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source file differs from the pinned public table")
    data = pyreadr.read_r(str(source))["myevo"]
    assert len(data) == 76 and data.wid.nunique() == 76
    labels = []
    for _, row in data.iterrows():
        names = (row.bc1, row.bc2)
        base = tuple(normalized_label(row["set"], name) for name in names)
        assert base[0] != base[1]
        labels.append((tuple(sorted(names)), tuple(sorted(base)), base[0] < base[1]))
    exact_ids = keyed_ids((pair for pair, _, _ in labels), "P")
    label_ids = keyed_ids((pair for _, pair, _ in labels), "L")
    strain_ids = keyed_ids(((p, pair) for p, (_, pair, _) in zip(data.ploidy, labels)), "S")
    assert (len(exact_ids), len(label_ids), len(strain_ids)) == (44, 38, 44)
    with destination.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for i, ((_, row), (pair, base, first_is_a)) in enumerate(zip(data.iterrows(), labels), 1):
            for day in DAYS:
                native_a, native_b = (row[f"bc{k}cts_{day}"] for k in (1, 2))
                assert all(float(x).is_integer() and x >= 1 for x in (native_a, native_b))
                assert math.isclose(row[f"p{day}"], native_a/(native_a + native_b))
                counts = (int(native_a) - 1, int(native_b) - 1)
                assert sum(counts) > 0
                a, b = counts if first_is_a else counts[::-1]
                writer.writerow(dict(zip(COLUMNS, (
                    f"W{i:03d}", exact_ids[pair], label_ids[base], strain_ids[(row.ploidy, base)],
                    CONDITIONS.index(row.treatment) + 1, day, a, b,
                ))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Native myevo.Rdata file")
    parser.add_argument("destination", type=Path, help="Output TSV")
    args = parser.parse_args()
    extract(args.source, args.destination)
