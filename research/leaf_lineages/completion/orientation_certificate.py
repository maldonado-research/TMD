"""Certify minimum additions using orientations of original crossing pairs.

For each choice of containing set on every original crossing, take the
transitive closure of inclusion constraints. If necessary, repeat the
partition at one additional crossing. This small-depth certificate can
be inconclusive on other data; the reported extrema require equality
between a relaxed lower bound and a feasible table.
"""
import argparse
import csv
import json
from itertools import combinations, product
from pathlib import Path


M71 = "Pp01:2130859"
M101 = "Pp04:21561355"


def read_table(path):
    markers, rows = [], []
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for row in reader:
            key = f"{row['chromosome']}:{row['position']}"
            members = row["listed_leaves"].split(";")
            if key in markers or not all(members) or len(set(members)) != len(members):
                raise ValueError("Invalid or duplicate marker or leaf identifier.")
            markers.append(key)
            rows.append(set(members))
    leaves = sorted(set.union(*rows))
    bits = {leaf: 1 << i for i, leaf in enumerate(leaves)}
    return markers, leaves, tuple(sum(bits[leaf] for leaf in row) for row in rows)


def crossings(rows):
    for i, j in combinations(range(len(rows)), 2):
        a, b = rows[i], rows[j]
        if (a & b) and (a & ~b) and (b & ~a):
            yield (i, j)


def containing_closure(original, arcs):
    """Collect the original observations from every directed predecessor."""
    reach = [1 << i for i in range(len(original))]
    for subset, superset in arcs:
        reach[superset] |= 1 << subset
    for via in range(len(original)):
        for target, predecessors in enumerate(reach):
            if predecessors & (1 << via):
                reach[target] |= reach[via]
    closure = list(original)
    for target, predecessors in enumerate(reach):
        extra = predecessors ^ (1 << target)
        while extra:
            bit = extra & -extra
            closure[target] |= original[bit.bit_length()-1]
            extra ^= bit
    return tuple(closure)


def count_additions(original, rows):
    return sum((expanded & ~old).bit_count() for old, expanded in zip(original, rows))


def certify(original, required=()):
    """Return unique optimal tables if the one-refinement certificate succeeds."""
    edges = list(crossings(original))
    first_lower = lower = float("inf")
    first_min_orientations = 0
    best_cost = float("inf")
    best = set()
    for choices in product((False, True), repeat=len(edges)):
        arcs = tuple((j, i) if flip else (i, j)
                     for (i, j), flip in zip(edges, choices)) + tuple(required)
        table = containing_closure(original, arcs)
        first_cost = count_additions(original, table)
        if first_cost < first_lower:
            first_lower, first_min_orientations = first_cost, 0
        if first_cost == first_lower:
            first_min_orientations += 1
        if first_cost > best_cost:
            continue
        residual = next(crossings(table), None)
        children = (table,) if residual is None else tuple(
            containing_closure(original, arcs + (direction,))
            for direction in (residual, residual[::-1]))
        for child in children:
            cost = count_additions(original, child)
            lower = min(lower, cost)
            if cost > best_cost or next(crossings(child), None) is not None:
                continue
            if cost < best_cost:
                best_cost, best = cost, set()
            best.add(child)
    if not best or best_cost != lower:
        raise ValueError("One residual crossing did not suffice to certify an optimum.")
    return int(lower), sorted(best), int(first_lower), first_min_orientations


def report(path):
    markers, leaves, original = read_table(path)
    m, n = markers.index(M71), markers.index(M101)
    def format_cells(cells):
        return {markers[i]: [leaf for j, leaf in enumerate(leaves) if row & (1 << j)]
                for i, row in enumerate(cells) if row}
    result = {"original_crossings": len(list(crossings(original))),
              "original_orientations_per_scenario": 2 ** len(list(crossings(original)))}
    for label, requirements in (("unrestricted", ()), ("M101_within_M71", ((n, m),)),
                                ("M101_equals_M71", ((m, n), (n, m)))):
        minimum, solutions, first_lower, n_first = certify(original, requirements)
        added = [tuple(row & ~start for row, start in zip(t, original)) for t in solutions]
        common = list(added[0])
        for delta in added[1:]:
            common = [a & b for a,b in zip(common, delta)]
        relation = set()
        for sol in solutions:
            if sol[m] == sol[n]:
                relationship = "equal"
            elif not (sol[m] & ~sol[n]):
                relationship = "M71_strictly_within_M101"
            elif not (sol[n] & ~sol[m]):
                relationship = "M101_strictly_within_M71"
            else:
                raise ValueError("The two original overlapping markers must be nested.")
            relation.add((relationship, sol[m].bit_count(), sol[n].bit_count()))
        result[label] = {"first_closure_lower_bound": first_lower,
                         "orientations_attaining_first_lower_bound": n_first,
                         "minimum_added_memberships": minimum, "distinct_optimal_tables": len(solutions),
                         "optimal_M71_M101_relation_and_sizes": sorted(relation),
                         "number_of_common_additions": sum(mask.bit_count() for mask in common),
                         "additions_common_to_all_optima": format_cells(common),
                         "other_additions_by_optimum": [format_cells(tuple(mask & ~forced for mask,forced in zip(d, common)))
                                                       for d in added]}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    args = parser.parse_args()
    print(json.dumps(report(args.carriers), indent=2))
