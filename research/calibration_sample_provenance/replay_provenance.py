#!/usr/bin/env python3
"""R35 offline identifier join. No network, writes, raw-read or author-code execution."""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LABEL = re.compile(r'^(ITS1|ITS2|V4)_soil(37|75|150|300)mgmixE_S([0-9]+)$')


def require(value, message):
    if not value:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def authenticated(path, expected):
    require(path.is_file() and not path.is_symlink(), 'Regular input required')
    require(path.stat().st_size == expected['bytes'], 'Input byte length mismatch')
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected['sha256'], 'Input SHA-256 mismatch')
    return data


def table(data):
    rows = list(csv.DictReader(io.StringIO(data.decode('utf-8')), delimiter='\t'))
    require(len(rows) == len({r['srr_accession'] for r in rows}), 'Non-unique TSV accessions')
    return {r['srr_accession']: r for r in rows}


def derive(xml_bytes, figure2d_bytes, figure_s3_bytes):
    """Only whitelisted metadata fields enter the returned original synthesis."""
    require(len(xml_bytes) < 4 * 1024 * 1024, 'XML cap')
    root = ET.fromstring(xml_bytes)
    require(root.tag == 'EXPERIMENT_PACKAGE_SET', 'Unexpected XML root')
    targets, supplement = table(figure2d_bytes), table(figure_s3_bytes)
    require(len(targets) == 22 and set(supplement) == set(targets), 'Fixed source scope')
    by_run, named = {}, []
    biosamples, experiments = set(), set()
    for package in root:
        require(package.tag == 'EXPERIMENT_PACKAGE', 'Unexpected package')
        experiment = package.find('EXPERIMENT')
        project = experiment.findtext("STUDY_REF/IDENTIFIERS/EXTERNAL_ID[@namespace='BioProject']")
        require(project == 'PRJNA1100950', 'Unexpected project')
        experiments.add(experiment.get('accession'))
        sample = package.find('SAMPLE')
        biosample = sample.findtext("IDENTIFIERS/EXTERNAL_ID[@namespace='BioSample']")
        biosamples.add(biosample)
        descriptor = experiment.find('DESIGN/SAMPLE_DESCRIPTOR')
        require(descriptor.get('accession')==sample.get('accession'), 'Experiment/sample cross-reference')
        require(descriptor.findtext("IDENTIFIERS/EXTERNAL_ID[@namespace='BioSample']")==biosample, 'Experiment/BioSample cross-reference')
        library = experiment.findtext('DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_NAME')
        label = LABEL.fullmatch(library or '')
        for run in package.findall('RUN_SET/RUN'):
            require(run.find('EXPERIMENT_REF').get('accession')==experiment.get('accession'), 'Run/experiment cross-reference')
            accession = run.get('accession')
            require(accession not in by_run, 'Duplicate SRA run accession')
            record = {
                'run_accession': accession,
                'sra_experiment': experiment.get('accession'),
                'sra_sample': sample.get('accession'),
                'biosample': biosample,
                'library_name': library,
            }
            by_run[accession] = record
            if label:
                require(experiment.findtext('TITLE') == library, 'Title/library disagreement')
                require(experiment.get('alias') == library, 'Alias/library disagreement')
                record.update(primer=label[1], nominal_soil_mg_from_library_label=int(label[2]))
                named.append(record)
    retained = []
    conflicts = []
    for accession in sorted(targets):
        target = targets[accession]
        require(accession in by_run, 'Unmatched target ' + accession)
        record = dict(by_run[accession])
        require(record in named, 'Target lacks explicit condition label')
        require(record['primer'] == target['primer_id'], 'Primer disagreement')
        require(str(record['nominal_soil_mg_from_library_label']) == target['level_id'], 'Figure 2D mass disagreement')
        s3 = supplement[accession]
        require(s3['primer_id'] == target['primer_id'], 'Figure S3 primer disagreement')
        conflict = s3['level_id'] != target['level_id']
        record.update(figure2d_nominal_soil_mg_label=target['level_id'],
                      figure_s3_nominal_soil_mg_label=s3['level_id'],
                      cross_artifact_soil_mass_label_conflict=conflict)
        retained.append(record)
        if conflict:
            conflicts.append({'run_accession':accession, 'figure2d_and_sra_label_mg':target['level_id'],
                              'figure_s3_label_mg':s3['level_id'], 'actual_weighed_soil_mg':None})
    candidates = []
    for record in sorted(named, key=lambda r:r['run_accession']):
        if record['run_accession'] not in targets:
            item = dict(record)
            item.update(evidence_status='CANDIDATE_OMITTED_CONDITION_RUN',
                        exact_postprocessing_standard_reads=None,
                        accession_specific_exclusion_confirmed=False)
            candidates.append(item)
    require(len(root) == len(experiments) == len(by_run) == 178, 'Project metadata scope')
    require(len(named) == 24 and len(candidates) == 2, 'Named condition scope')
    require(all(c['primer']=='V4' and c['nominal_soil_mg_from_library_label']==300 for c in candidates), 'Candidate condition')
    return {
        'schema_version':1,
        'status':'PASS_EXACT_ACCESSION_METADATA_JOIN',
        'project':'PRJNA1100950',
        'project_experiment_records':len(experiments),
        'project_run_records':len(by_run),
        'project_biosample_identifiers':len(biosamples),
        'target_rows':len(targets),
        'matched_target_rows':len(retained),
        'unmatched_targets':[],
        'multiply_matched_targets':[],
        'figure2d_to_sra_primer_or_mass_conflicts':[],
        'target_distinct_experiments':len({r['sra_experiment'] for r in retained}),
        'target_distinct_library_names':len({r['library_name'] for r in retained}),
        'target_sra_sample_identifiers':sorted({r['sra_sample'] for r in retained}),
        'target_biosample_identifiers':sorted({r['biosample'] for r in retained}),
        'named_soil_mass_condition_runs':len(named),
        'retained_accession_join':retained,
        'candidate_omitted_condition_runs':candidates,
        'cross_artifact_soil_mass_label_conflicts':conflicts,
        'independent_biological_unit_count':None,
        'extraction_replicate_map':None,
        'library_preparation_replicate_map':None,
        'physical_shared_pool_ancestry_map':None,
        'exact_per_accession_standard_dose_copies':None,
        'per_accession_dose_uncertainty':None,
        'full_attempted_sample_denominator':None,
        'new_regression_or_native_fit':False,
    }


def verify_public():
    public = read_json(HERE/'PUBLIC_FILES.json')['public_files']
    require(len(public)==len(set(public)), 'Public membership duplicate')
    require(set(public)=={p.name for p in HERE.iterdir()}, 'Exact public file closure')
    require(all(p.is_file() and not p.is_symlink() for p in HERE.iterdir()), 'Regular public files')
    checks = {}
    for line in (HERE/'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ',1)
        require(name in public and name not in checks, 'Checksum membership')
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest, 'Checksum '+name)
        checks[name] = digest
    require(set(checks)==set(public)-{'SHA256SUMS.txt'}, 'Complete checksum coverage')
    source = read_json(HERE/'SOURCE_PROVENANCE.json')
    joined = read_json(HERE/'JOIN_AUDIT.json')
    rows = joined['retained_accession_join']
    require(len(rows)==len({r['run_accession'] for r in rows})==22, '22 unique retained rows')
    require(len({r['sra_experiment'] for r in rows})==len({r['library_name'] for r in rows})==22, '22 archive experiment/library labels')
    require({r['biosample'] for r in rows}=={'SAMN43151561'} and {r['sra_sample'] for r in rows}=={'SRS22380613'}, 'Shared archive sample annotation')
    require({r['run_accession'] for r in joined['candidate_omitted_condition_runs']}=={'SRR30280226','SRR30280227'}, 'Two candidate identifiers')
    require(all(not r['accession_specific_exclusion_confirmed'] and r['exact_postprocessing_standard_reads'] is None for r in joined['candidate_omitted_condition_runs']), 'Candidate status retained')
    require(len(joined['cross_artifact_soil_mass_label_conflicts'])==6, 'Six unresolved mass-label discrepancies')
    for key in ['independent_biological_unit_count','extraction_replicate_map','library_preparation_replicate_map','physical_shared_pool_ancestry_map','exact_per_accession_standard_dose_copies','per_accession_dose_uncertainty','full_attempted_sample_denominator']:
        require(joined[key] is None, 'Unresolved '+key)
    decision = read_json(HERE/'DECISION.json')
    for key in ['study_fields_resolved','planning_fields_resolved','native_calibration_records_admitted','independent_mutation_events_admitted','matched_panels_admitted']:
        require(decision[key]==0, 'No native admission: '+key)
    require(not decision['native_TMD_fit_performed'] and not decision['frozen_core_changed'], 'Frozen scope')
    for item in source['frozen_dependencies']:
        require(not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts, 'Dependency path')
        authenticated(ROOT/item['path'], item)
    actual = read_json(ROOT/'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read_json(ROOT/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(actual)==26 and all(v is None for v in actual.values()), '26 NULL study fields')
    require(len(planning)==18 and all(v is None for v in planning.values()), '18 NULL planning fields')
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache','--source-dir',dest='source_dir',type=Path,help='External directory containing the five attempt captures')
    parser.add_argument('--data-archive',type=Path,help='Authenticated Zenodo data.tar.gz')
    args = parser.parse_args()
    require(bool(args.source_dir)==bool(args.data_archive), 'Supply both source arguments or neither')
    source = verify_public()
    status = 'UNRUN: external source captures not supplied; public integrity and frozen inputs only'
    if args.source_dir:
        captures = {c['filename']:authenticated(args.source_dir/c['filename'], c) for c in source['saved_acquisition_files']}
        discovery = json.loads(captures['S03_sra_esearch.body'])['esearchresult']
        require(int(discovery['count'])==len(discovery['idlist'])==178, 'Complete eSearch result')
        archive = authenticated(args.data_archive, source['reused_data_archive'])
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
            members = tar.getmembers()
            require(len({m.name for m in members})==len(members), 'Archive duplicate name')
            data = {}
            for item in source['selected_data_members']:
                member = tar.getmember(item['path'])
                require(member.isfile() and member.size==item['bytes'], 'Selected regular member')
                data[item['path']] = tar.extractfile(member).read()
                require(hashlib.sha256(data[item['path']]).hexdigest()==item['sha256'], 'Selected member hash')
        observed = derive(captures['S04_sra_experiments.body'],data['data/figure2D.tsv'],data['data/figureS3.tsv'])
        require(observed==read_json(HERE/'JOIN_AUDIT.json'), 'Exact recorded metadata join')
        status = 'PASS: all saved acquisition bytes, original data archive, 22 exact joins, two candidates and six mass-label discrepancies'
    print(json.dumps({'status':'PASS','source_metadata_replay':status,'study_nulls':26,'planning_nulls':18,
                      'native_records_admitted':0,'biological_independence_established':False},indent=2))


if __name__=='__main__':
    main()
