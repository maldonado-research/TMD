"""Verify finite sharp-bound certificates in stdlib; never imports producer code."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


def evaluate(mask,carriers,references,k,r):
    cb=sum(2**j for j in carriers);rb=sum(2**j for j in references)
    return int((mask&cb).bit_count()>=k and (mask&rb).bit_count()>=r)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oracle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();raw=args.oracle.read_bytes();oracle=json.loads(raw)
    counts={'nonnegative_witness_weights':0,'marginal_equalities':0,'dual_inequalities':0,'strong_duality':0,'endpoint_values':0,'independent_inside_interval':0,'full_law_scalar_checks':0}
    def check(value,category):
        if not value:raise RuntimeError('Exact certificate failed: '+category)
        counts[category]+=1
    for case in oracle['marginal_bound_cases']:
        n=case['n'];p=list(map(Fraction,case['marginals']))
        for endpoint in ['lower','upper']:
            cert=case[endpoint];w={int(mask):Fraction(v) for mask,v in cert['attaining_law'].items()}
            dual=list(map(Fraction,cert['dual_coefficients']));sign=1 if endpoint=='lower' else -1
            for mask in range(2**n):check(w.get(mask,Fraction())>=0,'nonnegative_witness_weights')
            check(sum(w.values())==1,'marginal_equalities')
            for j in range(n):check(sum(value for mask,value in w.items() if mask&(2**j))==p[j],'marginal_equalities')
            for mask in range(2**n):
                lhs=dual[0]+sum(dual[j+1] for j in range(n) if mask&(2**j))
                rhs=sign*evaluate(mask,case['carriers'],case['references'],case['k'],case['r'])
                check(lhs<=rhs,'dual_inequalities')
            primal=sum(sign*value*evaluate(mask,case['carriers'],case['references'],case['k'],case['r']) for mask,value in w.items())
            bound=dual[0]+sum(p[j]*dual[j+1] for j in range(n))
            check(primal==bound,'strong_duality')
            check(sign*primal==Fraction(cert['value']),'endpoint_values')
        check(Fraction(case['lower']['value'])<=Fraction(case['value_if_independent'])<=Fraction(case['upper']['value']),'independent_inside_interval')
    for case in oracle['full_law_cases']:
        n=case['n'];law={int(mask):Fraction(v) for mask,v in case['law'].items()};e=case['expected']
        cb=sum(2**j for j in case['carriers']);rb=sum(2**j for j in case['references'])
        check(sum(law.values())==1,'full_law_scalar_checks')
        marg=[sum(w for mask,w in law.items() if mask&(2**j)) for j in range(n)]
        check(marg==list(map(Fraction,e['descendant_call_marginals'])),'full_law_scalar_checks')
        pi=sum(w*evaluate(mask,case['carriers'],case['references'],case['k'],case['r']) for mask,w in law.items())
        check(pi==Fraction(e['inclusion_probability']),'full_law_scalar_checks')
        check(sum(w*(mask&cb).bit_count() for mask,w in law.items())==Fraction(e['expected_carrier_call_copies']),'full_law_scalar_checks')
        check(sum(w*(mask&rb).bit_count() for mask,w in law.items())==Fraction(e['expected_reference_calls']),'full_law_scalar_checks')
        positive=sorted(mask for mask,w in law.items() if w>0 and evaluate(mask,case['carriers'],case['references'],case['k'],case['r']))
        check(positive==e['successful_masks'],'full_law_scalar_checks')
    receipt={'status':'passed_exact_frozen_oracle_certificates_without_scipy_or_producer','oracle_sha256':hashlib.sha256(raw).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':counts,'total_checks':sum(counts.values()),'network_requests':0,'producer_imports':0,'qualified_external_review':False}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
