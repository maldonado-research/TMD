#!/usr/bin/env python3
"""Read-only R32 package/capture checks. No network, fits or source-code execution."""
import argparse
import hashlib
import json
import re
from pathlib import Path

F = Path(__file__).resolve().parent
R = F.parents[1]


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path, item):
    require(path.is_file() and not path.is_symlink(), 'Regular file: ' + path.name)
    require(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'],
            'Identity: ' + path.name)


def representation(path):
    result = read(path)
    result = result.get('result', result)
    structured = result.get('structuredContent')
    if isinstance(structured, dict) and structured:
        return structured
    for block in result.get('content', []):
        if block.get('type') == 'text':
            try:
                candidate = json.loads(block['text'])
            except (TypeError, ValueError):
                continue
            if isinstance(candidate, dict):
                return candidate
    raise ValueError('No structured representation: ' + path.name)


def norm(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text.replace('*', ''))).strip()


def cache_identities(cache, items):
    require(len(items) == len({x['filename'] for x in items}), 'Unique capture names')
    for item in items:
        name = item['filename']
        require(isinstance(name, str) and Path(name).name == name and name not in ('.', '..'),
                'Safe capture filename')
        identity(cache / name, item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path, help='External five-capture methods cache')
    parser.add_argument('--watch-cache', type=Path, help='External two-capture shared root cache')
    args = parser.parse_args()
    prov = read(F / 'SOURCE_PROVENANCE.json')
    assessment = read(F / 'ASSESSMENT.json')
    decision = read(F / 'DECISION.json')
    require(prov['logical_scientific_calls'] == len(prov['calls']) ==
            len(prov['saved_acquisition_files']) == 5, 'Five own calls')
    require(prov['logical_call_allocation'] == 6, 'Bounded calls, sixth unused')
    require(sum(x['bytes'] for x in prov['saved_acquisition_files']) ==
            prov['saved_acquisition_bytes'] == 541815 <= prov['byte_allocation'], 'Own byte accounting')
    require({x['filename'] for x in prov['calls']} ==
            {x['filename'] for x in prov['saved_acquisition_files']}, 'Call/capture membership')
    shared = prov['shared_root_acquisitions']
    require(shared['logical_scientific_calls'] == len(shared['saved_acquisition_files']) == 2
            and not shared['counted_in_own_totals'], 'Shared root accounting')
    require(sum(x['bytes'] for x in shared['saved_acquisition_files']) ==
            shared['saved_acquisition_bytes'] == 26719, 'Shared root bytes')
    require(not prov['supporting_information_acquired'] and
            not prov['actual_supplement_file_link_identified'] and
            prov['original_artifact_bytes_acquired'] == 0 and
            not prov['raw_source_bodies_published'] and
            not prov['source_code_or_sequencing_data_acquired'] and
            not prov['source_data_reanalysed'], 'Representation/acquisition boundaries')
    require(assessment['status'] ==
            'MAIN_TEXT_CALIBRATION_CLARIFICATION_SUPPORTING_INFORMATION_UNACQUIRED', 'Assessment status')
    require(assessment['source']['doi'] == '10.64898/2026.08.03.742544' and
            assessment['source']['version'] == 'v1' and
            assessment['source']['posted_date'] == '2026-08-07' and
            not assessment['source']['peer_review_certified'] and
            assessment['source']['independent_study_count'] == 1, 'One preprint evidence family')
    require(assessment['reported_system']['organism'] == 'Saccharomyces cerevisiae' and
            not assessment['reported_system']['native_Wsp_Aws_Mws'], 'Yeast boundary')
    require(assessment['calibration']['calibration_records_admitted'] ==
            assessment['unit_and_dependence']['independent_mutation_event_count_admitted'] == 0,
            'No measurement admission')
    require(not assessment['source_values_imported_into_TMD'] and
            not assessment['new_mathematical_theorem'] and
            not assessment['experiment_commissioned'] and
            not assessment['external_qualified_review'], 'No experiment/theorem/external review')
    require(decision['study_fields_resolved'] == decision['planning_fields_resolved'] ==
            decision['matched_panels_admitted'] == 0 and
            not decision['frozen_core_changed'] and not decision['methods_archive_changed'], 'No admission/change')
    for item in prov['inherited_dependencies']:
        path = Path(item['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'Safe inherited path')
        identity(R / path, item)
    actual = read(R / 'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(R / 'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(actual) == 26 and all(x is None for x in actual.values()), '26 NULL study fields')
    require(len(planning) == 18 and all(x is None for x in planning.values()), '18 NULL planning fields')
    public = read(F / 'PUBLIC_FILES.json')['public_files']
    require(len(public) == len(set(public)) == 11, 'Eleven unique public files')
    require(all(isinstance(n, str) and Path(n).name == n and n not in ('.', '..') for n in public),
            'Safe public names')
    require(set(public) == {x.name for x in F.iterdir()} and
            all(x.is_file() and not x.is_symlink() for x in F.iterdir()), 'Exact public closure')
    covered = set()
    for line in (F / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name in public and name not in covered and Path(name).name == name, 'Checksum membership')
        covered.add(name)
        require(sha(F / name) == digest, 'Checksum: ' + name)
    require(covered == set(public) - {'SHA256SUMS.txt'}, 'Complete checksum coverage')

    replay = 'UNRUN: methods source cache not supplied'
    if args.source_cache:
        cache_identities(args.source_cache, prov['saved_acquisition_files'])
        blocked = representation(args.source_cache / '01_supplementary_page.json')
        require(blocked['metadata']['statusCode'] == 429 and blocked.get('links') == [], 'SI rate-limit response')
        require('high number of requests' in blocked['markdown'], 'Blocked page, not scientific SI')
        search1 = representation(args.source_cache / '02_named_si_search.json')['data']['web']
        collision = representation(args.source_cache / '03_method_artifact_search.json')['data']['web']
        exact = representation(args.source_cache / '04_exact_title_artifact_search.json')['data']['web']
        require(len(search1) == 1 and len(collision) == 8 and len(exact) == 6, 'Search coverage')
        require('bacteriophage' in collision[0]['title'] and 'HIDEN-SEQ' in collision[0]['title'],
                'Off-target name collision')
        require(exact[0]['url'].endswith('742544v1.full-text'), 'Named full-text discovery')
        main_text = representation(args.source_cache / '05_main_fulltext_links.json')
        meta = main_text['metadata']
        require(meta['statusCode'] == 200 and meta['url'].endswith('742544v1.full') and
                meta['citation_doi'] == assessment['source']['doi'] and
                meta['citation_date'] == meta['DC.Date'] == '2026-08-07', 'Main article identity/date')
        require('has not been certified by peer review' in main_text['markdown'] and
                'CC BY 4.0' in meta['DC.Rights'], 'Main article status/rights')
        require(meta['citation_publication_date'] == '2026/01/01', 'Retain auxiliary date disagreement')
        content = norm(main_text['markdown'])
        for anchor in assessment['selected_main_text_anchors']:
            require(norm(anchor['text']) in content, 'Selected main-text anchor: ' + anchor['id'])
        require(any(x.endswith('742544v1.supplementary-material') for x in main_text['links']),
                'Actual named SI landing link')
        replay = 'PASS: capture identities and selected main-text/search/error anchors only; SI unacquired'

    watch = 'UNRUN: shared root watch cache not supplied'
    if args.watch_cache:
        cache_identities(args.watch_cache, shared['saved_acquisition_files'])
        for item in shared['saved_acquisition_files']:
            require(read(args.watch_cache / item['filename'])['args'] == item['arguments'],
                    'Shared root call arguments')
        results = representation(args.watch_cache / 'S01.json')['results']
        require(len(results) == 1 and results[0]['ids']['doi'] == [assessment['source']['doi']] and
                results[0]['ids']['pmcid'] == ['PMC13484652'] and
                results[0]['ids']['pmid'] == ['42620021'], 'Same indexed evidence family')
        pmc = representation(args.watch_cache / 'S02.json')
        require(pmc['metadata']['statusCode'] == 200 and
                pmc['metadata']['citation_doi'] == assessment['source']['doi'], 'PMC identity')
        for anchor in ['This is a preprint.', 'not yet been peer reviewed by a journal',
                       'Creative Commons Attribution 4.0 International License',
                       'Full Text Availability', 'do not permit archiving in PMC',
                       'The full text is available from the preprint server.']:
            require(anchor in pmc['markdown'], 'PMC coverage/rights anchor: ' + anchor)
        require(not any('supplement' in x.lower() for x in pmc['links']), 'No PMC SI link in retrieved list')
        watch = 'PASS: same-family metadata/abstract and availability discrepancy only; no PMC full text or SI'

    print(json.dumps({'status': 'PASS', 'source_replay': replay, 'shared_watch_replay': watch,
                      'study_nulls': 26, 'planning_nulls': 18, 'matched_panels_admitted': 0,
                      'supporting_information_acquired': False, 'source_data_reanalysed': False,
                      'external_qualified_review': False}, indent=2))


if __name__ == '__main__':
    main()
