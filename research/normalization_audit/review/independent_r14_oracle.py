"""Independently check nominal units, summary ambiguity and primary sources."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile


def main():
    if sys.flags.optimize:
        raise SystemExit('Independent verification requires ordinary Python')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True)
    ap.add_argument('--source-dir', type=Path, required=True)
    ap.add_argument('--response-dir', type=Path, required=True)
    ap.add_argument('--expected-engine-sha256', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    engine = args.package/'verify_normalization.py'
    if hashlib.sha256(engine.read_bytes()).hexdigest() != args.expected_engine_sha256:
        raise ValueError('Independent review engine pin differs')
    spec = importlib.util.spec_from_file_location('reviewed_normalization', engine)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []

    def check(ok, name):
        if not ok:
            raise ValueError('Independent review failed: '+name)
        checks.append(name)

    cases = 0
    for n in (0,1,3,17):
        for concentration in (F(1),F(5,2),F(10)):
            for volume in (1,10,100):
                represented_original_mL = F(volume,1000)*concentration
                expected = F(n)/represented_original_mL
                check(module.nominal_density(n,volume,concentration)==expected,'original_volume_unit_identity')
                check(module.nominal_density(n,volume,concentration,7)==7*expected,'dilution_unit_identity')
                cases += 1
    arithmetic = json.loads((args.package/'NORMALIZATION_ARITHMETIC.json').read_text())
    witness = arithmetic['synthetic_log_median_witness']
    check(F(witness['ordinary_untransformed_midpoint_median'])==F(0+100,2)==50,'raw_even_median')
    check(F(witness['backtransformed_log_midpoint_median_exact'])**2==F(1)*100,'geometric_midpoint_square')
    check(not witness['actual_source_reporting_convention_authenticated'] and not witness['clinical_data'],
          'conditional_witness_not_source_data')
    paired = arithmetic['synthetic_paired_summary_witness']
    before = [F(v) for v in paired['untreated_values']]
    after = [F(v) for v in paired['treated_values']]
    raw_ratio = sorted(after)[1]/sorted(before)[1]
    pair_median = sorted(a/b for a,b in zip(after,before))[1]
    check(raw_ratio==550 and pair_median==12 and raw_ratio!=pair_median,'paired_vs_marginal_inequality')
    manifest = json.loads((args.package/'SOURCE_MANIFEST.json').read_text())
    source_text = {}
    for source in manifest['cached_primary_sources']:
        data = (args.source_dir/source['file']).read_bytes()
        check(hashlib.sha256(data).hexdigest()==source['sha256'],'cached_primary_hash')
        article = ET.fromstring(data).find('article')
        ids = {n.get('pub-id-type'):n.text for n in article.findall('front/article-meta/article-id')}
        check(ids.get('doi')==source['doi'],'primary_doi_identity')
        source_text[source['pmcid']] = ' '.join(''.join(article.itertext()).split())
    dtt = source_text['PMC13228076']
    for anchor in ['10 mL of urine','resuspended in 1 mL','1 µL','12 h','<10 CFU/mL',
                   'constant value of 1 CFU','N = 69','N = 71','All 72 pairs',
                   'spectrum.03910-25-s0001.docx']:
        check(anchor in dtt,'independent_dtt_source_anchor')
    pa14 = source_text['PMC13272224']
    check('PA14' in pa14 and '24 h' in pa14,'unmatched_pa14_frame_retained')
    requests = manifest['new_requests']
    check(len(requests)==4 and sum(r['response_bytes_saved'] for r in requests)==71716,
          'new_acquisition_count_bytes')
    check(len({r['url'] for r in requests})==4,'distinct_requests')
    for row in requests:
        if not row['response_bytes_saved']:
            check(row['status'] is None and '403' in row['transport_error'],'no_body_proxy_failure')
            continue
        file = args.response_dir/row['output_file']
        data = file.read_bytes()
        check(len(data)==row['response_bytes_saved'],'failure_response_size')
        check(hashlib.sha256(data).hexdigest()==row['sha256'],'failure_response_hash')
        check(not zipfile.is_zipfile(file),'html_not_authenticated_docx')
    check('reCAPTCHA' in (args.response_dir/'pmc_instance_supplement_response.docx').read_text(),
          'http200_is_challenge_not_data')
    check(arithmetic['actual_registry_fields_resolved']==0 and not arithmetic['biological_fit'],
          'no_study_input_or_biological_fit')
    result = {'status':'PASS','scope':'nominal dimensional arithmetic and selected primary-source checks',
              'finite_volume_cases':cases,'total_checks':len(checks),'checks':checks,
              'engine_sha256':args.expected_engine_sha256,'reviewer_network_requests':0,
              'clinical_table_acquired_or_read':False,'actual_normalization_authenticated':False,
              'external_peer_review':False}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','volume_cases':cases,'checks':len(checks)}))


if __name__=='__main__':
    main()
