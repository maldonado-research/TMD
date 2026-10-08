"""Finite fixed-event/design capture identities; no biological inference."""
from fractions import Fraction
import json

MAX_DESCENDANTS = 8
MAX_EVENTS = 8
INPUT_BITS = 32


def exact(value, name):
    if type(value) not in (int, Fraction):
        raise TypeError(name + " must be int or Fraction, excluding bool")
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > INPUT_BITS:
        raise ValueError(name + " exceeds the external rational cap")
    return value


def descendant_count(n):
    if type(n) is not int or not 0 <= n <= MAX_DESCENDANTS:
        raise ValueError("n must be integer0..8, excluding bool")
    return n


def marginal_probabilities(marginals):
    if type(marginals) not in (tuple, list) or len(marginals) > MAX_DESCENDANTS:
        raise ValueError("marginals must be a tuple/list of length0..8")
    values = tuple(exact(value, "marginal probability") for value in marginals)
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("marginal probabilities outside[0,1]")
    return values


def capture_law(n, law):
    n = descendant_count(n)
    if type(law) is not dict or not law or len(law) > 1 << n:
        raise ValueError("capture law must be a nonempty finite dictionary")
    if any(type(mask) is not int or not 0 <= mask < 1 << n for mask in law):
        raise ValueError("capture masks must be integer0..2^n-1, excluding bool")
    law = {mask: exact(weight, "mask probability") for mask, weight in sorted(law.items())}
    if any(weight < 0 for weight in law.values()) or sum(law.values()) != 1:
        raise ValueError("capture-mask probabilities must be nonnegative and normalized")
    return law


def event_catalogue(n, events, ancestry_known):
    n = descendant_count(n)
    if ancestry_known is not True:
        raise ValueError("known ancestry/carrier mapping must be supplied; it is not authenticated here")
    if type(events) is not dict or len(events) > MAX_EVENTS:
        raise ValueError("event catalogue must be a dictionary of at most8events")
    if any(type(name) is not str or not name or len(name) > 32 for name in events):
        raise ValueError("event identifiers must be nonempty strings of at most32characters")
    out = {}
    for name, carriers in sorted(events.items()):
        if type(carriers) not in (tuple, list) or len(carriers) > n:
            raise ValueError("carriers must be an explicit tuple/list, including empty when known")
        if any(type(index) is not int or not 0 <= index < n for index in carriers):
            raise ValueError("carrier indices must be integer0..n-1, excluding bool")
        if len(set(carriers)) != len(carriers):
            raise ValueError("duplicate carriers are not allowed")
        out[name] = sum(1 << index for index in carriers)
    return out


def event_summary(n, law, events, ancestry_known=True):
    """Joint masks specify true all-target genotype observability, not isolation."""
    n, law = descendant_count(n), capture_law(n, law)
    masks = event_catalogue(n, events, ancestry_known)
    marginals = tuple(sum((weight for mask, weight in law.items() if mask & (1 << index)), Fraction())
                      for index in range(n))
    inclusion = {name: sum((weight for mask, weight in law.items() if mask & carriers), Fraction())
                 for name, carriers in masks.items()}
    joint = {(first, second): sum((weight for mask, weight in law.items()
                                   if mask & carriers1 and mask & carriers2), Fraction())
             for first, carriers1 in masks.items() for second, carriers2 in masks.items()}
    copies = sum((marginals[index] for carriers in masks.values() for index in range(n)
                  if carriers & (1 << index)), Fraction())
    return {"descendant_call_marginals": marginals, "event_inclusion": inclusion,
            "joint_event_inclusion": joint, "expected_observed_carrier_copy_count": copies,
            "expected_observed_distinct_event_count": sum(inclusion.values(), Fraction()),
            "ancestry_and_catalogue_supplied_not_authenticated": True}


def ht_summary(n, law, events, ancestry_known=True):
    """Classical Horvitz-Thompson fixed-catalogue expectation and variance."""
    summary = event_summary(n, law, events, ancestry_known)
    pi, pair = summary["event_inclusion"], summary["joint_event_inclusion"]
    if any(probability == 0 for probability in pi.values()):
        raise ValueError("full-catalogue HT total requires every event inclusion probability positive")
    variance = sum(((pair[first, second]-pi[first]*pi[second])/(pi[first]*pi[second])
                    for first in pi for second in pi), Fraction())
    if variance < 0:
        raise ArithmeticError("negative exact design variance")
    return {"fixed_catalogue_size": len(pi), "design_expectation": Fraction(len(pi)),
            "design_variance": variance, "event_inclusion": pi, "joint_event_inclusion": pair,
            "biological_catalogue_or_mutation_process_identified": False}


def ht_value(n, law, events, observed_mask, ancestry_known=True):
    n, law = descendant_count(n), capture_law(n, law)
    masks = event_catalogue(n, events, ancestry_known)
    if type(observed_mask) is not int or observed_mask not in law or law[observed_mask] <= 0:
        raise ValueError("observed mask must be a declared positive-probability mask, excluding bool")
    summary = ht_summary(n, law, events, ancestry_known)
    return sum((1/summary["event_inclusion"][name] for name, carriers in masks.items()
                if observed_mask & carriers), Fraction())


def frechet_union_bounds(marginals):
    marginals = marginal_probabilities(marginals)
    independent_empty_probability = Fraction(1)
    for probability in marginals:
        independent_empty_probability *= 1-probability
    return {"lower": max(marginals, default=Fraction()),
            "upper": min(Fraction(1), sum(marginals, Fraction())),
            "value_if_independent": 1-independent_empty_probability}


def independent_capture_law(marginals):
    marginals = marginal_probabilities(marginals)
    law = {}
    for mask in range(1 << len(marginals)):
        weight = Fraction(1)
        for index, probability in enumerate(marginals):
            weight *= probability if mask & (1 << index) else 1-probability
        if weight:
            law[mask] = weight
    return law


def _interval_law(marginals, upper):
    cuts = {Fraction(), Fraction(1)}
    intervals = []
    offset = Fraction()
    for probability in marginals:
        start = offset % 1 if upper else Fraction()
        end = start+probability
        intervals.append((start, end, probability))
        cuts.update((start, end % 1 if end > 1 else end))
        offset += probability
    cuts = sorted(cuts)
    law = {}
    for left, right in zip(cuts, cuts[1:]):
        midpoint = (left+right)/2
        mask = 0
        for index, (start, end, probability) in enumerate(intervals):
            if probability == 1 or (probability and
               ((start <= midpoint < end) if end <= 1 else (midpoint >= start or midpoint < end-1))):
                mask |= 1 << index
        law[mask] = law.get(mask, Fraction())+right-left
    return law


def extremal_union_laws(marginals):
    """Nested lower and circle-interval upper constructions attain sharp bounds."""
    marginals = marginal_probabilities(marginals)
    return {"lower_union_law": _interval_law(marginals, False),
            "upper_union_law": _interval_law(marginals, True)}


def _json_exact(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {(json.dumps(key, ensure_ascii=False, separators=(",", ":")) if isinstance(key, tuple) else str(key)): _json_exact(item)
                for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_exact(item) for item in value]
    return value


def benchmarks():
    if not __debug__:
        raise RuntimeError("Verification requires ordinary Python without -O/-OO")
    checks = {"constructed_law_normalizations": 0, "constructed_marginal_identities": 0,
              "sharp_union_endpoint_identities": 0, "independence_union_identities": 0,
              "event_complement_identities": 0, "pairwise_probability_bounds": 0,
              "HT_expectation_vs_complete_mask_enumeration": 0,
              "HT_variance_vs_complete_mask_enumeration": 0, "zero_inclusion_HT_refusals": 0,
              "explicit_counterexample_identities": 0, "invalid_input_guards": 0}

    def check(condition, category):
        if not condition:
            raise AssertionError("Synthetic event-capture benchmark failed: "+category)
        checks[category] += 1

    grids = [(), (Fraction(0),), (Fraction(1),), (Fraction(1, 2),),
             (Fraction(1, 2), Fraction(1, 2)), (Fraction(1, 4), Fraction(3, 4)),
             (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)), (Fraction(1, 2),)*4,
             (Fraction(0), Fraction(1, 10), Fraction(1), Fraction(9, 10)),
             (Fraction(1, 8), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(7, 8))]
    for marginals in grids:
        n = len(marginals)
        endpoints = extremal_union_laws(marginals)
        bounds = frechet_union_bounds(marginals)
        laws = dict(endpoints, independent=independent_capture_law(marginals))
        for frame, law in laws.items():
            check(sum(law.values()) == 1 and min(law.values()) >= 0, "constructed_law_normalizations")
            union = event_summary(n, law, {"union": tuple(range(n))})
            for actual, expected in zip(union["descendant_call_marginals"], marginals):
                check(actual == expected, "constructed_marginal_identities")
            if frame == "independent":
                check(union["event_inclusion"]["union"] == bounds["value_if_independent"],
                      "independence_union_identities")
            else:
                endpoint = "lower" if frame == "lower_union_law" else "upper"
                check(union["event_inclusion"]["union"] == bounds[endpoint], "sharp_union_endpoint_identities")
            events = {"whole": tuple(range(n)), "even": tuple(range(0, n, 2)),
                      "same_as_even": tuple(range(0, n, 2)), "last": (n-1,) if n else ()}
            summary = event_summary(n, law, events)
            for name, carriers in events.items():
                complement = sum((weight for mask, weight in law.items()
                                  if all(not mask & (1 << index) for index in carriers)), Fraction())
                check(summary["event_inclusion"][name]+complement == 1, "event_complement_identities")
            pi = summary["event_inclusion"]
            for (first, second), pair in summary["joint_event_inclusion"].items():
                check(max(Fraction(), pi[first]+pi[second]-1) <= pair <= min(pi[first], pi[second]),
                      "pairwise_probability_bounds")
            if any(probability == 0 for probability in pi.values()):
                try:
                    ht_summary(n, law, events)
                except ValueError:
                    checks["zero_inclusion_HT_refusals"] += 1
                else:
                    raise AssertionError("Zero-inclusion catalogue admitted for HT total")
            else:
                model = ht_summary(n, law, events)
                values = {mask: ht_value(n, law, events, mask) for mask in law if law[mask]}
                mean = sum((law[mask]*value for mask, value in values.items()), Fraction())
                variance = sum((law[mask]*(value-mean)**2 for mask, value in values.items()), Fraction())
                check(mean == model["design_expectation"] == len(events),
                      "HT_expectation_vs_complete_mask_enumeration")
                check(variance == model["design_variance"], "HT_variance_vs_complete_mask_enumeration")

    witnesses = {}
    laws = {"common": {0: Fraction(1, 2), 3: Fraction(1, 2)},
            "mutually_exclusive": {1: Fraction(1, 2), 2: Fraction(1, 2)},
            "independent": {mask: Fraction(1, 4) for mask in range(4)}}
    for frame, law in laws.items():
        union = event_summary(2, law, {"one_birth": (0, 1)})
        total = ht_summary(2, law, {"first": (0,), "second": (1,)})
        check(union["descendant_call_marginals"] == (Fraction(1, 2),)*2,
              "explicit_counterexample_identities")
        check(union["event_inclusion"]["one_birth"] ==
              {"common": Fraction(1, 2), "mutually_exclusive": Fraction(1), "independent": Fraction(3, 4)}[frame],
              "explicit_counterexample_identities")
        check(total["design_variance"] == {"common": Fraction(4), "mutually_exclusive": Fraction(),
                                            "independent": Fraction(2)}[frame], "explicit_counterexample_identities")
        witnesses[frame] = {"law": law, "one_birth_summary": union, "two_distinct_events_HT": total}
    copies = event_summary(3, {7: 1}, {"one_birth": (0, 1, 2)})
    check(copies["expected_observed_carrier_copy_count"] == 3 and
          copies["expected_observed_distinct_event_count"] == 1, "explicit_counterexample_identities")
    same = ht_summary(1, {0: Fraction(1, 2), 1: Fraction(1, 2)}, {"first": (0,), "second": (0,)})
    check(same["fixed_catalogue_size"] == 2 and same["design_variance"] == 4,
          "explicit_counterexample_identities")
    empty = ht_summary(0, {0: 1}, {})
    check(empty["design_expectation"] == 0 and empty["design_variance"] == 0,
          "explicit_counterexample_identities")
    rare = Fraction(1, 2**31)
    boundary_law = {0: 1-rare, 255: rare}
    boundary_events = {"e"+str(index): (index,) for index in range(8)}
    boundary = ht_summary(8, boundary_law, boundary_events)
    boundary_values = {mask: ht_value(8, boundary_law, boundary_events, mask) for mask in boundary_law}
    check(sum((boundary_law[mask]*value for mask, value in boundary_values.items()), Fraction()) == 8,
          "explicit_counterexample_identities")
    check(sum((boundary_law[mask]*(value-8)**2 for mask, value in boundary_values.items()), Fraction())
          == boundary["design_variance"] == 64*(1/rare-1), "explicit_counterexample_identities")
    route_events = {"R1": (0,), "R2": (1, 2), "R3": (3,)}
    route_law = independent_capture_law((Fraction(1, 2),)*4)
    route_summary = event_summary(4, route_law, route_events)
    inclusion = route_summary["event_inclusion"]
    shares = {name: value/sum(inclusion.values()) for name, value in inclusion.items()}
    curvature = shares["R2"]**2/(shares["R1"]*shares["R3"])
    check(inclusion == {"R1": Fraction(1, 2), "R2": Fraction(3, 4), "R3": Fraction(1, 2)},
          "explicit_counterexample_identities")
    check(curvature == Fraction(9, 4), "explicit_counterexample_identities")
    invalid = [lambda: event_catalogue(True, {}, True),
               lambda: event_catalogue(9, {}, True),
               lambda: event_summary(True, {0: 1}, {}),
               lambda: event_summary(9, {0: 1}, {}),
               lambda: event_summary(1, {}, {}),
               lambda: event_summary(1, {0: Fraction(1, 2)}, {}),
               lambda: event_summary(1, {0: 2, 1: -1}, {}),
               lambda: event_summary(1, {2: 1}, {}),
               lambda: event_summary(1, {True: 1}, {}),
               lambda: event_summary(1, {0: 1.0}, {}),
               lambda: event_summary(1, {0: True}, {}),
               lambda: event_summary(1, {0: Fraction(1, 2**40), 1: 1-Fraction(1, 2**40)}, {}),
               lambda: event_summary(1, {0: 1}, {"event": None}),
               lambda: event_summary(1, {0: 1}, {"event": (None,)}),
               lambda: event_summary(1, {0: 1}, {"event": (True,)}),
               lambda: event_summary(1, {0: 1}, {"event": (0, 0)}),
               lambda: event_summary(1, {0: 1}, {"event": (1,)}),
               lambda: event_summary(1, {0: 1}, {"event": (0,)}, ancestry_known=False),
               lambda: event_summary(1, {0: 1}, {"event": (0,)}, ancestry_known=None),
               lambda: ht_summary(1, {0: 1}, {"event": (0,)}),
               lambda: ht_summary(1, {1: 1}, {"extinct": ()}),
               lambda: ht_value(1, {1: 1}, {"event": (0,)}, 0),
               lambda: ht_value(1, {1: 1}, {"event": (0,)}, True),
               lambda: frechet_union_bounds((0.5,)),
               lambda: frechet_union_bounds((2,)),
               lambda: independent_capture_law((True,)),
               lambda: extremal_union_laws((Fraction(1, 2**40),)),
               lambda: event_summary(1, {0: 1}, {str(i): () for i in range(9)})]
    for operation in invalid:
        try:
            operation()
        except (TypeError, ValueError):
            checks["invalid_input_guards"] += 1
        else:
            raise AssertionError("Invalid event-capture input admitted")
    return _json_exact({"schema_version": 1, "status": "passed",
        "scope": "finite fixed-event/design expectation identities on synthetic joint genotype-observability laws",
        "checks": checks, "same_descendant_marginals_different_event_inclusion": witnesses,
        "one_birth_three_inherited_observed_copies": copies,
        "distinct_events_same_carriers": same,
        "known_empty_catalogue": empty,
        "maximum_dimension_rare_joint_inclusion": {"law": boundary_law, "events": boundary_events,
            "HT_summary": boundary, "complete_mask_HT_values": boundary_values},
        "route_dependent_event_inclusion_example": {"events": route_events, "per_descendant_marginals": (Fraction(1, 2),)*4,
            "true_fixed_events_per_route": 1, "event_inclusion": inclusion,
            "normalized_expected_detected_event_shares": shares, "raw_curvature": curvature,
            "expected_share_equality_is_not_a_full_sampling_law_or_causal_effect": True},
        "biological_catalogue_or_mutation_process_identified": False,
        "biological_estimator_or_confidence_interval_fitted": False,
        "actual_study_fields_resolved": 0, "new_count_law_or_error_budget": False,
        "new_theorem_or_priority_claim": False, "source_acquisitions": 0})
