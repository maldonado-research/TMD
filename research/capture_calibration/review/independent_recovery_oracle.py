#!/usr/bin/env python3
"""Independent finite recovery oracle, prepared without producer code.

Forward marks are enumerated as assignments on labelled units. The inverse is
computed by general rational Gauss-Jordan elimination. The implementation being
reviewed is optionally imported only at comparison time, after a SHA pin.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys


def assignments(j: int, c: F) -> list[F]:
    out = [F(0) for _ in range(j + 1)]
    for bits in itertools.product((0, 1), repeat=j):
        weight = F(1)
        for bit in bits:
            weight *= c if bit else 1 - c
        out[sum(bits)] += weight
    return out


def matrix(B: int, c: F) -> list[list[F]]:
    rows = [[F(0) for _ in range(B)] for _ in range(B)]
    for j in range(1, B + 1):
        law = assignments(j, c)
        for ell in range(1, j + 1):
            rows[ell - 1][j - 1] = law[ell]
    return rows


def forward(a: list[F], c: F) -> list[F]:
    M = matrix(len(a), c)
    return [sum((x * y for x, y in zip(row, a)), F(0)) for row in M]


def eliminate(M: list[list[F]], v: list[F]) -> list[F]:
    n = len(v)
    augmented = [list(row) + [rhs] for row, rhs in zip(M, v)]
    for pivot in range(n):
        candidate = next(k for k in range(pivot, n) if augmented[k][pivot])
        augmented[pivot], augmented[candidate] = augmented[candidate], augmented[pivot]
        div = augmented[pivot][pivot]
        augmented[pivot] = [x / div for x in augmented[pivot]]
        for k in range(n):
            if k == pivot:
                continue
            fac = augmented[k][pivot]
            augmented[k] = [x - fac * y for x, y in zip(augmented[k], augmented[pivot])]
    return [row[-1] for row in augmented]


def inverse(nu: list[F], c: F) -> list[F]:
    return eliminate(matrix(len(nu), c), nu)


def bounds(nu: list[F], c: F) -> tuple[F, F]:
    b = sum(nu, F(0))
    return b / (1 - (1 - c) ** len(nu)), b / c


def text_fraction(v: F) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def synthetic_cases():
    for B in range(1, 9):
        shapes = (
            [F(int(j == 0)) for j in range(B)],
            [F(int(j == B - 1)) for j in range(B)],
            [F(1, B) for _ in range(B)],
            [F(2 ** j, 2 ** B - 1) for j in range(B)],
        )
        for c in (F(1), F(1, 2), F(1, 4), F(2, 3), F(1, 8), F(7, 8)):
            for m in (F(0), F(1, 3), F(1), F(7, 2), F(20)):
                for shape in shapes:
                    a = [m * p for p in shape]
                    yield B, c, m, shape, a


def run_independent():
    checks = 0
    cases = 0
    assignment_states_in_one_forward_table = 0
    record = []
    for B, c, m, shape, a in synthetic_cases():
        cases += 1
        nu = forward(a, c)
        recovered = inverse(nu, c)
        if recovered != a:
            raise RuntimeError("Matrix-elimination round trip failed")
        checks += 1
        for original, result in zip(a, recovered):
            if original != result:
                raise RuntimeError("Positive intensity coefficient failed")
            checks += 1
        if sum(recovered, F(0)) != m:
            raise RuntimeError("Total positive intensity failed")
        checks += 1
        lower, upper = bounds(nu, c)
        if not lower <= m <= upper:
            raise RuntimeError("Void bound failed")
        checks += 1
        b_enumerated = sum((a[j - 1] * (1 - assignments(j, c)[0]) for j in range(1, B + 1)), F(0))
        if b_enumerated != sum(nu, F(0)):
            raise RuntimeError("Void intensity failed")
        checks += 1
        mean_enumerated = sum((a[j - 1] * sum((F(k) * p for k, p in enumerate(assignments(j, c))), F(0)) for j in range(1, B + 1)), F(0))
        if mean_enumerated != sum((F(k) * p for k, p in enumerate(nu, 1)), F(0)):
            raise RuntimeError("Count mean failed")
        checks += 1
        if mean_enumerated != c * sum((F(j) * a_j for j, a_j in enumerate(a, 1)), F(0)):
            raise RuntimeError("Mean thinning failed")
        checks += 1
        if shape[0] == 1:
            if upper != m:
                raise RuntimeError("Singleton upper-bound attainment failed")
            checks += 1
        if shape[-1] == 1:
            if lower != m:
                raise RuntimeError("Maximum mark lower-bound attainment failed")
            checks += 1
        assignment_states_in_one_forward_table += sum(2 ** j for j in range(1, B + 1))
        record.append({"B": B, "c": text_fraction(c), "m": text_fraction(m),
                       "pi": [text_fraction(x) for x in shape],
                       "a": [text_fraction(x) for x in a],
                       "nu": [text_fraction(x) for x in nu]})

    # Exact complete-law ambiguities, not merely matching first moments.
    unknown_c_left = forward([F(1)], F(1, 2))
    unknown_c_right = forward([F(2)], F(1, 4))
    if unknown_c_left != unknown_c_right:
        raise RuntimeError("Unknown recovery singleton ambiguity failed")
    checks += 1
    base = forward([F(0), F(1)], F(1, 3))
    # A zero mark contributes identically zero to every positive jump.
    zero_mark_intensity = F(7, 2)
    zero_forward = [x + zero_mark_intensity * F(0) for x in base]
    if zero_forward != base or 1 + zero_mark_intensity == 1:
        raise RuntimeError("Zero mark ambiguity failed")
    checks += 1
    incompatible = inverse([F(0), F(1)], F(1, 2))
    if incompatible != [F(-4), F(4)]:
        raise RuntimeError("Incompatible positive observation inverse failed")
    checks += 1
    # Exact perturbation illustrates the alternating inverse at c=1/4.
    initial = [F(1), F(1)]
    observed = forward(initial, F(1, 4))
    epsilon = F(1, 1024)
    perturbed = inverse([observed[0], observed[1] + epsilon], F(1, 4))
    if perturbed != [1 - 24 * epsilon, 1 + 16 * epsilon]:
        raise RuntimeError("Recovery perturbation identity failed")
    checks += 1
    for c in (F(1), F(1, 2), F(1, 8)):
        if inverse([F(0)] * 8, c) != [F(0)] * 8:
            raise RuntimeError("Zero intensity case failed")
        checks += 1
    serialized = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return {
        "status": "PASS",
        "method": "labelled Bernoulli assignment enumeration and rational Gauss-Jordan elimination",
        "producer_imported": False,
        "synthetic_cases": cases,
        "exact_checks": checks,
        "assignment_states_in_one_forward_table_per_case_total": assignment_states_in_one_forward_table,
        "assignment_states_are_not_extra_checks_or_biological_trials": True,
        "case_vector_sha256": hashlib.sha256(serialized).hexdigest(),
        "counterexamples": {
            "unknown_c": {"left_m": "1", "left_c": "1/2", "right_m": "2", "right_c": "1/4", "same_nu": ["1/2"]},
            "zero_mark": {"positive_m": "1", "additional_zero_intensity": "7/2", "total_m": "9/2", "unchanged_nu": [text_fraction(x) for x in base]},
            "incompatible_inverse": [text_fraction(x) for x in incompatible],
            "perturbation": {"c": "1/4", "delta_nu_2": "1/1024", "delta_a": ["-3/128", "1/64"]},
        },
        "limits": ["population exact coefficients only", "finite positive terminal marks only for total intensity identification", "known homogeneous iid unit retention", "no mutation-birth-rate fit", "no observed biological data", "no theorem novelty claim"],
    }


def run_comparison(implementation: Path, expected_sha256: str):
    observed_sha = hashlib.sha256(implementation.read_bytes()).hexdigest()
    if observed_sha != expected_sha256:
        raise RuntimeError("Implementation hash differs from reviewed freeze")
    spec = importlib.util.spec_from_file_location("reviewed_capture_calibration", implementation)
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    categories = {"forward_coefficients": 0, "forward_summary_fields": 0,
                  "inverse_coefficients": 0, "inverse_summary_and_law_fields": 0,
                  "point_bound_endpoints": 0, "rectangle_endpoints": 0,
                  "complete_law_witnesses": 0, "external_cap_refusals": 0,
                  "extreme_valid_forward_and_bounds": 0, "invalid_input_guards": 0}
    def check(ok, category):
        if not ok:
            raise RuntimeError("Producer disagreement: " + category)
        categories[category] += 1
    def admitted(v):
        return max(abs(v.numerator).bit_length(), v.denominator.bit_length()) <= 32
    inverse_cases = 0
    inverse_skips = 0
    bound_cases = 0
    bound_skips = 0
    for B, c, m, shape, a in synthetic_cases():
        law = {j: p for j, p in enumerate(shape, 1)}
        expected_nu = forward(a, c)
        model = producer.forward_jump_intensities(law, m, c)
        nu = model["positive_jump_intensities"]
        for j, value in enumerate(expected_nu, 1):
            check(nu[j] == value, "forward_coefficients")
        b = sum(expected_nu, F(0))
        expected_mean = sum((F(j) * value for j, value in enumerate(expected_nu, 1)), F(0))
        check(model["negative_log_zero_probability"] == b, "forward_summary_fields")
        check(model["mean_detected_count"] == expected_mean, "forward_summary_fields")
        check(model["positive_terminal_intensity"] == m, "forward_summary_fields")
        supplied = {j: value for j, value in enumerate(expected_nu, 1)}
        if all(admitted(value) for value in expected_nu):
            inverse_cases += 1
            solved = producer.invert_positive_jump_intensities(supplied, c)
            independent = inverse(expected_nu, c)
            for j, value in enumerate(independent, 1):
                check(solved["positive_terminal_weights"][j] == value, "inverse_coefficients")
            check(solved["positive_terminal_intensity"] == m, "inverse_summary_and_law_fields")
            check(solved["strictly_positive_marks_assumed"] is True, "inverse_summary_and_law_fields")
            check(solved["zero_mark_intensity_identified"] is False, "inverse_summary_and_law_fields")
            if m:
                for j, value in enumerate(shape, 1):
                    check(solved["conditional_positive_mark_law"][j] == value,
                          "inverse_summary_and_law_fields")
            else:
                check(solved["conditional_positive_mark_law"] is None,
                      "inverse_summary_and_law_fields")
        else:
            inverse_skips += 1
            try:
                producer.invert_positive_jump_intensities(supplied, c)
            except ValueError as error:
                check("external rational cap" in str(error), "external_cap_refusals")
            else:
                raise RuntimeError("Producer admitted an over-cap derived inverse input")
        if admitted(b):
            bound_cases += 1
            low, high = bounds(expected_nu, c)
            actual = producer.intensity_bounds(b, c, B)
            check(actual["lower"] == low, "point_bound_endpoints")
            check(actual["upper"] == high, "point_bound_endpoints")
        else:
            bound_skips += 1
            try:
                producer.intensity_bounds(b, c, B)
            except ValueError as error:
                check("external rational cap" in str(error), "external_cap_refusals")
            else:
                raise RuntimeError("Producer admitted an over-cap derived bound input")

    # Endpoints of independent, explicitly rectangular external ranges.
    for B in range(1, 9):
        for bl, bu in ((F(0), F(1)), (F(1, 2), F(3, 4)), (F(1), F(1))):
            for cl, cu in ((F(1, 8), F(1, 2)), (F(1, 3), F(1)), (F(1), F(1))):
                actual = producer.rectangle_bounds(bl, bu, cl, cu, B)
                check(actual["lower"] == bl / (1 - (1-cu)**B), "rectangle_endpoints")
                check(actual["upper"] == bu / cl, "rectangle_endpoints")

    one = producer.forward_jump_intensities({1: F(1)}, F(1), F(1, 2))
    two = producer.forward_jump_intensities({1: F(1)}, F(2), F(1, 4))
    check(one["positive_jump_intensities"] == two["positive_jump_intensities"] == {1: F(1, 2)},
          "complete_law_witnesses")
    base = producer.forward_jump_intensities({2: F(1)}, F(1), F(1, 3))
    augmented = producer.forward_jump_intensities({0: F(7, 9), 2: F(2, 9)}, F(9, 2), F(1, 3))
    check(base["positive_jump_intensities"] == augmented["positive_jump_intensities"] == {1: F(4, 9), 2: F(1, 9)},
          "complete_law_witnesses")
    check(base["positive_terminal_intensity"] == augmented["positive_terminal_intensity"] == F(1),
          "complete_law_witnesses")
    recovered = producer.invert_positive_jump_intensities(augmented["positive_jump_intensities"], F(1, 3))
    check(recovered["positive_terminal_intensity"] == F(1), "complete_law_witnesses")
    check(recovered["zero_mark_intensity_identified"] is False, "complete_law_witnesses")

    # Valid extreme external values: derived arithmetic need not fit the parser.
    for c in (F(1, 2**31), F(2**31-1, 2**31)):
        expected = forward([F(0)] * 7 + [F(20)], c)
        actual = producer.forward_jump_intensities({8: F(1)}, F(20), c)
        for j, value in enumerate(expected, 1):
            check(actual["positive_jump_intensities"][j] == value,
                  "extreme_valid_forward_and_bounds")
        interval = producer.intensity_bounds(F(20), c, 8)
        check(interval["lower"] == F(20) / (1-(1-c)**8), "extreme_valid_forward_and_bounds")
        check(interval["upper"] == F(20) / c, "extreme_valid_forward_and_bounds")
        if not all(admitted(value) for value in expected):
            try:
                producer.invert_positive_jump_intensities(
                    {j: value for j, value in enumerate(expected, 1)}, c)
            except ValueError as error:
                check("external rational cap" in str(error), "external_cap_refusals")
            else:
                raise RuntimeError("Extreme over-cap derived inverse was admitted")
        extreme_b = sum(expected, F(0))
        if not admitted(extreme_b):
            try:
                producer.intensity_bounds(extreme_b, c, 8)
            except ValueError as error:
                check("external rational cap" in str(error), "external_cap_refusals")
            else:
                raise RuntimeError("Extreme over-cap derived bound input was admitted")
    check(producer.intensity_bounds(F(20), F(1, 2**31), 8)["upper"] > 20,
          "extreme_valid_forward_and_bounds")

    bad = [
        lambda: producer.forward_jump_intensities({1: True}, 1, F(1, 2)),
        lambda: producer.forward_jump_intensities({True: F(1)}, 1, F(1, 2)),
        lambda: producer.forward_jump_intensities({1: F(1)}, 1, 0),
        lambda: producer.forward_jump_intensities({1: F(1)}, 1, F(1, 2**32)),
        lambda: producer.forward_jump_intensities({1: F(1)}, 1, 0.5),
        lambda: producer.forward_jump_intensities({1: F(1)}, 21, F(1, 2)),
        lambda: producer.invert_positive_jump_intensities({1: F(0), 2: F(1)}, F(1, 2)),
        lambda: producer.invert_positive_jump_intensities({2: F(1)}, F(1, 2)),
        lambda: producer.invert_positive_jump_intensities({1: F(1)}, F(1, 2**31)),
        lambda: producer.intensity_bounds(F(1), F(1, 2), True),
        lambda: producer.rectangle_bounds(F(1), F(0), F(1, 4), F(1, 2), 2),
        lambda: producer.rectangle_bounds(F(0), F(1), F(1, 2), F(1, 4), 2),
    ]
    for operation in bad:
        try:
            operation()
        except (TypeError, ValueError):
            categories["invalid_input_guards"] += 1
        else:
            raise RuntimeError("Producer accepted a declared invalid input")
    return {"status": "PASS", "implementation_sha256": observed_sha,
            "synthetic_forward_cases": 960, "accepted_domain_inverse_cases": inverse_cases,
            "inverse_cases_refused_for_derived_external_cap": inverse_skips,
            "accepted_domain_point_bound_cases": bound_cases,
            "point_bound_cases_refused_for_derived_external_cap": bound_skips,
            "comparison_checks_by_category": categories,
            "exact_comparison_checks": sum(categories.values()),
            "unrestricted_helper_composition_claimed": False}


def main():
    if sys.flags.optimize:
        raise SystemExit("Refusing optimized Python: review guards must remain active.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    if bool(args.implementation) != bool(args.expected_sha256):
        raise SystemExit("Supply both --implementation and --expected-sha256 for producer comparison.")
    receipt = run_independent()
    if args.implementation:
        receipt["producer_comparison"] = run_comparison(args.implementation, args.expected_sha256)
        receipt["producer_imported"] = True
    receipt["oracle_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "synthetic_cases": receipt["synthetic_cases"], "exact_checks": receipt["exact_checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
