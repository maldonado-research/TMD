"""Extract anonymous paired-library counts from the Fasanello source checkout."""
import argparse
import csv
from fractions import Fraction
import hashlib
from pathlib import Path

import pandas as pd
import rdata

# Source files in commit a370be7497fda328c6c8b13d957223ff4cba53c6.
FILES = {
    'myevo.Rdata': 'f10be28895efc07a2106f8de08e38661ccc75139826e919ffe54b170aa41d9e0',
    '002_Metadata.csv': '6257038e18b56ef6f9f608354364b1a5b340b25db0b90423d2a4e4345aea7504',
    '002_Reruns_Metadata.csv': 'd169ddb6b0d8e537be64470d6a819c6e73273a5ebe3a813002456d255e0a005e',
    '002_counts.expected.Rdata': '86a3ea966462f262e4de73fe87020ad6a4da7127a65d2d515372c6826173e660',
    '002_counts.unexpected.Rdata': '36f18a68780c7c27c9b980c76eefb85b3abea09f3341fa5a819906976ab61b55',
    '002_Reruns_counts.expected.Rdata': '1036f544ae090ebb582eab71a7efcf982aa176d752c9d3faf2fc3b42652a423d',
    '002_Reruns_counts.unexpected.Rdata': 'fdce0e88994082fa23b8bd098cddac110fa28179ae792f562493697eab2e2ec4',
}
COLUMNS = ('population_id', 'day', 'original_A', 'original_B', 'rerun_A', 'rerun_B', 'selected')


def checked_files(root):
    paths = {}
    for name, digest in FILES.items():
        folder = '002_Prepare_Datasets' if name == 'myevo.Rdata' else '002_Raw_Data_Metadata'
        path = root / '2_CountstoAnalysis' / folder / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Unexpected source contents: {name}')
        paths[name] = path
    return paths


def read_library(files, prefix):
    metadata = pd.read_csv(files[f'{prefix}_Metadata.csv'])
    subset = metadata.loc[metadata['at'].eq('evolution') & metadata.bcpwell.eq(2)]
    subset = subset.set_index(['set', 'etp'], verify_integrity=True)
    matrices = {}
    for kind in ('expected', 'unexpected'):
        key = f'counts.{kind}'
        raw = rdata.read_rda(files[f'{prefix}_{key}.Rdata'])[key].to_pandas()
        # The last row aggregates the whole sample. The 78 preceding rows identify labels.
        assert len(raw) == 79 and set(raw.columns) == set(metadata.exp)
        matrices[kind] = raw.iloc[:78]
    totals = {kind: frame.add(1).sum() for kind, frame in matrices.items()}
    rates = {}
    for sample in subset.itertuples():
        expected = int(totals['expected'].loc[sample.exp])
        unexpected = int(totals['unexpected'].loc[sample.exp])
        rates[sample.exp] = Fraction(unexpected, (expected + unexpected) * (78 - sample.bcpexp))
    return subset, matrices['expected'], rates


def visit(library, row, day, labels):
    samples, counts, rates = library
    key = row['set'], day
    if key not in samples.index:
        return None
    sample = samples.loc[key].exp
    observed = counts.loc[labels, sample]
    if observed.isna().any() or any(x < 0 or not float(x).is_integer() for x in observed):
        raise ValueError('Incomplete or invalid assigned label count')
    return tuple(int(x) for x in observed), rates[sample]


def endpoint_membership(original, repeated, wells):
    """Match the source endpoint sample and its intended two-label wells in both runs."""
    first = original[0].xs(25, level='etp').sort_index()
    second = repeated[0].xs(25, level='etp').sort_index()
    label_fields = [f'bc{i}' for i in range(1, 24)]
    fields = ['exp', 'bcpexp', *label_fields]
    pd.testing.assert_frame_equal(first[fields], second[fields], check_dtype=False)
    if not first.exp.is_unique or set(first.index) != set(wells['set']):
        raise ValueError('Endpoint pool/sample correspondence differs from the well roster')
    expected_pairs = {}
    for pool, endpoint in first.iterrows():
        labels = endpoint[label_fields].dropna().tolist()
        if len(labels) != endpoint.bcpexp or len(labels) % 2 or len(labels) != len(set(labels)):
            raise ValueError('Unexpected endpoint label roster')
        expected_pairs[pool] = {frozenset(labels[i:i+2]) for i in range(0, len(labels), 2)}
    return expected_pairs


def extract(root, destination, endpoint_pools=None):
    files = checked_files(root)
    wells = rdata.read_rda(files['myevo.Rdata'])['myevo']
    assert len(wells) == wells.wid.nunique() == 76
    original = read_library(files, '002')
    repeated = read_library(files, '002_Reruns')
    intended_pairs = endpoint_membership(original, repeated, wells)
    pool_rows = []
    output = []
    for index, (_, row) in enumerate(wells.iterrows(), 1):
        # The two native sets with reused identifiers have a source-added B suffix.
        labels = [str(row[f'bc{k}']) for k in (1, 2)]
        if row['set'] in ('S14', 'S2'):
            labels = [label.removesuffix('B') for label in labels]
        assert len(set(labels)) == 2
        pool = row['set']
        if frozenset(labels) not in intended_pairs[pool]:
            raise ValueError('Well labels do not belong to their reported endpoint pool')
        pool_rows.append((f'W{index:03d}', pool))
        for day in (0, 10, 25):
            first = visit(original, row, day, labels)
            second = visit(repeated, row, day, labels)
            assert first is not None
            choose_repeat = second is not None and second[1] < first[1]
            selected_counts = second[0] if choose_repeat else first[0]
            archived = tuple(int(row[f'bc{k}cts_{day}']) - 1 for k in (1, 2))
            if selected_counts != archived:
                raise ValueError('Raw matrices disagree with the archived selected counts')
            counts = [first[0], second[0] if second is not None else ('', '')]
            # Preserve the A/B orientation of the main normalized population table.
            if labels[1] < labels[0]:
                counts = [pair[::-1] for pair in counts]
            output.append((f'W{index:03d}', day, *counts[0], *counts[1],
                           'rerun' if choose_repeat else 'original'))
    with destination.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(COLUMNS)
        writer.writerows(output)
    if endpoint_pools is not None:
        with endpoint_pools.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
            writer.writerow(('population_id', 'pool_id'))
            writer.writerows(pool_rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_checkout', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--endpoint-pools', type=Path,
                        help='Optional mapping from population to the day-25 source sample set')
    args = parser.parse_args()
    extract(args.source_checkout, args.destination, args.endpoint_pools)
