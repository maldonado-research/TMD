"""Check pairwise leaf patterns and compute the smallest laminar subsets in the DHQ1 table."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

# Independent transcription of Wang S2, joined by chromosome and position to Ji S2.
# Rows use Ji ID, chromosome, position, change, sorted semicolon-delimited leaf labels.
CANONICAL_SHA256 = "15296a6f0185ad2617ce08e14bd8e5f84a51998f443959bbe7447b240ad286b9"


def read_roster(path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = sorted(csv.DictReader(handle, delimiter="\t"),
                      key=lambda r: (r["chromosome"], int(r["position"])))
    groups = {}
    canonical = []
    for index, row in enumerate(rows, start=71):
        marker = f"M{index}"
        listed = row["listed_leaves"].split(";")
        carriers = frozenset(listed)
        if "" in carriers or len(carriers) != len(listed):
            raise ValueError(f"Invalid leaf list for {marker}")
        groups[marker] = carriers
        canonical.append("\t".join((marker, row["chromosome"], row["position"],
                                    row["change"], ";".join(sorted(carriers)))))
    digest = hashlib.sha256(("\n".join(canonical) + "\n").encode()).hexdigest()
    if digest != CANONICAL_SHA256:
        raise ValueError("Carrier rows differ from the independent source transcription")
    return groups


def relation(a, b):
    if not a or not b:
        return "empty"
    if a == b:
        return "same"
    if a.isdisjoint(b):
        return "disjoint"
    if a <= b or b <= a:
        return "strict_nonempty_nest"
    return "cross"


def marker_repairs(edges):
    # Markers outside the crossing edges cannot improve a minimum cover.
    vertices = sorted({m for edge in edges for m in edge})
    for size in range(len(vertices) + 1):
        covers = [subset for subset in combinations(vertices, size)
                  if all(set(subset).intersection(edge) for edge in edges)]
        if covers:
            break
    matching = next((m for m in combinations(edges, size)
                     if len({vertex for edge in m for vertex in edge}) == 2 * size), None)
    if matching is None:
        raise AssertionError("No matching certificate of this size in the study graph")
    return {"minimum_omissions": size, "optimal_marker_omissions": covers,
            "disjoint_crossing_pairs_certifying_minimum": matching}


def leaf_repairs(groups, edges, require_nonempty=False):
    # Restriction can only remove crossings. At a surviving crossing every solution
    # must discard one whole remaining region: left only, intersection, or right only.
    best = None
    answers = set()
    seen = set()

    def visit(dropped):
        nonlocal best, answers
        if dropped in seen or (best is not None and len(dropped) > best):
            return
        seen.add(dropped)
        if require_nonempty and any(pattern <= dropped for pattern in groups.values()):
            return
        for left, right in edges:
            a, b = groups[left] - dropped, groups[right] - dropped
            regions = (a - b, a & b, b - a)
            if all(regions):
                for region in sorted(regions, key=len):
                    visit(dropped | region)
                return
        if best is None or len(dropped) < best:
            best, answers = len(dropped), set()
        answers.add(dropped)

    visit(frozenset())
    return {"minimum_omissions": best, "optima": [
        {"omitted_leaves": list(drop), "markers_reduced_to_empty": [
            marker for marker, group in groups.items() if group.issubset(drop)]}
        for drop in sorted(tuple(sorted(s)) for s in answers)]}


def run(groups):
    pairs = list(combinations(groups, 2))
    leaves = sorted(frozenset.union(*groups.values()))
    counts = Counter(relation(groups[i], groups[j]) for i, j in pairs)
    edges = [(i, j) for i, j in pairs if relation(groups[i], groups[j]) == "cross"]
    nested = [(i, j) for i, j in pairs if relation(groups[i], groups[j]) == "strict_nonempty_nest"]

    # A strict nonempty nest requires a representative in the inner set and in the
    # difference. A crossing requires a representative in each of three regions.
    stable_nests = []
    for left, right in nested:
        inner, outer = sorted((left, right), key=lambda m: len(groups[m]))
        if min(len(groups[inner]), len(groups[outer] - groups[inner])) > 1:
            stable_nests.append([inner, outer])
    stable_crosses = []
    for left, right in edges:
        a, b = groups[left], groups[right]
        if min(len(a - b), len(a & b), len(b - a)) > 1:
            stable_crosses.append([left, right])

    lost_nests = {}
    lost_crosses = {}
    stable_by_direct_omission = set(nested)
    for leaf in leaves:
        erased = [(i, j) for i, j in nested
                  if relation(groups[i] - {leaf}, groups[j] - {leaf}) != "strict_nonempty_nest"]
        lost_nests[leaf] = len(erased)
        stable_by_direct_omission.difference_update(erased)
        lost_crosses[leaf] = sum(relation(groups[i] - {leaf}, groups[j] - {leaf}) != "cross"
                                 for i, j in edges)
    assert {frozenset(pair) for pair in stable_by_direct_omission} == {frozenset(pair) for pair in stable_nests}
    marker_result = marker_repairs(edges)
    maximum_nested_omissions = max(lost_nests.values())
    maximum_crossing_omissions = max(lost_crosses.values())
    a, b = groups["M92"], groups["M101"]
    preserving_singletons = ["M84", "M100", "M80"]
    for marker, region in zip(preserving_singletons, (a - b, a & b, b - a)):
        assert len(groups[marker]) == 1 and groups[marker] <= region
    return {
        "canonical_roster_sha256": CANONICAL_SHA256,
        "markers": len(groups), "leaves": len(leaves), "distinct_patterns": len(set(groups.values())),
        "unordered_pairs": dict(sorted(counts.items())),
        "strict_nests_preserved_after_any_one_leaf_omission_inner_outer": stable_nests,
        "crossings_preserved_after_any_one_leaf_omission": stable_crosses,
        "max_strict_nests_lost_by_one_omission": maximum_nested_omissions,
        "leaves_attaining_max_nest_loss": [u for u in leaves if lost_nests[u] == maximum_nested_omissions],
        "max_crossings_removed_by_one_omission": maximum_crossing_omissions,
        "leaves_attaining_max_crossing_removal": [u for u in leaves if lost_crosses[u] == maximum_crossing_omissions],
        "marker_restriction": marker_result,
        "leaf_restriction_allowing_empty_markers": leaf_repairs(groups, edges),
        "leaf_restriction_preserving_all_markers": leaf_repairs(groups, edges, require_nonempty=True),
        "witness_for_impossible_nonempty_restriction": {
            "crossing_pair": ["M92", "M101"],
            "private_leaf_markers_in_left_only_both_right_only": preserving_singletons}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(read_roster(args.carriers)), indent=2))
