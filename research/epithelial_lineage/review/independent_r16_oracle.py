"""Read-only independent primary identity, pedigree attrition and software oracle."""
from pathlib import Path
from fractions import Fraction as F
import argparse, hashlib, importlib.util, json, xml.etree.ElementTree as E

def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not __debug__:raise SystemExit('Independent assertions must be enabled')
    engine=a.package/'audit_epithelial_lineage.py';engine_hash=hashlib.sha256(engine.read_bytes()).hexdigest();assert engine_hash=='870ad4495ed35e559d4eb58e361fadac6153a52ea9465e9ec56a51fe9a404ea7'
    spec=importlib.util.spec_from_file_location('source_producer',engine);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    ledger=json.loads((a.package/'SOURCES.json').read_text());source=ledger['primary_source'];checks={'primary':0,'source_stage':0,'nested_flow_cases':0,'software':0,'candidate_metadata':0}
    def check(test,category):
        if not test:raise AssertionError('Independent check failed: '+category)
        checks[category]+=1
    raw=(a.cache/'PMC6280753.xml').read_bytes();check(hashlib.sha256(raw).hexdigest()=='ce8c2399de162f9ce6586a13fcc6024f5ca818d723a9fd98390b1e1b22e84ae5','primary');check(len(raw)==243460,'primary');tree=E.fromstring(raw)
    normalize=lambda e:' '.join(''.join(e.itertext()).split())
    for kind,value in [('doi','10.1101/gr.238543.118'),('pmid','30459213'),('pmcid','PMC6280753')]:
        check(tree.find('.//front//article-id[@pub-id-type="'+kind+'"]').text==value,'primary')
    check('creativecommons.org/licenses/by/4.0/' in normalize(tree.find('.//front//permissions')),'primary')
    paras=[normalize(e) for e in tree.findall('.//body//p')];check(len(paras)==80,'primary')
    for anchor in source['anchors']:
        check(hashlib.sha256(paras[anchor['body_paragraph_index']].encode()).hexdigest()==anchor['normalized_paragraph_sha256'],'primary')
    for phrase in ['isolated 37 cells (out of 45 cells in the channel), of which 11 grew','isolated 22 single cells (out of 26 cells in the channel), of which 15 grew','Thirteen of these subclonal cultures were processed for sequencing']:
        check(phrase in paras[47],'source_stage')
    for text_index,phrase in [(6,'a single founding cell'),(33,'potential for bias'),(35,'overdispersed relative to a Poisson process'),(42,'DMEM/F12'),(50,'predominantly triploid'),(65,'lack of a sufficiently accurate independent validation method'),(70,'independent Poisson distributions'),(78,'SRP159787')]:
        check(phrase in paras[text_index],'primary')
    cases=0
    for total in range(1,9):
        for isolated in range(total+1):
            for grown in range(isolated+1):
                for sequenced in range(grown+1):
                    result=m.stage_flow(total,isolated,grown,sequenced);cases+=1
                    quotients=[('realized_fraction_isolated_given_available',isolated,total),('realized_fraction_outgrown_given_isolated',grown,isolated),('realized_fraction_sequenced_given_outgrown',sequenced,grown),('realized_fraction_sequenced_given_available',sequenced,total)]
                    for key,num,den in quotients:
                        value=result[key]
                        if den==0:check(value is None,'nested_flow_cases')
                        else:
                            frac=F(value);check(frac.numerator*den==num*frac.denominator,'nested_flow_cases')
                    check((result['not_isolated_count'],result['isolated_without_outgrowth_count'],result['outgrown_not_sequenced_count'])==(total-isolated,isolated-grown,grown-sequenced),'nested_flow_cases')
                    check(result['available_denominator_is_not_all_cells_ever_born'] is True,'nested_flow_cases')
                    check(result['independent_capture_probability_or_interval_estimated'] is False,'nested_flow_cases')
    for name,nums,expected in [('HT115',(45,37,11,11),F(11,45)),('RPE1',(26,22,15,13),F(1,2))]:
        result=m.stage_flow(*nums);check(F(result['realized_fraction_sequenced_given_available'])==expected,'source_stage')
        check(sum(result[k] for k in ['not_isolated_count','isolated_without_outgrowth_count','outgrown_not_sequenced_count','sequenced_subclones'])==nums[0],'source_stage')
    software=ledger['pinned_software_identity'];commits=json.loads((a.cache/'pipeline_commit.json').read_text());check(type(commits) is list and len(commits)==1,'software');commit=commits[0];check(commit['sha']=='bcfe5a6c1a1407306b1c8b82e423de124e7a9f9e','software')
    nodes=json.loads((a.cache/'pipeline_tree.json').read_text());check(not nodes['truncated'] and len(nodes['tree'])==6,'software');check(all(n['type']=='blob' and n['mode']=='100644' for n in nodes['tree']),'software')
    data=b''.join(n['mode'].encode()+b' '+n['path'].encode()+b'\0'+bytes.fromhex(n['sha']) for n in sorted(nodes['tree'],key=lambda n:n['path'].encode()))
    object_sha=hashlib.sha1(b'tree '+str(len(data)).encode()+b'\0'+data).hexdigest();check(object_sha==commit['commit']['tree']['sha']==software['tree_sha'],'software')
    readme=(a.cache/'pipeline_README.md').read_bytes();check(len(readme)==2959,'software');blob=hashlib.sha1(b'blob '+str(len(readme)).encode()+b'\0'+readme).hexdigest();check(blob=='cf76c4e3c358130808ccda49e93b3610f0eba5fe','software')
    check(blob==next(n['sha'] for n in nodes['tree'] if n['path']=='README.md'),'software');check('Python 2.7' in readme.decode(),'software');check(not any(n['path'].lower().startswith('license') for n in nodes['tree']),'software')
    # The API's tree.sha field is deliberately not treated as the object identity.
    for field,filename in [('commit_response_sha256','pipeline_commit.json'),('tree_response_sha256','pipeline_tree.json'),('readme_sha256','pipeline_README.md')]:check(hashlib.sha256((a.cache/filename).read_bytes()).hexdigest()==software[field],'software')
    pubmed=E.parse(a.cache/'pubmed_candidates.xml').getroot();ids={x.find('.//MedlineCitation/PMID').text for x in pubmed.findall('PubmedArticle')};check(len(ids)==12,'candidate_metadata')
    check(ids=={x['pmid'] for x in ledger['candidate_screen']},'candidate_metadata');check(len(ledger['candidate_screen'])==12 and ledger['total_index_hits_reported']==18,'candidate_metadata')
    result={'status':'PASS_INDEPENDENT_R16_SOURCE_AND_STAGE_REVIEW','engine_sha256':engine_hash,'enumerated_nested_stage_cases':cases,'checks':checks,'check_total':sum(checks.values()),'software_tree_reconstructed_sha1':object_sha,'primary_source_body_paragraphs':80,'primary_claim_inspection':'Root read the complete selected primary paragraphs7,21,34–36,43,48,51,66–68,71–73,79; reviewed identities and20anchors. Producer reports full80paragraph inspection; hashes alone do not verify interpretation.','biological_scope':'Two displayed pedigrees,24related sequenced subclones, non-isogenic HT115/RPE1; nested realized recovery fractions are not independently calibrated route probabilities or new mutation-birth denominators.','licenses':'Article CC BY4.0 verified; pinned software lacks LICENSE, no code/archive reuse right inferred. No full primary bodies, reads, variants or notebooks published.'}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['primary_claim_inspection','biological_scope','licenses']}))

if __name__=='__main__':main()
