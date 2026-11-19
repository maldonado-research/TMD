"""Check the tree DP against every observed and corrected 3-leaf, 3-marker table."""
from collections import defaultdict
from itertools import combinations, product

from mixed_frontier import keep_frontier, path_families, tree_rows


def pairwise_compatible(rows):
    sets = [{i for i, mask in enumerate(rows) if mask & (1 << j)} for j in range(3)]
    return all(a.isdisjoint(b) or a <= b or b <= a for a, b in combinations(sets, 2))


def witness_bits(rows):
    # Distinguish the two marker-only regions, their overlap, and M101 in the first row.
    flags = 8 if rows[0] & 2 else 0
    for row in rows:
        region = row & 3
        if region:
            flags |= 1 << (region - 1)
    return flags


def direct_frontier(points):
    return {(r, a) for r, a in points
            if not any((u, v) != (r, a) and u <= r and v <= a for u, v in points)}


def run(require_all_markers):
    matrices = list(product(range(8), repeat=3))
    compatible = [(rows, witness_bits(rows)) for rows in matrices if pairwise_compatible(rows)
                  and (not require_all_markers or rows[0] | rows[1] | rows[2] == 7)]
    families = list(path_families(3))
    for source in matrices:
        exact = defaultdict(set)
        for target, flags in compatible:
            removals = sum((old & ~new).bit_count() for old, new in zip(source, target))
            additions = sum((new & ~old).bit_count() for old, new in zip(source, target))
            exact[flags].add((removals, additions))
        actual = defaultdict(set)
        for paths in families:
            for flags, costs in tree_rows(paths, source, (1, 2), focal_row=0, require_all_markers=require_all_markers).items():
                actual[flags].update(costs)
        assert {k: direct_frontier(v) for k, v in exact.items()} == {
            k: keep_frontier(v) for k, v in actual.items()}, source
    print(f"Matched all {len(matrices)} observed three-by-three tables against "
          f"{len(compatible)} compatible corrected tables, including joint marker and focal states.")


if __name__ == "__main__":
    for require_all_markers in (False, True):
        run(require_all_markers)
