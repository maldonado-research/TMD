"""Original strict CSV audit. No source-author program is executed.

Run with Python standard library. The universe and complement convention are
read from the pinned munging.R source; this does not authenticate its execution.
Malformed records remain unknown. Comparisons are source-file disagreements,
not a claim that the authors' published analyses are erroneous.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
receipt = json.loads((P / 'data_receipt.json').read_text())
for source in receipt:
    data = (P / source['name']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == source['sha256']
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    assert hashlib.sha1(blob).hexdigest() == source['git_blob_sha1']

W = {f'{a}{i}' for a in 'BCDEFGHIJK' for i in range(2, 8)}
masks, issues, duplicates = {}, [], []
for suffix in ['none', 'single', 'double']:
    path = P / f'1ul_individual_{suffix}.csv'
    with path.open(newline='') as handle:
        raw = list(csv.reader(handle))
    header = raw[0]
    for line, values in enumerate(raw[1:], 2):
        row = dict(zip(header, values))
        treatment = {'none': 'none', 'double': 'rifampicin+nalidixic acid'}.get(suffix, row.get('antibiotic'))
        key = (treatment, row['volume'], row['day'], row['pmutS'], row['medium'])
        if key in masks:
            duplicates.append(list(key))
            raise ValueError(f'Duplicate assay key: {key}')
        value = row['wells']
        tokens = value.lstrip('-').split(';') if value not in ['ALL', '0'] else []
        invalid = sorted(set(tokens) - W)
        repeated = sorted(x for x, n in collections.Counter(tokens).items() if n > 1)
        if len(values) != len(header) or invalid or repeated:
            issues.append({'file': path.name, 'line': line, 'key': list(key),
                           'header_fields': len(header), 'row_fields': len(values),
                           'invalid_tokens': invalid, 'repeated_tokens': repeated,
                           'raw_fields': values})
            masks[key] = None
        elif value == 'ALL':
            masks[key] = W.copy()
        elif value == '0':
            masks[key] = set()
        else:
            masks[key] = W - set(tokens) if value.startswith('-') else set(tokens)

frequency_map, differences, missing = {}, [], []
comparisons = 0
for suffix in ['none', 'single', 'double']:
    with (P / f'1ul_aggregate_{suffix}.csv').open(newline='') as handle:
        for row in csv.DictReader(handle):
            treatment = row['antibiotic']
            frequency_map[treatment] = dict(zip(['0', '10', '25', '50'], list(row)[5:]))
            for rank, frequency in frequency_map[treatment].items():
                medium = {'MH': 'MH', 'Nal': 'nal', 'Rif': 'rif', 'Nal + Rif': 'nal+rif'}[row['resistance']]
                key = (treatment, row['volume'], row['day'], rank, medium)
                mask = masks[key]
                if row[frequency] == 'NA':
                    missing.append({'key': list(key)})
                elif mask is not None:
                    comparisons += 1
                    if len(mask) != int(row[frequency]):
                        differences.append({'key': list(key), 'individual_positive_wells': len(mask),
                                            'aggregate_count': int(row[frequency])})

endpoints = []
for treatment in frequency_map:
    for rank in ['0', '10', '25', '50']:
        mask = {medium: masks[(treatment, '1', '6', rank, medium)]
                for medium in ['MH', 'rif', 'nal', 'nal+rif']}
        states = collections.Counter()
        patterns = collections.Counter()
        if all(value is not None for value in mask.values()):
            for well in sorted(W):
                pattern = ''.join(str(int(well in mask[medium])) for medium in ['MH', 'rif', 'nal', 'nal+rif'])
                patterns[pattern] += 1
                state = ('double' if well in mask['nal+rif'] else
                         'mixed' if well in mask['nal'] and well in mask['rif'] else
                         'rif' if well in mask['rif'] else
                         'nal' if well in mask['nal'] else 'no_detected_resistance')
                states[state] += 1
        endpoints.append({'treatment': treatment, 'nominal_frequency_label': rank,
                          'frequency_header_from_aggregate': frequency_map[treatment][rank],
                          'declared_well_frame': 60,
                          'positive_well_counts': {key: len(value) if value is not None else None for key, value in mask.items()},
                          'simple_states': dict(states) if states else None,
                          'assay_patterns_MH_rif_nal_combination': dict(patterns) if patterns else None})

output = {'source_commit': '907311849f5610f114ed3ef99f5de73e51349b67',
          'assay_rows': len(masks), 'valid_assay_rows': sum(x is not None for x in masks.values()),
          'duplicate_assay_keys': duplicates, 'parse_issues': issues,
          'nonmissing_comparable_counts': comparisons, 'count_disagreements': differences,
          'aggregate_missing': missing, 'frequency_map': frequency_map, 'endpoints': endpoints,
          'scope': 'Structural and descriptive source audit only. No silent source correction, inferential fit, author-code execution, biological-origin census, or publication replay.'}
(P / 'structural_audit.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps({'assay_rows': len(masks), 'parse_issues': len(issues),
                  'comparisons': comparisons, 'count_disagreements': len(differences),
                  'aggregate_missing': len(missing), 'complete_endpoint_cells': sum(x['simple_states'] is not None for x in endpoints)}))
