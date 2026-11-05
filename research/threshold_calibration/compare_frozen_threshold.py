#!/usr/bin/env python3
"""Independently check a pinned threshold wrapper using exact binomial sums."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import comb
from pathlib import Path
import json
import sys

PRODUCER_SHA256 = '4256ca07cdd4d6e597c4ed2eda28926917e428391aa05710b2f5b962eb616c0b'


def load(path):
    assert sha256(path.read_bytes()).hexdigest() == PRODUCER_SHA256, 'Frozen producer hash mismatch'
    spec = spec_from_file_location('reviewed_threshold_producer', path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cdf(n, k, p):
    return sum(F(comb(n, j)) * p**j * (1-p)**(n-j) for j in range(k+1))


def run(producer_dir, repository):
    producer = load(producer_dir / 'threshold_calibration.py')
    engine, cp = producer.load_engine(repository)
    strict_input = json.loads((producer_dir / 'example_strict_twelve.json').read_text())
    inclusive_input = json.loads((producer_dir / 'example_inclusive_unique_maximum.json').read_text())
    checks = 0
    summaries = []
    for gamma in (F(1, 100), F(1, 20), F(1, 4), F(3, 4)):
        for n in tuple(range(1, 13)) + (59,):
            for rule in ('strict_maximum', 'inclusive_maximum'):
                for k in ((0,) if rule == 'strict_maximum' else range(1, n+1)):
                    doc = deepcopy(strict_input if rule == 'strict_maximum' else inclusive_input)
                    doc['gamma'] = str(gamma)
                    doc['control_summary']['tested'] = n
                    doc['control_summary']['maximum'] = '-5/2'
                    if rule == 'inclusive_maximum':
                        doc['control_summary']['maximum_multiplicity'] = k
                    result = producer.calibrate(engine, cp, doc)
                    upper = F(result['control_false_gate_upper_exact'])
                    assert 0 <= upper <= 1
                    if k == n:
                        assert upper == 1
                    else:
                        # This direct exact sum, distinct from the producer's
                        # recurrence, establishes returned endpoint >=ideal CP.
                        assert cdf(n, k, upper) <= gamma
                    assert result['frozen_gate'] == {'score_comparator': '>' if not k else '>=', 'threshold_exact': '-5/2'}
                    assert result['confidence']['one_sided_error_exact'] == str(gamma)
                    assert result['confidence']['coverage_at_least_exact'] == str(1-gamma)
                    assert result['confidence']['coverage_scope'] == 'marginal_over_repeated_calibration_samples_not_conditional_on_maximum_or_multiplicity'
                    assert result['numerical_endpoint']['equivalent_k'] == k
                    assert result['numerical_endpoint']['equivalent_k_is_not_a_fixed_gate_binomial_success_count'] is True
                    assert result['native_false_gate_upper'] is None
                    checks += 1
                    if gamma == F(1, 20) and (n, k) in ((12, 0), (12, 1), (12, 12), (59, 0)):
                        summaries.append({'rule': rule, 'n': n, 'k': k, 'upper_exact': str(upper), 'upper_approx': float(upper)})

    # Independent malformed documents; each must fail before returning output.
    invalid = []
    for label, base, path, value in (
        ('zero denominator', strict_input, ('control_summary', 'tested'), 0),
        ('Boolean denominator', strict_input, ('control_summary', 'tested'), True),
        ('float denominator', strict_input, ('control_summary', 'tested'), 12.0),
        ('float score', strict_input, ('control_summary', 'maximum'), 50.0),
        ('zero maximum multiplicity', inclusive_input, ('control_summary', 'maximum_multiplicity'), 0),
        ('oversized maximum multiplicity', inclusive_input, ('control_summary', 'maximum_multiplicity'), 13),
        ('Boolean maximum multiplicity', inclusive_input, ('control_summary', 'maximum_multiplicity'), True),
        ('zero gamma', strict_input, ('gamma',), '0'),
        ('gamma equal one', strict_input, ('gamma',), '1'),
        ('zero-floor gamma', strict_input, ('gamma',), '1/1000000000001'),
        ('learned processor contract', strict_input, ('contract', 'score_pipeline'), 'fit_on_calibration_scores'),
        ('unknown rule', strict_input, ('rule',), 'chosen_after_search'),
        ('omitted truth description', strict_input, ('contract', 'control_population'), ' '),
    ):
        doc = deepcopy(base)
        target = doc
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value
        try:
            producer.calibrate(engine, cp, doc)
        except (ValueError, TypeError, KeyError, ArithmeticError):
            invalid.append(label)
        else:
            raise AssertionError('Malformed input accepted: '+label)
    doc = deepcopy(inclusive_input)
    del doc['control_summary']['maximum_multiplicity']
    try:
        producer.calibrate(engine, cp, doc)
    except (ValueError, TypeError, KeyError, ArithmeticError):
        invalid.append('missing maximum multiplicity')
    else:
        raise AssertionError('Missing maximum multiplicity accepted')

    # Check the file-level parser's duplicate-key refusal independently of CLI.
    try:
        engine.load_json(b'{"gamma":"1/20","gamma":"1/4"}')
    except (ValueError, TypeError, KeyError, ArithmeticError):
        invalid.append('duplicate JSON key')
    else:
        raise AssertionError('Duplicate JSON key accepted')
    return {
        'status': 'passed', 'producer_sha256': PRODUCER_SHA256,
        'comparison_script_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'exact_direct_binomial_endpoint_and_output_checks': checks,
        'malformed_cases_refused': invalid,
        'illustrative_95_percent_results': summaries,
        'scope': 'Independent direct exact binomial sums establish outward endpoints. Arbitrary-distribution strict/inclusive selection coverage is separately proved and finite-audited; no native calibration is supplied.'
    }


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer-dir', type=Path, required=True)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(args.producer_dir, args.repository), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
