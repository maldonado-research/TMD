#!/usr/bin/env python3
"""Read-only R34 integrity/optional original-archive replay; no network or writes."""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
F = Path(__file__).resolve().parent
R = F.parents[1]

def require(ok, label):
    if not ok:
        raise ValueError(label)

def read(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError('Duplicate JSON key: ' + k)
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def numerical_equal(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= 2e-12
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(numerical_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(numerical_equal(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    args = parser.parse_args()
    public = read(F / 'PUBLIC_FILES.json')['public_files']
    require(len(public) == len(set(public)) == 14, 'Fourteen unique public files')
    require(all(Path(n).name == n and n not in ('.', '..') for n in public), 'Safe public names')
    require(set(public) == {p.name for p in F.iterdir()} and
            all(p.is_file() and not p.is_symlink() for p in F.iterdir()), 'Exact regular-file closure')
    covered = set()
    for line in (F / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name in public and name not in covered, 'Checksum membership')
        require(sha(F / name) == digest, 'Checksum: ' + name)
        covered.add(name)
    require(covered == set(public) - {'SHA256SUMS.txt'}, 'Complete checksum coverage')
    provenance = read(F / 'SOURCE_PROVENANCE.json')
    result = read(F / 'RESULTS.json')
    joins = read(F / 'JOIN_AUDIT.json')
    decision = read(F / 'DECISION.json')
    require(provenance['source_version_doi'] == '10.5281/zenodo.14592209', 'Fixed public source version')
    require(provenance['own_scientific_acquisition_calls'] == 0 and provenance['root_scientific_acquisition_calls'] == 2, 'Two root calls only')
    require(sum(a['bytes'] for a in provenance['original_archives']) == provenance['new_original_artifact_bytes'] == 9037599, 'Original archive bytes')
    require(provenance['root_HTTP_receipt_bytes'] == 1999 and provenance['round_saved_source_bytes'] == 9039598, 'Saved source accounting')
    require(sum(a['members'] for a in provenance['complete_archive_inventory']) == 173 and
            sum(a['regular_files'] for a in provenance['complete_archive_inventory']) == 171 and
            sum(a['expanded_regular_bytes'] for a in provenance['complete_archive_inventory']) == 20993744, 'Complete inventory totals')
    require(result['status'] == 'PASS_PROCESSED_FIGURE2D_DESCRIPTIVE_REPLAY' and
            result['figure'] == '2D' and not result['fallback_used'], 'Declared target')
    require(result['processed_accession_rows'] == 22 and result['new_exclusions'] == 0 and
            result['pseudocount'] is None and result['independent_biological_unit_count'] is None and
            result['inferential_confidence_intervals'] is None, 'Descriptive-only row scope')
    require(not result['source_author_code_executed'] and not result['absolute_spike_copy_truth_verified'] and
            not result['native_TMD_parameters_estimated'], 'No author code, true dose or native fit')
    require(set(result['fits']) == {'ITS1', 'ITS2', 'V4'}, 'Three primers')
    require(sum(v['n_accession_rows'] for v in result['fits'].values()) == 22, 'All rows in summaries')
    for primer, fit in result['fits'].items():
        require(fit['n_accession_rows'] == (6 if primer == 'V4' else 8), 'Primer row count')
        require(abs(fit['r_squared'] - (1 - fit['residual_sum_of_squares'] / fit['total_sum_of_squares'])) <= 1e-14,
                'Recorded R-squared identity')
        for key in ('slope', 'r_squared'):
            require(math.isfinite(fit[key]) and abs(fit[key] - fit['archived_author_display'][key]) <= 5e-8,
                    'Recorded author display agreement')
    require(len(joins['accession_to_primer_and_nominal_soil']) == 22 and
            len({x['accession'] for x in joins['accession_to_primer_and_nominal_soil']}) == 22,
            'Unique accession join coverage')
    require(not joins['filters']['excluded_accessions_or_counts_recovered'] and
            not joins['filters']['all_attempted_samples_or_detection_denominator_known'] and
            not joins['spike_dose']['exact_per_accession_copy_input_known'], 'Explicit missing joins')
    require(joins['replicate_join']['explicit_extraction_replicate_ID'] is None and
            joins['replicate_join']['explicit_library_replicate_ID'] is None and
            joins['replicate_join']['independent_biological_unit_count'] is None, 'Replication unresolved')
    for name in ['study_fields_resolved', 'planning_fields_resolved', 'matched_panels_admitted',
                 'native_calibration_records_admitted', 'independent_mutation_events_admitted']:
        require(decision[name] == 0, 'Zero native admission: ' + name)
    for name in ['new_mathematical_theorem', 'native_TMD_fit_performed', 'methods_archive_changed', 'frozen_core_changed']:
        require(not decision[name], 'Frozen scope: ' + name)
    for item in provenance['inherited_dependencies']:
        path = Path(item['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'Safe dependency path')
        file = R / path
        require(file.is_file() and not file.is_symlink() and file.stat().st_size == item['bytes'] and
                sha(file) == item['sha256'], 'Frozen dependency identity: ' + str(path))
    actual = read(R / 'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(R / 'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(actual) == 26 and all(v is None for v in actual.values()), '26 NULL study fields')
    require(len(planning) == 18 and all(v is None for v in planning.values()), '18 NULL planning fields')
    status = 'UNRUN: original archive cache not supplied; recorded results checked for integrity and internal consistency only'
    if args.source_cache:
        spec = importlib.util.spec_from_file_location('r34_original_replay', F / 'replay_figure2d.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        observed, points = module.replay(args.source_cache, provenance)
        require(numerical_equal(observed, result), 'Recorded reproduction within 2e-12 arithmetic tolerance')
        observed_joins = [{'accession':p['accession'],'primer':p['primer'],'nominal_soil_mg':p['soil_mg']}
                         for p in sorted(points,key=lambda x:(x['primer'],x['soil_mg'],x['accession']))]
        require(observed_joins == joins['accession_to_primer_and_nominal_soil'], 'Exact accession/primer/mass joins')
        status = 'PASS: original archive identities, selected recipe/output anchors, all 22 processed rows and six author-display agreements; no raw sequencing or experimental-truth validation'
    print(json.dumps({'status':'PASS','source_replay':status,'study_nulls':26,'planning_nulls':18,
                      'native_records_admitted':0,'source_author_code_executed':False,
                      'external_qualified_review':False},indent=2))

if __name__ == '__main__':
    main()
