"""Replay aggregate paired-call counts in Ji et al. 2025 peach flower Tables S2 and S5."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from openpyxl import load_workbook


SOURCES = {
    'S2': ('016', 'b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4'),
    'S5': ('019', 'a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394'),
}


def load_sheet(path, key):
    suffix, expected = SOURCES[key]
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected:
        raise ValueError(f'Unexpected {key} SHA-256')
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(workbook[f'{key}_Table'].values)
    finally:
        workbook.close()
    return rows, {
        'url': f'https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s{suffix}.xlsx',
        'bytes': len(data), 'sha256': digest,
    }


def replay(s2_path, s5_path):
    s2, s2_source = load_sheet(s2_path, 'S2')
    s5, s5_source = load_sheet(s5_path, 'S5')
    if s2[4][:2] != ('ID', 'SampleLocation') or s2[4][5:7] != ('Ref', 'Alt'):
        raise ValueError('Unexpected candidate-key header')
    if s5[3][:3] != ('Pair', 'Subsample', 'Name'):
        raise ValueError('Unexpected split-table header')
    key_rows = [r for r in s2[5:] if r[1] == 'Flower#2']
    alleles = {r[0]: r[5:7] for r in key_rows}
    sites = [x for x in s5[3][3:] if x is not None]
    if len(key_rows) != len(set(sites)) or len(sites) != len(set(sites)) or set(sites) != set(alleles):
        raise ValueError('The identified flower sites do not join one-to-one')
    pairs = {}
    for r in s5[4:]:
        if r[1] not in ('a', 'b'):
            continue
        pair, member = r[:2]
        members = pairs.setdefault(pair, {})
        if member in members:
            raise ValueError('Duplicate pair member')
        members[member] = r[3:3 + len(sites)]
    if len(pairs) != 20 or any(set(m) != {'a', 'b'} for m in pairs.values()):
        raise ValueError('Split roster differs from Figure 2')
    outcomes = Counter()
    intersections, unions = [], []
    for j, site in enumerate(sites):
        ref, alt = alleles[site]
        if ref == alt or ref is None or alt is None:
            raise ValueError('Missing or identical source reference and alternative')
        site_counts = Counter()
        for member in pairs.values():
            a, b = member['a'][j], member['b'][j]
            if a not in (ref, alt) or b not in (ref, alt):
                raise ValueError('Unexpected or missing categorical call')
            site_counts[(a == alt, b == alt)] += 1
        outcomes.update(site_counts)
        both, neither = site_counts[(True, True)], site_counts[(False, False)]
        intersections.append(both)
        unions.append(len(pairs) - neither)
        # S5's footer independently tabulates both matching categories for each site.
        if both != (s5[47][j + 3] or 0) or neither != (s5[46][j + 3] or 0):
            raise ValueError('Decoded pair calls disagree with a per-site source subtotal')
        single = (s5[48][j + 3] or 0) + (s5[49][j + 3] or 0)
        if single != len(pairs) - both - neither:
            raise ValueError('Per-site source discordance subtotal differs')
    both = outcomes[True, True]
    a_only, b_only = outcomes[True, False], outcomes[False, True]
    neither = outcomes[False, False]
    total = len(pairs) * len(sites)
    union = both + a_only + b_only
    defined_site_ratios = [Fraction(i, u) for i, u in zip(intersections, unions) if u]
    all_pairs_sites = [(i, u) for i, u in zip(intersections, unions) if u == len(pairs)]
    wide_i = sum(i for i, u in all_pairs_sites)
    wide_u = sum(u for i, u in all_pairs_sites)
    source_classes = {r[1]: r[2] for r in s5[46:51]}
    if (source_classes['Total'], source_classes['True Positives'], source_classes['True Negatives']) != (total, both, neither):
        raise ValueError('Worksheet summary disagrees with call-table totals')
    return {
        'article': 'https://doi.org/10.1371/journal.pgen.1011829',
        'source_workbooks': {'S2': s2_source, 'S5': s5_source},
        'frame': {'flower': 2, 'published_flower_sites': len(sites), 'split_tissue_pairs': len(pairs),
                  'unit': 'One ascertained flower site evaluated in both subsamples of one tissue.'},
        'pair_by_site_calls': {'both_positive': both, 'a_only_positive': a_only,
                               'b_only_positive': b_only, 'neither_positive': neither, 'total': total},
        'agreement': {'matching_calls_over_all': f'{both + neither}/{total}',
                      'both_positive_over_either_positive': f'{both}/{union}',
                      'b_positive_given_a_positive': f'{both}/{both + a_only}',
                      'a_positive_given_b_positive': f'{both}/{both + b_only}'},
        'across_sites': {
            'site_overlap_histogram': [
                {'both_positive_pairs': i, 'either_positive_pairs': u, 'number_of_sites': n}
                for (i, u), n in sorted(Counter(zip(intersections, unions)).items())
            ],
            'no_positive_in_split_tissues': len(sites) - len(defined_site_ratios),
            'at_least_one_positive_in_split_tissues': len(defined_site_ratios),
            'at_least_one_pair_with_both_positive': sum(i > 0 for i in intersections),
            'mean_intersection_over_union_weighting_each_nonempty_site_equally': str(sum(defined_site_ratios) / len(defined_site_ratios)),
            'observed_in_either_subsample_in_all_pairs': {'sites': len(all_pairs_sites), 'intersection': wide_i, 'union': wide_u},
            'remaining_sites': {'sites': len(sites) - len(all_pairs_sites), 'intersection': both - wide_i, 'union': union - wide_u},
        },
        'source_adjudication_of_discordances': {'source_false_negative': source_classes['False Negatives'],
                                                'source_false_positive': source_classes['False Positives'],
                                                'basis': 'Authors used supporting calls elsewhere in the flower to interpret discordance.'},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('s2', type=Path)
    parser.add_argument('s5', type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.s2, args.s5), indent=2))
