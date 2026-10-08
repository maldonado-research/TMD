"""Independent finite-corner oracle; population endpoint masses only, no sample CI."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

FIELDS = ('mass', 'supply', 'growth', 'recovery')

def point(values):
    return [(F(x), F(x)) for x in values]

def constant_context(mass=(1, 1, 1), supply=(1, 1, 1), growth=(1, 1, 1), recovery=(1, 1, 1)):
    return {name: point(value) for name, value in zip(FIELDS, (mass, supply, growth, recovery))}

def endpoint_oracle(context):
    """Enumerate physical factors, normalize corrected weights, compute curvature."""
    variables = [tuple(dict.fromkeys(pair)) for field in FIELDS for pair in context[field]]
    values = []
    for corner in product(*variables):
        m, q, g, r = [corner[i:i+3] for i in range(0, 12, 3)]
        corrected = [m[i] / (q[i] * g[i] * r[i]) for i in range(3)]
        total = sum(corrected)
        probabilities = [x / total for x in corrected]
        k = probabilities[1] ** 2 / (probabilities[0] * probabilities[2])
        values.append(k)
    return min(values), max(values), len(values)

def cases():
    rows = []
    for t in (F(1, 2), F(1), F(2), F(4)):
        yields = (t, F(2), 1/t)
        rows.append(('known_growth_' + str(t), constant_context(mass=yields, growth=yields)))
        scale = max(yields)
        recovery = tuple(y / scale for y in yields)
        rows.append(('known_recovery_' + str(t), constant_context(mass=recovery, recovery=recovery)))
        rows.append(('unadjusted_mimic_' + str(t), constant_context(mass=yields)))
    for n in range(1, 9):
        c = constant_context()
        c['mass'] = [(F(1,n+1), F(n+2)), (F(1,2), F(n+1)), (F(1,3), F(n+3))]
        c['supply'] = [(F(1,2), F(n+1)), (F(1,3), F(n+2)), (F(1,4), F(n+3))]
        c['growth'] = [(F(1,2), F(n+1)), (F(1,3), F(n+2)), (F(1,4), F(n+3))]
        c['recovery'] = [(F(1,n+2), F(1,2)), (F(1,n+3), F(2,3)), (F(1,n+4), F(3,4))]
        rows.append(('all_twelve_factors_' + str(n), c))
    for n in range(1, 10):
        c = constant_context(mass=(1, n+1, 1))
        c['growth'] = [(F(1), F(n+1))] * 3
        rows.append(('broad_growth_' + str(n), c))
        c2 = constant_context()
        c2['mass'][1] = (F(1), F(n+1))
        rows.append(('only_middle_' + str(n), c2))
    return rows

def document():
    out = []
    comparisons = 0
    for name, context in cases():
        lo, hi, count = endpoint_oracle(context)
        comparisons += count
        if name.startswith('known_'):
            assert lo == hi == 1
        if name.startswith('unadjusted_'):
            assert lo == hi == 4
        # Multiplying all endpoint masses in a context preserves corrected shape.
        scaled = {name: list(intervals) for name, intervals in context.items()}
        scaled['mass'] = [(a*7, b*7) for a, b in context['mass']]
        slo, shi, n2 = endpoint_oracle(scaled)
        assert (slo, shi) == (lo, hi)
        comparisons += n2
        out.append({'id':name,'context':{field:[[str(a),str(b)] for a,b in context[field]] for field in FIELDS},'sharp_curvature':[str(lo),str(hi)],'enumerated_corners':count})
    # Conditional common-parameter tests: exact closed interval contact is feasible.
    intersections = [
        {'id':'disjoint','intervals':[['4','4'],['9','9']],'common':None},
        {'id':'contact','intervals':[['1','4'],['4','9']],'common':['4','4']},
        {'id':'wide','intervals':[['1/4','16'],['1','81']],'common':['1','16']},
        {'id':'three_pairwise_contact','intervals':[['1','3'],['2','4'],['3','5']],'common':['3','3']},
    ]
    for item in intersections:
        lo = max(F(a) for a,b in item['intervals']);hi = min(F(b) for a,b in item['intervals'])
        got = [str(lo),str(hi)] if lo <= hi else None
        assert got == item['common']
    # Real-parameter feasibility does not require a rational-valued witness.
    irrational_context = constant_context()
    irrational_context['mass'][1] = (F(1),F(2))
    lo,hi,_ = endpoint_oracle(irrational_context)
    assert lo <= 2 <= hi and (lo,hi)==(1,4)
    return {'status':'PASS_BLIND_FINITE_CORNER_ORACLE','scope':'Positive unnormalized expected mass and independent Cartesian nuisance envelopes; no empirical coverage or count law. Continuity of the real-valued product on a connected box fills its extremal interval; enumeration itself checks only endpoints.','context_count':len(out),'enumerated_probability_curvatures':comparisons,'cases':out,'common_parameter_cases':intersections,'irrational_witness_note':'Only m2 in [1,2], other factors1, permits K=2 at m2=sqrt2. The real algebraic certificate does not promise a Fraction witness.'}

if __name__ == '__main__':
    import argparse
    if not __debug__:
        raise SystemExit('Independent oracle requires assertions enabled')
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    d=document();args.output.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:d[k] for k in ['status','context_count','enumerated_probability_curvatures']}))
