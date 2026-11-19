"""Finite-archive paired morphology classification summaries from the Howells aggregate receipt."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

FAMILIES = ("W", "A", "M")
CATEGORIES = FAMILIES + ("unmatched",)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def paired_table(section):
    """Identify the full cross-table only if all pairs with two matched records agree."""
    n = section["parents"]
    margins = section["clones_by_phenotype_and_recorded_family"]
    wrinkly, smooth = margins["wrinkly"], margins["smooth"]
    same = section["paired_clones_with_same_recorded_family"]
    any_family = section["pairs_with_any_recorded_family"]
    for counts in (wrinkly, smooth, same, any_family):
        check(all(type(v) is int and v >= 0 for v in counts.values()), "Invalid aggregate count.")
    check(set(wrinkly) == set(smooth) == set(CATEGORIES) and set(same) == set(FAMILIES),
          "Unexpected categories.")
    check(sum(wrinkly.values()) == sum(smooth.values()) == sum(any_family.values()) == n,
          "One category per clone and one pair per parent are required.")
    check(sum(same.values()) == any_family["both"],
          "Both-matched pairs include different categories. This reconstruction is unavailable.")

    table = [[0] * len(CATEGORIES) for _ in CATEGORIES]
    for i, family in enumerate(FAMILIES):
        table[i][i] = same[family]
        table[i][-1] = wrinkly[family] - same[family]
        table[-1][i] = smooth[family] - same[family]
    table[-1][-1] = any_family["neither"]
    check(all(count >= 0 for row in table for count in row), "Inconsistent family marginals.")
    check([sum(row) for row in table] == [wrinkly[c] for c in CATEGORIES]
          and [sum(col) for col in zip(*table)] == [smooth[c] for c in CATEGORIES],
          "Paired table disagrees with the category marginals.")
    check(sum(row[-1] for row in table[:-1]) == any_family["wrinkly_only"]
          and sum(table[-1][:-1]) == any_family["smooth_only"], "Any-family margins differ.")
    return table


def describe(table):
    n = sum(map(sum, table))
    paired = {}
    for i, family in enumerate(CATEGORIES):
        both = table[i][i]
        wrinkly_only = sum(table[i]) - both
        smooth_only = sum(row[i] for row in table) - both
        paired[family] = [both, wrinkly_only, smooth_only, n - both - wrinkly_only - smooth_only]
    return {"parent_pairs": n, "cross_category_counts": table, "paired_binary_counts": paired,
            "same_category_pairs": sum(table[i][i] for i in range(len(table)))}


def apparent_ceiling(table):
    wrinkly = list(map(sum, table))
    smooth = list(map(sum, zip(*table)))
    return sum(max(a, b) for a, b in zip(wrinkly, smooth))


def leave_pair_out(table):
    """Fit a category majority after holding out both records. Ambiguous predictions earn half."""
    wrinkly_counts = list(map(sum, table))
    smooth_counts = list(map(sum, zip(*table)))
    correct = Fraction(0)
    for wrinkly, row in enumerate(table):
        for smooth, frequency in enumerate(row):
            if frequency:
                for label, is_wrinkly in ((wrinkly, True), (smooth, False)):
                    difference = (wrinkly_counts[label] - (label == wrinkly)
                                  - smooth_counts[label] + (label == smooth))
                    if difference == 0:
                        correct += Fraction(frequency, 2)
                    elif (difference > 0) == is_wrinkly:
                        correct += frequency
    return correct


def performance(correct, total):
    return {"correct": correct, "records": total, "accuracy": str(Fraction(correct, total)),
            "shortfall_from_perfect_records": total - correct,
            "shortfall_from_perfect_fraction": str(Fraction(total - correct, total))}


def analyze(receipt):
    tables = {arm: paired_table(section) for arm, section in receipt["arms"].items()}
    all_parents = paired_table(receipt["paired_roster_totals"])
    aggregate = [[sum(t[i][j] for t in tables.values()) for j in range(len(CATEGORIES))]
                 for i in range(len(CATEGORIES))]
    check(aggregate == all_parents, "The pooled receipt differs from the sum of its contexts.")
    records = 2 * sum(map(sum, all_parents))
    context_ceilings = {key: apparent_ceiling(table) for key, table in tables.items()}
    context_holdouts = {key: leave_pair_out(table) for key, table in tables.items()}
    by_context = dict()
    for arm, table in tables.items():
        by_context[arm] = describe(table)
        size = 2 * by_context[arm]["parent_pairs"]
        by_context[arm]["apparent_ceiling"] = performance(context_ceilings[arm], size)
        by_context[arm]["leave_one_pair_out_expected_correct"] = str(context_holdouts[arm])
    return {
        "category_order": CATEGORIES,
        "cross_category_axes": ["wrinkly record", "smooth record"],
        "binary_cell_order": ["both", "wrinkly_only", "smooth_only", "neither"],
        "pooled": describe(all_parents),
        "by_recorded_context": by_context,
        "apparent_ceiling": {
            "category_only": performance(apparent_ceiling(all_parents), records),
            "category_and_context": performance(sum(context_ceilings.values()), records),
        },
        "leave_one_parent_out_retrospective_majority": {
            "ties_or_unseen": "Half credit per held-out record.",
            "category_only": performance(leave_pair_out(all_parents), records),
            "category_and_context": performance(sum(context_holdouts.values()), records),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    result = analyze(json.loads(raw))
    result["aggregate_receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, default=str, indent=2))
