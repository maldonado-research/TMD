#!/usr/bin/env python3
"""Verify original R4 ledger against pinned primary-source cache. MIT license."""
import argparse,datetime,hashlib,json,sys,xml.etree.ElementTree as E
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--ledger-root',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--raw-source-root',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();root=args.ledger_root.resolve()
 def load(name):return json.loads((root/name).read_text())
 q=load('QUERY_RECEIPT.json');s=load('SOURCES.json');screen=load('SCREENING_LEDGER.json');base=load('BASELINE_SOURCE_DEDUP.json');a=load('SOURCE_TEXT_ANCHORS.json');m=load('MEASUREMENT_LEDGER.json')
 assert q['source_acquisitions_attempted']==len(q['attempts'])==12
 assert q['successful_responses']==9
 assert q['total_downloaded_response_bytes']==sum(v['bytes'] for v in q['attempts'])==1195578
 assert q['total_downloaded_response_bytes']<=q['maximum_download_bytes'] and q['source_acquisitions_attempted']<=q['maximum_source_acquisitions']
 assert q['elapsed_wall_minutes_at_candidate_preparation']<q['maximum_active_minutes']==45
 assert q['publication_cutoff_local']==s['review_date_local']=='2026-10-02' and q['cutoff_timezone']==s['cutoff_timezone']=='America/Los_Angeles'
 assert not q['credential_used'] and q['tls_certificate_verification'] and not q['raw_third_party_material_publication']
 assert q['admitted_matched_WAM_biological_datasets']==s['matched_WAM_ledger_admitted_count']==0
 assert q['new_tmd_hypothesis_tests']==q['new_biological_observations_collected']==0
 assert len(s['sources'])==q['new_primary_source_assessments']==3 and len({v['doi'] for v in s['sources']})==3
 for source in s['sources']:
  assert source['doi'].lower() not in base['doi_identifiers']
  assert datetime.date.fromisoformat(source['published_online'])<=datetime.date(2026,10,2)
  assert not source['matched_WAM_ledger_admitted'] and not source['independent_replication_claimed'] and not source['raw_redistribution_by_default']
 assert len(s['existing_sources_watched'])==2
 for source in s['existing_sources_watched']:
  assert source['current_crossref_sha256']==source['prior_crossref_sha256'] and source['byte_identical'] and not source['new_independent_evidence']
 assert len(screen['records'])==screen['indexed_records_screened']==13
 assert sum(v['selected_for_primary_full_text'] for v in screen['records'])==3
 anaerobe=[v for v in screen['records'] if v['pmid'] in ['41369254','40060621']]
 assert len(anaerobe)==2 and len({v['evidence_family'] for v in anaerobe})==1
 assert len(a['anchors'])==72 and len(m['rows'])==m['rows_count']==10
 assert all(not v['admitted_to_WAM_likelihood'] for v in m['rows'])
 result={'schema_version':1,'status':'passed','round_id':'R000004','public_ledger_checks_passed':True,'source_cache_checked':args.raw_source_root is not None,'primary_articles_identity_date_checks':0,'primary_paragraph_hashes_checked':0,'response_hashes_checked':0,'deduplicated_preprint_records_unchanged':2,'matched_WAM_panels_admitted':0,'biological_hypothesis_tests_performed':0,'authors_code_or_raw_data_executed':False,'verification_scope':'Identity, date, acquisition budgets, source hashes, paragraph pins and stated bookkeeping; independent interpretation review is separate.'}
 if args.raw_source_root:
  raw=args.raw_source_root.resolve()
  for record in q['attempts']:
   path=Path(record['raw_path'])
   assert len(path.parts)==2 and path.parts[0]=='raw' and '..' not in path.parts
   data=(raw/path.name).read_bytes();assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256'];result['response_hashes_checked']+=1
  for source in s['sources']:
   data=(raw/source['raw_cache_filename']).read_bytes();assert hashlib.sha256(data).hexdigest()==source['raw_primary_xml_sha256']
   article=E.fromstring(data).find('.//article');meta=article.find('front/article-meta');ids={v.get('pub-id-type'):v.text for v in meta.findall('article-id')}
   assert ids['doi']==source['doi'] and ids['pmcid']==source['pmcid'] and ids['pmid']==source['pmid'] and ids['pmcid-ver']==source['source_version']
   title=''.join(meta.find('title-group/article-title').itertext());assert title==source['title']
   authors=[' '.join(filter(None,[v.findtext('name/given-names'),v.findtext('name/surname')])) for v in meta.findall('contrib-group/contrib') if v.get('contrib-type')=='author'];assert authors==source['authors']
   d=meta.find("pub-date[@pub-type='epub']");date='-'.join([d.findtext('year'),d.findtext('month').zfill(2),d.findtext('day').zfill(2)]);assert date==source['published_online'];result['primary_articles_identity_date_checks']+=1
   for anchor in [v for v in a['anchors'] if v['source_id']==source['id']]:
    sec=article.find("body//sec[@id='%s']"%anchor['section_id']);paragraph=sec.findall('p')[anchor['paragraph_index_zero_based']]
    assert paragraph.get('id')==anchor['paragraph_id']
    assert hashlib.sha256(''.join(paragraph.itertext()).encode()).hexdigest()==anchor['normalized_itertext_sha256'];result['primary_paragraph_hashes_checked']+=1
  dataset=json.loads((raw/'nlpd_dataset_14335473.json').read_text());src=next(v for v in s['sources'] if v['id']=='nlpd_hotspot_2025');f=src['data_availability']['dataset_file'];actual=dataset['files'][0]
  assert dataset['metadata']['doi']==src['data_availability']['dataset_doi']
  assert f['filename']==actual['key'] and f['size_bytes_reported']==actual['size']==7880751 and f['checksum_reported']==actual['checksum'] and not f['downloaded']
  assert dataset['metadata']['license']['id']=='cc-by-4.0'
  assert result['response_hashes_checked']==12 and result['primary_paragraph_hashes_checked']==72
 if args.check:
  saved=load('VERIFICATION_RECEIPT.json')
  if args.raw_source_root:assert saved==result,'saved verification receipt differs'
 else:(root/'VERIFICATION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))

if __name__=='__main__':
 try:main()
 except (AssertionError,KeyError,ValueError,OSError,E.ParseError) as error:
  print('Verification failed: '+str(error),file=sys.stderr);sys.exit(1)
