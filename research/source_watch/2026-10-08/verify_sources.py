#!/usr/bin/env python3
"""Verify locally captured source representations; no network or numeric refit."""
import argparse
import hashlib
import json
from pathlib import Path


def document(response):
    if 'value' in response:
        response = response['value']
    value = response.get('structuredContent')
    if value and value.get('markdown'):
        return value
    return json.loads(next(c['text'] for c in response['content'] if c['type'] == 'text'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).parent / 'SOURCES.json').read_text())
    checks = []

    def require(condition, label):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    docs = {}
    for entry in manifest['source_entries']:
        data = (args.source_cache / (entry['id'] + '.json')).read_bytes()
        require(len(data) == entry['saved_response_bytes'], entry['id'] + ':saved_bytes')
        require(hashlib.sha256(data).hexdigest() == entry['source_response_sha256'], entry['id'] + ':saved_sha256')
        value = document(json.loads(data)['result'])
        md = value['markdown'].encode('utf-8')
        require(len(md) == entry['markdown_bytes'], entry['id'] + ':parsed_bytes')
        require(hashlib.sha256(md).hexdigest() == entry['markdown_sha256'], entry['id'] + ':parsed_sha256')
        require(value['metadata']['statusCode'] == 200, entry['id'] + ':http_200')
        require(value['metadata']['sourceURL'] == entry['source_url'], entry['id'] + ':source_url')
        docs[entry['id']] = value

    html = docs['primary_1']
    require(html['metadata']['citation_doi'] == '10.64898/2026.10.05.756661', 'new_preprint_DOI')
    require(html['metadata']['citation_date'] == '2026-10-07', 'version_posted_date')
    require('not been certified by peer review' in html['markdown'], 'preprint_status')
    require('## Model' not in html['markdown'], 'HTML_inspection_limited_to_abstract')
    pdf = docs['theory_pdf']
    require(pdf['metadata']['numPages'] == 14 and pdf['metadata']['totalPages'] == 14, 'provider_reports_14_processed_pages')
    require(pdf['metadata']['contentType'] == 'application/pdf', 'PDF_source_content_type')
    body = pdf['markdown']
    for anchor in ['## Model', '## Strong selection', '## Weak selection', '## Outlook',
                   '## Appendix C:', 'least fit genotype', 'subsequently reach the higher',
                   'no standing variation', 'probability of fixation', 'ongoing effect of mutation']:
        require(anchor in body, 'source_anchor:' + anchor)
    require('raw_pdf_sha256' in manifest['source_entries'][-1]
            and manifest['source_entries'][-1]['raw_pdf_sha256'] is None,
            'raw_PDF_bytes_not_claimed_verified')
    require(not manifest['numeric_formula_replay'] and not manifest['graphical_tables_used_as_data'],
            'no_unexecuted_formula_or_graphic_replay_claim')
    require(not manifest['reused_experimental_source']['new_independent_cohort'], 'R4_source_deduplicated')
    print(json.dumps({'status': 'PASS', 'checks': len(checks), 'check_ids': checks,
                      'scope': 'Captured response/parsed-representation identity and selected source anchors; not equation validity, numeric replay or biological truth'}, indent=2))


if __name__ == '__main__':
    main()
