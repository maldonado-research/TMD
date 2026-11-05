#!/usr/bin/env python3
"""Independent, standard-library finite-law oracle for fixed reference tails.

Does not import any TMD inference/geometry implementation. The production API
may later be loaded only for comparisons with independently constructed values.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
from math import factorial, comb, prod
from pathlib import Path
import argparse
import json


ROOT = Path(__file__).resolve().parent


def counts(n):
    return [(w, a, n-w-a) for w in range(n+1) for a in range(n-w+1)]


def normalize(values):
    return tuple(x / sum(values) for x in values)


def multinomial(x, p):
    return F(factorial(sum(x)), prod(factorial(v) for v in x)) * prod(v**k for v, k in zip(p, x))


def shifted(q, theta, eta):
    return normalize((q[0]*eta, q[1]*theta, q[2]/eta))


def key(k1, x1, k2, x2):
    return (x1[0]-x1[2], x2[0]-x2[2],
            tuple(a+b for a, b in zip(k1, x1)),
            tuple(a+b for a, b in zip(k2, x2)), x1[1]+x2[1])


def fiber_h(k1, x1, k2, x2):
    return prod(comb(k+x, x) for k, x in zip(k1+k2, x1+x2))


def reference_prob(h, obs, t):
    tilted = [F(v)*t**j for j, v in enumerate(h)]
    return sum(v for j, v in enumerate(tilted) if h[j] <= h[obs]) / sum(tilted)


def robust_prob(h, obs, interval):
    return max(reference_prob(h, obs, t) for t in interval)


def assert_superuniform(pvalues, probabilities):
    merged = defaultdict(F)
    for p, weight in zip(pvalues, probabilities):
        merged[p] += weight
    total = F(0)
    for p in sorted(merged):
        total += merged[p]
        assert total <= p, (p, total)
    assert total == 1
    return len(merged)


def make_fibers(n=4):
    rows = counts(n)
    fibers = defaultdict(list)
    for k1, x1, k2, x2 in product(rows, repeat=4):
        fibers[key(k1, x1, k2, x2)].append((x2[1], fiber_h(k1, x1, k2, x2), (k1, x1, k2, x2)))
    for rows in fibers.values():
        rows.sort()
        assert all(rows[j+1][0]-rows[j][0] == 2 for j in range(len(rows)-1))
        h = [r[1] for r in rows]
        assert all(h[j]**2 >= h[j-1]*h[j+1] for j in range(1, len(h)-1))
        for obs in range(len(h)):
            middle = [j for j in range(len(h)) if h[j] > h[obs]]
            assert not middle or middle == list(range(middle[0], middle[-1]+1))
    return fibers


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'independent_receipt.json')
    args=parser.parse_args()
    n = 4
    fibers = make_fibers(n)
    q1, q2 = (F(1,6),F(1,3),F(1,2)), (F(1,2),F(1,6),F(1,3))
    scenarios = []
    grid = [F(1,16),F(1,8),F(1,4),F(1,2),F(1),F(2),F(4),F(8),F(16)]
    unique_h = sorted(set(tuple(row[1] for row in rows) for rows in fibers.values()))
    endpoint_grid_checks = 0
    for h in unique_h:
        for obs in range(len(h)):
            for loidx in range(len(grid)):
                for hiidx in range(loidx, len(grid)):
                    lo, hi = grid[loidx], grid[hiidx]
                    bound = robust_prob(h, obs, (lo,hi))
                    for t in grid[loidx:hiidx+1]:
                        assert reference_prob(h, obs, t) <= bound
                        endpoint_grid_checks += 1
                    assert bound == robust_prob(h[::-1], len(h)-1-obs, (1/hi, 1/lo))

    for rho in (F(1,2),F(1),F(2)):
        t = rho**2
        p1, p2 = shifted(q1,F(2),F(3,2)), shifted(q2,F(2)*rho,F(2,3))
        laws = (q1,p1,q2,p2)
        local_masses = [{x:multinomial(x,p) for x in counts(n)} for p in laws]
        intervals = ((t,t),(t/2,t*2),(F(1,4),F(4)))
        rejects = [F(0) for _ in intervals]
        zero_bias_reject = F(0)
        joint_total = F(0)
        thresholds = 0
        for rows in fibers.values():
            h = [r[1] for r in rows]
            raw = [prod(local_masses[k][x] for k,x in enumerate(row[2])) for row in rows]
            fiber_mass = sum(raw)
            joint_total += fiber_mass
            conditional = [v/fiber_mass for v in raw]
            candidate = [F(v)*t**j for j,v in enumerate(h)]
            candidate = [v/sum(candidate) for v in candidate]
            assert candidate == conditional
            for ix,interval in enumerate(intervals):
                pvalues = [robust_prob(h,j,interval) for j in range(len(h))]
                thresholds += assert_superuniform(pvalues, conditional)
                for p,mass in zip(pvalues,raw):
                    if p <= F(1,20):
                        rejects[ix] += mass
            for j,mass in enumerate(raw):
                if reference_prob(h,j,F(1)) <= F(1,20):
                    zero_bias_reject += mass
        assert joint_total == 1
        assert all(v <= F(1,20) for v in rejects)
        scenarios.append({
            "rho":str(rho), "t":str(t), "q1":list(map(str,q1)), "q2":list(map(str,q2)),
            "p1":list(map(str,p1)), "p2":list(map(str,p2)), "joint_mass":"1",
            "all_attainable_thresholds_checked":thresholds,
            "alpha":"1/20", "intervals":[list(map(str,v)) for v in intervals],
            "rejection_probabilities":list(map(str,rejects)),
            "zero_bias_reference_rejection_probability":str(zero_bias_reject),
        })
    h=(1,576,1)
    witness={"h":h,"p_zero":str(reference_prob(h,0,F(1))),
             "p_interval_quarter_to_four":str(robust_prob(h,0,(F(1,4),F(4)))),
             "p_interval_sixteenth_to_sixteen":str(robust_prob(h,0,(F(1,16),F(16))))}
    # Generic event: central singleton at t=1 yields an interior maximum.
    central=lambda t:t/(1+t+t*t)
    assert central(F(1)) > max(central(F(1,2)),central(F(2)))
    # A nonlogconcave reference sequence admits an interior maximum too.
    broken=(2,1,2)
    assert reference_prob(broken,1,F(1)) > max(reference_prob(broken,1,F(1,2)),reference_prob(broken,1,F(2)))
    receipt={"status":"pass", "source":"independent raw four-arm multinomial enumeration",
             "n_each_arm":n,"tables_per_scenario":len(counts(n))**4,
             "fibers":len(fibers),"unique_weight_sequences":len(unique_h),
             "endpoint_grid_checks":endpoint_grid_checks,"scenarios":scenarios,"witness":witness,
             "generic_endpoint_failure":{"h":broken,"observed_index":1,
                 "p_half":str(reference_prob(broken,1,F(1,2))),
                 "p_one":str(reference_prob(broken,1,F(1))),
                 "p_two":str(reference_prob(broken,1,F(2)))}}
    path=args.output
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
