#!/usr/bin/env python3
"""Read-only R33 package/capture checks. No network, source-code execution or fit."""
import argparse
import hashlib
import json
import re
from pathlib import Path

F = Path(__file__).resolve().parent
R = F.parents[1]

def read(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('Duplicate JSON key: ' + key)
            out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)

def require(ok, label):
    if not ok:
        raise ValueError(label)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def identity(path, item):
    require(path.is_file() and not path.is_symlink(), 'Regular file: ' + path.name)
    require(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], 'Identity: ' + path.name)

def norm(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text.replace('*', ''))).strip()

def rep(path):
    w = read(path)
    result = w.get('result', w)
    d = result.get('structuredContent')
    if isinstance(d, dict) and d:
        return d
    for block in result.get('content', []):
        if block.get('type') == 'text':
            try:
                d = json.loads(block['text'])
            except (ValueError, TypeError):
                continue
            if isinstance(d, dict):
                return d
    raise ValueError('Missing representation: ' + path.name)

def cache(cache_path, calls):
    require(len(calls) == len({x['filename'] for x in calls}), 'Unique capture names')
    for item in calls:
        name = item['filename']
        require(Path(name).name == name and name not in ('.', '..'), 'Safe capture name')
        p = cache_path / name
        identity(p, item)
        w = read(p)
        require(w.get('args', w.get('arguments')) == item['arguments'], 'Exact call arguments: ' + name)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--watch-cache', type=Path)
    parser.add_argument('--local-cache', type=Path)
    args = parser.parse_args()
    p = read(F / 'SOURCE_PROVENANCE.json')
    a = read(F / 'ASSESSMENT.json')
    d = read(F / 'DECISION.json')
    require(len(p['calls']) == p['logical_scientific_calls'] == p['logical_call_allocation'] == 6, 'Six own calls')
    require(sum(x['bytes'] for x in p['calls']) == p['saved_acquisition_bytes'] == 375661 <= p['byte_allocation'], 'Own bytes')
    require(p['shared_root']['logical_scientific_calls'] == len(p['shared_root']['calls']) == 4, 'Four root calls')
    require(p['shared_local']['logical_scientific_calls'] == len(p['shared_local']['calls']) == 2, 'Two local calls')
    for key, total in [('shared_root', 261765), ('shared_local', 31532)]:
        require(sum(x['bytes'] for x in p[key]['calls']) == p[key]['saved_acquisition_bytes'] == total, key + ' bytes')
        require(not p[key]['counted_in_own_totals'], 'No double counting')
    require(p['round_unique_logical_scientific_calls'] == 12 and p['round_unique_saved_bytes'] == 668958, 'Round accounting')
    require(a['source']['doi'] == '10.1128/aem.02179-25' and not a['source']['native_Wsp_Aws_Mws'], 'Primary context')
    require(a['calibration']['implemented'] and a['calibration']['physical_material'] == 'pre-extracted genomic DNA', 'DNA standard')
    require(a['orthogonal_validation']['shares_extraction_with_sequencing'] and not a['orthogonal_validation']['independently_replayed'], 'Shared extraction')
    require(not a['source_values_imported_into_TMD'] and not a['new_mathematical_theorem'], 'No import or theorem')
    require(not a['resource']['actual_fastq_downloaded'] and not a['resource']['barcode_replicate_calibration_crosswalk_acquired'], 'Metadata only')
    s = a['synthetic_rdna_resource']
    require(s['source']['doi'] == '10.1093/ismeco/ycaf028' and s['source']['publication_date_corrected'] == '2025-02-11', 'Synthetic primary/date')
    require(s['calibration']['implemented'] and s['calibration']['constructs'] == 12 and s['calibration']['bacterial_SSU_V4_compatible_constructs'] == 2, 'Synthetic constructs')
    require(s['TMD_admission']['records_admitted'] == 0 and s['TMD_admission']['all_44_actual_fields_stay_null'] and not s['TMD_admission']['stock_or_native_route_calibration_admitted'], 'Synthetic no admission')
    require(s['deposited_resource']['original_file_bytes_downloaded'] == 0 and not s['deposited_resource']['source_code_run'] and not s['deposited_resource']['source_counts_replayed'], 'Deposit metadata only')
    require(a['independent_primary_evidence_families_total'] == 2, 'Two primary evidence families')
    for key in ['study_fields_resolved','planning_fields_resolved','matched_panels_admitted','independent_mutation_events_admitted','calibration_records_admitted']:
        require(d[key] == 0, 'Zero admission: ' + key)
    for key in ['methods_archive_changed','frozen_core_changed','native_thresholds_or_stopping_changed']:
        require(not d[key], 'Frozen: ' + key)
    for item in p['inherited_dependencies']:
        name = Path(item['path'])
        require(not name.is_absolute() and '..' not in name.parts, 'Safe dependency')
        identity(R / name, item)
    actual = read(R / 'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(R / 'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(actual) == 26 and all(v is None for v in actual.values()), '26 NULL study values')
    require(len(planning) == 18 and all(v is None for v in planning.values()), '18 NULL planning values')
    public = read(F / 'PUBLIC_FILES.json')['public_files']
    require(len(public) == len(set(public)) == 11, 'Eleven public members')
    require(all(Path(n).name == n and n not in ('.', '..') for n in public), 'Safe public names')
    require(set(public) == {x.name for x in F.iterdir()} and all(x.is_file() and not x.is_symlink() for x in F.iterdir()), 'Exact public closure')
    covered = set()
    for line in (F / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name in public and name not in covered, 'Checksum membership')
        require(sha(F / name) == digest, 'Checksum: ' + name)
        covered.add(name)
    require(covered == set(public) - {'SHA256SUMS.txt'}, 'Complete checksum coverage')

    own = 'UNRUN: own source cache not supplied'
    if args.source_cache:
        cache(args.source_cache, p['calls'])
        require(rep(args.source_cache / '01_harrison_review_passages.json')['passages'] == [], 'Review unavailable')
        require(len(rep(args.source_cache / '02_primary_standard_discovery.json')['data']['web']) == 5, 'Five search excerpts')
        maintext = rep(args.source_cache / '03_portable_protocol_primary.json')
        require(maintext['metadata']['citation_doi'] == a['source']['doi'] and maintext['metadata']['statusCode'] == 200, 'Primary identity')
        for anchor in a['selected_primary_anchors']:
            require(norm(anchor['text']) in norm(maintext['markdown']), 'BSINC anchor: ' + anchor['id'])
        require('Creative Commons Attribution 4.0 International license' in maintext['markdown'], 'Primary rights')
        err = read(args.source_cache / '04_portable_protocol_supplement.json')['result']
        require(err['isError'] and err['structuredContent']['error_code'] == 'INVALID_ARGUMENT', 'Unacquired supplement')
        project = rep(args.source_cache / '05_bioproject_sra_records.json')
        require('Items: 1 to 20 of 218' in project['markdown'], 'Partial project page')
        nano = rep(args.source_cache / '06_nanopore_sra_records.json')
        require(nano['metadata']['ncbi_resultcount'] == '3', 'Three Nanopore summaries')
        for record in a['resource']['nanopore_summaries']:
            require('Accession: ' + record['experiment'] in nano['markdown'] and record['rounded_bases_display'] + ' bases' in nano['markdown'], 'SRA metadata: ' + record['experiment'])
        own = 'PASS: capture identities and selected primary/SRA/error anchors; no sequence, supplement or experimental replay'

    watch = 'UNRUN: shared root cache not supplied'
    if args.watch_cache:
        cache(args.watch_cache, p['shared_root']['calls'])
        require(rep(args.watch_cache / 'S03.json')['passages'] == [], 'LRQ indexed full text unavailable')
        lrq = rep(args.watch_cache / 'S02.json')
        require(lrq['metadata']['statusCode'] == 429, 'LRQ PDF blocked')
        rdna = rep(args.watch_cache / 'S04.json')
        require(rdna['metadata']['citation_doi'] == '10.1093/ismeco/ycaf028', 'rDNA primary identity')
        for anchor in a['synthetic_rdna_resource']['selected_primary_anchors']:
            require(norm(anchor['text']) in norm(rdna['markdown']), 'rDNA anchor: ' + anchor['id'])
        watch = 'PASS: reused root identities, rDNA primary anchors and bounded LRQ failures only'

    local = 'UNRUN: shared correction/deposit cache not supplied'
    if args.local_cache:
        cache(args.local_cache, p['shared_local']['calls'])
        correction = rep(args.local_cache / 'S01.json')
        require('11 February 2025 (not 17 March 2025)' in correction['markdown'], 'Publication-date correction')
        require(correction['metadata']['citation_doi'] == '10.1093/ismeco/ycaf112', 'Correction identity')
        deposit_text = rep(args.local_cache / 'S02.json')['markdown'].strip()
        if deposit_text.startswith('```json'):
            deposit_text = deposit_text[7:].rsplit('```', 1)[0].strip()
        z = json.loads(deposit_text)
        require(z['doi'] == '10.5281/zenodo.14592209' and z['status'] == 'published' and z['metadata']['license']['id'] == 'cc-by-4.0', 'Published deposit/rights')
        expected = a['synthetic_rdna_resource']['deposited_resource']['files']
        require(len(z['files']) == len(expected) == 3, 'Three deposited files')
        for item in expected:
            found = next(x for x in z['files'] if x['key'] == item['filename'])
            require(found['size'] == item['advertised_bytes'] and found['checksum'] == item['advertised_checksum'], 'Advertised file metadata: ' + item['filename'])
        local = 'PASS: publication-date correction and advertised deposit inventory; no downloaded archive validation'
    print(json.dumps({'status':'PASS','source_replay':own,'shared_root_replay':watch,'shared_local_replay':local,'study_nulls':26,'planning_nulls':18,'matched_panels_admitted':0,'source_data_reanalysed':False,'external_qualified_review':False},indent=2))

if __name__ == '__main__':
    main()
