"""Audit the 2015 archived counts against the 2019 de-duplicated technical counts.

Usage: python compare_levy_deposits.py MOESM90.csv MOESM93.csv SD1.csv SD2.csv
"""
import argparse
from array import array
from collections import Counter
import csv
from hashlib import file_digest
from itertools import zip_longest
import json
from pathlib import Path

from score_levy import STUDIES


SOURCE = ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41559-018-0758-1/"
          "MediaObjects/41559_2018_758_MOESM{}_ESM.csv")
TECHNICAL = {
    "E1": (3, "b65bc0687e88e73830bc74719af611a2a9bfaad3ed524f1246115167df6f4629"),
    "E2": (4, "5af368d7570c7e9db1debdd5a0615ef9bbde4d5b0bdf655867a32f068840a78b"),
}


def check_hash(path, expected):
    with path.open("rb") as stream:
        if file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError(f"Unexpected source bytes in {path}")


def audit(study, original, technical):
    suffix, digest = TECHNICAL[study]
    _, original_digest, visits = STUDIES[study]
    check_hash(original, original_digest)
    check_hash(technical, digest)
    original_ones_technical_zeros = 0
    early_positive_among_differences = 0
    final_positive_among_differences = 0
    mismatches = Counter()
    baseline, early, endpoint, extended = [array("Q") for _ in range(4)]
    with original.open(newline="") as a, technical.open(newline="") as b:
        arows, brows = csv.reader(a), csv.reader(b)
        if next(arows) != [f"t={v}" for v in visits]:
            raise ValueError("Unexpected original visit labels")
        technical_headers = next(brows)
        bvisits = [int(v.split(".")[0]) for v in technical_headers]
        groups = [[j for j, v in enumerate(bvisits) if v == t] for t in visits]
        terminal_group = [j for j, v in enumerate(bvisits) if v == max(bvisits)]
        if not all(groups):
            raise ValueError("Original visit missing from follow-on deposit")
        for row_a, row_b in zip_longest(arows, brows):
            if row_a is None or row_b is None:
                raise ValueError("Unequal row rosters")
            if len(row_a) != len(visits) or len(row_b) != len(bvisits):
                raise ValueError("Unexpected row width")
            old = [int(s) for s in row_a]
            raw = [int(s) for s in row_b]
            summed = [sum(raw[j] for j in indices) for indices in groups]
            for t, x, y in zip(visits, old, summed):
                if x != y:
                    mismatches[t] += 1
            if old[0] == 1 and summed[0] == 0:
                original_ones_technical_zeros += 1
                early_positive_among_differences += summed[1] > 0
                final_positive_among_differences += summed[-1] > 0
            baseline.append(summed[0])
            early.append(summed[1])
            endpoint.append(summed[-1])
            extended.append(sum(raw[j] for j in terminal_group))
    n = len(baseline)
    nb, ne = sum(baseline), sum(early)
    predictions = {}
    for rule in ("baseline", "early", "change"):
        best, ids, neligible = None, [], 0
        for i, (b, e) in enumerate(zip(baseline, early)):
            if not (b if rule == "baseline" else b + e):
                continue
            neligible += 1
            score = b if rule == "baseline" else e if rule == "early" else 2 * e * nb - b * ne
            if best is None or score > best:
                best, ids = score, [i]
            elif score == best:
                ids.append(i)
        predictions[rule] = {"eligible": neligible, "top_rows_1_based": [i + 1 for i in ids]}
    def endpoint_info(counts):
        maximum = max(counts)
        ids = [i for i, value in enumerate(counts) if value == maximum]
        return {"total_reads": sum(counts), "top_count": maximum,
                "top_rows_1_based": [i + 1 for i in ids],
                "rule_counts_if_unique": {k: counts[v["top_rows_1_based"][0] - 1]
                    for k, v in predictions.items() if len(v["top_rows_1_based"]) == 1}}
    return {
        "study": study, "technical_url": SOURCE.format(suffix), "technical_sha256": digest,
        "technical_column_labels": technical_headers, "rows": n, "overlap_cells": n * len(visits),
        "mismatch_counts_by_original_generation": dict(sorted(mismatches.items())),
        "original_one_technical_zero_at_baseline": original_ones_technical_zeros,
        "early_positive_among_those_rows": early_positive_among_differences,
        "original_endpoint_positive_among_those_rows": final_positive_among_differences,
        "technical_baseline_total": nb, "technical_early_total": ne,
        "native_rule_predictions": predictions,
        "original_endpoint_generation": visits[-1], "original_endpoint": endpoint_info(endpoint),
        "extended_endpoint_generation": max(bvisits), "extended_endpoint": endpoint_info(extended),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("E1", "E2", "SD1", "SD2"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps([audit("E1", args.E1, args.SD1), audit("E2", args.E2, args.SD2)], indent=2))
