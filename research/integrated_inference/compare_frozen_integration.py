#!/usr/bin/env python3
"""Independent frozen-wrapper comparison against the three pinned modules."""
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import importlib.util
import json
import sys

PRODUCER_SHA256 = '6bd25d526dc7a95338ab861eb426b36728fc997bf80c3bd45f4c19ce6494e45f'
PINS = {
    'threshold': ('research/threshold_calibration/threshold_calibration.py', '4256ca07cdd4d6e597c4ed2eda28926917e428391aa05710b2f5b962eb616c0b'),
    'eligibility': ('research/eligibility_gate_bounds/eligibility_gate_bounds.py', '5c5645e83b3f38ecfb8e196bb5332a555ef752ffab42d4315b6ce7ebbf5d2f6f'),
    'classification': ('research/classification_bounds/classification_bounds.py', '66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368'),
    'cp': ('research/classification_bounds/sources/boundary_confidence.py', '23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d'),
}


def load(path, name, expected):
    assert sha256(path.read_bytes()).hexdigest() == expected, ('source hash mismatch', path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(None)
def direct_tail(n, k, p, lower):
    """Closed binomial sum; separate from preserved recurrence implementation."""
    a, b = p.numerator, p.denominator
    values = range(k, n+1) if lower else range(k+1)
    return F(sum(comb(n,j)*a**j*(b-a)**(n-j) for j in values), b**n)


def compare(producer_dir, repository):
    sys.dont_write_bytecode = True
    wrapper = load(producer_dir/'integrated_inference.py', 'reviewed_wrapper', PRODUCER_SHA256)
    modules = {name: load(repository/path, 'reviewed_'+name, pin) for name,(path,pin) in PINS.items()}
    engine, cp, threshold, eligibility = (modules[k] for k in ('classification','cp','threshold','eligibility'))
    cases = []
    for name in ('strict_separation','inclusive_all_tied','one_context_no_truth_controls'):
        plan = json.loads((producer_dir/f'example_{name}_plan.json').read_text())
        record = json.loads((producer_dir/f'example_{name}_observations.json').read_text())
        cases.append((name, plan, record, False))
    plan, record = deepcopy(cases[0][1]), deepcopy(cases[0][2])
    plan['calibration_error_share'] = '1/3'
    for i,(p_row,r_row) in enumerate(zip(plan['contexts'],record['contexts'])):
        for j, arm in enumerate(('baseline','selected')):
            fixed, item = p_row[arm], r_row[arm]
            fixed['calibration']['tested'] = 20
            fixed['calibration']['rule'] = 'inclusive_maximum' if (i+j)%2 else 'strict_maximum'
            fixed['future_cohort_tested'] = 30
            fixed['true_route_control_introduced'] = {'W':20,'A':10,'M':0}
            item['calibration_summary'] = {'tested':20,'maximum':'3/7'}
            if fixed['calibration']['rule'] == 'inclusive_maximum':
                item['calibration_summary']['maximum_multiplicity'] = 1
            item['observed_counts'] = {'W':7,'A':10,'M':8,'U':5}
            item['gate_counts'] = {'tested':30,'positive':27}
            item['known_truth_controls'] = {'W':{'introduced':20,'correct':17}, 'A':{'introduced':10,'correct':8}, 'M':{'introduced':0,'correct':0}}
    record['plan_sha256'] = wrapper.canonical_digest(plan)
    cases.append(('independent_mixed_comparators_unequal_control_n',plan,record,True))
    zero_plan, zero_record = deepcopy(plan), deepcopy(record)
    for p_row,r_row in zip(zero_plan['contexts'],zero_record['contexts']):
        for arm in ('baseline','selected'):
            p_row[arm]['future_cohort_tested'] = 0
            r_row[arm]['observed_counts'] = dict.fromkeys(('W','A','M','U'),0)
            r_row[arm]['gate_counts'] = {'tested':0,'positive':0}
    zero_record['plan_sha256'] = wrapper.canonical_digest(zero_plan)
    cases.append(('independent_zero_future_cohort',zero_plan,zero_record,True))
    checks = {'cases':0, 'calibration_module_equalities':0, 'count_endpoint_equalities':0,
              'independent_exact_tail_checks':0, 'gate_module_equalities':0,
              'cap_projection_equalities':0, 'J_and_common_equalities':0}
    details = []
    for name,plan,record,exact_check in cases:
        result = wrapper.infer(engine,cp,threshold,eligibility,plan,record)
        c, alpha, share = len(plan['contexts']),F(plan['alpha']),F(plan['calibration_error_share'])
        gamma, eta = alpha*share/(2*c),alpha*(1-share)/(14*c)
        budget = result['confidence']
        assert F(budget['per_calibration_error_exact'])==gamma
        assert F(budget['per_count_endpoint_error_exact'])==eta
        assert budget['calibration_components']==2*c and budget['count_components']==14*c
        assert F(budget['global_error_bound_exact'])==alpha
        contexts = []
        for planned,raw,actual in zip(plan['contexts'],record['contexts'],result['contexts']):
            expected = {'id':raw['id']}
            for arm in engine.ARMS:
                fixed,item,out = planned[arm],raw[arm],actual[arm]
                calibration = threshold.calibrate(engine,cp,{
                    'rule':fixed['calibration']['rule'], 'provenance':record['provenance'],
                    'contract':fixed['calibration']['contract'], 'gamma':str(gamma),
                    'control_summary':item['calibration_summary']})
                assert out['calibration']==calibration
                checks['calibration_module_equalities'] += 1
                n,k=calibration['numerical_endpoint']['n'],calibration['numerical_endpoint']['equivalent_k']
                fu=F(calibration['control_false_gate_upper_exact'])
                if exact_check:
                    assert fu==1 if k==n else direct_tail(n,k,fu,False)<=gamma
                    checks['independent_exact_tail_checks']+=1
                upper,lower={},{}
                for route in engine.ROUTES:
                    ctl=item['known_truth_controls'][route]
                    for lower_flag,k,n in ((False,item['observed_counts'][route],sum(item['observed_counts'].values())),(True,ctl['correct'],ctl['introduced'])):
                        value,cert=engine.certified_one_sided(cp,k,n,eta,lower_flag)
                        key='correct_call_lower' if lower_flag else 'observed_upper'
                        assert out['marginal_limits'][route][key]==cert
                        checks['count_endpoint_equalities']+=1
                        (lower if lower_flag else upper)[route]=value
                        if exact_check:
                            if not n or (lower_flag and not k) or (not lower_flag and k==n):
                                assert value==(0 if lower_flag else 1)
                            else:
                                assert direct_tail(n,k,value,lower_flag)<=eta
                            checks['independent_exact_tail_checks']+=1
                gate=item['gate_counts']
                gl,gcert=engine.certified_one_sided(cp,gate['positive'],gate['tested'],eta,True)
                assert out['gate_positive_lower']==gcert
                checks['count_endpoint_equalities']+=1
                if exact_check:
                    assert gl==0 if not gate['positive'] else direct_tail(gate['tested'],gate['positive'],gl,True)<=eta
                    checks['independent_exact_tail_checks']+=1
                expected_gate=eligibility.gate_bound(engine,gl,fu)
                assert out['eligibility']==expected_gate
                checks['gate_module_equalities']+=1
                beta=max(F(0),(gl-fu)/(1-fu)) if fu<1 else F(0)
                assert F(expected_gate['eligible_fraction_lower_exact'])==beta
                # Direct ratio arithmetic checks the eligibility multiplication.
                caps={r:min(F(1),upper[r]/(beta*lower[r])) if beta*lower[r] else F(1) for r in engine.ROUTES}
                assert eligibility.eligibility_caps(engine,upper,lower,beta)==caps
                projected=engine.capped_simplex_bounds(caps)
                for key,value in projected.items():
                    if key!='range_kind':
                        assert out[key]==value, (name,key)
                checks['cap_projection_equalities']+=1
                expected[arm]=projected
            expected['J']=engine.ratio_interval(expected['baseline'],expected['selected'])
            assert actual['J']==expected['J']
            checks['J_and_common_equalities']+=1
            contexts.append(expected)
        common=engine.common_intersection([row['J'] for row in contexts])
        for key in ('separated','lower','upper'):
            if key in common:
                assert common[key]==result['common_J'][key]
        assert result['reject_common_J']==(c>=2 and common['separated'])
        checks['J_and_common_equalities']+=1
        assert result['joint_gate_classifier_sharpness_claimed'] is False
        assert result['confidence']['between_component_independence_required'] is False
        assert 'not registration, chronology' in result['hash_scope']
        checks['cases']+=1
        details.append({'case':name,'reject_common_J':result['reject_common_J'],
                        'common_status':result['common_J']['status'], 'gamma':str(gamma),'eta':str(eta)})
    assert details[0]['reject_common_J']
    assert not any(row['reject_common_J'] for row in details[1:])
    return {'status':'passed', 'producer_sha256':PRODUCER_SHA256,
            'comparison_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependencies':{name:pin for name,(_,pin) in PINS.items()},
            'checks':checks,'cases':details,
            'scope':'Frozen producer comparison and independent closed binomial sums; synthetic inputs only; no empirical native validation.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer-dir',type=Path,required=True)
    parser.add_argument('--repository',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    rendered=json.dumps(compare(args.producer_dir,args.repository),indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered,end='')
