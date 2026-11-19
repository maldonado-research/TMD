"""Exhibit and check one whole-table witness for each relationship at the first tradeoff."""
import argparse
from itertools import combinations, product
import json
from pathlib import Path

from mixed_frontier import (FOCAL_LEAF, PAIR, branch_frontiers, load, path_families,
                            rows_for_branch, summarize)


def fit_branch(markers, budget, required_relation):
    sites, leaves, source, bitpair = rows_for_branch(markers)
    for paths in path_families(len(sites)):
        states = {(0, 0, 0): ()}
        for leaf, old in zip(leaves, source):
            fresh = {}
            for new in paths:
                if bitpair and leaf == FOCAL_LEAF and new & bitpair[1]:
                    continue
                dr, da = (old & ~new).bit_count(), (new & ~old).bit_count()
                if bitpair:
                    a, b = bitpair
                    region = {(False, False): 0, (True, False): 1,
                              (False, True): 2, (True, True): 4}[bool(new & a), bool(new & b)]
                else:
                    region = 0
                for (r, a, seen), history in states.items():
                    if r + dr <= budget[0] and a + da <= budget[1]:
                        fresh.setdefault((r + dr, a + da, seen | region), history + (new,))
            states = fresh
            if not states:
                break
        for (r, a, flags), solution in states.items():
            if (r, a) != budget or bitpair and summarize(flags) != required_relation:
                continue
            return {site: {leaf for leaf, mask in zip(leaves, solution) if mask & (1 << i)}
                    for i, site in enumerate(sites)}
    return None


def verified_witness(branches, costs, relation):
    branches = list(branches.values())
    for budgets in product(*costs):
        if tuple(map(sum, zip(*budgets))) != (1, 9):
            continue
        original = {site: leaves for branch in branches for site, leaves in branch.items()}
        corrected = original.copy()
        for branch, budget in zip(branches, budgets):
            result = fit_branch(branch, budget, relation)
            if result is None:
                break
            corrected.update(result)
        else:
            removed = [[k, leaf] for k in sorted(original) for leaf in sorted(original[k] - corrected[k])]
            added = [[k, leaf] for k in sorted(original) for leaf in sorted(corrected[k] - original[k])]
            assert len(removed) == 1 and len(added) == 9
            assert all(a <= b or b <= a or a.isdisjoint(b) for a, b in combinations(corrected.values(), 2))
            m71, m101 = (corrected[k] for k in PAIR)
            assert m71 and m101 and FOCAL_LEAF not in m101
            fits = m71 < m101 if relation.startswith("M71_proper") else m71.isdisjoint(m101)
            assert fits
            return {"removed": removed, "added": added}
    raise AssertionError(f"No (1,9) witness found for {relation}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers", type=Path)
    branches = load(parser.parse_args().carriers)
    costs = [sorted(branch_frontiers(cols)[0]) for cols in branches.values()]
    results = {relation: verified_witness(branches, costs, relation) for relation in
               ["M71_proper_nonempty_subset_of_M101", "disjoint_nonempty"]}
    print(json.dumps(results, indent=2))
