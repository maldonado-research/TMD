"""Verify acquired primary identity/anchors, or explicitly limited public bookkeeping."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E


def normalize(element):
    return ' '.join(''.join(element.itertext()).split())


def verify(source):
    root=Path(__file__).resolve().parent
    ledger=json.loads((root/'SOURCE_LEDGER.json').read_text())
    measurements=json.loads((root/'MEASUREMENT_LEDGER.json').read_text())
    receipt=json.loads((root/'ACQUISITION_RECEIPT.json').read_text())
    assert len(receipt['requests'])<=receipt['maximum_requests']==3
    assert sum(x.get('bytes',0) for x in receipt['requests'])<=receipt['maximum_response_bytes']==5*1024*1024
    assert measurements['complete_matched_WAM_panel'] is False
    assert measurements['all_actual_study_fields_still_null']==26
    assert all(x['primary_anchor'] in {a['id'] for a in ledger['selected_primary_anchors']} for x in measurements['rows'])
    result={'public_ledger_checks':'passed','new_biological_TMD_confirmation':False,'matched_WAM_panels_admitted':0,'source_cache_identity_checks':0,'source_anchor_checks':0,'raw_source_replay':'UNRUN'}
    if source is not None:
        data=source.read_bytes()
        assert len(data)==ledger['full_primary_xml_bytes']
        assert hashlib.sha256(data).hexdigest()==ledger['full_primary_xml_sha256']==receipt['requests'][0]['sha256']
        article=E.fromstring(data).find('article')
        meta=article.find('front/article-meta')
        assert meta.findtext("article-id[@pub-id-type='doi']")==ledger['doi']
        assert meta.findtext("article-id[@pub-id-type='pmcid']")==ledger['pmcid']
        assert normalize(meta.find('title-group/article-title'))==ledger['title']
        authors=[' '.join([normalize(x.find('name/given-names')),normalize(x.find('name/surname'))]) for x in meta.findall('contrib-group/contrib') if x.get('contrib-type')=='author']
        assert authors==ledger['authors']
        date=meta.find("pub-date[@pub-type='epub']")
        assert date.get('iso-8601-date')==ledger['electronic_publication_date']
        permissions=meta.find('permissions')
        assert ledger['license_url'] in normalize(permissions)
        for anchor in ledger['selected_primary_anchors']:
            el=next(x for x in article.iter() if x.get('id')==anchor['id'])
            if el.tag=='fig':el=el.find('caption')
            text=normalize(el)
            assert len(text)==anchor['normalized_characters']
            assert hashlib.sha256(text.encode()).hexdigest()==anchor['sha256_normalized_text']
        result.update(source_cache_identity_checks=6,source_anchor_checks=len(ledger['selected_primary_anchors']),raw_source_replay='passed')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=verify(args.source)
    encoded=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(encoded)
    print(encoded,end='')
