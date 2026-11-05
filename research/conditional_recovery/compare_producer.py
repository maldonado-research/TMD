#!/usr/bin/env python3
"""Compare proposed producer to independent fibers; no repository writes."""
from copy import deepcopy
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from independent_recovery_oracle import make_fibers, reference_prob, robust_prob, assert_superuniform


def document(table, interval=('1/3','5/2'), gamma='1/97'):
    k1,x1,k2,x2=table
    return {
        'observation_contract':'shared_biological_curvature_with_differential_recovery',
        'sampling_contract':'independent_baseline_selected_multinomials',
        'recovery_bound_contract':'externally_justified_coverage_interval',
        'differential_tilt_interval':list(interval),
        'bound_noncoverage_probability':gamma,
        'alpha':'1/20',
        'contexts':[{'id':'first','baseline':list(k1),'selected':list(x1)},
                    {'id':'second','baseline':list(k2),'selected':list(x2)}],
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer',type=Path,default=HERE/'recovery_sensitivity.py')
    parser.add_argument('--engine-dir',type=Path,default=HERE.parent/'conditional_curvature')
    parser.add_argument('--output',type=Path,default=HERE/'producer_comparison_receipt.json')
    args=parser.parse_args()
    sys.path.insert(0,str(args.engine_dir.resolve()))
    spec=importlib.util.spec_from_file_location('reviewed_recovery_sensitivity',args.producer)
    producer=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    initial_hash=hashlib.sha256(args.producer.read_bytes()).hexdigest()
    fibers=make_fibers()
    comparisons=0
    interval=(F(1,3),F(5,2))
    for rows in fibers.values():
        h=[r[1] for r in rows]
        for j,row in enumerate(rows):
            result=producer.recovery_sensitivity_test(document(row[2]),include_fiber=True)
            assert [int(v['reference_weight_exact']) for v in result['fiber']] == h
            assert result['observed_index'] == j
            assert F(result['reference_p_exact']) == reference_prob(h,j,F(1))
            expected=robust_prob(h,j,interval)
            assert F(result['robust_p_exact']) == expected
            adjusted=min(F(1),expected+F(1,97))
            assert F(result['adjusted_p_exact']) == adjusted
            assert result['reject'] == (adjusted <= F(1,20))
            comparisons+=1
    malformed=[]
    base=document(((0,4,0),(2,0,2),(2,0,2),(0,4,0)))
    bads=[('false_count',('contexts',0,'baseline',0),True),
          ('float_count',('contexts',0,'baseline',0),0.0),
          ('negative_count',('contexts',0,'baseline',0),-1),
          ('over_budget',('contexts',0,'baseline',0),201),
          ('gamma_bool',('bound_noncoverage_probability',),False),
          ('gamma_negative',('bound_noncoverage_probability',),'-1/10'),
          ('gamma_one',('bound_noncoverage_probability',),'1'),
          ('gamma_float',('bound_noncoverage_probability',),0.01),
          ('interval_zero',('differential_tilt_interval',),['0','1']),
          ('interval_negative',('differential_tilt_interval',),['-1','1']),
          ('interval_reversed',('differential_tilt_interval',),['2','1']),
          ('interval_float',('differential_tilt_interval',),[0.5,1]),
          ('interval_bool',('differential_tilt_interval',),[True,1]),
          ('interval_oversized',('differential_tilt_interval',),[1,str(2**300)]),
          ('duplicate_id',('contexts',1,'id'),'first'),
          ('wrong_contract',('recovery_bound_contract',),'independently_estimated'),
          ('alpha_one',('alpha',),'1'),
          ('alpha_zero',('alpha',),'0')]
    for name,path,value in bads:
        doc=deepcopy(base)
        target=doc
        for component in path[:-1]:
            target=target[component]
        target[path[-1]]=value
        try:
            producer.recovery_sensitivity_test(doc)
        except ValueError:
            malformed.append(name)
        else:
            raise AssertionError(name)
    for name,call_args in [
        ('disconnected_complement',([2,1,2],1,F(1,2),F(2))),
        ('boolean_observed',([1,2],True,F(1),F(2))),
        ('negative_weight',([1,-1],0,F(1),F(2))),
        ('boolean_weight',([1,True],0,F(1),F(2))),
        ('float_weight',([1,1.0],0,F(1),F(2))),
    ]:
        try:
            producer.certified_reference_supremum(*call_args)
        except ValueError:
            malformed.append(name)
        else:
            raise AssertionError(name)

    # A deliberately outcome-dependent interval has valid marginal coverage.
    # True t=1; exclude it only when the rare state J=1 is observed.
    h=(24,1)
    gamma=F(1,25)
    true_probs=(F(24,25),F(1,25))
    intervals=((F(1),F(1)),(F(1,100),F(1,100)))
    raw=[robust_prob(h,j,v) for j,v in enumerate(intervals)]
    adj=[min(F(1),p+gamma) for p in raw]
    assert raw == [F(1),F(1,2401)]
    assert F(1,25)>F(1,100)
    assert_superuniform(adj,true_probs)
    assert sum(p for value,p in zip(raw,true_probs) if value <= F(1,100)) == F(1,25)
    assert sum(p for value,p in zip(adj,true_probs) if value <= F(1,100)) == 0

    source=Path(producer.__file__)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == initial_hash, 'Producer changed during comparison'
    receipt={'status':'pass','producer_filename':source.name,
        'producer_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'all_table_api_comparisons':comparisons,'malformed_inputs_rejected':malformed,
        'dependent_interval_stress_test':{
            'weights':h,'true_t':'1','interval_for_J0':['1','1'],
            'interval_for_J1':['1/100','1/100'],'marginal_noncoverage':str(gamma),
            'raw_pvalues':list(map(str,raw)),'adjusted_pvalues':list(map(str,adj)),
            'alpha':'1/100','raw_rejection_probability':'1/25','adjusted_rejection_probability':'0',
            'all_adjusted_attainable_thresholds_valid':True},
        'scope':'Synthetic computational review. Mathematical validity remains conditional on the declared count and coverage contracts.'}
    args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
