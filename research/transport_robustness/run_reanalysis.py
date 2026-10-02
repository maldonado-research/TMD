#!/usr/bin/env python3
"""Replay conditional sensitivity of 160 preserved synthetic confidence outputs."""
from collections import Counter
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path

import transport_robustness as tr

ROOT = Path(__file__).resolve().parent
RADII = ('1', '11/10', '5/4', '3/2', '2')
STATUSES = ('reject', 'compatible_finite', 'compatible_unbounded', 'descriptive_only')
ASSUMPTIONS = dict.fromkeys(tr.ASSUMPTIONS, True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal_enclosure(value, upper=False):
    ratio = F(value)
    with localcontext() as context:
        context.prec = max(40, len(str(abs(ratio.numerator))) + 12)
        context.rounding = ROUND_CEILING if upper else ROUND_FLOOR
        number = Decimal(ratio.numerator) / Decimal(ratio.denominator)
        return str(number.quantize(Decimal('0.000000000001')))


def evaluate_source(source, radius):
    names, _, _ = tr.parse_projection(source)
    return tr.evaluate({'schema_version': 'transport-robustness-1',
                        'assumptions': ASSUMPTIONS,
                        'source_projection': source,
                        'residual_bounds_by_context': {name: tr.symmetric_bounds(radius) for name in names}})


def build_outputs():
    manifest = json.loads((ROOT / 'sources/MANIFEST.json').read_text())
    for entry in manifest['sources']:
        if sha256(ROOT / entry['local_path']) != entry['sha256']:
            raise ValueError('Preserved public source hash mismatch: ' + entry['local_path'])
    source_path = ROOT / 'sources/calibration/repeated_sample_results.json'
    original = json.loads(source_path.read_text())
    if len(original['scenarios']) != 4 or any(len(s['records']) != 40 for s in original['scenarios']):
        raise ValueError('Expected four preserved scenarios with forty records each')
    scenarios, all_thresholds, original_agreements = [], [], 0
    for scenario in original['scenarios']:
        records, status_counts, thresholds = [], {r: Counter() for r in RADII}, []
        for record in scenario['records']:
            source = record['projection_result']
            tr.validate_stored_marginal_arithmetic(source)
            names, original_intervals, _ = tr.parse_projection(source)
            initial = tr.intersection(original_intervals)
            if initial['status'] != record['evaluation_status']:
                raise ValueError('R=1 exact decision differs from preserved reference')
            original_agreements += 1
            frontier = tr.threshold_bracket(original_intervals, bits=80)
            if frontier['status'] in ('certified_bracket', 'exact'):
                lower, upper, ratio = map(F, (frontier['R_lower_exact'], frontier['R_upper_exact'], frontier['power_ratio_exact']))
                if not lower ** 8 <= ratio <= upper ** 8 or upper - lower > F(1, 2**80):
                    raise ArithmeticError('Invalid exact threshold certificate')
                low_status = evaluate_source(source, lower)['status']
                hi_status = evaluate_source(source, upper)['status']
                if hi_status == 'reject' or (lower < upper and low_status != 'reject'):
                    raise ArithmeticError('Threshold endpoints failed exact decision crosscheck')
                frontier['R_lower_decimal_outward_display'] = decimal_enclosure(lower)
                frontier['R_upper_decimal_outward_display'] = decimal_enclosure(upper, upper=True)
                thresholds.append(frontier)
                all_thresholds.append(frontier)
            grid, previous = [], None
            for radius in RADII:
                evaluated = evaluate_source(source, radius)
                status_counts[radius][evaluated['status']] += 1
                adjusted = [tr.parse_interval(c['biological_J_interval']) for c in evaluated['contexts']]
                if previous is not None:
                    for (plo, phi), (lo, hi) in zip(previous, adjusted):
                        if not lo <= plo or (phi is None and hi is not None) or (phi is not None and hi is not None and hi < phi):
                            raise ArithmeticError('Symmetric sensitivity intervals failed nesting')
                previous = adjusted
                grid.append({'R_exact': radius, 'status': evaluated['status'],
                             'shared_biological_J_intersection': evaluated['shared_biological_J_intersection'],
                             'biological_J_intervals': [dict(context=name, **tr.interval_json(interval))
                                                        for name, interval in zip(names, adjusted)]})
            records.append({'original_dataset_index': record['dataset_index'],
                            'original_dataset_seed': record['dataset_seed'],
                            'initial_status': initial['status'],
                            'observable_control_corrected_J_intervals': [dict(context=name, **tr.interval_json(interval))
                                                                        for name, interval in zip(names, original_intervals)],
                            'symmetric_sensitivity_frontier': frontier, 'grid': grid})
        summary = {'records_reused': len(records), 'grid_status_counts': {
            r: {status: status_counts[r][status] for status in STATUSES} for r in RADII}}
        if thresholds:
            summary['threshold_minimum_R_enclosure'] = {
                'lower_exact': str(min(F(t['R_lower_exact']) for t in thresholds)),
                'upper_exact': str(min(F(t['R_upper_exact']) for t in thresholds))}
            summary['threshold_maximum_R_enclosure'] = {
                'lower_exact': str(max(F(t['R_lower_exact']) for t in thresholds)),
                'upper_exact': str(max(F(t['R_upper_exact']) for t in thresholds))}
        scenarios.append({'scenario': scenario['scenario'],
                          'original_sampling_relationship': scenario['sampling_relationship'],
                          'summary': summary, 'records': records})
    result = {'schema_version': 'transport-robustness-reanalysis-1',
              'provenance': 'Reanalysis of all 160 previously stored synthetic results; zero new random datasets and no biological observations.',
              'assumption_interpretation': 'Each R is a hypothetical differential-residual sensitivity bound. Confidence language is conditional on its validity and independent prespecification; neither is established from these data. The threshold is an exploratory sensitivity frontier, not an estimated bound.',
              'source_file': 'sources/calibration/repeated_sample_results.json',
              'source_sha256': sha256(source_path),
              'core_source_sha256': sha256(ROOT / 'transport_robustness.py'),
              'runner_source_sha256': sha256(ROOT / 'run_reanalysis.py'),
              'assumptions_for_conditional_interpretation': ASSUMPTIONS,
              'R_grid_exact': list(RADII),
              'R_definition': 'e_i=(r_1i/r_0i)/(d_1i/d_0i) in [1/R,R]; residual vectors may differ across contexts.',
              'unchanged_R_1_reference_decisions': original_agreements,
              'stored_context_projection_checks': 4 * original_agreements,
              'initial_rejections_with_certified_thresholds': len(all_thresholds),
              'scenarios': scenarios}
    fixture_path = ROOT / 'sources/illustrative_mismatch_projection.json'
    fixture = json.loads(fixture_path.read_text())
    population_checks = []
    for context in fixture['illustrative_population']:
        latent0, latent1 = [list(map(F, context[k])) for k in ('latent_baseline', 'latent_selected')]
        biological = (latent1[1] / latent0[1]) ** 2 / ((latent1[0] / latent0[0]) * (latent1[2] / latent0[2]))
        observed0, observed1 = [list(map(F, context[k])) for k in ('observed_baseline_probabilities', 'observed_selected_probabilities')]
        observable = (observed1[1] / observed0[1]) ** 2 / ((observed1[0] / observed0[0]) * (observed1[2] / observed0[2]))
        e = [F(context['differential_residual_by_route'][route]) for route in tr.ROUTES]
        assert observable == biological * e[1] ** 2 / (e[0] * e[2])
        assert biological == F(fixture['biological_common_J_exact']) == 1
        assert all(F(1, 2) <= value <= 2 for value in e)
        population_checks.append({'context': context['context'], 'biological_J_exact': str(biological),
                                  'observable_J_exact': str(observable), 'identity_verified_exactly': True})
    fixture_base, fixture_robust = (evaluate_source(fixture['source_projection'], r) for r in ('1', '2'))
    assert fixture_base['status'] == 'reject'
    assert fixture_robust['status'] == 'compatible_finite'
    fixture_base['bound_valid_for_constructed_population'] = False
    fixture_base['assumption_interpretation'] = 'The R=1 coverage premise is deliberately false in this counterexample; its nested true declaration is an invalid modeling assumption, not an authenticated fact.'
    fixture_robust['bound_valid_for_constructed_population'] = True
    fixture_robust['assumption_interpretation'] = 'The R=2 differential bound is valid by construction in this illustrative model.'
    robust_common = fixture_robust['shared_biological_J_intersection']
    assert F(robust_common['J_lower_exact']) <= 1 <= F(robust_common['J_upper_exact'])
    example = {'provenance': fixture['provenance'], 'fixture_sha256': sha256(fixture_path),
               'exact_transport_is_false_by_construction': True,
               'illustrative_population_checks': population_checks,
               'R_1_false_exact_transport_conclusion': fixture_base,
               'R_2_correct_bounded_transport_conclusion': fixture_robust,
               'interpretation': 'The biological J is 1 in both contexts. Exact-transport analysis of this chosen count realization rejects spuriously; the valid differential mismatch bound R=2 restores compatibility and contains J=1. This is an arithmetic counterexample, not an empirical frequency study.'}
    return {'reanalysis.json': result, 'mismatch_counterexample.json': example}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Require deterministic replay of existing output bytes')
    args = parser.parse_args()
    outputs = build_outputs()
    for name, value in outputs.items():
        encoded = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
        path = ROOT / 'results' / name
        if args.check:
            if path.read_text() != encoded:
                raise SystemExit('Replay mismatch: ' + name)
        else:
            path.write_text(encoded)
    summary = outputs['reanalysis.json']
    print(json.dumps({'all_preserved_records': summary['unchanged_R_1_reference_decisions'],
                      'thresholds_certified': summary['initial_rejections_with_certified_thresholds'],
                      'deterministic_replay': bool(args.check),
                      'scenario_summaries': {s['scenario']: s['summary'] for s in summary['scenarios']}}, indent=2))


if __name__ == '__main__':
    main()
