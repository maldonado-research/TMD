#!/usr/bin/env python3
"""Check pinned archived-code anchors and two declared constructed audit examples.

This does not fetch sources, execute the R workflow or measure biological data.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure-dir', type=Path, required=True,
                        help='External archived Figures directory containing the pinned R files')
    args = parser.parse_args()
    sources = {
        'Figure2.R': {
            'sha256': '0ceea1de01d6fb30507a492f6160f72b14ac45979f5bf6984d2905494115451e',
            'anchors': {71: 'IRanges(start = Callable[,2]', 1374: 'Metadata$Type == "PTA"',
                        1383: 'Previous_Clone <-', 1395: '$VAF > MinimalVAF',
                        1441: '"FAIL_QC"', 1442: '"LOW_COV"', 1449: '"FAIL_QC"',
                        1450: '"LOW_COV"', 1451: '<- "PASS"', 1459: '"17:"',
                        1501: 'levels = c("ABSENT", "LOW_COV", "FAIL_QC","FAIL","PASS")',
                        1529: 'mean = mean', 1555: 'Overview_CloneVariants$Variant[',
                        1557: '%in% CallableVariants', 1566: '%in% CallableVariants',
                        1584: 'levels = c("ABSENT", "LOW_COV", "FAIL_QC","FAIL","PASS")',
                        1609: 'mean = mean'}},
        'GeneralFunctions.R': {
            'sha256': '0687349ea90c4db697e505f3ae4f17e1616b880ff8ff473296798ca4cb815e8c',
            'anchors': {72: '$VAF < VAF_threshold', 73: '$PTAprob > PTAprobCutoff[cutoff]'}}
    }
    source_results = {}
    for name, expected in sources.items():
        data = (args.figure_dir / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == expected['sha256'], f'{name}: source hash mismatch'
        lines = data.decode('utf-8').splitlines()
        for line, token in expected['anchors'].items():
            assert token in lines[line - 1], f'{name}:{line}: anchor mismatch'
        source_results[name] = {'sha256': digest, 'anchor_count': len(expected['anchors'])}

    rows = [
        {'sample': 'A', 'variant': 'v', 'PTATO': 'PASS', 'SCAN2': 'PASS'},
        {'sample': 'B', 'variant': 'v', 'PTATO': 'LOW_COV', 'SCAN2': 'PASS'},
        {'sample': 'B', 'variant': 'w', 'PTATO': 'FAIL', 'SCAN2': 'ABSENT'},
    ]
    samples = sorted({r['sample'] for r in rows})
    reference = {s: {r['variant'] for r in rows if r['sample'] == s} for s in samples}
    eligible = {s: {r['variant'] for r in rows if r['sample'] == s and r['PTATO'] in ('PASS', 'FAIL')}
                for s in samples}
    union = set().union(*eligible.values())
    literal = {s: reference[s] & union for s in samples}
    excess = {s: literal[s] - eligible[s] for s in samples}
    for s in samples:
        others = set().union(*(eligible[t] for t in samples if t != s))
        assert excess[s] == (reference[s] - eligible[s]) & others
        assert eligible[s] <= literal[s]
        assert len(literal[s]) == len(eligible[s]) + len(excess[s])
    assert excess == {'A': set(), 'B': {'v'}}
    scan_pass = {}
    for label, frame in [('literal', literal), ('local', eligible)]:
        chosen = [r for r in rows if r['sample'] == 'B' and r['variant'] in frame['B']]
        scan_pass[label] = str(Fraction(sum(r['SCAN2'] == 'PASS' for r in chosen), len(chosen)))
    assert scan_pass == {'literal': '1/2', 'local': '0'}

    counts = {'A': {'PASS': 1, 'FAIL': 0}, 'B': {'PASS': 0, 'FAIL': 3}}
    totals = {s: sum(c.values()) for s, c in counts.items()}
    m = len(totals)
    assert all(n > 0 for n in totals.values())
    means = {}
    for category in ('PASS', 'FAIL'):
        frequencies = [Fraction(counts[s][category], totals[s]) for s in counts]
        positive = [f for f in frequencies if f > 0]
        k = len(positive)
        sparse = sum(positive, Fraction()) / k
        completed = sum(frequencies, Fraction()) / m
        pooled = Fraction(sum(c[category] for c in counts.values()), sum(totals.values()))
        assert sparse == Fraction(m, k) * completed
        means[category] = {'m': m, 'k': k, 'sparse': str(sparse),
                           'zero_completed': str(completed), 'pooled': str(pooled)}
    sums = {key: str(sum(Fraction(means[c][key]) for c in means))
            for key in ('sparse', 'zero_completed', 'pooled')}
    assert sums == {'sparse': '2', 'zero_completed': '1', 'pooled': '1'}
    receipt = {
        'record_id': 'R000025', 'status': 'PASS',
        'scope': 'Pinned source-anchor verification and exact arithmetic for two constructed rule checks only',
        'scientific_network_requests': 0, 'biological_variant_rows_acquired': 0,
        'actual_affected_study_rows': None, 'numerical_figure_replay': False,
        'sources': source_results,
        'constructed_membership': {'reference': {s: sorted(reference[s]) for s in samples},
                                   'local': {s: sorted(eligible[s]) for s in samples},
                                   'literal': {s: sorted(literal[s]) for s in samples},
                                   'excess': {s: sorted(excess[s]) for s in samples},
                                   'B_SCAN2_PASS_fraction': scan_pass},
        'constructed_category_means': means, 'constructed_category_sums': sums,
        'native_origin_truth_inferred': False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
