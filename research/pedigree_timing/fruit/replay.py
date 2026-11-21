"""Compare parental leaf and fruit calls and calculate finite-roster sampling coverage."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from fractions import Fraction
from math import comb
from pathlib import Path


def read(directory, name):
    with (directory / name).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def branch_for_map(tree, branch):
    if tree == "SR":
        if branch == "A":
            return None
        if branch == "B":
            return "B1"
    return branch


def positive(row, depth=1, alt=1):
    return int(row["source_call"]) == 1 and int(row["depth"]) >= depth and int(row["alt_reads"]) >= alt


def rarefaction(n, successes):
    # Uniform unordered subsets of the observed fruits with this tissue.
    rows = {}
    threshold = None
    for m in range(1, n+1):
        total = comb(n, m)
        recovered = sum(Fraction(total-comb(n-hits, m), total) for hits in successes.values())
        if 10*recovered >= 9*len(successes) and threshold is None:
            threshold = m
        if m in {1, 5, 10, n}:
            rows[m] = round(float(recovered), 5)
    return {"expected_distinct_calls": rows, "fruits_for_90pct_of_observed_markers_in_expectation": threshold}


def branch_comparison(tree, rows, leaf, depth, alt):
    branch_markers = set()
    fruit_markers = set()
    for r in rows:
        b = branch_for_map(tree, r["branch"])
        if b and positive(r, depth, alt):
            key = (r["marker"], b)
            if key not in leaf:
                raise ValueError(f"Unmapped leaf branch {key}")
            branch_markers.add(key)
            fruit_markers.add((*key, r["fruit"]))
    unmatched = {pair for pair in branch_markers if leaf[pair] == 0}
    return {
        "distinct_markers": len({m for m,b in branch_markers}),
        "branch_marker_calls": len(branch_markers),
        "branch_marker_calls_without_leaf_call": len(unmatched),
        "markers_with_at_least_one_branch_lacking_leaf_call": len({m for m,b in unmatched}),
        "positive_fruit_marker_measurements": len(fruit_markers),
        "positive_fruit_markers_without_corresponding_leaf_branch_call":
            sum((m,b) in unmatched for m,b,f in fruit_markers),
    }


def tissue_summary(tree, rows, leaf):
    fruits = {(r["branch"], r["fruit"]) for r in rows}
    markers = {r["marker"] for r in rows}
    assert len(rows) == len(fruits)*len(markers)
    successes = Counter(r["marker"] for r in rows if positive(r))
    assert successes
    return {
        "distinct_fruits_with_sampled_tissue": len(fruits),
        "fruit_marker_combinations": len(rows),
        "positive_depth": sum(int(r["depth"]) > 0 for r in rows),
        "distinct_markers_with_positive_call": len(successes),
        "markers_positive_in_one_fruit": sum(c == 1 for c in successes.values()),
        "positive_fruit_marker_measurements": sum(successes.values()),
        "rarefaction": rarefaction(len(fruits), successes),
        "matched_branch": branch_comparison(tree, rows, leaf, 1, 1),
        "matched_branch_at_depth_20_and_3_alternate_reads": branch_comparison(tree, rows, leaf, 20, 3),
    }


def compare_tissues(rows, tissue_first, tissue_second):
    paired = defaultdict(dict)
    for r in rows:
        if r["tissue"] in (tissue_first, tissue_second):
            paired[r["marker"], r["branch"], r["fruit"]][r["tissue"]] = r
    counts = Counter()
    for tissues in paired.values():
        if not all(t in tissues for t in (tissue_first, tissue_second)):
            counts["incomplete_tissue_pair"] += 1
            continue
        a, b = tissues[tissue_first], tissues[tissue_second]
        if min(int(a["depth"]),int(b["depth"])) == 0:
            counts["at_least_one_zero_depth"] += 1
            continue
        yes_a, yes_b = positive(a), positive(b)
        category = ("both" if yes_b else "first_only") if yes_a else ("second_only" if yes_b else "neither")
        counts[category] += 1
    return dict(sorted(counts.items()))


def analyze(directory):
    fruits = read(directory,"fruit_counts.tsv")
    leaves = read(directory,"leaf_calls.tsv")
    result = {}
    for tree in ("DG","SR"):
        rows = [r for r in fruits if r["tree"] == tree]
        leaf = {(r["marker"],r["branch"]): int(r["leaves_with_call"]) for r in leaves if r["tree"] == tree}
        by_tissue = defaultdict(list)
        for row in rows:
            by_tissue[row["tissue"]].append(row)
        tissue_pair = ("cotyledon","endocarpe") if tree == "DG" else ("embryo sac","pericarpe")
        result[tree] = {
            "distinct_measurements": len(rows),
            "distinct_fruits": len({(r["branch"],r["fruit"]) for r in rows}),
            "any_tissue_positive_markers": len({r["marker"] for r in rows if positive(r)}),
            "by_tissue": {k: tissue_summary(tree, group, leaf) for k,group in sorted(by_tissue.items())},
            "matched_tissues": {"tissues": tissue_pair,"counts": compare_tissues(rows,*tissue_pair)},
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    print(json.dumps(analyze(parser.parse_args().directory), indent=2))
