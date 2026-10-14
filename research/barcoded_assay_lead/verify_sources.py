#!/usr/bin/env python3
"""Verify R31 source representations and preserved registries; no fit or network."""
import argparse,hashlib,json,re
from pathlib import Path
F=Path(__file__).resolve().parent; R=F.parents[1]
def read(p):
 def unique(pairs):
  d={}
  for k,v in pairs:
   if k in d:raise ValueError('Duplicate JSON key: '+k)
   d[k]=v
  return d
 return json.loads(p.read_text(),object_pairs_hook=unique)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,label):
 if not ok:raise ValueError(label)
def representation(p):
 d=read(p);s=d.get('structuredContent',{})
 if isinstance(s,dict) and s.get('markdown'):return s
 for c in d.get('content',[]):
  if c.get('type')=='text':
   try:s=json.loads(c['text'])
   except (ValueError,TypeError):continue
   if isinstance(s,dict) and s.get('markdown'):return s
 raise ValueError('No markdown representation: '+p.name)
def norm(s):return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s.replace('*',''))).strip()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-cache',type=Path);args=p.parse_args()
 prov=read(F/'SOURCE_PROVENANCE.json');a=read(F/'ASSESSMENT.json');decision=read(F/'DECISION.json')
 require(prov['logical_scientific_calls']==len(prov['calls'])==len(prov['saved_acquisition_files'])==3,'three acquisitions')
 require(sum(x['bytes'] for x in prov['saved_acquisition_files'])==prov['saved_acquisition_bytes']<=prov['byte_allocation'],'byte accounting')
 require(not prov['original_PDF_bytes_acquired'] and not prov['raw_source_bodies_published'] and not prov['source_data_reanalysed'],'representation boundary')
 require(a['reported_system']['organism']=='Saccharomyces cerevisiae' and a['reported_system']['tracked_barcode_count']==119672 and a['reported_system']['undetectable_post_selection_percent']==84,'reported source frame')
 require(a['biological_inference_status']=='METHOD_LEAD_ONLY_NO_NATIVE_PANEL_OR_FIT' and not a['experiment_commissioned'] and not a['new_mathematical_theorem'],'no biological/theorem admission')
 require(decision['study_fields_resolved']==decision['planning_fields_resolved']==decision['matched_panels_admitted']==0,'no actual admissions')
 for m in prov['inherited_dependencies']:
  path=Path(m['path']);require(not path.is_absolute() and '..' not in path.parts,'safe inherited path');f=R/path;require(f.stat().st_size==m['bytes'] and sha(f)==m['sha256'],'inherited identity '+str(path))
 actual=read(R/'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution'];planning=read(R/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
 require(len(actual)==26 and all(v is None for v in actual.values()),'26 NULL actual fields');require(len(planning)==18 and all(v is None for v in planning.values()),'18 NULL planning fields')
 public=read(F/'PUBLIC_FILES.json')['public_files'];require(len(public)==len(set(public))==11,'eleven public files');require(all(isinstance(n,str) and Path(n).name==n and n not in ('.','..') for n in public),'safe public names');require(set(public)=={x.name for x in F.iterdir()} and all(x.is_file() and not x.is_symlink() for x in F.iterdir()),'public closure')
 covered=set()
 for line in (F/'SHA256SUMS.txt').read_text().splitlines():
  h,n=line.split('  ',1);require(Path(n).name==n and n in public and n not in covered,'safe checksum member');covered.add(n);require(sha(F/n)==h,'checksum '+n)
 require(covered==set(public)-{'SHA256SUMS.txt'},'checksum coverage')
 replay='UNRUN: original capture cache not supplied; no original artifact or experiment authentication'
 if args.source_cache:
  for m in prov['saved_acquisition_files']:
   require(Path(m['filename']).name==m['filename'],'safe cache filename');f=args.source_cache/m['filename'];require(f.stat().st_size==m['bytes'] and sha(f)==m['sha256'],'capture identity '+f.name)
  primary=representation(args.source_cache/'S02.json');page=representation(args.source_cache/'S03.json');text=norm(primary['markdown'])
  require(primary['metadata']['statusCode']==200 and primary['metadata']['numPages']==primary['metadata']['totalPages']==11,'11 main-document pages')
  for anchor in a['selected_source_anchors']:require(norm(anchor) in text,'selected source anchor '+anchor)
  meta=page['metadata'];require(meta['citation_doi']==a['source']['doi'] and meta['DC.Date']=='2026-08-07' and meta['citation_date']=='2026-08-07','canonical DOI/date')
  require('has not been certified by peer review' in page['markdown'] and 'CC-BY 4.0' in page['markdown'],'preprint status/rights')
  require(any('supplementary-material' in str(x) for x in page.get('links',[])) or 'supplementary-material' in page['markdown'],'named uninspected supplement path')
  replay='PASS: saved capture identities and selected reported source anchors only; no experiment, fitting, original PDF or sequence replay'
 result={'status':'PASS','source_replay':replay,'study_nulls':26,'planning_nulls':18,'matched_panels_admitted':0,'source_data_reanalysed':False,'supporting_information_inspected':False,'external_qualified_review':False};print(json.dumps(result,indent=2))
if __name__=='__main__':main()
