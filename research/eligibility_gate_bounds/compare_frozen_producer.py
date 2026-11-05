#!/usr/bin/env python3
"""Compare a hash-frozen eligibility producer against independent formulas."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
from gate_oracle import beta

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROUTES=('W','A','M')
ARMS=('baseline','selected')


def polygon_extrema(u):
    if min(u)<=0 or sum(u)<1:
        return None
    points=set()
    for i,j in combinations(range(3),2):
        k=3-i-j
        for x,y in product((F(0),u[i]),(F(0),u[j])):
            p=[F(0)]*3
            p[i],p[j],p[k]=x,y,1-x-y
            if all(0<=p[t]<=u[t] for t in range(3)):
                points.add(tuple(p))
    for a in (F(0),u[1]):
        p=((1-a)/2,a,(1-a)/2)
        if all(0<=p[t]<=u[t] for t in range(3)):
            points.add(p)
    za=sorted(p for p in points if p[1]==0)
    if len(za)>1:
        points.add(tuple((za[0][t]+za[-1][t])/2 for t in range(3)))
    vals=[a*a/(w*m) for w,a,m in points if w*m>0]
    unbounded=any(a>0 and w*m==0 for w,a,m in points)
    assert vals
    return min(vals),None if unbounded else max(vals)


def unpack(result):
    return (F(result['lower']['exact']),
            None if result['upper']['exact'] is None else F(result['upper']['exact']))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--producer',type=Path,required=True)
    ap.add_argument('--expected-sha256',required=True)
    ap.add_argument('--repository',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=HERE/'PRODUCER_COMPARISON_RECEIPT.json')
    args=ap.parse_args()
    digest=hashlib.sha256(args.producer.read_bytes()).hexdigest()
    if digest!=args.expected_sha256:
        raise ValueError('Producer source hash mismatch before import')
    spec=importlib.util.spec_from_file_location('frozen_eligibility_producer',args.producer)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    engine,cp=mod.load_engine(args.repository)
    gate_cases=cap_cases=endpoint_cases=0
    for g,f in product([F(i,24) for i in range(25)],repeat=2):
        result=mod.gate_bound(engine,g,f)
        expected=beta(g,f)
        assert F(result['eligible_fraction_lower_exact'])==expected
        assert result['sharpness_scope']=='gate_marginals_only'
        w={key:F(value) for key,value in result['closed_model_witness'].items()}
        assert w['T']==expected and w['a']*w['T']+w['f']*(1-w['T'])==w['g']==g
        assert 0<=w['a']<=1 and 0<=w['f']<=f
        gate_cases+=1
    for upper,lower,b in product(product((F(0),F(1,3),F(1)),repeat=3),
                                  product((F(0),F(1,2),F(1)),repeat=3),
                                  (F(0),F(1,10),F(1,2),F(1))):
        expected=tuple(min(F(1),upper[i]/(b*lower[i])) if b*lower[i] else F(1)
                       for i in range(3))
        actual=mod.eligibility_caps(engine,dict(zip(ROUTES,upper)),dict(zip(ROUTES,lower)),b)
        assert tuple(actual[r] for r in ROUTES)==expected
        cap_cases+=1
    cached={}
    fixtures=[]
    for path in sorted(args.producer.parent.glob('example_*.json')):
        if path.name.endswith('_result.json'):
            continue
        raw=path.read_bytes()
        doc=json.loads(raw)
        if doc['mode']=='gate':
            result=mod.population_gate_bounds(engine,doc)
            assert F(result['eligibility']['eligible_fraction_lower_exact'])==beta(F(doc['gate_positive_lower']),F(doc['other_false_gate_upper']))
        else:
            result=mod.count_bounds(engine,cp,doc)
            tail=F(doc['alpha'])/(16*len(doc['contexts']))
            assert result['confidence']['one_sided_allocations']==16*len(doc['contexts'])
            assert F(result['confidence']['per_endpoint_error_exact'])==tail
            work=0
            for row,out in zip(doc['contexts'],result['contexts']):
                for arm in ARMS:
                    item,found=row[arm],out[arm]
                    n=sum(item['observed_counts'].values())
                    work+=3*n
                    wanted=[]
                    upper,lower=[],[]
                    for r in ROUTES:
                        ctr=item['known_truth_controls'][r]
                        wanted.extend([(item['observed_counts'][r],n,'upper',found['marginal_limits'][r]['observed_upper']),
                                       (ctr['correct'],ctr['introduced'],'lower',found['marginal_limits'][r]['correct_call_lower'])])
                        work+=ctr['introduced']
                    gate,other=item['gate_counts'],item['known_Other_controls']
                    work+=gate['tested']+other['tested']
                    wanted.extend([(gate['positive'],gate['tested'],'lower',found['gate_limits']['gate_positive_lower']),
                                   (other['positive'],other['tested'],'upper',found['gate_limits']['other_false_gate_upper'])])
                    values=[]
                    for k,nt,direction,reported in wanted:
                        key=(k,nt,tail)
                        if key not in cached:
                            cached[key]=cp.clopper_pearson(k,nt,tail)
                        expected=F(cached[key][direction])
                        assert F(reported['exact'])==expected
                        values.append(expected)
                        endpoint_cases+=1
                    gl,fu=values[-2:]
                    b=beta(gl,fu)
                    assert F(found['eligibility']['eligible_fraction_lower_exact'])==b
                    caps=tuple(min(F(1),values[2*i]/(b*values[2*i+1])) if b*values[2*i+1] else F(1)
                               for i in range(3))
                    assert tuple(F(found['caps'][r]) for r in ROUTES)==caps
                    expected=polygon_extrema(caps)
                    assert (found['status']=='ok')==(expected is not None)
                    if expected is not None:
                        assert unpack(found)==expected
                    assert 'conservative' in found['range_kind']
            assert result['confidence']['CP_trial_work']==work
            assert result['reject_common_J']==(len(doc['contexts'])>=2 and result['common_J']['separated'])
        assert result['joint_gate_classifier_sharpness_claimed'] is False
        result['input_sha256']=hashlib.sha256(raw).hexdigest()
        saved=path.with_name(path.stem+'_result.json')
        assert saved.exists(),saved
        assert result==json.loads(saved.read_text())
        fixtures.append({'input':path.name,'input_sha256':hashlib.sha256(raw).hexdigest(),
                         'saved_result_matches':True,'reject_common_J':result.get('reject_common_J')})
    assert fixtures
    receipt={'all_checks_passed':True,'producer_sha256':digest,
             'gate_marginal_cases':gate_cases,'eligibility_cap_cases':cap_cases,
             'one_sided_count_endpoints_compared':endpoint_cases,'fixtures':fixtures,
             'scope':'Frozen producer compared with independent gate/cap arithmetic and polygon extrema. CP endpoints intentionally reuse the separately audited, preserved scalar engine.'}
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
