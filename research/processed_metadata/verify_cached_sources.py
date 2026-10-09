#!/usr/bin/env python3
"""Replay the R24 metadata audit from exact local sources; never fetch or write.

Copyright (c) 2026 Ricardo Maldonado. Original checker code: MIT.
External source content remains under its own terms and is not included.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--figure-code', type=Path, required=True)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    provenance = json.loads((package / 'PROVENANCE.json').read_text())
    audit = json.loads((package / 'METADATA_AUDIT.json').read_text())
    admission = json.loads((package / 'ADMISSION_UPDATE.json').read_text())
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def content(filename):
        response = json.loads((args.cache / filename).read_text())
        response = response.get('result', response)
        if 'structuredContent' in response:
            return response['structuredContent']
        return json.loads(next(item['text'] for item in response['content'] if item['type'] == 'text'))

    for source in provenance['source_pins']:
        raw = (args.cache / source['cache_filename']).read_bytes()
        check('byte_size:' + source['cache_filename'], len(raw) == source['bytes'])
        check('sha256:' + source['cache_filename'], hashlib.sha256(raw).hexdigest() == source['sha256'])

    page = content('mendeley_v1_firecrawl.json')
    state_match = re.search(r'window.INITIAL_STATE = (.*?)\n\s*window.initialTime', page['rawHtml'], re.S)
    check('official_page_state_present', state_match is not None)
    snapshot = json.loads(state_match.group(1))['dataset']['snapshot']
    expected = provenance['processed_dataset']
    for key, source_key in [('doi', 'doi'), ('version', 'version'), ('name', 'name'), ('published_at', 'publish_date')]:
        check('dataset:' + key, expected[key] == snapshot[source_key])
    check('dataset_specific_license', snapshot['licence']['short_name'] == expected['license_id'] == 'CC BY 4.0')
    check('dataset_license_link', snapshot['licence']['url'] == expected['license_url'])
    check('dataset_license_third_party_caveat', 'third party' in snapshot['licence']['description'])
    check('dataset_confidential_flag', snapshot['is_confidential'] is expected['is_confidential_metadata_value'] is False)

    catalog = json.loads(content('mendeley_root_files_v1_firecrawl.json')['rawHtml'])
    catalog_by_name = {record['filename']: record for record in catalog}
    check('four_root_file_records', len(catalog) == len(catalog_by_name) == 4)
    for record in provenance['root_file_records']:
        actual = catalog_by_name[record['filename']]
        check('root_record:' + record['filename'], record == {
            'filename': actual['filename'], 'id': actual['id'],
            'content_id': actual['content_details']['id'], 'bytes': actual['size'],
            'sha256': actual['content_details']['sha256_hash'],
            'view_url': actual['content_details']['view_url']
        })

    tables = {}
    for number in (1, 2):
        name = f'Table_S{number}.txt'
        raw = (args.cache / name).read_bytes()
        returned = content(f'mendeley_Table_S{number}_firecrawl.json')['rawHtml'].encode('utf-8')
        details = catalog_by_name[name]['content_details']
        check('raw_field_exact_bytes:' + name, returned == raw)
        check('official_size:' + name, len(raw) == details['size'])
        check('official_sha256:' + name, hashlib.sha256(raw).hexdigest() == details['sha256_hash'])
        table = list(csv.DictReader(io.StringIO(raw.decode('utf-8')), delimiter='\t'))
        tables[number] = table
        expected = audit[f'Table_S{number}']
        check('dimensions:' + name, len(table) == expected['data_rows'] and all(len(row) == expected['columns'] and None not in row and None not in row.values() for row in table))
        check('sample_identifiers_unique:' + name, len({row['Sample'] for row in table}) == len(table))
        check('type_counts:' + name, dict(Counter(row['Type'] for row in table)) == expected['type_counts'])
        check('training_counts:' + name, dict(Counter(row['Training'] for row in table)) == expected['training_counts'])

    table = tables[1]
    expected = audit['Table_S1']
    yes = {row['Individual'] for row in table if row['Training'] == 'Yes'}
    no = {row['Individual'] for row in table if row['Training'] == 'No'}
    check('nonmissing_individual_labels', all(row['Individual'] not in ('', 'NA') for row in table))
    check('training_yes_type_counts', dict(Counter(row['Type'] for row in table if row['Training'] == 'Yes')) == expected['training_yes_type_counts'])
    check('source_counts', dict(Counter(row['Source'] for row in table)) == expected['source_row_counts'])
    check('individual_label_counts', [len(yes | no), len(yes), len(no), len(yes & no)] == [expected['distinct_individual_labels'], expected['distinct_individual_labels_with_training_yes'], expected['distinct_individual_labels_with_training_no'], expected['individual_labels_in_both_training_flags']])

    code = args.figure_code.read_bytes()
    check('figure_code_sha256', hashlib.sha256(code).hexdigest() == provenance['cached_figure_code']['sha256'])
    lines = code.decode().splitlines()
    check('recovery_loop_uses_all_pta_rows', lines[1373].strip() == 'for(Sample in Metadata$Sample[ Metadata$Type == "PTA"]){')
    check('predecessor_rule_code', 'Previous_Clone <- Metadata$Sample[Metadata$Days_after_clone == max(' in lines[1382])
    table = tables[2]
    pta = [row for row in table if row['Type'] == 'PTA']
    check('pta_training_counts', dict(Counter(row['Training'] for row in pta)) == audit['Table_S2']['pta_training_counts'])
    expected_rows = audit['Table_S2']['pta_metadata_to_code_join']
    check('four_joined_pta_rows', len(expected_rows) == len(pta) == 4)
    for row, expected in zip(pta, expected_rows):
        index = table.index(row) + 1
        peers = [candidate for candidate in table if candidate['Clone'] == row['Clone'] and candidate['Sample'] != row['Sample']]
        maximum = max(int(peer['Days_after_clone']) for peer in peers)
        previous = [peer for peer in peers if int(peer['Days_after_clone']) == maximum]
        check(f'unique_predecessor:data_row_{index}', len(previous) == 1)
        check(f'day_mapping:data_row_{index}', (
            index == expected['metadata_data_row'] and row['Label'] == expected['metadata_label']
            and previous[0]['Label'] == expected['previous_sample_metadata_label_under_code_rule']
            and previous[0]['Training'] == expected['previous_sample_training_flag']
            and maximum == expected['previous_sample_days_after_clone']
            and int(row['Days_after_clone']) == expected['sample_days_after_clone']
            and int(row['Days_after_sort']) == expected['sample_days_after_sort']
            and int(row['Days_after_clone']) - maximum == expected['code_predecessor_day_difference'] == int(row['Days_after_sort'])
            and expected['days_after_sort_matches_predecessor_difference'] is True
            and row['Training'] == expected['training_flag']
        ))
        assignment = lines[expected['figure_code_line'] - 1]
        code_label = assignment.rsplit('<-', 1)[1].strip().strip('"').replace('\\n', '')
        check(f'code_label:data_row_{index}', 'Overview_CloneVariants$ID[' in assignment and row['Sample'] in assignment and code_label == expected['figure_code_label'] and (row['Label'] == code_label) == expected['label_agrees'])
    check('two_wt_label_disagreements', sum(not row['label_agrees'] for row in expected_rows) == 2)

    check('error400_not_manifest', json.loads(content('mendeley_files_v1_firecrawl.json')['rawHtml']) == {'error': 400})
    check('folder404_not_manifest', content('mendeley_folders_v1_firecrawl.json')['metadata']['statusCode'] == 404)
    check('six_agent_calls', len(provenance['data_access_agent_calls']) == provenance['data_access_agent_call_count'] == 6)
    check('serialized_byte_total', sum(call['returned_serialized_bytes'] for call in provenance['data_access_agent_calls']) == provenance['data_access_agent_serialized_returned_bytes'] == 1078560)
    check('nine_partial_or_unsatisfied_gates', len(admission['gates']) == 9 and all(gate['status'] in ('PARTIALLY_VERIFIED', 'NOT_SATISFIED') for gate in admission['gates']))
    check('no_benchmark_or_external_review_claim', all(admission[key] is False for key in ('genotype_stage_numerical_benchmark_admitted', 'native_origin_benchmark_admitted', 'native_origin_truth_inferred', 'numerical_replication_obtained', 'qualified_external_review_obtained')))
    check('no_actual_fields_or_design_changes_claimed', admission['actual_bacterial_registry_fields_resolved'] == admission['native_control_planning_fields_resolved'] == admission['admitted_matched_WAM_biological_datasets'] == 0 and admission['confirmatory_design_changes'] == [])
    print(json.dumps({
        'record_id': 'R000024', 'verified_at_utc': datetime.now(timezone.utc).isoformat(),
        'success': True, 'checks_passed': len(checks), 'source_files_verified': len(provenance['source_pins']),
        'Table_S1_dimensions': [len(tables[1]), len(tables[1][0])],
        'Table_S2_dimensions': [len(tables[2]), len(tables[2][0])],
        'official_table_hashes_verified': True, 'wt_label_disagreements_reproduced': 2,
        'source_checks': checks, 'numerical_genotype_benchmark_reproduced': False,
        'native_origin_benchmark_admitted': False, 'qualified_external_review_obtained': False
    }, indent=2))


if __name__ == '__main__':
    main()
