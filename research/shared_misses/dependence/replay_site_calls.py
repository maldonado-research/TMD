"""Count anonymous split-call tables per site in Ji et al., Tables S2 and S5."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

SOURCES = {
    "S2": ("016", "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4"),
    "S5": ("019", "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394"),
}


def worksheet(path, key):
    number, digest = SOURCES[key]
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"Unexpected digest for Table {key}.")
    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        return list(workbook[f"{key}_Table"].values)
    finally:
        workbook.close()


def replay(s2_path, s5_path):
    variants = worksheet(s2_path, "S2")
    calls = worksheet(s5_path, "S5")
    alt = {row[0]: row[5:7] for row in variants[5:] if row[1] == "Flower#2"}
    names = [name for name in calls[3][3:] if name]
    pairs = {}
    for row in calls[4:]:
        if row[1] in {"a", "b"}:
            by_side = pairs.setdefault(row[0], {})
            if row[1] in by_side:
                raise ValueError("Duplicate split label.")
            by_side[row[1]] = row[3:3 + len(names)]
    if len(names) != 37 or set(names) != set(alt) or len(pairs) != 20:
        raise ValueError("Unexpected site or pair roster.")
    if any(set(sides) != {"a", "b"} for sides in pairs.values()):
        raise ValueError("A tissue is missing a split.")
    bins = Counter()
    tissue_counts = {name: Counter() for name in pairs}
    order = [(True, True), (True, False), (False, True), (False, False)]
    for col, name in enumerate(names):
        ref, positive = alt[name]
        counts = Counter()
        for tissue, sides in pairs.items():
            a, b = sides["a"][col], sides["b"][col]
            if ref == positive or any(x not in (ref, positive) for x in (a, b)):
                raise ValueError("Unexpected source call.")
            state = (a == positive, b == positive)
            counts[state] += 1
            tissue_counts[tissue][state] += 1
        bins[tuple(counts[state] for state in order)] += 1
    tissue_bins = Counter(tuple(counts[state] for state in order) for counts in tissue_counts.values())
    return {
        "article": "https://doi.org/10.1371/journal.pgen.1011829",
        "source_workbooks": {key: {"sha256": sha, "url":
            f"https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s{n}.xlsx"}
            for key, (n, sha) in SOURCES.items()},
        "columns": ["both", "a_only", "b_only", "neither", "multiplicity"],
        "site_tables": [list(table) + [count] for table, count in sorted(bins.items())],
        "tissue_tables": [list(table) + [count] for table, count in sorted(tissue_bins.items())],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table_s2", type=Path)
    parser.add_argument("table_s5", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.table_s2, args.table_s5), indent=2))
