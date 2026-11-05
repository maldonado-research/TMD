#!/usr/bin/env python3
"""Exact two-context sensitivity of the fixed reference curvature statistic.

The reference ordering is frozen at zero differential recovery. Positive,
externally justified rational bounds constrain the actual conditional tilt;
their declared noncoverage allocation is added to the supremum tail probability.
No controls are estimated and no biological observation contract is verified.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

# Installed beside the existing conditional_curvature directory. A scratch
# verification may instead put that unchanged directory on PYTHONPATH.
_ENGINE_DIR = Path(__file__).resolve().parent.parent / "conditional_curvature"
if _ENGINE_DIR.is_dir():
    sys.path.insert(0, str(_ENGINE_DIR))
from baseline_conditional_homogeneity import _PairedContext, _fiber_weights
from conditional_homogeneity import MAX_CONTEXT_N, MAX_TOTAL_N, _rational, load_input

MAX_FIBER_SIZE = MAX_CONTEXT_N // 2 + 1
MAX_WEIGHT_BITS = MAX_TOTAL_N + 1
MAX_POLYNOMIAL_INTEGER_BITS = 12_000


def _positive_interval(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("differential_tilt_interval requires two rational endpoints")
    lower, upper = (_rational(x, "differential tilt endpoint") for x in value)
    if not 0 < lower <= upper:
        raise ValueError("Require finite 0 < lower <= upper; no unbounded interval")
    return lower, upper


def _polynomial(coefficients, point):
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = value * point + coefficient
    return value


def certified_reference_supremum(weights, observed_index, lower, upper):
    """Exact supremum, only after certifying a contiguous strict complement.

Positive weights index every integer from zero. E={j:h_j<=h_observed}
remains fixed for every tilt. If C=E^c is contiguous, its probability is
unimodal in positive tilt; hence P_t(E) is maximized at an interval endpoint.
Arbitrary events or disconnected strict complements are not admitted.
"""
    if not isinstance(weights, (tuple, list)) or not 1 <= len(weights) <= MAX_FIBER_SIZE:
        raise ValueError(f"Require 1..{MAX_FIBER_SIZE} contiguous fiber weights")
    if any(type(weight) is not int or weight <= 0 or weight.bit_length() > MAX_WEIGHT_BITS
           for weight in weights):
        raise ValueError(f"Weights must be positive integers of at most {MAX_WEIGHT_BITS} bits")
    if type(observed_index) is not int or not 0 <= observed_index < len(weights):
        raise ValueError("Observed index must be an integer on the fiber")
    lower, upper = _positive_interval((lower, upper))
    # At t=a/b, multiplying a degree-d polynomial by b**d gives
    # sum_j h_j*a**j*b**(d-j). This bound applies before constructing powers,
    # and leaves room for the 256-bit gamma adjustment under Python's default
    # integer-to-decimal output limit. It is not a complete runtime guarantee.
    max_endpoint_bits = max(max(value.numerator.bit_length(), value.denominator.bit_length())
                            for value in (lower, upper))
    integer_bits = (max(weight.bit_length() for weight in weights)
                    + (len(weights) - 1) * max_endpoint_bits
                    + (len(weights) - 1).bit_length())
    if integer_bits > MAX_POLYNOMIAL_INTEGER_BITS:
        raise ValueError(f"Polynomial integer bound {integer_bits} exceeds {MAX_POLYNOMIAL_INTEGER_BITS} bits; result uncomputed")
    threshold = weights[observed_index]
    event = [j for j, weight in enumerate(weights) if weight <= threshold]
    complement = [j for j, weight in enumerate(weights) if weight > threshold]
    if complement and complement != list(range(complement[0], complement[-1] + 1)):
        raise ValueError("Disconnected strict complement: endpoint certification refused")
    event_set = set(event)
    numerator = [weight if j in event_set else 0 for j, weight in enumerate(weights)]
    endpoint_p = [_polynomial(numerator, point) / _polynomial(weights, point)
                  for point in (lower, upper)]
    robust_p = max(endpoint_p)
    reference_p = Fraction(sum(numerator), sum(weights))
    return {
        "reference_p_exact": str(reference_p),
        "robust_p_exact": str(robust_p),
        "differential_tilt_interval": [str(lower), str(upper)],
        "endpoint_p_exact": [str(value) for value in endpoint_p],
        "maximizing_endpoints": [name for name, value in zip(("lower", "upper"), endpoint_p)
                                 if value == robust_p],
        "reference_event_indices": event,
        "strict_complement_interval": ([complement[0], complement[-1]] if complement else None),
        "certificate": "positive_contiguous_support_and_contiguous_strict_complement",
        "supremum_method": "exact_endpoint_maximum_for_fixed_reference_statistic",
        "reference_ordering": "inclusive_h_j_at_t_equals_one_frozen_across_all_t",
        "polynomial_integer_bit_bound": integer_bits,
    }


def _parse(document):
    keys = {"observation_contract", "sampling_contract", "recovery_bound_contract",
            "differential_tilt_interval", "bound_noncoverage_probability", "alpha", "contexts"}
    if not isinstance(document, dict) or set(document) != keys:
        raise ValueError(f"Input must have exactly these keys: {sorted(keys)}")
    if document["observation_contract"] != "shared_biological_curvature_with_differential_recovery":
        raise ValueError("Requires declared biological curvature and positive differential recovery model")
    if document["sampling_contract"] != "independent_baseline_selected_multinomials":
        raise ValueError("Requires the joint product multinomial law across all arms and contexts")
    if document["recovery_bound_contract"] != "externally_justified_coverage_interval":
        raise ValueError("Requires externally justified interval coverage, not estimated point recovery")
    lower, upper = _positive_interval(document["differential_tilt_interval"])
    gamma = _rational(document["bound_noncoverage_probability"], "bound noncoverage probability")
    if not 0 <= gamma < 1:
        raise ValueError("Bound noncoverage probability must be fixed in [0,1)")
    alpha = _rational(document["alpha"], "alpha")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    rows = document["contexts"]
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("This endpoint certificate requires exactly two contexts")
    contexts, seen = [], set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "baseline", "selected"}:
            raise ValueError("Each context requires exactly id, baseline, selected")
        name = row["id"]
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("Context IDs must be unique nonempty strings")
        seen.add(name)
        arms = []
        for arm in ("baseline", "selected"):
            counts = row[arm]
            if (not isinstance(counts, list) or len(counts) != 3
                    or any(type(x) is not int or x < 0 for x in counts)):
                raise ValueError(f"{arm}: requires three nonnegative integers in W,A,M order")
            if sum(counts) > MAX_CONTEXT_N:
                raise ValueError(f"Per-arm total exceeds {MAX_CONTEXT_N}")
            arms.append(tuple(counts))
        contexts.append(_PairedContext(name, *arms))
    if sum(c.n + sum(c.baseline) for c in contexts) > MAX_TOTAL_N:
        raise ValueError(f"Total observations exceed {MAX_TOTAL_N}")
    return tuple(contexts), alpha, lower, upper, gamma


def recovery_sensitivity_test(document, *, include_fiber=False):
    """Bounded exact test conditional on the specified recovery interval.

The imported baseline helper supplies combinatorial support and weights only.
Its shared observed-offset assertion is not invoked or asserted for this model.
"""
    contexts, alpha, lower, upper, gamma = _parse(document)
    fiber, candidates = _fiber_weights(contexts)
    allocations = sorted(fiber, key=lambda a: a[1])
    minimum_a2 = allocations[0][1]
    if [a[1] for a in allocations] != list(range(minimum_a2, allocations[-1][1] + 1, 2)):
        raise ValueError("Noncontiguous selected-A support: certificate refused")
    raw_weights = [fiber[a] for a in allocations]
    if any(weight.denominator != 1 for weight in raw_weights):
        raise ValueError("Expected integer combinatorial reference weights")
    weights = [weight.numerator for weight in raw_weights]
    if any(weights[j] ** 2 < weights[j - 1] * weights[j + 1]
           for j in range(1, len(weights) - 1)):
        raise ValueError("Reference weights failed their log-concavity certificate")
    observed = tuple(c.counts[1] for c in contexts)
    observed_index = allocations.index(observed)
    result = certified_reference_supremum(weights, observed_index, lower, upper)
    adjusted_p = min(Fraction(1), Fraction(result["robust_p_exact"]) + gamma)
    result.update({
        "scope": "two-context shared biological curvature conditional on declared recovery bounds; no mechanism claim",
        "observation_contract": document["observation_contract"],
        "sampling_contract": document["sampling_contract"],
        "recovery_bound_contract": document["recovery_bound_contract"],
        "bound_validity_established_by_counts": False,
        "bound_noncoverage_probability_exact": str(gamma),
        "adjusted_p_exact": str(adjusted_p),
        "guarantee_scope": ("conditional_on_fiber_given_deterministically_covering_interval"
                            if gamma == 0 else "unconditional_given_valid_marginal_interval_coverage"),
        "context_order": [c.name for c in contexts],
        "conditioned_N": [c.n for c in contexts],
        "conditioned_baseline_M": [sum(c.baseline) for c in contexts],
        "conditioned_D": [c.d for c in contexts],
        "conditioned_pooled_routes": [list(c.pooled) for c in contexts],
        "conditioned_total_A": sum(observed),
        "fiber_size": len(weights),
        "cartesian_candidates": candidates,
        "minimum_second_context_A": minimum_a2,
        "observed_index": observed_index,
        "log_concavity_verified": True,
        "alpha_exact": str(alpha),
        "reject": adjusted_p <= alpha,
        "information_status": ("uninformative_singleton_fiber" if len(weights) == 1
                               else "non_singleton_fiber"),
    })
    if include_fiber:
        result["fiber"] = [{"j": j, "selected_A": list(a), "reference_weight_exact": str(weight)}
                           for j, (a, weight) in enumerate(zip(allocations, weights))]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--include-fiber", action="store_true")
    args = parser.parse_args()
    result = recovery_sensitivity_test(load_input(args.input), include_fiber=args.include_fiber)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
