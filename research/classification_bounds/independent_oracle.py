#!/usr/bin/env python3
"""Independent rational classifier-completion and capped-simplex checks."""
from fractions import Fraction as F
from itertools import product, combinations
import json
from pathlib import Path


def triads(n):
    return [(F(w,n),F(a,n),F(n-w-a,n)) for w in range(n+1) for a in range(n-w+1)]


def quadrads(n):
    return [(F(w,n),F(a,n),F(m,n),F(n-w-a-m,n))
            for w in range(n+1) for a in range(n-w+1) for m in range(n-w-a+1)]


def polygon_extrema(u):
    """Enumerate vertices/edge critical points without the producer formulas."""
    if min(u)<=0 or sum(u)<1:
        return None
    candidates=set()
    for i,j in combinations(range(3),2):
        k=3-i-j
        for x,y in product((0,u[i]),(0,u[j])):
            p=[F(0)]*3
            p[i],p[j],p[k]=F(x),F(y),1-x-y
            if all(0<=p[t]<=u[t] for t in range(3)):
                candidates.add(tuple(p))
    # Each polygon edge is a fixed-coordinate segment. Q has no critical
    # points on fixed-W or fixed-M edges; on fixed-A edges W=M is critical.
    for a in (F(0),u[1]):
        p=((1-a)/2,a,(1-a)/2)
        if all(0<=p[t]<=u[t] for t in range(3)):
            candidates.add(p)
    # A=0 may be feasible only through a nonsymmetric edge. Add edge midpoint.
    zero_a=sorted(p for p in candidates if p[1]==0)
    if len(zero_a)>1:
        candidates.add(tuple((zero_a[0][t]+zero_a[-1][t])/2 for t in range(3)))
    vals=[]
    unbounded=False
    for w,a,m in candidates:
        if w*m>0:
            vals.append(a*a/(w*m))
        elif a>0:
            unbounded=True
    assert vals or unbounded
    # Some all-boundary polygons have no finite vertex values but have
    # an interior equal-coordinate candidate; the positive domain guarantees
    # a finite minimum candidate under this full enumeration.
    assert vals
    return min(vals),None if unbounded else max(vals)


def proposed_extrema(u):
    if min(u)<=0 or sum(u)<1:
        return None
    a=max(F(0),1-u[0]-u[2])
    w=max(max(F(0),1-a-u[2]),min((1-a)/2,min(u[0],1-a)))
    lower=a*a/(w*(1-a-w))
    a=u[1]
    wl,wh=max(F(0),1-a-u[2]),min(u[0],1-a)
    den=min(wl*(1-a-wl),wh*(1-a-wh))
    return lower,None if den==0 else a*a/den


def completion(o,d,p,beta=F(1)):
    masses=tuple(beta*x for x in p)+(1-beta,)
    diag=tuple(beta*d[i]*p[i] for i in range(3))
    residual=tuple(o[i]-diag[i] for i in range(3))+(o[3],)
    if min(residual)<0:
        return None
    R=sum(residual)
    columns=[]
    for i in range(4):
        di=d[i] if i<3 else F(0)
        col=[F(0)]*4
        if R:
            col=[(1-di)*z/R for z in residual]
            if i<3:
                col[i]+=di
        else:
            col[i]=F(1)
        columns.append(tuple(col))
    assert all(min(c)>=0 and sum(c)==1 for c in columns)
    assert all(columns[i][i]>=d[i] for i in range(3))
    assert all(sum(columns[i][j]*masses[i] for i in range(4))==o[j] for j in range(4))
    return columns


def main():
    cap_cases=grid_points=completion_cases=other_cases=0
    for u in product([F(i,8) for i in range(9)],repeat=3):
        expected=polygon_extrema(u)
        actual=proposed_extrema(u)
        assert actual==expected,(u,actual,expected)
        cap_cases+=1
        if actual is None:
            continue
        for p in triads(24):
            if min(p)<=0 or any(p[i]>u[i] for i in range(3)):
                continue
            q=p[1]**2/(p[0]*p[2])
            assert q>=actual[0] and (actual[1] is None or q<=actual[1])
            grid_points+=1
    for o,d,p in product(quadrads(3),product([F(0),F(1,2),F(1)],repeat=3),triads(4)):
        caps=tuple(min(F(1),o[i]/d[i]) if d[i] else F(1) for i in range(3))
        feasible=all(p[i]<=caps[i] for i in range(3))
        c=completion(o,d,p)
        assert (c is not None)==feasible
        completion_cases+=1
        for beta in (F(1,4),F(1,2)):
            caps=tuple(min(F(1),o[i]/(beta*d[i])) if d[i] else F(1) for i in range(3))
            feasible=all(p[i]<=caps[i] for i in range(3))
            c=completion(o,d,p,beta)
            assert (c is not None)==feasible
            other_cases+=1
    report={'rational_cap_vectors_checked':cap_cases,'positive_rational_latent_grid_checks':grid_points,
            'classifier_completion_cases':completion_cases,'true_other_completion_cases':other_cases,
            'all_checks_passed':True,'producer_implementation_imported':False,
            'scope':'Finite exact rational software checks support but do not replace the algebraic proof.'}
    Path(__file__).with_name('INDEPENDENT_ORACLE_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
