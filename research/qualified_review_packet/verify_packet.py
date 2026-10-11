#!/usr/bin/env python3
"""MIT: read-only verification of the unfilled R28 review checkpoint; no network."""
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

CHECKS = 0


def require(condition, message):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_identity(path, record):
    require(path.is_file() and not path.is_symlink(), 'Missing/nonregular file: '+str(path))
    require(path.stat().st_size == record['bytes'], 'Byte mismatch: '+path.name)
    require(digest(path) == record['sha256'], 'SHA256 mismatch: '+path.name)


def check_worksheet(sheet, study, native):
    expected = [('S', 'research/prospective_design/REGISTRY_CANDIDATE.json', study['study_inputs_requiring_resolution']),
                ('N', 'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json', native['actual_values'])]
    expected_rows = [(f'{prefix}{i:02d}', source, field) for prefix, source, fields in expected
                     for i, field in enumerate(fields, 1)]
    rows = sheet['field_rows']
    require(len(rows) == 44, 'Expected exactly 44 registry questions')
    require([(r['id'], r['registry_path'], r['registry_field']) for r in rows] == expected_rows,
            'Registry question coverage/order drift')
    require(sheet['mandatory_categories'] == study['mandatory_outcome_ledger_categories'], 'Outcome category drift')
    require(sheet['preserved_axis'] == [1, 0, -1], 'Frozen axis drift')
    response_slots = ('actual_answer', 'evidence_supplied', 'reviewer_decision', 'decision_rationale', 'reviewer_identity_and_qualification')
    for r in rows:
        for slot in response_slots:
            require(slot in r and r[slot] is None, 'Worksheet response must remain explicit NULL: '+r['id']+'/'+slot)
        require(isinstance(r.get('suggested_review_expertise'), str) and len(r['suggested_review_expertise']) > 2, 'Missing suggested expertise')
        for slot in ('reviewer_question', 'minimum_evidence_deliverable', 'acceptance_condition', 'refusal_trigger'):
            require(isinstance(r.get(slot), str) and len(r[slot]) > 20, 'Missing substantive reviewer field: '+r['id']+'/'+slot)
    gates = {g['id']:g for g in sheet['gates']}
    require(len(gates) == len(sheet['gates']) == 8, 'Duplicate/missing gates')
    order = sheet['gate_order']
    require(len(order) == len(set(order)) == 8 and set(order) == set(gates), 'Invalid gate order')
    for g in sheet['gates']:
        require(g['current_evidence_decision'] == 'NOT_ADMITTED', 'Gate promoted without scientific admission')
        for slot in ('qualified_reviewer_decision','supporting_evidence','remaining_measurements','reviewer'):
            require(g[slot] is None, 'Qualified gate response must remain NULL')
        require(len(g['depends_on']) == len(set(g['depends_on'])), 'Duplicate gate dependency')
        require(all(d in gates and order.index(d) < order.index(g['id']) for d in g['depends_on']), 'Cycle or forward gate dependency')
        require(all(r['gate'] in gates for r in rows), 'Unknown row gate')
    required = {'G0':[], 'O1':['G0'], 'O2':['O1'], 'O3':['O2'], 'O4':['O3'],
                'B1':['G0','O1'], 'B2':['B1','O2'], 'B3':['B2','O3','O4']}
    require({k:gates[k]['depends_on'] for k in gates} == required, 'Admission dependency boundary drift')
    require(all(gates[k]['branch'] == 'observed_prediction' for k in ['O1','O2','O3','O4']), 'Observed branch drift')
    require(all(gates[k]['branch'] == 'biological_origin_interpretation' for k in ['B1','B2','B3']), 'Biological branch drift')


def rejected_mutation(sheet, study, native, mutate, name):
    changed=copy.deepcopy(sheet)
    mutate(changed)
    try:
        check_worksheet(changed, study, native)
    except (ValueError, KeyError):
        return name
    raise ValueError('Negative fixture unexpectedly accepted: '+name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    args=parser.parse_args()
    require(sys.flags.optimize == 0, 'Run without -O/-OO')
    package=Path(__file__).resolve().parent
    root=package.parent.parent
    study=read(root/'research/prospective_design/REGISTRY_CANDIDATE.json')
    native=read(root/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')
    require(len(study['study_inputs_requiring_resolution']) == 26 and all(v is None for v in study['study_inputs_requiring_resolution'].values()), '26 original study NULLs changed')
    require(len(native['actual_values']) == 18 and all(v is None for v in native['actual_values'].values()), '18 original native NULLs changed')
    priors=read(package/'PRIOR_ARTIFACTS.json')['files']
    require(len({x['path'] for x in priors}) == len(priors) == 10, 'Prior input coverage mismatch')
    for r in priors:
        require(not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts, 'Unsafe prior path')
        check_identity(root/r['path'],r)
    sheet=read(package/'REVIEW_WORKSHEET.json')
    check_worksheet(sheet,study,native)
    negative=[]
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['field_rows'].pop(),'missing_registry_field'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['field_rows'][0].update(actual_answer='published strain ID'),'source_ID_cannot_fill_actual_value'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['field_rows'][0].pop('evidence_supplied'),'missing_explicit_evidence_slot'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['mandatory_categories'].remove('unresolved_classification'),'unresolved_category_cannot_be_dropped'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['gates'][0]['depends_on'].append('B3'),'cyclic_admission_dependencies'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['gates'][7].update(depends_on=['O4']),'prediction_cannot_bypass_origin_gates'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['gates'][4]['depends_on'].append('B1'),'origin_not_automatic_observed_prediction_requirement'))
    negative.append(rejected_mutation(sheet,study,native,lambda x:x['gates'][2].update(current_evidence_decision='ACCEPTED'),'unreviewed_establishment_admission'))
    resources=read(package/'RESOURCE_FEASIBILITY.json')
    require(resources['status'] == 'UNPRICED_UNCOMMISSIONED', 'Resource status drift')
    require(len(resources['items']) == 6 and len({r['id'] for r in resources['items']}) == 6, 'Resource coverage mismatch')
    for r in resources['items']:
        for field in ('capacity_available','quantity_of_independent_units','instrument_or_assay_hours','storage_requirement','cost_and_currency','lead_time','access_or_license_evidence','assigned_partner','qualified_feasibility_decision'):
            require(r[field] is None, 'Resource answer/quantity must remain NULL')
        require(all(g in sheet['gate_order'] for g in r['gates']), 'Unknown resource gate')
    decision=read(package/'DECISION.json')
    require(decision['preserved_blockers'] == ['R5','R11','R17'], 'Prior blocker drift')
    for key in ('observed_prediction_admitted','biological_origin_interpretation_admitted','qualified_external_review_completed','outreach_performed','laboratory_protocol_or_partner_selected','forecasts_eta_count_law_error_stopping_changed','paused_runner_changed','methods_0_6_0_changed','new_theorem_or_priority_claim','new_zenodo_release_justified'):
        require(decision[key] is False, 'Unsupported advancement: '+key)
    for key in ('actual_study_inputs_resolved','native_planning_inputs_resolved','admitted_matched_panels','new_biological_observations'):
        require(decision[key] == 0, 'Unsupported scientific result: '+key)
    provenance=read(package/'SOURCE_PROVENANCE.json')
    require(provenance['logical_science_calls'] == decision['logical_science_calls'] == 2, 'Source call count mismatch')
    require(provenance['failed_science_calls'] == decision['failed_science_calls'] == 0, 'Failure count mismatch')
    require(sum(r['bytes'] for r in provenance['response_files']) == provenance['counted_response_bytes'] == decision['counted_response_bytes'] == 215614, 'Source byte accounting mismatch')
    source_replay='UNRUN: optional source cache not supplied; source interpretation not authenticated by public-only replay'
    if args.source_cache is not None:
        cache=args.source_cache
        for record in provenance['response_files']+[provenance['primary_source']['representation_file']]:
            require(Path(record['path']).name == record['path'], 'Unsafe source cache path')
            check_identity(cache/record['path'],record)
        response=read(cache/'primary_response.json')
        body=response.get('structuredContent')
        if not isinstance(body,dict) or 'markdown' not in body:
            body=json.loads(next(x['text'] for x in response['content'] if x.get('type')=='text'))
        md=(cache/'PMC10973407.md').read_text()
        require(md.rstrip('\n') == body['markdown'].rstrip('\n'), 'Extracted representation differs from full response')
        require(body['metadata']['statusCode'] == 200, 'Primary HTTP response was not successful')
        require(body['metadata']['citation_doi'] == '10.1038/s41467-024-46950-0', 'Primary article DOI mismatch')
        lines=md.splitlines()
        anchors=provenance['primary_source']['anchors']
        require(len(anchors) == len({x['id'] for x in anchors}) == 13, 'Anchor coverage mismatch')
        for anchor in anchors:
            line=lines[anchor['line_1based']-1]
            require(line.startswith(anchor['prefix']), 'Anchor prefix mismatch: '+anchor['id'])
            require(hashlib.sha256(line.encode()).hexdigest() == anchor['line_sha256'], 'Anchor hash mismatch: '+anchor['id'])
        search=read(cache/'search_result.json')
        require(len(search['structuredContent']['results']) == 5, 'Search result count mismatch')
        source_replay='PASS: exact stored provider responses, derived representation and 13 anchors; no raw experiment/PDF replay'
    public=read(package/'PUBLIC_FILES.json')
    names=public['public_files']
    require(len(names)==len(set(names)), 'Duplicate public files')
    require(set(names)=={p.name for p in package.iterdir()}, 'Public allowlist mismatch')
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()), 'Unexpected directory/symlink in public package')
    excluded={'PUBLIC_FILES.json','SHA256SUMS.txt','VERIFICATION_RECEIPT.json'}
    records=public['files']
    require(len(records)==len({r['path'] for r in records}) and {r['path'] for r in records}==set(names)-excluded, 'Public core coverage mismatch')
    for record in records:
        require(Path(record['path']).name==record['path'], 'Unsafe public path')
        check_identity(package/record['path'],record)
    sums={}
    for line in (package/'SHA256SUMS.txt').read_text().splitlines():
        value,name=line.split('  ',1)
        require(name in names and Path(name).name==name and name not in sums, 'Unsafe/duplicate checksum file')
        require(digest(package/name)==value, 'Public checksum mismatch: '+name)
        sums[name]=value
    require(set(sums)==set(names)-{'SHA256SUMS.txt','VERIFICATION_RECEIPT.json'}, 'Incomplete public checksum coverage')
    print(json.dumps({'status':'PASS','checks':CHECKS,'negative_fixtures_rejected':negative,'study_NULLs':26,'native_planning_NULLs':18,'worksheet_rows':44,'gates':8,'resource_items':6,'source_replay':source_replay,'scientific_admission':False,'qualified_external_review':False,'scope':'Read-only checkpoint consistency, preservation and optional source identity; not a future filled-worksheet admission validator.'},indent=2))


if __name__=='__main__':
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError, StopIteration) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc),'checks_before_failure':CHECKS}),file=sys.stderr)
        raise SystemExit(1)
