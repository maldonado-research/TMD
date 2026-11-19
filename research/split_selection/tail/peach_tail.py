"""Exact bounds for a sum of one-sided comparisons given only its marginal probabilities."""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path

ZERO = Fraction(0)
ONE = Fraction(1)


def read_margins(path):
    """Compute the uniform and five-read-gated marginal benchmarks for this archived frame."""
    raw = path.read_bytes()
    data = json.loads(raw)
    q = []
    pass_by_site = defaultdict(list)
    observed = 0
    for i, (_, site, a, b, k, one_sided) in enumerate(data["eligible"]):
        if not 2 <= k <= a + b or min(a, b) <= 0 or type(one_sided) is not bool:
            raise ValueError("Invalid split profile")
        total = comb(a + b, k)
        q.append(Fraction(comb(a, k) + comb(b, k), total))
        # A split pair misses the five-read gate only if both alternate counts are below five.
        missed = sum(comb(a, x) * comb(b, k-x)
                     for x in range(max(0, k-4), min(k, 4)+1))
        pass_by_site[site].append((i, ONE - Fraction(missed, total)))
        observed += one_sided
    gated = q.copy()
    witnesses = []
    for site, (outside_max, _) in data["other_library_evidence_by_site"].items():
        local = pass_by_site[site]
        if outside_max >= 5 or any(p == 1 for _, p in local):
            continue
        capable = [(i, p) for i, p in local if p > 0]
        if len(capable) != 1:
            raise ValueError("Expected exactly one possible within-pair gate witness")
        i, p = capable[0]
        # Any one-sided outcome passes whenever a pair is capable of meeting the gate.
        gated[i] = q[i] / p
        witnesses.append(site)
    return q, gated, observed, sorted(witnesses), hashlib.sha256(raw).hexdigest()


def upper_bound(qs, threshold):
    """Return the sharp upper probability and the minimizing number of largest margins removed."""
    if not 1 <= threshold <= len(qs) or any(q < 0 or q > 1 for q in qs):
        raise ValueError("Need probabilities and an attainable count threshold")
    ordered = sorted(qs, reverse=True)
    remaining = sum(ordered, ZERO)
    candidates = []
    for removed in range(threshold):
        candidates.append((remaining / (threshold - removed), removed))
        remaining -= ordered[removed]
    raw, removed = min(candidates)
    return min(ONE, raw), removed


def independent_tail(qs, threshold):
    """Poisson-binomial tail for mutually independent indicators, using exact recursion."""
    weights = [ONE]
    for q in qs:
        updated = [ZERO] * (len(weights) + 1)
        for i, mass in enumerate(weights):
            updated[i] += (1 - q) * mass
            updated[i + 1] += q * mass
        weights = updated
    return sum(weights[threshold:], ZERO)


def describe(q):
    return {"exact": str(q), "decimal": float(q)}


def scenario(qs, r):
    n = len(qs)
    upper, dropped = upper_bound(qs, r)
    complement, _ = upper_bound([1 - q for q in qs], n - r + 1)
    return {
        "expected_one_sided": describe(sum(qs, ZERO)),
        "forced_one_sided": qs.count(1),
        "mean_over_threshold": describe(sum(qs, ZERO) / r),
        "sharp_lower": describe(1 - complement),
        "sharp_upper": describe(upper),
        "largest_probabilities_removed_in_optimal_bound": dropped,
        "tail_assuming_mutual_independence": describe(independent_tail(qs, r)),
        "upper_if_marginals_multiplied_then_capped_at_one": {
            str(c): describe(upper_bound([min(ONE, c*q) for q in qs], r)[0])
            for c in (Fraction(5, 4), Fraction(2), Fraction(5))
        }
    }


def analyze(path):
    qs, gated, r, witnesses, digest = read_margins(path)
    return {
        "input_sha256": digest, "comparisons": len(qs), "observed_one_sided": r,
        "conditional_frame": "Treat all selected depths, alternate totals and the outside library evidence as fixed.",
        "single_gate_witness_sites": witnesses,
        "uniform": scenario(qs, r),
        "five_read_gate": scenario(gated, r),
        "interpretation": "In each scenario the given probabilities are prescribed marginals in the full frame. Unknown ascertainment and split composition can change them."
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", type=Path, help="influence_profiles.json from the Ji workbook replay")
    print(json.dumps(analyze(parser.parse_args().profiles), indent=2))
