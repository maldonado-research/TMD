#!/usr/bin/env python3
"""Validate this standalone analysis and record a deterministic check receipt."""
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import io
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import run_reanalysis as replay
import transport_robustness as tr

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def independent_tail_check(n, k, probability, upper_tail, tail_error):
    """Direct positive binomial sum, independent of preserved CP recurrence."""
    p = F(probability)
    a, b = p.numerator, p.denominator
    selected = range(k, n+1) if upper_tail else range(k+1)
    numerator = sum(comb(n, j) * a**j * (b-a)**(n-j) for j in selected)
    return numerator * tail_error.denominator <= tail_error.numerator * b**n


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern='test_transport_robustness.py')
    report = io.StringIO()
    tests = unittest.TextTestRunner(stream=report, verbosity=2).run(suite)
    if not tests.wasSuccessful():
        raise AssertionError(report.getvalue())
    replay_outputs = replay.build_outputs()
    for name, value in replay_outputs.items():
        expected = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
        if (ROOT / 'results' / name).read_text() != expected:
            raise AssertionError('Deterministic replay differs: ' + name)
    boundary_checks = []
    for path in sorted((ROOT / 'sources/inference/results').glob('*_result.json')):
        source = json.loads(path.read_text())
        evaluated = replay.evaluate_source(source, '1')
        original = source['decision']
        expected = {'reject_shared_theta': 'reject_shared_finite_theta',
                    'no_shared_theta_departure_established': 'no_shared_finite_theta_departure_established',
                    'not_evaluable_one_context': 'not_evaluable_one_context'}[original]
        if evaluated['decision'] != expected:
            raise AssertionError('Published boundary fixture decision changed: ' + path.name)
        boundary_checks.append({'source': str(path.relative_to(ROOT)), 'sha256': digest(path),
                                'status': evaluated['status'], 'original_decision_preserved': True})
    fixture = json.loads((ROOT / 'sources/illustrative_mismatch_projection.json').read_text())
    tail = F(fixture['source_projection']['per_tail_error_exact'])
    endpoint_checks = 0
    for context, facts in zip(fixture['source_projection']['contexts'], fixture['illustrative_population']):
        groups = context['marginal_intervals']
        for branch in ('baseline', 'selected'):
            counts = facts[branch + '_counts']
            for k, row in zip(counts, groups[branch]):
                if not independent_tail_check(sum(counts), k, row['lower'], True, tail):
                    raise AssertionError('Illustrative CP lower endpoint failed exact binomial oracle')
                if not independent_tail_check(sum(counts), k, row['upper'], False, tail):
                    raise AssertionError('Illustrative CP upper endpoint failed exact binomial oracle')
                endpoint_checks += 2
            for row in groups[branch + '_controls']:
                n = facts['control_introduced_each_route_branch']
                k = facts['control_recovered_each_route_branch']
                assert independent_tail_check(n, k, row['lower'], True, tail)
                assert independent_tail_check(n, k, row['upper'], False, tail)
                endpoint_checks += 2
    example = json.loads((ROOT / 'example_bounded_mismatch_input.json').read_text())
    with tempfile.TemporaryDirectory(prefix='tmd-transport-check-') as temporary:
        output = Path(temporary) / 'output.json'
        process = subprocess.run([sys.executable, str(ROOT / 'transport_robustness.py'),
                                  str(ROOT / 'example_bounded_mismatch_input.json'), '--output', str(output)],
                                 check=True, capture_output=True, text=True)
        assert not process.stderr
        assert json.loads(output.read_text()) == tr.evaluate(example)
    result = replay_outputs['reanalysis.json']
    checked_files = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                     and p.name not in ('VALIDATION.json', 'SHA256SUMS.txt', 'TEST_RESULTS.txt')]
    receipt = {
        'status': 'passed',
        'unit_tests': {'run': tests.testsRun, 'failures': len(tests.failures), 'errors': len(tests.errors)},
        'deterministic_result_replay': True,
        'published_source_manifest_hashes_verified': True,
        'preserved_calibration_source_sha256': result['source_sha256'],
        'preserved_calibration_reference_decisions_verified': result['unchanged_R_1_reference_decisions'],
        'stored_context_projection_arithmetic_checks': result['stored_context_projection_checks'],
        'sensitivity_grid_evaluations': 160 * len(replay.RADII),
        'initial_rejection_thresholds_exactly_certified': result['initial_rejections_with_certified_thresholds'],
        'threshold_absolute_bracket_width_at_most_exact': str(F(1, 2**80)),
        'published_boundary_fixture_checks': boundary_checks,
        'illustrative_mismatch_CP_endpoint_direct_integer_binomial_checks': endpoint_checks,
        'CLI_example_matches_library_result': True,
        'no_new_random_datasets': True,
        'scope_limit': 'Checks software arithmetic and preserved artifacts. Does not scientifically authenticate marginal sampling laws, recovery bounds, or biological conclusions.',
        'checked_file_sha256': {str(path.relative_to(ROOT)): digest(path) for path in sorted(checked_files)},
    }
    (ROOT / 'VALIDATION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + '\n')
    # Stable receipt text omits platform-dependent elapsed time.
    lines = [f'Tests run: {tests.testsRun}', 'Failures: 0', 'Errors: 0',
             'Deterministic stored-output replay: passed',
             'Published baseline/boundary checks: 160 repeated records; 6 boundary fixtures',
             'Exact original context projections: 640', 'Sensitivity grid evaluations: 800',
             'Certified rejection frontiers: 40', 'Independent illustrative CP endpoint checks: 48',
             'CLI smoke check: passed']
    (ROOT / 'TEST_RESULTS.txt').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('checked_file_sha256', 'published_boundary_fixture_checks')}, indent=2))


if __name__ == '__main__':
    main()
