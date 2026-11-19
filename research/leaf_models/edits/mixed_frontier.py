"""Exact two-cost frontier for leaf-marker tables under a laminar single-lineage model."""
import argparse
import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path


PAIR = ("Pp01:2130859", "Pp04:21561355")
FOCAL_LEAF = "DHQ1_B1-1-L1"


def load(path):
    columns = defaultdict(dict)
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            leaves = set(row["listed_leaves"].split(";"))
            branches = {leaf.split("_", 1)[1].split("-", 1)[0] for leaf in leaves}
            if len(branches) != 1:
                raise ValueError("A source marker spans main branches")
            locus = f"{row['chromosome']}:{row['position']}"
            branch = branches.pop()
            if locus in columns[branch]:
                raise ValueError(f"Duplicate marker {locus}")
            columns[branch][locus] = leaves
    return columns


def path_families(size):
    """Enumerate a rooted tree on all markers and one fixed ancestral root."""
    root = size
    # A node's parent is any other marker or the artificial root.
    choices = [[j for j in range(size + 1) if j != i] for i in range(size)]
    for parents in itertools.product(*choices):
        paths = [0]
        for start in range(size):
            node, seen = start, 0
            while node != root and not (seen & (1 << node)):
                seen |= 1 << node
                node = parents[node]
            if node != root:
                break
            paths.append(seen)
        else:
            yield tuple(paths)


def keep_frontier(costs):
    """Keep (removals, additions) incomparable in the product order."""
    best_add = float("inf")
    result = set()
    for removed, added in sorted(costs):
        if added < best_add:
            best_add = added
            result.add((removed, added))
    return result


def summarize(flags):
    # Classes are exclusive. Emptied columns are reported separately.
    left_only, right_only, shared = ((flags & b) != 0 for b in (1, 2, 4))
    if shared:
        if left_only and right_only:
            raise AssertionError("Crossing cannot occur on a tree")
        if left_only:
            return "M101_proper_nonempty_subset_of_M71"
        if right_only:
            return "M71_proper_nonempty_subset_of_M101"
        return "equal_nonempty"
    if left_only and right_only:
        return "disjoint_nonempty"
    if left_only:
        return "M101_empty_only"
    if right_only:
        return "M71_empty_only"
    return "both_empty"


def pair_region(mask, bitpair):
    if not bitpair:
        return 0
    a, b = bitpair
    return (0, 1, 2, 4)[bool(mask & a) + 2 * bool(mask & b)]


def rows_for_branch(columns):
    sites = [site for site, leaves in columns.items() if len(leaves) > 1]
    leaves = sorted(set.union(*columns.values()))
    masks = [sum(1 << i for i, site in enumerate(sites) if leaf in columns[site]) for leaf in leaves]
    pair = tuple(1 << sites.index(site) for site in PAIR) if PAIR[0] in columns else ()
    return sites, leaves, masks, pair


def tree_rows(paths, masks, bitpair, focal_row=None, require_all_markers=False):
    options = {}
    rows = [(source, i == focal_row) for i, source in enumerate(masks)]
    for source, is_focal in set(rows):
        by_region = defaultdict(set)
        for target in paths:
            cost = ((source & ~target).bit_count(), (target & ~source).bit_count())
            focal_flag = 8 if is_focal and target & bitpair[1] else 0
            occupancy = target << 4 if require_all_markers else 0
            by_region[pair_region(target, bitpair) | focal_flag | occupancy].add(cost)
        options[source, is_focal] = [(region, r, a) for region, costs in by_region.items()
                           for r, a in keep_frontier(costs)]
    states = {0: {(0, 0)}}
    for row in rows:
        new = defaultdict(set)
        for flags, partial in states.items():
            for region, dr, da in options[row]:
                new[flags | region].update((r + dr, a + da) for r, a in partial)
        states = {flags: keep_frontier(costs) for flags, costs in new.items()}
    if require_all_markers:
        all_markers = (1 << (len(paths) - 1)) - 1
        return {flags & 15: costs for flags, costs in states.items() if flags >> 4 == all_markers}
    return states


def branch_frontiers(columns, require_all_markers=False):
    sites, leaves, masks, bitpair = rows_for_branch(columns)
    focal_row = leaves.index(FOCAL_LEAF) if bitpair else None
    by_relation = defaultdict(set)
    count = 0
    for paths in path_families(len(sites)):
        count += 1
        for flags, costs in tree_rows(paths, masks, bitpair, focal_row, require_all_markers).items():
            name = (summarize(flags), bool(flags & 8)) if bitpair else ("all", False)
            by_relation[name].update(costs)
    costs = keep_frontier(set.union(*by_relation.values()))
    return costs, {k: keep_frontier(v) for k, v in by_relation.items()}, count


def combine(frontiers):
    running = {(0, 0)}
    for frontier in frontiers:
        running = keep_frontier((r + u, a + v) for r, a in running for u, v in frontier)
    return running


def analyze(columns, require_all_markers=False):
    parts = {}
    b1_relations = {}
    trees = {}
    for branch, markers in sorted(columns.items()):
        costs, relations, trees[branch] = branch_frontiers(markers, require_all_markers)
        parts[branch] = costs
        if PAIR[0] in markers:
            b1_relations = relations
            pair_branch = branch
    total = combine(parts.values())
    other_branches = [f for b, f in parts.items() if b != pair_branch]
    relation_costs = {rel: combine([costs, *other_branches]) for rel, costs in b1_relations.items()}
    possible = []
    for r, a in sorted(total):
        classifications = sorted((rel, focal) for (rel, focal), frontier in relation_costs.items()
                                 if (r, a) in frontier)
        possible.append({"removed": r, "added": a,
                         "possible_M71_M101_relations": sorted({rel for rel, _ in classifications}),
                         "joint_relation_and_focal_M101_state":
                             [{"relation": rel, "present_in_completed_table": focal}
                              for rel, focal in classifications]})
    focal_costs = {str(focal).lower(): sorted(keep_frontier(
        cost for (rel, present), frontier in relation_costs.items() if present == focal
        for cost in frontier)) for focal in (False, True)}
    return {"rooted_marker_trees_evaluated_by_branch": trees,
            "branch_frontiers_removed_added": {b: sorted(f) for b, f in parts.items()},
            "focal_leaf": FOCAL_LEAF, "focal_site": PAIR[1],
            "frontier_constrained_by_focal_M101_presence": focal_costs,
            "global_frontier": possible}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    parser.add_argument("--require-all-markers", action="store_true",
                        help="Check attainment using at least one native-branch leaf per marker")
    args = parser.parse_args()
    print(json.dumps(analyze(load(args.carriers), args.require_all_markers), indent=2))
