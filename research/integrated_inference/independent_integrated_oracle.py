#!/usr/bin/env python3
"""Exact, producer-independent audit of the integrated error argument.

Enumerates finite categorical experiments with random learned gates and exact
one-sided binomial test inversion. No producer imports, quantiles or simulation.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from hashlib import sha256
from math import comb, factorial, lcm
from pathlib import Path
import argparse
import json

ALPHA, SHARE, CONTEXTS = F(1, 20), F(1, 8), 2
GAMMA = ALPHA * SHARE / (2 * CONTEXTS)
ETA = ALPHA * (1 - SHARE) / (14 * CONTEXTS)


def binomial_masses(n, p):
    a, b = p.numerator, p.denominator
    return [comb(n, k) * a**k * (b-a)**(n-k) for k in range(n+1)], b**n


def failures(n, p, tail, lower):
    """All k with a true p strictly outside the ideal one-sided CP bound."""
    masses, den = binomial_masses(n, p)
    running = 0
    bad = set()
    if lower:
        for k in range(n, -1, -1):
            running += masses[k]
            if running * tail.denominator < tail.numerator * den:
                bad.add(k)
    else:
        for k in range(n+1):
            running += masses[k]
            if running * tail.denominator < tail.numerator * den:
                bad.add(k)
    return bad, F(sum(masses[k] for k in bad), den)


def weak_compositions(n, length):
    if length == 1:
        yield (n,)
    else:
        for k in range(n+1):
            for rest in weak_compositions(n-k, length-1):
                yield (k,) + rest


def conditional_counts(a, f, n=24):
    """Exact union of 3 label UCB, native gate LCB, 3 route-control LCB errors.

    T=3/4; p=(1/4,1/2,1/4); native/control correct probability a.
    True-route gate pass means correct route; Other pass is labelled U.
    Native label and gate counts use the SAME iid full-cohort units.
    Three route-control samples are independent conditional on calibration.
    """
    label = (F(3, 16)*a, F(3, 8)*a, F(3, 16)*a)
    probs = label + (f/4, 1-sum(label)-f/4)
    assert all(0 <= p <= 1 for p in probs) and sum(probs) == 1
    gate = sum(probs[:-1])
    upper_bad = [failures(n, p, ETA, False)[0] for p in label]
    gate_bad, gate_error = failures(n, gate, ETA, True)
    den = lcm(*(p.denominator for p in probs))
    weights = [int(p*den) for p in probs]
    total = error = states = 0
    fn = factorial(n)
    for counts in weak_compositions(n, 5):
        if any(k and not w for k, w in zip(counts, weights)):
            continue
        mass = fn
        for k in counts:
            mass //= factorial(k)
        for k, w in zip(counts, weights):
            mass *= w**k
        total += mass
        states += 1
        if any(counts[j] in upper_bad[j] for j in range(3)) or n-counts[-1] in gate_bad:
            error += mass
    assert total == den**n
    endpoint_error = F(error, total)
    control_bad, control_error = failures(n, a, ETA, True)
    assert control_error <= ETA
    for p in label:
        assert failures(n, p, ETA, False)[1] <= ETA
    assert gate_error <= ETA and endpoint_error <= 4*ETA
    # This factorization belongs ONLY to the explicit synthetic law. The
    # general integration proof uses a union bound, without independence.
    union_error = 1 - (1-endpoint_error)*(1-control_error)**3
    assert union_error <= 7*ETA
    return union_error, {
        'full_cohort_n': n, 'control_n_each_route': n,
        'native_T': '3/4', 'native_eligible_p': ['1/4', '1/2', '1/4'],
        'true_route_correct_probability': str(a), 'Other_false_gate_probability': str(f),
        'native_gate_probability': str(gate), 'category_probabilities': list(map(str, probs)),
        'nonzero_multinomial_states': states,
        'label_upper_failure_counts': [sorted(bad) for bad in upper_bad],
        'gate_lower_failure_counts': sorted(gate_bad),
        'control_lower_failure_counts': sorted(control_bad),
        'same_unit_label_gate_union_error_exact': str(endpoint_error),
        'one_control_lower_error_exact': str(control_error),
        'seven_endpoint_union_error_exact': str(union_error),
        'seven_endpoint_union_error_approx': float(union_error),
        'conditional_union_budget_exact': str(7*ETA),
    }


def experiment(rule):
    # Known-Other calibration scores: P(S=0)=1/5, P(S=1)=4/5.
    # True-route scores: P(S=1)=1/4, P(S=2)=3/4.
    # Every context/arm intentionally shares the SAME calibration and future
    # samples; fourfold perfect dependence checks independence is unnecessary.
    n = 8
    masses, den = binomial_masses(n, F(4, 5))
    count_cache, details, cal_error, combined_error, count_error = {}, [], F(0), F(0), F(0)
    for k, mass in enumerate(masses):
        maximum = int(k > 0)
        multiplicity = k if k else n
        if rule == 'strict_maximum':
            a, f = (F(1), F(4,5)) if maximum == 0 else (F(3,4), F(0))
            cal_bad = (1-f)**n < GAMMA
        else:
            a, f = F(1), (F(1) if maximum == 0 else F(4,5))
            cal_bad = multiplicity in failures(n, f, GAMMA, False)[0]
        key = (a, f)
        if key not in count_cache:
            count_cache[key] = conditional_counts(a, f)
        error, count_detail = count_cache[key]
        weight = F(mass, den)
        cal_error += weight * cal_bad
        count_error += weight * error
        combined_error += weight * (1 if cal_bad else error)
        details.append({'calibration_ones': k, 'maximum': maximum,
                        'maximum_multiplicity': multiplicity, 'probability_exact': str(weight),
                        'calibration_certificate_fails': bool(cal_bad),
                        'count_experiment_index': list(count_cache).index(key)})
    assert 0 < cal_error <= GAMMA
    assert 0 < count_error <= 7*ETA
    assert 0 < combined_error <= cal_error + count_error <= GAMMA + 7*ETA <= ALPHA
    return {
        'rule': rule, 'calibration_n': n, 'calibration_law': {'0': '1/5', '1': '4/5'},
        'cross_context_and_arm_dependence': 'all four cells use identical samples and outcomes',
        'calibration_outcomes': details,
        'conditional_count_experiments': [detail for _, detail in count_cache.values()],
        'calibration_union_noncoverage_exact': str(cal_error),
        'averaged_count_union_noncoverage_exact': str(count_error),
        'combined_certificate_noncoverage_exact': str(combined_error),
        'combined_certificate_noncoverage_approx': float(combined_error),
        'global_budget_exact': str(ALPHA),
        'projection_actual_noncoverage_computed': False,
        'scope': 'Exact sufficient simultaneous event; projection can cover even when this event fails.'}


def run():
    assert GAMMA == ETA == F(1, 640)
    assert 2*CONTEXTS*GAMMA + 14*CONTEXTS*ETA == ALPHA
    epsilon = F(1,20)
    minimum_n = next(n for n in range(1,1000) if (1-epsilon)**n <= GAMMA)
    assert minimum_n == 126
    with localcontext() as ctx:
        ctx.prec = 50
        upper = {str(n): str(1-(Decimal(1)/640)**(Decimal(1)/n)) for n in (59,125,126)}
    block = F(47,50)**126
    four = 1-(1-block)**4
    many = 1-(1-block)**125
    assert four > GAMMA and many > ALPHA
    # Counts also require fixed sampling: fixed Bernoulli(1/2) stream, n=10,
    # all-success lower CP >1/2 at eta=1/640; two searched blocks violate eta.
    count_block = F(1,2)**10
    count_search = 1-(1-count_block)**2
    assert count_block < ETA < count_search
    return {
        'status': 'passed', 'oracle_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'independence_from_producer': 'standard library only; no producer/CP imports or simulation',
        'allocation': {'contexts': CONTEXTS, 'alpha': str(ALPHA), 'calibration_share': str(SHARE),
                       'calibration_components': 2*CONTEXTS, 'gamma': str(GAMMA),
                       'count_components': 14*CONTEXTS, 'eta': str(ETA)},
        'experiments': [experiment('strict_maximum'), experiment('inclusive_maximum')],
        'strict_5_percent_population_tail_planning': {
            'minimum_n_per_gate': minimum_n, 'strict_U_approximations': upper,
            'n125_failure_exact': str((1-epsilon)**125), 'n126_failure_exact': str((1-epsilon)**126),
            'scope': 'Conditional design arithmetic under stated premises; no native validation or power claim'},
        'optional_calibration_search_counterexample': {
            'Other_score_law': 'Bernoulli(3/50)', 'fixed_block_n': 126,
            'all_zero_block_probability_exact': str(block),
            'four_blocks_failure_exact': str(four), 'four_blocks_failure_approx': float(four),
            '125_blocks_failure_approx': float(many),
            '125_blocks_failure_gt_global_alpha_exactly_verified': True,
            'scope': 'Counterexample to per-gate and global false-tail certification after unauthorized search; not a computed J-test size'},
        'optional_count_search_counterexample': {
            'law': 'Bernoulli(1/2)', 'block_n': 10, 'searched_blocks': 2,
            'all_success_block_probability_exact': str(count_block),
            'searched_lower_endpoint_noncoverage_exact': str(count_search), 'eta_exact': str(ETA)},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
