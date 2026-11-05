#!/usr/bin/env python3
"""Exact finite-law checks, independent of the threshold producer and CP code.

All coverage decisions use integer binomial tails, not numerical beta quantiles.
This is a finite audit of the separately supplied proofs, not a replacement for
their arbitrary-distribution arguments. No third-party dependencies or network.
"""
import argparse
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from math import comb
from pathlib import Path
import json


def compositions(total, length):
    if length == 1:
        yield (total,)
        return
    for first in range(1, total - length + 2):
        for rest in compositions(total - first, length - 1):
            yield (first,) + rest


@lru_cache(None)
def binomial_cdfs(n, successes, denominator):
    """Integer numerators for CDF(k; n, successes/denominator)."""
    failures = denominator - successes
    running = 0
    result = []
    for k in range(n + 1):
        running += comb(n, k) * successes**k * failures**(n-k)
        result.append(running)
    assert running == denominator**n
    return tuple(result)


def inclusive_error(weights, n, gamma):
    """P[P(S>=M) > CP_U(K,n,gamma)] for ordered finite scores."""
    denominator = sum(weights)
    sample_denominator = denominator**n
    lower_mass = 0
    failure_mass = 0
    joint_mass = 0
    for mass in weights:
        # The inclusive tail at this possible maximum is 1 - F(M-).
        tail_numerator = denominator - lower_mass
        cdfs = binomial_cdfs(n, tail_numerator, denominator)
        for k in range(1, n+1):
            mass_at_max_and_k_ties = comb(n, k) * mass**k * lower_mass**(n-k)
            joint_mass += mass_at_max_and_k_ties
            # For k<n, p>CP_U(k) iff BinCDF(k;n,p)<gamma. At k=n the
            # CDF is one and the inequality is false, as CP_U(n)=1.
            if cdfs[k] * gamma.denominator < gamma.numerator * sample_denominator:
                failure_mass += mass_at_max_and_k_ties
        lower_mass += mass
    assert joint_mass == sample_denominator
    return F(failure_mass, sample_denominator)


def strict_max_error(weights, n, gamma):
    """P[P(S>M) > 1-gamma**(1/n)] using only integer comparisons."""
    denominator = sum(weights)
    sample_denominator = denominator**n
    cumulative = 0
    failure_mass = 0
    for mass in weights:
        previous = cumulative
        cumulative += mass
        if cumulative**n * gamma.denominator < gamma.numerator * sample_denominator:
            failure_mass += cumulative**n - previous**n
    return F(failure_mass, sample_denominator)


def order_statistic_error(weights, n, rank, epsilon):
    """Strict-tail failure at ascending order rank, all arithmetic exact."""
    denominator = sum(weights)
    cumulative = 0
    qualifying = 0
    for mass in weights:
        cumulative += mass
        if F(denominator - cumulative, denominator) > epsilon:
            qualifying += mass
    cdfs = binomial_cdfs(n, qualifying, denominator)
    return F(denominator**n - cdfs[rank-1], denominator**n)


def run():
    gammas = (F(1, 100), F(1, 20), F(1, 4), F(3, 4))
    epsilons = (F(1, 20), F(1, 4), F(1, 2), F(3, 4))
    laws = [weights for denominator in range(1, 13)
            for length in range(1, min(5, denominator)+1)
            for weights in compositions(denominator, length)]
    maxima = {str(gamma): {'inclusive': F(0), 'strict': F(0)} for gamma in gammas}
    inclusive_checks = strict_checks = order_checks = 0
    for weights in laws:
        for n in range(1, 13):
            for gamma in gammas:
                inc = inclusive_error(weights, n, gamma)
                strict = strict_max_error(weights, n, gamma)
                assert inc <= gamma, (weights, n, gamma, inc)
                assert strict <= gamma, (weights, n, gamma, strict)
                maxima[str(gamma)]['inclusive'] = max(maxima[str(gamma)]['inclusive'], inc)
                maxima[str(gamma)]['strict'] = max(maxima[str(gamma)]['strict'], strict)
                inclusive_checks += 1
                strict_checks += 1
            if n <= 6:
                for rank in range(1, n+1):
                    for epsilon in epsilons:
                        actual = order_statistic_error(weights, n, rank, epsilon)
                        target = 1-epsilon
                        cdfs = binomial_cdfs(n, target.numerator, target.denominator)
                        bound = F(target.denominator**n - cdfs[rank-1], target.denominator**n)
                        assert actual <= bound, (weights, n, rank, epsilon, actual, bound)
                        order_checks += 1

    # Exact design calculation for strict sample maximum, fixed epsilon/gamma.
    epsilon, gamma = F(1, 20), F(1, 20)
    minimum_n = next(n for n in range(1, 1000) if (1-epsilon)**n <= gamma)
    assert minimum_n == 59 and (1-epsilon)**58 > gamma

    # Constant score: inclusive false-gate probability is one with certainty.
    # K=n makes tie-aware CP_U(K)=1; applying strict CP_U(0) would fail always.
    for n in range(1, 13):
        assert inclusive_error((1,), n, F(1, 20)) == 0
        assert strict_max_error((1,), n, F(1, 20)) == 0

    # Fixed sample size and frozen-score premises are essential. A deliberately
    # learned score S_D(x)=1{x not observed in D} maps every calibration value
    # to zero. With n=2 from Uniform{1,...,100}, future strict passage is .98
    # or .99 for every D. Both exceed CP_U(0,2,.05) by exact root comparison.
    for distinct in (1, 2):
        false_gate = F(100-distinct, 100)
        assert (1-false_gate)**2 < F(1, 20)

    # Unbounded stopping: for independent Bernoulli(.1) fixed-gate controls,
    # each disjoint block of 59 all-zero outcomes wrongly certifies p<=.05
    # by strict-maximum calibration. Thirty such blocks make failure >.05;
    # scanning/restarting was not authorized by a fixed-n calibration rule.
    block_probability = F(9, 10)**59
    searched_failure = 1-(1-block_probability)**30
    assert searched_failure > F(1, 20)

    return {
        'status': 'passed',
        'scope': 'Exact finite audits of separately proved arbitrary-distribution statements; no native calibration.',
        'oracle_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'finite_laws': len(laws),
        'law_grid': {'ordered_support_sizes': [1, 2, 3, 4, 5], 'positive_integer_mass_denominators': [1, 12]},
        'sample_sizes': [1, 12],
        'gamma_values_exact': [str(x) for x in gammas],
        'inclusive_max_CP_K_coverage_checks': inclusive_checks,
        'strict_max_order_statistic_coverage_checks': strict_checks,
        'general_ascending_order_statistic_coverage_checks': order_checks,
        'general_order_statistic_sample_sizes': [1, 6],
        'general_order_statistic_epsilon_values_exact': [str(x) for x in epsilons],
        'maximum_grid_noncoverage': {g: {kind: str(value) for kind, value in row.items()} for g, row in maxima.items()},
        'strict_5_percent_95_percent_tolerance_design': {
            'minimum_n': minimum_n, 'n58_failure_probability_exact': str((1-epsilon)**58),
            'n59_failure_probability_exact': str((1-epsilon)**59),
            'interpretation': 'Fixed-n distribution-free tolerance calculation; not native calibration, power, or a scientific sample-size recommendation.'},
        'inclusive_missing_ties': {'n': 12, 'possible_K': [1, 12], 'worst_case_upper': '1', 'constant_score_inclusive_false_gate': '1'},
        'learned_score_counterexample': {'raw_law': 'iid uniform on 100 symbols', 'n': 2,
            'score': 'S_D(x)=0 for symbols seen in calibration, 1 otherwise',
            'calibration_maximum': 0, 'future_strict_false_gate_minimum_exact': '49/50',
            'strict_tolerance_bound_noncoverage_exact': '1',
            'interpretation': 'Generic synthetic counterexample to omitting the fixed score-processor premise; no attribution to a biological study.'},
        'repeated_search_counterexample': {'law': 'iid Bernoulli(1/10)', 'block_n': 59, 'independent_blocks': 30,
            'each_block_all_zero_probability_exact': str(block_probability),
            'at_least_one_all_zero_block_probability_exact': str(searched_failure),
            'at_least_one_all_zero_block_probability_approx': float(searched_failure)},
        'independence': 'No imports or calls to the producer, preserved CP engine, scipy, or any third-party package.'
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
