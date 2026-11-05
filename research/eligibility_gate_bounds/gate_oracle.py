#!/usr/bin/env python3
"""Independent exact-rational eligibility-gate checks; no producer imported."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path


def beta(g, f):
    return max(F(0), (g-f)/(1-f)) if f < 1 else F(0)


def gate_witness(g, f):
    t = beta(g, f)
    if t == 0:
        return t, F(0), g
    return t, F(1), f


def triads(n):
    return [(F(w,n),F(a,n),F(n-w-a,n))
            for w in range(1,n) for a in range(1,n-w)]


def quadrads(n):
    return [(F(w,n),F(a,n),F(m,n),F(n-w-a-m,n))
            for w in range(n+1) for a in range(n-w+1)
            for m in range(n-w-a+1)]


def label_completion(o,d,p,t):
    """Return label columns conditional on W,A,M,Other, or None."""
    residual=tuple(o[i]-t*d[i]*p[i] for i in range(3))+(o[3],)
    if min(residual)<0:
        return None
    r=sum(residual)
    z=tuple(x/r for x in residual) if r else (F(0),F(0),F(0),F(1))
    cols=[]
    for i in range(4):
        di=d[i] if i<3 else F(0)
        cols.append(tuple(di*int(j==i)+(1-di)*z[j] for j in range(4)))
    masses=tuple(t*x for x in p)+(1-t,)
    assert all(min(col)>=0 and sum(col)==1 for col in cols)
    assert all(cols[i][i]>=d[i] for i in range(3))
    assert all(sum(masses[i]*cols[i][j] for i in range(4))==o[j] for j in range(4))
    return cols


def main():
    necessity=sharpness=monotonicity=label_cases=joint_cases=zero_beta_limits=0
    grid=[F(i,12) for i in range(13)]
    for t,a,f in product(grid,repeat=3):
        g=a*t+f*(1-t)
        for f_upper in grid:
            if f_upper<f:
                continue
            for g_lower in grid:
                if g_lower<=g:
                    assert t>=beta(g_lower,f_upper)
                    necessity+=1
    fine=[F(i,24) for i in range(25)]
    for g,f in product(fine,repeat=2):
        t,a,fp=gate_witness(g,f)
        assert 0<=t<=1 and 0<=a<=1 and 0<=fp<=f
        assert a*t+fp*(1-t)==g
        assert t==beta(g,f)
        sharpness+=1
        if t==0:
            # Conditional triad targets require T>0. These gate kernels permit
            # every arbitrarily small positive T without altering the marginal.
            for eps in (F(1,10),F(1,100),F(1,1000)):
                assert g*eps+g*(1-eps)==g and g<=f
                zero_beta_limits+=1
    for g1,g2,f1,f2 in product(grid,repeat=4):
        if g1<=g2 and f1<=f2:
            assert beta(g1,f2)<=beta(g2,f1)
            monotonicity+=1
    for g,f in product([F(i,4) for i in range(5)],repeat=2):
        t,a,fp=gate_witness(g,f)
        if not t:
            continue
        for o,d,p in product(quadrads(4),product((F(0),F(1)),repeat=3),triads(6)):
            caps=tuple(min(F(1),o[i]/(t*d[i])) if d[i] else F(1) for i in range(3))
            admissible=all(p[i]<=caps[i] for i in range(3))
            cols=label_completion(o,d,p,t)
            assert (cols is not None)==admissible
            label_cases+=1
            if cols is None:
                continue
            # Conditional independence constructs one admissible *unrestricted*
            # joint gate-label law, including T=1 where Other is unoccupied.
            masses=tuple(t*x for x in p)+(1-t,)
            gate_rates=(a,a,a,fp)
            gate_mass=sum(masses[i]*gate_rates[i] for i in range(4))
            assert gate_mass==g
            for i in range(4):
                joint=[cols[i][j]*gate_rates[i] for j in range(4)]
                joint += [cols[i][j]*(1-gate_rates[i]) for j in range(4)]
                assert min(joint)>=0 and sum(joint)==1
            joint_cases+=1
    # PPV is not full-cohort T: perfect eligibility gating can have small T.
    t,a,f=F(1,10),F(1),F(0)
    g=a*t+f*(1-t)
    ppv=a*t/g
    o=(F(1,5),)*3+(F(2,5),)
    d=(F(3,5),)*3
    p=(F(4,5),F(1,10),F(1,10))
    assert ppv==1 and beta(g,f)==t
    assert label_completion(o,d,p,t) is not None
    assert label_completion(o,d,p,ppv) is None
    # No negative-control constraint gives F=1 and no positive T bound even
    # for a population gate-positive fraction of one.
    for eps in (F(1,10),F(1,100),F(1,1000)):
        assert eps+1-eps==1 and beta(F(1),F(1))==0
    # Coupling counterexample: G+ iff observed W, exact identity classification
    # on eligible units, and zero W false gates on Other force oW=T*pW.
    o2=(F(1,2),F(1,4),F(1,4),F(0))
    p2=(F(1,10),F(9,20),F(9,20))
    b2=beta(o2[0],F(0))
    caps2=tuple(min(F(1),x/b2) for x in o2[:3])
    assert all(p2[i]<=caps2[i] for i in range(3))
    assert o2[0]/p2[0]>1
    assert label_completion(o2,(F(1),)*3,p2,b2) is not None
    report={
        'all_checks_passed':True,
        'producer_implementation_imported':False,
        'gate_necessity_cases':necessity,
        'sharp_gate_endpoint_witnesses':sharpness,
        'zero_beta_positive_T_approaches':zero_beta_limits,
        'conservative_endpoint_monotonicity_cases':monotonicity,
        'eligible_fraction_label_completion_cases':label_cases,
        'unrestricted_joint_gate_label_completions':joint_cases,
        'counterexamples':{
            'PPV_not_full_cohort_fraction':{'T':'1/10','gate_sensitivity':'1','Other_false_gate':'0','gate_rate':'1/10','PPV':'1','true_latent_p':['4/5','1/10','1/10'],'observed':['1/5','1/5','1/5','2/5'],'correct_lower':['3/5']*3},
            'no_negative_control_information':{'F':'1','gate_rate':'1','beta':'0'},
            'ignored_gate_label_coupling':{'definition':'G+ iff observed W','observed':['1/2','1/4','1/4','0'],'correct_lower':['1']*3,'Other_false_gate':'0','beta':'1/2','outer_caps':['1','1/2','1/2'],'outer_feasible_p':['1/10','9/20','9/20'],'joint_required_T':'5'}
        },
        'scope':'Finite exact rational checks support the algebraic proof. Gate-only sharpness does not establish sharpness under additional gate-label coupling.'
    }
    Path(__file__).with_name('GATE_ORACLE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
