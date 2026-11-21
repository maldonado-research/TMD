"""Audit whether the released founder roster supports the frozen M3 test."""
import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile


COUNTS_SHA = '49bd605ffa896beed59e16eb013d65bdea8ae0a33e54ac574157dfbf277541fa'
WORKBOOK_SHA = 'd27fe37b56d87e4be9a1de6e1b85f6cdd8230729cda287eeef4565400f1d7dad'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
VISITS = ('T0', 'T2', 'T63')


def verify(path, expected):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f'Unexpected SHA-256 for {path.name}: {actual}')


def read_reference(path):
    with ZipFile(path) as book:
        strings = ET.fromstring(book.read('xl/sharedStrings.xml'))
        dictionary = [''.join(item.itertext()) for item in strings]
        sheets = []
        for index in (1, 2):
            sheet = ET.fromstring(book.read(f'xl/worksheets/sheet{index}.xml'))
            rows = []
            for row in sheet.findall('.//s:row', NS):
                cells = {}
                for cell in row.findall('s:c', NS):
                    value = cell.findtext('s:v', namespaces=NS)
                    if value is None:
                        continue
                    key = re.match('[A-Z]+', cell.get('r')).group()
                    cells[key] = dictionary[int(value)] if cell.get('t') == 's' else value
                rows.append(cells)
            formats = [rule.attrib['type'] for rule in sheet.findall('.//s:cfRule', NS)]
            hidden = sum(row.get('hidden', '0') == '1' for row in sheet.findall('.//s:row', NS))
            sheets.append((rows, formats, hidden))
    rows, rules, hidden = sheets[0]
    if (rows[0]['A'], rows[0]['B']) != ('Strain_id', 'consensus barcode'):
        raise ValueError('Unexpected genetic reference worksheet')
    ids = [row['A'] for row in rows[1:]]
    reference = set(ids)
    return reference, {
        'sheet1_rows_after_header': len(ids), 'sheet1_unique_labels': len(reference),
        'sheet1_repeat_label_rows': len(ids) - len(reference),
        'sheet1_hidden_rows': hidden, 'sheet1_conditional_format_types': rules,
        'sheet2_review_rows': len(sheets[1][0]), 'sheet2_hidden_rows': sheets[1][2],
        'sheet2_conditional_format_types': sheets[1][1],
    }


def marker(label):
    if label.startswith('sky_bc_'):
        return 'laboratory_reference_series'
    if label.startswith(('unkown', 'unknown')):
        return 'unknown_spelling_in_source'
    if label.endswith('_maybe'):
        return 'maybe_suffix_in_source'
    return 'other'


def audit(count_path, workbook_path):
    verify(count_path, COUNTS_SHA)
    verify(workbook_path, WORKBOOK_SHA)
    reference, workbook_summary = read_reference(workbook_path)
    counts = defaultdict(Counter)
    rows = Counter()
    samples = defaultdict(set)
    plates = defaultdict(set)
    all_rows = 0
    with count_path.open(newline='') as source:
        for row in csv.DictReader(source):
            all_rows += 1
            if row['experiment'] != 'LT-EVO' or row['environment'] != 'M3':
                continue
            visit = row['timepoint']
            if visit not in VISITS:
                continue
            replicate = int(row['replicate'].removeprefix('R'))
            if not 1 <= replicate <= 20:
                raise ValueError('Unexpected replicate in frozen slice')
            count = int(row['count'])
            if count <= 0:
                raise ValueError('Unexpected nonpositive count in sparse table')
            counts[visit, replicate][row['Barcode_ID']] += count
            rows[visit] += 1
            samples[visit, replicate].add(row['admera_ID'])
            plates[visit, 'R1-R10' if replicate <= 10 else 'R11-R20'].add(row['2nd_primer_plate'])

    visits = {}
    for visit in VISITS:
        population = [counts[visit, rep] for rep in range(1, 21)]
        if not all(population):
            raise ValueError('Missing frozen visit or replicate')
        detected = [set(p) for p in population]
        total = sum(population, Counter())
        nonreference = set(total) - reference
        total_by_marker = Counter()
        for label, count in total.items():
            total_by_marker[marker(label)] += count
        visits[visit] = {
            'biological_populations': len(population), 'native_rows': rows[visit],
            'pooled_replicate_label_cells': sum(map(len, population)),
            'distinct_recorded_labels': len(total),
            'labels_present_in_every_population': len(set.intersection(*detected)),
            'positive_labels_per_population_min_max': [min(map(len, detected)), max(map(len, detected))],
            'reads_all_recorded_labels': sum(total.values()),
            'distinct_labels_absent_from_s3_sheet1_exact_match': len(nonreference),
            'reads_absent_from_s3_sheet1_exact_match': sum(total[k] for k in nonreference),
            'reads_by_source_label_spelling': dict(sorted(total_by_marker.items())),
            'replicates_with_multiple_sample_ids': sum(len(samples[visit, r]) > 1 for r in range(1, 21)),
            'secondary_primer_plates_by_fold': {
                fold: sorted(plates[visit, fold]) for fold in ('R1-R10', 'R11-R20')
            },
        }
    return {
        'count_file_sha256': COUNTS_SHA, 'table_s3_sha256': WORKBOOK_SHA,
        'full_count_file_rows': all_rows, 'count_rows_used_in_coverage_audit': sum(rows.values()),
        'prespecified_natural_founder_count': 282,
        'workbook': workbook_summary, 'visit_audit': visits,
        'status': 'unscored_missing_verified_282_founder_assignment',
        'scored_populations': 0, 'hits': None,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('counts', type=Path)
    parser.add_argument('supplementary_table_3', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.counts, args.supplementary_table_3), indent=2, sort_keys=True))
