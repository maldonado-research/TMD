#!/usr/bin/env python3
"""Verify externally cached acquired bytes and source anchors; no network."""
import argparse, base64, hashlib, json, pathlib, xml.etree.ElementTree as ET, zipfile

def verify(cache, package):
    checked = []
    def require(ok, label):
        if not ok:
            raise AssertionError(label)
        checked.append(label)
    receipts = json.loads((package / 'SOURCE_ACQUISITION_RECEIPT.json').read_text())
    require(receipts['network_requests'] == 12, 'bounded_network_requests')
    require(receipts['network_response_bytes'] < 20 * 1024 * 1024, 'bounded_response_bytes')
    for rec in receipts['requests']:
        data = (cache / rec['name']).read_bytes()
        require(len(data) == rec['bytes'], 'source_bytes:' + rec['name'])
        require(hashlib.sha256(data).hexdigest() == rec['sha256'], 'source_sha256:' + rec['name'])
    require(sum(x['bytes'] for x in receipts['requests']) == receipts['network_response_bytes'], 'receipt_byte_total')
    for name in ('ptato_mmc2.xlsx', 'ptato_mmc3.xlsx'):
        data = (cache / name).read_bytes()
        require(not zipfile.is_zipfile(cache / name), 'supplement_not_xlsx:' + name)
        require(b'recaptcha' in data.lower() and data.lstrip().startswith(b'<!doctype html>'), 'supplement_is_challenge_html:' + name)
    xml = ET.parse(cache / 'ptato_pmc10504672.xml').getroot()
    require(any(x.text == '10.1016/j.xgen.2023.100389' for x in xml.findall('.//article-id')), 'article_doi_identity')
    paras = xml.findall('.//body//p')
    review = json.loads((package / 'SOURCE_REVIEW.json').read_text())
    require(len(paras) == review['article']['body_paragraph_count'], 'article_body_paragraph_count')
    for anchor in review['article']['anchors']:
        para = paras[anchor['one_based_body_paragraph'] - 1]
        require(para.get('id') == anchor['xml_id'], 'article_paragraph_id:' + str(anchor['one_based_body_paragraph']))
        require(hashlib.sha256(''.join(para.itertext()).strip().encode()).hexdigest() == anchor['paragraph_sha256'], 'article_paragraph_hash:' + str(anchor['one_based_body_paragraph']))
    manifest = json.loads((package / 'ARTIFACT_MANIFEST.json').read_text())
    figure = next(x for x in manifest['objects'] if x['role'] == 'figure_analysis_code')
    data = (cache / 'figure_code_v1.0.1.zip').read_bytes()
    require('md5:' + hashlib.md5(data).hexdigest() == figure['metadata_checksum'], 'figure_archive_md5')
    with zipfile.ZipFile(cache / 'figure_code_v1.0.1.zip') as archive:
        require(len(archive.infolist()) == 18, 'figure_archive_member_count')
        for member in figure['archive_members']:
            raw = archive.read(member['path'])
            require(len(raw) == member['size'], 'figure_member_bytes:' + member['path'])
            require(hashlib.sha256(raw).hexdigest() == member['sha256'], 'figure_member_sha256:' + member['path'])
        require(not any(x.filename.endswith('Table_S2.txt') for x in archive.infolist()), 'figure_metadata_not_included')
        prefix = 'ProjectsVanBox-PTATO-95ae7b1/'
        lines = archive.read(prefix + 'Figures/Figure2.R').decode().splitlines()
        for line, token in [(240, 'tmp_table[is.na(tmp_table)]'), (243, 'tmp_table[!is.na(tmp_table2)]'), (286, 'na.rm = T'), (1392, 'Previous_Clone'), (1395, 'MinimalVAF'), (1441, 'FAIL_QC'), (1442, 'LOW_COV'), (1459, '17:'), (1529, 'mean = mean'), (1533, 'sum = sum'), (1555, 'Overview_CloneVariants$Variant'), (1557, '%in% CallableVariants')]:
            require(token in lines[line - 1], 'figure_code_anchor:' + str(line))
        require(b'MIT License' in archive.read(prefix + 'LICENSE'), 'figure_license')
    for name in ['tool_LICENSE_blob.json', 'tool_resources_config_blob.json', 'tool_process_config_blob.json', 'tool_README_blob.json']:
        blob = json.loads((cache / name).read_text())
        raw = base64.b64decode(blob['content'])
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blob['sha'], 'git_blob_identity:' + name)
    tree = json.loads((cache / 'github_tool_v1.2.4_tree.json').read_text())
    require(tree['truncated'] is False, 'tool_tree_not_truncated')
    require(len([x for x in tree['tree'] if x['type'] == 'blob']) == 154, 'tool_tree_blob_count')
    require(tree['sha'] == 'cfa3351b6341d71534d07b3acdf0b60e222fdaae', 'tool_tree_identity')
    return {'status': 'PASS', 'checks': len(checked), 'check_ids': checked, 'scope': 'Source-byte, metadata, code-line and manifest identity checks only; not semantic/external qualification or numerical reproduction', 'network_requests': 0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=pathlib.Path, required=True)
    parser.add_argument('--package', type=pathlib.Path, default=pathlib.Path(__file__).parent)
    args = parser.parse_args()
    print(json.dumps(verify(args.cache, args.package), indent=2))
