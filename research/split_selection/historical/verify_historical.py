"""Independently check the 40 archived comparisons using a sampling-without-replacement product."""
import json
from fractions import Fraction
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent


def all_in_one_side(depth, population, k):
    if k > depth:
        return Fraction()
    return prod((Fraction(depth - i, population - i) for i in range(k)), start=Fraction(1))


def run():
    profiles = json.loads((HERE / "historical_profiles.json").read_bytes())["rows"]
    results = json.loads((HERE / "historical_result.json").read_bytes())
    full = Fraction()
    observed = []
    for marker, rows in profiles.items():
        if {row[0] for row in rows} != {f"Pair{i}" for i in range(1, 21)}:
            raise ValueError("Historical site does not match the 20-tissue frame")
        expected = Fraction()
        for pair, ar, aa, br, ba in rows:
            a, b, k = ar + aa, br + ba, aa + ba
            if min(a, b) < 1 or k < 2:
                raise ValueError("Unexpected ineligible historical comparison")
            expected += all_in_one_side(a, a + b, k) + all_in_one_side(b, a + b, k)
            if aa == 0 or ba == 0:
                observed.append((marker, pair, aa, ba))
        if round(float(expected), 12) != results["by_marker"][marker]["expected_one_sided"]:
            raise ValueError("Marker total differs")
        full += expected
    if sorted(observed) != [("M101", "Pair1", 5, 0), ("M101", "Pair19", 0, 43)]:
        raise ValueError("One-sided counts differ")
    if round(float(full), 12) != results["both_markers"]["expected_one_sided"]:
        raise ValueError("Combined expectation differs")
    print("Both site margins, 40 eligible rows, two one-sided cases and exact-product sums agree.")


if __name__ == "__main__":
    run()
