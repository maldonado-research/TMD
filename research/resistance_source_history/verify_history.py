"""Original bounded structural diagnostics; no author code is executed."""
import argparse,collections,csv,hashlib,itertools,json
from pathlib import Path
A=argparse.ArgumentParser(description=__doc__)
A.add_argument('original_cache',type=Path)
A.add_argument('history_cache',type=Path)
A.add_argument('--output',type=Path)
args=A.parse_args()
S=args.original_cache; P=args.history_cache
for r in json.loads((Path(__file__).resolve().parent/'evidence_receipt.json').read_text()):
 cache=S if r['cache']=='original' else P
 assert hashlib.sha256((cache/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
# Verify source cache identity and pinned static scripts against Git tree.
tree={r['path']:r for r in json.loads((S/'tree.json').read_text())['tree']}
for name in ['model-fitting.R','plots.R','run-R-code.sh']:
 b=(P/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==tree[name]['sha']
W={f'{r}{c}' for r in 'BCDEFGHIJK' for c in range(2,8)}
raw={}; counts={};agg={};freq={}
for kind in ['none','single','double']:
 with (S/f'1ul_individual_{kind}.csv').open(newline='') as f: rows=list(csv.reader(f))
 for i,v in enumerate(rows[1:],2):
  r=dict(zip(rows[0],v));tr={'none':'none','double':'rifampicin+nalidixic acid'}.get(kind,r.get('antibiotic'))
  k=(tr,r['volume'],r['day'],r['pmutS'],r['medium']);s=r['wells']
  toks=s.lstrip('-').split(';') if s not in ['ALL','0'] else []
  valid=len(v)==len(rows[0]) and not(set(toks)-W) and len(toks)==len(set(toks))
  counts[k]=None if not valid else 60 if s=='ALL' else 0 if s=='0' else 60-len(toks) if s.startswith('-') else len(toks)
  raw[k]={'file':f'1ul_individual_{kind}.csv','line':i,'wells':s,'row_fields':len(v),'fields':v}
 with (S/f'1ul_aggregate_{kind}.csv').open(newline='') as f:
  reader=csv.DictReader(f);headers=reader.fieldnames[5:]
  assert headers==sorted(headers,key=float)
  for i,r in enumerate(reader,2):
   tr=r['antibiotic'];freq[tr]=headers
   for rank,h in zip(['0','10','25','50'],headers):
    m={'MH':'MH','Nal':'nal','Rif':'rif','Nal + Rif':'nal+rif'}[r['resistance']]
    agg[(tr,r['volume'],r['day'],rank,m)]={'count':None if r[h]=='NA' else int(r[h]),'file':f'1ul_aggregate_{kind}.csv','line':i,'header':h}
diff=[]
for k,n in counts.items():
 a=agg[k]['count']
 if n is not None and a is not None and n!=a:
  diff.append({'key':k,'individual':n,'aggregate':a,'delta':n-a,'raw':raw[k],'aggregate_source':agg[k]})
none=[d for d in diff if d['key'][0]=='none']
assert len(none)==33 and all(d['delta']==1 and d['raw']['wells'].count(';')==d['aggregate'] for d in none)
explicit_none=[k for k,r in raw.items() if k[0]=='none' and r['wells'] not in ['ALL','0']]
assert len(explicit_none)==33 and set(explicit_none)=={tuple(d['key']) for d in none}
perms={};ranks=['0','10','25','50']
for tr in freq:
 res=[]
 for p in itertools.permutations(ranks):
  diffs=[]
  for k,n in counts.items():
   if k[0]!=tr or n is None:continue
   ak=k[:3]+(p[ranks.index(k[3])],)+k[4:];a=agg[ak]['count']
   if a is not None:diffs.append(n-a)
  res.append({'individual_to_aggregate_rank':dict(zip(ranks,p)),'compared':len(diffs),'disagreements':sum(d!=0 for d in diffs),'absolute_difference_sum':sum(abs(d) for d in diffs)})
 perms[tr]=sorted(res,key=lambda r:(r['disagreements'],r['absolute_difference_sum']))
oldrows=list(csv.reader((P/'original_1ul_individual_single.csv').open()))
oldissues=[]
for i,v in enumerate(oldrows[1:],2):
 s=v[-1]; toks=s.lstrip('-').split(';') if s not in ['ALL','0'] else []
 invalid=sorted(set(toks)-W);repeat=sorted(k for k,n in collections.Counter(toks).items() if n>1)
 if len(v)!=len(oldrows[0]) or invalid or repeat:oldissues.append({'line':i,'field_count':len(v),'invalid_tokens':invalid,'repeated_tokens':repeat,'raw':v})
out={'no_drug_delimiter_identity_count':33,'no_drug_explicit_nonempty_list_count':len(explicit_none),'differences':diff,'rank_permutations':perms,'original_2019_strict_parse_issues':oldissues,'limits':'Diagnostic identities and permutations are not a repair, biological reassignment, author-pipeline execution, or publication validation.'}
if args.output: args.output.write_text(json.dumps(out,indent=2)+'\n')
assert len(diff)==54 and len(oldissues)==3
assert sum(v is None for v in counts.values())==2
assert sum(n is not None and agg[k]['count'] is not None for k,n in counts.items())==381
for tr,v in perms.items():
 best=min(r['absolute_difference_sum'] for r in v)
 winners=[r for r in v if r['absolute_difference_sum']==best]
 assert len(winners)==1 and winners[0]['individual_to_aggregate_rank']==dict(zip(ranks,ranks))
oldtree={r['path']:r for r in json.loads((P/'original_tree.json').read_text())['tree']}
elifetree={r['path']:r for r in json.loads((P/'elife_tree.json').read_text())['tree']}
assayfiles=[f'1ul_{k}_{t}.csv' for k in ['aggregate','individual'] for t in ['none','single','double']]
assert all(tree[f]['sha']==elifetree[f]['sha'] for f in assayfiles+['munging.R','plots.R','model-fitting.R'])
assert sum(tree[f]['sha']==oldtree[f]['sha'] for f in assayfiles)==5
b=(P/'original_1ul_individual_single.csv').read_bytes()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==oldtree['1ul_individual_single.csv']['sha']
assert len(json.loads((P/'commits.json').read_text()))==67
assert json.loads((P/'tags.json').read_text())==json.loads((P/'releases.json').read_text())==[]
print(json.dumps({'disagreement_count':len(diff),'current_rejected_assay_records':sum(v is None for v in counts.values()),'none_semicolon_identity':len(none),'remaining_signed_differences':dict(collections.Counter(d['delta'] for d in diff if d['key'][0]!='none')),'rank_permutation_minimum_absolute_difference':{k:min(v,key=lambda r:r['absolute_difference_sum']) for k,v in perms.items()},'old_strict_issues':oldissues},indent=2))
