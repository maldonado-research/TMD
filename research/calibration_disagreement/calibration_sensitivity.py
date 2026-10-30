#!/usr/bin/env python3
"""Conditional sensitivity of TMD's hypothetical two-context design.

Standard library only. CP root brackets use exact integer arithmetic; reported
transcendental quantities use 60-digit Decimal arithmetic, not certified logs.
This is a design calculation, not observations, a power analysis, or a new test.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from math import comb
from pathlib import Path


def tail_numerator(n, k, a, b, upper):
    """Binomial tail numerator with common denominator b**n at p=a/b."""
    indexes = range(k, n + 1) if upper else range(k + 1)
    return sum(comb(n, j) * a**j * (b - a)**(n - j) for j in indexes)


def compare_tail(n, k, p, upper, target):
    difference = (tail_numerator(n, k, p.numerator, p.denominator, upper)
                  * target.denominator
                  - target.numerator * p.denominator**n)
    return (difference > 0) - (difference < 0)


def root_bracket(n, k, upper, target, bits):
    lo, hi = Fraction(0), Fraction(1)
    for _ in range(bits):
        mid = (lo + hi) / 2
        sign = compare_tail(n, k, mid, upper, target)
        if sign == 0:
            return mid, mid
        # Upper-tail probability is increasing; lower-tail probability decreases.
        if (sign < 0) == upper:
            lo = mid
        else:
            hi = mid
    assert hi - lo == Fraction(1, 2**bits)
    assert compare_tail(n, k, lo, upper, target) * (1 if upper else -1) <= 0
    assert compare_tail(n, k, hi, upper, target) * (1 if upper else -1) >= 0
    return lo, hi


def cp_interval(n, k, tail, bits):
    lower = (Fraction(0), Fraction(0)) if k == 0 else root_bracket(n, k, True, tail, bits)
    upper = (Fraction(1), Fraction(1)) if k == n else root_bracket(n, k, False, tail, bits)
    assert 0 <= lower[0] <= upper[1] <= 1
    return lower[0], upper[1], lower, upper


def dec(x):
    return Decimal(x.numerator) / Decimal(x.denominator) if isinstance(x, Fraction) else Decimal(x)


def decimal_text(x):
    return format(dec(x), '.30g')


def normalize(values):
    total = sum(values)
    return tuple(x / total for x in values)


def symmetric_vector(p):
    return ((1 - p) / 2, p, (1 - p) / 2)


def divergence(p, q):
    return sum(dec(x) * (dec(x) / dec(y)).ln() for x, y in zip(p, q) if x)


def vector_text(vector):
    return [decimal_text(x) for x in vector]


def calculate():
    n, bits = 100, 64
    alpha, tails = Fraction(1, 20), 12
    tail = alpha / tails
    intervals = {k: cp_interval(n, k, tail, bits) for k in (10, 20, 80)}
    l10, u10, _, _ = intervals[10]
    l20, u20, _, _ = intervals[20]
    l80, u80, _, _ = intervals[80]

    # Each interval below is sharp over all three independent box coordinates.
    a1 = (l10 / (l10 + 2*u20), u10 / (u10 + 2*l20))
    a2 = (l80 / (l80 + 2*u20), u80 / (u80 + 2*l20))
    assert a1[1] < a2[0]
    p1, p2 = symmetric_vector(a1[1]), symmetric_vector(a2[0])
    f1, f2 = normalize((l20, u10, l20)), normalize((u20, l80, u20))
    assert p1 == f1 and p2 == f2  # Attainment by all six admissible F values.
    mean = tuple((x + y)/2 for x, y in zip(p1, p2))
    fixed1 = tuple(Fraction(k, 103) for k in (41, 21, 41))
    fixed2 = tuple(Fraction(k, 243) for k in (41, 161, 41))
    fixed_mean = tuple((x + y)/2 for x, y in zip(fixed1, fixed2))
    illustrative_common = tuple(Fraction(k, 4) for k in (1, 2, 1))
    interior_F1 = tuple(Fraction(k,1000) for k in (107,204,107))
    interior_F2 = tuple(Fraction(k,1000) for k in (324,676,324))
    for counts, values in (((20,10,20),interior_F1),((20,80,20),interior_F2)):
        for k, value in zip(counts,values):
            # Strictly inside the exact-root CP interval, not just its outer bracket.
            assert intervals[k][2][1] < value < intervals[k][3][0]
    interior1, interior2 = normalize(interior_F1), normalize(interior_F2)
    for p in (p1, p2, mean, fixed1, fixed2, fixed_mean, illustrative_common):
        assert sum(p) == 1 and all(0 < x < 1 for x in p)

    with localcontext() as ctx:
        ctx.prec = 60
        js = (divergence(p1, mean) + divergence(p2, mean))/2
        point_js = (divergence(fixed1, fixed_mean) + divergence(fixed2, fixed_mean))/2
        misspecification = (divergence(p1, fixed1) + divergence(p2, fixed2))/2
        fixed_gain = js - misspecification
        specified_gain = fixed_gain + divergence(mean, illustrative_common)
        interior_gain = (divergence(interior1,illustrative_common)
                         + divergence(interior2,illustrative_common)
                         - divergence(interior1,fixed1)
                         - divergence(interior2,fixed2))/2
        z1 = ((dec(l10)/dec(u20)).ln(), (dec(u10)/dec(l20)).ln())
        z2 = ((dec(l80)/dec(u20)).ln(), (dec(u80)/dec(l20)).ln())
        return {
            'status': 'illustrative_conditional_design_sensitivity_not_empirical_or_power',
            'assumptions': {
                'qstar': ['1/3', '1/3', '1/3'],
                'context_weights': ['1/2', '1/2'],
                'hypothetical_control_counts': [[20,10,20],[20,80,20]],
                'n_per_binary_control': n,
                'six_marginal_binomial_count_laws_assumed': True,
                'cross_arm_independence_required_for_union_bound': False,
                'biological_truth_for_sensitivity': 'p_c = normalize(qstar * F_c)',
                'transfer_error_and_qstar_uncertainty': 'excluded, not assumed calibrated by these data',
                'alpha': str(alpha),
                'tail_allocation': str(tail),
                'allocation_status': 'illustrative separate budget; not frozen study allocation',
                'CP_root_bracket_width_at_most': str(Fraction(1, 2**bits)),
                'transcendental_arithmetic': '60-digit Decimal; printed 30 significant digits; not certified',
            },
            'CP_intervals': {str(k): {
                'outer_lower': decimal_text(row[0]), 'outer_upper': decimal_text(row[1]),
                'lower_root_bracket': list(map(str,row[2])),
                'upper_root_bracket': list(map(str,row[3])),
            } for k,row in intervals.items()},
            'A_probability_intervals': [vector_text(a1),vector_text(a2)],
            'z_intervals': [vector_text(z1),vector_text(z2)],
            'z_gap_lower': decimal_text(z2[0]-z1[1]),
            'attaining_F_vectors': [vector_text((l20,u10,l20)),vector_text((u20,l80,u20))],
            'attaining_outcome_vectors': [vector_text(p1),vector_text(p2)],
            'best_common_at_witness': vector_text(mean),
            'oracle_JS_at_point_forecasts_nats': decimal_text(point_js),
            'sharp_oracle_JS_over_outer_CP_box_nats': decimal_text(js),
            'point_to_robust_JS_ratio': decimal_text(point_js/js),
            'total_oracle_expected_log_regret_500_endpoints_each': decimal_text(1000*js),
            'fixed_qF_vectors': [vector_text(fixed1),vector_text(fixed2)],
            'fixed_qF_misspecification_cost_at_witness': decimal_text(misspecification),
            'fixed_qF_gain_over_best_common_at_witness': decimal_text(fixed_gain),
            'illustrative_fixed_common': vector_text(illustrative_common),
            'fixed_qF_gain_over_illustrative_common_at_witness': decimal_text(specified_gain),
            'strict_interior_counterexample': {
                'F_vectors_exact': [list(map(str,interior_F1)),list(map(str,interior_F2))],
                'outcome_vectors': [vector_text(interior1),vector_text(interior2)],
                'fixed_qF_gain_over_illustrative_common': decimal_text(interior_gain),
            },
            'interpretation': [
                'The oracle JS bound compares true qstar*F probabilities to any common vector.',
                'The negative witness score concerns the stored point forecasts, not an oracle.',
                'No actual TMD coefficients, training observations or held-out endpoints are supplied.',
                'No achieved power, study-size recommendation or study decision follows.',
                'Observed independently frozen forecast evaluation does not require F to be known truth.',
                'This confidence box is neither a posterior distribution nor a probability on its corners.',
            ],
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = json.dumps(calculate(), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(output)
    else:
        print(output, end='')
