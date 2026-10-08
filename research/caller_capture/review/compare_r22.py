"""Compare frozen blind exact predictions to a supplied engine, read-only."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,required=True)
    p.add_argument('--oracle',type=Path,required=True)
    p.add_argument('--selection',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--marginal-n-cap',type=int,choices=(3,4),required=True)
    p.add_argument('--guard-only',action='store_true')
    args=p.parse_args();start=time.monotonic()
    spec=importlib.util.spec_from_file_location('r22_candidate_under_review',args.engine)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    checks={'full_law_scalar_comparisons':0,'sharp_bound_comparisons':0,'witness_marginal_checks':0,'witness_nonnegative_weights':0,'witness_objective_checks':0,'invalid_input_guards':0}
    results=[]
    def check(ok,category,case):
        if not ok:raise RuntimeError('Mismatch '+category+' at '+case)
        checks[category]+=1
    def refused(call):
        try:call()
        except (ValueError,TypeError):return True
        return False
    guards=[('n_bool',lambda:m.caller_summary(True,{0:1},(),(),1,0)),('n9',lambda:m.caller_summary(9,{0:1},(),(),1,0)),
      ('empty_law',lambda:m.caller_summary(1,{},(0,),(),1,0)),('unnormalized_law',lambda:m.caller_summary(1,{0:F(1,2)},(0,),(),1,0)),
      ('negative_law',lambda:m.caller_summary(1,{0:-1,1:2},(0,),(),1,0)),('bool_weight',lambda:m.caller_summary(1,{0:True},(0,),(),1,0)),
      ('float_weight',lambda:m.caller_summary(1,{0:1.0},(0,),(),1,0)),('bool_mask',lambda:m.caller_summary(1,{True:1},(0,),(),1,0)),
      ('out_mask',lambda:m.caller_summary(1,{2:1},(0,),(),1,0)),('weight_cap',lambda:m.caller_summary(1,{0:F(1,2**40),1:1-F(1,2**40)},(0,),(),1,0)),
      ('unknown_S',lambda:m.caller_summary(1,{1:1},None,(),1,0)),('unknown_R',lambda:m.caller_summary(1,{1:1},(0,),None,1,0)),
      ('overlap',lambda:m.caller_summary(1,{1:1},(0,),(0,),1,1)),('duplicate_S',lambda:m.caller_summary(1,{1:1},(0,0),(),1,0)),
      ('duplicate_R',lambda:m.caller_summary(2,{3:1},(0,),(1,1),1,1)),('outside_S',lambda:m.caller_summary(1,{1:1},(1,),(),1,0)),
      ('outside_R',lambda:m.caller_summary(1,{1:1},(),(1,),1,0)),('bool_index',lambda:m.caller_summary(1,{1:1},(True,),(),1,0)),
      ('k_zero',lambda:m.caller_summary(1,{1:1},(0,),(),0,0)),('k_negative',lambda:m.caller_summary(1,{1:1},(0,),(),-1,0)),
      ('k_bool',lambda:m.caller_summary(1,{1:1},(0,),(),True,0)),('k_fraction',lambda:m.caller_summary(1,{1:1},(0,),(),F(1),0)),
      ('k10',lambda:m.caller_summary(1,{1:1},(0,),(),10,0)),('r_negative',lambda:m.caller_summary(1,{1:1},(0,),(),1,-1)),
      ('r_bool',lambda:m.caller_summary(1,{1:1},(0,),(),1,False)),('r_fraction',lambda:m.caller_summary(1,{1:1},(0,),(),1,F(0))),
      ('r10',lambda:m.caller_summary(1,{1:1},(0,),(),1,10)),('unknown_ancestry',lambda:m.caller_summary(1,{1:1},(0,),(),1,0,ancestry_known=False)),
      ('null_ancestry',lambda:m.caller_summary(1,{1:1},(0,),(),1,0,ancestry_known=None)),
      ('marginal_float',lambda:m.marginal_bounds((0.5,),(0,),(),1,0)),('marginal_bool',lambda:m.marginal_bounds((True,),(0,),(),1,0)),
      ('marginal_negative',lambda:m.marginal_bounds((-1,),(0,),(),1,0)),('marginal_above_one',lambda:m.marginal_bounds((2,),(0,),(),1,0)),
      ('marginal_dimension',lambda:m.marginal_bounds((F(1,2),)*(args.marginal_n_cap+1),(0,),(),1,0)),
      ('marginal_missing',lambda:m.marginal_bounds(None,(0,),(),1,0)),('marginal_overlap',lambda:m.marginal_bounds((F(1,2),),(0,),(0,),1,1)),
      ('marginal_unknown_ancestry',lambda:m.marginal_bounds((F(1,2),),(0,),(),1,0,ancestry_known=False))]
    for name,call in guards:check(refused(call),'invalid_input_guards',name)
    full_cases=bound_cases=skipped=0
    if not args.guard_only:
        oracle=json.loads(args.oracle.read_text());selection=json.loads(args.selection.read_text())
        for c in oracle['full_law_cases']:
            law={int(mask):F(value) for mask,value in c['law'].items()}
            got=m.caller_summary(c['n'],law,tuple(c['carriers']),tuple(c['references']),c['k'],c['r'])
            e=c['expected'];name=c['id']
            check(tuple(got['descendant_call_marginals'])==tuple(map(F,e['descendant_call_marginals'])),'full_law_scalar_comparisons',name)
            for key in ['inclusion_probability','expected_carrier_call_copies','expected_reference_calls']:
                check(type(got[key]) in (int,F) and got[key]==F(e[key]),'full_law_scalar_comparisons',name+':'+key)
            check(tuple(sorted(got['successful_masks']))==tuple(e['successful_masks']),'full_law_scalar_comparisons',name+':support')
            check(got['structural_zero'] is e['structural_zero'],'full_law_scalar_comparisons',name+':structural')
            full_cases+=1
        selected=set(selection['marginal_case_ids'])
        for c in oracle['marginal_bound_cases']:
            if c['id'] not in selected:continue
            if c['n']>args.marginal_n_cap:skipped+=1;continue
            probs=tuple(map(F,c['marginals']));name=c['id'];t0=time.monotonic()
            got=m.marginal_bounds(probs,tuple(c['carriers']),tuple(c['references']),c['k'],c['r'])
            for endpoint in ['lower','upper']:
                check(type(got[endpoint]) in (int,F) and got[endpoint]==F(c[endpoint]['value']),'sharp_bound_comparisons',name+':'+endpoint)
                law=got[endpoint+'_law']
                check(sum(law.values())==1,'witness_marginal_checks',name+':normalization')
                for mask,value in law.items():
                    check(type(mask) is int and 0<=mask<2**c['n'] and type(value) in (int,F) and value>=0,'witness_nonnegative_weights',name)
                for j,prob in enumerate(probs):check(sum(w for mask,w in law.items() if mask&(1<<j))==prob,'witness_marginal_checks',name)
                def included(mask):
                    return sum(int(bool(mask&(1<<j))) for j in c['carriers'])>=c['k'] and sum(int(bool(mask&(1<<j))) for j in c['references'])>=c['r']
                value=sum(w for mask,w in law.items() if included(mask))
                check(value==got[endpoint],'witness_objective_checks',name)
            check(type(got['value_if_independent']) in (int,F) and got['value_if_independent']==F(c['value_if_independent']),'sharp_bound_comparisons',name+':independent')
            bound_cases+=1;results.append({'id':name,'elapsed_seconds':round(time.monotonic()-t0,6)})
            if bound_cases%64==0:print(json.dumps({'marginal_cases_compared':bound_cases,'elapsed_seconds':round(time.monotonic()-start,3)}),flush=True)
    receipt={'status':'passed_independent_blind_comparison','engine_sha256':hashlib.sha256(args.engine.read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256(args.oracle.read_bytes()).hexdigest(),'selection_sha256':hashlib.sha256(args.selection.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'total_checks':sum(checks.values()),'full_law_cases':full_cases,'marginal_cases':bound_cases,'prespecified_4bit_cases_refused_by_declared_domain':skipped,'declared_marginal_n_cap':args.marginal_n_cap,'guard_only':args.guard_only,'elapsed_seconds':round(time.monotonic()-start,6),'per_marginal_case_times':results,'network_requests':0,'qualified_external_review':False}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='per_marginal_case_times'},sort_keys=True))

if __name__=='__main__':main()
