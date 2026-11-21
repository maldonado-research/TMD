"""Compare pairs of reported changes in serial divisions of the same mother lineage."""
import csv
import json
from collections import defaultdict
from itertools import combinations
from math import comb
from pathlib import Path
from statistics import mean


def analyze():
    groups = defaultdict(dict)
    with Path(__file__).with_name("divisions.tsv").open() as f:
        for r in csv.DictReader(f, delimiter="\t"):
            key = int(r["physical_division"])
            assert key not in groups[r["pedigree"]]
            groups[r["pedigree"]][key] = int(r["assigned_changes"])
    breakdown = {}
    for group, counts in sorted(groups.items()):
        total = sum(counts.values())
        tied = sum(comb(n, 2) for n in counts.values())
        ordered = sum(a*b for a, b in combinations(counts.values(), 2))
        assert ordered + tied == comb(total, 2)
        breakdown[group] = {"scored_divisions": len(counts), "assigned_changes": total,
                            "same_division_pairs": tied, "distinct_division_ordered_pairs": ordered}
    aggregate = {k: sum(r[k] for r in breakdown.values()) for k in next(iter(breakdown.values()))}
    ordered, same = aggregate["distinct_division_ordered_pairs"], aggregate["same_division_pairs"]
    within = ordered + same
    total_pairs = comb(aggregate["assigned_changes"], 2)
    return {"all": aggregate, "within_pedigree_pairs": within, "within_pedigree_fraction_ordered": ordered/within,
            "equal_pedigree_mean_fraction_ordered": mean(r["distinct_division_ordered_pairs"]/comb(r["assigned_changes"], 2)
                                                        for r in breakdown.values()),
            "cross_pedigree_pairs_no_common_division_clock": total_pairs-within,
            "all_pairs": total_pairs, "per_pedigree": breakdown}


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
