"""R000018: exact conditional feasibility of expected-endpoint curvature.

Positive real parameters range independently over closed intervals whose
endpoints are exact rationals. This is not an empirical count likelihood,
confidence procedure, power calculation, or causal-mechanism certificate.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

INPUT_BITS = 32
MAX_CONTEXTS = 64
MAX_JSON_BYTES = 1_048_576
GROUPS = ("endpoint_masses", "supply_weights", "growth_yields",
          "recovery_probabilities")
EXPONENTS = {
    "endpoint_masses": (-1, 2, -1),
    "supply_weights": (1, -2, 1),
    "growth_yields": (1, -2, 1),
    "recovery_probabilities": (1, -2, 1),
}
REQUIRED_ASSUMPTIONS = {
    "population_expected_mass_model": True,
    "cartesian_parameter_bounds": True,
    "bounds_fixed_independently_of_selected_outcomes": True,
    "fixed_route_axis": True,
    "representation": "unnormalized_expected_masses_and_relative_supply_weights",
    "endpoint_count_law_claim": False,
    "coverage_or_power_claim": False,
}


def _runtime_guard():
    if not __debug__:
        raise RuntimeError("Certification requires ordinary Python without -O/-OO")


def exact(value, name):
    """Admit exact finite rationals; exclude bool, floats and unknown bounds."""
    if type(value) is str:
        if len(value) > 24 or re.fullmatch(
                r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value) is None:
            raise ValueError(name + " must be a short exact rational string")
        value = Fraction(value)
    elif type(value) in (int, Fraction):
        value = Fraction(value)
    else:
        raise TypeError(name + " must be int, Fraction or an exact rational string")
    if max(abs(value.numerator).bit_length(),
           value.denominator.bit_length()) > INPUT_BITS:
        raise ValueError(name + " exceeds the external rational bit cap")
    return value


def _keys(value, expected, name):
    if type(value) is not dict or set(value) != set(expected):
        raise ValueError(name + " has missing or unknown fields")


def _group_bounds(value, name):
    if type(value) not in (list, tuple) or len(value) != 3:
        raise ValueError(name + " requires three ordered R1/R2/R3 bounds")
    result = []
    for index, pair in enumerate(value):
        if type(pair) not in (list, tuple) or len(pair) != 2:
            raise ValueError(name + " requires closed lower/upper pairs")
        lower = exact(pair[0], name + ".lower")
        upper = exact(pair[1], name + ".upper")
        if lower <= 0 or upper <= 0 or lower > upper:
            raise ValueError(name + " bounds must be ordered and strictly positive")
        if name == "recovery_probabilities" and upper > 1:
            raise ValueError("recovery probabilities cannot exceed one")
        result.append((lower, upper))
    return tuple(result)


def _ratio(point):
    product = Fraction(1)
    for group in GROUPS:
        for value, exponent in zip(point[group], EXPONENTS[group]):
            product *= value ** exponent
    return product


def _context_certificate(context):
    _keys(context, ("name",) + GROUPS, "context")
    name = context["name"]
    if type(name) is not str or not name.strip() or len(name) > 128:
        raise ValueError("context name must be a nonempty short string")
    bounds = {group: _group_bounds(context[group], group) for group in GROUPS}
    minimum, maximum = {}, {}
    for group in GROUPS:
        minimum[group] = tuple(pair[0] if exponent > 0 else pair[1]
                               for pair, exponent in
                               zip(bounds[group], EXPONENTS[group]))
        maximum[group] = tuple(pair[1] if exponent > 0 else pair[0]
                               for pair, exponent in
                               zip(bounds[group], EXPONENTS[group]))
    lower, upper = _ratio(minimum), _ratio(maximum)
    if lower <= 0 or lower > upper:
        raise RuntimeError("Internal positive-ratio invariant failed")
    # The full conventional endpoint model fixes both theta=0 and eta=0.
    # Its necessary K=1 condition alone leaves eta free and is insufficient.
    scale_ranges = []
    for route in range(3):
        scale_lower = bounds["endpoint_masses"][route][0]
        scale_upper = bounds["endpoint_masses"][route][1]
        for group in GROUPS[1:]:
            scale_lower /= bounds[group][route][1]
            scale_upper /= bounds[group][route][0]
        scale_ranges.append((scale_lower, scale_upper))
    scale_lower = max(lo for lo, _ in scale_ranges)
    scale_upper = min(hi for _, hi in scale_ranges)
    return {
        "name": name,
        "K_interval": {"lower": str(lower), "upper": str(upper),
                       "closed": True, "sharp_under_admitted_cartesian_bounds": True},
        "minimum_corner": {key: [str(x) for x in minimum[key]] for key in GROUPS},
        "maximum_corner": {key: [str(x) for x in maximum[key]] for key in GROUPS},
        "corner_witnesses_are_rational": True,
        "interior_feasibility_is_over_positive_real_parameters": True,
        "conventional_qgr_model": {
            "route_scale_intervals": [{"lower": str(lo), "upper": str(hi)}
                                     for lo, hi in scale_ranges],
            "scale_intersection_lower": str(scale_lower),
            "scale_intersection_upper": str(scale_upper),
            "status": ("conditionally_feasible" if scale_lower <= scale_upper
                       else "conditionally_incompatible"),
            "theta_and_eta_fixed_zero": True,
            "context_wide_exposure_scale_is_free": True,
        },
    }, lower, upper


def _fixed_target_result(target, intervals):
    failed = [name for name, lower, upper in intervals
              if not (lower <= target <= upper)]
    return {
        "target_K": str(target),
        "status": ("conditionally_incompatible" if failed
                   else "conditionally_feasible"),
        "incompatible_contexts": failed,
        "eta_is_free_not_a_complete_probability_forecast": True,
        "is_statistical_rejection": False,
    }


def certify(request):
    """Return a deterministic exact certificate, conditional on admission flags.

    Admission declarations are not independently authenticated by this engine.
    Cartesian bounds describe feasible parameter sets, not random independence.
    """
    _runtime_guard()
    _keys(request, ("schema_version", "provenance", "assumptions", "contexts",
                    "forecast_K"), "request")
    if type(request["schema_version"]) is not int or request["schema_version"] != 1:
        raise ValueError("schema_version must be integer one")
    if request["provenance"] not in ("synthetic", "supplied_population_bounds"):
        raise ValueError("provenance must identify synthetic or population bounds")
    assumptions = request["assumptions"]
    _keys(assumptions, REQUIRED_ASSUMPTIONS, "assumptions")
    for key, expected in REQUIRED_ASSUMPTIONS.items():
        actual = assumptions[key]
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError("Unadmitted assumption: " + key)
    contexts = request["contexts"]
    if type(contexts) not in (list, tuple) or not 1 <= len(contexts) <= MAX_CONTEXTS:
        raise ValueError("one to 64 prespecified contexts are required")
    names, output, intervals = set(), [], []
    for context in contexts:
        certificate, lower, upper = _context_certificate(context)
        name = certificate["name"]
        if name in names:
            raise ValueError("context names must be unique")
        names.add(name)
        output.append(certificate)
        intervals.append((name, lower, upper))
    common_lower = max(lower for _, lower, _ in intervals)
    common_upper = min(upper for _, _, upper in intervals)
    common_feasible = common_lower <= common_upper
    forecast = request["forecast_K"]
    if forecast is not None:
        forecast = exact(forecast, "forecast_K")
        if forecast <= 0:
            raise ValueError("forecast_K must be strictly positive")
        forecast_result = _fixed_target_result(forecast, intervals)
    else:
        forecast_result = {"status": "not_supplied", "is_statistical_rejection": False}
    return {
        "schema_version": 1,
        "record_id": "R000018",
        "provenance": request["provenance"],
        "scope": "conditional exact feasibility for positive expected endpoint masses",
        "K_definition": "m2^2*q1*q3*g1*g3*r1*r3/(m1*m3*q2^2*g2^2*r2^2)",
        "K_equals": "exp(2*theta) under admitted residual endpoint model",
        "contexts": output,
        "free_common_curvature": {
            "status": ("conditionally_feasible" if common_feasible
                       else "conditionally_incompatible"),
            "intersection_lower": str(common_lower),
            "intersection_upper": str(common_upper),
            "intersection_empty": not common_feasible,
            "touching_is_feasible": True,
            "contact_only": common_lower == common_upper,
            "comparison_cross_products": {
                "lower_numerator_times_upper_denominator":
                    str(common_lower.numerator*common_upper.denominator),
                "upper_numerator_times_lower_denominator":
                    str(common_upper.numerator*common_lower.denominator),
            },
            "limiting_lower_contexts": [n for n, lo, _ in intervals
                                        if lo == common_lower],
            "limiting_upper_contexts": [n for n, _, hi in intervals
                                        if hi == common_upper],
            "between_context_sharing_evaluable": len(intervals) > 1,
            "is_statistical_rejection": False,
            "compatibility_is_not_predictive_or_causal_support": True,
        },
        "fixed_curvature_forecast": forecast_result,
        "conventional_qgr_necessary_curvature_condition":
            _fixed_target_result(Fraction(1), intervals),
        "conventional_supply_growth_recovery_model": {
            "status": ("conditionally_feasible" if all(
                item["conventional_qgr_model"]["status"] == "conditionally_feasible"
                for item in output) else "conditionally_incompatible"),
            "incompatible_contexts": [
                item["name"] for item in output if
                item["conventional_qgr_model"]["status"] == "conditionally_incompatible"],
            "theta_and_eta_fixed_zero": True,
            "is_statistical_rejection": False,
        },
        "rational_interval_endpoints_do_not_imply_rational_interior_witness": True,
        "empirical_histogram_confidence_or_power_claim": False,
        "culture_founder_lineage_count_law_admitted": False,
        "simplex_constrained_coordinate_share_bounds_admitted": False,
        "source_assumptions_authenticated_by_engine": False,
    }


def _unique_json(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field: " + key)
        result[key] = value
    return result


def load_request(path):
    source = Path(path)
    if source.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("Request exceeds the JSON size cap")
    raw = source.read_bytes()
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("Request exceeds the JSON size cap")
    def reject_constant(value):
        raise ValueError("Nonfinite JSON constant is unsupported: " + value)
    request = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json,
                         parse_constant=reject_constant)
    return request, hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request_json")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        request, digest = load_request(args.request_json)
        certificate = certify(request)
        certificate["input_sha256"] = digest
        encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(encoded, encoding="utf-8")
        else:
            print(encoded, end="")
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        print(json.dumps({"status": "declined", "reason": str(error)}),
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
