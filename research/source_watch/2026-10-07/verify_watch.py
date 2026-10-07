"""Read-only verification of a bounded PubMed metadata/abstract screening receipt."""
from pathlib import Path
import argparse,json,hashlib,xml.etree.ElementTree as E
p=argparse.ArgumentParser();p.add_argument('--raw-source-root',type=Path);args=p.parse_args()
root=Path(__file__).resolve().parent
r=json.loads((root/'SOURCE_WATCH_RECEIPT.json').read_text())
assert r['request_count']==2 and r['retrieved_record_count']==2 and r['new_biological_panels_admitted']==0
assert all(not x['fulltext_read'] and x['abstract_read'] and not x['matched_WAM_panel_admitted'] for x in r['screened_records'])
expected={'42832043':'10.1093/jeb/voag096','42827080':'10.1093/molbev/msag238'}
assert {x['pmid']:x['doi'] for x in r['screened_records']}==expected
replayed=0
if args.raw_source_root:
 for item in r['requests']:
  body=(args.raw_source_root/item['cache_filename']).read_bytes()
  assert len(body)==item['response_bytes'] and hashlib.sha256(body).hexdigest()==item['sha256']
  replayed+=1
 search=json.loads((args.raw_source_root/'search.json').read_text())
 assert set(search['esearchresult']['idlist'])==set(expected)
 xml=E.fromstring((args.raw_source_root/'records.xml').read_bytes())
 assert {a.findtext('MedlineCitation/PMID'):next(i.text for i in a.findall('PubmedData/ArticleIdList/ArticleId') if i.get('IdType')=='doi') for a in xml.findall('PubmedArticle')}==expected
 assert all(a.find('MedlineCitation/Article/Abstract') is not None for a in xml.findall('PubmedArticle'))
print(json.dumps({'receipt_bookkeeping':'pass','raw_response_hashes_replayed':replayed,'raw_source_replay':'pass' if replayed else 'UNRUN','fulltext_or_data_reanalysis_performed':False},indent=2))
