"""Offline source-pinned normalization arithmetic; no clinical data fitting."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
from math import isqrt
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent

def rational(value, name):
    if type(value) not in (int, F):
        raise TypeError(name+' must be exact int/Fraction, not bool or float')
    return F(value)

def nominal_density(count, plated_microlitres, concentration=1, dilution=1):
    """Nominal CFU per original mL; volume adjustment is not recovery."""
    n, v, k, d = (rational(x,name) for x,name in
                  [(count,'count'),(plated_microlitres,'volume'),
                   (concentration,'concentration'),(dilution,'dilution')])
    if n<0 or v<=0 or k<=0 or d<1:
        raise ValueError('Count must be nonnegative; volume/concentration positive; dilution at least1')
    return F(1000)*n*d/(v*k)

def midpoint_median(values):
    if not values:
        raise ValueError('Median requires values')
    values=sorted(rational(x,'value') for x in values)
    n=len(values)
    return values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2

def exact_sqrt(value):
    value=rational(value,'radical')
    if value<0:
        raise ValueError('Negative radical')
    a,b=isqrt(value.numerator),isqrt(value.denominator)
    return F(a,b) if a*a==value.numerator and b*b==value.denominator else None

def encode(value):
    if isinstance(value,F):
        return str(value)
    if isinstance(value,dict):
        return {str(k):encode(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [encode(v) for v in value]
    return value

def arithmetic():
    if sys.flags.optimize:
        raise RuntimeError('Verification requires ordinary Python without -O/-OO')
    checks=0
    def check(condition):
        nonlocal checks
        if not condition:
            raise RuntimeError('Frozen normalization arithmetic failed')
        checks+=1
    suspension=nominal_density(1,1)
    original=nominal_density(1,1,10)
    check(suspension==1000)
    check(original==100)
    check(F(10,1)/F(1,1)==10)
    check(F(1,1000)*10==F(1,100))
    check(F(5500,10)==550)
    check(72-69==3)
    check(72-71==1)
    grid=[]
    for q in (F(100),F(1000)):
        step=q/2
        compatible=(F(10)/step).denominator==1
        check(not compatible)
        check((F(5500)/step).denominator==1)
        grid.append({'nominal_single_colony_density':q,
                     'ordinary_even_sample_midpoint_median_step':step,
                     'reported_10_on_this_grid':compatible,
                     'reported_5500_on_this_grid':True})
    # Explicit synthetic distribution, not raw clinical observations.
    raw=[F(0)]*36+[F(100)]*36
    adjusted=[F(1) if x==0 else x for x in raw]
    raw_median=midpoint_median(raw)
    center=(adjusted[35],adjusted[36])
    backtransformed=exact_sqrt(center[0]*center[1])
    check(raw_median==50)
    check(center==(F(1),F(100)))
    check(backtransformed==10)
    check(exact_sqrt(F(101)) is None)
    check(exact_sqrt(F(1000)) is None)
    # A different synthetic paired set witnesses non-equivalent summaries.
    untreated=[F(100),F(200),F(10000)]
    treated=[F(110000),F(100),F(120000)]
    ratio=midpoint_median(treated)/midpoint_median(untreated)
    paired=[t/u for u,t in zip(untreated,treated)]
    median_fold=midpoint_median(paired)
    check(ratio==550)
    check(paired==[F(1100),F(1,2),F(12)])
    check(median_fold==12)
    check(ratio!=median_fold)
    common_scaled=midpoint_median([x/10 for x in treated])/midpoint_median([x/10 for x in untreated])
    check(common_scaled==ratio)
    asymmetric=F(5500,10)/F(10)
    check(asymmetric==55)
    invalid=[lambda: nominal_density(-1,1),lambda:nominal_density(1,0),
             lambda:nominal_density(1,1,0),lambda:nominal_density(1,1,1,0),
             lambda:nominal_density(True,1),lambda:nominal_density(1,0.001),
             lambda:midpoint_median([]),lambda:exact_sqrt(-1)]
    for operation in invalid:
        try:operation()
        except (ValueError,TypeError):checks+=1
        else:raise RuntimeError('Invalid exact-arithmetic input admitted')
    return encode({'status':'PASS','checks':checks,
        'source_reported_numbers_preserved':{'untreated_median_CFU_per_mL':10,
                                            'treated_median_CFU_per_mL':5500,
                                            'ratio_of_reported_marginal_medians':F(550)},
        'nominal_volume_map':{'original_mL':10,'resuspension_mL':1,
                              'plated_microlitres':1,'nominal_concentration_factor':F(10),
                              'one_colony_per_mL_suspension':suspension,
                              'one_colony_per_original_mL_if_10fold_mapping_applies':original,
                              'nominal_original_mL_represented_by_1uL':F(1,100),
                              'biological_recovery_calibrated':False},
        'conditional_ordinary_even_sample_median_grids':grid,
        'synthetic_log_median_witness':{'clinical_data':False,'n':72,
             'synthetic_sorted_multiset':[{'value':'0','multiplicity':36},{'value':'100','multiplicity':36}],
             'ordinary_untransformed_midpoint_median':raw_median,
             'zero_only_replacement':1,'adjusted_central_values':center,
             'backtransformed_log_midpoint_median_exact':backtransformed,
             'all_values_plus1_radical_argument':101,
             'all_values_plus1_rational_square_root':None,
             'actual_source_reporting_convention_authenticated':False},
        'synthetic_paired_summary_witness':{'clinical_data':False,
             'untreated_values':untreated,'treated_values':treated,
             'ratio_of_marginal_medians':ratio,'paired_fold_changes':paired,
             'median_paired_fold_change':median_fold},
        'conditional_scaling':{'common10fold_scaling_preserves_median_ratio':common_scaled,
             'if_only_treated_reported_densities_were10fold_concentrated_original_ratio':asymmetric,
             'actual_between_group_normalization_authenticated':False},
        'actual_registry_fields_resolved':0,'biological_fit':False,
        'new_confidence_interval_or_theorem_claim':False})

def normalize(node):
    return ' '.join(''.join(node.itertext()).split())

def verify(source_dir,response_dir):
    if sys.flags.optimize:
        raise RuntimeError('Verification requires ordinary Python without -O/-OO')
    manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    contract=json.loads((ROOT/'NORMALIZATION_CONTRACT.json').read_text())
    checks=0
    def check(condition,message):
        nonlocal checks
        if not condition:raise ValueError(message)
        checks+=1
    for source in manifest['cached_primary_sources']:
        path=source_dir/source['file']
        if not path.is_file():raise FileNotFoundError('UNRUN: required cached primary source absent: '+source['file'])
        data=path.read_bytes()
        check(len(data)==source['bytes'],'Primary source size mismatch')
        check(hashlib.sha256(data).hexdigest()==source['sha256'],'Primary source hash mismatch')
        node=ET.fromstring(data)
        article=node.find('article')
        check(article is not None,'Primary article absent')
        ids={x.get('pub-id-type'):x.text for x in article.findall('front/article-meta/article-id')}
        check(ids.get('doi')==source['doi'],'Primary DOI mismatch')
        check('creativecommons.org/licenses/by/4.0/' in ET.tostring(article.find('front/article-meta/permissions'),encoding='unicode'),'Cached primary license mismatch')
        text=normalize(article)
        for anchor in contract['source_anchors'][source['pmcid']]:
            check(anchor in text,'Source anchor absent: '+anchor)
        if source['pmcid']=='PMC13228076':
            supplement=article.find(".//supplementary-material[@id='SuF1']")
            check(supplement is not None,'Declared supplement absent')
            media=supplement.find('media')
            check(media.get('{http://www.w3.org/1999/xlink}href')=='spectrum.03910-25-s0001.docx','Declared filename mismatch')
            check(supplement.findtext("object-id[@pub-id-type='doi']")=='10.1128/spectrum.03910-25.SuF1','Supplement DOI mismatch')
    requests=manifest['new_requests']
    check(len(requests)==4 and len({r['url'] for r in requests})==4,'New request identity/count mismatch')
    check(sum(r['response_bytes_saved'] for r in requests)==71716,'New response byte sum mismatch')
    check(len(requests)<=6 and sum(r['response_bytes_saved'] for r in requests)<=5*1024*1024,'Round acquisition cap exceeded')
    check([r['status'] for r in requests]==[404,None,404,200],'Observed request outcomes changed')
    check(all(not r['automatic_redirects_followed'] for r in requests),'Unaccounted redirects')
    response_checks=0
    if response_dir is not None:
        for response in requests:
            if not response['response_bytes_saved']:continue
            path=response_dir/response['output_file']
            if not path.is_file():raise FileNotFoundError('UNRUN: cached failure response absent: '+response['output_file'])
            data=path.read_bytes()
            check(len(data)==response['response_bytes_saved'],'Failure response size mismatch')
            check(hashlib.sha256(data).hexdigest()==response['sha256'],'Failure response hash mismatch')
            check(not zipfile.is_zipfile(path),'Previously failed response is unexpectedly a ZIP')
            response_checks+=3
        captcha=(response_dir/'pmc_instance_supplement_response.docx').read_text()
        check('Checking your browser - reCAPTCHA' in captcha,'Recorded challenge identity changed')
        response_checks+=1
    result=arithmetic()
    check(result==json.loads((ROOT/'NORMALIZATION_ARITHMETIC.json').read_text()),'Frozen arithmetic differs')
    return {'status':'PASS','source_and_acquisition_checks':checks,
            'cached_failure_response_checks':response_checks,
            'failure_response_replay':'PASS' if response_dir is not None else 'UNRUN',
            'arithmetic_checks':result['checks'],'new_requests':4,'new_response_bytes':71716,
            'supplement_filename_declared':True,'authenticated_DOCX_acquired':False,
            'clinical_table_read':False,'clinical_table_reanalysis':False,
            'actual_source_reporting_convention_authenticated':False,
            'known_introduced_units_or_lineages_authenticated':False,
            'actual_registry_fields_resolved':0,'biological_fit':False,
            'engine_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

def main():
    if sys.flags.optimize:raise SystemExit('Verification requires ordinary Python without -O/-OO')
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--source-dir',type=Path)
    mode.add_argument('--arithmetic-only',action='store_true')
    parser.add_argument('--response-dir',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--check-against',type=Path)
    args=parser.parse_args()
    if args.arithmetic_only and args.response_dir:
        raise SystemExit('--arithmetic-only does not inspect source/response caches')
    result=arithmetic() if args.arithmetic_only else verify(args.source_dir,args.response_dir)
    if args.check_against and result!=json.loads(args.check_against.read_text()):
        raise ValueError('Offline normalization verification differs from frozen receipt')
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
