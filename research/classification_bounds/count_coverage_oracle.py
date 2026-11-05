#!/usr/bin/env python3
"""Exact enumeration of a small valid count design; no producer import."""
from fractions import Fraction as F
from itertools import product
from math import factorial
from pathlib import Path
import argparse
import importlib.util
import hashlib
import json
from independent_oracle import polygon_extrema


CP_SHA256='23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d'
HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cp-source',type=Path,default=HERE/'sources'/'boundary_confidence.py')
    parser.add_argument('--output',type=Path,default=HERE/'COUNT_COVERAGE_RECEIPT.json')
    args=parser.parse_args()
    source_hash=hashlib.sha256(args.cp_source.read_bytes()).hexdigest()
    if source_hash!=CP_SHA256:
        raise ValueError('Preserved CP source hash differs from the independently inspected engine')
    spec=importlib.util.spec_from_file_location('stored_cp',args.cp_source)
    cp=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    n=50
    control_n=40
    alpha=F(1,20)
    context_count=2
    tail=alpha/(12*context_count)
    d_lower=F(cp.clopper_pearson(control_n,control_n,tail)['lower'])
    observed_upper=[F(cp.clopper_pearson(k,n,tail)['upper']) for k in range(n+1)]
    rows=[]
    for w in range(n+1):
        for a in range(n-w+1):
            m=n-w-a
            counts=(w,a,m)
            caps=tuple(min(F(1),observed_upper[k]/d_lower) for k in counts)
            bounds=polygon_extrema(caps)
            coefficient=factorial(n)//(factorial(w)*factorial(a)*factorial(m))
            rows.append((counts,bounds,coefficient))
    reports=[]
    for weights,denominator in (((1,1,1),3),((4,2,1),7)):
        selected_p=tuple(F(x,denominator) for x in weights)
        baseline_p=(F(1,3),)*3
        target=(selected_p[1]**2/(selected_p[0]*selected_p[2]))/(baseline_p[1]**2/(baseline_p[0]*baseline_p[2]))
        covered=0
        nonvacuous_intervals=0
        total=3**n*denominator**n
        selected_rows=[]
        for ks,s,cs in rows:
            selected_weight=cs
            for i in range(3):
                selected_weight*=weights[i]**ks[i]
            selected_rows.append((ks,s,selected_weight))
        assert sum(r[2] for r in rows)==3**n
        assert sum(r[2] for r in selected_rows)==denominator**n
        for (kb,b,cb),(ks,s,cs) in product(rows,selected_rows):
            # Selection and baseline classifiers are identity here; U has
            # zero probability but remains an explicit fourth observed class.
            weight=cb*cs
            nonvacuous_intervals+=int((b[1] is not None and s[0]>0) or (s[1] is not None and b[0]>0))
            if (b[1] is None or s[0]<=target*b[1]) and (s[1] is None or s[1]>=target*b[0]):
                covered+=weight
        coverage=F(covered,total)
        assert coverage>=1-alpha/context_count
        reports.append({'selected_probabilities':[str(x) for x in selected_p],
                        'baseline_probabilities':[str(x) for x in baseline_p],
                        'J_exact':str(target),'covered_probability_exact':str(coverage),
                        'coverage_decimal':float(coverage),'positive_probability_of_noncoverage':covered<total,
                        'noncoverage_probability_exact':str(1-coverage),
                        'noncoverage_decimal':float(1-coverage),
                        'outcomes_enumerated':len(rows)**2,
                        'nonvacuous_J_intervals':nonvacuous_intervals})
    report={'alpha_exact':str(alpha),'one_sided_tail_exact':str(tail),
            'observed_units_per_arm':n,'known_truth_units_per_route_arm':control_n,
            'classifier':'identity; all known-truth controls always correct',
            'contexts':reports,
            'scope':'Per-context baseline/selected J coverage under a two-context allocation; not a four-arm shared-null enumeration.',
            'count_design_independence':'Used only for the two-arm multinomial product in this illustrative enumeration; union-bound theorem does not require across-cell independence.',
            'producer_implementation_imported':False,
            'cp_source':'sources/boundary_confidence.py (preserved engine, or --cp-source override)',
            'cp_source_sha256':source_hash,
            'all_checks_passed':True}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
