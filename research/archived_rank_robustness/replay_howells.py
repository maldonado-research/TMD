"""Reproduce aggregate source-annotation counts from Howells et al.'s Figshare workbook."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from openpyxl import load_workbook


DOI = 'https://doi.org/10.6084/m9.figshare.28340420.v1'
SHA256 = '48f769eb2b49fb02e5a468a0c991d70557848fb79b99629cbd5683233bfbb328'
STUDY = 'https://doi.org/10.1111/1462-2920.70061'
KEY = 'https://doi.org/10.7554/eLife.38822'
# Lind et al., Key resources table. Normalize only case and underscores.
ALIAS_GROUPS = {
    'W': 'wspA wspB wspC wspD wspE wspF wspR PFLU1219 PFLU1220 PFLU1221 PFLU1222 PFLU1223 PFLU1224 PFLU1225',
    'A': 'awsX awsR awsO yfiR yfiN yfiB tpbB PFLU5211 PFLU5210 PFLU5209',
    'M': 'mwsR morA PFLU5329',
}
FAMILY = {alias.lower(): group for group, aliases in ALIAS_GROUPS.items() for alias in aliases.split()}
PHENOTYPES = {'W': 'wrinkly', 'S': 'smooth'}


def read_frame(book):
    """Colony-count roster agrees with the Methods contamination exclusion."""
    colony_rows = list(book['Colony counts'].values)
    frame = {}
    for arm, column in [('monoculture', 5), ('coculture', 0)]:
        frame[arm] = [str(row[column]).upper() for row in colony_rows
                      if re.fullmatch(r'[CP][1-5]', str(row[column]), re.IGNORECASE)]
    if set(frame['monoculture']) != {'P1', 'P3', 'P4', 'P5'} or set(frame['coculture']) != {f'C{i}' for i in range(1, 6)}:
        raise ValueError('Colony frame differs from the published analysis populations')
    summary = {r[0]: r[1] for r in book['Summary of mutations'].values}
    for arm, label in [('monoculture', 'Monoculture'), ('coculture', 'Co-culture')]:
        if summary[f'{label} P. fluorescens'] != len(frame[arm]) * 2:
            raise ValueError('Sequenced clone count and colony roster disagree')
    return frame


def counts_by_parent(parents, observed):
    both_same = Counter()
    families = {name: Counter() for name in PHENOTYPES.values()}
    pairs = Counter()
    for parent in parents:
        for suffix, phenotype in PHENOTYPES.items():
            labels = observed[parent + suffix]
            category = '+'.join(sorted(labels)) if labels else 'unmatched'
            families[phenotype][category] += 1
        wrinkly, smooth = observed[parent + 'W'], observed[parent + 'S']
        if wrinkly and smooth:
            pairs['both'] += 1
            if wrinkly == smooth:
                both_same['+'.join(sorted(wrinkly))] += 1
        elif wrinkly:
            pairs['wrinkly_only'] += 1
        elif smooth:
            pairs['smooth_only'] += 1
        else:
            pairs['neither'] += 1
    categories = ['W', 'A', 'M', 'unmatched']
    if any(set(counts) - set(categories) for counts in families.values()):
        raise ValueError('At least one clone has annotations in more than one family')
    return {
        'parents': len(parents),
        'clones_by_phenotype_and_recorded_family': {
            name: {k: counts[k] for k in categories} for name, counts in families.items()
        },
        'pairs_with_any_recorded_family': {
            k: pairs[k] for k in ('both', 'wrinkly_only', 'smooth_only', 'neither')
        },
        'paired_clones_with_same_recorded_family': {k: both_same[k] for k in ('W', 'A', 'M')},
    }


def replay(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('Unexpected source workbook SHA-256')
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        frame = read_frame(book)
        rows = list(book['Pfluor mutations'].values)
    finally:
        book.close()
    header = rows[1]
    all_names = {x for x in header if re.fullmatch(r'[CP][1-5][SW]', str(x))}
    eligible = {p + suffix for parents in frame.values() for p in parents for suffix in PHENOTYPES}
    if all_names - eligible != {'P2W', 'P2S'} or not eligible <= all_names:
        raise ValueError('Genomic roster does not match the analysis frame and exclusion')
    columns = {name: header.index(name) for name in all_names}
    gene_column = header.index('gene')
    observed = {name: set() for name in eligible}
    with_delta = {name: set() for name in eligible}
    column_has_calls = set()
    gene_rows = 0
    markers = Counter()
    for row in rows[2:]:
        if row == header:
            continue
        if type(row[0]) is not int:
            raise ValueError('Unrecognized source matrix row')
        gene_rows += 1
        field = row[gene_column].lower().replace('_', '')
        tokens = set(re.findall(r'[a-z0-9]+', field))
        labels = {FAMILY[t] for t in tokens if t in FAMILY}
        if labels and (len(tokens) != 1 or len(labels) != 1):
            raise ValueError('A family match requires review of a mixed label')
        for name, column in columns.items():
            marker = row[column]
            if marker is None:
                continue
            if marker != 1 and marker != 'Δ':
                raise ValueError('Unrecognized source presence symbol')
            column_has_calls.add(name)
            markers['numeric_one' if marker == 1 else 'delta'] += 1
            if name in eligible and labels:
                with_delta[name].update(labels)
                if marker == 1:
                    observed[name].update(labels)
    return {
        'article': STUDY, 'supplement': DOI, 'alias_reference': KEY,
        'source_bytes': len(data), 'sha256': SHA256,
        'source_registered_md5': hashlib.md5(data).hexdigest(),
        'genome_matrix': {'listed_clone_columns': len(columns), 'data_rows': gene_rows,
                          'excluded_parent': 'P2', 'excluded_columns_with_recorded_calls': len(column_has_calls - eligible),
                          'eligible_clone_columns': len(eligible), 'nonempty_markers_all_columns': dict(markers)},
        'including_delta_yields_identical_eligible_family_sets': observed == with_delta,
        'sample_rule': 'One archived clone of each chosen morphology per retained population at week 8.',
        'count_rule': 'Numeric 1 for a matching gene annotation in Pfluor mutations. Each clone contributes once per family. Unmatched means no matched annotation under this rule.',
        'arms': {arm: counts_by_parent(parents, observed) for arm, parents in frame.items()},
        'paired_roster_totals': counts_by_parent(frame['monoculture'] + frame['coculture'], observed),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook', type=Path)
    print(json.dumps(replay(parser.parse_args().workbook), indent=2))
