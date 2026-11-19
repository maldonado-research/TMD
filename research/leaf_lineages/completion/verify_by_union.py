"""Check all minimum-addition counts by branching directly on pairs that cross."""
import csv
import heapq
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(path):
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    names = [f"{row['chromosome']}:{row['position']}" for row in rows]
    sets = [row["listed_leaves"].split(";") for row in rows]
    leaf_names = sorted(set(itertools.chain.from_iterable(sets)))
    bits = {name: 1 << i for i, name in enumerate(leaf_names)}
    masks = tuple(sum(bits[x] for x in group) for group in sets)
    return names, leaf_names, masks


def first_crossing(sets):
    for j, right in enumerate(sets):
        for i in range(j):
            left = sets[i]
            if left & right and left & ~right and right & ~left:
                return i, j
    return None


def minimize(original, required):
    # Each scenario specifies no relation, one inclusion, or equality of two sets.
    def close(state):
        state = list(state)
        for inner, outer in required:
            state[outer] |= state[inner]
        return tuple(state)

    def cost(state):
        return sum((new & ~old).bit_count() for new, old in zip(state, original))

    initial = close(original)
    queue = [(cost(initial), initial)]
    seen = {initial}
    solutions = []
    minimum = None
    while queue:
        expense, state = heapq.heappop(queue)
        if minimum is not None and expense > minimum:
            break
        conflict = first_crossing(state)
        if conflict is None:
            solutions.append(state)
            minimum = expense
            continue
        i, j = conflict
        union = state[i] | state[j]
        for index in (i, j):
            child = close((*state[:index], union, *state[index + 1:]))
            if child not in seen:
                seen.add(child)
                heapq.heappush(queue, (cost(child), child))
    return minimum, solutions


def additions(reference, version, sites, leaves):
    return {(sites[i], leaf) for i, (old, new) in enumerate(zip(reference, version))
            for j, leaf in enumerate(leaves) if (new & ~old) >> j & 1}


def as_pairs(mapping):
    return {(site, leaf) for site, leaves in mapping.items() for leaf in leaves}


def diagram_sets():
    path = HERE.parent / "topology" / "figure4_leaf_icons.tsv"
    sets = [0] * 48
    leaves = 0
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for entry in row["marker_lists_on_drawn_leaf_icons"].split(";"):
                for number in map(int, entry.split(",")):
                    sets[number - 1] |= 1 << leaves
                leaves += 1
    assert leaves == 75 and sum(s.bit_count() for s in sets) == 148
    return tuple(sets)


def main():
    sites, leaves, original = load(HERE.parent / "carrier" / "carriers.tsv")
    reference = json.loads((HERE / "orientation_result.json").read_bytes())
    m71, m101 = sites.index("Pp01:2130859"), sites.index("Pp04:21561355")
    scenarios = {
        "unrestricted": [],
        "M101_within_M71": [(m101, m71)],
        "M101_equals_M71": [(m71, m101), (m101, m71)],
    }
    for label, required in scenarios.items():
        expected = reference[label]
        cost, solutions = minimize(original, required)
        assert cost == expected["minimum_added_memberships"]
        assert len(solutions) == expected["distinct_optimal_tables"]
        observed = {frozenset(additions(original, s, sites, leaves)) for s in solutions}
        common = as_pairs(expected["additions_common_to_all_optima"])
        wanted = {frozenset(common | as_pairs(x)) for x in expected["other_additions_by_optimum"]}
        assert wanted == observed
        # The figure numbers M71 and M101 as 4 and 2. Sheet leaf names
        # and left/right assignments within a pictured location are unnecessary.
        figure_indices = {m71: 3, m101: 1}
        diagram_rules = [(figure_indices[i], figure_indices[j]) for i, j in required]
        figure_cost, figure_solutions = minimize(diagram_sets(), diagram_rules)
        assert (figure_cost, len(figure_solutions)) == (cost, len(solutions))
        print(f"{label}: {cost} additions, {len(solutions)} independently reproduced minimum tables")


if __name__ == "__main__":
    main()
