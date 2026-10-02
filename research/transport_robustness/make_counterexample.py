#!/usr/bin/env python3
"""Build an illustrative chosen-count mismatch fixture, not a random new dataset.

This calls only the preserved 0.5 CP endpoint and probability-projection routines.
It never calls the old raw-count validator or asserts its false exact-transport
assumption for this mismatch model. Regeneration may change float-proposed CP
endpoints across platforms; stored exact J bounds are the replay reference.
"""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path

from transport_robustness import interval_json

ROOT = Path(__file__).resolve().parent


def normalized(values):
    total = sum(values)
    return [v / total for v in values]


def contrast(selected, baseline):
    ratios = [a / b for a, b in zip(selected, baseline)]
    return ratios[1] ** 2 / (ratios[0] * ratios[2])


def build():
    spec = importlib.util.spec_from_file_location('preserved_cp', ROOT / 'sources/inference/boundary_confidence.py')
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    alpha, tail = F(1, 20), F(1, 960)
    latent = [F(1, 3)] * 3
    controls = [F(1, 2)] * 3
    recovery_rows = ([F(1, 4), F(1), F(1, 4)], [F(1), F(1, 4), F(1)])
    chosen_selected_counts = ([150, 600, 150], [400, 100, 400])
    contexts, facts = [], []
    for index, (selected_recovery, selected_counts) in enumerate(zip(recovery_rows, chosen_selected_counts), 1):
        baseline_observed = normalized([p * r for p, r in zip(latent, controls)])
        selected_observed = normalized([p * r for p, r in zip(latent, selected_recovery)])
        residuals = [r / b for r, b in zip(selected_recovery, controls)]
        mult = residuals[1] ** 2 / (residuals[0] * residuals[2])
        biological_J = contrast(latent, latent)
        observed_J = contrast(selected_observed, baseline_observed)
        assert observed_J == biological_J * mult
        baseline_counts = [300, 300, 300]
        marginal = {
            'baseline': [cp.clopper_pearson(k, 900, tail) for k in baseline_counts],
            'selected': [cp.clopper_pearson(k, 900, tail) for k in selected_counts],
            'baseline_controls': [cp.clopper_pearson(500, 1000, tail) for _ in range(3)],
            'selected_controls': [cp.clopper_pearson(500, 1000, tail) for _ in range(3)],
        }
        result, lo, hi = cp.project_context(marginal)
        name = f'illustrative_context_{index}'
        contexts.append({'context': name, 'marginal_intervals': marginal, **result})
        facts.append({'context': name, 'latent_baseline': list(map(str, latent)),
                      'latent_selected': list(map(str, latent)),
                      'actual_baseline_recovery': list(map(str, controls)),
                      'actual_selected_recovery': list(map(str, selected_recovery)),
                      'baseline_and_selected_control_recovery': list(map(str, controls)),
                      'observed_baseline_probabilities': list(map(str, baseline_observed)),
                      'observed_selected_probabilities': list(map(str, selected_observed)),
                      'differential_residual_by_route': dict(zip(('W', 'A', 'M'), map(str, residuals))),
                      'biological_J_exact': str(biological_J), 'corrected_observable_J_exact': str(observed_J),
                      'baseline_counts': baseline_counts, 'selected_counts': selected_counts,
                      'control_introduced_each_route_branch': 1000,
                      'control_recovered_each_route_branch': 500})
    return {'provenance': 'Illustrative model and chosen count tables, not experimental observations or new Monte Carlo replicates.',
            'sampling_laws': 'Each route-count vector may be one multinomial sample; each control uses a known fixed denominator and one binary recovery per unit.',
            'exact_transport_is_false_by_construction': True,
            'biological_common_J_exact': '1', 'differential_residual_symmetric_bound_R': '2',
            'illustrative_population': facts,
            'source_projection': {'schema_version': '0.5.0', 'nominal_alpha': str(alpha), 'coordinates': 24,
                'per_tail_error_exact': str(tail), 'simultaneous_coverage_lower_bound_exact': str(1-alpha),
                'method': 'Preserved 0.5 scalar CP and observable probability projection only; old raw validator not called.',
                'contexts': contexts}}


if __name__ == '__main__':
    path = ROOT / 'sources/illustrative_mismatch_projection.json'
    path.write_text(json.dumps(build(), indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(path.relative_to(ROOT))
