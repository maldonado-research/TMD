#!/usr/bin/env python3
"""MIT. Offline, read-only source and conditional-calculation verification."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import statistics
import xml.etree.ElementTree as ET
import zipfile

M = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
C = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
SOURCE_NAME = 'elife-38822-fig9-data1-v1.xlsx'


def require(condition, message):
    if not condition:
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
    response = capture['result']
    if isinstance(response.get('structuredContent'), dict):
        return response['structuredContent']
    for item in response.get('content', []):
        if item.get('type') == 'text':
            parsed = json.loads(item['text'])
            if isinstance(parsed, dict):
                return parsed
    raise ValueError('Missing provider representation')


def workbook_fields(path):
    with zipfile.ZipFile(path) as archive:
        info = archive.infolist()
        require(len(info) == len({i.filename for i in info}), 'Duplicate ZIP member')
        require(sum(i.file_size for i in info) < 4 * 1024 * 1024, 'Oversized ZIP')
        for item in info:
            pp = PurePosixPath(item.filename)
            require(not pp.is_absolute() and '..' not in pp.parts, 'Unsafe ZIP path')
            require(not item.flag_bits & 1 and (item.external_attr >> 16) & 0o170000 != 0o120000,
                    'Encrypted or symlink ZIP member')
        strings = [''.join(t.text or '' for t in node.iter('{'+M['m']+'}t'))
                   for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        cells = {}
        for cell in sheet.findall('m:sheetData/m:row/m:c', M):
            value, formula = cell.find('m:v', M), cell.find('m:f', M)
            lexical = value.text if value is not None else None
            if cell.get('t') == 's' and lexical is not None:
                lexical = strings[int(lexical)]
            cells[cell.get('r')] = {'value': lexical, 'formula': formula.text if formula is not None else None}
        selected = ['A1','A2','B2','C2','D2','E2','G2','O2','A21','B21','C21',
                    'D20','E20','D21','E21','G21','H21','I21','J21','O21','D22','E22']
        selected_cells = {address: cells.get(address, {'value': None, 'formula': None}) for address in selected}
        rows, counts, mismatches = [], [], []
        for row in range(3, 23):
            if cells.get('D'+str(row), {}).get('value') is None:
                continue
            values = [float(cells[c+str(row)]['value']) for c in 'GHIJKLM'
                      if cells.get(c+str(row), {}).get('value') is not None]
            if not values:
                continue
            rows.append(row)
            counts.append(len(values))
            if not (math.isclose(statistics.mean(values), float(cells['D'+str(row)]['value']), abs_tol=1e-14)
                    and math.isclose(statistics.stdev(values), float(cells['E'+str(row)]['value']), abs_tol=1e-14)):
                mismatches.append(row)
        chart = ET.fromstring(archive.read('xl/charts/chart1.xml'))
        series = chart.findall('.//c:ser', C)
        require(len(series) == 1, 'Unexpected chart series count')
        chart_fields = {}
        for label, selector, ref in [
            ('category', 'c:cat/c:strRef', 'c:strCache'),
            ('value', 'c:val/c:numRef', 'c:numCache'),
            ('error_plus', 'c:errBars/c:plus/c:numRef', 'c:numCache'),
            ('error_minus', 'c:errBars/c:minus/c:numRef', 'c:numCache')]:
            node = series[0].find(selector, C)
            chart_fields[label] = {
                'range': node.find('c:f', C).text,
                'point_index': 18,
                'cached_value': node.find(ref+'/c:pt[@idx="18"]/c:v', C).text}
        return {
            'workbook_filename': SOURCE_NAME, 'worksheet': 'Sheet1',
            'cell_storage_note': 'Numeric values are exact lexical XML values; null means no stored value/formula. Source strings are attributed facts.',
            'selected_cells': selected_cells,
            'genotype_rows': len(rows), 'visible_coefficient_cells': sum(counts),
            'nonmatching_unweighted_mean_sample_sd_rows': mismatches,
            'worksheet_formula_count': len(sheet.findall('m:sheetData/m:row/m:c/m:f', M)),
            'hidden_rows': [r.get('r') for r in sheet.findall('m:sheetData/m:row', M) if r.get('hidden') == '1'],
            'hidden_columns': [dict(c.attrib) for c in sheet.findall('m:cols/m:col', M) if c.get('hidden') == '1'],
            'comment_parts_present': any('comment' in n.lower() for n in archive.namelist()),
            'embedded_chart': {'part': 'xl/charts/chart1.xml', 'fields': chart_fields,
                'independent_experiment': False,
                'interpretation': 'The embedded chart references and caches the stored row21 summaries. It does not supply their intended aggregation or authenticate the rendered published figure.'}}


def square_bounds(low, high):
    return (F(0) if low <= 0 <= high else min(low*low, high*high), max(low*low, high*high))


def diagnostic(fields):
    cells = fields['selected_cells']
    xs = [F(cells[a]['value']) for a in ['G21','H21','I21']]
    mean, sd = F(cells['D21']['value']), F(cells['E21']['value'])
    centered = [x-mean for x in xs]
    a, c = sum(v*v for v in centered), sum(centered)
    fourth = 4*mean-sum(xs)
    four_sd = math.sqrt(float((a+c*c)/3))
    require(sum(xs+[fourth])/4 == mean, 'Forced fourth does not reproduce mean')
    require(sum((x-mean)**2 for x in xs+[fourth])/3 == (a+c*c)/3, 'Direct fourth-value variance identity failed')
    epsilon = F('5e-15')
    squares = [square_bounds(v-2*epsilon, v+2*epsilon) for v in centered]
    alo, ahi = sum(v[0] for v in squares), sum(v[1] for v in squares)
    blo, bhi = square_bounds(c-6*epsilon, c+6*epsilon)
    slo, shi = square_bounds(sd-epsilon, sd+epsilon)
    checks = []
    for total_n in [4,20,21]:
        k = total_n-3
        minimum, target = a+c*c/k, (total_n-1)*sd*sd
        gap_bounds = [alo+blo/k-(total_n-1)*shi, ahi+bhi/k-(total_n-1)*slo]
        checks.append({'total_n': total_n, 'additional_count': k,
                       'minimum_sse_at_stored_mean': float(minimum), 'required_sse_from_stored_sd': float(target),
                       'minimum_minus_required_sse': float(minimum-target),
                       'gap_bounds_with_each_input_perturbed_at_most_5e_minus_15': [float(v) for v in gap_bounds],
                       'feasible_as_unrestricted_real_extension': minimum == target if k == 1 else minimum <= target})
    require(checks[0]['gap_bounds_with_each_input_perturbed_at_most_5e_minus_15'][0] > 0, 'Fourth-value rounding conclusion failed')
    require(checks[1]['gap_bounds_with_each_input_perturbed_at_most_5e_minus_15'][0] > 0 and
            checks[2]['gap_bounds_with_each_input_perturbed_at_most_5e_minus_15'][1] < 0,
            'Boundary rounding conclusion failed')
    minimum_n = next(n for n in range(4, 100)
                     if (a+c*c == 3*sd*sd if n == 4 else a+c*c/(n-3) <= (n-1)*sd*sd))
    require(minimum_n == 21, 'Unexpected smallest feasible unrestricted count')
    return {
        'convention': 'Retain all three exported coefficients unchanged, append unrestricted real values, equal weights, arithmetic mean and sample SD with denominator n-1.',
        'unweighted_visible_mean': float(sum(xs)/3),
        'unweighted_visible_sample_sd': statistics.stdev(map(float, xs)),
        'stored_mean': float(mean), 'stored_sd': float(sd),
        'forced_fourth_value_from_stored_mean': float(fourth),
        'sample_sd_with_forced_fourth': four_sd,
        'one_additional_value_can_reconcile_both': False,
        'boundary_checks': checks,
        'smallest_feasible_total_n_for_unrestricted_real_extension': minimum_n,
        'smallest_additional_count_for_unrestricted_real_extension': minimum_n-3,
        'rounding_envelope': 'Independent absolute perturbations up to 5e-15 in each of the three coefficients and both stored summaries; conservative rational interval bounds retain all three gap signs.',
        'not_an_imputation': True, 'evidence_for_actual_additional_replicates': False,
        'source_intended_aggregation_identified': False,
        'novel_theorem_claimed': False}


def check_fingerprint(folder, record, field='filename'):
    name = record[field]
    require(Path(name).name == name, 'Unsafe cache name')
    path = folder/name
    require(path.is_file() and path.stat().st_size == record['bytes'] and sha(path) == record['sha256'],
            'Source fingerprint mismatch: '+name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--r28-cache', type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    public = read(package/'PUBLIC_FILES.json')['public_files']
    require(len(public) == len(set(public)) and all(Path(f).name == f for f in public), 'Unsafe public allowlist')
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()), 'Unexpected directory or symlink in public package')
    require(set(p.name for p in package.iterdir() if p.is_file()) == set(public), 'Public file closure mismatch')
    covered = set()
    for line in (package/'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name in public and name not in covered and sha(package/name) == digest, 'Public hash mismatch: '+name)
        covered.add(name)
    require(covered == set(public)-{'SHA256SUMS.txt'}, 'Incomplete public hash coverage')
    provenance = read(package/'SOURCE_PROVENANCE.json')
    require(len(provenance['calls']) == provenance['logical_scientific_calls'] <= provenance['logical_call_allocation'], 'Call accounting drift')
    require(sum(r['bytes'] for r in provenance['saved_acquisition_files']) == provenance['saved_acquisition_bytes'] <= provenance['byte_allocation'], 'Byte accounting drift')
    for record in provenance['inherited_dependencies']:
        path = root/record['path']
        require(path.stat().st_size == record['bytes'] and sha(path) == record['sha256'], 'Inherited dependency changed: '+record['path'])
    study = read(root/'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(root/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(study) == 26 and all(v is None for v in study.values()), 'Study NULL guard failed')
    require(len(planning) == 18 and all(v is None for v in planning.values()), 'Planning NULL guard failed')
    decision = read(package/'DECISION.json')
    require(decision['matched_panels_admitted'] == 0 and decision['new_biological_fit'] is False and decision['author_values_replaced'] is False, 'Decision drift')
    fields = read(package/'SOURCE_FIELDS.json')
    require(diagnostic(fields) == read(package/'CONDITIONAL_DIAGNOSTIC.json'), 'Conditional calculation drift')
    new_replay, prior_replay = 'UNRUN: no R29 source cache supplied', 'UNRUN: no R28 workbook cache supplied'
    if args.source_cache:
        for record in provenance['saved_acquisition_files']:
            check_fingerprint(args.source_cache, record)
        article = representation(read(args.source_cache/'S02.json'))['markdown']
        api = representation(read(args.source_cache/'S04.json'))['markdown']
        for anchor in ['independently inoculated quadruplicates', 'excluded (two cases)',
                       'correct for the cost of the GFP marker', 'cost of the double deletions and the reporter construct']:
            require(anchor in article, 'Article method anchor missing: '+anchor)
        for anchor in ['"version": 1', 'elife-38822-fig9-data1-v1.xlsx', 'one standard deviation']:
            require(anchor in api, 'Publisher API representation anchor missing: '+anchor)
        new_replay = 'PASS: capture identities and selected primary-source anchors; no exhaustive correction-search claim'
    if args.r28_cache:
        for record in provenance['reused_source_files']:
            check_fingerprint(args.r28_cache, record)
        require(workbook_fields(args.r28_cache/SOURCE_NAME) == fields, 'Workbook facts differ')
        prior_replay = 'PASS: reused exact R28 binary identity, cell/formula/chart audit and row arithmetic; not a fresh acquisition'
    print(json.dumps({'status':'PASS','new_source_replay':new_replay,'reused_workbook_replay':prior_replay,
                      'conditional_calculation':'PASS','study_nulls':26,'planning_nulls':18,
                      'matched_panels_admitted':0,'source_experimental_truth_validated':False}, indent=2))


if __name__ == '__main__':
    main()
