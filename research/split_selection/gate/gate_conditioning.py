"""Site-local conditional one-sided allocation at an any-library minimum count."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from math import comb, prod
from pathlib import Path


def pair_terms(a, b, k, threshold):
    """Return P(one-sided and scored), P(no library passes), and their intersection."""
    if min(a, b, threshold) < 1 or not 0 <= k <= a + b:
        raise ValueError("Invalid depths, total alternate count or threshold")
    slots = comb(a + b, k)
    one = Fraction(comb(a, k) + comb(b, k), slots) if k >= 2 else Fraction()
    lower = max(0, k - b, k - threshold + 1)
    upper = min(a, k, threshold - 1)
    fail = Fraction(sum(comb(a, x) * comb(b, k - x) for x in range(lower, upper + 1)), slots)
    return one, fail, one if k < threshold else Fraction()


def site_score(profiles, outside_pass, threshold=5):
    """Unfiltered E[O], P(site passes), E[O | site passes] under product allocations."""
    terms = [pair_terms(a, b, k, threshold) for a, b, k in profiles]
    ordinary = sum((one for one, _, _ in terms), Fraction())
    if outside_pass:
        return ordinary, Fraction(1), ordinary
    failures = [fail for _, fail, _ in terms]
    pass_probability = 1 - prod(failures, start=Fraction(1))
    if not pass_probability:
        return ordinary, Fraction(), None
    # Remove contributions from outcomes where every pair fails the screen.
    expected_on_failure = sum(
        (joint * prod(failures[:i] + failures[i + 1:], start=Fraction(1))
         for i, (_, _, joint) in enumerate(terms)), Fraction())
    return ordinary, pass_probability, (ordinary - expected_on_failure) / pass_probability


def analyze(data):
    records = defaultdict(list)
    for tissue, site, a, b, k, one_sided in data["eligible"]:
        if k < 2 or type(one_sided) is not bool:
            raise ValueError("Invalid eligible comparison")
        records[site].append((a, b, k, one_sided))
    if set(records) - set(data["other_library_evidence_by_site"]):
        raise ValueError("Unmatched site identifier")
    strata = defaultdict(Counter)
    combined = Counter()
    sensitive = {}
    for site, (outside_max, _) in data["other_library_evidence_by_site"].items():
        rows = records[site]
        outside = outside_max >= 5
        before, passed, after = site_score([row[:3] for row in rows], outside)
        if after is None:
            raise ValueError(f"The recorded site {site} cannot satisfy the five-read screen")
        status = ("outside_library_passes" if outside else
                  "automatic_given_split_totals" if passed == 1 else "sensitive_to_allocation")
        observed = sum(row[3] for row in rows)
        values = {"sites": 1, "eligible_pairs": len(rows), "observed_one_sided": observed,
                  "expected_without_gate": before, "expected_given_gate": after}
        strata[status].update(values)
        combined.update(values)
        if 0 < passed < 1:
            sensitive[site] = {"eligible_pairs": len(rows), "gate_probability": str(passed),
                               "observed_one_sided": observed,
                               "expected_without_gate": round(float(before), 9),
                               "expected_given_gate": round(float(after), 9)}
    def report(values):
        return {k: round(float(v), 9) if isinstance(v, Fraction) else v for k, v in values.items()}
    return {"threshold": 5, "totals": report(combined),
            "by_site_status": {k: report(v) for k, v in sorted(strata.items())},
            "sensitive_sites": sensitive}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    default_profiles = Path(__file__).resolve().parents[1] / "influence" / "influence_profiles.json"
    p.add_argument("profiles", type=Path, nargs="?", default=default_profiles,
                   help="influence_profiles.json extracted from the original workbooks")
    print(json.dumps(analyze(json.loads(p.parse_args().profiles.read_bytes())), indent=2))
