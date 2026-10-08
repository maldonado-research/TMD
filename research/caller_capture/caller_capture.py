"""Exact finite threshold/reference capture; conditional synthetic methods only."""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import lcm

MAX_DESCENDANTS = 8
MAX_BOUND_DESCENDANTS = 4
INPUT_BITS = 32


def _n(value, maximum=MAX_DESCENDANTS):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError("descendant count outside supported integer domain; bool excluded")
    return value


def _exact(value):
    if type(value) not in (int, Fraction):
        raise TypeError("external probability must be int/Fraction; bool and float excluded")
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > INPUT_BITS:
        raise ValueError("external rational exceeds 32-bit numerator/denominator cap")
    if not 0 <= value <= 1:
        raise ValueError("probability outside [0,1]")
    return value


def _marginals(values, maximum):
    if type(values) not in (tuple, list):
        raise ValueError("marginals must be an explicit tuple/list")
    _n(len(values), maximum)
    return tuple(_exact(value) for value in values)


def _law(n, law):
    _n(n)
    if type(law) is not dict or not law or len(law) > 1 << n:
        raise ValueError("complete law must be a nonempty bounded mask dictionary")
    if any(type(mask) is not int or not 0 <= mask < 1 << n for mask in law):
        raise ValueError("mask must be integer in the n-bit domain; bool excluded")
    law = {mask: _exact(weight) for mask, weight in sorted(law.items())}
    if sum(law.values(), Fraction()) != 1:
        raise ValueError("complete joint mask law must be normalized")
    return law


def _predicate(n, carriers, references, k, r, ancestry_known):
    _n(n)
    if ancestry_known is not True:
        raise ValueError("known ancestry/carrier/reference mapping must be supplied")
    masks = []
    for group in (carriers, references):
        if type(group) not in (tuple, list) or len(group) > n:
            raise ValueError("known sets must be explicit bounded tuple/list, not unknown")
        if any(type(index) is not int or not 0 <= index < n for index in group):
            raise ValueError("known set indices must be integer in the n-bit domain")
        if len(set(group)) != len(group):
            raise ValueError("duplicate set indices are not allowed")
        masks.append(sum(1 << index for index in group))
    if masks[0] & masks[1]:
        raise ValueError("carrier and reference sets must be disjoint")
    if type(k) is not int or not 1 <= k <= 9 or type(r) is not int or not 0 <= r <= 9:
        raise ValueError("k must be integer 1..9 and r integer 0..9; bool excluded")
    return masks[0], masks[1], k, r


def _included(mask, predicate):
    carrier, reference, k, r = predicate
    return (mask & carrier).bit_count() >= k and (mask & reference).bit_count() >= r


def caller_summary(n, law, carriers, references, k, r, ancestry_known=True):
    """Known target-specific correct calls; no native caller/origin authentication."""
    n = _n(n)
    predicate = _predicate(n, carriers, references, k, r, ancestry_known)
    law = _law(n, law)
    marginals = tuple(sum((weight for mask, weight in law.items() if mask & (1 << index)), Fraction())
                      for index in range(n))
    successful = tuple(mask for mask, weight in law.items() if weight > 0 and _included(mask, predicate))
    return {"descendant_call_marginals": marginals,
            "inclusion_probability": sum((law[mask] for mask in successful), Fraction()),
            "successful_masks": successful,
            "predicate_true_masks": tuple(mask for mask in range(1 << n) if _included(mask, predicate)),
            "expected_carrier_call_copies": sum((marginals[index] for index in carriers), Fraction()),
            "expected_reference_calls": sum((marginals[index] for index in references), Fraction()),
            "structural_zero": k > len(carriers) or r > len(references),
            "known_mapping_supplied_not_authenticated": True,
            "complete_native_caller_or_mutation_origin_authenticated": False}


def independent_law(marginals):
    """Labelled independence special case, not inferred from marginals."""
    marginals = _marginals(marginals, MAX_DESCENDANTS)
    law = {}
    for mask in range(1 << len(marginals)):
        value = Fraction(1)
        for index, probability in enumerate(marginals):
            value *= probability if mask & (1 << index) else 1-probability
        if value:
            law[mask] = value
    return law


def _inverse(matrix):
    """Structural small binary matrix inverse; None means singular."""
    size = len(matrix)
    work = [[Fraction(value) for value in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value/scale for value in work[column]]
        for row in range(size):
            scale = work[row][column]
            if row != column and scale:
                work[row] = [a-scale*b for a, b in zip(work[row], work[column])]
    inverse = tuple(tuple(row[size:]) for row in work)
    denominator = lcm(*(value.denominator for row in inverse for value in row))
    integers = tuple(tuple(value.numerator*(denominator//value.denominator) for value in row)
                     for row in inverse)
    return integers, denominator


@lru_cache(maxsize=5)
def _basis_table(n):
    _n(n, MAX_BOUND_DESCENDANTS)
    nonsingular, enumerated = [], 0
    for masks in combinations(range(1 << n), n+1):
        enumerated += 1
        matrix = [[1]*(n+1)] + [[(mask >> index) & 1 for mask in masks] for index in range(n)]
        inverse = _inverse(matrix)
        if inverse is not None:
            nonsingular.append((masks, inverse[0], inverse[1]))
    return tuple(nonsingular), enumerated


def marginal_bounds(marginals, carriers, references, k, r, ancestry_known=True):
    """Sharp population/design bounds over every compatible joint mask law, n<=4."""
    marginals = _marginals(marginals, MAX_BOUND_DESCENDANTS)
    n = len(marginals)
    predicate = _predicate(n, carriers, references, k, r, ancestry_known)
    denominator = lcm(*(value.denominator for value in marginals)) if marginals else 1
    target = (denominator,) + tuple(value.numerator*(denominator//value.denominator) for value in marginals)
    table, enumerated = _basis_table(n)
    lower, upper, lower_witness, upper_witness, feasible = None, None, None, None, 0
    for masks, inverse, inverse_denominator in table:
        numerators = tuple(sum(coefficient*rhs for coefficient, rhs in zip(row, target)) for row in inverse)
        if any(value < 0 for value in numerators):
            continue
        feasible += 1
        common = denominator*inverse_denominator
        objective = sum(value for mask, value in zip(masks, numerators) if _included(mask, predicate))
        if lower is None or objective*lower[1] < lower[0]*common:
            lower = objective, common
            lower_witness = masks, numerators, common
        if upper is None or objective*upper[1] > upper[0]*common:
            upper = objective, common
            upper_witness = masks, numerators, common
    if feasible == 0:
        raise ArithmeticError("compatible marginal polytope has no enumerated vertex")
    def law(witness):
        masks, numerators, common = witness
        return {mask: Fraction(value, common) for mask, value in zip(masks, numerators) if value}
    independent = Fraction()
    for mask, value in independent_law(marginals).items():
        if _included(mask, predicate):
            independent += value
    return {"lower": Fraction(*lower), "upper": Fraction(*upper),
            "lower_law": law(lower_witness), "upper_law": law(upper_witness),
            "value_if_independent": independent,
            "bases_enumerated": enumerated, "nonsingular_bases": len(table), "feasible_bases": feasible,
            "structural_zero": k > len(carriers) or r > len(references),
            "bounds_are_population_constraints_not_empirical_confidence_limits": True,
            "complete_native_caller_or_mutation_origin_authenticated": False}
