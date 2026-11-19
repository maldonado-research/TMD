"""Check read-allocation arithmetic by enumerating slots and by sequential drawing."""
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path

from read_allocation import one_sided_probability

HERE = Path(__file__).resolve().parent


def all_marked_in_one_half(a, b, k):
    def draw(half):
        p = Fraction(1)
        for removed in range(k):
            if removed == half:
                return Fraction(0)
            p *= Fraction(half - removed, a + b - removed)
        return p
    return draw(a) + draw(b)


def run():
    tests = 0
    for a, b in product(range(1, 6), repeat=2):
        for k in range(1, a + b + 1):
            allocations = list(combinations(range(a + b), k))
            one_side = sum(group[-1] < a or group[0] >= a for group in allocations)
            check = Fraction(one_side, len(allocations))
            if not (check == one_sided_probability(a, b, k) == all_marked_in_one_half(a, b, k)):
                raise ValueError("Small exact check differs")
            tests += 1
    data = json.loads((HERE / "allocation_profiles.json").read_bytes())
    result = json.loads((HERE / "read_allocation_result.json").read_bytes())
    expanded = [(a,b,k,side) for a,b,k,side,n in data["positive_profiles"] for _ in range(n)]
    if len(expanded) != 71 or sum(r[-1] for r in expanded) != 21:
        raise ValueError("Positive roster is inconsistent")
    def compare(rows, saved):
        expected = sum(all_marked_in_one_half(*r[:3]) for r in rows)
        if (len(rows), sum(r[3] for r in rows), round(float(expected), 8)) != (
                saved["positive_comparisons"], saved["observed_one_sided"], saved["expected_one_sided"]):
            raise ValueError("Aggregate check differs")
    compare(expanded, result["all_positive"])
    compare([r for r in expanded if r[2] > 1], result["two_or_more_alternate_reads"])
    intervals = {"1": (1, 1), "2": (2, 2), "3": (3, 3), "4-5": (4, 5),
                 "6-10": (6, 10), "11 or more": (11, max(r[2] for r in expanded))}
    for label, (lo, hi) in intervals.items():
        compare([r for r in expanded if lo <= r[2] <= hi], result["by_pooled_alternate_reads"][label])
    return {"exhaustive_small_allocations_checked": tests,
            "positive_tissue_site_comparisons_checked": len(expanded), "summary_rows_checked": 8}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
