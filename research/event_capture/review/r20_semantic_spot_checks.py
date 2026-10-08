"""Read-only exact semantic spot checks; no biological inference or network."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import hashlib
import json

BASE=Path('/workspace/tmd-research-progress/r20_event_capture_2026-10-07/public_candidate')
OUT=Path('/workspace/tmd-research-progress/r19_r20_review_2026-10-07')
spec=importlib.util.spec_from_file_location('r20_semantic_spot_engine',BASE/'event_capture.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
checks=[]
def check(name,condition):
    if not condition: raise RuntimeError('Failed semantic spot check: '+name)
    checks.append(name)
def refused(call):
    try: call()
    except (TypeError,ValueError): return True
    return False

ind={0:F(1,4),1:F(1,4),2:F(1,4),3:F(1,4)}
a=m.event_summary(2,ind,{'one_origin':(0,1)})
check('OR_one_carrier_call_probability_three_quarters',a['event_inclusion']['one_origin']==F(3,4))
two_support=sum((w for mask,w in ind.items() if (mask&1) and (mask&2)),F())
check('simplified_two_carrier_support_probability_one_quarter',two_support==F(1,4))
check('OR_does_not_replay_two_support_component',a['event_inclusion']['one_origin']!=two_support)
check('two_descendant_expected_inherited_copies_one',a['expected_observed_carrier_copy_count']==1)
for label,law,pi,var in [('common',{0:F(1,2),3:F(1,2)},F(1,2),F(4)),('exclusive',{1:F(1,2),2:F(1,2)},F(1),F()),('independent',ind,F(3,4),F(2))]:
    s=m.event_summary(2,law,{'one_origin':(0,1)})
    h=m.ht_summary(2,law,{'first_origin':(0,),'second_origin':(1,)})
    check(label+'_same_marginals',s['descendant_call_marginals']==(F(1,2),F(1,2)))
    check(label+'_event_union',s['event_inclusion']['one_origin']==pi)
    check(label+'_two_distinct_origins_variance',h['design_variance']==var)

law3={mask:F(1,8) for mask in range(8)}
overlap=m.ht_summary(3,law3,{'a':(0,1),'b':(1,2)})
check('overlap_joint_probability_five_eighths',overlap['joint_event_inclusion']['a','b']==F(5,8))
check('overlap_event_covariance_one_sixteenth',overlap['joint_event_inclusion']['a','b']-overlap['event_inclusion']['a']*overlap['event_inclusion']['b']==F(1,16))
check('overlap_HT_variance_eight_ninths',overlap['design_variance']==F(8,9))
noninteger=m.ht_value(1,{0:F(1,3),1:F(2,3)},{'origin':(0,)},1)
check('HT_sample_total_can_be_noninteger',noninteger==F(3,2))
check('known_empty_carrier_inclusion_zero',m.event_summary(1,{1:1},{'known_extinct':()})['event_inclusion']['known_extinct']==0)
check('known_zero_inclusion_full_catalogue_total_refused',refused(lambda:m.ht_summary(1,{1:1},{'known_extinct':()})))
check('unknown_carriers_not_accepted_as_known_empty',refused(lambda:m.event_summary(1,{1:1},{'unknown':None})))
check('known_empty_catalogue_total_zero',m.ht_summary(0,{0:1},{})['design_expectation']==0)

route_events={'r1':(0,),'r2':(1,2),'r3':(3,)}
route_law={mask:F(1,16) for mask in range(16)}
r=m.event_summary(4,route_law,route_events)
means=r['event_inclusion']
shares={key:value/sum(means.values()) for key,value in means.items()}
check('normalized_expected_event_count_shares',shares=={'r1':F(2,7),'r2':F(3,7),'r3':F(2,7)})
check('raw_expected_count_curvature_nine_quarters',shares['r2']**2/(shares['r1']*shares['r3'])==F(9,4))
# Independent calculation of the different target E[realized shares | D>0].
weighted={key:F() for key in route_events}; nonempty=F()
for mask,weight in route_law.items():
    inclusion={key:bool(mask&sum(1<<j for j in carriers)) for key,carriers in route_events.items()}
    total=sum(inclusion.values())
    if total:
        nonempty+=weight
        for key,value in inclusion.items(): weighted[key]+=weight*F(int(value),total)
realized={key:value/nonempty for key,value in weighted.items()}
check('conditional_realized_share_target_differs',realized=={'r1':F(4,15),'r2':F(7,15),'r3':F(4,15)} and realized!=shares)
check('engine_output_cannot_authenticate_supplied_catalogue',a['ancestry_and_catalogue_supplied_not_authenticated'] is True)
check('HT_output_does_not_claim_mutation_process_identification',overlap['biological_catalogue_or_mutation_process_identified'] is False)
check('direct_catalogue_helper_nine_descendants_refused',refused(lambda:m.event_catalogue(9,{'e':(8,)},True)))
check('direct_catalogue_helper_boolean_n_refused',refused(lambda:m.event_catalogue(True,{'e':(0,)},True)))

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x
receipt={'status':'passed_read_only_semantic_spot_checks','engine_sha256':hashlib.sha256((BASE/'event_capture.py').read_bytes()).hexdigest(),'checks':checks,'check_count':len(checks),'target_contrast':{'normalized_expected_counts':shares,'conditional_mean_realized_shares_given_nonempty':realized},'assay_component_contrast':{'OR_one_or_more_true_calls':F(3,4),'at_least_two_true_carrier_calls':two_support,'actual_native_caller_replayed':False},'source_requests':0,'qualified_external_review':False,'biological_inference':False}
(OUT/'R20_SEMANTIC_SPOT_CHECK_RECEIPT.json').write_text(json.dumps(encode(receipt),indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':receipt['status'],'check_count':len(checks),'engine_sha256':receipt['engine_sha256']}))
