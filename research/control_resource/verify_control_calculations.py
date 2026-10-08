#!/usr/bin/env python3
"""Recover standard illustrative CP/PPV claims using exact arithmetic only."""

import argparse
from fractions import Fraction
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational_text(value):
    return f"{value.numerator}/{value.denominator}"


def fixed_decimal(value, places=10):
    """Display-only decimal, rounded half upward using integer arithmetic."""
    require(value >= 0, "display routine expects nonnegative values")
    scale = 10 ** places
    quotient, remainder = divmod(value.numerator * scale, value.denominator)
    if 2 * remainder >= value.denominator:
        quotient += 1
    whole, tail = divmod(quotient, scale)
    return f"{whole}.{tail:0{places}d}"


def power_comparison(n, q, alpha):
    """Compare (1-q)^n to alpha after clearing positive denominators.

    For q in [0,1], U=1-alpha^(1/n) satisfies:
      U <= q iff (1-q)^n <= alpha.
    The comparison uses arbitrary-precision integers, never root evaluation.
    """
    require(type(n) is int and n > 0, "n must be a positive integer")
    require(isinstance(q, Fraction) and 0 <= q <= 1, "q must be rational in [0,1]")
    require(isinstance(alpha, Fraction) and 0 < alpha < 1, "alpha must be in (0,1)")
    left = alpha.denominator * (q.denominator - q.numerator) ** n
    right = alpha.numerator * q.denominator ** n
    sign = (left > right) - (left < right)
    return {
        "n": n,
        "q": rational_text(q),
        "alpha": rational_text(alpha),
        "left_expression": f"{alpha.denominator} * {q.denominator - q.numerator}^{n}",
        "right_expression": f"{alpha.numerator} * {q.denominator}^{n}",
        "comparison": {-1: "<", 0: "=", 1: ">"}[sign],
        "difference_sign": sign,
        "left_bit_length": left.bit_length(),
        "right_bit_length": right.bit_length(),
        "U_le_q": sign <= 0,
    }


def minimum_n(epsilon, alpha):
    """Find first passing n via monotonicity and exact integer comparisons."""
    require(0 < epsilon < 1, "epsilon must lie strictly between zero and one")
    lo, hi = 0, 1
    while not power_comparison(hi, epsilon, alpha)["U_le_q"]:
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if power_comparison(mid, epsilon, alpha)["U_le_q"]:
            hi = mid
        else:
            lo = mid
    return hi


def ppv(p, sensitivity, false_positive):
    require(all(isinstance(x, Fraction) for x in (p, sensitivity, false_positive)),
            "PPV inputs must be exact fractions")
    require(all(0 <= x <= 1 for x in (p, sensitivity, false_positive)),
            "PPV probabilities must be in [0,1]")
    true_positive_mass = p * sensitivity
    false_positive_mass = (1 - p) * false_positive
    require(true_positive_mass + false_positive_mass > 0,
            "PPV is undefined when positive-call probability is zero")
    return true_positive_mass / (true_positive_mass + false_positive_mass)


def calculate():
    alpha = Fraction(1, 20)
    minima = []
    for denominator, expected_n in ((100, 299), (1000, 2995), (10000, 29956)):
        epsilon = Fraction(1, denominator)
        n = minimum_n(epsilon, alpha)
        require(n == expected_n, "recovered minimum differs from handoff")
        passing = power_comparison(n, epsilon, alpha)
        failing = power_comparison(n - 1, epsilon, alpha)
        require(passing["U_le_q"] and not failing["U_le_q"],
                "minimum proof requires n passing and n-1 failing")
        minima.append({"epsilon": rational_text(epsilon), "minimum_n": n,
                       "n_passes": passing, "n_minus_1_fails": failing})

    lower = Fraction(5973551516, 10 ** 12)
    upper = Fraction(5973551517, 10 ** 12)
    lower_comparison = power_comparison(500, lower, alpha)
    upper_comparison = power_comparison(500, upper, alpha)
    require(lower_comparison["difference_sign"] == 1,
            "lower endpoint is not strictly below U")
    require(upper_comparison["difference_sign"] == -1,
            "upper endpoint is not strictly above U")
    bound_percent_display = fixed_decimal(100 * lower, 8)
    require(bound_percent_display == fixed_decimal(100 * upper, 8),
            "strict bracket endpoints do not imply one rounded display value")

    p, s = Fraction(1, 1000), Fraction(9, 10)
    predictive_values = []
    for f, expected in ((Fraction(1, 1000), Fraction(100, 211)),
                        (Fraction(1, 10000), Fraction(1000, 1111))):
        value = ppv(p, s, f)
        require(value == expected, "recovered PPV differs from handoff")
        # Independent cleared-denominator Bayes-identity check.
        require(value * (p * s + (1 - p) * f) == p * s,
                "PPV does not satisfy its defining probability identity")
        predictive_values.append({
            "target_frame_positive_prevalence": rational_text(p),
            "sensitivity": rational_text(s),
            "false_positive_probability": rational_text(f),
            "true_positive_mass": rational_text(p * s),
            "false_positive_mass": rational_text((1 - p) * f),
            "PPV_exact": rational_text(value),
            "PPV_percent_display": fixed_decimal(100 * value, 8),
            "exact_identity_verified": True,
        })

    return {
        "schema_version": 1,
        "status": "PASS",
        "scope": "standard hypothetical planning illustrations recovered from unpublished planning calculations",
        "arithmetic": "Python standard library arbitrary-precision integers and Fraction; no floating scientific comparisons",
        "alpha": rational_text(alpha),
        "confidence_level_single_metric": rational_text(1 - alpha),
        "zero_error_minima": minima,
        "hypothetical_500_trial_upper_bound": {
            "n": 500, "observed_errors_assumed": 0,
            "strict_lower": "5973551516/1000000000000",
            "strict_upper": "5973551517/1000000000000",
            "lower_proof": lower_comparison, "upper_proof": upper_comparison,
            "bound_percent_display_rounded_8_places": bound_percent_display,
        },
        "predictive_value_illustrations": predictive_values,
        "assumptions": [
            "Fixed sample size with no outcome-dependent stopping for the CP calculation.",
            "Independent homogeneous Bernoulli origin-error trials for the CP calculation.",
            "Independent origin-negative ancestry/episode truth, not only genotype-negative truth.",
            "Complete frozen caller, eligible candidate frame, error definition and exclusions.",
            "PPV p, s and f apply to the same target-frame origin truth and complete caller.",
        ],
        "limitations": {
            "native_control_observations": False,
            "native_p_s_f_pi_estimated": False,
            "mutation_rate_estimated": False,
            "achieved_power": False,
            "new_alpha_or_threshold_commitment": False,
            "selected_actual_study_size": False,
            "qualified_external_review_obtained": False,
            "truth_without_authentication_may_measure_only_disagreement": True,
            "pooling_contexts_does_not_establish_route_calibration": True,
            "selected_control_panel_mixture_is_not_target_prevalence": True,
            "original_historical_receipt_reconstructed": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write newly computed result JSON.")
    parser.add_argument("--check-against", type=Path, help="Compare exactly with stored JSON.")
    args = parser.parse_args()
    result = calculate()
    if args.check_against:
        require(json.loads(args.check_against.read_text()) == result,
                "stored result differs from freshly computed exact result")
    if args.output:
        require(Path(__file__).resolve().parent not in args.output.resolve().parents,
                "output must remain outside the packaged directory")
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: exact n/n-1 proofs, strict 500-trial bracket, and PPV identities.")


if __name__ == "__main__":
    main()
