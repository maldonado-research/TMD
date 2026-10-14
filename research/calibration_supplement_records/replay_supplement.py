#!/usr/bin/env python3
"""Original offline R36 source-representation and count-total audit. MIT license.

No network access, author code execution, regression, figure digitization or mutation.
Public-only invocation checks packaged hashes and frozen dependencies; provide
external captures and the source archive for a full source replay.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def jread(path):
    return json.loads(path.read_text())


def caption(text, label):
    start = text.index('**Fig. ' + label + '.**')
    end = text.find('\n\n---', start)
    if end < 0:
        end = len(text)
    return ' '.join(text[start:end].split())


def derive_capture(wrapper, frame):
    result = wrapper['result']['structuredContent']
    text = result['markdown']
    meta = result['metadata']
    rows = frame['retained_accession_join'] + frame['candidate_omitted_condition_runs']
    assert len(rows) == 24
    searches = []
    for row in rows:
        for field in ('run_accession', 'sra_experiment', 'library_name'):
            token = row[field]
            searches.append({'identifier': token, 'field': field, 'literal_hits': text.count(token)})
    table = text[text.index('**Table S5.**'):]
    processing = []
    for region in ('SSU-V4', 'ITS1', 'ITS2'):
        line = next(line for line in table.splitlines() if line.startswith('| ' + region + ' |'))
        def setting(name):
            m = re.search(name + r'\s*=\s*(c\([^)]*\)|\d+)', line)
            return [int(v) for v in re.findall(r'\d+', m.group(1))] if m else None
        processing.append({
            'source_label': region,
            'scope': 'SOURCE_REPORTED_PROTOCOL_NOT_RUN_LEVEL_EXECUTION',
            'cutadapt_minimum_length_bases': int(re.search(r'--minimum-length\s+(\d+)', line).group(1)),
            'cutadapt_max_n': int(re.search(r'--max-n\s+(\d+)', line).group(1)),
            'cutadapt_discard_untrimmed': '--discard-untrimmed' in line,
            'dada2_trunc_len_bases': setting('truncLen'),
            'dada2_max_expected_errors': setting('maxEE'),
            'explicit_truncation_setting_absent_is_not_a_zero': setting('truncLen') is None,
        })
    s3 = caption(text, 'S3')
    s9 = caption(text, 'S9')
    return {
        'representation': 'FIRECRAWL_EXTRACTED_MARKDOWN_NOT_LOCAL_ORIGINAL_PDF',
        'provider_reported_processed_pages': meta['numPages'],
        'provider_reported_total_pages': meta['totalPages'],
        'provider_reported_http_status': meta['statusCode'],
        'provider_reported_content_type': meta['contentType'],
        'figures_identified': sorted(set(re.findall(r'\*\*Fig\. (S\d+)\.\*\*', text)), key=lambda x:int(x[1:])),
        'tables_identified': sorted(set(re.findall(r'Table (S\d+)\.', text)), key=lambda x:int(x[1:])),
        'frame_records': len(rows),
        'literal_identifier_queries': len(searches),
        'literal_identifier_hits': sum(x['literal_hits'] for x in searches),
        'identifier_search': searches,
        'figure_s3_reports_random_subsampling_to_60000': 'randomly subsampled to 60,000 reads' in s3,
        'figure_s9_reports_mock_strain_under10_exclusion': all(t in s9 for t in ('mock communities', 'strains with less than 10 reads')),
        'table_s5_selected_protocol_parameters': processing,
        'automatic_plot_tables_used': False,
        'original_pdf_bytes_authenticated': False,
        'per_run_measured_dose': None,
        'per_run_dose_uncertainty': None,
        'extraction_pcr_library_genealogy': None,
        'accession_specific_exclusion_decisions': None,
        'full_attempted_sample_denominator': None,
    }


def derive_totals(archive):
    with tarfile.open(archive, 'r:gz') as tar:
        selected = {}
        for member in ('data/figure2D.tsv', 'data/figureS3.tsv'):
            raw = tar.extractfile(member).read()
            rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8')), delimiter='\t'))
            count_cols = [c for c in rows[0] if c not in ('srr_accession', 'primer_id', 'level_id')]
            assert len(count_cols) == 13
            assert len(rows) == len({r['srr_accession'] for r in rows}) == 22
            values = {r['srr_accession']: {'total': sum(int(r[c]) for c in count_cols),
                'primer': r['primer_id'], 'mass_label': r['level_id']} for r in rows}
            selected[member] = {'bytes': len(raw), 'sha256': sha(raw), 'count_columns': len(count_cols), 'rows': values}
    d = selected['data/figure2D.tsv']['rows']
    s = selected['data/figureS3.tsv']['rows']
    assert set(d) == set(s)
    audit = [{'run_accession': k, 'figure2d_total_reads': d[k]['total'], 'figure_s3_total_reads': s[k]['total'],
              'primer_labels_agree': d[k]['primer'] == s[k]['primer'],
              'literal_mass_labels_agree': d[k]['mass_label'] == s[k]['mass_label']} for k in sorted(d)]
    return {'kind': 'EXPLORATORY_POST_CAPTURE_CAPTION_CONSISTENCY_CHECK', 'rows': 22,
        'same_accession_set': True, 'summed_count_columns_per_row': 13,
        'figure_s3_total_read_values': sorted(set(r['figure_s3_total_reads'] for r in audit)),
        'figure2d_total_read_min': min(r['figure2d_total_reads'] for r in audit),
        'figure2d_total_read_max': max(r['figure2d_total_reads'] for r in audit),
        'figure2d_rows_above_60000': sum(r['figure2d_total_reads'] > 60000 for r in audit),
        'literal_mass_label_disagreements': sum(not r['literal_mass_labels_agree'] for r in audit),
        'primer_label_disagreements': sum(not r['primer_labels_agree'] for r in audit),
        'row_audit': audit, 'random_draw_or_seed_reconstructed': False, 'new_fit': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--data-archive', type=Path)
    args = parser.parse_args()
    prov = jread(HERE / 'SOURCE_PROVENANCE.json')
    manifest = jread(HERE / 'PUBLIC_FILES.json')
    assert {p.name for p in HERE.iterdir() if p.is_file()} == set(manifest['files']), 'Public file inventory mismatch'
    for line in (HERE / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert sha((HERE / name).read_bytes()) == digest, name
    repo = HERE.parent.parent
    for record in prov['frozen_dependencies']:
        assert sha((repo / record['path']).read_bytes()) == record['sha256'], record['path']
    output = {'public_integrity': 'PASS', 'frozen_dependencies': 'PASS', 'source_replay': 'UNRUN'}
    if args.source_cache is not None or args.data_archive is not None:
        assert args.source_cache is not None and args.data_archive is not None, 'Supply both external source paths.'
        for record in prov['saved_acquisition_files'] + prov['worker_complementary_acquisition']['saved_files']:
            data = (args.source_cache / record['filename']).read_bytes()
            assert len(data) == record['bytes'] and sha(data) == record['sha256'], record['filename']
        assert sha(args.data_archive.read_bytes()) == prov['reused_data_archive']['sha256']
        frame = jread(repo / 'research/calibration_sample_provenance/JOIN_AUDIT.json')
        capture = derive_capture(jread(args.source_cache / 'S01_firecrawl_pdf_scrape.json'), frame)
        assert capture == jread(HERE / 'SUPPLEMENT_AUDIT.json')
        totals = derive_totals(args.data_archive)
        assert totals == jread(HERE / 'COUNT_TOTAL_AUDIT.json')
        assert not (args.source_cache / 'S02_pdf_download_interstitial.html').read_bytes().startswith(b'%PDF')
        output.update(source_replay='PASS', original_pdf_byte_authentication='UNAVAILABLE',
                      identifier_queries=capture['literal_identifier_queries'], identifier_hits=capture['literal_identifier_hits'],
                      figure_s3_total_read_values=totals['figure_s3_total_read_values'],
                      figure2d_total_read_range=[totals['figure2d_total_read_min'],totals['figure2d_total_read_max']],
                      source_capture_depth='18/18 pages reported by provider; text representation only')
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
