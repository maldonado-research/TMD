#!/usr/bin/env python3
"""TMD 0.5.0: Bonferroni Clopper-Pearson confidence projection; no MLE or LRT.
Copyright (c) 2026 Ricardo Maldonado. MIT; see LICENSE and VERSION_LINEAGE.md.
Floating roots propose endpoints; exact rational binomial tails certify coverage.
"""
from __future__ import annotations
import argparse
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

ROUTES=('W','A','M');BRANCHES=('baseline','selected')
MAX_TRIALS=5000;MAX_CONTEXTS=64;MIN_ALPHA=1e-12


def integer_count(value,label):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or value!=int(value):
        raise ValueError(f'{label} must be a nonnegative integer; missing values are not zeros')
    value=int(value)
    if value>MAX_TRIALS:raise ValueError(f'{label} exceeds prototype limit {MAX_TRIALS}')
    return value


def alpha_fraction(alpha):
    if isinstance(alpha,bool):raise ValueError('Alpha must be a number')
    try:value=Fraction(str(alpha))
    except (ValueError,TypeError,ZeroDivisionError):raise ValueError('Alpha must be finite numeric')
    if not Fraction(str(MIN_ALPHA))<=value<1:raise ValueError(f'Alpha must be at least {MIN_ALPHA} and below one')
    return value


def float_tail(n,k,p,upper=True):
    """Stable shorter-tail log-sum recurrence, used ONLY to propose a root."""
    if upper:
        if k<=0:return 1.
        if k>n:return 0.
    else:
        if k<0:return 0.
        if k>=n:return 1.
    if p<=0:return float(k<=0) if upper else 1.
    if p>=1:return 1. if upper else float(k>=n)
    # Choose the shorter positive sum; complement only for proposal accuracy.
    direct_upper=upper
    if upper and n-k+1>k:direct_upper=False;cut=k-1;complement=True
    elif not upper and k+1>n-k:direct_upper=True;cut=k+1;complement=True
    else:cut=k;complement=False
    start=cut if direct_upper else 0;stop=n if direct_upper else cut
    lp,lq=math.log(p),math.log1p(-p)
    term=math.lgamma(n+1)-math.lgamma(start+1)-math.lgamma(n-start+1)+start*lp+(n-start)*lq
    logs=[term]
    for j in range(start,stop):
        term+=math.log(n-j)-math.log(j+1)+lp-lq;logs.append(term)
    peak=max(logs);log_sum=peak+math.log(math.fsum(math.exp(v-peak) for v in logs))
    value=-math.expm1(min(0.,log_sum)) if complement else math.exp(min(0.,log_sum))
    return max(0.,min(1.,value))


def exact_tail(n,k,p,upper=True):
    """Return exact integer numerator/denominator for a binomial tail at float p."""
    if upper:
        if k<=0:return (1,1)
        if k>n:return (0,1)
    else:
        if k<0:return (0,1)
        if k>=n:return (1,1)
    if p==0.:return (int(k<=0),1) if upper else (1,1)
    if p==1.:return (1,1) if upper else (int(k>=n),1)
    U,D=float(p).as_integer_ratio();Q=D-U
    if not 0<U<D:raise ValueError('Tail probability must be between zero and one')
    if upper and n-k+1>k:return_complement=True;start=0;stop=k-1
    elif not upper and k+1>n-k:return_complement=True;start=k+1;stop=n
    else:return_complement=False;start=k if upper else 0;stop=n if upper else k
    term=math.comb(n,start)*U**start*Q**(n-start);total=term
    for j in range(start,stop):
        numerator=term*(n-j)*U;denominator=(j+1)*Q
        term,remainder=divmod(numerator,denominator)
        if remainder:raise ArithmeticError('Exact binomial recurrence lost integer divisibility')
        total+=term
    denominator=D**n
    if return_complement:total=denominator-total
    return total,denominator


def tail_at_most(n,k,p,target,upper):
    numerator,denominator=exact_tail(n,k,p,upper)
    return numerator*target.denominator<=target.numerator*denominator


def proposed_root(n,k,target,upper):
    q=float(target)
    if upper and k==n:return math.exp(math.log(q)/n)
    if not upper and k==0:return -math.expm1(math.log(q)/n)
    left,right=0.,1.
    for _ in range(90):
        middle=(left+right)/2
        if middle==left or middle==right:break
        value=float_tail(n,k,middle,upper)
        if (value<q)==upper:left=middle
        else:right=middle
    return (left+right)/2


def certified_outer_endpoint(n,k,target,upper):
    candidate=proposed_root(n,k,target,upper)
    # Lower confidence endpoints use increasing upper tails; upper endpoints decreasing lower tails.
    direction=-1 if upper else 1
    width=max(16*math.ulp(candidate),1e-10*candidate*(1-candidate))
    for correction in range(80):
        endpoint=max(0.,min(1.,candidate+direction*width))
        if tail_at_most(n,k,endpoint,target,upper):
            return endpoint,{'exact_tail_certified':True,'outward_expansions':correction,
                             'proposed_root':candidate,'outward_width':width}
        width*=2
    # Endpoint 0 or 1 always certifies but can be uninformative; no fabricated finite bound.
    endpoint=0. if upper else 1.
    if not tail_at_most(n,k,endpoint,target,upper):raise ArithmeticError('Endpoint certificate failed')
    return endpoint,{'exact_tail_certified':True,'outward_expansions':80,'coarsened_to_support_boundary':True}


def clopper_pearson(k,n,tail_error):
    n=integer_count(n,'trials');k=integer_count(k,'successes')
    if k>n:raise ValueError('Successes cannot exceed trials')
    target=tail_error if isinstance(tail_error,Fraction) else Fraction(str(tail_error))
    if not 0<target<Fraction(1,2):raise ValueError('Each tail error must be strictly between zero and one half')
    if n==0:return {'lower':0.,'upper':1.,'status':'no_observations','certificates':[]}
    certificates=[]
    if k==0:lower=0.
    else:lower,cert=certified_outer_endpoint(n,k,target,True);certificates.append(dict(endpoint='lower',**cert))
    if k==n:upper=1.
    else:upper,cert=certified_outer_endpoint(n,k,target,False);certificates.append(dict(endpoint='upper',**cert))
    if not 0<=lower<=upper<=1:raise ArithmeticError('Invalid certified confidence interval')
    return {'lower':lower,'upper':upper,'status':'certified','certificates':certificates}


def route_dict(value,label):
    if not isinstance(value,dict) or set(value)!=set(ROUTES):raise ValueError(f'{label} must contain exactly W,A,M; missing counts are not zero')
    return [value[r] for r in ROUTES]


def validate_document(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get('metadata'),dict):raise ValueError('Input and metadata must be objects')
    meta=doc['metadata']
    for key in ('categorical_multinomial_marginals_justified','route_control_binomial_marginals_justified',
                'common_genetic_background','context_matched_calibration','control_relative_recovery_transports',
                'eligible_winner_observation_rule_locked','positive_population_components_for_log_contrast'):
        if meta.get(key) is not True:raise ValueError(f'metadata.{key} must explicitly be true')
    if meta.get('control_sampling_design')!='fixed_route_independent_binomial' or meta.get('control_outcome_definition')!='one_binary_recovery_per_introduced_unit':
        raise ValueError('Known fixed route denominators and one binary recovery per unit required')
    unit=meta.get('exposed_unit_definition')
    if not isinstance(unit,str) or not unit.strip():raise ValueError('A nonempty exposed-unit definition is required')
    if meta.get('calibration_design')!='matched_route_multinomial' or meta.get('calibration_validation')!='validated_for_route_probability':
        raise ValueError('Validated categorical route calibration required; colony/fluctuation totals unsupported')
    if meta.get('triad_sampling') not in ('exhaustive_triad','conditioned_on_triad'):raise ValueError('Explicit common triad sampling rule required')
    if meta.get('provenance') not in ('synthetic','observed','literature_transcription'):raise ValueError('Explicit provenance required')
    if doc.get('route_order')!=list(ROUTES) or doc.get('branch_order')!=list(BRANCHES):raise ValueError('Explicit W,A,M route and baseline,selected branch orders required')
    contexts=doc.get('contexts')
    if not isinstance(contexts,list) or not 1<=len(contexts)<=MAX_CONTEXTS or any(not isinstance(c,dict) for c in contexts):raise ValueError(f'One to {MAX_CONTEXTS} context objects required')
    names=[c.get('context') for c in contexts]
    if any(not isinstance(n,str) or not n for n in names) or len(set(names))!=len(names):raise ValueError('Unique nonempty context names required')
    parsed=[]
    for c in contexts:
        counts=[];introduced=[];recovered=[]
        for branch in BRANCHES:
            row=[integer_count(v,branch+' route count') for v in route_dict(c.get(branch+'_counts'),branch+'_counts')]
            if sum(row)>MAX_TRIALS:raise ValueError(f'Categorical sample total exceeds {MAX_TRIALS}')
            control=route_dict(c.get(branch+'_recovery_controls'),branch+'_recovery_controls')
            if any(not isinstance(v,dict) or set(v)!= {'introduced','recovered'} for v in control):raise ValueError('Each control requires explicit introduced and recovered values')
            L=[integer_count(v['introduced'],'introduced') for v in control];k=[integer_count(v['recovered'],'recovered') for v in control]
            if any(l<=0 for l in L):raise ValueError('Known introduced denominators must be positive')
            if any(s>l for s,l in zip(k,L)):raise ValueError('Recovered units cannot exceed introduced units')
            counts.append(row);introduced.append(L);recovered.append(k)
        parsed.append((counts,introduced,recovered))
    return names,parsed


def endpoint(value,infinity=None):return {'value':value,'infinity':infinity}


def theta_endpoint(ratio,lower):
    if ratio is None:return endpoint(None,'positive')
    if ratio==0:return endpoint(None,'negative')
    # Enclose the rational first, then correctly-rounded Decimal ln by adjacent decimals.
    with localcontext() as ctx:
        ctx.prec=90;ctx.rounding=ROUND_FLOOR if lower else ROUND_CEILING
        bound=Decimal(ratio.numerator)/Decimal(ratio.denominator)
        nearest=bound.ln() # Decimal ln is correctly rounded using ROUND_HALF_EVEN.
        log_bound=nearest.next_minus() if lower else nearest.next_plus()
        decimal_theta=log_bound/2
        candidate=float(decimal_theta)
    candidate=math.nextafter(candidate,-math.inf if lower else math.inf)
    if not math.isfinite(candidate):raise ArithmeticError('Finite contrast display overflow')
    return endpoint(candidate)


def project_context(intervals):
    # J=exp(2theta); exact integer powers remove log-rounding from the decision.
    exponents={'baseline':[1,-2,1],'selected':[-1,2,-1],
               'baseline_controls':[-1,2,-1],'selected_controls':[1,-2,1]}
    if not isinstance(intervals,dict) or set(intervals)!=set(exponents):raise ValueError('Exactly four groups of route intervals required')
    for group in exponents:
        cells=intervals[group]
        if not isinstance(cells,list) or len(cells)!=3:raise ValueError('Each interval group requires W,A,M intervals')
        for cell in cells:
            if not isinstance(cell,dict) or 'lower' not in cell or 'upper' not in cell:raise ValueError('Explicit lower and upper interval endpoints required')
            if isinstance(cell['lower'],bool) or isinstance(cell['upper'],bool):raise ValueError('Probability endpoints cannot be boolean')
            try:lo,hi=Fraction(cell['lower']),Fraction(cell['upper'])
            except (ValueError,TypeError,OverflowError):raise ValueError('Finite numeric probability endpoints required')
            if not 0<=lo<=hi<=1 or hi==0:raise ValueError('Intervals must lie in [0,1] with positive upper endpoint')
    lower=Fraction(1);upper=Fraction(1);unbounded=False
    for group,powers in exponents.items():
        for cell,power in zip(intervals[group],powers):
            lo,hi=Fraction(cell['lower']),Fraction(cell['upper'])
            if power>0:lower*=lo**power;upper*=hi**power
            else:
                lower/=hi**(-power)
                if lo==0:unbounded=True
                elif not unbounded:upper/=lo**(-power)
    upper=None if unbounded else upper
    return {'theta_interval':{'lower':theta_endpoint(lower,True),'upper':theta_endpoint(upper,False)},
            'J_lower_exact':str(lower),'J_upper_exact':None if upper is None else str(upper),
            'J_upper_infinity':'positive' if upper is None else None},lower,upper


def simultaneous_confidence(doc,alpha=.05):
    names,data=validate_document(doc);a=alpha_fraction(alpha);C=len(names);coordinates=12*C;tail=a/(2*coordinates)
    contexts=[];bounds=[]
    for name,(counts,L,k) in zip(names,data):
        intervals={}
        for j,branch in enumerate(BRANCHES):
            intervals[branch]=[clopper_pearson(v,sum(counts[j]),tail) for v in counts[j]]
            intervals[branch+'_controls']=[clopper_pearson(s,l,tail) for s,l in zip(k[j],L[j])]
        projection,lower,upper=project_context(intervals);bounds.append((lower,upper))
        contexts.append({'context':name,'marginal_intervals':intervals,**projection})
    lower=max(b[0] for b in bounds);finite=[b[1] for b in bounds if b[1] is not None];upper=min(finite) if finite else None
    empty=upper is not None and lower>upper
    decision='not_evaluable_one_context' if C==1 else ('reject_shared_theta' if empty else 'no_shared_theta_departure_established')
    return {'schema_version':'0.5.0','method':'Equal-Bonferroni Clopper-Pearson rectangular confidence projection',
            'nominal_alpha':str(a),'coordinates':coordinates,'per_tail_error_exact':str(tail),
            'simultaneous_coverage_lower_bound_exact':str(1-a),'contexts':contexts,
            'shared_theta_intersection':{'empty':empty,'J_lower_exact':str(lower),
                'J_upper_exact':None if upper is None else str(upper),'J_upper_infinity':'positive' if upper is None else None,
                'theta_lower_display':theta_endpoint(lower,True),'theta_upper_display':theta_endpoint(upper,False)},
            'decision':decision,'p_value':None,
            'decision_basis':'Exact rational intersection of projected J=exp(2theta) intervals; theta endpoints are outward display enclosures.',
            'numerical_policy':{'maximum_trials':MAX_TRIALS,'maximum_contexts':MAX_CONTEXTS,'minimum_alpha':MIN_ALPHA,
                'CP_endpoint_certification':'Exact integer binomial tails at dyadic float endpoints, compared to exact rational tail allocation'},
            'scope':'Finite-sample simultaneous coverage and shared-null rejection bound under valid marginal count laws and relative recovery transport, for finite positive log contrasts. No across-component independence is needed for the union bound. Not a likelihood fit, profile interval, equivalence result or mechanism validation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path)
    parser.add_argument('--alpha',default='0.05');parser.add_argument('--output',type=Path);args=parser.parse_args()
    try:
        raw=args.input.read_bytes();doc=json.loads(raw);result=simultaneous_confidence(doc,args.alpha)
        result.update(input_sha256=hashlib.sha256(raw).hexdigest(),metadata=doc['metadata'],
                      provenance_warning='Synthetic fixtures are software/mathematical checks, not biological evidence.' if doc['metadata']['provenance']=='synthetic' else 'Declarations and hashes do not authenticate marginal laws or recovery transport.')
        encoded=json.dumps(result,indent=2,allow_nan=False)+'\n'
        if args.output:args.output.write_text(encoded)
        else:print(encoded,end='')
    except (ValueError,TypeError,KeyError,ArithmeticError,OSError) as exc:parser.exit(2,f'Invalid input or unsupported numerical domain: {exc}\n')

if __name__=='__main__':main()
