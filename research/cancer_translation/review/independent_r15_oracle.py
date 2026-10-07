"""Independent finite rational and primary-source checks; no cancer fit."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def main():
    if sys.flags.optimize:
        raise SystemExit('Independent verification requires ordinary Python')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True)
    ap.add_argument('--source-dir', type=Path, required=True)
    ap.add_argument('--expected-engine-sha256', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    engine = args.package / 'translation_counterexample.py'
    if hashlib.sha256(engine.read_bytes()).hexdigest() != args.expected_engine_sha256:
        raise ValueError('Independent review engine pin differs')
    spec = importlib.util.spec_from_file_location('reviewed_translation', engine)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    counts = {}

    def check(ok, category):
        if not ok:
            raise ValueError('Independent check failed: ' + category)
        counts[category] = counts.get(category, 0) + 1

    cases = 0
    for base in itertools.product(range(1, 5), repeat=3):
        q = tuple(F(v, sum(base)) for v in base)
        for k in (F(1), F(3, 2), F(2), F(5, 2)):
            for x in (F(1, 3), F(2, 3), F(1), F(3, 2), F(3)):
                yield_weights = (x, k, 1/x)
                masses = tuple(F(base[i]) * yield_weights[i] for i in range(3))
                expected = tuple(v / sum(masses) for v in masses)
                calculated = module.endpoint_mixture(q, yield_weights, (1, 1, 1))
                check(calculated == expected, 'independent_mass_normalization')
                check(sum(calculated) == 1 and min(calculated) > 0, 'probability_identity')
                detection = tuple(v/max(yield_weights) for v in yield_weights)
                check(all(0 < v <= 1 for v in detection), 'valid_capture_probabilities')
                check(module.endpoint_mixture(q, (1, 1, 1), detection) == expected,
                      'growth_recovery_expected_mixture_equality')
                amplification = tuple(3*v for v in yield_weights)
                check(min(amplification) >= 1 and max(amplification) <= 16,
                      'expansion_only_mimic_within_declared_cap')
                check(module.endpoint_mixture(q, amplification, (1, 1, 1)) == expected,
                      'common_scale_cancellation')
                check(calculated[1]**2*q[0]*q[2] == k*k*calculated[0]*calculated[2]*q[1]**2,
                      'cross_multiplied_restriction')
                check(module.supply_adjusted_curvature(calculated, q) == k*k,
                      'producer_curvature_vs_independent_identity')
                corrected = tuple(calculated[i]/yield_weights[i] for i in range(3))
                corrected = tuple(v/sum(corrected) for v in corrected)
                check(corrected == q, 'independent_calibration_restores_supply')
                cases += 1

    ledger = json.loads((args.package/'SOURCE_LEDGER.json').read_text())
    check(ledger['actual_request_count'] == 4 and ledger['recorded_response_bytes'] == 631752,
          'source_acquisition_scope')
    expected_dois = {'PMC6298579':'10.1126/science.aau3879',
                     'PMC7612642':'10.1038/s41586-021-03965-7'}
    for source in ledger['primary_sources']:
        path = args.source_dir/(source['pmc']+'.xml')
        data = path.read_bytes()
        check(hashlib.sha256(data).hexdigest() == source['sha256'], 'source_byte_identity')
        check(len(data) == source['bytes'], 'source_size_identity')
        tree = ET.fromstring(data)
        article = tree if tree.tag == 'article' else tree.find('article')
        ids = {n.get('pub-id-type'):n.text for n in article.findall('front/article-meta/article-id')}
        check(ids.get('doi') == expected_dois[source['pmc']] == source['doi'], 'primary_doi_identity')
        paragraphs = [' '.join(''.join(n.itertext()).split()) for n in article.findall('body//p')]
        check(len(paragraphs) == source['body_paragraphs_inspected'], 'body_inventory')
        for anchor in source['anchors']:
            actual = hashlib.sha256(paragraphs[anchor['body_paragraph_index']].encode()).hexdigest()
            check(actual == anchor['normalized_paragraph_sha256'], 'independent_source_anchor')
        permissions = ' '.join(' '.join(''.join(n.itertext()).split()) for n in article.findall('.//permissions'))
        check('text mining' in permissions, 'redistribution_limit_preserved')
        whole = ' '.join(paragraphs)
        if source['pmc'] == 'PMC6298579':
            check('844' in whole and 'nine' in whole and '6,935' in whole, 'human_nested_units')
            check('Methods S1' in whole and 'Methods S5' in whole, 'unacquired_methods_distinguished')
        else:
            check('analogous mechanism of micro-tumor elimination exists in humans is unknown' in whole,
                  'human_translation_unknown')
            check('randomiz' in whole.lower() and 'blind' in whole.lower(), 'design_limits_present')

    frozen = json.loads((args.package/'SYNTHETIC_BENCHMARKS.json').read_text())
    for row in frozen['fixed_supply_growth_or_recovery_mimic']:
        q = tuple(F(v) for v in row['fixed_supply'])
        p = tuple(F(v) for v in row['common_expected_endpoint_mixture'])
        check(p[1]**2*q[0]*q[2] == F(row['J'])*p[0]*p[2]*q[1]**2,
              'frozen_reported_example')
    check(frozen['expected_mixture_equality_is_not_full_count_law_or_first_arrival_equivalence'],
          'expected_composition_scope')
    check(not frozen['cancer_observations_fitted'] and not frozen['clinical_prevention_or_treatment_result'],
          'no_cancer_result')
    result = {'status':'PASS','scope':'independent rational identities and selected primary-source anchors',
              'finite_cases':cases,'checks_by_category':counts,'total_checks':sum(counts.values()),
              'engine_sha256':args.expected_engine_sha256,'reviewer_network_requests':0,
              'biological_fit':False,'external_peer_review':False}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'cases':cases,'checks':result['total_checks']}))


if __name__ == '__main__':
    main()
