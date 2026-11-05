#!/usr/bin/env python3
"""Independent exhaustive raw-sample oracle; no fitted biology or power claim."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
from math import factorial, prod
import json

from baseline_conditional_homogeneity import baseline_conditional_test
from conditional_homogeneity import conditional_test


def rows(n, p):
    for w in range(n + 1):
        for a in range(n - w + 1):
            x = (w, a, n - w - a)
            coefficient = F(factorial(n), prod(factorial(v) for v in x))
            yield x, coefficient * prod(q ** v for q, v in zip(p, x))


def selected(q, t, u):
    values = (q[0] * u, q[1] * t, q[2] / u)
    return tuple(v / sum(values) for v in values)


def baseline_oracle(m, n, qs, t, us, check_engine=True):
    per_context = []
    for q, u in zip(qs, us):
        per_context.append(tuple((b, x, pb * px)
            for (b, pb), (x, px) in product(rows(m, q), rows(n, selected(q, t, u)))))
    fibers = defaultdict(list)
    for left, right in product(*per_context):
        b, x, pl = left
        d, y, pr = right
        pooled = (tuple(i+j for i,j in zip(b,x)), tuple(i+j for i,j in zip(d,y)))
        key = (pooled, x[0]-x[2], y[0]-y[2], x[1]+y[1])
        fibers[key].append((b, x, d, y, pl*pr))
    assert sum(sum(row[-1] for row in values) for values in fibers.values()) == 1
    rejection = F(0)
    for values in fibers.values():
        normalizer = sum(row[-1] for row in values)
        probabilities = {(x[1],y[1]): mass/normalizer for b,x,d,y,mass in values}
        pvalues = {a: sum(p for p in probabilities.values() if p <= mass)
                   for a,mass in probabilities.items()}
        # Check every attainable threshold, not just the illustrative 0.05.
        for threshold in set(pvalues.values()):
            assert sum(probabilities[a] for a,p in pvalues.items() if p <= threshold) <= threshold
        for b,x,d,y,mass in values:
            pvalue = pvalues[(x[1],y[1])]
            if pvalue <= F(1,20):
                rejection += mass
            if check_engine:
                result = baseline_conditional_test({
                    "observation_contract": "shared_positive_offset_within_context",
                    "sampling_contract": "independent_baseline_selected_multinomials",
                    "alpha": "1/20",
                    "contexts": [
                        {"id": "left", "baseline": list(b), "selected": list(x)},
                        {"id": "right", "baseline": list(d), "selected": list(y)},
                    ],
                }, include_fiber=True)
                actual = {tuple(row["A"]): F(row["probability"]) for row in result["fiber"]}
                assert actual == probabilities
                assert F(result["p_value"]) == pvalue
    assert rejection <= F(1,20)
    return {"M": m, "N": n, "joint_sample_tables": sum(map(len,fibers.values())),
            "conditioning_fibers": len(fibers),
            "informative_fibers": sum(len(v)>1 for v in fibers.values()),
            "maximum_fiber_size": max(map(len,fibers.values())),
            "unconditional_size_at_1_20": str(rejection),
            "engine_compared_to_every_raw_sample_table": check_engine,
            "conditional_superuniformity_at_every_attained_threshold": True}


def plugin_witness():
    # Two independent one-draw calibrations, then independent N=5 selected samples.
    # All four arms have the true uniform q. Thus theta=eta=0 is a true null.
    q = (F(1,3),)*3
    rejection = F(0)
    strata = []
    for (b,pb), (d,pd) in product(rows(1,q),repeat=2):
        qs = [tuple((F(k)+F(1,2))/F(5,2) for k in counts) for counts in (b,d)]
        conditional_rejection = F(0)
        for (x,px),(y,py) in product(rows(5,q),repeat=2):
            result = conditional_test({
                "offset_contract": "fixed_known_positive_rational",
                "sampling_contract": "independent_multinomial_given_totals",
                "alpha": "1/20",
                "contexts": [
                    {"id":"left", "counts":list(x), "q":[str(v) for v in qs[0]]},
                    {"id":"right", "counts":list(y), "q":[str(v) for v in qs[1]]},
                ],
            })
            if F(result["p_value"]) <= F(1,20):
                conditional_rejection += px*py
        rejection += pb*pd*conditional_rejection
        strata.append({"baseline_left":b,"baseline_right":d,"selected_rejection_rate":str(conditional_rejection)})
    assert rejection == F(30620,531441) > F(1,20)
    return {"nominal_alpha":"1/20", "actual_type_I_error":str(rejection),
            "calibration_per_context":1, "selected_per_context":5,
            "calibration_smoothing":"(k_i+1/2)/(1+3/2)",
            "true_null":"Both contexts uniform baseline and selected; theta=eta=0",
            "strata":strata,
            "note":"Deliberately violates known-offset input declaration to demonstrate that independent estimation does not make a plug-in exact."}


if __name__ == "__main__":
    uniform = (F(1,3),)*3
    output = {
        "uniform_baseline_cases":[baseline_oracle(m,n,(uniform,uniform),F(1),(F(1),F(1)))
                                  for m,n in ((1,5),(3,3),(4,4))],
        "nonuniform_nuisance_cancellation":baseline_oracle(3,3,((F(1,6),F(2,6),F(3,6)),
                                                                (F(3,6),F(2,6),F(1,6))),
                                                           F(2),(F(2),F(1,3))),
        "estimated_offset_counterexample":plugin_witness(),
    }
    print(json.dumps(output,indent=2,sort_keys=True))
