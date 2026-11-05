#!/usr/bin/env python3
"""Compare a frozen producer with independently constructed rational oracles."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
from independent_oracle import polygon_extrema, quadrads, triads

PRODUCER_SHA256='66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368'
CP_SHA256='23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d'
HERE=Path(__file__).resolve().parent
ROUTES=('W','A','M')
LABELS=ROUTES+('U',)


def frozen_import(path,name,expected):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=expected:
        raise ValueError(f'Frozen {name} digest mismatch')
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def unpack(result):
    return (F(result['lower']['exact']),
            None if result['upper']['exact'] is None else F(result['upper']['exact']))


def check_matrix(result,o,d,p):
    matrix=[[F(x) for x in row] for row in result['matrix_exact']]
    assert len(matrix)==4 and all(len(row)==3 for row in matrix)
    assert all(min(row)>=0 for row in matrix)
    assert all(sum(matrix[j][i] for j in range(4))==1 for i in range(3))
    assert all(matrix[i][i]>=d[i] for i in range(3))
    assert all(sum(matrix[j][i]*p[i] for i in range(3))==o[j] for j in range(4))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer',type=Path,default=HERE/'classification_bounds.py')
    parser.add_argument('--output',type=Path,default=HERE/'PRODUCER_COMPARISON_RECEIPT.json')
    args=parser.parse_args()
    producer=frozen_import(args.producer,'frozen_producer',PRODUCER_SHA256)
    cp=frozen_import(args.producer.parent/'sources'/'boundary_confidence.py','frozen_cp',CP_SHA256)
    cap_cases=matrix_cases=0
    for caps in product([F(i,8) for i in range(9)],repeat=3):
        expected=polygon_extrema(caps)
        actual=producer.capped_simplex_bounds(dict(zip(ROUTES,caps)))
        if expected is None:
            assert actual['status']!='ok'
        else:
            assert actual['status']=='ok' and unpack(actual)==expected
            for key in ('lower_closure_witness','upper_closure_witness','positive_feasible_witness'):
                p=tuple(F(actual[key][r]) for r in ROUTES)
                assert sum(p)==1 and all(0<=p[i]<=caps[i] for i in range(3))
                if key=='positive_feasible_witness':
                    assert min(p)>0
        cap_cases+=1
    for o,d,p in product(quadrads(3),product([F(0),F(1,2),F(1)],repeat=3),triads(4)):
        feasible=all(d[i]*p[i]<=o[i] for i in range(3))
        try:
            matrix=producer.complete_classifier(dict(zip(LABELS,o)),dict(zip(ROUTES,d)),dict(zip(ROUTES,p)))
        except ValueError:
            assert not feasible
        else:
            assert feasible
            check_matrix(matrix,o,d,p)
        matrix_cases+=1
    fixture_reports=[]
    cached_limits={}
    limits_checked=0
    for name in ('shared_classifier','retained_U_denominator','incompatible_population_contract',
                 'count_separation','no_control_observations'):
        doc=json.loads((args.producer.parent/f'example_{name}.json').read_text())
        if doc['mode']=='population':
            result=producer.population_bounds(doc)
            for inp,out in zip(doc['contexts'],result['contexts']):
                for arm in ('baseline','selected'):
                    o=tuple(F(inp[arm]['observed'][r]) for r in LABELS)
                    d=tuple(F(inp[arm]['correct_call_lower'][r]) for r in ROUTES)
                    caps=tuple(min(F(1),o[i]/d[i]) if d[i] else F(1) for i in range(3))
                    expected=polygon_extrema(caps)
                    assert (out[arm]['status']=='ok')==(expected is not None)
                    if expected is not None:
                        assert unpack(out[arm])==expected
                        for key,matrix in out[arm]['classifier_completions'].items():
                            p=tuple(F(out[arm][key][r]) for r in ROUTES)
                            check_matrix(matrix,o,d,p)
        else:
            result=producer.count_bounds(doc)
            tail=F(doc['alpha'])/(12*len(doc['contexts']))
            assert result['confidence']['per_endpoint_error_exact']==str(tail)
            for inp,out in zip(doc['contexts'],result['contexts']):
                for arm in ('baseline','selected'):
                    counts=inp[arm]['observed_counts']
                    n=sum(counts.values())
                    caps=[]
                    for route in ROUTES:
                        control=inp[arm]['known_truth_controls'][route]
                        obs_key=(counts[route],n,tail)
                        ctrl_key=(control['correct'],control['introduced'],tail)
                        for key in (obs_key,ctrl_key):
                            if key not in cached_limits:
                                cached_limits[key]=cp.clopper_pearson(*key)
                        upper=F(cached_limits[obs_key]['upper'])
                        lower=F(cached_limits[ctrl_key]['lower'])
                        reported=out[arm]['marginal_limits'][route]
                        assert upper==F(reported['observed_upper']['exact'])
                        assert lower==F(reported['correct_call_lower']['exact'])
                        assert reported['observed_trials']==n
                        caps.append(min(F(1),upper/lower) if lower else F(1))
                        limits_checked+=2
                    assert unpack(out[arm])==polygon_extrema(tuple(caps))
        saved=json.loads((args.producer.parent/f'example_{name}_result.json').read_text())
        result['input_sha256']=hashlib.sha256((args.producer.parent/f'example_{name}.json').read_bytes()).hexdigest()
        assert result==saved
        fixture_reports.append({'fixture':f'example_{name}.json',
                                'common_J_status':result['common_J']['status'],
                                'saved_result_matches_execution':True})
    report={'producer_sha256':PRODUCER_SHA256,'preserved_CP_sha256':CP_SHA256,
            'cap_vectors_compared':cap_cases,'classifier_completion_cases':matrix_cases,
            'one_sided_count_limits_compared':limits_checked,'fixtures':fixture_reports,
            'all_checks_passed':True,
            'scope':'Frozen producer comparison against independent polygon/completion logic; CP endpoints intentionally reuse the preserved certified scalar engine.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
