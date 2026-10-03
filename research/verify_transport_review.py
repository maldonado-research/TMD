#!/usr/bin/env python3
"""Independent review oracle for the public transport-sensitivity extension.

Run beside transport_robustness/. An optional --public-archive path additionally
checks public ZIP bytes and its six original boundary/descriptive fixtures.
This uses a routewise ratio factorization distinct from the production monomial
projection. It writes only the reviewer-owned JSON receipt beside this file.
"""
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / 'transport_robustness'
SOURCE_SHA = '509783c2a67bf70e590b3daca4b7f9706cf4c9a6b578a5e4e318e47939dd819f'
TRACKED = ('transport_robustness.py', 'run_reanalysis.py', 'make_counterexample.py',
           'test_transport_robustness.py', 'sources/calibration/repeated_sample_results.json',
           'sources/illustrative_mismatch_projection.json',
           'results/reanalysis.json', 'results/mismatch_counterexample.json')


def snapshot():
    return {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in TRACKED}


def endpoint_pair(row):
    return F(row['J_lower_exact']), None if row['J_upper_exact'] is None else F(row['J_upper_exact'])


def oracle_interval(context):
    # r_i = t_i*d0_i/(b_i*d1_i), then J = r_A^2/(r_W*r_M).
    rows = context['marginal_intervals']
    lows, highs = [], []
    for i in range(3):
        t, b, d0, d1 = (rows[key][i] for key in
                        ('selected', 'baseline', 'baseline_controls', 'selected_controls'))
        lows.append(F(t['lower']) * F(d0['lower']) / (F(b['upper']) * F(d1['upper'])))
        denominator = F(b['lower']) * F(d1['lower'])
        highs.append(None if denominator == 0 else F(t['upper']) * F(d0['upper']) / denominator)
    lower = F(0) if highs[0] is None or highs[2] is None else lows[1] ** 2 / (highs[0] * highs[2])
    upper = None if highs[1] is None or lows[0] * lows[2] == 0 else highs[1] ** 2 / (lows[0] * lows[2])
    return lower, upper


def status(intervals):
    lower = max(row[0] for row in intervals)
    highs = [row[1] for row in intervals if row[1] is not None]
    upper = min(highs) if highs else None
    return ('descriptive_only' if len(intervals) == 1 else
            'reject' if upper is not None and lower > upper else
            'compatible_unbounded' if lower == 0 or upper is None else 'compatible_finite')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-archive', type=Path)
    args = parser.parse_args()
    initial_hashes = snapshot()
    assert initial_hashes['sources/calibration/repeated_sample_results.json'] == SOURCE_SHA
    spec = importlib.util.spec_from_file_location('reviewed_transport', PACKAGE / 'transport_robustness.py')
    tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tr)

    def evaluate(source, radius):
        return tr.evaluate({'schema_version': 'transport-robustness-1',
                            'assumptions': dict.fromkeys(tr.ASSUMPTIONS, True),
                            'source_projection': source,
                            'residual_bounds_by_context': {
                                c['context']: tr.symmetric_bounds(radius) for c in source['contexts']}})

    old = json.loads((PACKAGE / 'sources/calibration/repeated_sample_results.json').read_text())
    new = json.loads((PACKAGE / 'results/reanalysis.json').read_text())
    counts = dict(records=0, contexts=0, grid_and_api_decisions=0, frontiers=0,
                  counterexample_contexts=0, public_boundary_fixture_evaluations=0)
    assert len(old['scenarios']) == len(new['scenarios']) == 4
    for oldscenario, newscenario in zip(old['scenarios'], new['scenarios']):
        assert oldscenario['scenario'] == newscenario['scenario']
        assert len(oldscenario['records']) == len(newscenario['records']) == 40
        for oldrecord, newrecord in zip(oldscenario['records'], newscenario['records']):
            assert oldrecord['dataset_index'] == newrecord['original_dataset_index']
            assert oldrecord['dataset_seed'] == newrecord['original_dataset_seed']
            source = oldrecord['projection_result']
            intervals = []
            for context in source['contexts']:
                interval = oracle_interval(context)
                assert interval == endpoint_pair(context)
                intervals.append(interval)
                counts['contexts'] += 1
            assert status(intervals) == oldrecord['evaluation_status'] == newrecord['initial_status']
            assert [g['R_exact'] for g in newrecord['grid']] == ['1', '11/10', '5/4', '3/2', '2']
            for grid in newrecord['grid']:
                radius = F(grid['R_exact'])
                adjusted = [(lo / radius ** 4, None if hi is None else hi * radius ** 4)
                            for lo, hi in intervals]
                assert status(adjusted) == grid['status'] == evaluate(source, radius)['status']
                assert adjusted == [endpoint_pair(row) for row in grid['biological_J_intervals']]
                counts['grid_and_api_decisions'] += 1
            frontier = newrecord['symmetric_sensitivity_frontier']
            if status(intervals) == 'reject':
                ratio = max(p[0] for p in intervals) / min(p[1] for p in intervals if p[1] is not None)
                lo, hi = F(frontier['R_lower_exact']), F(frontier['R_upper_exact'])
                assert F(frontier['power_ratio_exact']) == ratio
                assert lo ** 8 <= ratio <= hi ** 8 and hi - lo <= F(1, 2 ** 80)
                assert lo == hi or lo ** 8 < ratio
                counts['frontiers'] += 1
            else:
                assert frontier['status'] == 'already_compatible'
            counts['records'] += 1

    fixture = json.loads((PACKAGE / 'sources/illustrative_mismatch_projection.json').read_text())
    for facts, projection in zip(fixture['illustrative_population'], fixture['source_projection']['contexts']):
        q, p = [list(map(F, facts[key])) for key in ('latent_baseline', 'latent_selected')]
        r0, r1 = [list(map(F, facts[key])) for key in ('actual_baseline_recovery', 'actual_selected_recovery')]
        d = list(map(F, facts['baseline_and_selected_control_recovery']))
        assert all(0 < x <= 1 for x in r0 + r1 + d)
        raw0 = [x * y for x, y in zip(q, r0)]
        raw1 = [x * y for x, y in zip(p, r1)]
        b, t = [x / sum(raw0) for x in raw0], [x / sum(raw1) for x in raw1]
        assert b == list(map(F, facts['observed_baseline_probabilities']))
        assert t == list(map(F, facts['observed_selected_probabilities']))
        e = [y / x for x, y in zip(r0, r1)]  # Control branch probabilities are equal.
        assert e == [F(facts['differential_residual_by_route'][route]) for route in ('W', 'A', 'M')]
        biological = (p[1] / q[1]) ** 2 / ((p[0] / q[0]) * (p[2] / q[2]))
        observed = (t[1] / b[1]) ** 2 / ((t[0] / b[0]) * (t[2] / b[2]))
        assert biological == 1 and observed == e[1] ** 2 / (e[0] * e[2])
        lo, hi = oracle_interval(projection)
        assert lo <= observed <= hi and lo / 16 <= 1 <= hi * 16
        counts['counterexample_contexts'] += 1
    assert evaluate(fixture['source_projection'], 1)['status'] == 'reject'
    assert evaluate(fixture['source_projection'], 2)['status'] == 'compatible_finite'

    public_archive_verified = False
    if args.public_archive:
        with zipfile.ZipFile(args.public_archive) as archive:
            prefix = 'research_extension_0_5_0/'
            assert archive.read(prefix + 'calibration/repeated_sample_results.json') == (
                PACKAGE / 'sources/calibration/repeated_sample_results.json').read_bytes()
            for name in archive.namelist():
                if '/inference/results/' not in name or not name.endswith('_result.json'):
                    continue
                source = json.loads(archive.read(name))
                baseline = evaluate(source, 1)
                if source['decision'] == 'not_evaluable_one_context':
                    assert baseline['status'] == 'descriptive_only'
                else:
                    assert (baseline['status'] == 'reject') == (source['decision'] == 'reject_shared_theta')
                intervals = [oracle_interval(context) for context in source['contexts']]
                for radius in (F(1), F(2)):
                    adjusted = [(lo / radius ** 4, None if hi is None else hi * radius ** 4)
                                for lo, hi in intervals]
                    assert status(adjusted) == evaluate(source, radius)['status']
                    counts['public_boundary_fixture_evaluations'] += 1
            public_archive_verified = True
    final_hashes = snapshot()
    assert initial_hashes == final_hashes, 'Reviewed files changed during independent verification'
    result = {'status': 'pass', 'scope': 'Independent projection, API, frontier and constructed-model checks; source sampling laws and transport bounds remain assumptions.',
              'public_archive_member_byte_identity_verified': public_archive_verified,
              'independent_checks': counts, 'source_hashes': final_hashes,
              'reviewer_oracle_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT / 'TRANSPORT_CODE_REVIEW_RECEIPT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
