#!/usr/bin/env python3
"""MIT. Offline source/admission verifier; no requests, fits, or source modification."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import statistics
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def representation(capture):
    response = capture['result']['value']
    data = response.get('structuredContent')
    if isinstance(data, dict) and 'markdown' in data:
        return data
    for item in response.get('content', []):
        if item.get('type') == 'text':
            try:
                data = json.loads(item['text'])
            except ValueError:
                continue
            if isinstance(data, dict) and 'markdown' in data:
                return data
    raise ValueError('No markdown representation')


def workbook(path):
    with zipfile.ZipFile(path) as archive:
        info = archive.infolist()
        require(len(info) == len({i.filename for i in info}), 'Duplicate ZIP members')
        require(sum(i.file_size for i in info) < 4 * 1024 * 1024, 'Oversized ZIP')
        for item in info:
            pp = PurePosixPath(item.filename)
            require(not pp.is_absolute() and '..' not in pp.parts, 'Unsafe ZIP path')
            require(not item.flag_bits & 1 and (item.external_attr >> 16) & 0o170000 != 0o120000,
                    'Encrypted or symlink ZIP member')
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(t.text or '' for t in node.iter('{'+NS['m']+'}t'))
                       for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        relations = {n.get('Id'): n.get('Target') for n in ET.fromstring(
            archive.read('xl/_rels/workbook.xml.rels'))}
        result = {}
        for sheet in ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
            rel = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target = relations[rel]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            if not target.startswith('xl/worksheets/'):
                continue
            rows = {}
            formulas = []
            for row in ET.fromstring(archive.read(target)).findall('m:sheetData/m:row', NS):
                cells = {}
                for cell in row:
                    address = cell.get('r')
                    value = cell.find('m:v', NS)
                    value = value.text if value is not None else None
                    if cell.get('t') == 's' and value is not None:
                        value = strings[int(value)]
                    elif cell.get('t') == 'inlineStr':
                        value = ''.join(cell.find('m:is', NS).itertext())
                    if cell.find('m:f', NS) is not None:
                        formulas.append(address)
                    if value is not None:
                        cells[re.sub(r'\d', '', address)] = value
                if cells:
                    rows[int(row.get('r'))] = cells
            result[sheet.get('name')] = {'rows': rows, 'formula_cells': formulas}
        return result, {'zip_members': len(info), 'expanded_bytes': sum(i.file_size for i in info)}


def derive(cache):
    mutation, mutation_zip = workbook(cache / 'elife-38822-fig6-data1-v1.xlsx')
    spectrum = []
    expected_headers = ['Genome position', 'Type', 'Change', 'Gene position', 'Gene locus',
                        'Gene symbol', 'Effect', 'Comment', 'Proposed molecular effect']
    for sheet in ['Wsp', 'Aws', 'Mws']:
        rows = mutation[sheet]['rows']
        require([rows[1].get(c) for c in 'ABCDEFGHI'] == expected_headers, 'Unexpected spectrum headers')
        entries = [(i, r) for i, r in rows.items() if i > 1 and r.get('F')]
        spectrum.append({'sheet': sheet, 'row_count': len(entries),
                         'first_row': entries[0][0], 'last_row': entries[-1][0],
                         'gene_counts': dict(sorted(collections.Counter(r['F'].strip() for _, r in entries).items())),
                         'named_culture_isolate_date_batch_columns': [],
                         'formula_cells': mutation[sheet]['formula_cells']})
    fitness, fitness_zip = workbook(cache / 'elife-38822-fig9-data1-v1.xlsx')
    rows = fitness['Sheet1']['rows']
    fitness_rows = []
    for number, row in rows.items():
        if number < 3 or 'D' not in row:
            continue
        values = [float(row[c]) for c in 'GHIJKLM' if c in row]
        if not values:
            continue
        observed_mean, observed_sd = statistics.mean(values), statistics.stdev(values)
        stored_mean, stored_sd = float(row['D']), float(row['E'])
        fitness_rows.append({'row': number, 'gene': row['B'].strip(), 'mutation_label': row['C'],
            'coefficient_cells': [c+str(number) for c in 'GHIJKLM' if c in row],
            'coefficient_count': len(values), 'stored_mean': stored_mean, 'stored_sample_sd': stored_sd,
            'recomputed_mean': observed_mean, 'recomputed_sample_sd': observed_sd,
            'mean_matches': math.isclose(observed_mean, stored_mean, rel_tol=1e-12, abs_tol=1e-14),
            'sample_sd_matches': math.isclose(observed_sd, stored_sd, rel_tol=1e-12, abs_tol=1e-14)})
    article = representation(read(cache / 'S03.json'))['markdown']
    earlier = representation(read(cache / 'S07.json'))['markdown']
    table = article.split('## TABLE 1.', 1)[1].split('[Open in a new tab]', 1)[0]
    routes = []
    for line in table.splitlines():
        if not re.match(r'\| WS[A-Z](?: |<)', line):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        label = re.match(r'WS[A-Z]', cells[0]).group()
        gene = re.sub(r'<br>.*', '', cells[1]).strip('_ ')
        route = {'wspF':'Wsp','wspE':'Wsp','awsO':'Aws','awsR':'Aws','awsX':'Aws','mwsR':'Mws'}.get(gene)
        routes.append({'isolate_label': label, 'reported_gene': None if gene == '?' else gene,
                       'molecular_table_route': route,
                       'functional_dependency': 'Wsp (source discussion; causal mutation unidentified)' if label == 'WSX' else None,
                       'source_locator': 'McDonald2009 Table1 / '+label})
    require([r['isolate_label'] for r in routes] == ['WS'+chr(i) for i in range(65,91)], 'Incomplete cohort table')
    require('a single WS genotype was selected at random from each microcosm' in earlier,
            'Random WS selection anchor absent')
    require('26 separate microcosms' in earlier and 'After 5 days of selection' in earlier,
            'Collection unit anchor absent')
    require('25 of 26 WS genotypes' in article and 'no mutation in _wsp_, _aws_, or _mws_' in article,
            'Unknown molecular classification anchor absent')
    require('WST contains an in-frame deletion (33 nucleotides) spanning residues 229–261' in article,
            'WST explicitly reported deletion-length anchor absent')
    return {'schema_version': 1, 'source_replay_scope': 'OOXML values and fresh provider markdown representations; no source experimental validation',
        'lind2019_spectrum': {'sheets': spectrum, 'total_focal_rows': sum(r['row_count'] for r in spectrum),
            'rare_rows_exported': 0, 'rare_rows_meaning': 'No rare-pathway records in this focal-pathway workbook; not zero rare mutations in the study.',
            'column_headers': expected_headers, 'archive': mutation_zip},
        'lind2019_fitness': {'rows': fitness_rows, 'total_genotype_rows': len(fitness_rows),
            'total_coefficient_cells': sum(r['coefficient_count'] for r in fitness_rows),
            'source_A1_label': rows[1]['A'], 'formula_cells': fitness['Sheet1']['formula_cells'],
            'nonmatching_summary_rows': [r['row'] for r in fitness_rows if not (r['mean_matches'] and r['sample_sd_matches'])],
            'archive': fitness_zip, 'new_fit_performed': False},
        'historical_cohort': {'rows': routes, 'molecular_table_counts': dict(sorted(collections.Counter(r['molecular_table_route'] or 'Unresolved' for r in routes).items())),
            'collection_size': 26, 'collection_reused_between_2007_and_2009': True,
            'WST_reported_awsX_annotation': {'table_coordinates':'Δ229-261', 'results_reported_deletion_nucleotides':33,
                'results_reported_in_frame':True, 'Karita_stock_equality_authenticated':False,
                'Karita_32bp_annotation_corrected':False, 'actual_study_allele_selected':False},
            'source_reported_independent_microcosms': 26, 'selection_rule': 'one random WS isolate after five days from each separate common-ancestor microcosm',
            'complete_eligible_run_outcome_ledger_acquired': False, 'first_arrival_records_acquired': False,
            'actual_study_registry_filled': False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--derive-to', type=Path, help='Write audit only; used during preparation with source cache')
    args = parser.parse_args()
    require(sys.flags.optimize == 0, 'Do not run optimized Python')
    package = Path(__file__).resolve().parent
    if args.derive_to:
        require(args.source_cache is not None, 'Source cache required')
        args.derive_to.write_text(json.dumps(derive(args.source_cache), indent=2, ensure_ascii=False)+'\n')
        return
    public = read(package/'PUBLIC_FILES.json')
    require(len(public['public_files']) == len(set(public['public_files'])), 'Duplicate public names')
    require({p.name for p in package.iterdir()} == set(public['public_files']), 'Public whitelist mismatch')
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()), 'Nonregular public file')
    names = [r['path'] for r in public['files']]
    require(len(names) == len(set(names)), 'Duplicate public fingerprints')
    require(set(names) == set(public['public_files']) - {'PUBLIC_FILES.json','SHA256SUMS.txt','VERIFICATION_RECEIPT.json'},
            'Incomplete core fingerprint coverage')
    for record in public['files']:
        require(Path(record['path']).name == record['path'], 'Unsafe public path')
        p = package/record['path']
        require(p.is_file() and not p.is_symlink() and len(p.read_bytes()) == record['bytes'] and sha(p) == record['sha256'], 'Public fingerprint mismatch')
    covered = set()
    for line in (package/'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ',1)
        require(name not in covered, 'Duplicate SHA256SUMS member')
        covered.add(name)
        require(Path(name).name == name and sha(package/name) == digest, 'SHA256SUMS mismatch')
    require(covered == set(public['public_files']) - {'SHA256SUMS.txt','VERIFICATION_RECEIPT.json'},
            'Incomplete SHA256SUMS coverage')
    root = package.parent.parent
    study = read(root/'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(root/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(study)==26 and all(v is None for v in study.values()), '26 study NULLs changed')
    require(len(planning)==18 and all(v is None for v in planning.values()), '18 planning NULLs changed')
    decision = read(package/'DECISION.json')
    require(decision['matched_panels_admitted']==0 and decision['new_biological_fit'] is False, 'Admission drift')
    audit = read(package/'DERIVED_SOURCE_AUDIT.json')
    require(audit['historical_cohort']['molecular_table_counts']=={'Aws':6,'Mws':3,'Unresolved':1,'Wsp':16}, 'Molecular route counts drift')
    require(audit['lind2019_spectrum']['total_focal_rows']==105, 'Spectrum row count drift')
    require(audit['lind2019_fitness']['nonmatching_summary_rows']==[21], 'Summary mismatch erased')
    provenance = read(package/'SOURCE_PROVENANCE.json')
    require(provenance['logical_scientific_calls'] == len(provenance['calls']) == 7,
            'Acquisition call accounting drift')
    require(sum(r['bytes'] for r in provenance['saved_acquisition_files']) == provenance['saved_acquisition_bytes'] <= provenance['byte_allocation'],
            'Saved acquisition byte accounting drift')
    for record in provenance['inherited_dependencies']:
        target = root/record['path']
        require(len(target.read_bytes()) == record['bytes'] and sha(target) == record['sha256'],
                'Inherited requirement changed: '+record['path'])
    replay = 'UNRUN: no source cache supplied'
    if args.source_cache:
        for record in provenance['saved_acquisition_files']:
            require(Path(record['filename']).name == record['filename'], 'Unsafe source path')
            p = args.source_cache/record['filename']
            require(p.is_file() and len(p.read_bytes())==record['bytes'] and sha(p)==record['sha256'], 'Source fingerprint mismatch: '+p.name)
        require(derive(args.source_cache)==audit, 'Source replay differs from derived audit')
        replay = 'PASS: source identities, workbook structure/arithmetic, cohort molecular rows and selected method anchors'
    print(json.dumps({'status':'PASS','source_replay':replay,'study_nulls':26,'planning_nulls':18,
        'matched_panels_admitted':0,'source_experimental_truth_validated':False},indent=2))


if __name__ == '__main__':
    main()
