"""Offline source-pinned measurement audit; never downloads or fits biological data."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

def read_json(path):
    return json.loads(path.read_text())

def normalized(node):
    return ' '.join(''.join(node.itertext()).split())

def audit(source_dir):
    if not __debug__:
        raise RuntimeError('Optimized Python is unsupported for verification.')
    count = 0
    def check(condition, message):
        nonlocal count
        if not condition:
            raise ValueError(message)
        count += 1
    manifest = read_json(ROOT/'SOURCE_MANIFEST.json')
    for record in manifest['sources']:
        path = source_dir/record['file']
        if not path.is_file():
            raise FileNotFoundError('UNRUN: required public source cache is absent: '+record['file'])
        data = path.read_bytes()
        check(len(data)==record['bytes'], 'Source byte size mismatch: '+record['file'])
        check(hashlib.sha256(data).hexdigest()==record['sha256'], 'Source SHA256 mismatch: '+record['file'])
    check(len(manifest['sources'])==4 and manifest['download_bytes']==506673,'Acquisition ledger mismatch')
    check(manifest['request_count']==4,'Request count mismatch')
    primary = {}
    for pmcid,doi in [('PMC13228076','10.1128/spectrum.03910-25'),('PMC13272224','10.1007/s00203-026-04995-3')]:
        root = ET.parse(source_dir/(pmcid+'.xml')).getroot()
        article = root.find('article')
        check(article is not None,'Missing primary article')
        ids = {n.get('pub-id-type'):n.text for n in article.findall('front/article-meta/article-id')}
        check(ids.get('doi')==doi,'Primary DOI mismatch')
        check(ids.get('pmcid')==pmcid,'Primary PMCID mismatch')
        check('https://creativecommons.org/licenses/by/4.0/' in ET.tostring(article.find('front/article-meta/permissions'),encoding='unicode'),'Inspected license mismatch')
        primary[pmcid] = normalized(article).casefold()
    articles = ET.parse(source_dir/'pubmed_candidates.xml').getroot().findall('PubmedArticle')
    check(len(articles)==8,'Candidate record count mismatch')
    by_pmid = {a.findtext('MedlineCitation/PMID'):a for a in articles}
    nano = by_pmid['42831674']
    ids = {n.get('IdType'):n.text for n in nano.findall('PubmedData/ArticleIdList/ArticleId')}
    check(ids.get('doi')=='10.1039/d6lc00655h','Newest lead DOI mismatch')
    check(ids.get('pmc') is None,'Newest lead inspection status changed')
    date = nano.find('MedlineCitation/Article/ArticleDate')
    check([date.findtext(t) for t in ['Year','Month','Day']]==['2026','10','05'],'Newest lead date mismatch')
    primary['pubmed:42831674'] = normalized(nano.find('MedlineCitation/Article/Abstract')).casefold()
    search = read_json(source_dir/'recovery_search.json')['esearchresult']
    check(int(search['count'])==45,'Search count mismatch')
    check(set(search['idlist'])==set(by_pmid),'Search/abstract candidate identity mismatch')
    ledger = read_json(ROOT/'MEASUREMENT_LEDGER.json')
    check(len(ledger['rows'])==20,'Measurement row count mismatch')
    check(len({r['id'] for r in ledger['rows']})==20,'Duplicate measurement row')
    anchors = 0
    for row in ledger['rows']:
        for anchor in row['anchors']:
            check(anchor.casefold() in primary[row['source']], 'Missing source anchor: '+row['id']+' / '+anchor)
            anchors += 1
    ratio = Fraction(5500,10)
    check(ratio==550,'Ratio of source-reported marginal medians mismatch')
    suspension = 1/Fraction(1,1000)
    check(suspension==1000,'Nominal one-colony suspension density mismatch')
    original = suspension/Fraction(10,1)
    check(original==100,'Conditional original-volume conversion mismatch')
    check(72-69==3 and 72-71==1,'Complete-case denominator arithmetic mismatch')
    return {'round':'R000012','status':'PASS','checks':count,'measurement_rows':20,'source_text_anchors':anchors,'source_requests':4,'source_download_bytes':506673,'exact_descriptive_arithmetic':{'ratio_of_reported_CFU_marginal_medians':str(ratio),'one_colony_in_one_microlitre_per_mL_suspension':str(suspension),'conditional_per_original_mL_if_tenfold_concentration_applies':str(original),'cross_method_exclusions':[3,1]},'fitted_recovery_probability':None,'biological_mutation_fit':False,'new_common_background_panels':0,'actual_registry_fields_resolved':0,'ledger_sha256':hashlib.sha256((ROOT/'MEASUREMENT_LEDGER.json').read_bytes()).hexdigest()}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--check-against',type=Path)
    args=parser.parse_args()
    result=audit(args.source_dir)
    if args.check_against and result!=read_json(args.check_against):
        raise ValueError('Source replay differs from the frozen receipt')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
