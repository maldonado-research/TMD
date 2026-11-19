"""Sharp hidden-count ranges under caps on realized split-call cross products."""
import json
from fractions import Fraction
from math import ceil, floor
from pathlib import Path

HERE = Path(__file__).resolve().parent


def site_interval(table, lower, upper):
    """Bound h among reference/reference calls by lower*a*b <= both*h <= upper*a*b.

    upper=None removes the upper inequality, including on zero-product strata.
    """
    both, a, b, neither = table
    if lower < 0 or (upper is not None and upper < lower):
        raise ValueError("Nonnegative ordered cross-product multipliers are required.")
    if any(type(n) is not int or n < 0 for n in table):
        raise ValueError("Cell counts must be nonnegative integers.")
    singles_product = a * b
    if not both:
        return None if lower * singles_product > 0 else (0, neither)
    lo = ceil(Fraction(lower * singles_product, both))
    hi = neither if upper is None else min(neither, floor(Fraction(upper * singles_product, both)))
    return (lo, hi) if lo <= hi else None


def total_interval(tables, lower, upper):
    lo = hi = 0
    for table, sites in tables:
        endpoints = site_interval(table, lower, upper)
        if endpoints is None:
            return None
        lo += sites * endpoints[0]
        hi += sites * endpoints[1]
    return [lo, hi]


def counts_and_rates(pooled, interval):
    both, a, b, _ = pooled
    caught = both + a + b
    if not caught:
        raise ValueError("The detected union must be positive to define these fractions throughout.")
    lo, hi = interval
    def rates(numerators):
        ratios = [Fraction(n, caught + h) for n, h in zip(numerators, (lo, hi))]
        return [str(min(ratios)), str(max(ratios))]
    return {
        "true_site_tissue_count": [caught + lo, caught + hi],
        "missed_by_both_count": [lo, hi],
        "missed_by_a_fraction": rates((b + lo, b + hi)),
        "missed_by_b_fraction": rates((a + lo, a + hi)),
        "missed_by_exactly_one_fraction": rates((a + b, a + b)),
        "missed_by_both_fraction": rates((lo, hi)),
        "detected_by_either_fraction": rates((caught, caught)),
    }


def analyze(receipt):
    if receipt["columns"] != ["both", "a_only", "b_only", "neither", "multiplicity"]:
        raise ValueError("Unexpected column order.")
    tables = [(r[:4], r[4]) for r in receipt["site_tables"]]
    pooled = [sum(t[i] * n for t, n in tables) for i in range(4)]
    tissue_tables = [(r[:4], r[4]) for r in receipt["tissue_tables"]]
    tissue_totals = [sum(t[i] * n for t, n in tissue_tables) for i in range(4)]
    if tissue_totals != pooled:
        raise ValueError("Site and tissue rosters disagree on the pooled counts.")
    groupings = {"pooled": [(pooled, 1)], "within_sites": tables, "within_tissues": tissue_tables}
    def signed_ranges(low, high):
        return {name: total_interval(groups, low, high) for name, groups in groupings.items()}
    example = signed_ranges(0, 1)
    # For finite multipliers, zero single-side products force h=0 if both>0.
    finite_limits = {name: sum(n*t[3] for t,n in groups if t[0] == 0 or t[1]*t[2] > 0)
                     for name, groups in groupings.items()}
    witness = []
    for table, n in tables:
        _, hi = site_interval(table, 0, 1)
        if hi:
            witness.append({"table": table, "sites": n, "h_per_site": hi})
    return {
        "assumptions": ["All detections are true in their tissue.",
                        "Each site-tissue pair has one common binary truth for both splits.",
                        "Finite bounds constrain realized counts at the specified grouping."],
        "pooled_table_both_a_only_b_only_neither": pooled,
        "uncapped": counts_and_rates(pooled, [0, pooled[3]]),
        "hidden_counts_by_one_sided_cap": {str(g): signed_ranges(0, g) for g in [0, 1, 2, 5, 10]},
        "hidden_counts_by_two_sided_band": {
            str(g): signed_ranges(Fraction(1, g), g) for g in [1, 2, 10]},
        "cap_one": {name: counts_and_rates(pooled, interval) for name, interval in example.items()},
        "largest_hidden_count_for_arbitrarily_large_finite_upper_cap": finite_limits,
        "cap_one_maximum_sitewise_witness_nonzero_terms": witness,
    }


if __name__ == "__main__":
    receipt = json.loads((HERE / "site_calls.json").read_bytes())
    print(json.dumps(analyze(receipt), indent=2))
