"""Exact synthetic endpoint-mixture ambiguity; no biological fit or count law."""
from fractions import Fraction

INPUT_BITS = 32


def exact(value, name):
    if type(value) not in (int, Fraction):
        raise TypeError(name + " must be int or Fraction, excluding bool")
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > INPUT_BITS:
        raise ValueError(name + " exceeds the external rational cap")
    return value


def triple(values, name):
    if type(values) not in (tuple, list) or len(values) != 3:
        raise ValueError(name + " must contain exactly three positive values")
    result = tuple(exact(value, name) for value in values)
    if any(value <= 0 for value in result):
        raise ValueError(name + " values must be positive")
    return result


def endpoint_mixture(supply, growth, recovery):
    """Normalize expected mass q_i*g_i*r_i, with g relative terminal yield.

    Fractional yields allow retention/loss; this is not a lineage likelihood
    or an assertion that a fractional realized cell count exists.
    """
    q, g, r = triple(supply, "supply"), triple(growth, "growth"), triple(recovery, "recovery")
    if sum(q) != 1:
        raise ValueError("supply must be normalized")
    if any(value > 16 for value in g):
        raise ValueError("growth multiplier exceeds16")
    if any(value > 1 for value in r):
        raise ValueError("recovery exceeds1")
    masses = tuple(qi*gi*ri for qi, gi, ri in zip(q, g, r))
    total = sum(masses)
    return tuple(mass/total for mass in masses)


def supply_adjusted_curvature(probabilities, supply):
    """Exact J = p2^2*q1*q3/(p1*p3*q2^2), on positive triad shares."""
    p, q = triple(probabilities, "probabilities"), triple(supply, "supply")
    if sum(p) != 1 or sum(q) != 1:
        raise ValueError("probabilities and supply must be normalized")
    return p[1]**2*q[0]*q[2]/(p[0]*p[2]*q[1]**2)


def _normalize(values):
    total = sum(values)
    return tuple(value/total for value in values)


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
    counts = {"endpoint_mixture_normalizations": 0, "growth_vs_recovery_only_equalities": 0,
              "common_terminal_yield_scale_invariance": 0,
              "common_curvature_identities": 0, "independently_corrected_supply_identities": 0,
              "context_change_checks": 0, "explicit_falsifier_checks": 0,
              "invalid_input_guards": 0}

    def check(condition, category):
        if not condition:
            raise AssertionError("Synthetic benchmark failed: " + category)
        counts[category] += 1

    supplies = [(Fraction(1, 3),)*3, (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)),
                (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4))]
    contexts = (Fraction(1, 2), Fraction(1), Fraction(2), Fraction(4))
    multipliers = (Fraction(1), Fraction(2), Fraction(3))
    first_examples = []
    for q in supplies:
        for u in multipliers:
            previous = None
            for t in contexts:
                a = (t, u, 1/t)
                g_only = endpoint_mixture(q, a, (1, 1, 1))
                r = tuple(value/max(a) for value in a)
                r_only = endpoint_mixture(q, (1, 1, 1), r)
                direct = _normalize(tuple(qi*ai for qi, ai in zip(q, a)))
                check(sum(g_only) == 1 and min(g_only) > 0, "endpoint_mixture_normalizations")
                check(g_only == r_only == direct, "growth_vs_recovery_only_equalities")
                scaled = tuple(value/min(a) for value in a)
                check(min(scaled) >= 1 and endpoint_mixture(q, scaled, (1, 1, 1)) == g_only,
                      "common_terminal_yield_scale_invariance")
                check(supply_adjusted_curvature(g_only, q) == u**2,
                      "common_curvature_identities")
                corrected = _normalize(tuple(pi/ai for pi, ai in zip(g_only, a)))
                check(corrected == q and supply_adjusted_curvature(corrected, q) == 1,
                      "independently_corrected_supply_identities")
                if previous is not None:
                    check(g_only != previous, "context_change_checks")
                previous = g_only
                if q == supplies[0] and u == 2:
                    first_examples.append({"context_t": t, "fixed_supply": q,
                        "growth_only_multipliers": a, "recovery_only_probabilities": r,
                        "common_expected_endpoint_mixture": g_only, "J": u**2})

    q = supplies[0]
    a = endpoint_mixture(q, (1, 2, 1), (1, 1, 1))
    incompatible = endpoint_mixture(q, (1, 3, 1), (1, 1, 1))
    check(supply_adjusted_curvature(a, q) == 4, "explicit_falsifier_checks")
    check(supply_adjusted_curvature(incompatible, q) == 9, "explicit_falsifier_checks")
    check(supply_adjusted_curvature(a, q) != supply_adjusted_curvature(incompatible, q),
          "explicit_falsifier_checks")
    invalid = [lambda: endpoint_mixture((1, 1, 1), (1, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture((Fraction(1, 2), Fraction(1, 2)), (1, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture((0, Fraction(1, 2), Fraction(1, 2)), (1, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture((True, 1, 1), (1, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture((0.25, 0.25, 0.5), (1, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture(q, (17, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture(q, (-1, 1, 1), (1, 1, 1)),
               lambda: endpoint_mixture(q, (1, 1, 1), (2, 1, 1)),
               lambda: endpoint_mixture(q, (1, 1, 1), (0, 1, 1)),
               lambda: endpoint_mixture(q, (Fraction(1, 2**40), 1, 1), (1, 1, 1)),
               lambda: supply_adjusted_curvature((1, 1, 1), q),
               lambda: supply_adjusted_curvature(q, (1, 1, 1))]
    for operation in invalid:
        try:
            operation()
        except (ValueError, TypeError):
            counts["invalid_input_guards"] += 1
        else:
            raise AssertionError("Invalid synthetic input admitted")

    return _json_exact({"schema_version": 1, "status": "passed",
        "scope": "exact identities of synthetic expected endpoint mixtures",
        "checks": counts, "fixed_supply_growth_or_recovery_mimic": first_examples,
        "unequal_curvature_example": {"first_expected_mixture": a,
            "second_expected_mixture": incompatible, "first_J": Fraction(4), "second_J": Fraction(9)},
        "expected_mixture_equality_is_not_full_count_law_or_first_arrival_equivalence": True,
        "cancer_observations_fitted": False, "cancer_route_catalog_selected": False,
        "mutation_generation_changed_in_mimic": False, "new_theorem_or_priority_claim": False,
        "clinical_prevention_or_treatment_result": False, "registered_study_or_error_budget_change": False,
        "existing_actual_study_fields_resolved": 0})
