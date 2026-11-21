"""Verify the joint distribution by direct enumeration of each pair of allocation masks."""

import json
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent


def allocations(family):
    pups = family["pups_in_bit_order"]
    patterns = [(int(bits, 2), n) for bits, n in family["recorded_carrier_pattern_counts"].items()]
    all_pups = (1 << len(pups)) - 1
    def covariates(mask):
        group = [p for i, p in enumerate(reversed(pups)) if mask & (1 << i)]
        return (sum(p["sex"] == "F" for p in group), sum(p["wgs_depth"] for p in group))
    observed = int("".join("1" if p["litter"] == min(q["litter"] for q in pups) else "0" for p in pups), 2)
    target = covariates(observed)
    options = []
    for mask in range(1, all_pups):
        if bin(mask).count("1") != len(pups) // 2:
            continue
        # Every roster event appears in at least one panel. Subtract those confined to either panel.
        one_side = sum(n for bits, n in patterns if not bits & mask or not bits & (all_pups ^ mask))
        bridges = sum(n for _, n in patterns) - one_side
        cov = covariates(mask)
        options.append((bridges, cov[0] == target[0], cov == target, mask == observed))
    return options


def verify():
    families = json.loads((HERE / "profiles.json").read_text())["families"]
    result = json.loads((HERE / "split_results.json").read_text())
    panels = [allocations(f) for f in families.values()]
    observed = sum(next(t for t, _, _, original in options if original) for options in panels)
    laws = {m: Counter() for m in result["combined_tests"]}
    for pair in product(*panels):
        t = sum(row[0] for row in pair)
        laws["balanced"][t] += 1
        if all(row[1] for row in pair):
            laws["fixed_early_sex"][t] += 1
        if all(row[2] for row in pair):
            laws["fixed_early_sex_and_depth_sum"][t] += 1
    for m, law in laws.items():
        output = result["combined_tests"][m]
        assert dict(law) == {int(k): v for k, v in output["distribution"].items()}
        n = sum(law.values())
        mean = Fraction(sum(i * f for i, f in law.items()), n)
        assert output["observed_bridging_events"] == observed
        assert Fraction(output["expectation"]["fraction"]) == mean
        assert output["tail_counts"] == {
            "lower": sum(f for i, f in law.items() if i <= observed),
            "upper": sum(f for i, f in law.items() if i >= observed),
            "two_sided_about_expectation": sum(f for i, f in law.items() if abs(i-mean) >= abs(observed-mean)),
        }
    print("All three joint histograms, observed count, expectations and tails verified.")


if __name__ == "__main__":
    verify()
