"""Compare the producer to previously saved physical-model corner enumeration."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import argparse, copy, hashlib, importlib.util, json, subprocess, sys

NAMES={'mass':'endpoint_masses','supply':'supply_weights','growth':'growth_yields','recovery':'recovery_probabilities'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine',type=Path,required=True);p.add_argument('--sha256',required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    assert __debug__, 'Oracle assertions must be enabled'
    raw=args.engine.read_bytes();assert hashlib.sha256(raw).hexdigest()==args.sha256
    spec=importlib.util.spec_from_file_location('producer_r18',args.engine);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    blind=json.loads((Path(__file__).parent/'R18_BLIND_ORACLE.json').read_text())
    checks=0
    def check(condition):
        nonlocal checks
        if not condition: raise AssertionError('Independent comparison failed at check '+str(checks+1))
        checks+=1
    def request(contexts, forecast=None):
        return {'schema_version':1,'provenance':'synthetic','assumptions':copy.deepcopy(mod.REQUIRED_ASSUMPTIONS),'contexts':contexts,'forecast_K':forecast}
    def converted(case):
        return {'name':case['id'],**{NAMES[k]:v for k,v in case['context'].items()}}
    full_null_checks=[]
    for row in blind['cases']:
        ctx=converted(row);got=mod.certify(request([ctx]))
        interval=got['contexts'][0]['K_interval'];lo,hi=map(F,row['sharp_curvature'])
        check((F(interval['lower']),F(interval['upper']))==(lo,hi))
        # Independently enumerate each route's quotient extrema for full proportionality.
        route_ranges=[]
        for i in range(3):
            variables=[tuple(dict.fromkeys(map(F,row['context'][k][i]))) for k in ('mass','supply','growth','recovery')]
            quotients=[m/(q*g*r) for m,q,g,r in product(*variables)]
            route_ranges.append((min(quotients),max(quotients)))
        expected_full_null=max(a for a,b in route_ranges)<=min(b for a,b in route_ranges)
        full=got['conventional_supply_growth_recovery_model']
        check(full['status']==('conditionally_feasible' if expected_full_null else 'conditionally_incompatible'))
        full_null_checks.append({'id':row['id'],'route_ratio_bounds':[[str(a),str(b)] for a,b in route_ranges],'expected_full_null_feasible':expected_full_null})
        for target in (lo,hi,(lo+hi)/2,lo/2,hi*2):
            if max(target.numerator.bit_length(),target.denominator.bit_length())>32:
                try: mod.certify(request([ctx],str(target)))
                except ValueError: checks+=1
                else: raise AssertionError('Oversized externally supplied target admitted')
                continue
            fixed=mod.certify(request([ctx],str(target)))['fixed_curvature_forecast']
            check(fixed['status']==('conditionally_feasible' if lo<=target<=hi else 'conditionally_incompatible'))
            check(fixed['is_statistical_rejection'] is False)
    # One context at K=1 can still fail full proportionality: outer ratio tilts remain.
    c={'name':'curvature_one_but_full_null_fails',**{n:[['1','1']]*3 for n in NAMES.values()}}
    c['endpoint_masses']=[['2','2'],['1','1'],['1/2','1/2']]
    got=mod.certify(request([c],'1'))
    check(got['fixed_curvature_forecast']['status']=='conditionally_feasible')
    check(got['conventional_supply_growth_recovery_model']['status']=='conditionally_incompatible')
    # Single-variable population mass boxes build independent closed intervals exactly.
    for lo1,hi1,lo2,hi2 in [(1,2,2,3),(1,2,3,4),(1,4,2,3),(2,2,2,2)]:
        ctxs=[]
        for i,(a,b) in enumerate(((lo1,hi1),(lo2,hi2))):
            ctx={'name':'c'+str(i),**{n:[['1','1']]*3 for n in NAMES.values()}}
            ctx['endpoint_masses'][1]=[str(a),str(b)];ctxs.append(ctx)
        got=mod.certify(request(ctxs))['free_common_curvature']
        l=max(F(lo1)**2,F(lo2)**2);u=min(F(hi1)**2,F(hi2)**2)
        check(got['intersection_empty']==(l>u))
        check(got['status']==('conditionally_feasible' if l<=u else 'conditionally_incompatible'))
        check(F(got['intersection_lower'])==l and F(got['intersection_upper'])==u)
        check(got['contact_only']==(l==u))
    original=request([converted(blind['cases'][0])])
    bad=[]
    for name,value in [('zero',0),('negative',-1),('float',0.5),('boolean',True),('missing',None),('unbounded','Infinity'),('oversized',2**32)]:
        req=copy.deepcopy(original);req['contexts'][0]['endpoint_masses'][0][0]=value;bad.append((name,req))
    req=copy.deepcopy(original);req['contexts'][0]['recovery_probabilities'][0]=['1','2'];bad.append(('recovery_above_one',req))
    req=copy.deepcopy(original);req['assumptions']['representation']='normalized_simplex_coordinate_bounds';bad.append(('simplex',req))
    req=copy.deepcopy(original);req['assumptions']['coverage_or_power_claim']=True;bad.append(('coverage_claim',req))
    req=copy.deepcopy(original);req['contexts']*=65;bad.append(('too_many_contexts',req))
    for name,req in bad:
        try: mod.certify(req)
        except (TypeError,ValueError,RuntimeError): checks+=1
        else: raise AssertionError('Unsupported input admitted: '+name)
    opt_code="import importlib.util,json,sys; s=importlib.util.spec_from_file_location('x',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.certify(json.loads(sys.argv[2]))"
    for flag in ('-O','-OO'):
        proc=subprocess.run([sys.executable,flag,'-c',opt_code,str(args.engine),json.dumps(original)],capture_output=True,text=True)
        check(proc.returncode!=0 and 'Certification requires ordinary Python' in proc.stderr)
    check(hashlib.sha256(args.engine.read_bytes()).hexdigest()==args.sha256)
    result={'status':'PASS_INDEPENDENT_R18_ENGINE_COMPARISON','engine_sha256':args.sha256,'blind_contexts':len(blind['cases']),'blind_enumerated_probability_curvatures':blind['enumerated_probability_curvatures'],'comparison_and_guard_checks':checks,'full_conventional_null_route_oracles':full_null_checks,'scope':'Deterministic supplied positive real Cartesian population-mass envelopes; no biological data, CI, forecast eta or causality inference.'}
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='full_conventional_null_route_oracles'}))

if __name__=='__main__': main()
