"""Measure how many missed bulk memberships suffice for two markers to share a cellular path."""
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path

from row_split_witness import read_table, lineage_patterns

HERE = Path(__file__).resolve().parent
CARRIERS = HERE.parents[1] / "leaf_lineages/carrier/carriers.tsv"
TARGET = "DHQ1_B1-1-L1"
SHARED = "DHQ1_B1-1-L2"
PAIR = {71, 101}


def check_witness(assignments, supports, keep_separate):
    columns = defaultdict(set)
    histogram = Counter()
    for leaf, patterns in assignments.items():
        observed = {m for m, carriers in supports.items() if leaf in carriers}
        assert set.union(*patterns) == observed
        incompatible = {frozenset((a,b)) for a,b in combinations(observed,2)
                        if supports[a] - supports[b] and supports[b] - supports[a]}
        if keep_separate:
            incompatible.add(frozenset(PAIR))
        maximum = max((len(group) for n in range(1,len(observed)+1)
                       for group in combinations(observed,n)
                       if all(frozenset(edge) in incompatible for edge in combinations(group,2))),
                      default=1)
        assert len(patterns) == maximum, leaf
        for i, pattern in enumerate(patterns):
            if keep_separate:
                assert not PAIR <= pattern
            for marker in pattern:
                columns[marker].add((leaf,i))
        histogram[len(patterns)] += 1
    for x,y in combinations(columns.values(),2):
        assert not (x & y and x-y and y-x)
    return {"minimum_total":sum(size*n for size,n in histogram.items()),
            "leaves_by_minimum_signatures":dict(sorted(histogram.items())),
            "focal_leaf_signatures":list(map(sorted,assignments[TARGET])),
            "originally_double_listed_leaf_signatures":list(map(sorted,assignments[SHARED]))}


def main():
    rows = sorted(read_table(CARRIERS), key=lambda r:(r["chromosome"],int(r["position"])))
    supports = {i:frozenset(r["listed_leaves"].split(";")) for i,r in enumerate(rows,71)}
    leaves = sorted(set().union(*supports.values()))
    thresholds = []
    for (a,x),(b,y) in combinations(supports.items(),2):
        if x & y and x-y and y-x:
            thresholds.append({"pair":[a,b], "additions_for_a_ancestral_to_b":len(y-x),
                               "additions_for_b_ancestral_to_a":len(x-y),
                               "minimum_for_shared_path":min(len(y-x),len(x-y))})
    assert supports[71]-supports[101] == {TARGET}
    original = {leaf:lineage_patterns(leaf,{m for m,s in supports.items() if leaf in s},supports)
                for leaf in leaves}
    changed = dict(supports)
    changed[101] = supports[101] | {TARGET}
    colocated = {leaf:lineage_patterns(leaf,{m for m,s in changed.items() if leaf in s},changed)
                 for leaf in leaves}
    assert any(PAIR <= p for p in colocated[SHARED])
    separate = dict(original)
    separate[TARGET] = original[TARGET] + [{101}]
    print(json.dumps({"original_crossing_pair_thresholds":thresholds,
                      "cost_histogram_for_possible_colocation":
                          dict(sorted(Counter(r["minimum_for_shared_path"] for r in thresholds).items())),
                      "with_one_addition_M101_at_focal_leaf":{
                          "unconstrained_with_attained_colocation":check_witness(colocated,changed,False),
                          "forced_separate":check_witness(separate,changed,True)}},indent=2))


if __name__ == "__main__":
    main()
