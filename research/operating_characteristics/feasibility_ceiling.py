#!/usr/bin/env python3
"""Independent pre-outcome score-ceiling projection; uses existing certified logs.

Reads a plan or score document. Does not read outcomes, edit the frozen plan,
change the score engine, fit forecasts, or issue an inferential certificate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path


ENGINE_PATH = Path(__file__).resolve().parents[1] / 'certified_score' / 'certified_score.py'


def load_engine(path=ENGINE_PATH):
    spec = importlib.util.spec_from_file_location('ceiling_certified_score', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def score_ceilings(plan, engine=None):
    """Enclose each comparator's maximum expected gain over all truth simplices.

    The maximizing truth can differ by context. The resulting necessary
    conditions do not jointly characterize feasibility of all comparisons.
    """
    engine = load_engine() if engine is None else engine
    parsed = engine.validate_plan(plan)
    table = engine.coefficient_table(parsed)
    result = {}
    for name in parsed['names']:
        low = high = Fraction(0)
        rows = []
        for row in parsed['rows']:
            intervals = table[row['id']][name]
            max_lower = max(a for a, _ in intervals)
            max_upper = max(b for _, b in intervals)
            low += row['weight'] * max_lower
            high += row['weight'] * max_upper
            rows.append({
                'id': row['id'],
                'weight_exact': str(row['weight']),
                'maximum_gain_enclosure_exact': [str(max_lower), str(max_upper)],
                'forecasts_exactly_identical': row['tmd'] == row['comparators'][name],
            })
        impossible = high <= parsed['success']
        result[name] = {
            'ceiling_enclosure_exact': [str(low), str(high)],
            'strict_success_precluded_by_ceiling': impossible,
            'status': ('pre_outcome_gate_unattainable_for_this_comparator'
                       if impossible else 'ceiling_does_not_rule_out_gate'),
            'contexts': rows,
        }
    return {
        'status': 'pre_outcome_arithmetic_diagnostic_not_a_score_decision',
        'plan_sha256': engine.plan_sha256(plan),
        'success_threshold_exact': str(parsed['success']),
        'all_comparator_success_precluded': any(
            v['strict_success_precluded_by_ceiling'] for v in result.values()),
        'comparators': result,
        'limits': [
            'Uses only frozen forecasts, weights, threshold and log precision; no outcomes.',
            'Passing this necessary condition does not establish joint feasibility or power.',
            'Unattainability is not a failure certificate, model rejection, or unevaluable input.',
            'An overlapping numerical enclosure leaves the ceiling diagnostic unresolved.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    engine = load_engine()
    doc = engine.strict_json(args.input.read_text())
    result = score_ceilings(doc.get('plan', doc), engine)
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
