#!/usr/bin/env python3
"""Authenticate external R23-R25 caches and recompute R26 artifact-cost facts.

Original code: Ricardo Maldonado with AI assistance. MIT under repository terms.
No network, R execution, variant replay, synthetic measurements or truth inference.
"""
import argparse
import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def check_pin(path, expected):
    data = path.read_bytes()
    check(len(data) == expected['bytes'], expected['source_id'] + ': byte count')
    check(digest(data) == expected['sha256'], expected['source_id'] + ': SHA256')
    return data


def catalogue(path):
    response = read_json(path)
    response = response.get('result', response)
    check(response.get('isError') is False, path.name + ': provider error')
    body = response['structuredContent']
    check(body['metadata']['statusCode'] == 200, path.name + ': HTTP status')
    rows = json.loads(body['rawHtml'])
    check(isinstance(rows, list), path.name + ': non-list catalogue')
    return rows


def verify(args):
    provenance = read_json(HERE / 'PROVENANCE.json')
    plan = read_json(HERE / 'ARTIFACT_PLAN.json')
    budget = read_json(HERE / 'SIZE_BOUNDED_REPLAY_PLAN.json')
    roots = {key: getattr(args, key) for key in ['r23', 'figures', 'r24', 'r25', 'r25_root']}
    source_data = {}
    for row in provenance['source_pins']:
        source_data[row['source_id']] = check_pin(roots[row['cache_group']] / row['filename'], row)
    for row in provenance['prior_analysis_pins']:
        check_pin(args.repo / row['repository_relative_path'], row)
    paras = ET.fromstring(source_data['r23:ptato_pmc10504672.xml']).findall('.//article/body//p')
    for row in provenance['article_paragraph_anchors']:
        para = paras[row['one_based_body_paragraph'] - 1]
        check(para.get('id') == row['xml_id'], 'article XML paragraph ID')
        check(digest(''.join(para.itertext()).strip().encode()) == row['paragraph_sha256'], 'article paragraph hash')
    for row in provenance['code_anchors']:
        lines = source_data[row['source_id']].splitlines(keepends=True)
        block = b''.join(lines[row['start_line_1based'] - 1:row['end_line_1based']])
        check(digest(block) == row['exact_line_bytes_sha256'], 'code block hash')

    # Reconstruct official paths independently from cached folder parentage.
    folders = catalogue(args.r25 / 'mendeley_folders_v1_firecrawl.json')
    by_id = {r['id']: r for r in folders}
    check(len(by_id) == len(folders), 'duplicate folder ID')

    def folder_path(fid, ancestors=()):
        check(fid not in ancestors, 'folder cycle')
        row = by_id[fid]
        parent = row.get('parent_id')
        return (folder_path(parent, ancestors + (fid,)) + '/' if parent else '') + row['name']

    paths = {fid: folder_path(fid) for fid in by_id}
    check(len(set(paths.values())) == len(paths), 'duplicate folder path')
    inventory = read_json(args.repo / 'research/processed_input_audit/MANIFEST_AUDIT.json')
    all_rows = {}
    for scoped in inventory['scoped_file_inventories']:
        name = scoped['response_cache']
        cache = args.r25_root if name in {'msh2_callable_manifest.json', 'msh2_snvs_callable_manifest.json', 'fancc_snvs_callable_manifest.json'} else args.r25
        rows = catalogue(cache / name)
        check(len(rows) < 1000, 'unresolved inventory pagination')
        check(len(rows) == scoped['direct_file_records'], 'inventory row count')
        for row in rows:
            check(paths[row['folder_id']] == scoped['path'], 'file outside declared directory')
            check(row['id'] not in all_rows, 'repeated file ID')
            all_rows[row['id']] = (scoped['path'], row)
    for row in catalogue(args.r24 / 'mendeley_root_files_v1_firecrawl.json'):
        check(row['id'] not in all_rows, 'repeated root file ID')
        all_rows[row['id']] = ('', row)

    objects = plan['scoped_SNV_objects']
    check(len(objects) == 18, 'scoped object count')
    check(len({r['object_id'] for r in objects}) == 18, 'duplicate scoped object ID')
    known = []
    for obj in objects:
        if obj['catalogue_file_id'] is None:
            check(obj['catalogue_bytes'] is None and obj['catalogue_sha256'] is None, 'unknown object assigned size/hash')
            check(not obj['exact_path_known'], 'unknown object assigned exact path')
            continue
        directory, source = all_rows[obj['catalogue_file_id']]
        official = source['content_details']
        check(obj['catalogue_bytes'] == official['size'], 'object catalogue bytes')
        check(obj['catalogue_sha256'] == official['sha256_hash'], 'object catalogue SHA256')
        expected_path = (directory + '/' if directory else '') + source['filename']
        check(obj['required_source_path_or_pattern'] == expected_path, 'object exact path')
        known.append(obj)
    table_object = next(o for o in objects if o['object_id'] == 'S01')
    table_bytes = source_data['r24:Table_S2.txt']
    check(digest(table_bytes) == table_object['catalogue_sha256'], 'Table S2 content/catalogue hash')
    check(len(table_bytes) == table_object['catalogue_bytes'], 'Table S2 content/catalogue size')
    fancc = next(o for o in objects if o['object_id'] == 'S07')
    fancc_files = [r for directory, r in all_rows.values() if directory == 'PMCAHH1-FANCCKO/PTATO/snvs_callable']
    check(len(fancc_files) == 3, 'FANCC inspected direct-file count')
    check(not any(r['filename'].endswith(fancc['sample']+'.snvs.ptato.callable.vcf.gz') for r in fancc_files), 'FANCC missing-object scope changed')

    metadata = list(csv.DictReader(table_bytes.decode().splitlines(), delimiter='\t'))
    pta = [r for r in metadata if r['Type'] == 'PTA']
    subclones = [r for r in metadata if r['Type'] == 'Subclone']
    all_cell_lines = {r['Cell_line'] for r in metadata if r['Cell_line'] != 'PMCAHH1'}
    pta_cell_lines = {r['Cell_line'] for r in pta}
    check(len(pta) == 4 and len(subclones) == 5, 'PTA/subclone sample counts')
    check(len(all_cell_lines) == 5 and len(pta_cell_lines) == 3, 'whole/scoped cell-line counts')
    extras = plan['whole_script_additional_dataset_objects']
    check(len(extras) == len(all_cell_lines - pta_cell_lines) + len(subclones) + len(pta) + 5, 'whole-script dependency count')
    check({x['sample'] for x in extras if x['role'] == 'subclone_somatic_SNV_and_indel'} == {x['Sample'] for x in subclones}, 'subclone object coverage')
    check({x['sample'] for x in extras if x['role'] == 'PTA_indel'} == {x['Sample'] for x in pta}, 'PTA indel coverage')
    figure_lines = source_data['figures:Figure2.R'].decode().splitlines()
    resource_anchors = {148:'Indels/excludelist_v1.vcf',156:'Indels/Indel_RecurrencyList_Info.txt',410:'PMCAHH1_SCAN2_SNV_Burden.txt',767:'Resources/PTA_Artefact_Signature.txt',971:'Indels/IndelExclusionList.rds'}
    for line, token in resource_anchors.items():
        check(token in figure_lines[line-1] and not figure_lines[line-1].lstrip().startswith('#'), 'active resource read anchor')
    for line, token in {63:'Metadata$Type == "PTA"',103:'length(indel_vcf_file) == 1',117:'"Subclone"',218:'unique(Metadata$Cell_line'}.items():
        check(token in figure_lines[line-1], 'active metadata dependency anchor')

    calculated = {'logical_scoped_SNV_objects':len(objects),'catalogued_with_sizes_and_hashes':len(known),'content_authenticated':sum(o['content_authenticated_in_cache'] for o in objects),'not_content_acquired':sum(not o['content_authenticated_in_cache'] for o in objects),'objects_without_known_size_or_hash':len(objects)-len(known),'known_byte_subtotal_including_cached_Table_S2':sum(o['catalogue_bytes'] for o in known),'known_unacquired_byte_subtotal':sum(o['catalogue_bytes'] for o in known if not o['content_authenticated_in_cache']),'full_scoped_byte_total':None,'four_PTA_BED_byte_subtotal':sum(o['catalogue_bytes'] for o in known if o['role']=='PTA_callable_intervals'),'whole_script_extra_dataset_objects':len(extras),'whole_script_minimum_dataset_objects':len(objects)+len(extras)}
    check(calculated == plan['summary'], 'derived artifact summary')
    pilot = budget['scope_alternatives'][1]
    selected = [o for o in objects if o['object_id'] in pilot['object_ids']]
    check(len(selected) == 5, 'five-object pilot')
    pilot_known_bytes = sum(o['catalogue_bytes'] or 0 for o in selected)
    check(pilot_known_bytes == pilot['known_bytes_lower_bound'], 'pilot known subtotal')
    check(sum(o['catalogue_bytes'] is None for o in selected) == 1, 'pilot unknown object count')
    payload_cap = budget['future_reopening_gates'][2]['max_new_payload_bytes']
    check(pilot_known_bytes > payload_cap, 'original-file pilot cannot fit payload cap')
    decision = read_json(HERE/'TRUTH_ADMISSION_DECISION.json')
    check(not decision['numerical_PTATO_accuracy_computed'], 'unrun numerical status')
    return {'record_id':'R000026','status':'PASS_CACHED_IDENTITIES_DEPENDENCIES_AND_SIZE_FACTS_ONLY','source_pins_verified':len(source_data),'prior_analysis_pins_verified':len(provenance['prior_analysis_pins']),'article_paragraph_hashes_verified':len(provenance['article_paragraph_anchors']),'code_range_hashes_verified':len(provenance['code_anchors']),'folder_records_checked':len(folders),'direct_directory_file_records_checked':sum(x['direct_file_records'] for x in inventory['scoped_file_inventories']),'root_file_records_checked':4,'summary':calculated,'pilot_known_bytes':pilot_known_bytes,'code_executed_R':False,'genotype_or_BED_content_replayed':False,'independent_truth_validated':False,'new_network_calls':0,'review_limit':'Identity and dependency verification, not scientific adjudication or successful whole-script execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=HERE.parents[1], help='Repository root containing prior public analysis packages')
    for name in ['r23','figures','r24','r25','r25_root']:
        parser.add_argument('--'+name.replace('_','-'), dest=name, type=Path, required=True, help='External cache root for '+name+' source group in PROVENANCE.json')
    args = parser.parse_args()
    try:
        result = verify(args)
    except (OSError, ValueError, KeyError, IndexError, ET.ParseError) as exc:
        # OSError path may be private, so do not echo exception text or local paths.
        print(json.dumps({'record_id':'R000026','status':'FAILED_OR_UNRUN','error_type':type(exc).__name__,'reason':'Required cache/pin/schema/dependency verification failed; no passing source verification or numerical claim is available.'}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
