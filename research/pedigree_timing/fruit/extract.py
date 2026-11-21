"""Extract anonymous fruit measurements and parental branch observations (Python standard library)."""
import argparse
import csv
import gzip
import hashlib
import io
from collections import defaultdict
from pathlib import Path

FILES = {
    "fruit_mutations.tsv.gz": "ac860196c362ee608dddffb5883a3cab9db2c5c9a4869dc90be1caca96c7d328",
    "angela.leaf_mutations.tsv.gz": "13be8a6566d5dfc7883eb6914db2fa9c2d6e8d9d110e0fd90716e7ab0c7469f4",
    "sixto.leaf_mutations.tsv.gz": "93724d2809c111a72a55c67dc0885969e2667ccb22c079b2afffd98db620a3fa",
}
TREES = {"Dicorynia guianensis": ("DG", "angela"), "Sextonia rubra": ("SR", "sixto")}


def read(directory, name):
    data = (directory / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != FILES[name]:
        raise ValueError(f"Source checksum mismatch for {name}")
    return csv.DictReader(io.StringIO(gzip.decompress(data).decode()), delimiter="\t")


def write(path, fields, records):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(fields.split())
        writer.writerows(records)


def extract(source, output):
    fruits = {}
    counts = defaultdict(int)
    markers = defaultdict(set)
    for row in read(source, "fruit_mutations.tsv.gz"):
        tree, _ = TREES[row["species"]]
        marker = (int(row["scaffold"]), int(row["position"]), row["normal"], row["mutation"])
        key = tree, marker, row["branch"], row["fruit"], row["tissue"]
        value = tuple(int(row[field]) for field in
                      ["normal_read_count", "mutation_read_count", "sequencing_depth", "heterozygous_call_gatk"])
        assert min(value) >= 0 and value[3] in (0, 1)
        fraction = row["allelic_fraction"]
        assert (fraction == "NA") == (value[2] == 0)
        if value[2]:
            assert abs(float(fraction) - value[1]/value[2]) < 1e-10
        if key in fruits and fruits[key] != value:
            raise ValueError("Conflicting duplicate fruit measurement")
        fruits[key] = value
        markers[tree].add(marker)
        counts[tree] += 1
    assert dict(counts) == {"DG": 7252, "SR": 1722} and len(fruits) == 4142
    assert {k: len(v) for k, v in markers.items()} == {"DG": 23, "SR": 9}
    ids = {tree: {mark: f"M{i:02d}" for i, mark in enumerate(sorted(items), 1)}
           for tree, items in markers.items()}
    leaves = []
    for tree, prefix in TREES.values():
        calls = defaultdict(set)
        all_samples = defaultdict(set)
        for r in read(source, f"{prefix}.leaf_mutations.tsv.gz"):
            m = int(r["CHROM"].split("_")[-1]), int(r["POS"]), r["REF"], r["ALT"]
            all_samples[r["branch"]].add(r["tumor"])
            if m in markers[tree]:
                calls[m, r["branch"]].add(r["tumor"])
        expected = {m for m, branch in calls}
        assert expected == markers[tree]
        for marker in sorted(markers[tree]):
            for branch, samples in sorted(all_samples.items()):
                leaves.append((tree, ids[tree][marker], branch, len(calls[marker, branch]), len(samples)))
    output.mkdir(parents=True, exist_ok=True)
    write(output/"fruit_counts.tsv", "tree marker branch fruit tissue ref_reads alt_reads depth source_call",
          ((t, ids[t][m], b, f, tissue, *fruits[t,m,b,f,tissue]) for t,m,b,f,tissue in sorted(fruits)))
    write(output/"leaf_calls.tsv", "tree marker branch leaves_with_call sampled_leaves_in_call_table", leaves)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    extract(args.source, args.output)
