"""Exact reassignment of measured parental allele fractions to recorded markers."""
import csv
import json
from bisect import bisect_left
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import accumulate, permutations
from math import lcm
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "mouse" / "ee.tsv"


@dataclass(frozen=True)
class Marker:
    family: str
    parent: str
    discovery: int
    p: F
    r: F
    weight: F

    @property
    def q(self):
        return F(self.discovery, 10)


def load(carrier_column):
    with SOURCE.open() as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    sizes = Counter(s["family"] for s in rows)
    if len(rows) != 17 or sorted(sizes.values()) != [8, 9]:
        raise ValueError("Unexpected marker or family roster")
    markers = []
    for s in rows:
        x = int(s["early_wgs_carriers"]) + int(s["late_wgs_carriers"])
        future = int(s[carrier_column]) - x
        n = int(s["offspring_assayed"]) - 10
        if not 0 <= future <= n or not 1 <= x <= 10:
            raise ValueError("Inconsistent offspring counts")
        markers.append(Marker(s["family"], s["parent"], x, F(s["parent_alt_percent"]) / 100,
                              F(future, n), F(1, len(sizes) * sizes[s["family"]])))
    return markers


def strata_of(markers, fields):
    strata = defaultdict(list)
    for m in markers:
        strata[tuple(getattr(m, name) for name in fields)].append(m)
    return list(strata.values())


def group_distribution(group, p_scale, r_scale):
    """Multiplicities retain each swap of labeled markers, including tied fractions."""
    p = [int(m.p * p_scale) for m in group]
    r = [int(m.weight * m.r * r_scale) for m in group]
    return Counter(sum(a*b for a, b in zip(assignment, r)) for assignment in permutations(p))


def add_distributions(one, two):
    total = Counter()
    for a, n in one.items():
        for b, k in two.items():
            total[a+b] += n*k
    return total


def exact_tail(markers, groups):
    p_scale = lcm(*(m.p.denominator for m in markers))
    r_scale = lcm(*((m.weight*m.r).denominator for m in markers))
    obs = sum(int(m.p*p_scale) * int(m.weight*m.r*r_scale) for m in markers)
    by_family = {}
    for group in groups:
        family = group[0].family
        counts = group_distribution(group, p_scale, r_scale)
        by_family[family] = add_distributions(by_family.get(family, {0: 1}), counts)
    a, b = by_family.values()
    values = sorted(b)
    prefix = [0, *accumulate(b[v] for v in values)]
    total = sum(a.values()) * prefix[-1]
    ge = sum(n * (prefix[-1] - prefix[bisect_left(values, obs-v)]) for v, n in a.items())
    expected = (F(sum(v*n for v, n in a.items()), sum(a.values()))
                + F(sum(v*n for v, n in b.items()), prefix[-1]))
    return total, ge, 2*(obs-expected)/(p_scale*r_scale)


def brier(forecast, rate):
    return forecast**2 + rate*(1-2*forecast)


def evaluate(markers, fields):
    groups = strata_of(markers, fields)
    covariance, variance = F(0), F(0)
    for group in groups:
        mean_p = sum(m.p for m in group)/len(group)
        mean_r = sum(m.r for m in group)/len(group)
        covariance += sum(m.weight*(m.p-mean_p)*(m.r-mean_r) for m in group)
        variance += sum(m.weight*(m.p-mean_p)**2 for m in group)
    gain = sum(m.weight*(brier(m.q, m.r)-brier(m.p, m.r)) for m in markers)
    total, ge, placement = exact_tail(markers, groups)
    if placement != 2*covariance:
        raise ArithmeticError("Enumeration does not reproduce covariance identity")
    return dict(strata=fields, groups=len(groups), multi_marker_groups=sum(len(g)>1 for g in groups),
                groups_with_distinct_parent_values=sum(len({m.p for m in g})>1 for g in groups),
                allocations=total, at_least_observed=ge, tail_fraction=str(F(ge,total)),
                tail=float(F(ge,total)), observed_gain=float(gain), expected_shuffled_gain=float(gain-placement),
                gain_from_matching=float(placement), gain_over_stratum_mean_parent_forecast=float(placement-variance))


def calculate():
    baseline = load("table2_carriers")
    strata = ["family", "discovery"]
    midpoint_gain = sum(m.weight*(brier(m.q,m.r)-brier((m.p+m.q)/2,m.r)) for m in baseline)
    parent_gain = sum(m.weight*(brier(m.q,m.r)-brier(m.p,m.r)) for m in baseline)
    disagreement = sum(m.weight*(m.q-m.p)**2/4 for m in baseline)
    if midpoint_gain != parent_gain/2 + disagreement:
        raise ArithmeticError("Midpoint loss identity differs from direct score")
    analyses = [evaluate(baseline, f) for f in (["family"], strata, [*strata, "parent"])]
    # WGS frequency is constant within these strata, so averaging halves the matching term.
    expected_shuffled_midpoint = float(midpoint_gain) - analyses[1]["gain_from_matching"] / 2
    return {"table2": analyses,
            "workbook_sensitivity": evaluate(load("workbook_carriers"), strata),
            "midpoint_gain_components": {"half_parent_gain": float(parent_gain/2),
                "quarter_squared_disagreement": float(disagreement), "midpoint_gain": float(midpoint_gain),
                "expected_midpoint_gain_shuffling_within_discovery_count": expected_shuffled_midpoint}}


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2))
