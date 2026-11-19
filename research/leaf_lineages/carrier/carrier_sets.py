"""Compare pairs of listed carrier sets in the 2016 DHQ1 peach leaf inventory."""
import argparse
from collections import Counter
import csv
from itertools import combinations
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
M71 = "Pp01:2130859"
M101 = "Pp04:21561355"
RELATIONS = ("equal", "strict_containment", "disjoint", "crossing")


def table(path, header):
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if reader.fieldnames != list(header):
            raise ValueError(f"Unexpected columns in {path.name}")
        return list(reader)


def main_branch(leaf):
    match = re.fullmatch(r"DHQ1_(B[1-4])(?:-[0-9]+)*-L[0-9]+", leaf)
    if not match:
        raise ValueError(f"Unrecognized DHQ1 leaf label: {leaf}")
    return match.group(1)


def read_frame(roster_path, carriers_path):
    samples = table(roster_path, ("sample_id", "mapped_depth", "genome_pct_depth_at_least_five"))
    roster = {r["sample_id"] for r in samples}
    if len(roster) != len(samples) or not roster:
        raise ValueError("The S1 leaf roster is empty or contains duplicates.")
    for leaf in roster:
        main_branch(leaf)
    variants = {}
    for row in table(carriers_path, ("chromosome", "position", "change", "listed_leaves")):
        marker = f"{row['chromosome']}:{int(row['position'])}"
        members = row["listed_leaves"].split(";")
        leaves = frozenset(members)
        if marker in variants or len(leaves) != len(members) or not leaves <= roster:
            raise ValueError(f"Duplicate or unmatched record for {marker}")
        variants[marker] = leaves
    return samples, roster, variants


def compare(left, right):
    if left == right:
        return "equal"
    if left < right or right < left:
        return "strict_containment"
    if left.isdisjoint(right):
        return "disjoint"
    return "crossing"


def four_cells(a, b, roster):
    return {"both": len(a & b), "first_only": len(a - b), "second_only": len(b - a),
            "neither_listed": len(roster - a - b)}


def full_counts(counter):
    return {key: counter[key] for key in RELATIONS}


def analyze(samples, roster, variants):
    branch = {}
    for marker, leaves in variants.items():
        branches = {main_branch(leaf) for leaf in leaves}
        if len(branches) != 1:
            raise ValueError(f"This dataset's site is not restricted to one main branch: {marker}")
        branch[marker] = branches.pop()
    relation_totals = Counter()
    by_branch = {}
    conflicts = []
    for a, b in combinations(variants, 2):
        A, B = variants[a], variants[b]
        relation = compare(A, B)
        relation_totals[relation] += 1
        group = branch[a] if branch[a] == branch[b] else "different_branches"
        by_branch.setdefault(group, Counter())[relation] += 1
        if relation == "crossing":
            conflicts.append({"first": a, "second": b, **four_cells(A, B, roster)})
    historical = four_cells(variants[M71], variants[M101], roster)
    return {
        "source_individual": "DHQ1",
        "source_organ": "leaf",
        "distinct_leaf_roster": len(roster),
        "distinct_leaves_listed_across_sites": len(set().union(*variants.values())),
        "leaf_count_by_main_branch": dict(sorted(Counter(main_branch(s) for s in roster).items())),
        "site_count": len(variants),
        "site_count_by_main_branch": dict(sorted(Counter(branch.values()).items())),
        "listed_site_leaf_memberships": sum(map(len, variants.values())),
        "distinct_carrier_sets": len(set(variants.values())),
        "number_of_sites_by_listed_leaf_count": dict(sorted(Counter(map(len, variants.values())).items())),
        "leaf_fraction_genome_covered_at_depth_five_percent_range": [
            min(float(x["genome_pct_depth_at_least_five"]) for x in samples),
            max(float(x["genome_pct_depth_at_least_five"]) for x in samples)],
        "unordered_site_pairs": sum(relation_totals.values()),
        "relations": full_counts(relation_totals),
        "relations_by_main_branch": {b: full_counts(counts) for b, counts in sorted(by_branch.items())},
        "crossing_pairs": conflicts,
        "historical_M71_then_M101_cells": historical,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=HERE / "sample_roster.tsv")
    parser.add_argument("--carriers", type=Path, default=HERE / "carriers.tsv")
    args = parser.parse_args()
    print(json.dumps(analyze(*read_frame(args.roster, args.carriers)), indent=2))
