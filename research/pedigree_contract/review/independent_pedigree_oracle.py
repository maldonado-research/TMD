"""Reconstruct the declared toy ledger independently of its producer validator."""
from pathlib import Path
from fractions import Fraction as F
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Independent verification requires ordinary Python')
    ledger = json.loads((args.candidate / 'SYNTHETIC_LEDGER.json').read_text())
    cells = {cell['cell_id']: cell for cell in ledger['cells']}
    children = {name: [] for name in cells}
    for name, cell in cells.items():
        parent = cell['parent_cell_id']
        if parent is not None:
            children[parent].append(name)
    roots = [name for name, cell in cells.items() if cell['parent_cell_id'] is None]
    frontier = list(roots)
    ancestry = {name: {name} for name in roots}
    while frontier:
        parent = frontier.pop(0)
        for child in children[parent]:
            if child in ancestry:
                raise ValueError('Repeated/cyclic pedigree node')
            ancestry[child] = ancestry[parent] | {child}
            frontier.append(child)
    if set(ancestry) != set(cells):
        raise ValueError('Unreachable pedigree nodes')
    checks = 0
    def check(actual, expected):
        nonlocal checks
        if actual != expected:
            raise AssertionError((actual, expected))
        checks += 1
    check(len(roots), 1)
    check(len(cells), 13)
    check(sum(len(v) == 2 for v in children.values()), 6)
    check(sum(len(v) == 0 for v in children.values()), 7)
    check(len(cells), 1 + 2 * len(ledger['divisions']))
    exposure = sum((F(cell['stop_time']) - F(cell['birth_time']) for cell in cells.values()), F())
    check(exposure, F(20))
    stages = {name: sum(cell['stages'][name] for cell in cells.values()) for name in ['available_at_collection', 'isolated', 'outgrown', 'sequenced']}
    check(tuple(stages.values()), (5, 4, 3, 3))
    terminal_unknown = [name for name in cells if not children[name] and cells[name]['genotype_status'] == 'unknown']
    check(len(terminal_unknown), 4)
    check(sum(cell['stop_reason'] == 'death' for cell in cells.values()), 1)
    check(sum(cell['stop_reason'] == 'lost_tracking' for cell in cells.values()), 1)
    samples = {cell['sample_id']: name for name, cell in cells.items() if cell['sample_id'] is not None}
    positives = {}
    for call in ledger['variant_calls']:
        if call['call_state'] == 'toy_validated_alternate':
            positives.setdefault(call['variant_tag'], []).append(samples[call['sample_id']])
    check({tag: len(nodes) for tag, nodes in positives.items()}, {'TOY_VARIANT_A': 2, 'TOY_VARIANT_B': 1})
    common = set.intersection(*(ancestry[node] for node in positives['TOY_VARIANT_A']))
    check(common, {'F', 'A'})
    check('A' in ancestry[samples['S21']], False)
    check(len(ledger['synthetic_truth_only']), 2)
    check(sum(len(nodes) for nodes in positives.values()), 3)
    check(ledger['design_status']['biological_admission'], 'blocked')
    check(all(ledger['design_status'][name] is None for name in ['actual_axis', 'actual_system', 'actual_count_law', 'actual_route_catalog', 'actual_event_inclusion_predicate', 'actual_error_stopping_plan', 'actual_partner_protocol']), True)
    check(ledger['design_status']['actual_registry_fields_resolved'], 0)
    result = {'status': 'PASS_INDEPENDENT_TOY_PEDIGREE_ENUMERATION', 'checks': checks, 'tracked_cells': len(cells), 'optical_divisions': len(ledger['divisions']), 'terminal_cells': 7, 'tracked_cell_time': str(exposure), 'collection_stages': stages, 'terminal_unknown_genotypes': len(terminal_unknown), 'detected_alternate_copies': 3, 'toy_supported_origin_hypotheses': 1, 'leaf_ambiguous_variants': 1, 'synthetic_true_origin_count': 2, 'truth_is_known_only_in_simulation': True, 'actual_parameters_resolved': 0, 'mutation_rate_or_event_inclusion_estimated': False}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
