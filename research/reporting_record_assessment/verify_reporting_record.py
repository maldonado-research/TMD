#!/usr/bin/env python3
"""Read-only R31 reporting-record replay. Copyright Ricardo Maldonado; MIT."""
import argparse
import hashlib
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise SystemExit(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def fingerprint(path):
    return {'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def representation(capture):
    value = capture['result'].get('structuredContent')
    if isinstance(value, dict) and isinstance(value.get('markdown'), str):
        return value
    for item in capture['result'].get('content', []):
        if item.get('type') == 'text':
            try:
                value = json.loads(item['text'])
                if isinstance(value.get('markdown'), str):
                    return value
            except (ValueError, AttributeError):
                pass
    raise SystemExit('No markdown representation')


def derive(cache):
    form = representation(read(cache / 'S01.json'))['markdown']
    titles = ['Sample-size estimation', 'Replicates', 'Statistical reporting',
              'Group allocation', 'Additional data files (“source data”)']
    rows = []
    for i, title in enumerate(titles):
        block = form.split('**' + title + '**', 1)[1]
        if i + 1 < len(titles):
            block = block.split('**' + titles[i + 1] + '**', 1)[0]
        if i < 4:
            answer = block.split('Please outline where this information can be found', 1)[1]
            answer = answer.split(':', 1)[1].strip().split('\n\n', 1)[0]
        else:
            answer = block.split('Please indicate the figures or tables for which source data files have been provided:', 1)[1].strip().split('\n\n', 1)[0]
        rows.append({'heading': title, 'author_answer': answer})
    template = form.split('**Statistical reporting**', 1)[1].split('Please outline where', 1)[0]
    require('mean, median, SD, SEM, confidence intervals' in template, 'Template examples absent')
    require('SEM' not in rows[2]['author_answer'], 'Author dispersion answer changed')
    require(all(x not in form for x in ['I844L', 'G21', 'D21', 'E21']), 'New row-specific token; reassess')
    form_audit = {
        'schema_version': 1, 'round': 'R31', 'doi': '10.7554/eLife.38822.023',
        'artifact': 'Transparent reporting form', 'inspected_headings': rows,
        'template_dispersion_examples': 'mean, median, SD, SEM, confidence intervals',
        'template_examples_are_author_statistical_choices': False,
        'author_answer_defines_E21_as_SEM': False,
        'row21_original_calculation_record_supplied_in_inspected_form': False,
        'scope': 'All five headings and answers in the provider representation; original DOCX binary and completeness against original bytes not independently authenticated.'}
    peer = representation(read(cache / 'S02.json'))['markdown']
    divider = '[https://doi.org/10.7554/eLife.38822.026](https://doi.org/10.7554/eLife.38822.026)'
    require(peer.count(divider) == 1, 'Decision/response delimiter changed')
    decision, response = peer.split(divider, 1)
    stage = 'the authors’ response after being formally invited to submit a revised submission follows.'
    require(response.count(stage) == 1, 'Author response stage changed')
    plan, final = response.split(stage, 1)
    def author_sentence(section, text):
        paragraphs = section.split('\n\n')
        require(any(text in p and not p.lstrip().startswith('>') for p in paragraphs),
                'Author statement missing or only reviewer quotation: ' + text)
        return text
    record = {
        'schema_version': 1, 'round': 'R31',
        'author_response_doi': '10.7554/eLife.38822.027',
        'decision_letter_doi': '10.7554/eLife.38822.026',
        'author_revision_plan': {
            'frequency_dependence': author_sentence(plan, 'Firstly, the fitness of WS is frequency-dependent and thus a mutant’s selection coefficient is very different at the time it originates compared to when it is established at the air-liquid interface'),
            'other_competitors': author_sentence(plan, 'Secondly, the selection coefficient is also dependent on the frequency of other WS types and other phenotypes selected at the air-liquid interface'),
            'assay_reference': author_sentence(plan, 'Thirdly, fitness in our study is measured against a _wspF_ (WS) mutant and not the wild type ancestor, which is needed for use in origin-fixation models.')},
        'author_final_revision': {
            'title_scope': author_sentence(final, 'our previous title gave the unintended message that we were combining mutation and selection into our model of evolutionary forecasting.'),
            'forecast_scope': author_sentence(final, 'we do not attempt to predict the outcome of experimental evolution using mutation rates and selection coefficients.'),
            'fitness_assay_purpose': author_sentence(final, 'We have provided a better motivation for the fitness assays, which is to provide an explanation for these differences.'),
            'reporting_additions': author_sentence(final, 'We have included statistical tests for all claims of differences as well as number of replicates.')},
        'reviewer_suggestion': {
            'eye_estimation_sentence': 'Here x is the selection coefficient of the WspF control used in growth competitions, and I have estimated s by eye from Figure 6.',
            'proposed_origin_fixation_fit_is_accepted_author_calibration': False,
            'prepublication_figure_numbers_are_final_figure_crosswalk': False},
        'TMD_assessment': {
            'assay_reference_and_frequency_context_required_for_transport': True,
            'reporting_form_resolves_row21_aggregation': False,
            'peer_review_record_resolves_row21_aggregation': False,
            'new_observed_WAM_vector_or_establishment_parameter_supplied': False,
            'general_origin_fixation_theory_rejected': False,
            'matched_panels_admitted': 0}}
    require(record['reviewer_suggestion']['eye_estimation_sentence'] in decision, 'Reviewer estimate absent')
    require('is not what we have done.' in final, 'Final scope clarification absent')
    require('Information about controls for fitness assays have been added to the methods section' in final,
            'Final controls statement absent')
    return form_audit, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--r29-source-cache', type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    public = read(package / 'PUBLIC_FILES.json')['public_files']
    require(len(public) == len(set(public)) == 12 and all(Path(n).name == n for n in public), 'Unsafe allowlist')
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()), 'Unexpected directory or symlink')
    require(set(p.name for p in package.iterdir()) == set(public), 'Allowlist drift')
    sums = {}
    for line in (package / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(name not in sums and Path(name).name == name, 'Unsafe checksum path')
        sums[name] = digest
    require(set(sums) == set(public) - {'SHA256SUMS.txt'}, 'Checksum closure')
    require(all(fingerprint(package / n)['sha256'] == h for n, h in sums.items()), 'Checksum mismatch')
    provenance = read(package / 'SOURCE_PROVENANCE.json')
    require(len(provenance['calls']) == provenance['logical_scientific_calls'] == 2 <= provenance['logical_call_allocation'] == 5, 'Call accounting')
    require(sum(x['bytes'] for x in provenance['saved_acquisition_files']) == provenance['saved_acquisition_bytes'] == 102415 <= provenance['byte_allocation'] == 8388608, 'Byte accounting')
    for item in provenance['inherited_dependencies']:
        require(fingerprint(root / item['path']) == {k: item[k] for k in ['bytes', 'sha256']}, 'Inherited dependency drift')
    study = read(root / 'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(root / 'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(study) == 26 and all(v is None for v in study.values()), 'Study NULL drift')
    require(len(planning) == 18 and all(v is None for v in planning.values()), 'Planning NULL drift')
    decision = read(package / 'DECISION.json')
    require(decision['matched_panels_admitted'] == 0 and not decision['new_biological_fit'] and not decision['author_values_replaced'], 'Admission or value drift')
    replay = 'UNRUN: no R31 source cache supplied'
    inherited = 'UNRUN: no R29 source cache supplied'
    if args.source_cache:
        for item in provenance['saved_acquisition_files']:
            require(Path(item['filename']).name == item['filename'], 'Unsafe capture filename')
            require(fingerprint(args.source_cache / item['filename']) == {k: item[k] for k in ['bytes', 'sha256']}, 'Capture identity')
        for call in provenance['calls']:
            capture = read(args.source_cache / call['capture_file'])
            require(all(capture[k] == call[k] for k in ['call_id', 'tool', 'args', 'started', 'completed']), 'Call provenance')
            metadata = representation(capture)['metadata']
            require(all(metadata[k] == v for k, v in call['provider_metadata'].items()), 'Provider metadata drift')
        form, record = derive(args.source_cache)
        require(form == read(package / 'REPORTING_FORM_AUDIT.json'), 'Form extraction drift')
        require(record == read(package / 'APPLICABILITY_RECORD.json'), 'Author/reviewer/stage replay drift')
        replay = 'PASS: capture identities, five form answers, template/author distinction, author response stages and reviewer suggestion attribution'
    if args.r29_source_cache:
        item = provenance['reused_source_files'][0]
        path = args.r29_source_cache / item['filename']
        require(fingerprint(path) == {k: item[k] for k in ['bytes', 'sha256']}, 'Reused capture identity')
        m = representation(read(path))['markdown']
        require(all(x in m for x in ['elife-38822-transrepform-v1.docx', '10.7554/eLife.38822.023', '"authorResponse"', '10.7554/eLife.38822.027']), 'Named discovery linkage')
        inherited = 'PASS: reused provider representation and named reporting-form/author-response identifiers'
    print(json.dumps({'status': 'PASS', 'source_replay': replay, 'inherited_source_replay': inherited,
                      'study_nulls': 26, 'planning_nulls': 18, 'matched_panels_admitted': 0,
                      'source_intended_aggregation_identified': False,
                      'experimental_truth_validated': False, 'network_requests': 0}, indent=2))


if __name__ == '__main__':
    main()
