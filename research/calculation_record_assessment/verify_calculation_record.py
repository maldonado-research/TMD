#!/usr/bin/env python3
"""MIT. Offline, read-only source-record and conditional-dispersion verification."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile

COMMIT = 'e78d2b2df7c7af799687e4739f05027f204b3bf8'
SOURCE_NAME = 'elife-38822-fig9-data1-v1.xlsx'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key: '+key)
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


def diagnostic(fields):
    cells = fields['selected_cells']
    g, h, i, m, s = [F(cells[a]['value']) for a in ['G21','H21','I21','D21','E21']]
    require(i < h < m < g and s > 0, 'Unexpected support or mean ordering')
    # Every support point lies outside the open interval (h,g), so
    # E[(X-h)(X-g)] >= 0 implies Var(X) >= (m-h)(g-m).
    minimum = (m-h)*(g-m)
    weights = [(m-h)/(g-h), (g-m)/(g-h), F(0)]
    require(sum(weights) == 1 and all(w >= 0 for w in weights), 'Invalid extremal weights')
    require(sum(w*x for w,x in zip(weights,[g,h,i])) == m, 'Extremal mean differs')
    require(sum(w*(x-m)**2 for w,x in zip(weights,[g,h,i])) == minimum, 'Sharp variance differs')
    require(all((x-h)*(x-g) >= 0 for x in [g,h,i]), 'Support inequality failed')
    # Independent check: feasible vertices have support on at most two points.
    vertices = []
    for a,b in [(h,g),(i,g)]:
        w = (m-a)/(b-a)
        vertices.append((1-w)*(a-m)**2+w*(b-m)**2)
    require(min(vertices) == minimum, 'Two-point vertex calculation differs')
    epsilon = F('5e-15')
    require(i+epsilon < h-epsilon and h+epsilon < m-epsilon and m+epsilon < g-epsilon,
            'Rounding interval changes ordering')
    gap_low = (m-h-2*epsilon)*(g-m-2*epsilon)-(s+epsilon)**2
    gap_high = (m-h+2*epsilon)*(g-m+2*epsilon)-(s-epsilon)**2
    require(gap_low > 0, 'Rounding-robust exclusion failed')
    return {
        'assumptions': 'Only the unchanged visible G21/H21/I21 coefficients; nonnegative weights summing to one; their weighted arithmetic mean equals D21; E21 is population SD or an SD whose variance is at least this weighted population variance.',
        'visible_cell_order': ['G21','H21','I21'],
        'stored_mean': float(m), 'stored_sd': float(s),
        'stored_variance': float(s*s),
        'minimum_weighted_population_variance_at_stored_mean': float(minimum),
        'minimum_weighted_population_sd_at_stored_mean': math.sqrt(float(minimum)),
        'minimum_variance_minus_stored_variance': float(minimum-s*s),
        'attaining_weights_in_visible_cell_order': [float(w) for w in weights],
        'attaining_weights_are_diagnostic_not_author_weights': True,
        'gap_bounds_with_each_input_perturbed_at_most_5e_minus_15': [float(gap_low),float(gap_high)],
        'weights_alone_reconcile_mean_and_sd_under_assumptions': False,
        'zero_weights_permitted': True,
        'not_ruled_out': ['SEM or other uncertainty measures','transformations','different underlying records','GFP or background corrections','source transcription or undocumented aggregation'],
        'source_intended_aggregation_identified': False,
        'novel_theorem_claimed': False,
        'author_values_replaced': False
    }


def commit_fields(markdown):
    text = markdown.strip()
    require(text.startswith('```json') and text.endswith('```'), 'Expected JSON representation fence')
    data = json.loads(text[len('```json'):-3].strip())
    require(data['sha'] == COMMIT and data['parents'] == [], 'Unexpected commit identity/history')
    require(data['stats'] == {'total':215,'additions':215,'deletions':0}, 'Unexpected commit stats')
    require({f['filename'] for f in data['files']} == {'PlotModelComparison.m','RunModelComparison.m'}, 'Unexpected commit files')
    result = []
    for f in data['files']:
        lines = f['patch'].splitlines()
        require(f['status'] == 'added' and f['deletions'] == 0, 'Expected initial added file')
        require(lines[0] == '@@ -0,0 +1,'+str(f['additions'])+' @@', 'Unexpected patch header')
        require(all(line.startswith('+') or line == '\\ No newline at end of file' for line in lines[1:]), 'Unexpected patch line')
        added = [line[1:] for line in lines[1:] if line.startswith('+')]
        require(len(added) == f['additions'], 'Incomplete patch')
        raw = ('\n'.join(added)+('' if lines[-1] == '\\ No newline at end of file' else '\n')).encode()
        git_hash = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(git_hash == f['sha'], 'Provider patch does not reproduce declared Git blob')
        result.append({'filename':f['filename'],'lines':len(added),'bytes':len(raw),
                       'git_blob_sha1':git_hash,'sha256':hashlib.sha256(raw).hexdigest()})
    return result


def fingerprint(folder, record):
    name = record['filename']
    require(Path(name).name == name, 'Unsafe cache name')
    path = folder/name
    require(path.is_file() and path.stat().st_size == record['bytes'] and sha(path) == record['sha256'], 'Source identity mismatch: '+name)


def check_workbook(path, fields):
    ns = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        info = z.infolist()
        require(len(info) == len({x.filename for x in info}) and sum(x.file_size for x in info) < 4*1024*1024, 'Unsafe ZIP size/member collision')
        for x in info:
            p = PurePosixPath(x.filename)
            require(not p.is_absolute() and '..' not in p.parts and not x.flag_bits & 1, 'Unsafe ZIP member')
            require((x.external_attr >> 16) & 0o170000 != 0o120000, 'Symlink ZIP member')
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        cells = {c.get('r'):c for c in sheet.findall('m:sheetData/m:row/m:c',ns)}
        for address in ['D21','E21','G21','H21','I21','J21']:
            cell = cells.get(address)
            v = cell.find('m:v',ns) if cell is not None else None
            f = cell.find('m:f',ns) if cell is not None else None
            require({'value':v.text if v is not None else None,'formula':f.text if f is not None else None} == fields['selected_cells'][address], 'Workbook cell differs: '+address)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache',type=Path)
    parser.add_argument('--r29-cache',type=Path)
    parser.add_argument('--r28-cache',type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    public = read(package/'PUBLIC_FILES.json')['public_files']
    require(len(public) == len(set(public)) == 12 and all(Path(f).name == f for f in public), 'Public allowlist differs')
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()), 'Unexpected public directory or symlink')
    require({p.name for p in package.iterdir()} == set(public), 'Public file closure differs')
    covered = set()
    for line in (package/'SHA256SUMS.txt').read_text().splitlines():
        digest,name = line.split('  ',1)
        require(name in public and name not in covered and sha(package/name) == digest, 'Public hash differs: '+name)
        covered.add(name)
    require(covered == set(public)-{'SHA256SUMS.txt'}, 'Hash coverage incomplete')
    provenance = read(package/'SOURCE_PROVENANCE.json')
    require(len(provenance['calls']) == provenance['logical_scientific_calls'] <= provenance['logical_call_allocation'], 'Call accounting differs')
    require(sum(r['bytes'] for r in provenance['saved_acquisition_files']) == provenance['saved_acquisition_bytes'] <= provenance['byte_allocation'], 'Byte accounting differs')
    for rec in provenance['inherited_dependencies']:
        path = root/rec['path']
        require(path.stat().st_size == rec['bytes'] and sha(path) == rec['sha256'], 'Inherited dependency differs: '+rec['path'])
    study = read(root/'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(root/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(study) == 26 and all(v is None for v in study.values()), 'Study NULL guard failed')
    require(len(planning) == 18 and all(v is None for v in planning.values()), 'Planning NULL guard failed')
    fields = read(root/'research/summary_reconciliation/SOURCE_FIELDS.json')
    require(diagnostic(fields) == read(package/'CONDITIONAL_DIAGNOSTIC.json'), 'Conditional diagnostic differs')
    decision = read(package/'DECISION.json')
    require(decision['matched_panels_admitted'] == 0 and not any(decision[k] for k in ['new_biological_fit','author_values_replaced','missing_values_imputed','outreach_performed']), 'Decision guard failed')
    new_replay, old_replay, binary_replay = 'UNRUN: no R30 cache supplied','UNRUN: no R29 cache supplied','UNRUN: no R28 cache supplied'
    if args.source_cache:
        for rec in provenance['saved_acquisition_files']:
            fingerprint(args.source_cache,rec)
        captures = {c['call_id']:read(args.source_cache/c['capture_file']) for c in provenance['calls']}
        for c in provenance['calls']:
            cap = captures[c['call_id']]
            require(cap['args'] == c['arguments'] and cap['started'] == c['started_utc'] and cap['completed'] == c['completed_utc'], 'Capture provenance differs')
        reps = {k:representation(v) for k,v in captures.items()}
        require(reps['S01']['metadata']['numPages'] == reps['S01']['metadata']['totalPages'] == 9, 'Supplement coverage differs')
        for anchor in ['Differential equations for WSP, AWS, & MWS pathways','MATLAB code for interpreting saved data WSP vs MWS','MATLAB code for interpreting saved data WSP vs AWS']:
            require(anchor in reps['S01']['markdown'], 'Supplement anchor absent')
        for anchor in ['10.21769/BioProtoc.3407','https://github.com/ericlibby/BioProtocol','RunModelComparison','PlotModelComparison']:
            require(anchor in reps['S03']['markdown'], 'Protocol anchor absent')
        require(COMMIT in reps['S04']['markdown'], 'Repository commit anchor absent')
        require(commit_fields(reps['S05']['markdown']) == read(package/'RECORD_ASSESSMENT.json')['inspected_repository_files'], 'Repository facts differ')
        new_replay = 'PASS: capture identities, supplement coverage, protocol/repository linkage and both complete initial-commit patches reproduce declared Git blob hashes; source code not executed'
    if args.r29_cache:
        for rec in provenance['reused_capture_files']:
            fingerprint(args.r29_cache,rec)
        api = representation(read(args.r29_cache/'S04.json'))['markdown']
        for anchor in ['Source data files have been provided for Figures 6 and 9.','elife-38822-supp1-v1.pdf','elife-38822-transrepform-v1.docx']:
            require(anchor in api, 'Inherited source-link anchor absent')
        old_replay = 'PASS: reused R29 source identities and named availability/supplement anchors'
    if args.r28_cache:
        fingerprint(args.r28_cache,provenance['reused_workbook'])
        check_workbook(args.r28_cache/SOURCE_NAME,fields)
        binary_replay = 'PASS: reused exact R28 workbook identity and six row21 cell/formula fields'
    print(json.dumps({'status':'PASS','new_source_replay':new_replay,'inherited_source_replay':old_replay,
                      'reused_workbook_replay':binary_replay,'conditional_calculation':'PASS',
                      'study_nulls':26,'planning_nulls':18,'matched_panels_admitted':0,
                      'source_intended_aggregation_identified':False,'source_experimental_truth_validated':False},indent=2))


if __name__ == '__main__':
    main()
