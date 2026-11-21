"""Exact balanced litter allocations preserving each WGS pup's whole carrier profile."""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, prod
from pathlib import Path


MODES = ("balanced", "fixed_early_sex", "fixed_early_sex_and_depth_sum")


def as_number(x):
    return {"fraction": str(x), "decimal": float(x)}


def describe(law, observed):
    total = sum(law.values())
    expected = Fraction(sum(t * n for t, n in law.items()), total)
    delta = abs(observed - expected)
    counts = {
        "lower": sum(n for t, n in law.items() if t <= observed),
        "upper": sum(n for t, n in law.items() if t >= observed),
        "two_sided_about_expectation": sum(n for t, n in law.items() if abs(t - expected) >= delta),
    }
    return dict(observed_bridging_events=observed, allocations=total, expectation=as_number(expected),
                tail_counts=counts, p_values={k: as_number(Fraction(v, total)) for k, v in counts.items()},
                distribution={str(k): law[k] for k in sorted(law)})


def roster(pup_rows, pattern_counts):
    litters = sorted({p["litter"] for p in pup_rows})
    if len(litters) != 2 or len(pup_rows) != 10:
        raise ValueError("Expected two litters and ten named sequenced pups")
    early = frozenset(i for i, p in enumerate(pup_rows) if p["litter"] == litters[0])
    if len(early) != 5:
        raise ValueError("Expected five pups in each sequencing litter")
    events = []
    for bits, count in pattern_counts.items():
        if len(bits) != 10 or set(bits) - {"0", "1"} or "1" not in bits or count <= 0:
            raise ValueError("Invalid documented carrier pattern")
        events.append((frozenset(i for i, b in enumerate(bits) if b == "1"), count))
    return early, events


def split_counts(events, early):
    counts = Counter()
    for carriers, multiplicity in events:
        early_positive = bool(early & carriers)
        late_positive = bool(carriers - early)
        counts["early_positive"] += multiplicity * early_positive
        counts["late_positive"] += multiplicity * late_positive
        counts["both"] += multiplicity * (early_positive and late_positive)
        counts["total"] += multiplicity
    counts["early_only"] = counts["early_positive"] - counts["both"]
    counts["late_only"] = counts["late_positive"] - counts["both"]
    return counts


def analytic_mean(pups, events, early, with_sex):
    # Given K marked pups per stratum, compute the probability all are on one side.
    strata = [set(range(len(pups)))]
    if with_sex:
        strata = [{i for i, p in enumerate(pups) if p["sex"] == sx} for sx in ("M", "F")]
    expected = Fraction(0)
    for carriers, multiplicity in events:
        same_side = Fraction(0)
        for chosen in (early, set(range(len(pups))) - early):
            same_side += prod(Fraction(comb(len(chosen & s), len(carriers & s)),
                                       comb(len(s), len(carriers & s))) for s in strata)
        expected += multiplicity * (1 - same_side)
    return expected


def family_stats(data):
    pups = data["pups_in_bit_order"]
    early, events = roster(pups, data["recorded_carrier_pattern_counts"])
    observed = split_counts(events, early)
    all_ids = set(range(len(pups)))
    def covariates(subset):
        return (sum(pups[i]["sex"] == "F" for i in subset), sum(pups[i]["wgs_depth"] for i in subset))
    target = covariates(early)
    distributions = {m: Counter() for m in MODES}
    for allocation in combinations(sorted(all_ids), len(early)):
        assigned = frozenset(allocation)
        sx, depth = covariates(assigned)
        t = split_counts(events, assigned)["both"]
        distributions["balanced"][t] += 1
        if sx == target[0]:
            distributions["fixed_early_sex"][t] += 1
            if depth == target[1]:
                distributions["fixed_early_sex_and_depth_sum"][t] += 1
    for mode in MODES[:2]:
        law = distributions[mode]
        expected = Fraction(sum(k * n for k, n in law.items()), sum(law.values()))
        if expected != analytic_mean(pups, events, early, mode == MODES[1]):
            raise ValueError("Direct enumeration and per-event null expectation disagree")
    phases = {}
    for period, subset in (("early", early), ("late", all_ids - early)):
        females, depth = covariates(subset)
        phases[period] = dict(litter=pups[min(subset)]["litter"], pups=len(subset), female_pups=females,
                              mean_wgs_depth=as_number(Fraction(depth, len(subset))))
    by_k = {}
    for k in sorted({len(x) for x, count in events}):
        by_k[str(k)] = dict(split_counts([(x, count) for x, count in events if len(x) == k], early))
    report = dict(panels=phases, observed_counts=dict(observed),
                  later_documented_fraction_among_early=as_number(Fraction(observed["both"], observed["early_positive"])),
                  observed_counts_by_number_of_recorded_WGS_pups=by_k,
                  tests={mode: describe(law, observed["both"]) for mode, law in distributions.items()})
    return report, distributions


def analyze(path):
    families = json.loads(path.read_text())["families"]
    reports, laws = {}, []
    for family, data in families.items():
        reports[family], family_laws = family_stats(data)
        laws.append(family_laws)
    joint = {}
    observed = sum(r["observed_counts"]["both"] for r in reports.values())
    for mode in MODES:
        total_law = Counter({0: 1})
        for family_laws in laws:
            next_law = Counter()
            for a, n in total_law.items():
                for b, m in family_laws[mode].items():
                    next_law[a + b] += n * m
            total_law = next_law
        joint[mode] = describe(total_law, observed)
    return dict(families=reports, combined_tests=joint)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", nargs="?", type=Path, default=Path(__file__).with_name("profiles.json"))
    print(json.dumps(analyze(parser.parse_args().profiles), indent=2, allow_nan=False))
