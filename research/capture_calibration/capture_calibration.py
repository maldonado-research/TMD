"""Exact finite synthetic capture calibration; no empirical fitting.

Latent terminal-unit marks are binomially captured. The inverse concerns
population positive compound-Poisson jump intensities, not a finite histogram.
"""
from fractions import Fraction
from itertools import product
from math import comb

MAX_MARK = 8
MAX_INTENSITY = 20
INPUT_BITS = 32


def exact(value, name):
    if type(value) not in (int, Fraction):
        raise TypeError(name + " must be int or Fraction, excluding bool")
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > INPUT_BITS:
        raise ValueError(name + " exceeds the external rational cap")
    return value


def capture(value):
    value = exact(value, "capture")
    if not 0 < value <= 1:
        raise ValueError("capture must be in (0,1]")
    return value


def support_bound(value):
    if type(value) is not int or not 1 <= value <= MAX_MARK:
        raise ValueError("support bound must be integer 1 through 8")
    return value


def intensity(value, name="intensity"):
    value = exact(value, name)
    if not 0 <= value <= MAX_INTENSITY:
        raise ValueError(name + " must be in [0,20]")
    return value


def terminal_law(law):
    if type(law) is not dict or not law or len(law) > MAX_MARK + 1:
        raise ValueError("terminal law must be a nonempty finite dictionary")
    if any(type(j) is not int or not 0 <= j <= MAX_MARK for j in law):
        raise ValueError("terminal support must be integer 0 through 8")
    law = {j: exact(weight, "terminal weight") for j, weight in law.items()}
    if any(weight < 0 for weight in law.values()) or sum(law.values()) != 1:
        raise ValueError("terminal weights must be nonnegative and normalized")
    return law


def positive_vector(nu):
    if type(nu) is not dict or not nu or len(nu) > MAX_MARK:
        raise ValueError("positive jump vector must be a complete finite dictionary")
    if any(type(j) is not int or not 1 <= j <= MAX_MARK for j in nu):
        raise ValueError("jump keys must be integer 1 through 8")
    bound = max(nu)
    if set(nu) != set(range(1, bound + 1)):
        raise ValueError("positive jump vector must explicitly include every key 1..B")
    nu = {j: intensity(nu[j], "jump intensity") for j in range(1, bound + 1)}
    if sum(nu.values()) > MAX_INTENSITY:
        raise ValueError("total observed jump intensity exceeds 20")
    return nu


def _forward_weights(weights, c, bound):
    return {ell: sum((weight * comb(j, ell) * c ** ell * (1-c) ** (j-ell)
                     for j, weight in weights.items() if j >= ell), Fraction())
            for ell in range(1, bound + 1)}


def forward_jump_intensities(law, m, c):
    """Return positive population jump intensities, allowing invisible J=0."""
    law, m, c = terminal_law(law), intensity(m), capture(c)
    bound = max(1, max(law))
    weights = {j: m * weight for j, weight in law.items()}
    nu = _forward_weights(weights, c, bound)
    return {"positive_jump_intensities": nu,
            "negative_log_zero_probability": sum(nu.values()),
            "mean_detected_count": sum(ell * weight for ell, weight in nu.items()),
            "positive_terminal_intensity": m * (1-law.get(0, 0))}


def invert_positive_jump_intensities(nu, c):
    """Invert known capture for a conditional strictly-positive mark family.

    Refuse population vectors outside this finite family. Negative empirical
    inverses would need a statistical model; this routine performs no such test.
    """
    nu, c = positive_vector(nu), capture(c)
    weights = {}
    for j in range(max(nu), 0, -1):
        weights[j] = nu[j] / c ** j - sum(
            (comb(k, j) * (1-c) ** (k-j) * weights[k]
             for k in weights if k > j), Fraction())
        if weights[j] < 0:
            raise ValueError("vector has no nonnegative inverse in the declared family")
    weights = {j: weights[j] for j in sorted(weights)}
    m = sum(weights.values())
    if m > MAX_INTENSITY:
        raise ValueError("recovered positive terminal intensity exceeds 20")
    if _forward_weights(weights, c, max(nu)) != nu:
        raise ArithmeticError("exact inverse failed the forward identity")
    return {"positive_terminal_weights": weights,
            "positive_terminal_intensity": m,
            "conditional_positive_mark_law":
                {j: weight/m for j, weight in weights.items()} if m else None,
            "strictly_positive_marks_assumed": True,
            "zero_mark_intensity_identified": False}


def intensity_bounds(b, c, bound):
    """Sharp deterministic m bounds from a population void exponent alone.

    Under 1<=J<=B: b/[1-(1-c)^B] <= m <= b/c. This function leaves
    algebraic output untruncated even if an endpoint exceeds MAX_INTENSITY.
    """
    b, c, bound = intensity(b, "void exponent"), capture(c), support_bound(bound)
    return {"lower": b/(1-(1-c)**bound), "upper": b/c}


def rectangle_bounds(b_lower, b_upper, c_lower, c_upper, bound):
    """Propagate externally justified deterministic bounds; no coverage claim."""
    bl, bu = intensity(b_lower, "lower void exponent"), intensity(b_upper, "upper void exponent")
    cl, cu, bound = capture(c_lower), capture(c_upper), support_bound(bound)
    if bl > bu or cl > cu:
        raise ValueError("rectangle endpoints are reversed")
    return {"lower": bl/(1-(1-cu)**bound), "upper": bu/cl}


def _enumerate_capture(law, m, c):
    """Separate direct Bernoulli assignment enumeration for producer checks."""
    nu = {ell: Fraction() for ell in range(1, max(1, max(law)) + 1)}
    for j, weight in law.items():
        for marks in product((0, 1), repeat=j):
            probability = Fraction(1)
            for marked in marks:
                probability *= c if marked else 1-c
            ell = sum(marks)
            if ell:
                nu[ell] += m * weight * probability
    return nu


def _json_exact(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_exact(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_exact(item) for item in value]
    return value


def benchmarks():
    if not __debug__:
        raise RuntimeError("Verification requires ordinary Python without -O/-OO")
    checks = {"forward_vs_direct_assignment_entries": 0,
              "positive_support_inverse_weight_entries": 0,
              "positive_support_inverse_intensities": 0,
              "PGF_exponent_identities": 0,
              "sharp_void_endpoint_checks": 0,
              "deterministic_rectangle_checks": 0,
              "full_law_witness_checks": 0,
              "invalid_input_guards": 0}

    def check(condition, category):
        if not condition:
            raise AssertionError("Benchmark failed: " + category)
        checks[category] += 1

    positive_laws = [{1: Fraction(1)}, {2: Fraction(1)}, {8: Fraction(1)},
                     {1: Fraction(3, 4), 3: Fraction(1, 4)},
                     {1: Fraction(1, 5), 2: Fraction(1, 5), 8: Fraction(3, 5)}]
    laws = positive_laws + [{0: Fraction(1)}, {0: Fraction(1, 2), 2: Fraction(1, 2)}]
    captures = (Fraction(1), Fraction(1, 2), Fraction(1, 4), Fraction(1, 3), Fraction(3, 4))
    for law in laws:
        for c in captures:
            for m in (Fraction(0), Fraction(1, 3), Fraction(2)):
                model = forward_jump_intensities(law, m, c)
                nu = model["positive_jump_intensities"]
                direct = _enumerate_capture(law, m, c)
                for ell in nu:
                    check(nu[ell] == direct[ell], "forward_vs_direct_assignment_entries")
                for z in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(1)):
                    observed = sum((weight*(z**ell-1) for ell, weight in nu.items()), Fraction())
                    latent = m*(sum((weight*(1-c+c*z)**j for j, weight in law.items()), Fraction())-1)
                    check(observed == latent, "PGF_exponent_identities")
                if law in positive_laws:
                    inverse = invert_positive_jump_intensities(nu, c)
                    check(inverse["positive_terminal_intensity"] == m,
                          "positive_support_inverse_intensities")
                    for j, weight in inverse["positive_terminal_weights"].items():
                        check(weight == m*law.get(j, 0), "positive_support_inverse_weight_entries")
                    if m == 0:
                        check(inverse["conditional_positive_mark_law"] is None,
                              "positive_support_inverse_intensities")

    for bound in range(1, MAX_MARK + 1):
        for c in captures:
            for b in (Fraction(0), Fraction(1, 3), Fraction(1)):
                interval = intensity_bounds(b, c, bound)
                lower_law = forward_jump_intensities({bound: 1}, interval["lower"], c)
                upper_law = forward_jump_intensities({1: 1}, interval["upper"], c)
                check(lower_law["negative_log_zero_probability"] == b, "sharp_void_endpoint_checks")
                check(upper_law["negative_log_zero_probability"] == b, "sharp_void_endpoint_checks")
                check(interval["lower"] <= interval["upper"], "sharp_void_endpoint_checks")

    rectangle = rectangle_bounds(Fraction(1, 2), Fraction(3, 4), Fraction(1, 4), Fraction(1, 2), 2)
    check(rectangle == {"lower": Fraction(2, 3), "upper": Fraction(3)},
          "deterministic_rectangle_checks")
    check(forward_jump_intensities({2: 1}, rectangle["lower"], Fraction(1, 2))
          ["negative_log_zero_probability"] == Fraction(1, 2), "deterministic_rectangle_checks")
    check(forward_jump_intensities({1: 1}, rectangle["upper"], Fraction(1, 4))
          ["negative_log_zero_probability"] == Fraction(3, 4), "deterministic_rectangle_checks")

    singleton_a = forward_jump_intensities({1: 1}, 1, Fraction(1, 2))
    singleton_b = forward_jump_intensities({1: 1}, 2, Fraction(1, 4))
    check(singleton_a["positive_jump_intensities"] == singleton_b["positive_jump_intensities"],
          "full_law_witness_checks")
    check(singleton_a["positive_jump_intensities"] == {1: Fraction(1, 2)}, "full_law_witness_checks")
    zero_a = forward_jump_intensities({2: 1}, 1, Fraction(1, 3))
    zero_b = forward_jump_intensities({0: Fraction(1, 2), 2: Fraction(1, 2)}, 2, Fraction(1, 3))
    check(zero_a["positive_jump_intensities"] == zero_b["positive_jump_intensities"],
          "full_law_witness_checks")
    inverse = invert_positive_jump_intensities(zero_a["positive_jump_intensities"], Fraction(1, 3))
    check(inverse["positive_terminal_intensity"] == 1, "full_law_witness_checks")
    b_not_mean = forward_jump_intensities({2: 1}, 1, Fraction(1, 2))
    check(b_not_mean["negative_log_zero_probability"] == Fraction(3, 4), "full_law_witness_checks")
    check(b_not_mean["mean_detected_count"] == 1, "full_law_witness_checks")
    conditional_case = forward_jump_intensities({1: Fraction(3, 4), 3: Fraction(1, 4)}, 2, Fraction(1, 3))
    conditional_inverse = invert_positive_jump_intensities(conditional_case["positive_jump_intensities"], Fraction(1, 3))

    invalid = [lambda: forward_jump_intensities({}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({True: 1}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({9: 1}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: Fraction(1, 2)}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: 2, 2: -1}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: 1.0}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: True}, 1, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: 1}, True, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: 1}, -1, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: 1}, 21, Fraction(1, 2)),
               lambda: forward_jump_intensities({1: 1}, 1, 0),
               lambda: forward_jump_intensities({1: 1}, 1, 2),
               lambda: forward_jump_intensities({1: 1}, 1, 0.5),
               lambda: forward_jump_intensities({1: 1}, 1, Fraction(1, 2**40)),
               lambda: invert_positive_jump_intensities({}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({0: 1}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({True: 1}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({2: 1}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({1: 1, 2: 1}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({1: 20}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({1: -1}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({1: 21}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({1: 20, 2: 1}, Fraction(1, 2)),
               lambda: invert_positive_jump_intensities({1: Fraction(1, 2**40)}, Fraction(1, 2)),
               lambda: intensity_bounds(1, Fraction(1, 2), 0),
               lambda: intensity_bounds(1, Fraction(1, 2), 9),
               lambda: intensity_bounds(1, Fraction(1, 2), True),
               lambda: intensity_bounds(-1, Fraction(1, 2), 2),
               lambda: rectangle_bounds(1, 0, Fraction(1, 4), Fraction(1, 2), 2),
               lambda: rectangle_bounds(0, 1, Fraction(1, 2), Fraction(1, 4), 2)]
    for operation in invalid:
        try:
            operation()
        except (TypeError, ValueError):
            checks["invalid_input_guards"] += 1
        else:
            raise AssertionError("Invalid benchmark input admitted")

    return _json_exact({"schema_version": 1, "status": "passed",
            "scope": "finite exact synthetic population-intensity calibration",
            "checks": checks,
            "known_capture_example": {"m": Fraction(2), "capture": Fraction(1, 3),
                "law": {1: Fraction(3, 4), 3: Fraction(1, 4)},
                "forward": conditional_case, "inverse": conditional_inverse},
            "unknown_capture_full_law_witness": {"first_m": Fraction(1), "first_c": Fraction(1, 2),
                "second_m": Fraction(2), "second_c": Fraction(1, 4), "law": {1: Fraction(1)},
                "common_positive_jump_intensities": singleton_a["positive_jump_intensities"],
                "all_observable_PGF_terms_identical": True},
            "zero_terminal_mark_full_law_witness": {"capture": Fraction(1, 3),
                "first_m": Fraction(1), "first_law": {2: Fraction(1)},
                "second_m": Fraction(2), "second_law": {0: Fraction(1, 2), 2: Fraction(1, 2)},
                "common_positive_jump_intensities": zero_a["positive_jump_intensities"],
                "identified_positive_terminal_intensity": Fraction(1),
                "all_observable_PGF_terms_identical": True},
            "void_exponent_is_not_mean": b_not_mean,
            "deterministic_rectangle_example": {"b_range": [Fraction(1, 2), Fraction(3, 4)],
                "c_range": [Fraction(1, 4), Fraction(1, 2)], "B": 2, "m_bounds": rectangle},
            "biological_data_fitted": False, "empirical_histogram_inverted": False,
            "new_rate_or_confidence_interval": False, "new_theorem_or_priority_claim": False,
            "actual_study_fields_resolved": 0, "source_acquisitions": 0})
