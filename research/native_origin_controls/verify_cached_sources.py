"""Read-only cached primary-source identity checks; no acquisition or inference."""
from pathlib import Path
import argparse, hashlib, json, xml.etree.ElementTree as ET

def verify(cache_dir):
    package = Path(__file__).resolve().parent
    review = json.loads((package/'SOURCE_REVIEW.json').read_text())
    rows=[]; checks=0; missing=[]; failures=[]
    for source in review['sources']:
        p=cache_dir/(source['pmc']+'.xml')
        if not p.is_file():
            missing.append(source['pmc']); continue
        raw=p.read_bytes()
        if len(raw)!=source['xml_bytes'] or hashlib.sha256(raw).hexdigest()!=source['xml_sha256']:
            failures.append({'source':source['id'],'problem':'XML identity mismatch'});continue
        checks+=2
        doc=ET.fromstring(raw);art=doc if doc.tag=='article' else doc.find('article')
        if art is None:
            failures.append({'source':source['id'],'problem':'Missing article element'});continue
        norm=lambda e: ''.join(e.itertext()).strip() if e is not None else ''
        ids={e.get('pub-id-type'):norm(e) for e in art.findall('./front/article-meta/article-id')}
        paras=art.findall('./body//p')
        tests=[ids.get('doi')==source['doi'],norm(art.find('./front/article-meta/title-group/article-title'))==source['title'],len(paras)==source['body_paragraph_count']]
        if not all(tests):
            failures.append({'source':source['id'],'problem':'Primary metadata/paragraph count mismatch'});continue
        checks+=len(tests)
        for anchor in source['anchors']:
            i=anchor['one_based_index']
            if not 1<=i<=len(paras) or hashlib.sha256(norm(paras[i-1]).encode()).hexdigest()!=anchor['paragraph_sha256']:
                failures.append({'source':source['id'],'problem':'Paragraph identity mismatch','one_based_index':i})
            checks+=1
        rows.append({'source':source['id'],'source_sha256':source['xml_sha256'],'anchors_checked':len(source['anchors']),'assessment_depth':source['assessment_depth']})
    acquisition=json.loads((package/'SOURCE_ACQUISITION_RECEIPT.json').read_text())
    acquisition_ok=len(acquisition)==review['source_request_count'] and sum(x.get('bytes',0) for x in acquisition)==review['source_response_bytes'] and all(x.get('status')==200 and 'error_type' not in x for x in acquisition)
    checks+=3
    if not acquisition_ok: failures.append({'problem':'Acquisition budget/identity receipt inconsistent'})
    return {'record_id':'R000021','status':'FAIL' if failures else ('UNRUN_MISSING_CACHE' if missing else 'PASS_CACHED_SOURCE_IDENTITY'),'identity_checks':checks,'sources':rows,'missing_sources':missing,'failures':failures,'new_network_requests':0,'source_semantics_validated_by_hashes':False,'actual_study_fields_resolved':0}

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    package=Path(__file__).resolve().parent
    if a.output.resolve().is_relative_to(package):p.error('Outputs must be outside the packaged source directory')
    receipt=verify(a.cache_dir);a.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'identity_checks':receipt['identity_checks'],'sources':len(receipt['sources'])}))
    return 0 if receipt['status']=='PASS_CACHED_SOURCE_IDENTITY' else 2

if __name__=='__main__':raise SystemExit(main())
