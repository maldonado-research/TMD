"""Score the prespecified split-allocation direction on one complete tissue–site frame."""
import argparse
import csv
import json
import re
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from read_allocation import one_sided_probability

IDS = ("plant_id", "tissue_id", "site_id")
COUNTS = ("a_ref", "a_alt", "b_ref", "b_alt")


def exact_text(value):
    """Write an exact fraction even when its denominator exceeds the integer string limit."""
    numerator = str(Decimal(value.numerator))
    if value.denominator == 1:
        return numerator
    return numerator + "/" + str(Decimal(value.denominator))


def read_count(field, line):
    value = field.strip()
    if not value:
        return None
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError(f"Line {line}: expected a nonnegative integer or an empty count.")
    return int(value)


def inventory(keys):
    return {
        "tissue_site_pairs": len(keys),
        "distinct_plants": len({plant for plant, _, _ in keys}),
        "distinct_tissues": len({(plant, tissue) for plant, tissue, _ in keys}),
    }


def score(stream):
    reader = csv.reader(stream, delimiter="\t", strict=True)
    header = next(reader, [])
    required = IDS + COUNTS
    if len(header) != len(required) or set(header) != set(required):
        raise ValueError("Expected each TSV field exactly once: " + ", ".join(required))

    all_keys = set()
    scored_keys = set()
    exclusions = dict.fromkeys(("missing_counts", "zero_depth", "zero_alternates", "one_alternate"), 0)
    incomplete = Counter()
    observed = forced = 0
    expected = Fraction()
    for row in reader:
        if len(row) != len(header):
            raise ValueError(f"Line {reader.line_num}: row has the wrong number of fields.")
        fields = dict(zip(header, row))
        key = tuple(fields[name].strip() for name in IDS)
        if any(not identifier for identifier in key):
            raise ValueError(f"Line {reader.line_num}: missing identifier.")
        if key in all_keys:
            raise ValueError(f"Line {reader.line_num}: duplicate plant, tissue and site.")
        all_keys.add(key)
        ar, aa, br, ba = [read_count(fields[name], reader.line_num) for name in COUNTS]
        missing_a = ar is None or aa is None
        missing_b = br is None or ba is None
        if missing_a or missing_b:
            exclusions["missing_counts"] += 1
            incomplete[(missing_a, missing_b)] += 1
            continue
        depth_a, depth_b = ar + aa, br + ba
        if min(depth_a, depth_b) == 0:
            exclusions["zero_depth"] += 1
            continue
        k = aa + ba
        if k < 2:
            exclusions["zero_alternates" if k == 0 else "one_alternate"] += 1
            continue
        scored_keys.add(key)
        probability = one_sided_probability(depth_a, depth_b, k)
        observed += int(aa == 0 or ba == 0)
        expected += probability
        forced += int(probability in (0, 1))

    eligible = len(scored_keys)
    difference = observed - expected
    if eligible == forced:
        outcome = "uninformative"
    elif difference > 0:
        outcome = "positive_direction"
    else:
        outcome = "direction_failed"
    return {
        "frame": inventory(all_keys),
        "exclusive_exclusions": exclusions,
        "missing_counts_by_incomplete_half": {
            "a_only": incomplete[True, False], "b_only": incomplete[False, True],
            "both": incomplete[True, True]},
        "eligible": inventory(scored_keys),
        "forced_comparisons": forced,
        "informative_comparisons": eligible - forced,
        "observed_one_sided": observed,
        "expected_one_sided": exact_text(expected),
        "observed_minus_expected": exact_text(difference),
        "difference_per_eligible_comparison": exact_text(difference / eligible) if eligible else None,
        "directional_outcome": outcome,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frame", type=Path, help="complete-frame TSV with one row per declared tissue–site pair")
    args = parser.parse_args()
    try:
        with args.frame.open(encoding="utf-8-sig", newline="") as stream:
            result = score(stream)
    except (ValueError, csv.Error, OSError) as error:
        parser.exit(2, f"Cannot score the declared frame: {error}\n")
    print(json.dumps(result, indent=2))
