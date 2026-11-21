"""Independently count subset minima event by event and convolve the seven score laws."""

import argparse
import csv
import json
from collections import Counter
from fractions import Fraction
from math import lcm, prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")


def subset_minima(event_values, k):
    levels = [Counter() for _ in range(k + 1)]
    levels[0][None] = 1
    for value in event_values:
        for chosen in range(k, 0, -1):
            for before, ways in levels[chosen - 1].items():
                new = value if before is None else min(before, value)
                levels[chosen][new] += ways
    return levels[k]


def verify(events, result):
    distributions = []
    observed = []
    for path in sorted({r["path"] for r in events} - {"G2"}):
        path_rows = [r for r in events if r["path"] == path]
        family, = {r["pedigree"] for r in path_rows}
        train = Counter(r["substitution_class"] for r in events
                        if r["pedigree"] != family and r["substitution_class"] in CLASSES)
        p = {c: Fraction(train[c] + 1, sum(train.values()) + len(CLASSES)) for c in CLASSES}
        def gain(y):
            q_loss = sum((Fraction(1, 6) - int(c == y)) ** 2 for c in CLASSES)
            p_loss = sum((p[c] - int(c == y)) ** 2 for c in CLASSES)
            return q_loss - p_loss
        weights = {c: gain(c) for c in CLASSES}
        first = min(int(r["time_upper"]) for r in path_rows)
        early = [weights[r["substitution_class"]] for r in path_rows if int(r["time_lower"]) <= first]
        all_values = [weights[r["substitution_class"]] for r in path_rows if r["substitution_class"] in CLASSES]
        distributions.append(subset_minima(all_values, len(early)))
        observed.append(min(early))
    n = len(observed)
    assert Fraction(result["observed_mean_lower_brier_gain"]["fraction"]) == sum(observed) / n
    expected = sum(sum(v * m for v, m in law.items()) / sum(law.values()) for law in distributions) / n
    assert expected == Fraction(result["expected_mean_lower_brier_gain_under_null"]["fraction"])
    scale = lcm(*(v.denominator for law in distributions for v in law))
    total_law = Counter({0: 1})
    for law in distributions:
        convolved = Counter()
        for value, multiplicity in law.items():
            change = int(value * scale)
            for total, count in total_law.items():
                convolved[total + change] += multiplicity * count
        total_law = convolved
    threshold = int(sum(observed) * scale)
    tail = sum(m for v, m in total_law.items() if v >= threshold)
    size = sum(total_law.values())
    assert size == prod(sum(law.values()) for law in distributions)
    assert int(result["subset_combinations_at_least_as_large"]) == tail
    assert int(result["subset_combinations"]) == size
    assert Fraction(result["one_sided_inclusive_p"]["fraction"]) == Fraction(tail, size)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path, nargs="?", default=HERE.parent / "kennedy" / "kennedy_events.tsv")
    parser.add_argument("result", type=Path, nargs="?", default=HERE / "random_window_results.json")
    args = parser.parse_args()
    with args.events.open() as source:
        events = list(csv.DictReader(source, delimiter="\t"))
    report = json.loads(args.result.read_text())
    verify(events, report["unlinked_later_F_event_excluded"])
    for cls, result in report["unlinked_F_event_assigned_one_of_six_classes"].items():
        completed = [dict(r, substitution_class=cls) if r["substitution_class"] == "unknown" else r
                     for r in events]
        verify(completed, result)
    print("Verified observed score, expected score and exact tail counts under all seven specifications.")


if __name__ == "__main__":
    main()
