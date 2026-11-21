"""Exact conditional random-window comparison for the seven Kennedy founder paths."""

import argparse
import csv
import json
from collections import Counter
from fractions import Fraction
from itertools import product
from math import comb, lcm, prod
from pathlib import Path


CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")
PATHS = ("B", "C", "D", "E", "F", "G1", "H")
SOURCE = Path(__file__).resolve().parent.parent / "kennedy" / "kennedy_events.tsv"


def ratio(x):
    return {"fraction": str(x), "decimal": float(x)}


def min_distribution(pool, k, probability):
    counts = Counter(probability[c] for c in pool)
    if not 1 <= k <= len(pool):
        raise ValueError("Invalid window size for typed pool")
    remaining = len(pool)
    ways = {}
    for value, size in sorted(counts.items()):
        ways[value] = comb(remaining, k) - comb(remaining - size, k)
        remaining -= size
    return {value: count for value, count in ways.items() if count}


def build_folds(events):
    folds = []
    for path in PATHS:
        catalog = [r for r in events if r["path"] == path]
        family, = {r["pedigree"] for r in catalog}
        upper = min(int(r["time_upper"]) for r in catalog)
        first = [r for r in catalog if int(r["time_lower"]) <= upper]
        if any(int(r["time_lower"]) != int(r["time_upper"]) or r["substitution_class"] not in CLASSES
               for r in first):
            raise ValueError("This null requires known earliest-window event membership and classes")
        pool = [r["substitution_class"] for r in catalog if r["substitution_class"] in CLASSES]
        training = Counter(r["substitution_class"] for r in events
                           if r["pedigree"] != family and r["substitution_class"] in CLASSES)
        p = {c: Fraction(training[c] + 1, training.total() + 6) for c in CLASSES}
        k = len(first)
        observed_min = min(p[r["substitution_class"]] for r in first)
        weights = min_distribution(pool, k, p)
        total = comb(len(pool), k)
        if sum(weights.values()) != total or observed_min not in weights:
            raise ValueError("Weights or observed subset disagree with the eligible pool")
        offset = -sum(x * x for x in p.values()) - Fraction(1, 6)
        expected_min = sum(x * w for x, w in weights.items()) / total
        folds.append(dict(path=path, n=len(pool), k=k, ways=weights, total=total,
                          observed_min=observed_min, observed_gain=offset + 2 * observed_min,
                          expected_gain=offset + 2 * expected_min))
    return folds


def tail_count(folds):
    # Fold-specific Brier offsets cancel in the inclusive comparison.
    scale = lcm(*(x.denominator for f in folds for x in f["ways"]))
    target = int(sum(f["observed_min"] for f in folds) * scale)
    choices = [[(int(x * scale), w) for x, w in f["ways"].items()] for f in folds]
    return sum(prod(w for _, w in assignment) for assignment in product(*choices)
               if sum(value for value, _ in assignment) >= target)


def summarize(folds, include_folds):
    denom = prod(f["total"] for f in folds)
    numer = tail_count(folds)
    n = len(folds)
    result = {
        "observed_mean_lower_brier_gain": ratio(sum(f["observed_gain"] for f in folds) / n),
        "expected_mean_lower_brier_gain_under_null": ratio(sum(f["expected_gain"] for f in folds) / n),
        "subset_combinations": str(denom),
        "subset_combinations_at_least_as_large": str(numer),
        "one_sided_inclusive_p": ratio(Fraction(numer, denom)),
    }
    if include_folds:
        result["folds"] = [
            dict(path=f["path"], typed_pool=f["n"], window_size=f["k"], eligible_subsets=f["total"],
                 min_probability_counts={str(x): w for x, w in f["ways"].items()},
                 observed_min_probability=str(f["observed_min"]),
                 observed_lower_brier_gain=ratio(f["observed_gain"]),
                 expected_lower_brier_gain=ratio(f["expected_gain"])) for f in folds
        ]
    return result


def run(path):
    with path.open() as source:
        events = list(csv.DictReader(source, delimiter="\t"))
    by_id = {r["event_id"]: r for r in events}
    unknown = [r for r in events if r["substitution_class"] not in CLASSES]
    if len(by_id) != 237 or len(by_id) != len(events) or len(unknown) != 1:
        raise ValueError("Source event roster differs from the audited Kennedy cohort")
    if (unknown[0]["event_id"], unknown[0]["path"], unknown[0]["substitution_class"]) != ("V133", "F", "unknown"):
        raise ValueError("Unlinked event differs from the audited F row")
    observed = summarize(build_folds(events), True)
    sensitivity = {}
    for cls in CLASSES:
        completed = [dict(r, substitution_class=cls) if r["event_id"] == "V133" else r for r in events]
        sensitivity[cls] = summarize(build_folds(completed), False)
    return {"unlinked_later_F_event_excluded": observed,
            "unlinked_F_event_assigned_one_of_six_classes": sensitivity}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path, nargs="?", default=SOURCE)
    print(json.dumps(run(parser.parse_args().events), indent=2, allow_nan=False))
