"""Independent synthetic-only partial-capture and finite compound-Poisson checks."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import comb, factorial
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def D(value):
    return Decimal(value.numerator)/Decimal(value.denominator)


def A(p):
    if p==0:return Decimal(0)
    if p==1:return Decimal(1)
    pd=D(p)
    return pd*(-pd.ln())/(1-pd)


def truncated_bounds(p,k):
    t=1-p
    s=sum((t**j/F(j*(j+1)) for j in range(1,k+1)),F())
    tail=t**(k+1)/(k+1)
    return 1-s-tail,1-s


def recurrence(m,q,nmax):
    out=[F(1)]
    for n in range(1,nmax+1):
        out.append(m/n*sum((j*q[j]*out[n-j] for j in range(1,min(n,len(q)-1)+1)),F()))
    return out


def partition_coefficient(m,q,n):
    # A distinct exhaustive count-of-jumps formula, not the recursive PMF oracle.
    total=F()
    def visit(j,remaining,value):
        nonlocal total
        if j==len(q):
            if remaining==0:total+=value
            return
        for count in range(remaining//j+1):
            visit(j+1,remaining-j*count,value*(m*q[j])**count/factorial(count))
    visit(1,n,F(1))
    return total


def run(producer_script=None):
    assertions=0
    p_grid=[F(0),F(3,40000),F(1,6000),F(3,4000),F(3,40),F(1,10),F(1,2),F(9,10),F(1)]
    tail_cases=0
    zero_cases=0
    with localcontext() as ctx:
        ctx.prec=140
        for p in p_grid:
            ad=A(p)
            for k in [1,2,3,8,16,32,64]:
                low,high=truncated_bounds(p,k)
                assert 0<=low<=high<=1
                assert D(low)<=ad<=D(high)
                assertions+=2;tail_cases+=1
                for m in [F(1,100),F(1,2),F(1),F(5)]:
                    point=(-D(m)*ad).exp()
                    pl=(-D(m)*D(high)).exp()
                    pu=(-D(m)*D(low)).exp()
                    assert pl<=point<=pu
                    assertions+=1;zero_cases+=1
        full_law=[]
        for p in [F(1,10),F(4,5)]:
            pd=D(p);m=1/A(p)
            derivative=(-pd.ln()-1+pd)/(1-pd)**2
            ratio=m*pd*derivative
            full_law.append({'p':str(p),'m_for_unit_zero_intensity_decimal':str(m),'P1_over_P0_decimal':str(ratio)})
        assert full_law[0]['P1_over_P0_decimal']!=full_law[1]['P1_over_P0_decimal']
        assertions+=1
    finite=[];partition_checks=0
    for k in [2,3,8]:
        for p in [F(0),F(1,3),F(1,2),F(1)]:
            q=[F(comb(k,j))*p**j*(1-p)**(k-j) for j in range(k+1)]
            assert sum(q,F())==1;assertions+=1
            for m in [F(2,3),F(4,3)]:
                coeff=recurrence(m,q,8)
                for n in range(9):
                    assert coeff[n]==partition_coefficient(m,q,n)
                    partition_checks+=1;assertions+=1
    for k in [2,8]:
        p=F(1,2);a=1-(1-p)**k;m=1/a
        assert m*a==1;assertions+=1
        first=m*k*p*(1-p)**(k-1)
        finite.append({'clone_size':k,'p':str(p),'m':str(m),'negative_log_P0':'1','P1_over_P0_exact':str(first)})
    assert finite[0]['P1_over_P0_exact']=='2/3' and finite[1]['P1_over_P0_exact']=='8/255';assertions+=1
    producer_checks=0;endpoint_checks=0
    if producer_script:
        spec=importlib.util.spec_from_file_location('reviewed_conditional_fluctuation',producer_script)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for k in [2,3,8]:
            for p in [F(0),F(1,3),F(1,2),F(1)]:
                q=[F(comb(k,j))*p**j*(1-p)**(k-j) for j in range(k+1)]
                observed=module.thin_clone_law({k:F(1)},p)
                assert observed==dict(enumerate(q));producer_checks+=1
                for m in [F(2,3),F(4,3)]:
                    rec=module.cp_relative_coefficients_recurrence(m,observed,8)
                    direct=module.cp_relative_coefficients_direct(m,observed,8)
                    for n in range(9):
                        exact=partition_coefficient(m,q,n)
                        assert rec[n]==exact and direct[n]==exact
                        producer_checks+=2
        with localcontext() as ctx:
            ctx.prec=140
            for p in p_grid:
                assert abs(module.ld_zero_factor(p)-A(p))<Decimal('1e-75')
                producer_checks+=1
                for k in [1,2,3,8,16,32,64]:
                    low,high=truncated_bounds(p,k)
                    g_low,g_high=module.clone_zero_bounds(p,k)
                    assert (low,high)==(1-g_high,1-g_low)
                    producer_checks+=1
        for p in [F(0),F(1)]:
            for law in [{1:F(1)},{16:F(1)},module.capped_clone_law(16)]:
                obs=module.thin_clone_law(law,p)
                for fn in [module.cp_relative_coefficients_recurrence,module.cp_relative_coefficients_direct]:
                    assert fn(F(0),obs,32)==[F(1)]+[F(0)]*32;endpoint_checks+=1
        obs=module.thin_clone_law(module.capped_clone_law(16),F(0))
        assert len(obs)==17 and obs[0]==1;endpoint_checks+=1
        for fn in [module.cp_relative_coefficients_recurrence,module.cp_relative_coefficients_direct]:
            assert fn(F(100),obs,32)==[F(1)]+[F(0)]*32;endpoint_checks+=1
    return {'status':'passed','synthetic_only':True,'independent_assertions':assertions,
            'rational_tail_bound_cases':tail_cases,'high_precision_zero_bound_cases':zero_cases,
            'finite_PMF_partition_comparisons':partition_checks,
            'reviewed_producer_function_assertions':producer_checks,
            'reviewed_producer_endpoint_assertions':endpoint_checks,
            'reviewed_producer_sha256':hashlib.sha256(Path(producer_script).read_bytes()).hexdigest() if producer_script else None,
            'LD_equal_zero_intensity_different_positive_count_examples':full_law,
            'finite_clone_equal_zero_intensity_examples':finite,
            'decimal_precision':140,'decimal_comparisons_are_not_certified_score_intervals':True,
            'new_sampling_law_or_biological_rate_fit':False,
            'source_integer_colonies_not_used_as_mutation_births':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--producer-script',type=Path)
    args=parser.parse_args()
    receipt=run(args.producer_script)
    receipt['reviewer_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
