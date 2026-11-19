"""Certify a minimum perfect-phylogeny row split of the DHQ1 bulk-leaf matrix."""
import argparse
import csv
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def read_table(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def maximum_antichain(observed, supports):
    """Use only markers in this leaf. No two incomparable supports can share a lineage."""
    for size in range(len(observed), 0, -1):
        for markers in combinations(sorted(observed), size):
            if all(not (supports[a] <= supports[b] or supports[b] <= supports[a])
                   for a, b in combinations(markers, 2)):
                return markers
    return ()


def lineage_patterns(leaf, observed, supports):
    """Build a witness from all inclusion-minimal multi-leaf supports at this leaf."""
    shared = {supports[m] for m in observed if len(supports[m]) > 1}
    terminals = sorted((x for x in shared if not any(y < x for y in shared)),
                       key=lambda leaves: tuple(sorted(leaves)))
    signatures = [
        {m for m in observed if node <= supports[m]}
        for node in terminals
    ] or [set()]
    local = {m for m in observed if supports[m] == {leaf}}
    signatures[0].update(local)
    return signatures


def numbered(values):
    return [f"M{i}" for i in sorted(values)]


def certify(carriers, roster):
    rows = read_table(carriers)
    leaves = sorted(row["sample_id"] for row in read_table(roster))
    # IDs M71--M118 follow the coordinate order in Ji et al. S2.
    sites = sorted(rows, key=lambda row: (row["chromosome"], int(row["position"])))
    supports = {i: frozenset(row["listed_leaves"].split(";")) for i, row in enumerate(sites, 71)}
    assert all(supports.values()) and set().union(*supports.values()) <= set(leaves)
    assignments = {}
    columns = defaultdict(set)
    histogram = Counter()
    per_branch = defaultdict(Counter)
    for leaf in leaves:
        observed = {m for m, support in supports.items() if leaf in support}
        lower = maximum_antichain(observed, supports)
        signatures = lineage_patterns(leaf, observed, supports)
        assert set.union(*signatures) == observed, leaf
        assert len(signatures) == max(1, len(lower)), leaf
        for i, sig in enumerate(signatures):
            for marker in sig:
                columns[marker].add((leaf, i))
        assignments[leaf] = {"incomparable_markers": numbered(lower),
                             "lineage_signatures": [numbered(s) for s in signatures]}
        histogram[len(signatures)] += 1
        per_branch[leaf.split("-")[0].split("_")[-1]][len(signatures)] += 1

    assert set(columns) == set(supports)
    relations = Counter()
    for a, b in combinations(sorted(columns), 2):
        x, y = columns[a], columns[b]
        if x == y:
            relations["identical"] += 1
        elif x < y or y < x:
            relations["nested"] += 1
        elif x.isdisjoint(y):
            relations["disjoint"] += 1
        else:
            raise AssertionError(f"expanded columns still cross at {a} and {b}")
    total = sum(n*k for k, n in histogram.items())
    return {
        "input_sha256": {"carriers": sha256(carriers.read_bytes()).hexdigest(),
                         "roster": sha256(roster.read_bytes()).hexdigest()},
        "markers": len(supports), "bulk_leaves": len(leaves),
        "minimum_signature_occurrences": total, "minimum_extra_occurrences": total-len(leaves),
        "minimum_mixed_leaves": len(leaves)-histogram[1],
        "smallest_possible_maximum_per_leaf": max(histogram),
        "distribution_by_minimum_signatures": dict(sorted(histogram.items())),
        "distribution_by_main_branch": {b: dict(sorted(counts.items())) for b, counts in sorted(per_branch.items())},
        "pair_relations_in_this_expanded_witness": dict(sorted(relations.items())),
        "leaves": assignments,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    parser.add_argument("roster", type=Path)
    args = parser.parse_args()
    print(json.dumps(certify(args.carriers, args.roster), indent=2))
