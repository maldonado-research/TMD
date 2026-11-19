"""Find the minimum bulk mixture directly from the numbered Wang Figure 4 icons."""
from collections import Counter
from itertools import combinations, product
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGURE = HERE.parents[1] / "leaf_lineages/topology/figure4_leaf_icons.tsv"


def load_diagram():
    with FIGURE.open() as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    branches = {}
    for row in rows:
        location = row["location"]
        calls = row["marker_lists_on_drawn_leaf_icons"]
        branch = location.split("-")[0]
        for label in calls.split(";"):
            branches.setdefault(branch, []).append(frozenset(map(int, label.split(","))))
    return branches


def possible_forests(supports):
    # Every ancestor has a strict superset of descendant carriers after merging
    # duplicate columns. Zero means that a marker attaches directly to the root.
    choices = [[0] + [j for j, other in enumerate(supports, 1) if cols < other]
               for cols in supports]
    return product(*choices)


def branch_result(rows):
    sites = sorted(set.union(*map(set, rows)))
    columns = {site: frozenset(i for i, calls in enumerate(rows) if site in calls)
               for site in sites}
    repeated = sorted({col for col in columns.values() if len(col) >= 2},
                      key=lambda col: (len(col), sorted(col)))
    observed = [{i for i, col in enumerate(repeated, 1) if leaf in col}
                for leaf in range(len(rows))]
    # An antichain of carriers observed in one leaf needs a separate path for
    # each member, because single-origin events on one path must be comparable.
    lower = []
    for calls in observed:
        maximum = 1
        for size in range(2, len(calls) + 1):
            for group in combinations(calls, size):
                if all(not (repeated[i-1] <= repeated[j-1] or repeated[j-1] <= repeated[i-1])
                       for i, j in combinations(group, 2)):
                    maximum = size
                    break
        lower.append(maximum)
    objectives = []
    simultaneous = 0
    for forest in possible_forests(repeated):
        parts = []
        for calls in observed:
            parents = {forest[site-1] for site in calls}
            parts.append(max(1, len(calls - parents)))
        if parts == lower:
            simultaneous += 1
        objectives.append((sum(parts), sum(n > 1 for n in parts), max(parts)))
    assert simultaneous and tuple(map(min, zip(*objectives))) == (
        sum(lower), sum(n > 1 for n in lower), max(lower))
    # All singleton markers in a leaf can be attached as a terminal chain on
    # one of its existing paths, including a leaf initially at the root.
    return {
        "leaves": len(rows), "distinct_original_markers": len(sites),
        "distinct_multileaf_supports": len(repeated),
        "labeled_forests_after_reduction": len(objectives),
        "forests_attaining_every_leaf_lower_bound": simultaneous,
        "leaf_counts_by_minimum_paths": dict(sorted(Counter(lower).items())),
        "minimum_parts": sum(lower),
    }


def main():
    results = {branch: branch_result(rows) for branch, rows in load_diagram().items()}
    counts = Counter()
    for r in results.values():
        counts.update(r["leaf_counts_by_minimum_paths"])
    print(json.dumps({"analysis": "Exact OR mixture on the numbered Figure 4 leaf records",
                      "branches": results, "combined_histogram": dict(sorted(counts.items())),
                      "total_minimum_parts":sum(n * count for n, count in counts.items()),
                      "leaves_requiring_mixture":sum(count for n,count in counts.items() if n > 1)},
                     indent=2))


if __name__ == "__main__":
    main()
