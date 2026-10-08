"""Compare the producer with the independently frozen exact design oracle."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True

BASE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Independent verification requires ordinary Python')
    spec = importlib.util.spec_from_file_location('producer_event_engine', args.engine)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    blind = json.loads((BASE / 'R20_BLIND_ORACLE.json').read_text())
    checks = 0
    def same(actual, expected):
        nonlocal checks
        if actual != expected:
            raise AssertionError((actual, expected))
        checks += 1
    for case in blind['cases']:
        n, events = case['n'], case['events']
        law = {int(mask): F(prob) for mask, prob in case['law'].items()}
        expected = case['expected']
        actual = mod.event_summary(n, law, events)
        same(tuple(actual['descendant_call_marginals']), tuple(F(expected['descendant_marginals'][str(i)]) for i in range(n)))
        for name in events:
            same(actual['event_inclusion'][name], F(expected['event_inclusion'][name]))
            for other in events:
                same(actual['joint_event_inclusion'][(name, other)], F(expected['joint_inclusion'][name][other]))
            ps = [F(expected['descendant_marginals'][str(i)]) for i in events[name]]
            bounds = mod.frechet_union_bounds(ps)
            # Field adaptation will be locked only to documented producer names.
            lower, upper, independent = (F(expected['frechet'][name][key]) for key in ['lower', 'upper', 'independent'])
            same(bounds['lower'], lower)
            same(bounds['upper'], upper)
            same(bounds['value_if_independent'], independent)
            witness = mod.extremal_union_laws(ps)
            for label, target in [('lower_union_law', lower), ('upper_union_law', upper)]:
                joint = witness[label]
                same(sum(joint.values(), F()), F(1))
                same(sum((p for mask, p in joint.items() if mask), F()), target)
                for i, marginal in enumerate(ps):
                    same(sum((p for mask, p in joint.items() if mask // (2 ** i) % 2), F()), marginal)
        same(actual['expected_observed_carrier_copy_count'], F(expected['expected_inherited_copies']))
        same(actual['expected_observed_distinct_event_count'], F(expected['expected_detected_events']))
        if expected['ht'] is None:
            try:
                mod.ht_summary(n, law, events)
            except (ValueError, TypeError):
                checks += 1
            else:
                raise AssertionError('Zero-inclusion catalogue was estimated')
        else:
            ht = mod.ht_summary(n, law, events)
            same(ht['fixed_catalogue_size'], expected['ht']['catalogue_size'])
            same(ht['design_expectation'], F(expected['ht']['expectation']))
            same(ht['design_variance'], F(expected['ht']['variance']))
            for mask, value in expected['ht']['values'].items():
                same(mod.ht_value(n, law, events, int(mask)), F(value))
    enumeration_checks = checks
    guards = [
        lambda: mod.event_catalogue(9, {'e': [8]}, True),
        lambda: mod.event_catalogue(True, {'e': [0]}, True),
        lambda: mod.event_summary(True, {0: 1}, {}),
        lambda: mod.event_summary(1, {True: 1}, {}),
        lambda: mod.event_summary(1, {0: F(1, 2)}, {}),
        lambda: mod.event_summary(1, {0: -1, 1: 2}, {}),
        lambda: mod.event_summary(1, {0: 1.0}, {}),
        lambda: mod.event_summary(1, {0: True}, {}),
        lambda: mod.event_summary(1, {0: 1}, {'x': [None]}),
        lambda: mod.event_summary(1, {0: 1}, {'x': [0, 0]}),
        lambda: mod.event_summary(1, {0: 1}, {'x': [0]}, ancestry_known=None),
        lambda: mod.ht_summary(1, {0: 1}, {'x': [0]}),
        lambda: mod.ht_value(1, {0: 0, 1: 1}, {'x': [0]}, 0),
        lambda: mod.ht_value(1, {0: 1}, {}, True),
        lambda: mod.frechet_union_bounds([F(-1, 2)]),
        lambda: mod.frechet_union_bounds([F(3, 2)]),
        lambda: mod.event_summary(1, {0: F(2**32 - 1, 2**32), 1: F(1, 2**32)}, {'x': [0]}),
    ]
    for guard in guards:
        try:
            guard()
        except (ValueError, TypeError):
            checks += 1
        else:
            raise AssertionError('Independent admission guard failed')
    law = {0: F(2**32 - 2, 2**32 - 1), 1: F(1, 2**32 - 1)}
    boundary = mod.ht_summary(1, law, {'x': [0]})
    same(boundary['design_expectation'], F(1))
    same(boundary['design_variance'], F(2**32 - 2))
    same(mod.ht_value(1, law, {'x': [0]}, 1), F(2**32 - 1))
    receipt = {'status': 'PASS_BLIND_EXACT_ORACLE_COMPARISON', 'cases': blind['case_count'], 'enumerated_mask_rows': blind['mask_rows'], 'blind_comparison_checks': enumeration_checks, 'independent_admission_guards': len(guards), 'valid_32bit_boundary_checks': 3, 'total_checks': checks, 'scope': 'Conditional fixed-event, supplied carrier and all-target true-call design; no biological fit or sampling confidence claim.'}
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
