#!/usr/bin/env python3
"""Reproduce independent internal synthetic review checks using stdlib only.

The candidate is a floating verifier, not a certified prospective decision engine.
Run --check to verify these evidence counts and the reviewed file snapshots.
MIT under the project terms.
"""

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "review"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    path = ROOT / "verify_design.py"
    candidate = {"__name__": "independent_review_candidate", "__file__": str(path)}
    exec(compile(path.read_text(), str(path), "exec"), candidate)
    assert candidate["verify"]() == json.loads((ROOT / "VERIFICATION_RECEIPT.json").read_text())

    # These endpoints have closed forms independent of the candidate root solver.
    cp_checks = 0
    for n in (1, 2, 7, 12):
        for alpha in (0.05, 0.01):
            zero = candidate["cp_interval"](n, 0, alpha)
            full = candidate["cp_interval"](n, n, alpha)
            assert zero[0] == 0 and full[1] == 1
            assert math.isclose(zero[1], 1 - (alpha / 2) ** (1 / n), abs_tol=2e-12)
            assert math.isclose(full[0], (alpha / 2) ** (1 / n), abs_tol=2e-12)
            cp_checks += 2

    # Exact Fraction vertices independently check the candidate greedy optimizer.
    generator = random.Random(20261003)
    lp_checks = 0
    for case in range(240):
        categories = 3 + case % 4
        weights = [generator.randint(1, 20) for _ in range(categories)]
        true_p = [Fraction(w, sum(weights)) for w in weights]
        box = [(x * Fraction(generator.randint(0, 10), 10),
                x + (1 - x) * Fraction(generator.randint(0, 10), 10)) for x in true_p]
        coefficients = [Fraction(generator.randint(-30, 30), 7) for _ in range(categories)]
        values = []
        for free in range(categories):
            fixed = [i for i in range(categories) if i != free]
            for bits in itertools.product((0, 1), repeat=categories - 1):
                vertex = [Fraction(0) for _ in range(categories)]
                for i, bit in zip(fixed, bits):
                    vertex[i] = box[i][bit]
                vertex[free] = 1 - sum(vertex)
                if box[free][0] <= vertex[free] <= box[free][1]:
                    values.append(sum(a * b for a, b in zip(vertex, coefficients)))
        lower, upper = candidate["score_bounds"](
            [(float(a), float(b)) for a, b in box], [float(c) for c in coefficients])
        assert math.isclose(lower, float(min(values)), abs_tol=2e-12)
        assert math.isclose(upper, float(max(values)), abs_tol=2e-12)
        lp_checks += 1

    # Verify stationarity for the declared unpenalized-intercept/slope-ridge loss.
    ridge_checks = 0
    for x, y in [([1, 1], [2, 4]), ([-1, 0, 2], [4, 1, -2]), ([3], [7])]:
        intercept, slope = candidate["ridge"](x, y)
        residual = [intercept + slope * a - b for a, b in zip(x, y)]
        assert abs(sum(residual)) < 1e-12
        assert abs(sum(a * r for a, r in zip(x, residual)) + 0.01 * slope) < 1e-12
        ridge_checks += 1

    invalid_counts = [
        lambda: candidate["smooth_triad"]([0, 0, 0]),
        lambda: candidate["smooth_triad"]([True, 1, 1]),
        lambda: candidate["smooth_triad"]([1.5, 1, 1]),
        lambda: candidate["smooth_binary"](1, 0),
        lambda: candidate["smooth_binary"](3, 2),
        lambda: candidate["smooth_binary"](True, 2),
    ]
    invalid_scores = [
        lambda: candidate["score_bounds"]([(0, 1)] * 3, [float("nan"), 0, 0]),
        lambda: candidate["score_bounds"]([(0, 1)] * 3, [float("inf"), 0, 0]),
        lambda: candidate["score_bounds"]([(0.5000000000002, 0.7), (0.5, 0.7)], [0, 1]),
        lambda: candidate["score_bounds"]([(0, 0.4999999999999), (0, 0.5)], [0, 1]),
    ]
    for call in invalid_counts + invalid_scores:
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("An invalid count, coefficient or empty region was accepted")

    # An independent nonuniform-supply example checks the core algebra directly.
    q, theta, eta = (0.2, 0.5, 0.3), 0.7, 1.1
    p = candidate["forecast"](q, theta, eta)
    j = p[1] ** 2 * q[0] * q[2] / (p[0] * p[2] * q[1] ** 2)
    assert math.isclose(j, math.exp(2 * theta), rel_tol=1e-12)
    quadratic = [q[i] * math.exp(-theta * s ** 2 + eta * s) for i, s in enumerate((1, 0, -1))]
    quadratic = [v / sum(quadratic) for v in quadratic]
    assert all(math.isclose(a, b, rel_tol=1e-12) for a, b in zip(p, quadratic))
    left = candidate["conditional_count_distribution"](8, 2, q, theta, -2)
    right = candidate["conditional_count_distribution"](8, 2, q, theta, 3)
    assert left.keys() == right.keys()
    assert all(math.isclose(left[k], right[k], rel_tol=1e-12) for k in left)
    uniform = (1 / 3,) * 3
    pair = [candidate["forecast"](uniform, 0.4, e) for e in (1.3, -1.3)]
    pooled = [(a + b) / 2 for a, b in zip(*pair)]
    assert math.isclose(math.log(pooled[1] / math.sqrt(pooled[0] * pooled[2])),
                        0.4 - math.log(math.cosh(1.3)), rel_tol=1e-12)
    recovered = (2 / 7, 3 / 7, 2 / 7)
    assert math.isclose(math.log(recovered[1] / math.sqrt(recovered[0] * recovered[2])),
                        math.log(1.5), rel_tol=1e-12)
    assert math.isclose(recovered[1] ** 2 / (recovered[0] * recovered[2]), 2.25, rel_tol=1e-12)

    return {
        "owner_receipt_matches_recomputed_checks": True,
        "source_optimizer_random_exact_vertex_cases": lp_checks,
        "CP_boundary_closed_form_cases": cp_checks,
        "ridge_normal_equation_cases": ridge_checks,
        "invalid_count_cases_rejected": len(invalid_counts),
        "corrected_finite_input_and_tiny_empty_region_cases_rejected": len(invalid_scores),
        "independent_core_identity_cases": 5,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    checks = verify()
    if args.check:
        receipt = json.loads((REVIEW / "REVIEW_RECEIPT.json").read_text())
        assert checks == receipt["reviewer_check_counts"]
        for relative_path, digest in receipt["verified_file_sha256"].items():
            assert sha256(ROOT / relative_path) == digest, relative_path
        print("PASS: independent review checks and reviewed candidate hashes agree")
    else:
        print(json.dumps(checks, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
